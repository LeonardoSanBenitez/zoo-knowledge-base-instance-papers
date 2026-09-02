#!/usr/bin/env python3
"""r02 -- paired nonparametric bootstrap of the KKM (2023) quantile slopes.

Why: KKM Table 1 draws its central qualitative boundary -- "flattening ... is
restricted to the least happy 20% of the population" -- by thresholding p-values
row by row. Rows 5/10/15% are called flat because their above-$100k slope is not
significant; rows 25/30/35% are called not-flat because theirs is. That is the
Gelman-Stern error (the difference between "significant" and "not significant" is
not itself significant) unless the slopes are shown to DIFFER ACROSS PERCENTILES.

Testing that needs the covariance between quantile-slope estimates at different
tau on the SAME data, which no per-row standard error supplies. Hence a paired
bootstrap: one resample of the full person-level table per replicate, all taus
refit on it, so cross-tau covariance falls out.

Also produces, for every tau:
  * the CI on the above-$100k slope (so "flat" can be read as an interval, not a
    verdict), and
  * the below-minus-above difference with its own CI.

Resampling unit: the person-row. That matches the paper's unit of analysis (each
row is one participant's mean well-being over their experience-sampling reports).

Output: out_bootstrap_slopes.npz, out_bootstrap_summary.csv
"""
import os
import sys
import time

import numpy as np
import pandas as pd
from statsmodels.regression.quantile_regression import QuantReg

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "..", "artifacts", "kkm2023.csv")
TAUS = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.50, 0.70, 0.85]
B = int(os.environ.get("NBOOT", 1000))
SEED = 20260902


def slopes(y, L, A, taus):
    """Return (below[ntau], above[ntau]) slope vectors."""
    below, above = np.empty(len(taus)), np.empty(len(taus))
    m0, m1 = A == 0, A == 1
    X0 = np.column_stack([np.ones(m0.sum()), L[m0]])
    X1 = np.column_stack([np.ones(m1.sum()), L[m1]])
    y0, y1 = y[m0], y[m1]
    for i, t in enumerate(taus):
        below[i] = QuantReg(y0, X0).fit(q=t).params[1]
        above[i] = QuantReg(y1, X1).fit(q=t).params[1]
    return below, above


def main():
    d = pd.read_csv(CSV)
    y = d["wellbeing"].values
    L = np.log(d["income"].values)
    A = (d["income"].values > 100000).astype(int)
    n = len(d)

    b0, a0 = slopes(y, L, A, TAUS)
    print("point estimates")
    for t, b, a in zip(TAUS, b0, a0):
        print("  tau=%.2f  below %.3f  above %.3f  diff %.3f" % (t, b, a, b - a))

    rng = np.random.default_rng(SEED)
    BB = np.empty((B, len(TAUS)))
    AA = np.empty((B, len(TAUS)))
    t0 = time.time()
    for r in range(B):
        idx = rng.integers(0, n, n)
        BB[r], AA[r] = slopes(y[idx], L[idx], A[idx], TAUS)
        if (r + 1) % 50 == 0:
            el = time.time() - t0
            print("  %d/%d  %.1fs elapsed, %.1fs projected total"
                  % (r + 1, B, el, el / (r + 1) * B), flush=True)

    np.savez_compressed(os.path.join(HERE, "out_bootstrap_slopes.npz"),
                        taus=np.array(TAUS), below=BB, above=AA,
                        below_point=b0, above_point=a0, seed=SEED, B=B)

    rows = []
    for i, t in enumerate(TAUS):
        a = AA[:, i]
        b = BB[:, i]
        dfm = b - a
        rows.append({
            "tau": t,
            "below": b0[i], "below_se": b.std(ddof=1),
            "above": a0[i], "above_se": a.std(ddof=1),
            "above_lo": np.percentile(a, 2.5), "above_hi": np.percentile(a, 97.5),
            "diff_below_minus_above": b0[i] - a0[i],
            "diff_se": dfm.std(ddof=1),
            "diff_lo": np.percentile(dfm, 2.5), "diff_hi": np.percentile(dfm, 97.5),
            "p_above_eq_0": 2 * min((a <= 0).mean(), (a >= 0).mean()),
        })
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(HERE, "out_bootstrap_summary.csv"), index=False)
    print(out.to_string(index=False, float_format=lambda v: "%.4f" % v))
    print("\nwrote out_bootstrap_slopes.npz, out_bootstrap_summary.csv  (B=%d, %.0fs)"
          % (B, time.time() - t0))


if __name__ == "__main__":
    main()
