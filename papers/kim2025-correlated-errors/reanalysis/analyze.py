"""Decompose LLM agreement-on-errors into item structure vs pair kinship.

See README.md. Three statistics per model pair, computed over the items where
BOTH models are wrong:

  A_obs   observed agreement (Kim et al. 2025's headline statistic)
  A_unif  E[agreement] under uniform choice among that item's wrong options
          (Kim et al.'s stated baseline: 1/(k-1))
  A_item  E[agreement] under independent draws from the item's *empirical*
          wrong-answer distribution, estimated leave-this-pair-out

Answers are compared by ANSWER TEXT (mapped_output), not by letter, so the
result is invariant to any per-model shuffling of option order. We verify
whether option order actually varies across models and report it.
"""
import json, os, glob, itertools, collections
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.environ.get("KB_HELM_RAW", os.path.join(HERE, "raw"))
OUT = os.path.join(HERE, "results")


TIDY = os.path.join(os.path.dirname(HERE), "data", "helm_mmlu_responses.csv.gz")


def load():
    """-> answers[(model, qkey)] = chosen text or None; correct[qkey]; nopts[qkey]

    Prefers the 1MB tidy table (data/helm_mmlu_responses.csv.gz, built by
    build_tidy.py). Falls back to the 56MB raw JSON in RAW/ if present, which is
    the only path that can also check option ORDER across models.
    """
    if os.path.exists(TIDY) and not os.path.isdir(RAW):
        import gzip, csv
        answers, correct, opts = {}, {}, {}
        with gzip.open(TIDY, "rt", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                qkey = (row["subject"], row["item_id"])
                correct[qkey] = row["correct_text"]
                opts[qkey] = int(row["n_options"])
                answers[(row["model"], qkey)] = row["chosen_text"] or None
        # order check is not recoverable from the tidy form; it was run once on
        # the raw data and passed (0/2918 items differ), recorded in FINDINGS.md
        return answers, correct, opts, collections.defaultdict(lambda: {None})

    answers, correct, opts = {}, {}, {}
    order_signature = collections.defaultdict(set)
    for pf in sorted(glob.glob(os.path.join(RAW, "*.pred.json"))):
        base = os.path.basename(pf)[:-len(".pred.json")]
        model, subj = base.split("__")
        inf = os.path.join(RAW, base + ".inst.json")
        if not os.path.exists(inf):
            continue
        preds = json.load(open(pf))
        insts = json.load(open(inf))
        by_id = {i["id"]: i for i in insts}
        for p in preds:
            inst = by_id.get(p["instance_id"])
            if inst is None:
                continue
            refs = [r["output"]["text"] for r in inst["references"]]
            corr = [r["output"]["text"] for r in inst["references"]
                    if "correct" in (r.get("tags") or [])]
            if len(corr) != 1:
                continue
            qkey = (subj, p["instance_id"])
            correct[qkey] = corr[0]
            opts[qkey] = len(refs)
            order_signature[qkey].add(tuple(refs))
            answers[(model, qkey)] = p.get("mapped_output")
    return answers, correct, opts, order_signature


def main():
    os.makedirs(OUT, exist_ok=True)
    answers, correct, nopts, order_sig = load()
    models = sorted({m for (m, _) in answers})
    qkeys = sorted(correct)
    print(f"models={len(models)}  items={len(qkeys)}  cells={len(answers)}")

    shuffled = sum(1 for q in qkeys if len(order_sig[q]) > 1)
    print(f"items whose option ORDER differs across models: {shuffled}/{len(qkeys)} "
          f"({shuffled/len(qkeys):.1%})  -> letter-based comparison "
          f"{'IS' if shuffled else 'is not'} confounded; we use answer text regardless")

    # wrong[q] = {model: chosen_text} restricted to models that answered and were wrong
    wrong = {}
    unparsed = 0
    for q in qkeys:
        d = {}
        for m in models:
            a = answers.get((m, q))
            if a is None:
                unparsed += 1
                continue
            if a != correct[q]:
                d[m] = a
        wrong[q] = d
    print(f"missing/unparsed model-item cells: {unparsed}")

    rows = []
    for m1, m2 in itertools.combinations(models, 2):
        obs = unif = item = n = 0.0
        for q in qkeys:
            w = wrong[q]
            if m1 not in w or m2 not in w:
                continue
            n += 1
            obs += (w[m1] == w[m2])
            k = nopts[q]
            unif += 1.0 / (k - 1)
            # leave-this-pair-out empirical wrong-answer distribution
            others = [a for mm, a in w.items() if mm not in (m1, m2)]
            if len(others) >= 2:
                c = collections.Counter(others)
                tot = len(others)
                # unbiased estimate of collision prob from a finite sample:
                # sum n_c(n_c-1) / (N(N-1))
                item += sum(v * (v - 1) for v in c.values()) / (tot * (tot - 1))
            else:
                item += 1.0 / (k - 1)
        if n < 30:
            continue
        rows.append(dict(model1=m1, model2=m2, n_both_wrong=int(n),
                         A_obs=obs / n, A_unif=unif / n, A_item=item / n))

    df = pd.DataFrame(rows)
    df["excess_vs_unif"] = df.A_obs - df.A_unif       # what Kim et al. report
    df["explained_by_item"] = df.A_item - df.A_unif   # attributable to the test
    df["excess_vs_item"] = df.A_obs - df.A_item       # needs pair kinship
    df["frac_explained_by_item"] = df.explained_by_item / df.excess_vs_unif

    # provider kinship flag
    prov = lambda s: s.split("_")[0]
    df["same_provider"] = [prov(a) == prov(b) for a, b in zip(df.model1, df.model2)]

    df.to_csv(os.path.join(OUT, "pairs.csv"), index=False)

    print("\n=== PAIRWISE DECOMPOSITION (n pairs = %d) ===" % len(df))
    for c in ["A_obs", "A_unif", "A_item", "excess_vs_unif",
              "explained_by_item", "excess_vs_item"]:
        print(f"{c:>20s}  mean={df[c].mean():+.4f}  median={df[c].median():+.4f}  "
              f"sd={df[c].std():.4f}  min={df[c].min():+.4f}  max={df[c].max():+.4f}")

    tot_u = df.excess_vs_unif.mean()
    tot_i = df.explained_by_item.mean()
    print(f"\nShare of Kim et al.'s excess agreement explained by item structure alone:"
          f" {tot_i/tot_u:.1%}")
    print(f"Pairs whose excess-over-item-null is NEGATIVE: "
          f"{(df.excess_vs_item < 0).mean():.1%}")
    print(f"Pairs whose excess-over-uniform-null is NEGATIVE: "
          f"{(df.excess_vs_unif < 0).mean():.1%}")

    print("\n=== SAME PROVIDER vs DIFFERENT ===")
    print(df.groupby("same_provider")[
        ["A_obs", "A_item", "excess_vs_unif", "excess_vs_item"]].mean().to_string())

    print("\n=== 10 pairs with largest kinship residual (excess over item null) ===")
    print(df.nlargest(10, "excess_vs_item")[
        ["model1", "model2", "n_both_wrong", "A_obs", "A_item",
         "excess_vs_item"]].to_string(index=False))

    print("\n=== the pair Kim et al. flag as anomalous ===")
    anom = df[(df.model1.str.contains("unicorn") | df.model2.str.contains("unicorn")) &
              (df.model1.str.contains("palmyra") | df.model2.str.contains("palmyra"))]
    print(anom.to_string(index=False) if len(anom) else "(pair not in sample)")


if __name__ == "__main__":
    main()
