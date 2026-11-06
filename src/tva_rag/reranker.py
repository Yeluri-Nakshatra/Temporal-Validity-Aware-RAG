"""Validity-aware reranking: final score = retrieval score x validity(t) x source trust."""
from __future__ import annotations
from .conflict import Evidence


def rerank(evs: list[Evidence], trust: dict[str, float] | None = None) -> list[Evidence]:
    trust = trust or {}
    for e in evs:
        e.final_score = e.retrieval_score * e.validity * trust.get(e.doc_id, 1.0)
    live = [e for e in evs if e.status != "FUTURE"]
    return sorted(live, key=lambda e: e.final_score, reverse=True)


def recency_sort(evs: list[Evidence]) -> list[Evidence]:
    """Baseline from the stale-document poisoning paper: order by date only, newest first."""
    import datetime as dt
    return sorted(evs, key=lambda e: e.anchor or dt.date.min, reverse=True)
