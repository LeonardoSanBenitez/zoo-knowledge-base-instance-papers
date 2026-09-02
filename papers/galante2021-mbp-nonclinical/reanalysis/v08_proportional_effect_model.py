#!/usr/bin/env python3
"""v08 -- one parameter explains the whole thing, on symptom scales.

Everything found so far is consistent with a single very simple model:

    a mindfulness programme multiplies each participant's symptom score by the
    same factor (1 - k), rather than subtracting the same amount from everyone.

Under a multiplicative effect, if the treated arm's scores are (1-k) times the
control arm's, then BOTH the mean and the SD are multiplied by (1-k), so

    ratio of means  =  ratio of SDs   ->   ln(m1/m2) = lnVR
    lnCVR           =  lnVR - ln(m1/m2)  =  0        exactly
    lnVR            ~  SMD / (m2 / sd2)               (for small k)

and every one of the results so far falls out:

  * VR < 1 without any heterogeneity of treatment effect that a clinician could
    act on -- everybody's proportional benefit is identical;
  * lnCVR indistinguishable from zero (v02: -0.031 [-0.071, +0.006]), which the
    variability-ratio literature reads as "no variability difference" and which is
    in fact the SIGNATURE of a proportional effect;
  * compression graded by the size of the mean effect (v06 test 3), because both
    are the same k;
  * no dependence on baseline severity or on targeted vs universal recruitment
    (v05 P1, P3), because k is a fraction and therefore scale-free.

This script tests the model where it can be tested and reports where it fails.
It CANNOT be right for every scale: a proportional model needs a meaningful zero,
and on a positively-keyed scale it predicts the SD to RISE with the mean, which
the corpus contradicts. So the D-scales and U-scales are analysed separately and
the disagreement between them is the result, not a nuisance.

Output: out_proportional_model.csv
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


def cluster_ci(x, cluster, B=4000, seed=SEED):
    x = np.asarray(x, float)
    cl = np.asarray(cluster)
    uq = np.unique(cl)
    idx = {c: np.flatnonzero(cl == c) for c in uq}
    rng = np.random.default_rng(seed)
    bs = [float(np.mean(x[np.concatenate(
        [idx[c] for c in rng.choice(uq, len(uq), replace=True)])])) for _ in range(B)]
    return float(np.mean(x)), float(np.percentile(bs, 2.5)), \
        float(np.percentile(bs, 97.5)), len(uq)


def cluster_slope_ci(x, y, cluster, B=3000, seed=SEED):
    cl = np.asarray(cluster)
    uq = np.unique(cl)
    idx = {c: np.flatnonzero(cl == c) for c in uq}
    rng = np.random.default_rng(seed)
    sl, ic = [], []
    for _ in range(B):
        sel = np.concatenate([idx[c] for c in rng.choice(uq, len(uq), replace=True)])
        if len(np.unique(x[sel])) < 3:
            continue
        s, i_, *_ = stats.linregress(x[sel], y[sel])
        sl.append(s)
        ic.append(i_)
    s0, i0, *_ = stats.linregress(x, y)
    return (s0, float(np.percentile(sl, 2.5)), float(np.percentile(sl, 97.5)),
            i0, float(np.percentile(ic, 2.5)), float(np.percentile(ic, 97.5)))


def main():
    d = pd.read_csv(os.path.join(HERE, "out_arms.csv"))
    d["lnvr"], d["lnvr_v"] = statlib.lnvr(d.sd_mbp, d.n_mbp, d.sd_ctl, d.n_ctl)
    d["lncvr"], d["lncvr_v"] = statlib.lncvr(d.m_mbp, d.sd_mbp, d.n_mbp,
                                             d.m_ctl, d.sd_ctl, d.n_ctl)
    d["lnmr"] = np.log(d.m_mbp / d.m_ctl)
    post = d[(d.trange == "Postintervention") & (d.ctrl_cat == "passive")].copy()
    base = d[(d.trange == "Baseline") & (d.ctrl_cat == "passive")].copy()

    rows = []
    print("THE CORE PREDICTION: ratio of MEANS = ratio of SDs\n")
    print("%-46s %8s %8s %20s" % ("", "ln(mean", "lnVR", "difference = lnCVR"))
    print("%-46s %8s %8s %20s" % ("", "ratio)", "", "(0 if proportional)"))
    for lab, sub in (("BASELINE, passive-controlled (negative control)", base),
                     ("POST-INTERVENTION, all scales", post),
                     ("POST, symptom scales only (lower is better)",
                      post[post.dir_imp == "D"]),
                     ("POST, positively-keyed scales (higher is better)",
                      post[post.dir_imp == "U"])):
        if len(sub) < 5:
            continue
        a, alo, ahi, nst = cluster_ci(sub.lnmr.values, sub.study.values)
        b, blo, bhi, _ = cluster_ci(sub.lnvr.values, sub.study.values)
        c, clo, chi, _ = cluster_ci((sub.lnvr - sub.lnmr).values, sub.study.values)
        print("%-46s %+8.4f %+8.4f   %+8.4f [%+.4f, %+.4f]"
              % (lab, a, b, c, clo, chi))
        rows.append({"subset": lab, "k": len(sub), "studies": nst,
                     "ln_mean_ratio": a, "lnvr": b, "diff": c,
                     "diff_lo": clo, "diff_hi": chi})
    print("\n  A proportional effect predicts the last column to be zero. Note that")
    print("  it is zero on SYMPTOM scales and NOT zero on positively-keyed ones,")
    print("  which is exactly where a proportional model has to fail: on a scale")
    print("  whose zero is arbitrary, a ratio of means means nothing, and raising")
    print("  the mean proportionally would RAISE the SD, not lower it.")

    print("\nREGRESSION FORM: lnVR on ln(mean ratio). Proportional -> slope 1, "
          "intercept 0")
    for lab, sub in (("all scales", post),
                     ("symptom scales (D)", post[post.dir_imp == "D"]),
                     ("positively-keyed (U)", post[post.dir_imp == "U"]),
                     ("BASELINE negative control", base)):
        ok = np.isfinite(sub.lnmr) & np.isfinite(sub.lnvr) & (sub.lnmr.abs() < 1.5)
        s = sub[ok]
        if len(s) < 10:
            continue
        sl, sl_lo, sl_hi, ic, ic_lo, ic_hi = cluster_slope_ci(
            s.lnmr.values, s.lnvr.values, s.study.values)
        print("  %-26s slope %+.3f [%+.3f, %+.3f]   intercept %+.4f "
              "[%+.4f, %+.4f]   n=%d"
              % (lab, sl, sl_lo, sl_hi, ic, ic_lo, ic_hi, len(s)))
        rows.append({"subset": "regression: " + lab, "k": len(s),
                     "studies": s.study.nunique(), "slope": sl,
                     "slope_lo": sl_lo, "slope_hi": sl_hi,
                     "intercept": ic, "intercept_lo": ic_lo, "intercept_hi": ic_hi})

    print("\nSMALL-k APPROXIMATION: lnVR should equal SMD / (control mean / control SD)")
    post["R"] = post.m_ctl / post.sd_ctl
    sp = np.sqrt(((post.n_mbp - 1) * post.sd_mbp ** 2
                  + (post.n_ctl - 1) * post.sd_ctl ** 2)
                 / (post.n_mbp + post.n_ctl - 2))
    post["smd_raw"] = (post.m_mbp - post.m_ctl) / sp
    post["pred_lnvr"] = post.smd_raw / post.R
    for lab, sub in (("symptom scales (D)", post[post.dir_imp == "D"]),
                     ("positively-keyed (U)", post[post.dir_imp == "U"])):
        s = sub[np.isfinite(sub.pred_lnvr) & (sub.pred_lnvr.abs() < 1)]
        pm, plo, phi, nst = cluster_ci(s.pred_lnvr.values, s.study.values)
        om, olo, ohi, _ = cluster_ci(s.lnvr.values, s.study.values)
        print("  %-22s predicted %+.4f [%+.4f, %+.4f]   observed %+.4f "
              "[%+.4f, %+.4f]   (k=%d, %d studies)"
              % (lab, pm, plo, phi, om, olo, ohi, len(s), nst))
        rows.append({"subset": "small-k prediction: " + lab, "k": len(s),
                     "studies": nst, "predicted_lnvr": pm, "lnvr": om,
                     "diff": om - pm})

    print("\nWHAT THE MODEL SAYS ABOUT INDIVIDUALS, and what it does not")
    dsub = post[post.dir_imp == "D"]
    kk = 1 - np.exp(cluster_ci(dsub.lnvr.values, dsub.study.values)[0])
    print("  On symptom scales the fitted multiplier is 1 - k with k = %.3f, i.e." % kk)
    print("  a %.0f%% proportional reduction in symptom score." % (100 * kk))
    print("  Someone scoring 20 on a distress scale is predicted to end at %.1f;"
          % (20 * (1 - kk)))
    print("  someone scoring 5 is predicted to end at %.1f. The ABSOLUTE benefit"
          % (5 * (1 - kk)))
    print("  differs by a factor of four; the PROPORTIONAL benefit is identical.")
    print("  Both readings are 'heterogeneity of treatment effect' and they point")
    print("  in opposite directions for who should be offered the programme.")
    print("  What the model CANNOT establish from aggregate arm data: whether any")
    print("  individual actually follows it. Arm-level means and SDs are consistent")
    print("  with a proportional effect; they are equally consistent with a mixture")
    print("  in which some people improve a great deal and others not at all, if")
    print("  that mixture happens to reproduce the same two moments.")

    pd.DataFrame(rows).to_csv(os.path.join(HERE, "out_proportional_model.csv"),
                              index=False)
    print("\nwrote out_proportional_model.csv")


if __name__ == "__main__":
    main()
