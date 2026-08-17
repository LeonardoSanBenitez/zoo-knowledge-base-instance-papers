"""Collapse the 56MB of raw HELM JSON into one compact tidy table.

This is deliberately the same object as the authors'
`data/helm/all_mmlu_data_limitedcols.csv`, whose Git LFS pointer 404s
(see paper.json artifact a1, status: dangling). Building it here means the
reanalysis is reproducible by a peer without re-downloading 56MB, and the
repaired artifact is small enough to keep under the >50MB disk policy.

  raw JSON (56MB, regenerable via fetch_helm.py)  ->  responses.csv.gz (~1MB)

Columns: model, subject, item_id, chosen_text, correct_text, is_correct, n_options
Answers are stored as TEXT (HELM's mapped_output), not letters, so the table is
invariant to any per-model option shuffling.
"""
import json, os, glob, gzip, csv

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.environ.get("KB_HELM_RAW", os.path.join(HERE, "raw"))
OUT = os.path.join(os.path.dirname(HERE), "data", "helm_mmlu_responses.csv.gz")


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    n = skipped = 0
    with gzip.open(OUT, "wt", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["model", "subject", "item_id", "chosen_text",
                    "correct_text", "is_correct", "n_options"])
        for pf in sorted(glob.glob(os.path.join(RAW, "*.pred.json"))):
            base = os.path.basename(pf)[:-len(".pred.json")]
            model, subject = base.split("__")
            inf = os.path.join(RAW, base + ".inst.json")
            if not os.path.exists(inf):
                continue
            preds = json.load(open(pf, encoding="utf-8"))
            by_id = {i["id"]: i for i in json.load(open(inf, encoding="utf-8"))}
            for p in preds:
                inst = by_id.get(p["instance_id"])
                if inst is None:
                    skipped += 1
                    continue
                refs = inst["references"]
                corr = [r["output"]["text"] for r in refs
                        if "correct" in (r.get("tags") or [])]
                if len(corr) != 1:
                    skipped += 1
                    continue
                chosen = p.get("mapped_output")
                w.writerow([model, subject, p["instance_id"], chosen, corr[0],
                            int(chosen == corr[0]) if chosen is not None else "",
                            len(refs)])
                n += 1
    print(f"wrote {OUT}")
    print(f"  {n} rows, {skipped} skipped, {os.path.getsize(OUT)/1e6:.2f} MB gzipped")


if __name__ == "__main__":
    main()
