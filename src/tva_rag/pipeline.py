"""End-to-end TVA-RAG pipeline with switchable system variants.

modes:
  closed_book  - no retrieval
  naive        - hybrid top-k, raw documents, no temporal reasoning
  naive_trust  - naive + "answer must follow the documents" (poisoning-paper condition)
  recency      - hybrid top-k ordered newest-first by extracted date (paper's baseline)
  tva          - conflict detection + validity-aware rerank + validity prompting + abstention
"""
from __future__ import annotations
import datetime as dt, time
from .corpus import Document
from .temporal import extract, TemporalMeta
from .retriever import HybridRetriever
from .conflict import ConflictDetector, Evidence
from .reranker import rerank, recency_sort
from . import generator as G

MODES = ["closed_book", "naive", "naive_trust", "recency", "tva"]


class TVARAG:
    def __init__(self, docs: list[Document], client, embed_model="BAAI/bge-base-en-v1.5",
                 device=None, k=5, llm_date_model: str | None = None,
                 detector_method: str = "claims", detector_model: str = "qwen3.5:35b",
                 detector_cache: str | None = None):
        self.client, self.k = client, k
        self.retriever = HybridRetriever(docs, embed_model, device)
        self.detector = ConflictDetector(detector_method, client, detector_model,
                                         embed_fn=self.retriever.embed_texts, cache_path=detector_cache, device=device)
        self.meta: dict[str, TemporalMeta] = {d.doc_id: extract(d.text, llm_date_model, client) for d in docs}
        self.single_doc_setting = all(d.role != "new" for d in docs)

    def retrieve(self, question: str) -> list[Evidence]:
        hits = self.retriever.search(question, self.k)
        return [Evidence(h["doc"].doc_id, h["doc"].title, h["doc"].text, self.meta[h["doc"].doc_id], h["score"]) for h in hits]

    def answer(self, question: str, t: dt.date, mode: str, model: str) -> dict:
        t0 = time.time()
        rec = dict(mode=mode, model=model, t=t.isoformat(), retrieved=[], statuses={}, prompt="")
        if mode == "closed_book":
            prompt = G.prompt_closed_book(question, t)
        else:
            evs = self.retrieve(question)
            rec["retrieved"] = [e.doc_id for e in evs]
            if mode in ("naive", "naive_trust"):
                prompt = G.prompt_rag(question, evs, trust_instruction=(mode == "naive_trust"), t=t)
            elif mode == "recency":
                evs = recency_sort(evs)
                prompt = G.prompt_rag(question, evs, t=t)
            elif mode == "tva":
                evs = self.detector.detect(question, evs, t)
                evs = rerank(evs)
                rec["statuses"] = {e.doc_id: e.status for e in evs}
                rec["conflicts"] = {e.doc_id: e.conflicts_with for e in evs if e.conflicts_with}
                rec["claims"] = {e.doc_id: e.claim for e in evs if e.claim}
                if self.single_doc_setting:
                    prompt = G.prompt_tva_single(question, evs, t)
                else:
                    prompt = G.prompt_tva(question, evs, t)
            else:
                raise ValueError(mode)
            rec["context_order"] = [e.doc_id for e in evs]
        raw = G.chat(self.client, model, prompt, system=G.SYSTEM)
        rec.update(G.parse_answer(raw))
        rec["prompt"] = prompt
        rec["latency_s"] = round(time.time() - t0, 2)
        return rec
