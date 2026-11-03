"""Bootstrap over lemmas for the r01 averages (pre-registered test in arena-lsc ticket 2026-10-31-Literature:
reproduction succeeds if the paper's value lies in my 95% interval). Re-runs r01's per-lemma rows.

    python r02_bootstrap_lemmas.py <synthetic dir> <gold EN dir> <emb dir> [n_boot]
"""
import runpy
import sys

import numpy as np
from scipy.stats import spearmanr

n_boot = int(sys.argv[4]) if len(sys.argv) > 4 else 1000
sys.argv = sys.argv[:4]
import io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    g = runpy.run_path(__file__.replace("r02_bootstrap_lemmas.py", "r01_table2_on_300_lemmas.py"), run_name="r01")
rows = g["rows"]
PAPER = {"PRT": 0.473, "APD": 0.297, "JSD0.32": 0.408, "JSD0.5": 0.266}
lemmas = sorted({r["lemma"] for r in rows if r["first"] == 1810 and "gold_q_dist" in r})
by = {l: [r for r in rows if r["lemma"] == l and "gold_q_dist" in r] for l in lemmas}
rng = np.random.default_rng(0)


def avg_rho(sample, metric, gold="gold_q_dist"):
    out = []
    for b in range(1830, 1991, 20):
        rs = [r for l in sample for r in by[l] if r["t"] == b]
        if len(rs) >= 10:
            out.append(spearmanr([r[gold] for r in rs], [r[metric] for r in rs])[0])
    return float(np.mean(out))


for m in PAPER:
    point = avg_rho(lemmas, m)
    bs = [avg_rho(list(rng.choice(lemmas, len(lemmas), replace=True)), m) for _ in range(n_boot)]
    lo, hi = np.percentile(bs, [2.5, 97.5])
    inside = lo <= PAPER[m] <= hi
    print(f"{m:8s} mine={point:.3f} 95%[{lo:.3f},{hi:.3f}] paper={PAPER[m]:.3f} -> {'INSIDE' if inside else 'OUTSIDE'} (n_lemmas={len(lemmas)}, B={n_boot})")
