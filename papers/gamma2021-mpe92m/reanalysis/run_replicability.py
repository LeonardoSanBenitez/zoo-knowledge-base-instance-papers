"""MPE-92M: how many factors REPLICATE, as opposed to how many exist?

The prior pass (2026-07-31) established the dimension COUNT is a resolution
choice: parallel analysis 11, authors 12, Kaiser 18, same data. That answers
"how many can be extracted". It does not answer "how many would survive in a
second sample", which is the question a taxonomy actually needs.

Here: for each k, split N=1403 into two independent halves, run the paper's own
EFA (Spearman / principal / quartimin) on each half, match factors by Tucker's
phi under the Hungarian algorithm, and record the matched phi per factor rank.

The null is NOT gaussian noise -- it is the SAME data with each item column
independently permuted, which destroys the correlation structure while keeping
every item's marginal distribution (VAS scales are heavily skewed and bounded;
a gaussian null would flatter the result).

Output: results_replicability.json
Run:    python run_replicability.py
"""
import json
import numpy as np
import pandas as pd
import mpelib as M

KS = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18]
N_SPLITS = 30

X, cov = M.load()
print(f"N={len(X)}  items={X.shape[1]}  rank-trick error={M.check_rank_trick(X):.2e}")

# --- empirical null: column-permuted real data, marginals preserved ----------
rng = np.random.default_rng(7)
Xp = X.copy()
for c in Xp.columns:
    Xp[c] = rng.permutation(Xp[c].values)

res = {'n': int(len(X)), 'n_splits': N_SPLITS, 'ks': KS, 'real': {}, 'null': {}}

for k in KS:
    a = M.split_half_congruence(X, k, n_splits=N_SPLITS, seed=100 + k)
    b = M.split_half_congruence(Xp, k, n_splits=max(10, N_SPLITS // 3), seed=200 + k)
    res['real'][str(k)] = {'median': np.median(a, 0).tolist(),
                           'p05': np.percentile(a, 5, 0).tolist(),
                           'p95': np.percentile(a, 95, 0).tolist()}
    res['null'][str(k)] = {'median': np.median(b, 0).tolist(),
                           'max': b.max(0).tolist()}
    med, nullmax = np.median(a, 0), b.max(0)
    n95 = int((med >= 0.95).sum())
    n85 = int((med >= 0.85).sum())
    nnull = int((med > nullmax).sum())
    print(f"k={k:2d}  >=.95:{n95:2d}  >=.85:{n85:2d}  above-null-max:{nnull:2d}  "
          f"| phi: " + " ".join(f"{v:.2f}" for v in med))

json.dump(res, open('results_replicability.json', 'w'), indent=1)
print("\nwrote results_replicability.json")
