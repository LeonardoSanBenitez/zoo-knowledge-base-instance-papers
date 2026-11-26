"""Period-blind GOLD statistics vs the gold change score (cluster JSD) on two-period DWUG sets.

    python gold_entropy.py NAME=SUBTASK1_JSONL ... > gold_entropy.json

Per word: JSD (base 2) between the two periods' gold sense distributions; K = number of senses; H = entropy (bits) of the
POOLED sense distribution (periods ignored). Spearman of JSD with K and with H. No embeddings: this asks what the gold rewards.
"""
import json, sys
from collections import Counter, defaultdict
import numpy as np
from scipy.spatial.distance import jensenshannon
from scipy.stats import spearmanr

out = {}
for arg in sys.argv[1:]:
    name, path = arg.split("=", 1)
    by = defaultdict(list)
    for l in open(path, encoding="utf-8"):
        r = json.loads(l); by[r["word"]].append((r["period_label"], r["label"][0]))
    J, K, H = [], [], []
    for w, xs in by.items():
        ps = sorted({p for p, _ in xs})
        if len(ps) != 2:
            continue
        ss = sorted({s for _, s in xs})
        P = np.array([[sum(1 for p, s in xs if p == q and s == t) for t in ss] for q in ps], float)
        P = P / P.sum(1, keepdims=True)
        J.append(float(jensenshannon(P[0], P[1], base=2)) if len(ss) > 1 else 0.0)
        c = np.array(list(Counter(s for _, s in xs).values()), float); c /= c.sum()
        K.append(len(ss)); H.append(float(-(c * np.log2(c)).sum()))
    out[name] = {"n_words": len(J), "rho_JSD_K": float(spearmanr(J, K)[0]), "rho_JSD_Hpooled": float(spearmanr(J, H)[0])}
print(json.dumps(out, indent=1))
