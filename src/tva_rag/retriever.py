"""Hybrid retrieval: BM25 + dense embeddings fused with reciprocal rank fusion."""
from __future__ import annotations
import re
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from .corpus import Document

TOKEN = re.compile(r"[a-z0-9]+")


def tokenize(s: str) -> list[str]:
    return TOKEN.findall(s.lower())


class HybridRetriever:
    def __init__(self, docs: list[Document], embed_model: str = "BAAI/bge-base-en-v1.5",
                 device: str | None = None, rrf_k: int = 60):
        self.docs = docs
        self.by_id = {d.doc_id: d for d in docs}
        self.bm25 = BM25Okapi([tokenize(d.text) for d in docs])
        self.embedder = SentenceTransformer(embed_model, device=device)
        self.doc_emb = self.embedder.encode([d.text for d in docs], normalize_embeddings=True,
                                            batch_size=64, show_progress_bar=False)
        self.rrf_k = rrf_k
        self.query_prefix = "Represent this sentence for searching relevant passages: " if "bge" in embed_model else ""

    def embed_query(self, q: str) -> np.ndarray:
        return self.embedder.encode([self.query_prefix + q], normalize_embeddings=True)[0]

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        return self.embedder.encode(texts, normalize_embeddings=True, show_progress_bar=False)

    def search(self, query: str, k: int = 5, mode: str = "hybrid") -> list[dict]:
        n = len(self.docs)
        bm = self.bm25.get_scores(tokenize(query))
        de = self.doc_emb @ self.embed_query(query)
        bm_rank = np.empty(n, int); bm_rank[np.argsort(-bm)] = np.arange(n)
        de_rank = np.empty(n, int); de_rank[np.argsort(-de)] = np.arange(n)
        if mode == "bm25":
            fused = -bm_rank.astype(float)
        elif mode == "dense":
            fused = -de_rank.astype(float)
        else:
            fused = 1.0 / (self.rrf_k + bm_rank) + 1.0 / (self.rrf_k + de_rank)
        order = np.argsort(-fused)[:k]
        return [dict(doc=self.docs[i], score=float(fused[i]), bm25_rank=int(bm_rank[i]),
                     dense_rank=int(de_rank[i]), dense_sim=float(de[i])) for i in order]
