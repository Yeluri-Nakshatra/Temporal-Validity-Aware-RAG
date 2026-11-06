"""Label raw records (alias + LLM judge), compute all metrics, write tables and figures.

Outputs (results/):
  labeled.csv                 one row per generation with final label
  metrics_main.csv            accuracy / stale-follow / abstain per setting x model x mode x t_kind
  metrics_flip.csv            flip rate relative to closed-book-correct subset
  metrics_components.csv      extractor, retrieval, conflict-detector metrics
  metrics_validity.csv        VALID_FROM agreement with change date (tva mode)
  figures/*.png
"""
import sys, json, pathlib, argparse, datetime as dt, itertools
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from tva_rag.corpus import load_benchmark, load_documents, build_queries, Query
from tva_rag.judge import Judge, final_label
from tva_rag.generator import get_client, parse_answer
from tva_rag.temporal import extract_regex, extract_llm

ROOT = pathlib.Path(__file__).resolve().parents[1]
RES = ROOT / "results"; FIG = RES / "figures"; FIG.mkdir(parents=True, exist_ok=True)
MODE_ORDER = ["closed_book", "naive", "naive_trust", "recency", "tva"]
MODE_NAME = {"closed_book": "Closed-book", "naive": "Naive RAG", "naive_trust": "Naive RAG + trust",
             "recency": "Recency rerank", "tva": "TVA-RAG (ours)"}
PALETTE = {"closed_book": "#9CA3AF", "naive": "#60A5FA", "naive_trust": "#2563EB", "recency": "#F59E0B", "tva": "#7C3AED"}


def load_runs(path):
    rows = [json.loads(l) for l in pathlib.Path(path).read_text().splitlines() if l.strip()]
    return rows


def label_rows(rows, judge):
    out = []
    for r in rows:
        q = Query(item=r["item"], question=r["question"], domain=r["domain"], kind=r["kind"],
                  t=dt.date.fromisoformat(r["t"]), t_kind=r["t_kind"], gold=r["gold"], gold_label=r["gold_label"],
                  old_answer=r["old_answer"], new_answer=r["new_answer"], old_aliases=r["old_aliases"],
                  new_aliases=r["new_aliases"], change_date=r["change_date"], undated_old=r["undated_old"])
        parsed = dict(answer=r["answer"], abstain=r["abstain"])
        lab, method = final_label(q, parsed, judge)
        correct = (lab == r["gold_label"])
        stale = (r["gold_label"] == "NEW" and lab == "OLD")
        out.append(dict(setting=r["setting"], model=r["model"], mode=r["mode"], item=r["item"], domain=r["domain"],
                        kind=r["kind"], t_kind=r["t_kind"], gold_label=r["gold_label"], label=lab, method=method,
                        correct=correct, stale_follow=stale, abstain=(lab == "ABSTAIN"), answer=r["answer"],
                        valid_from=r.get("valid_from"), change_date=r.get("change_date"), undated_old=r["undated_old"],
                        latency_s=r.get("latency_s", np.nan), retrieved=json.dumps(r.get("retrieved", [])),
                        statuses=json.dumps(r.get("statuses", {})), conflicts=json.dumps(r.get("conflicts", {}))))
    return pd.DataFrame(out)


def main_metrics(df):
    g = df.groupby(["setting", "model", "mode", "t_kind"]).agg(
        n=("correct", "size"), accuracy=("correct", "mean"), stale_follow=("stale_follow", "mean"),
        abstain=("abstain", "mean"), latency_s=("latency_s", "mean")).reset_index()
    g["mode"] = pd.Categorical(g["mode"], MODE_ORDER)
    return g.sort_values(["setting", "model", "t_kind", "mode"])


def flip_metrics(df):
    """Flip rate: among reversal queries at t=now that the model answered correctly closed-book,
    fraction answered with the OLD answer under each RAG mode (the stale-document poisoning metric)."""
    cb = df[(df.setting == "mixed") & (df["mode"] == "closed_book") & (df.t_kind == "now")]
    cb_correct = cb[cb.correct][["model", "item"]]
    rows = []
    for (setting, model, mode), sub in df[(df.t_kind == "now") & (df["mode"] != "closed_book")].groupby(["setting", "model", "mode"]):
        m = sub.merge(cb_correct, on=["model", "item"])
        if len(m) == 0:
            continue
        rows.append(dict(setting=setting, model=model, mode=mode, n_cb_correct=len(m),
                         flip_to_old=m.stale_follow.mean(), flip_any=(~m.correct & ~m.abstain).mean(),
                         abstain=m.abstain.mean(), still_correct=m.correct.mean()))
    return pd.DataFrame(rows)


def validity_metrics(df):
    sub = df[(df["mode"] == "tva") & (df.setting == "mixed") & (df.t_kind == "now") & (df.kind == "reversal")].copy()
    def ok(row, tol_days):
        if not row.valid_from or not row.change_date:
            return False
        try:
            v = pd.to_datetime(row.valid_from, errors="coerce")
            if pd.isna(v): return False
            return abs((v.date() - dt.date.fromisoformat(row.change_date)).days) <= tol_days
        except Exception:
            return False
    sub["vf_stated"] = sub.valid_from.notna()
    sub["vf_exact31"] = sub.apply(lambda r: ok(r, 31), axis=1)
    sub["vf_year"] = sub.apply(lambda r: ok(r, 366), axis=1)
    return sub.groupby("model")[["vf_stated", "vf_exact31", "vf_year"]].mean().reset_index()


def component_metrics(judge_client):
    bench = load_benchmark()
    docs = load_documents(bench, "mixed")
    rows = []
    # extractor
    ok = 0; undated_ok = 0; n_undated = 0
    for d in docs:
        m = extract_regex(d.text)
        exp = None if d.undated else (d.true_effective or d.true_date)
        got = m.anchor().isoformat() if m.anchor() else None
        good = got == exp or (m.precision == "month" and got and exp and got[:7] == exp[:7])
        ok += good
        if d.undated:
            n_undated += 1; undated_ok += (got is None)
    rows.append(dict(component="temporal extractor (regex)", metric="anchor-date accuracy (all docs)", value=ok / len(docs), n=len(docs)))
    rows.append(dict(component="temporal extractor (regex)", metric="correct 'unknown' on undated docs", value=undated_ok / max(n_undated, 1), n=n_undated))
    # extractor LLM fallback on undated docs (hallucination check)
    halluc = 0
    for d in [x for x in docs if x.undated]:
        m = extract_llm(d.text, "llama3.1:8b", judge_client)
        halluc += m.pub_date is not None
    rows.append(dict(component="temporal extractor (LLM fallback, llama3.1:8b)", metric="hallucinated a date on undated docs", value=halluc / max(n_undated, 1), n=n_undated))
    # retrieval
    from tva_rag.retriever import HybridRetriever
    ret = HybridRetriever(docs, device="cuda")
    qs = [q for q in build_queries(bench) if q.t_kind == "now"]
    for mode in ["bm25", "dense", "hybrid"]:
        both = old = new = 0
        for q in qs:
            ids = [h["doc"].doc_id for h in ret.search(q.question, 5, mode)]
            o, nw = f"{q.item}#old" in ids, f"{q.item}#new" in ids
            old += o; new += nw; both += (o and nw)
        rows.append(dict(component=f"retrieval ({mode})", metric="recall@5 of current doc", value=new / len(qs), n=len(qs)))
        rows.append(dict(component=f"retrieval ({mode})", metric="recall@5 of stale doc", value=old / len(qs), n=len(qs)))
        rows.append(dict(component=f"retrieval ({mode})", metric="recall@5 of both docs", value=both / len(qs), n=len(qs)))
    return pd.DataFrame(rows), docs


def conflict_metrics(df):
    """Pair-level precision/recall of the conflict detector from the tva-mode records (mixed setting)."""
    sub = df[(df["mode"] == "tva") & (df.setting == "mixed")].drop_duplicates(["item", "t_kind"])
    tp = fp = fn = 0; status_ok = 0; status_n = 0
    for _, r in sub.iterrows():
        retrieved = json.loads(r.retrieved); conflicts = json.loads(r.conflicts); statuses = json.loads(r.statuses)
        flagged = set()
        for a, lst in conflicts.items():
            for b, *_ in lst:
                flagged.add(tuple(sorted((a, b))))
        truth = set(); offtopic = set()
        for a, b in itertools.combinations(retrieved, 2):
            if a.split("#")[0] == b.split("#")[0] and a != b:
                (truth if a.split("#")[0] == r["item"] else offtopic).add(tuple(sorted((a, b))))
        flagged -= offtopic  # same-item pairs about another question are neither hits nor false alarms
        tp += len(flagged & truth); fp += len(flagged - truth); fn += len(truth - flagged)
        # status correctness for the item's own docs
        if r.kind == "reversal":
            o, n = f"{r['item']}#old", f"{r['item']}#new"
            if r.t_kind == "now":
                if n in statuses:
                    status_n += 1; status_ok += statuses[n] == "CURRENT"
                if o in statuses:
                    status_n += 1; status_ok += statuses[o] in ("SUPERSEDED", "UNVERIFIED")
            else:
                if o in statuses:
                    status_n += 1; status_ok += statuses[o] in ("CURRENT", "UNCONFLICTED", "UNVERIFIED")
    prec = tp / max(tp + fp, 1); rec = tp / max(tp + fn, 1)
    return pd.DataFrame([
        dict(component="conflict detector", metric="pair precision", value=prec, n=tp + fp),
        dict(component="conflict detector", metric="pair recall", value=rec, n=tp + fn),
        dict(component="conflict detector", metric="pair F1", value=2 * prec * rec / max(prec + rec, 1e-9), n=tp + fp + fn),
        dict(component="status assignment", metric="item-doc status correct", value=status_ok / max(status_n, 1), n=status_n),
    ])


def figures(main, flip, df):
    models = list(main.model.unique())
    # Fig 1: accuracy at t=now and t=past, mixed setting
    for tk, title in [("now", "Reversal questions, reference date = 2026-01-01 (gold = current answer)"),
                      ("past", "Reversal questions, reference date before the change (gold = historical answer)"),
                      ("ctl", "Control questions (stable facts)")]:
        sub = main[(main.setting == "mixed") & (main.t_kind == tk)]
        fig, ax = plt.subplots(figsize=(9, 4))
        w = 0.8 / len(MODE_ORDER)
        for i, mode in enumerate(MODE_ORDER):
            vals = [sub[(sub.model == m) & (sub["mode"] == mode)].accuracy.mean() for m in models]
            ax.bar(np.arange(len(models)) + i * w, vals, w, label=MODE_NAME[mode], color=PALETTE[mode])
        ax.set_xticks(np.arange(len(models)) + 0.4 - w / 2); ax.set_xticklabels(models)
        ax.set_ylim(0, 1); ax.set_ylabel("accuracy"); ax.set_title(title, fontsize=10)
        ax.legend(fontsize=8, ncol=3, frameon=False); ax.spines[["top", "right"]].set_visible(False)
        fig.tight_layout(); fig.savefig(FIG / f"accuracy_{tk}.png", dpi=160); plt.close(fig)
    # Fig 2: stale-follow rate at t=now (mixed)
    sub = main[(main.setting == "mixed") & (main.t_kind == "now") & (main["mode"] != "closed_book")]
    fig, ax = plt.subplots(figsize=(9, 4))
    modes = [m for m in MODE_ORDER if m != "closed_book"]; w = 0.8 / len(modes)
    for i, mode in enumerate(modes):
        vals = [sub[(sub.model == m) & (sub["mode"] == mode)].stale_follow.mean() for m in models]
        ax.bar(np.arange(len(models)) + i * w, vals, w, label=MODE_NAME[mode], color=PALETTE[mode])
    ax.set_xticks(np.arange(len(models)) + 0.4 - w / 2); ax.set_xticklabels(models)
    ax.set_ylabel("stale-answer rate"); ax.set_title("Rate of answering with the superseded (stale) answer, mixed corpus, t = 2026-01-01", fontsize=10)
    ax.legend(fontsize=8, frameon=False); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(FIG / "stale_follow_now.png", dpi=160); plt.close(fig)
    # Fig 3: flip rate, stale-only setting (poisoning replication)
    sub = flip[flip.setting == "stale_only"]
    if len(sub):
        fig, ax = plt.subplots(figsize=(9, 4))
        modes = ["naive", "naive_trust", "tva"]; w = 0.8 / len(modes)
        for i, mode in enumerate(modes):
            vals = [sub[(sub.model == m) & (sub["mode"] == mode)].flip_to_old.mean() for m in models]
            ax.bar(np.arange(len(models)) + i * w, vals, w, label=MODE_NAME[mode], color=PALETTE[mode])
        ax.set_xticks(np.arange(len(models)) + 0.4 - w / 2); ax.set_xticklabels(models)
        ax.set_ylabel("flip rate"); ax.set_title("Stale-document poisoning: fraction of closed-book-correct answers flipped to the stale answer", fontsize=10)
        ax.legend(fontsize=8, frameon=False); ax.spines[["top", "right"]].set_visible(False)
        fig.tight_layout(); fig.savefig(FIG / "flip_stale_only.png", dpi=160); plt.close(fig)
    # Fig 4: per-domain accuracy for tva vs naive at t=now
    sub = df[(df.setting == "mixed") & (df.t_kind == "now") & (df["mode"].isin(["naive", "tva"]))]
    piv = sub.groupby(["domain", "mode"]).correct.mean().unstack()
    fig, ax = plt.subplots(figsize=(9, 4))
    piv.plot.bar(ax=ax, color=[PALETTE[c] for c in piv.columns], width=0.7)
    ax.set_ylim(0, 1); ax.set_ylabel("accuracy"); ax.set_xlabel(""); ax.set_title("Accuracy by domain (all models pooled), t = 2026-01-01", fontsize=10)
    ax.legend([MODE_NAME[c] for c in piv.columns], fontsize=8, frameon=False); ax.spines[["top", "right"]].set_visible(False)
    plt.setp(ax.get_xticklabels(), rotation=0)
    fig.tight_layout(); fig.savefig(FIG / "accuracy_by_domain.png", dpi=160); plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default=str(RES / "runs.jsonl"))
    ap.add_argument("--judge-model", default="qwen3.5:35b")
    ap.add_argument("--skip-components", action="store_true")
    args = ap.parse_args()
    client = get_client()
    judge = Judge(client, args.judge_model, RES / "judge_cache.json")
    rows = load_runs(args.runs)
    df = label_rows(rows, judge)
    df.to_csv(RES / "labeled.csv", index=False)
    main = main_metrics(df); main.to_csv(RES / "metrics_main.csv", index=False)
    flip = flip_metrics(df); flip.to_csv(RES / "metrics_flip.csv", index=False)
    val = validity_metrics(df); val.to_csv(RES / "metrics_validity.csv", index=False)
    comp = conflict_metrics(df)
    if not args.skip_components:
        comp2, _ = component_metrics(client)
        comp = pd.concat([comp2, comp], ignore_index=True)
    comp.to_csv(RES / "metrics_components.csv", index=False)
    figures(main, flip, df)
    pd.set_option("display.width", 200); pd.set_option("display.max_rows", 500)
    print("\n== MAIN ==\n", main.round(3).to_string(index=False))
    print("\n== FLIP ==\n", flip.round(3).to_string(index=False))
    print("\n== VALIDITY ==\n", val.round(3).to_string(index=False))
    print("\n== COMPONENTS ==\n", comp.round(3).to_string(index=False))
    print("\nlabel method share:", df.method.value_counts(normalize=True).round(3).to_dict())


if __name__ == "__main__":
    main()
