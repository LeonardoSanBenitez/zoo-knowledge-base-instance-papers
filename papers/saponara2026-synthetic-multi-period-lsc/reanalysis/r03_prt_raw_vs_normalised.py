"""Does PRT depend on whether usage embeddings are L2-normalised before averaging? r01 averaged normalised vectors
(PRT 0.367, outside the paper's 0.473 by bootstrap, r02). Here: PRT from RAW XL-LEXEME vectors (embed.py --raw),
same lemmas, same gold q, same periods; bootstrap over lemmas as in r02.

    python r03_prt_raw_vs_normalised.py <synthetic dir> <gold EN dir> <normalised emb dir> <raw emb dir> [n_boot]
"""
import contextlib
import io
import json
import os
import runpy
import sys

import numpy as np
from scipy.stats import spearmanr

SYN, GOLD, EMBN, EMBR = sys.argv[1:5]
n_boot = int(sys.argv[5]) if len(sys.argv) > 5 else 400
sys.argv = [sys.argv[0], SYN, GOLD, EMBN]
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "r01_table2_on_300_lemmas.py"), run_name="r01")
rows, usages, safe = g["rows"], g["usages"], g["safe"]
norms = []
for lemma, us in usages.items():
    X = np.load(os.path.join(EMBR, safe(lemma) + ".npy"))
    ids = json.load(open(os.path.join(EMBR, safe(lemma) + ".ids.json"), encoding="utf-8"))["ids"]
    pos = {s: i for i, s in enumerate(ids)}
    norms.extend(np.linalg.norm(X, axis=1).tolist())
    per = {}
    for u in us:
        per.setdefault(int(u["period_label"][:4]), []).append(pos[u["sentence_id"]])
    first = min(per)
    for r in rows:
        if r["lemma"] == lemma and r["t"] in per:
            ca, cb = X[per[first]].mean(0), X[per[r["t"]]].mean(0)
            r["PRT_raw"] = float(1 - ca @ cb / (np.linalg.norm(ca) * np.linalg.norm(cb)))
norms = np.array(norms)
print(f"raw embedding norms: mean {norms.mean():.3f} sd {norms.std():.3f} min {norms.min():.3f} max {norms.max():.3f} (n={len(norms)})")
lemmas = sorted({r["lemma"] for r in rows if r["first"] == 1810 and "gold_q_dist" in r})
by = {l: [r for r in rows if r["lemma"] == l and "gold_q_dist" in r] for l in lemmas}


def avg(sample, m):
    out = []
    for b in range(1830, 1991, 20):
        rs = [r for l in sample for r in by[l] if r["t"] == b]
        if len(rs) >= 10:
            out.append(spearmanr([r["gold_q_dist"] for r in rs], [r[m] for r in rs])[0])
    return float(np.mean(out))


rng = np.random.default_rng(0)
for m in ("PRT", "PRT_raw"):
    bs = [avg(list(rng.choice(lemmas, len(lemmas), replace=True)), m) for _ in range(n_boot)]
    lo, hi = np.percentile(bs, [2.5, 97.5])
    print(f"{m:8s} {avg(lemmas, m):.3f} 95%[{lo:.3f},{hi:.3f}]  paper PRT 0.473 -> {'INSIDE' if lo <= 0.473 <= hi else 'OUTSIDE'}")
d = [r["PRT"] - r["PRT_raw"] for r in rows if "PRT_raw" in r]
print(f"per-row PRT(normalised) - PRT(raw): mean {np.mean(d):+.5f}, max |d| {np.max(np.abs(d)):.5f}, rank corr {spearmanr([r['PRT'] for r in rows if 'PRT_raw' in r], [r['PRT_raw'] for r in rows if 'PRT_raw' in r])[0]:.5f}")
