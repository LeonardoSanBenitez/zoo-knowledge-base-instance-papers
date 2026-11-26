"""How much of the gold change ranking is finite-sample bias? Per word: gold JSD (base 2, distance as scipy returns it,
the same quantity as gold_entropy.py) vs the mean JSD over 50 permutations of the gold PERIOD labels within the word
(true change removed, period sizes and sense counts kept). Spearman(gold, null mean) and the share of words whose gold JSD
exceeds the null 95th percentile. Run: python null_jsd.py NAME=SUBTASK1_JSONL ... > null_jsd.json
"""
import json, sys
from collections import defaultdict
import numpy as np
from scipy.spatial.distance import jensenshannon
from scipy.stats import spearmanr


def jsd(per, sen, ps, ss):
    P = np.array([[np.sum((per == q) & (sen == t)) for t in ss] for q in ps], float)
    P = P / P.sum(1, keepdims=True)
    return float(jensenshannon(P[0], P[1], base=2)) if len(ss) > 1 else 0.0


rng = np.random.default_rng(0)
out = {}
for arg in sys.argv[1:]:
    name, path = arg.split("=", 1)
    by = defaultdict(list)
    for l in open(path, encoding="utf-8"):
        r = json.loads(l); by[r["word"]].append((r["period_label"], r["label"][0]))
    G, N, sig = [], [], 0
    for w, xs in by.items():
        ps = sorted({p for p, _ in xs}); ss = sorted({s for _, s in xs})
        if len(ps) != 2:
            continue
        per = np.array([p for p, _ in xs]); sen = np.array([s for _, s in xs])
        g = jsd(per, sen, ps, ss)
        null = [jsd(rng.permutation(per), sen, ps, ss) for _ in range(50)]
        G.append(g); N.append(float(np.mean(null))); sig += g > np.percentile(null, 95)
    out[name] = {"n_words": len(G), "rho_gold_vs_nullmean": float(spearmanr(G, N)[0]),
                 "mean_gold": float(np.mean(G)), "mean_null": float(np.mean(N)), "share_gold_above_null95": sig / len(G)}
print(json.dumps(out, indent=1))
