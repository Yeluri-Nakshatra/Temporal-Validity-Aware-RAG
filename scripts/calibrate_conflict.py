"""Pair-level precision/recall of the conflict detectors on all retrieved pairs (t = now queries)."""
import sys, itertools, time, pandas as pd
sys.path.insert(0, "src")
from tva_rag.corpus import load_benchmark, load_documents, build_queries
from tva_rag.retriever import HybridRetriever
from tva_rag.conflict import ConflictDetector, Evidence
from tva_rag.temporal import extract_regex
from tva_rag.generator import get_client

bench = load_benchmark(); docs = load_documents(bench, "mixed")
ret = HybridRetriever(docs, device="cuda"); client = get_client()
meta = {d.doc_id: extract_regex(d.text) for d in docs}
dets = {"claims/qwen3.5:35b": ConflictDetector("claims", client, "qwen3.5:35b", embed_fn=ret.embed_texts, cache_path="results/detector_cache_claims_mixed_qwen3.5_35b.json"),
        "claims/llama3.1:8b": ConflictDetector("claims", client, "llama3.1:8b", embed_fn=ret.embed_texts, cache_path="results/detector_cache_claims_mixed_llama3.1_8b.json"),
        "nli": ConflictDetector("nli", embed_fn=ret.embed_texts, device="cuda")}
rows = []
for q in [x for x in build_queries(bench) if x.t_kind == "now"]:
    hits = ret.search(q.question, 5)
    for name, det in dets.items():
        evs = [Evidence(h["doc"].doc_id, h["doc"].title, h["doc"].text, meta[h["doc"].doc_id], h["score"]) for h in hits]
        t0 = time.time(); pairs = det.find_conflicts(q.question, evs); dt_ = time.time() - t0
        flagged = {tuple(sorted((evs[i].doc_id, evs[j].doc_id))) for i, j, _ in pairs}
        for a, b in itertools.combinations([e.doc_id for e in evs], 2):
            same_item = a.split("#")[0] == b.split("#")[0]
            if same_item and a.split("#")[0] != q.item:
                continue  # off-topic same-item pair: neither a hit nor a false alarm for this question
            rows.append(dict(detector=name, item=q.item, a=a, b=b, truth=same_item,
                             pred=tuple(sorted((a, b))) in flagged, secs=dt_))
df = pd.DataFrame(rows); df.to_csv("results/conflict_pairs_eval.csv", index=False)
for name, sub in df.groupby("detector"):
    tp = (sub.pred & sub.truth).sum(); fp = (sub.pred & ~sub.truth).sum(); fn = (~sub.pred & sub.truth).sum()
    p = tp / max(tp + fp, 1); r = tp / max(tp + fn, 1)
    print(f"{name:7s} P={p:.3f} R={r:.3f} F1={2*p*r/max(p+r,1e-9):.3f} tp={tp} fp={fp} fn={fn} mean_secs/query={sub.groupby('item').secs.first().mean():.2f}")
for name in dets:
    print(name, 'FP:', df[(df.detector==name)&df.pred&~df.truth][['a','b']].values.tolist()[:6])
    print(name, 'FN:', df[(df.detector==name)&~df.pred&df.truth][['a','b']].values.tolist()[:6])
