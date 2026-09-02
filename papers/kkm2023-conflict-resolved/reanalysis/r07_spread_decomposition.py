#!/usr/bin/env python3
"""r07 -- a model-free decomposition of KKM's "flattening".

Every quantile slope splits exactly into a CENTRE term and a SPREAD term:

    Q_tau(L) = median(L) + D_tau(L),        D_tau(L) = Q_tau(L) - median(L)
    dQ_tau/dL = d median/dL  +  d D_tau/dL

No model, no error distribution, no threshold assumed. It just asks: when the
15th percentile "flattens" above $100k, is that because the centre of the
happiness distribution stops rising, or because the lower tail stops keeping up
with a centre that is still rising?

The answer decides what the finding means. KKM's interpretive sentences -- "The
suffering of the unhappy group diminishes as income increases up to 100k but very
little beyond that ... Heartbreak, bereavement, and clinical depression may be
examples of such miseries" -- are claims about the absolute well-being of a group
of people. If the centre keeps rising at full speed and only the SPREAD changes,
then nothing about happiness flattens; the distribution stretches downward.

Also runs the two simulation generators r06 was missing:
  LS-SAT     saturated location-scale: sigma free at every income category, which
             is the MOST a pure width change can do. If flattening still does not
             appear, flattening is a change of SHAPE, not of width.
  LOCFIX     the real data with the centre forced to be exactly linear in
             log(income) -- every trace of a threshold in the central tendency
             removed, conditional shapes untouched.

Output: out_spread_decomposition.csv, out_simulation2.csv
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
warnings.simplefilter("ignore", IterationLimitWarning)

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "..", "artifacts", "kkm2023.csv")
LOW = [0.05, 0.10, 0.15]
HIGH = [0.25, 0.30, 0.35]
NSIM = int(os.environ.get("NSIM", 200))
NBOOT_SPREAD = int(os.environ.get("NBOOT_SPREAD", 2000))
SEED = 20260902


def qslopes(y, L, A, taus):
    X = np.column_stack([np.ones(len(y)), L, A, L * A])
    out = {}
    for t in taus:
        r = QuantReg(y, X).fit(q=t, max_iter=2000)
        V = r.cov_params()
        b = r.params[1] + r.params[3]
        se = float(np.sqrt(max(V[1, 1] + V[3, 3] + 2 * V[1, 3], 1e-12)))
        out[t] = {"below": r.params[1], "above": b,
                  "p_above": 2 * (1 - stats.norm.cdf(abs(b / se))),
                  "inter": r.params[3], "p_inter": r.pvalues[3]}
    return out


def verdict(res):
    return (all(res[t]["p_above"] > 0.05 for t in LOW),
            all(res[t]["p_above"] < 0.05 for t in HIGH),
            res[0.85]["p_inter"] < 0.05 and res[0.85]["inter"] > 0)


def wls(x, yv, w):
    X = np.column_stack([np.ones(len(x)), x])
    W = np.diag(w)
    XtWX = X.T @ W @ X
    b = np.linalg.solve(XtWX, X.T @ W @ yv)
    return b, np.linalg.inv(XtWX)


def main():
    d = pd.read_csv(CSV)
    y = d.wellbeing.values
    L = np.log(d.income.values)
    A = (d.income.values > 100000).astype(float)
    rng = np.random.default_rng(SEED)

    # ---------- 1. centre vs spread, by income category, with bootstrap CIs ----
    cats = np.sort(d.income.unique())
    TAUS = [0.05, 0.10, 0.15, 0.20, 0.30, 0.50, 0.70, 0.85, 0.90, 0.95]
    idx = {c: np.flatnonzero(d.income.values == c) for c in cats}

    def stats_for(yv):
        rows = []
        for c in cats:
            s = yv[idx[c]]
            q = np.quantile(s, TAUS)
            rows.append(q)
        return np.array(rows)                      # [ncat, ntau]

    obs = stats_for(y)
    boot = np.empty((NBOOT_SPREAD, len(cats), len(TAUS)))
    for b in range(NBOOT_SPREAD):
        yv = np.empty_like(y)
        for c in cats:
            ii = idx[c]
            yv[ii] = y[rng.choice(ii, len(ii), replace=True)]
        boot[b] = stats_for(yv)

    imed = TAUS.index(0.50)
    tab = pd.DataFrame({"income": cats, "L": np.log(cats),
                        "n": [len(idx[c]) for c in cats]})
    for j, t in enumerate(TAUS):
        tab["q%02d" % (t * 100)] = obs[:, j]
        tab["D%02d" % (t * 100)] = obs[:, j] - obs[:, imed]
        tab["seD%02d" % (t * 100)] = (boot[:, :, j] - boot[:, :, imed]).std(axis=0, ddof=1)
    tab["se_med"] = boot[:, :, imed].std(axis=0, ddof=1)
    print("CENTRE AND SPREAD BY INCOME CATEGORY  (D = quantile minus median)")
    show = ["income", "n", "q50", "se_med", "D05", "D15", "D85", "D95"]
    print(tab[show].to_string(index=False, float_format=lambda v: "%.3f" % v))
    tab.to_csv(os.path.join(HERE, "out_spread_decomposition.csv"), index=False)

    print("\nSLOPES OF THE CENTRE AND OF EACH SPREAD TERM, per log(income),"
          " fitted separately below and above $100k")
    print("%-8s %-24s %-24s %-18s" % ("term", "slope <=100k", "slope >100k", "change"))
    lo = cats <= 100000
    hi = ~lo
    res_rows = []
    for name, col, se in [("median", "q50", "se_med")] + \
                         [("D%02d" % (t * 100), "D%02d" % (t * 100), "seD%02d" % (t * 100))
                          for t in TAUS if t != 0.50]:
        line = []
        vals = []
        for m in (lo, hi):
            w = 1.0 / tab[se].values[m] ** 2
            b, cov = wls(tab.L.values[m], tab[col].values[m], w)
            # bootstrap the slope directly (weights are estimated, so trust the boot)
            bs = []
            for r in range(min(NBOOT_SPREAD, 2000)):
                yy = (boot[r, :, TAUS.index(0.50)] if col == "q50"
                      else boot[r, :, TAUS.index(float(col[1:]) / 100)] - boot[r, :, imed])
                bb, _ = wls(tab.L.values[m], yy[m], w)
                bs.append(bb[1])
            bs = np.array(bs)
            line.append("%+.3f (%.3f)" % (b[1], bs.std(ddof=1)))
            vals.append((b[1], bs.std(ddof=1), bs))
        chg = vals[1][0] - vals[0][0]
        se_chg = (vals[1][2] - vals[0][2]).std(ddof=1)
        print("%-8s %-24s %-24s %+.3f (%.3f) z=%.2f"
              % (name, line[0], line[1], chg, se_chg, chg / se_chg))
        res_rows.append({"term": name, "slope_below": vals[0][0], "se_below": vals[0][1],
                         "slope_above": vals[1][0], "se_above": vals[1][1],
                         "change": chg, "se_change": se_chg, "z_change": chg / se_chg})
    pd.DataFrame(res_rows).to_csv(os.path.join(HERE, "out_spread_slopes.csv"), index=False)

    # ---------- 2. the two extra generators --------------------------------
    print("\n\nSIMULATION LADDER, PART 2")
    real = qslopes(y, L, A, LOW + HIGH + [0.85])
    print("REAL: flat=%s bnd=%s accel=%s   above-slope@.15=%.3f"
          % (verdict(real) + (real[0.15]["above"],)))

    # LS-SAT: saturated scale, location exactly linear
    rmed = QuantReg(y, np.column_stack([np.ones(len(y)), L])).fit(q=0.5)
    loc = rmed.params[0] + rmed.params[1] * L
    dev = y - loc
    sd_by_cat = pd.Series(dev).groupby(d.income.values).std(ddof=1)
    s_i = d.income.map(sd_by_cat).values
    eps = dev / s_i
    eps = (eps - np.median(eps)) / eps.std(ddof=1)

    # LOCFIX: real deviations from the category median, re-centred on a linear median
    med_by_cat = d.groupby("income").wellbeing.median()
    dev_med = y - d.income.map(med_by_cat).values
    y_locfix = loc + dev_med

    rows = []
    r_lf = qslopes(y_locfix, L, A, LOW + HIGH + [0.85])
    f, b_, a_ = verdict(r_lf)
    print("LOCFIX (centre forced exactly linear, shapes untouched): "
          "flat=%s bnd=%s accel=%s  above-slope@.15=%.3f"
          % (f, b_, a_, r_lf[0.15]["above"]))
    rows.append({"generator": "LOCFIX (single dataset)", "nsim": 1,
                 "rate_flat_bottom": float(f), "rate_boundary20": float(b_),
                 "rate_accel_top": float(a_),
                 "mean_slope_above_t15": r_lf[0.15]["above"]})

    cnt = {"flat": 0, "bnd": 0, "accel": 0}
    sl15 = []
    for it in range(NSIM):
        e = rng.choice(eps, size=len(y), replace=True)
        r_ = qslopes(loc + s_i * e, L, A, LOW + HIGH + [0.85])
        f, b_, a_ = verdict(r_)
        cnt["flat"] += f
        cnt["bnd"] += b_
        cnt["accel"] += a_
        sl15.append(r_[0.15]["above"])
    print("LS-SAT (saturated width, iid shape): flat %.1f%%  bnd %.1f%%  accel %.1f%%"
          "  mean above-slope@.15 = %.3f  (real %.3f, pure-location expectation "
          "= median slope %.3f)"
          % (100 * cnt["flat"] / NSIM, 100 * cnt["bnd"] / NSIM,
             100 * cnt["accel"] / NSIM, np.mean(sl15), real[0.15]["above"],
             qslopes(y, L, A, [0.50])[0.50]["above"]))
    rows.append({"generator": "LS-SAT", "nsim": NSIM,
                 "rate_flat_bottom": cnt["flat"] / NSIM,
                 "rate_boundary20": cnt["bnd"] / NSIM,
                 "rate_accel_top": cnt["accel"] / NSIM,
                 "mean_slope_above_t15": float(np.mean(sl15))})
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "out_simulation2.csv"), index=False)
    print("\nwrote out_spread_decomposition.csv, out_spread_slopes.csv, out_simulation2.csv")


if __name__ == "__main__":
    main()
