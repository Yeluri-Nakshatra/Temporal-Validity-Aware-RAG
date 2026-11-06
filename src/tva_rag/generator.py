"""LLM access through Ollama, and the prompt templates for each system variant."""
from __future__ import annotations
import datetime as dt, time
import ollama
from .conflict import Evidence


def get_client(host: str = "http://localhost:11434"):
    return ollama.Client(host=host)


def chat(client, model: str, prompt: str, max_tokens: int = 220, system: str | None = None) -> str:
    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
    kw = dict(model=model, messages=msgs, options={"temperature": 0, "num_predict": max_tokens, "num_ctx": 6144, "seed": 7})
    if "qwen3" in model:
        kw["think"] = False
    last = None
    for attempt in range(4):
        try:
            r = client.chat(**kw)
            return r["message"]["content"].strip()
        except Exception as ex:  # Ollama runner crashes / transient 500s
            last = ex
            time.sleep(3 * (attempt + 1))
    raise last


SYSTEM = "You are a precise question-answering assistant. Be concise."

FORMAT_BASIC = "\nRespond with a brief justification (one or two sentences) and then a final line of the form:\nANSWER: <short answer>"

FORMAT_TVA = ("\nRespond with a brief justification (one or two sentences), then these final lines:\n"
              "ANSWER: <the answer itself in a few words, as of the reference date; or the single word ABSTAIN>\n"
              "VALID_FROM: <date from which this answer holds, or unknown>\n"
              "BASIS: <document numbers used>")


def _ref(t: dt.date | None) -> str:
    return f"Reference date: {t.isoformat()}. Answer the question as it would be correctly answered on that date.\n\n" if t else ""


def prompt_closed_book(question: str, t: dt.date | None = None) -> str:
    return _ref(t) + f"Question: {question}" + FORMAT_BASIC


def _docs_block(evs: list[Evidence], annotate: bool, t: dt.date) -> str:
    parts = []
    for i, e in enumerate(evs, 1):
        if annotate:
            if e.status == "SUPERSEDED":
                st = f"SUPERSEDED on {e.superseded_on} by Document {[x.doc_id for x in evs].index(e.superseded_by) + 1}"
            elif e.status == "CURRENT":
                st = f"CURRENT as of {t.isoformat()}"
            elif e.status == "UNVERIFIED":
                st = "DATE UNKNOWN - cannot verify whether still valid"
            else:
                st = "no conflicting evidence found"
            date = e.meta.effective or e.meta.pub_date or "unknown"
            parts.append(f"[Document {i} | dated: {date} | status: {st}]\n{e.text}")
        else:
            parts.append(f"[Document {i}]\n{e.text}")
    return "\n\n".join(parts)


def prompt_rag(question: str, evs: list[Evidence], trust_instruction: bool = False, t: dt.date | None = None) -> str:
    inst = "Use the documents below to answer the question."
    if trust_instruction:
        inst = "Answer the question based on the documents below. Your answer must follow the information in the documents."
    return _ref(t) + f"{inst}\n\n{_docs_block(evs, False, dt.date.today())}\n\nQuestion: {question}" + FORMAT_BASIC


def prompt_tva(question: str, evs: list[Evidence], t: dt.date) -> str:
    inst = (
        f"Reference date: {t.isoformat()}. Answer the question as it would be correctly answered on the reference date.\n"
        "Each document below is annotated with its date and a validity status that was computed by comparing the documents:\n"
        "- CURRENT: the most recent valid evidence on this point as of the reference date.\n"
        "- SUPERSEDED: older evidence that a newer document has replaced; treat it as historical, not as the current answer.\n"
        "- DATE UNKNOWN: the document's date could not be established, so it may be outdated.\n"
        "Rules: prefer CURRENT evidence. Never give a SUPERSEDED answer as the current answer. "
        "If a CURRENT document answers the question, answer from it; do not abstain. "
        "Answer ABSTAIN only when no CURRENT document answers the question and the only relevant evidence is DATE UNKNOWN and it conflicts with other evidence or with what you know. "
        "If every document is older than the reference date by many years and you believe the fact has since changed, say so. "
        "The ANSWER line must contain the answer itself (a name, number, yes/no or short phrase), never a status word such as CURRENT or SUPERSEDED."
    )
    return f"{inst}\n\n{_docs_block(evs, True, t)}\n\nQuestion: {question}" + FORMAT_TVA


def prompt_tva_single(question: str, evs: list[Evidence], t: dt.date) -> str:
    """Stale-only setting: no newer evidence exists in the corpus; signal the document age."""
    inst = (
        f"Reference date: {t.isoformat()}. Answer the question as it would be correctly answered on the reference date.\n"
        "Each document below is annotated with its date. No newer document on this topic was found in the knowledge base.\n"
        "Rules: if a document is dated several years before the reference date and the fact it states is one that changes over time "
        "(an office holder, a rule, a version, a status), do not assume it is still valid. Use your own knowledge of later developments if you are confident; "
        "otherwise answer ABSTAIN rather than repeating possibly outdated information. If the document's date is unknown, be especially cautious."
    )
    parts = []
    for i, e in enumerate(evs, 1):
        date = e.meta.effective or e.meta.pub_date
        if date:
            age = (t - dt.date.fromisoformat(date)).days / 365.25
            tag = f"dated: {date} | age at reference date: {age:.1f} years"
        else:
            tag = "dated: unknown"
        parts.append(f"[Document {i} | {tag}]\n{e.text}")
    return f"{inst}\n\n" + "\n\n".join(parts) + f"\n\nQuestion: {question}" + FORMAT_TVA


def parse_answer(raw: str) -> dict:
    out = {"answer": "", "valid_from": None, "basis": None, "abstain": False, "raw": raw}
    for line in raw.splitlines():
        s = line.strip().strip("*").strip()
        up = s.upper()
        if up.startswith("ANSWER:"):
            out["answer"] = s.split(":", 1)[1].strip().strip("*").strip()
        elif up.startswith("VALID_FROM:"):
            v = s.split(":", 1)[1].strip()
            out["valid_from"] = None if v.lower().startswith("unknown") else v
        elif up.startswith("BASIS:"):
            out["basis"] = s.split(":", 1)[1].strip()
    if not out["answer"]:
        out["answer"] = raw.strip().splitlines()[-1] if raw.strip() else ""
    if "ABSTAIN" in out["answer"].upper():
        out["abstain"] = True
    return out
