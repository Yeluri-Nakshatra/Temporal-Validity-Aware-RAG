"""Benchmark and corpus loading."""
from __future__ import annotations
import json, datetime as dt
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


@dataclass
class Document:
    doc_id: str
    item: str
    role: str            # old | new | control
    title: str
    text: str
    true_date: str
    true_effective: Optional[str]
    undated: bool

    @property
    def body(self) -> str:
        return self.text.split("\n\n", 1)[-1]


@dataclass
class Query:
    item: str
    question: str
    domain: str
    kind: str                 # reversal | control
    t: dt.date               # reference date
    t_kind: str               # now | past | ctl
    gold: str                 # expected answer text
    gold_label: str           # NEW | OLD | CTL
    old_answer: str = ""
    new_answer: str = ""
    old_aliases: list = field(default_factory=list)
    new_aliases: list = field(default_factory=list)
    change_date: Optional[str] = None
    undated_old: bool = False


def parse_date(s: str) -> dt.date:
    return dt.date.fromisoformat(s)


def load_benchmark(path: Path | None = None) -> dict:
    path = path or DATA_DIR / "temprev.json"
    return json.loads(Path(path).read_text())


def load_documents(bench: dict, setting: str = "mixed") -> list[Document]:
    """setting: 'mixed' = all docs; 'stale_only' = drop the current ('new') docs."""
    docs = []
    for d in bench["documents"]:
        if setting == "stale_only" and d["role"] == "new":
            continue
        docs.append(Document(d["doc_id"], d["item"], d["role"], d["title"], d["text"],
                             d["true_date"], d["true_effective"], d["undated"]))
    return docs


T_NOW = dt.date(2026, 1, 1)


def midpoint(a: str, b: str) -> dt.date:
    da, db = parse_date(a), parse_date(b)
    return da + (db - da) / 2


def build_queries(bench: dict, include_past: bool = True, include_controls: bool = True) -> list[Query]:
    qs = []
    for it in bench["reversals"]:
        base = dict(item=it["id"], question=it["question"], domain=it["domain"], kind="reversal",
                    old_answer=it["old"]["answer"], new_answer=it["new"]["answer"],
                    old_aliases=it["old"]["aliases"], new_aliases=it["new"]["aliases"],
                    change_date=it["change_date"], undated_old=it["undated_old"])
        qs.append(Query(t=T_NOW, t_kind="now", gold=it["new"]["answer"], gold_label="NEW", **base))
        if include_past:
            tp = parse_date(it["t_past"]) if it.get("t_past") else midpoint(it["old"]["date"], it["change_date"])
            qs.append(Query(t=tp, t_kind="past", gold=it["old"]["answer"], gold_label="OLD", **base))
    if include_controls:
        for it in bench["controls"]:
            qs.append(Query(item=it["id"], question=it["question"], domain=it["domain"], kind="control",
                            t=T_NOW, t_kind="ctl", gold=it["answer"], gold_label="CTL",
                            new_answer=it["answer"], new_aliases=it["aliases"]))
    return qs
