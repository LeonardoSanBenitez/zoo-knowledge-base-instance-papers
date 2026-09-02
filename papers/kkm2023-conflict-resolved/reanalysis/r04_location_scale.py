#!/usr/bin/env python3
"""r04 -- is KKM's "complementary nonlinearities" one fact or two?

KKM (2023) report two findings and treat them as substantively distinct:

  (i)  the least happy 15-20% flatten above $100k -- "the miseries that remain are
       not alleviated by high income. Heartbreak, bereavement, and clinical
       depression may be examples of such miseries";
  (ii) the happiest 30% accelerate above $100k -- "very happy people gain much more
       from increased income".

Both are statements about the SLOPE OF A QUANTILE. But a single, boring fact --
the conditional DISPERSION of happiness widening as income rises above $100k --
implies both at once, with no subpopulations and no mechanism specific to the
unhappy or the happy.

Formally, under a location-scale model  Y = mu(L) + sigma(L) * eps,  eps _||_ L:

    Q_tau(Y | L)      = mu(L) + sigma(L) * F^-1(tau)
    d Q_tau / dL      = mu'(L) + sigma'(L) * F^-1(tau)

so the quantile slope is LINEAR in F^-1(tau). Flattening at the bottom and
acceleration at the top are then the two ends of one straight line, not two
phenomena. The paper never tests this, and its homogeneity discussion -- which is
otherwise excellent -- treats the alternative to homogeneity as unspecified.

This script:
  1. measures the conditional dispersion of well-being by income category;
  2. cross-checks it against the SEPARATE deposit for Killingsworth 2021, which
     stores per-category standard errors and person counts (an independent route
     to the same SDs, from a file deposited two years earlier);
  3. tests whether the estimated quantile slopes are linear in F^-1(tau);
  4. fits the location-scale model and reports how much of the tau-variation in
     slope it absorbs.

Output: out_dispersion_by_income.csv, out_slope_vs_ztau.csv
"""
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.regression.quantile_regression import QuantReg

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "..", "artifacts", "kkm2023.csv")
K2021 = os.path.join(HERE, "..", "..", "killingsworth2021-experienced-wellbeing",
                     "artifacts", "k2021_income_wellbeing.csv")
TAUS = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50,
        0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]


def dispersion(d):
    g = d.groupby("income")["wellbeing"]
    out = pd.DataFrame({
        "n": g.size(),
        "mean": g.mean(),
        "median": g.median(),
        "sd": g.std(ddof=1),
        "iqr": g.quantile(0.75) - g.quantile(0.25),
        "p10": g.quantile(0.10), "p15": g.quantile(0.15),
        "p85": g.quantile(0.85), "p90": g.quantile(0.90),
        "skew": g.apply(lambda s: stats.skew(s)),
    })
    out["iqr_sd"] = out["iqr"] / 1.3489795
    out["p10_90_sd"] = (out["p90"] - out["p10"]) / 2.5631031
    out["L"] = np.log(out.index.values)
    out["se_mean"] = out["sd"] / np.sqrt(out["n"])
    return out.reset_index()


def main():
    d = pd.read_csv(CSV)
    disp = dispersion(d)

    # ---- 2. cross-deposit check against Killingsworth 2021's aggregate file ----
    try:
        k = pd.read_csv(K2021)
        k = k[["household_income", "experienced_wellbeing.Mean",
               "experienced_wellbeing.std.error", "experienced_wellbeing.personcount"]]
        k.columns = ["income", "k21_mean", "k21_se", "k21_n"]
        k["k21_sd"] = k.k21_se * np.sqrt(k.k21_n)
        disp = disp.merge(k, on="income", how="left")
        disp["mean_diff"] = disp["mean"] - disp["k21_mean"]
        disp["sd_ratio"] = disp["sd"] / disp["k21_sd"]
        disp["n_diff"] = disp["n"] - disp["k21_n"]
    except Exception as e:                                     # pragma: no cover
        print("cross-deposit check unavailable:", e)

    pd.set_option("display.width", 200)
    print("CONDITIONAL DISPERSION OF WELL-BEING BY INCOME CATEGORY")
    cols = ["income", "n", "mean", "median", "sd", "iqr_sd", "p10_90_sd", "skew"]
    if "k21_sd" in disp:
        cols += ["k21_n", "n_diff", "k21_mean", "mean_diff", "k21_sd", "sd_ratio"]
    print(disp[cols].to_string(index=False, float_format=lambda v: "%.3f" % v))
    disp.to_csv(os.path.join(HERE, "out_dispersion_by_income.csv"), index=False)

    lo, hi = disp[disp.income <= 100000], disp[disp.income > 100000]
    for lab, part in (("<=100k", lo), (">100k", hi), ("all", disp)):
        for scale in ("sd", "iqr_sd"):
            sl, ic, r, p, se = stats.linregress(part.L, np.log(part[scale]))
            print("  d log(%-6s)/d log(income)  %-7s = %+8.4f  (se %.4f, p=%.4f, "
                  "k=%d income points)" % (scale, lab, sl, se, p, len(part)))

    # ---- 3/4. quantile slopes vs F^-1(tau) -------------------------------------
    y = d.wellbeing.values
    L = np.log(d.income.values)
    A = (d.income.values > 100000).astype(float)
    rows = []
    for t in TAUS:
        X = np.column_stack([np.ones(len(y)), L, A, L * A])
        r = QuantReg(y, X).fit(q=t)
        V = r.cov_params()
        rows.append({"tau": t,
                     "z": stats.norm.ppf(t),
                     "below": r.params[1],
                     "above": r.params[1] + r.params[3],
                     "se_below": r.bse[1],
                     "se_above": float(np.sqrt(V[1, 1] + V[3, 3] + 2 * V[1, 3]))})
    q = pd.DataFrame(rows)

    # residual-based F^-1(tau): do not assume normal errors
    res_lo = y[A == 0] - np.polyval(np.polyfit(L[A == 0], y[A == 0], 1), L[A == 0])
    res_hi = y[A == 1] - np.polyval(np.polyfit(L[A == 1], y[A == 1], 1), L[A == 1])
    s_lo, s_hi = res_lo.std(ddof=2), res_hi.std(ddof=2)
    q["f_lo"] = [np.quantile(res_lo, t) / s_lo for t in q.tau]
    q["f_hi"] = [np.quantile(res_hi, t) / s_hi for t in q.tau]

    print("\nQUANTILE SLOPE vs STANDARDISED QUANTILE OF THE ERROR")
    print("a location-scale model predicts slope = mu' + sigma' * F^-1(tau), i.e. a LINE")
    for lab, ycol, xcol, secol in (("below 100k", "below", "f_lo", "se_below"),
                                   ("above 100k", "above", "f_hi", "se_above")):
        w = 1.0 / q[secol] ** 2
        X = np.column_stack([np.ones(len(q)), q[xcol]])
        W = np.diag(w)
        beta = np.linalg.solve(X.T @ W @ X, X.T @ W @ q[ycol])
        fitv = X @ beta
        chi2 = float(((q[ycol] - fitv) ** 2 * w).sum())
        dfree = len(q) - 2
        pfit = 1 - stats.chi2.cdf(chi2, dfree)
        var_tot = float((w * (q[ycol] - np.average(q[ycol], weights=w)) ** 2).sum())
        print("  %-11s  mu' = %+.3f   sigma' = %+.3f   "
              "explains %.1f%% of the weighted tau-variation in slope; "
              "lack-of-fit chi2=%.1f df=%d p=%.3f"
              % (lab, beta[0], beta[1], 100 * (1 - chi2 / var_tot), chi2, dfree, pfit))
        q[ycol + "_ls_fit"] = fitv
    print()
    print(q[["tau", "z", "below", "below_ls_fit", "se_below",
             "above", "above_ls_fit", "se_above"]]
          .to_string(index=False, float_format=lambda v: "%.3f" % v))
    q.to_csv(os.path.join(HERE, "out_slope_vs_ztau.csv"), index=False)
    print("\nwrote out_dispersion_by_income.csv, out_slope_vs_ztau.csv")


if __name__ == "__main__":
    main()
