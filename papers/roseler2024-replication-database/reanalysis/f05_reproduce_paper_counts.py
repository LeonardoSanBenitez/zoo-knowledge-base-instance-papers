"""Reproduce the counts printed in Roeseler et al. (2024, JOPD 12:8) from the frozen version they analysed
(osf.io/qtkzy, 16 Oct 2023, served as CSV despite the .xlsx name).

Printed: 1,239 entries; 336 independent original studies; 468 independent replication findings; 201 entries not
in quantitative analyses; outcomes 641 informative failure / 447 success / 133 not available / 15 inconclusive /
3 practical failure; relative replication effect size (es_replication / es_original, es_original != 0):
k = 1,050, M = 0.52, SD = 0.98, Min -6.9, Max 22.82, Md 0.387. Fig 3: k = 1,051 pairs.

BLINDING NOTE: runs on the UNFILTERED file but prints only corpus-wide aggregates, never a row, a reference or a
per-paper value, so nothing about mark's 8 blinded papers can be read from the output.
Usage: python f05_reproduce_paper_counts.py <FReD_2023-10-16_qtkzy.csv>   Writes out/f05.json
"""
import json, os, sys
import numpy as np, pandas as pd
x = pd.read_csv(sys.argv[1], low_memory=False)
num = lambda s: pd.to_numeric(s, errors="coerce")
res = {"rows": int(len(x))}
res["result_counts"] = x["result"].fillna("NA").value_counts().to_dict()
res["unique_ref_original"] = int(x.ref_original.nunique())
res["unique_id_sample"] = int(x.id_sample.nunique())
res["exclusion_nonempty"] = int(x.exclusion.notna().sum())
eo, er = num(x.es_original), num(x.es_replication)
both = eo.notna() & er.notna()
res["pairs_with_both_es"] = int(both.sum())
m = both & (eo != 0)
rel = (er / eo)[m]
res["relative_es"] = {"k": int(m.sum()), "mean": round(float(rel.mean()), 3), "sd": round(float(rel.std()), 3), "min": round(float(rel.min()), 2),
                      "max": round(float(rel.max()), 2), "median": round(float(rel.median()), 3)}
# what share of 'success' is the both-non-significant kind (the paper's success definition includes it)
so, sr = num(x.significant_original), num(x.significant_replication)
res["success_with_both_nonsignificant"] = int(((x.result == "success") & (so == 0) & (sr == 0)).sum())
res["success_total"] = int((x.result == "success").sum())
res["share_orig_significant_among_coded"] = round(float((so == 1).sum() / so.notna().sum()), 3)
# median power of replications as computed in the file
res["power_median"] = round(float(num(x.power).median()), 3)
res["power_share_ge_.8"] = round(float((num(x.power) >= .8).mean()), 3)
print(json.dumps(res, indent=1, default=str))
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "f05.json"), "w"), indent=1, default=str)
