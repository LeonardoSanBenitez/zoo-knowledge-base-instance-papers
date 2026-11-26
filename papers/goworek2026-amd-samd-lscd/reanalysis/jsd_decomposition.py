"""JSD(P1,P2) (base 2, equal weights) = H(M) - (H(P1)+H(P2))/2 with M = (P1+P2)/2: the gold change score as
'mixture entropy minus mean within-period entropy'. Per set: identity check, sd of each term across words, and Spearman
of JSD with each term. Run: python jsd_decomposition.py NAME=SUBTASK1_JSONL ... > jsd_decomposition.json
"""
import json, sys
from collections import defaultdict
import numpy as np
from scipy.spatial.distance import jensenshannon
from scipy.stats import spearmanr


def H(p):
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


out = {}
for arg in sys.argv[1:]:
    name, path = arg.split("=", 1)
    by = defaultdict(list)
    for l in open(path, encoding="utf-8"):
        r = json.loads(l); by[r["word"]].append((r["period_label"], r["label"][0]))
    J, HM, HW = [], [], []
    for w, xs in by.items():
        ps = sorted({p for p, _ in xs}); ss = sorted({s for _, s in xs})
        if len(ps) != 2:
            continue
        P = np.array([[sum(1 for p, s in xs if p == q and s == t) for t in ss] for q in ps], float)
        P = P / P.sum(1, keepdims=True)
        J.append(float(jensenshannon(P[0], P[1], base=2)) ** 2 if len(ss) > 1 else 0.0)   # scipy returns the distance = sqrt(divergence)
        HM.append(H((P[0] + P[1]) / 2)); HW.append((H(P[0]) + H(P[1])) / 2)
    J, HM, HW = map(np.array, (J, HM, HW))
    out[name] = {"n_words": len(J), "identity_max_abs_err": float(np.abs(J - (HM - HW)).max()),
                 "sd_HM": float(HM.std()), "sd_HW": float(HW.std()),
                 "rho_JSDdiv_HM": float(spearmanr(J, HM)[0]), "rho_JSDdiv_HW": float(spearmanr(J, HW)[0]),
                 "rho_JSDdist_HM": float(spearmanr(np.sqrt(J), HM)[0])}
print(json.dumps(out, indent=1))
