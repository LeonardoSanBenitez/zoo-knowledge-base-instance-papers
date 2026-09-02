#!/usr/bin/env python3
"""r05 -- does KKM's pattern survive without the $100,000 knot, and how much does
the knot's position matter?

The knot is inherited, twice over. KD's "$75,000" is, in KKM's own words, "simply
the midpoint of the '60 to 90K' income category". KKM inflation-adjust KD's
"<= 90K" to "<= 97K", then round to the boundary of MK's 90-100k band and split at
$100,000. So the threshold that defines every number in KKM Table 1 is a rounded
inflation adjustment of the midpoint of somebody else's survey category.

Two checks:

  PART A -- KNOT SWEEP. Refit KKM's own estimator at every knot the income bands
  permit. If "flattening restricted to the bottom 15-20%" is a fact about people,
  it should not appear only at one cut point.

  PART B -- NO KNOT AT ALL. Fit Q_tau(y) = a + b*L + c*L^2 for a grid of tau. The
  curvature c needs no threshold. KKM's story predicts c < 0 at low tau (bottom
  quantiles bend over) and c > 0 at high tau (top quantiles bend up). The
  location-scale account of r04 predicts, additionally, that c is LINEAR in the
  standardised error quantile F^-1(tau) -- because curvature in the quantile
  function is then just mu'' + sigma'' * F^-1(tau).

Output: out_knot_sweep.csv, out_curvature_by_tau.csv
"""
import os
import sys
import warnings

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.regression.quantile_regression import QuantReg
from statsmodels.tools.sm_exceptions import IterationLimitWarning

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "..", "artifacts", "kkm2023.csv")
LOW = [0.05, 0.10, 0.15]
HIGH = [0.25, 0.30, 0.35]
CURV_TAUS = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50,
             0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]


def qfit(y, X, tau):
    """Fit and REPORT non-convergence rather than swallowing it.

    statsmodels QuantReg emits IterationLimitWarning and returns a result object
    anyway. A warning that is printed once and then filtered is a silent wrong
    number, so convergence is returned as data, not as a log line."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        r = QuantReg(y, X).fit(q=tau, max_iter=5000)
        hit = any(issubclass(x.category, IterationLimitWarning) for x in w)
    return r, hit


def main():
    d = pd.read_csv(CSV)
    y = d.wellbeing.values
    L = np.log(d.income.values)
    cats = np.sort(d.income.unique())

    # ---------------- PART A: knot sweep -----------------------------------
    print("PART A -- KNOT SWEEP.  'flat_bottom' = above-knot slope n.s. at .05 for "
          "tau in {.05,.10,.15};  'boundary' = significant for tau in {.25,.30,.35}")
    rows = []
    for i in range(3, len(cats) - 2):                # need >=3 points either side
        knot = cats[i]
        A = (d.income.values >= knot).astype(float)
        res = {}
        nonconv = 0
        for t in LOW + HIGH:
            X = np.column_stack([np.ones(len(y)), L, A, L * A])
            r, hit = qfit(y, X, t)
            nonconv += hit
            V = r.cov_params()
            b = r.params[1] + r.params[3]
            se = float(np.sqrt(V[1, 1] + V[3, 3] + 2 * V[1, 3]))
            res[t] = (b, 2 * (1 - stats.norm.cdf(abs(b / se))))
        flat = all(res[t][1] > 0.05 for t in LOW)
        bnd = all(res[t][1] < 0.05 for t in HIGH)
        rows.append({"knot": knot, "n_above": int(A.sum()), "n_income_pts_above":
                     int((cats >= knot).sum()), "flat_bottom": flat, "boundary": bnd,
                     "slope_above_t15": res[0.15][0], "p_above_t15": res[0.15][1],
                     "slope_above_t30": res[0.30][0], "p_above_t30": res[0.30][1],
                     "nonconverged_fits": nonconv})
        print("  knot=%9.0f  n_above=%6d  pts=%2d  flat_bottom=%-5s boundary=%-5s"
              "  b>k@.15=%+.2f (p=%.3f)  b>k@.30=%+.2f (p=%.3f)  nonconv=%d"
              % (knot, A.sum(), (cats >= knot).sum(), flat, bnd,
                 res[0.15][0], res[0.15][1], res[0.30][0], res[0.30][1], nonconv),
              flush=True)
    ks = pd.DataFrame(rows)
    ks.to_csv(os.path.join(HERE, "out_knot_sweep.csv"), index=False)
    print("  --> flat_bottom holds at %d/%d knots; both conditions at %d/%d"
          % (ks.flat_bottom.sum(), len(ks), (ks.flat_bottom & ks.boundary).sum(), len(ks)))

    # ---------------- PART B: no knot, quadratic in log income --------------
    print("\nPART B -- NO KNOT.  Q_tau(y) = a + b*L + c*L^2 ; c is the curvature")
    Lc = L - L.mean()
    X = np.column_stack([np.ones(len(y)), Lc, Lc ** 2])
    out = []
    nonconv = 0
    for t in CURV_TAUS:
        r, hit = qfit(y, X, t)
        nonconv += hit
        out.append({"tau": t, "z": stats.norm.ppf(t),
                    "b_linear": r.params[1], "c_curv": r.params[2],
                    "se_c": r.bse[2], "t_c": r.tvalues[2], "p_c": r.pvalues[2],
                    "nonconverged": hit})
    cv = pd.DataFrame(out)
    print(cv.to_string(index=False, float_format=lambda v: "%.4f" % v))
    print("  (%d of %d curvature fits hit the iteration limit)" % (nonconv, len(cv)))

    neg = cv[(cv.c_curv < 0) & (cv.p_c < 0.05)]
    pos = cv[(cv.c_curv > 0) & (cv.p_c < 0.05)]
    print("\n  significantly NEGATIVE curvature at tau = %s"
          % (list(neg.tau.round(2)) or "none"))
    print("  significantly POSITIVE curvature at tau = %s"
          % (list(pos.tau.round(2)) or "none"))

    w = 1.0 / cv.se_c ** 2
    Xz = np.column_stack([np.ones(len(cv)), cv.z])
    W = np.diag(w)
    beta = np.linalg.solve(Xz.T @ W @ Xz, Xz.T @ W @ cv.c_curv)
    fit = Xz @ beta
    chi2 = float(((cv.c_curv - fit) ** 2 * w).sum())
    print("\n  curvature regressed on z(tau):  c(tau) = %+.4f %+.4f * z"
          % (beta[0], beta[1]))
    print("  slope/se = %.2f    (a pure LOCATION model needs beta1 = 0;"
          " a location-SCALE model with sigma'' != 0 predicts beta1 != 0)"
          % (beta[1] / np.sqrt(np.linalg.inv(Xz.T @ W @ Xz)[1, 1])))
    print("  residual chi2 = %.1f on %d points (NOT a valid test: the tau-specific "
          "estimates are strongly correlated; see r07)" % (chi2, len(cv)))
    cv["ls_fit"] = fit
    cv.to_csv(os.path.join(HERE, "out_curvature_by_tau.csv"), index=False)
    print("\nwrote out_knot_sweep.csv, out_curvature_by_tau.csv")


if __name__ == "__main__":
    main()
