"""Temporal conflict detection and validity status assignment.

Two detector back-ends:

  method="claims" (default)
     1. Similarity gate: only documents whose whole-text embedding similarity to at least one
        other retrieved document is >= sim_gate are candidates (cheap pre-filter).
     2. Question-conditioned claim extraction: a small LLM states the short answer each
        candidate document gives to the question, or NONE if it does not address it.
     3. Two documents conflict when both give an answer and the answers are not equivalent
        (normalised string match, else an LLM equivalence check). All LLM calls are cached.

  method="nli"
     Pairwise NLI contradiction on the query-relevant key sentence of each document, gated
     by document similarity and the supersession cue (thresholds calibrated with
     scripts/calibrate_conflict.py).

Status assignment is pairwise, not transitive: a document is SUPERSEDED if some document it
conflicts with has a later temporal anchor that is <= the reference date t; CURRENT if it
conflicts with others and none is later; UNVERIFIED if it has no date; FUTURE if its anchor
is after t (such documents are dropped before generation); UNCONFLICTED otherwise.
"""
from __future__ import annotations
import re, json, hashlib, datetime as dt, pathlib
from dataclasses import dataclass, field
from typing import Optional
import numpy as np
from .temporal import TemporalMeta

SENT = re.compile(r"(?<=[.!?])\s+")


@dataclass
class Evidence:
    doc_id: str
    title: str
    text: str
    meta: TemporalMeta
    retrieval_score: float
    key_sentence: str = ""
    claim: Optional[str] = None
    status: str = "UNCONFLICTED"
    superseded_by: Optional[str] = None
    superseded_on: Optional[str] = None
    validity: float = 1.0
    final_score: float = 0.0
    conflicts_with: list = field(default_factory=list)

    @property
    def anchor(self) -> Optional[dt.date]:
        return self.meta.anchor()


CLAIM_PROMPT = """Question: {q}

Document:
{doc}

Step 1 - scope check. Does this document address this exact question: the same specific item, rule, entity, office or product that the question asks about? A document about a related but different matter (for example a general rate structure when the question asks about one specific item's rate, a different law, a different product, or a different office) does NOT address the question.
Step 2 - if it does, state the answer the document gives, as its author would answer: a document that states, uses or presupposes a name, value, status or holder for the exact subject of the question is giving that as its answer.

Reply with only the shortest possible answer (a name, a number, yes/no, or at most 8 words), or exactly NONE if the document does not address this exact question. No explanation."""

EQUIV_PROMPT = """Question: {q}
Answer 1: {a}
Answer 2: {b}

Are these the same answer to this question? They are DIFFERENT if they give different names or spellings (even for the same underlying thing, when the question asks for a name), different entities, organisations, people, places, numbers, versions or dates, or if one says yes and the other says no. Reply with exactly YES or NO."""

_NORM = re.compile(r"[^a-z0-9 ]+")


def normalise(s: str) -> str:
    s = _NORM.sub(" ", s.lower())
    s = re.sub(r"\b(the|a|an|is|are|was|of|in|to|and|it|its|as|by|on)\b", " ", s)
    return " ".join(s.split())


class ConflictDetector:
    def __init__(self, method: str = "claims", client=None, llm_model: str = "llama3.1:8b",
                 embed_fn=None, cache_path: str | pathlib.Path | None = None, device: str | None = None,
                 sim_gate: float = 0.60, nli_model: str = "cross-encoder/nli-deberta-v3-base",
                 nli_contra: float = 0.5, nli_sim: float = 0.72, nli_cue_sim: float = 0.78):
        self.method, self.client, self.llm_model, self.embed_fn = method, client, llm_model, embed_fn
        self.sim_gate = sim_gate
        self.cache_path = pathlib.Path(cache_path) if cache_path else None
        self.cache = json.loads(self.cache_path.read_text()) if self.cache_path and self.cache_path.exists() else {}
        self.nli_contra, self.nli_sim, self.nli_cue_sim = nli_contra, nli_sim, nli_cue_sim
        self.nli = None
        if method == "nli":
            from sentence_transformers import CrossEncoder
            self.nli = CrossEncoder(nli_model, device=device)
            labels = [l.lower() for l in self.nli.config.id2label.values()]
            self.ci = [i for i, l in enumerate(labels) if l.startswith("contra")][0]
        self.n_llm_calls = 0

    # ---------------------------------------------------------------- LLM helpers
    def _ask(self, prompt: str, max_tokens: int = 40) -> str:
        key = hashlib.sha1((self.llm_model + prompt).encode()).hexdigest()
        if key not in self.cache:
            from .generator import chat
            self.cache[key] = chat(self.client, self.llm_model, prompt, max_tokens=max_tokens)
            self.n_llm_calls += 1
            if self.cache_path:
                self.cache_path.write_text(json.dumps(self.cache))
        return self.cache[key].strip()

    def extract_claim(self, question: str, e: Evidence) -> Optional[str]:
        r = self._ask(CLAIM_PROMPT.format(q=question, doc=e.text), 40)
        r = r.splitlines()[0].strip().strip("*").strip() if r else ""
        if not r or r.upper().startswith("NONE"):
            return None
        return r

    def equivalent(self, question: str, a: str, b: str) -> bool:
        na, nb = normalise(a), normalise(b)
        if na == nb:
            return True
        r = self._ask(EQUIV_PROMPT.format(q=question, a=a, b=b), 4).upper()
        return r.startswith("YES")

    # ---------------------------------------------------------------- NLI helpers
    def key_sentences(self, query: str, evs: list[Evidence]):
        q = self.embed_fn([query])[0]
        for e in evs:
            sents = [s for s in SENT.split(e.text.split("\n\n", 1)[-1].replace("\n", " ")) if len(s) > 15]
            if not sents:
                e.key_sentence = e.text[:300]; continue
            embs = self.embed_fn(sents)
            e.key_sentence = sents[int(np.argmax(embs @ q))]

    def contradiction(self, a: str, b: str) -> float:
        logits = self.nli.predict([(a, b), (b, a)], convert_to_numpy=True)
        probs = np.exp(logits - logits.max(axis=1, keepdims=True)); probs /= probs.sum(axis=1, keepdims=True)
        return float(probs[:, self.ci].max())

    # ---------------------------------------------------------------- main entry
    def find_conflicts(self, question: str, evs: list[Evidence]) -> list[tuple[int, int, dict]]:
        n = len(evs)
        if n < 2:
            return []
        D = self.embed_fn([e.text for e in evs]); sims = D @ D.T
        pairs = []
        if self.method == "claims":
            cand = [i for i in range(n) if any(sims[i, j] >= self.sim_gate for j in range(n) if j != i)]
            for i in cand:
                evs[i].claim = self.extract_claim(question, evs[i])
            for i in cand:
                for j in cand:
                    if j <= i or evs[i].claim is None or evs[j].claim is None:
                        continue
                    if sims[i, j] < self.sim_gate:
                        continue
                    if not self.equivalent(question, evs[i].claim, evs[j].claim):
                        pairs.append((i, j, dict(sim=round(float(sims[i, j]), 3), claims=[evs[i].claim, evs[j].claim])))
        else:
            self.key_sentences(question, evs)
            for i in range(n):
                for j in range(i + 1, n):
                    a, b = evs[i], evs[j]
                    sim = float(sims[i, j])
                    if sim < self.nli_sim:
                        continue
                    c = self.contradiction(a.key_sentence, b.key_sentence)
                    newer = max([a, b], key=lambda e: e.anchor or dt.date.min)
                    cue = newer.meta.supersedes_cue and sim >= self.nli_cue_sim and a.anchor != b.anchor
                    if c >= self.nli_contra or cue:
                        pairs.append((i, j, dict(sim=round(sim, 3), contra=round(c, 3), cue=bool(cue))))
        return pairs

    def detect(self, question: str, evs: list[Evidence], t: dt.date) -> list[Evidence]:
        pairs = self.find_conflicts(question, evs)
        for i, j, info in pairs:
            evs[i].conflicts_with.append((evs[j].doc_id, info))
            evs[j].conflicts_with.append((evs[i].doc_id, info))
        return assign_status(evs, t)


def assign_status(evs: list[Evidence], t: dt.date) -> list[Evidence]:
    by_id = {e.doc_id: e for e in evs}
    for e in evs:
        if e.anchor and e.anchor > t:
            e.status, e.validity = "FUTURE", 0.0
    for e in evs:
        if e.status == "FUTURE":
            continue
        partners = [by_id[d] for d, _ in e.conflicts_with if by_id[d].status != "FUTURE"]
        if not partners:
            e.status, e.validity = ("UNCONFLICTED", 1.0) if e.anchor else ("UNVERIFIED", 0.6)
            continue
        if not e.anchor:
            e.status, e.validity = "UNVERIFIED", 0.4
            continue
        later = [p for p in partners if p.anchor and p.anchor > e.anchor]
        if later:
            newest = max(later, key=lambda p: p.anchor)
            e.status, e.validity = "SUPERSEDED", 0.25
            e.superseded_by, e.superseded_on = newest.doc_id, newest.anchor.isoformat()
        else:
            e.status, e.validity = "CURRENT", 1.0
    return evs
