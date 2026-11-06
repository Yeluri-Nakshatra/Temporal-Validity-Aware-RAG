"""Run all system variants over the TempRev benchmark and append raw records to a JSONL file.

Example:
  python scripts/run_experiments.py --models llama3.1:8b qwen2.5:7b --settings mixed stale_only
Resumable: records already present in the output file are skipped.
"""
import sys, json, argparse, time, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from tqdm import tqdm
from tva_rag.corpus import load_benchmark, load_documents, build_queries
from tva_rag.pipeline import TVARAG
from tva_rag.generator import get_client

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODES_BY_SETTING = {
    "mixed": ["closed_book", "naive", "naive_trust", "recency", "tva"],
    "stale_only": ["naive", "naive_trust", "tva"],
}


def key(r):
    return (r["setting"], r["mode"], r["model"], r["item"], r["t_kind"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=["llama3.1:8b"])
    ap.add_argument("--settings", nargs="+", default=["mixed", "stale_only"])
    ap.add_argument("--modes", nargs="+", default=None)
    ap.add_argument("--out", default=str(ROOT / "results" / "runs.jsonl"))
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--limit", type=int, default=0, help="debug: limit queries per setting")
    ap.add_argument("--detector", default="claims", choices=["claims", "nli"])
    ap.add_argument("--detector-model", default="qwen3.5:35b")
    args = ap.parse_args()

    out = pathlib.Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out.exists():
        for line in out.read_text().splitlines():
            if line.strip():
                done.add(key(json.loads(line)))
    print(f"{len(done)} records already present")

    bench = load_benchmark()
    client = get_client()
    for setting in args.settings:
        docs = load_documents(bench, setting)
        tag = args.detector_model.replace(":", "_")
        system = TVARAG(docs, client, device="cuda", k=args.k, detector_method=args.detector, detector_model=args.detector_model,
                        detector_cache=str(ROOT / "results" / f"detector_cache_{args.detector}_{setting}_{tag}.json"))
        qs = build_queries(bench, include_past=(setting == "mixed"), include_controls=True)
        if args.limit:
            qs = qs[: args.limit]
        modes = args.modes or MODES_BY_SETTING[setting]
        with out.open("a") as f:
            for model in args.models:
                for mode in modes:
                    todo = [q for q in qs if (setting, mode, model, q.item, q.t_kind) not in done]
                    for q in tqdm(todo, desc=f"{setting}/{model}/{mode}", ncols=100):
                        try:
                            rec = system.answer(q.question, q.t, mode, model)
                        except Exception as ex:  # keep going, log the failure
                            rec = dict(mode=mode, model=model, t=q.t.isoformat(), error=str(ex), answer="", raw="",
                                       abstain=False, valid_from=None, basis=None, retrieved=[], statuses={}, prompt="")
                        rec.update(setting=setting, item=q.item, t_kind=q.t_kind, kind=q.kind, domain=q.domain,
                                   question=q.question, gold=q.gold, gold_label=q.gold_label,
                                   old_answer=q.old_answer, new_answer=q.new_answer,
                                   old_aliases=q.old_aliases, new_aliases=q.new_aliases,
                                   change_date=q.change_date, undated_old=q.undated_old, ts=time.time())
                        f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
                        done.add(key(rec))


if __name__ == "__main__":
    main()
