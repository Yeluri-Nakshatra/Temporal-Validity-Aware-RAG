"""Temporal metadata extraction: publication date, effective date, supersession cues.

Regex-first with calibrated confidence; optional LLM fallback for documents where no
date cue is found (off by default: it is slow and can hallucinate dates from content).
"""
from __future__ import annotations
import re, datetime as dt, json
from dataclasses import dataclass, asdict
from typing import Optional

MONTHS = {m.lower(): i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July", "August",
     "September", "October", "November", "December"], start=1)}
MONTHS.update({k[:3]: v for k, v in list(MONTHS.items())})
MONTHS["sept"] = 9
MON = r"(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"

# (pattern, builder, precision)
PATTERNS = [
    (re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b"), lambda m: (int(m[1]), int(m[2]), int(m[3])), "day"),
    (re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+" + MON + r"\s*,?\s*(\d{4})\b", re.I),
     lambda m: (int(m[3]), MONTHS[m[2].lower()], int(m[1])), "day"),
    (re.compile(r"\b" + MON + r"\s+(\d{1,2})(?:st|nd|rd|th)?\s*,\s*(\d{4})\b", re.I),
     lambda m: (int(m[3]), MONTHS[m[1].lower()], int(m[2])), "day"),
    (re.compile(r"\b(\d{2})[/.\-](\d{2})[/.\-](\d{4})\b"), lambda m: (int(m[3]), int(m[2]), int(m[1])), "day"),
    (re.compile(r"\b" + MON + r"\s+(\d{4})\b", re.I), lambda m: (int(m[2]), MONTHS[m[1].lower()], 1), "month"),
]
EFFECTIVE_CUE = re.compile(r"(effective\s+from|with\s+effect\s+from|w\.e\.f\.?|comes?\s+into\s+force|in\s+force\s+from|applicable\s+from)", re.I)
SUPERSEDE_CUE = re.compile(r"(supersed|replac(?:es|ing|ed)|no\s+longer|repeal|abolish|retired|reclassif|renamed|succeed)", re.I)
HEADER_LINES = 3


@dataclass
class TemporalMeta:
    pub_date: Optional[str]          # ISO or None
    precision: Optional[str]         # day | month | None
    effective: Optional[str]         # ISO or None
    supersedes_cue: bool
    confidence: float                # 0..1
    source: str                      # header | body | llm | none

    def anchor(self) -> Optional[dt.date]:
        """Date used for validity reasoning: effective date if present, else publication."""
        s = self.effective or self.pub_date
        return dt.date.fromisoformat(s) if s else None

    def to_dict(self):
        return asdict(self)


def _find_dates(text: str):
    found = []
    for pat, build, prec in PATTERNS:
        for m in pat.finditer(text):
            try:
                y, mo, d = build(m)
                date = dt.date(y, mo, d)
            except (ValueError, KeyError):
                continue
            if 1900 <= y <= 2100:
                found.append((m.start(), date, prec))
    # remove month-precision hits that overlap a day-precision hit
    day_spans = [(s, s + 12) for s, _, p in found if p == "day"]
    out = []
    for s, date, p in found:
        if p == "month" and any(a <= s <= b for a, b in day_spans):
            continue
        out.append((s, date, p))
    return sorted(out)


def extract_regex(text: str) -> TemporalMeta:
    lines = text.split("\n")
    header = "\n".join(lines[:HEADER_LINES])
    body = "\n".join(lines[HEADER_LINES:])
    supersedes = bool(SUPERSEDE_CUE.search(text))

    effective = None
    for m in EFFECTIVE_CUE.finditer(text):
        window = text[m.end(): m.end() + 40]
        ds = _find_dates(window)
        if ds:
            effective = ds[0][1].isoformat()
            break

    hdr = _find_dates(header)
    # the effective date line can also sit in the header; exclude it from pub-date candidates
    hdr = [h for h in hdr if h[1].isoformat() != effective] or hdr
    if hdr:
        _, date, prec = hdr[0]
        conf = 0.95 if prec == "day" else 0.8
        return TemporalMeta(date.isoformat(), prec, effective, supersedes, conf, "header")
    bod = _find_dates(body)
    if bod:
        _, date, prec = bod[0]
        return TemporalMeta(date.isoformat(), prec, effective, supersedes, 0.5, "body")
    if effective:
        return TemporalMeta(effective, "day", effective, supersedes, 0.7, "body")
    return TemporalMeta(None, None, None, supersedes, 0.0, "none")


LLM_PROMPT = """Extract temporal metadata from the document below. Reply with JSON only:
{"publication_date": "YYYY-MM-DD or null", "effective_date": "YYYY-MM-DD or null"}
Only report a date if the document explicitly states when it was published, issued or took effect.
Do not infer a date from historical facts mentioned in the content. If unsure, use null.

DOCUMENT:
"""


def extract_llm(text: str, model: str, client) -> TemporalMeta:
    from .generator import chat
    raw = chat(client, model, LLM_PROMPT + text, max_tokens=80)
    m = re.search(r"\{.*\}", raw, re.S)
    pub = eff = None
    if m:
        try:
            j = json.loads(m.group(0))
            pub = j.get("publication_date") or None
            eff = j.get("effective_date") or None
            for v in (pub, eff):
                if v:
                    dt.date.fromisoformat(v)
        except Exception:
            pub = eff = None
    sup = bool(SUPERSEDE_CUE.search(text))
    if pub or eff:
        return TemporalMeta(pub or eff, "day", eff, sup, 0.4, "llm")
    return TemporalMeta(None, None, None, sup, 0.0, "none")


def extract(text: str, llm_model: str | None = None, client=None) -> TemporalMeta:
    meta = extract_regex(text)
    if meta.pub_date is None and llm_model:
        meta = extract_llm(text, llm_model, client)
    return meta
