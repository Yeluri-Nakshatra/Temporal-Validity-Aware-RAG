"""Answer classification: OLD / NEW / BOTH / OTHER / ABSTAIN.

Alias matching first; an LLM judge resolves ambiguous or unmatched answers. Judge
decisions are cached on disk so repeated runs are deterministic and cheap.
"""
from __future__ import annotations
import json, re, hashlib
from pathlib import Path

YESNO = {"yes", "no"}


def _match(answer: str, aliases: list[str]) -> bool:
    a = answer.lower()
    for al in aliases:
        al = al.lower()
        if al in YESNO:
            if re.match(rf"^\W*{al}\b", a):
                return True
        elif len(al) <= 3 and al.isalnum():
            if re.search(rf"\b{re.escape(al)}\b", a):
                return True
        elif al in a:
            return True
    return False


def alias_label(answer: str, old_aliases: list[str], new_aliases: list[str], abstain: bool) -> str:
    if abstain or not answer.strip():
        return "ABSTAIN"
    o, n = _match(answer, old_aliases), _match(answer, new_aliases)
    if o and n:
        return "BOTH"
    if n:
        return "NEW"
    if o:
        return "OLD"
    return "OTHER"


JUDGE_PROMPT = """You are grading a short answer to a question. Two reference answers are given:
(A) is the answer that was correct before a change took place; (B) is the answer that became correct after the change.
Decide which reference the candidate answer agrees with. Ignore wording differences; judge the substance only.

Question: {q}
Reference A (old): {old}
Reference B (new): {new}
Candidate answer: {cand}

Reply with exactly one token: A, B, BOTH (if it asserts both as currently true or hedges between them), or NEITHER."""

JUDGE_PROMPT_CTL = """You are grading a short answer to a question against a reference answer. Ignore wording; judge substance.

Question: {q}
Reference answer: {ref}
Candidate answer: {cand}

Reply with exactly one token: CORRECT or WRONG."""


class Judge:
    def __init__(self, client, model: str, cache_path: Path):
        self.client, self.model, self.cache_path = client, model, Path(cache_path)
        self.cache = json.loads(self.cache_path.read_text()) if self.cache_path.exists() else {}

    def _ask(self, prompt: str) -> str:
        key = hashlib.sha1((self.model + prompt).encode()).hexdigest()
        if key not in self.cache:
            from .generator import chat
            self.cache[key] = chat(self.client, self.model, prompt, max_tokens=8)
            self.cache_path.write_text(json.dumps(self.cache, indent=0))
        return self.cache[key].strip().upper()

    def label_reversal(self, q: str, old: str, new: str, cand: str) -> str:
        r = self._ask(JUDGE_PROMPT.format(q=q, old=old, new=new, cand=cand))
        tok = re.findall(r"\b(BOTH|NEITHER|A|B)\b", r)
        if not tok:
            return "OTHER"
        return {"A": "OLD", "B": "NEW", "BOTH": "BOTH", "NEITHER": "OTHER"}[tok[0]]

    def label_control(self, q: str, ref: str, cand: str) -> str:
        r = self._ask(JUDGE_PROMPT_CTL.format(q=q, ref=ref, cand=cand))
        return "CTL" if "CORRECT" in r and "WRONG" not in r.split("CORRECT")[0] else "OTHER"


def final_label(query, parsed: dict, judge: Judge | None) -> tuple[str, str]:
    """Returns (label, method). label in NEW/OLD/BOTH/OTHER/ABSTAIN/CTL."""
    ans = parsed["answer"]
    if query.kind == "control":
        if parsed["abstain"]:
            return "ABSTAIN", "alias"
        if _match(ans, query.new_aliases):
            return "CTL", "alias"
        return (judge.label_control(query.question, query.gold, ans), "judge") if judge else ("OTHER", "alias")
    lab = alias_label(ans, query.old_aliases, query.new_aliases, parsed["abstain"])
    negated = re.search(r"\b(not|no longer|never|n't|neither)\b", ans.lower()) is not None
    if lab == "ABSTAIN" or judge is None or (lab in ("NEW", "OLD") and not negated):
        return lab, "alias"
    return judge.label_reversal(query.question, query.old_answer, query.new_answer, ans), "judge"
