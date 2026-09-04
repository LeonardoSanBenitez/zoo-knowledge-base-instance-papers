#!/usr/bin/env python3
"""w05 -- can the corpus choose between the additive and multiplicative
homogeneity models, rather than leaving the reader to pick one?

w04 established that lnVR is unbiased under additive homogeneity and lnCVR under
multiplicative homogeneity, that each is badly biased under the other, and that
they imply bounds on individual response variation of 0.00 and 4.91 HAMD points
on the same 104 comparisons.

There is one discriminating test the corpus supports, and it uses the variation
the trials supply for free -- drugs differ in efficacy, so ln(mean ratio) varies
across comparisons from near zero to substantial:

    ADDITIVE homogeneity        predicts lnVR flat in ln(mean ratio):  slope 0
    MULTIPLICATIVE homogeneity  predicts lnVR = ln(mean ratio):        slope 1

The slope is estimable. Two things could corrupt it and both are checked:

  (i)  lnVR and ln(mean ratio) share the treated arm's sample SD only through the
       SD, not the mean, so the induced correlation is weaker here than in the
       SMD case -- but it is checked by simulation anyway, under both models;
  (ii) between-trial confounding: trials with larger mean ratios may differ in
       population. Handled by adding a within-trial version using multi-arm
       trials, where two active arms of DIFFERENT efficacy are compared with the
       SAME placebo arm, so trial-level confounders cancel.

Output: out_model_discrimination.csv
"""
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "..", "tools"))
import statlib  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 20260902


def cluster_slope(x, y, cl, B=4000, seed=SEED):
    rng = np.random.default_rng(seed)
    uq = np.unique(cl)
    idx = {c: np.flatnonzero(cl == c) for c in uq}
    sl = []
    for _ in range(B):
        sel = np.concatenate([idx[c] for c in rng.choice(uq, len(uq), replace=True)])
        if len(np.unique(x[sel])) < 3:
            continue
        sl.append(stats.linregress(x[sel], y[sel])[0])
    s0 = stats.linregress(x, y)[0]
    return s0, float(np.percentile(sl, 2.5)), float(np.percentile(sl, 97.5)), \
        float(np.std(sl, ddof=1))


def main():
    C = pd.read_csv(os.path.join(HERE, "out_comparisons.csv"))
    sub = C[~C.is_change].copy()
    print("1  THE DISCRIMINATING SLOPE, across %d raw-endpoint comparisons "
          "(%d trials)" % (len(sub), sub.study.nunique()))
    print("   additive homogeneity predicts 0, multiplicative predicts 1")
    s, lo, hi, se = cluster_slope(sub.lnmr.values, sub.lnvr.values,
                                  sub.study.values)
    print("   slope = %+.3f  95%% cluster bootstrap [%+.3f, %+.3f]" % (s, lo, hi))
    print("   distance from 0: %.1f SEs;  distance from 1: %.1f SEs"
          % (abs(s) / se, abs(1 - s) / se))
    rows = [{"analysis": "across comparisons, raw endpoint", "slope": s,
             "lo": lo, "hi": hi, "se": se, "k": len(sub),
             "studies": sub.study.nunique()}]

    # ---- within-trial version: multi-arm trials sharing one placebo arm ----
    multi = sub.groupby("study").filter(lambda g: len(g) >= 2)
    if len(multi) > 10:
        x = multi.lnmr.values
        y = multi.lnvr.values
        g = pd.Series(multi.study.values)
        xc = x - pd.Series(x).groupby(g).transform("mean").values
        yc = y - pd.Series(y).groupby(g).transform("mean").values
        s2 = float((xc * yc).sum() / (xc ** 2).sum())
        rng = np.random.default_rng(SEED)
        uq = np.unique(multi.study.values)
        idx = {c: np.flatnonzero(multi.study.values == c) for c in uq}
        bs = []
        for _ in range(4000):
            sel = np.concatenate([idx[c] for c in
                                  rng.choice(uq, len(uq), replace=True)])
            xx = x[sel] - pd.Series(x[sel]).groupby(
                pd.Series(multi.study.values[sel])).transform("mean").values
            yy = y[sel] - pd.Series(y[sel]).groupby(
                pd.Series(multi.study.values[sel])).transform("mean").values
            if (xx ** 2).sum() > 0:
                bs.append(float((xx * yy).sum() / (xx ** 2).sum()))
        lo2, hi2 = np.percentile(bs, [2.5, 97.5])
        print("\n2  WITHIN-TRIAL version: %d comparisons in %d multi-arm trials,"
              % (len(multi), len(uq)))
        print("   trial fixed effects, so population and protocol cancel")
        print("   slope = %+.3f  95%% cluster bootstrap [%+.3f, %+.3f]"
              % (s2, lo2, hi2))
        rows.append({"analysis": "within multi-arm trials", "slope": s2,
                     "lo": lo2, "hi": hi2, "se": float(np.std(bs, ddof=1)),
                     "k": len(multi), "studies": len(uq)})

    # ---- 3  is the slope estimator itself honest? -------------------------
    print("\n3  IS THE SLOPE ESTIMATOR HONEST? simulate under each model,")
    print("   with the corpus's own sample sizes, and read the slope back")
    n_d = sub.n_drug.values.astype(int)
    n_p = sub.n_pbo.values.astype(int)
    m_p = sub.m_pbo.values
    s_p = sub.sd_pbo.values
    rng = np.random.default_rng(SEED)
    print("   Each simulated comparison is given the SAME efficacy as its real")
    print("   counterpart, so the corpus matches the real one in effect-size")
    print("   distribution (observed ln mean ratio: mean %+.3f, range %+.3f to %+.3f)"
          % (sub.lnmr.mean(), sub.lnmr.min(), sub.lnmr.max()))
    dfrac_obs = 1.0 - np.exp(sub.lnmr.values)
    for kind, floor in (("additive, NO floor", False), ("additive, floor at 0", True),
                        ("multiplicative", True)):
        sl, mean_lnvr = [], []
        for rep in range(150):
            lv, lm = [], []
            for i in range(len(sub)):
                shape = (m_p[i] / s_p[i]) ** 2
                scale = s_p[i] ** 2 / m_p[i]
                c = rng.gamma(shape, scale, n_p[i])
                t0 = rng.gamma(shape, scale, n_d[i])
                dfrac = dfrac_obs[i]
                if kind.startswith("additive"):
                    t = t0 - dfrac * m_p[i]
                    if floor:
                        t = np.clip(t, 0, None)
                else:
                    t = t0 * (1 - dfrac)
                if t.std(ddof=1) <= 0:
                    continue
                y, _ = statlib.lnvr(t.std(ddof=1), n_d[i], c.std(ddof=1), n_p[i])
                lv.append(float(y))
                lm.append(float(np.log(np.abs(t.mean()) / c.mean())))
            sl.append(stats.linregress(lm, lv)[0])
            mean_lnvr.append(float(np.mean(lv)))
        print("   true model %-22s -> slope %+.3f (mc se %.3f), pooled VR %.3f"
              % (kind, np.mean(sl), np.std(sl, ddof=1) / np.sqrt(len(sl)),
                 np.exp(np.mean(mean_lnvr))))
        rows.append({"analysis": "simulation, true " + kind,
                     "slope": float(np.mean(sl)), "lo": np.nan, "hi": np.nan,
                     "se": float(np.std(sl, ddof=1)), "k": len(sub),
                     "studies": None})
    print("   OBSERVED slope %+.3f [%+.3f, %+.3f]; OBSERVED pooled VR %.3f"
          % (s, lo, hi, float(np.exp(
              (sub.lnvr / sub.lnvr_v).sum() / (1 / sub.lnvr_v).sum()))))

    pd.DataFrame(rows).to_csv(os.path.join(HERE, "out_model_discrimination.csv"),
                              index=False)
    print("\nwrote out_model_discrimination.csv")


if __name__ == "__main__":
    main()
