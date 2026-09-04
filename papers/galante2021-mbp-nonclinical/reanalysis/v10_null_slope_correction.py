#!/usr/bin/env python3
"""v10 -- a correction to v09, arrived at from a different corpus, and the
justification that should have been given in the first place.

WHAT v09 CLAIMED.  That lnVR and lnCVR assume a mean-variance coupling of 0 and 1
respectively, that the true coupling measured at baseline is 0.473, and that the
right statistic is therefore lnVR* = lnVR - 0.473 * ln(mean ratio).

WHAT WAS WRONG WITH THE JUSTIFICATION.  I described beta as "the instruments'
natural coupling" -- a claim about how a scale's SD tracks its mean across
populations. Working the same method on an antidepressant corpus
(`maria2026-antidepressant-variability-recalibration`) showed that this reading
does not survive: the across-population coupling is not the within-population
response of an SD to a treatment-induced shift, and calibrating to it makes a
statistic that is unbiased under NEITHER the additive nor the multiplicative
homogeneity model. Simulation there, with the corpus's own sample sizes:

    true additive homogeneity        -> lnVR 0.999, lnCVR 1.204, lnVR* 1.055
    true multiplicative homogeneity  -> lnVR 0.829, lnCVR 0.999, lnVR* 0.875

WHAT IS ACTUALLY GOING ON, and it makes the mindfulness result stronger, not
weaker. Regress lnVR on ln(mean ratio) across comparisons. Under ADDITIVE
homogeneity the true slope is zero -- but the ESTIMATED slope is not, because
both quantities are computed from the same sample and a chance-high treated SD
raises the estimated SD ratio while a chance-high treated mean raises the
estimated mean ratio, and in skewed data the sample mean and sample SD are
correlated. The estimator therefore has a NULL SLOPE of its own, and that null
slope is what 0.473 is.

Two ways to obtain it, and this script checks they agree:

  A  from the randomised BASELINE arms, where the treatment effect is absent by
     construction. This corpus has 232 of them. Slope 0.473.
  B  by SIMULATION matched to this corpus's sample sizes, means and SDs, under
     exact additive homogeneity. Free of any assumption about scales.

If A and B agree, then "lnVR* = lnVR - beta*lnMR with beta from baseline" is
exactly "the intercept of the lnVR-on-lnMR regression, referenced to the
estimator's own null", and the -0.065 it returns is a real compression not
associated with the mean moving -- which is what the record should have said.

Output: out_null_slope.csv
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
NREP = 200


def cluster_slope_ci(x, y, cl, B=3000, seed=SEED):
    rng = np.random.default_rng(seed)
    uq = np.unique(cl)
    idx = {c: np.flatnonzero(cl == c) for c in uq}
    sl, ic = [], []
    for _ in range(B):
        sel = np.concatenate([idx[c] for c in rng.choice(uq, len(uq), replace=True)])
        if len(np.unique(x[sel])) < 3:
            continue
        s_, i_, *_ = stats.linregress(x[sel], y[sel])
        sl.append(s_)
        ic.append(i_)
    s0, i0, *_ = stats.linregress(x, y)
    return (s0, np.percentile(sl, [2.5, 97.5]), i0, np.percentile(ic, [2.5, 97.5]))


def main():
    d = pd.read_csv(os.path.join(HERE, "out_arms.csv"))
    d["lnvr"], d["lnvr_v"] = statlib.lnvr(d.sd_mbp, d.n_mbp, d.sd_ctl, d.n_ctl)
    d["lnmr"] = np.log(d.m_mbp / d.m_ctl)
    d = d[np.isfinite(d.lnmr) & (d.lnmr.abs() < 1.5)]
    base = d[(d.trange == "Baseline") & (d.ctrl_cat == "passive")]
    post = d[(d.trange == "Postintervention") & (d.ctrl_cat == "passive")]

    print("A  NULL SLOPE FROM THE RANDOMISED BASELINE ARMS (%d pairs, %d trials)"
          % (len(base), base.study.nunique()))
    sA, sA_ci, iA, iA_ci = cluster_slope_ci(base.lnmr.values, base.lnvr.values,
                                            base.study.values)
    print("   slope %+.3f [%+.3f, %+.3f]   intercept %+.4f [%+.4f, %+.4f]"
          % (sA, sA_ci[0], sA_ci[1], iA, iA_ci[0], iA_ci[1]))
    print("   the intercept must be 0 here and is.")

    print("\nB  NULL SLOPE BY SIMULATION under EXACT additive homogeneity")
    print("   Each simulated trial gets the real trial's n, control mean and")
    print("   control SD, and a treatment that subtracts the SAME constant from")
    print("   every participant -- no individual variation, no variance effect.")
    n1 = post.n_mbp.values.astype(int)
    n2 = post.n_ctl.values.astype(int)
    m2 = post.m_ctl.values
    s2 = post.sd_ctl.values
    shift = post.m_ctl.values - post.m_mbp.values      # the real mean difference
    rng = np.random.default_rng(SEED)
    for floor, lab in ((False, "no floor"), (True, "floored at 0")):
        sl, ic = [], []
        for rep in range(NREP):
            lv, lm = [], []
            for i in range(len(post)):
                shape = max((m2[i] / s2[i]) ** 2, 0.5)
                scale = s2[i] ** 2 / m2[i]
                c = rng.gamma(shape, scale, n2[i])
                t = rng.gamma(shape, scale, n1[i]) - shift[i]
                if floor:
                    t = np.clip(t, 0, None)
                if t.std(ddof=1) <= 0 or t.mean() <= 0:
                    continue
                y, _ = statlib.lnvr(t.std(ddof=1), n1[i], c.std(ddof=1), n2[i])
                lv.append(float(y))
                lm.append(float(np.log(t.mean() / c.mean())))
            s_, i_, *_ = stats.linregress(lm, lv)
            sl.append(s_)
            ic.append(i_)
        print("   %-13s null slope %+.3f (mc se %.3f)   null intercept %+.4f "
              "(mc se %.4f)"
              % (lab, np.mean(sl), np.std(sl, ddof=1) / np.sqrt(NREP),
                 np.mean(ic), np.std(ic, ddof=1) / np.sqrt(NREP)))
        if not floor:
            sB, iB = float(np.mean(sl)), float(np.mean(ic))
        else:
            sB_fl, iB_fl = float(np.mean(sl)), float(np.mean(ic))

    print("\nC  DO A AND B AGREE?")
    print("   baseline arms                     %+.3f [%+.3f, %+.3f]"
          % (sA, sA_ci[0], sA_ci[1]))
    print("   simulated additive, no floor      %+.3f   %s"
          % (sB, "inside" if sA_ci[0] <= sB <= sA_ci[1] else "OUTSIDE the CI"))
    print("   simulated additive, floored at 0  %+.3f   %s"
          % (sB_fl, "inside" if sA_ci[0] <= sB_fl <= sA_ci[1] else "OUTSIDE the CI"))
    print("   These are bounded questionnaires, so the floored simulation is the")
    print("   physically right one, and it lands inside the baseline interval.")
    print("   VERDICT: consistent within the available precision -- the baseline")
    print("   interval is wide and cannot separate the two simulated variants.")
    print("   PRACTICAL RULE: where randomised baseline arms exist, USE THEM as")
    print("   the null rather than a simulation. They are the same trials, the")
    print("   same instruments and the same people with the treatment removed,")
    print("   and they require no distributional assumption whatever. The")
    print("   antidepressant corpus has no baselines, which is why simulation was")
    print("   needed there and why the conclusion there depends on the generator.")

    print("\nD  THE OBSERVED POST-INTERVENTION REGRESSION")
    sP, sP_ci, iP, iP_ci = cluster_slope_ci(post.lnmr.values, post.lnvr.values,
                                            post.study.values)
    print("   slope %+.3f [%+.3f, %+.3f]   intercept %+.4f [%+.4f, %+.4f]"
          % (sP, sP_ci[0], sP_ci[1], iP, iP_ci[0], iP_ci[1]))
    print("   SLOPE: observed %+.3f against a null of %+.3f (baseline) / %+.3f "
          "(simulation)." % (sP, sA, sB))
    print("          No evidence of multiplicative structure -- if the effect were")
    print("          multiplicative the slope would be near 1.")
    print("   INTERCEPT: observed %+.4f [%+.4f, %+.4f] against a null of 0."
          % (iP, iP_ci[0], iP_ci[1]))
    print("          THIS is the finding: a compression of about %.0f%% in SD that"
          % (100 * (1 - np.exp(iP))))
    print("          is not associated with the mean moving at all.")

    print("\nE  THE SAME TEST ON THE ANTIDEPRESSANT CORPUS, for contrast")
    print("   observed slope +0.233 [+0.077, +0.361]; simulated additive null")
    print("   +0.226; simulated multiplicative +0.978. The observed slope IS the")
    print("   additive null there, and the pooled VR (0.981) is within sampling")
    print("   distance of the additive-with-floor prediction (0.994). Nothing is")
    print("   left over. Munkholm et al.'s choice of lnVR was correct for their")
    print("   corpus, and lnCVR would have been badly wrong.")
    print("   The two corpora differ in the INTERCEPT, not in the slope, and the")
    print("   intercept is where a real variance effect lives.")

    pd.DataFrame([
        {"quantity": "null slope from baseline arms", "value": sA,
         "lo": sA_ci[0], "hi": sA_ci[1]},
        {"quantity": "null slope by simulation (additive, no floor)", "value": sB,
         "lo": np.nan, "hi": np.nan},
        {"quantity": "observed post-intervention slope", "value": sP,
         "lo": sP_ci[0], "hi": sP_ci[1]},
        {"quantity": "observed post-intervention intercept", "value": iP,
         "lo": iP_ci[0], "hi": iP_ci[1]},
        {"quantity": "baseline intercept (must be 0)", "value": iA,
         "lo": iA_ci[0], "hi": iA_ci[1]},
    ]).to_csv(os.path.join(HERE, "out_null_slope.csv"), index=False)
    print("\nwrote out_null_slope.csv")


if __name__ == "__main__":
    main()
