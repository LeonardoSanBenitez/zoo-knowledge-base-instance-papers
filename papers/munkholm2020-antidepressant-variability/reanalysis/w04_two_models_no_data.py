#!/usr/bin/env python3
"""w04 -- the honest version, after my own negative control failed.

WHAT WENT WRONG IN w03, AND WHY IT MATTERS MORE THAN WHAT WENT RIGHT.

w03 simulated a treatment that MULTIPLIES each patient's score by a factor. On a
gamma-distributed outcome that makes the SD scale exactly with the mean, i.e. an
effective coupling of 1. I then scored three statistics on it, one of which
(lnVR*) was calibrated to the coupling of 0.29 I had measured ACROSS PLACEBO ARMS
in the real data. The negative control -- zero individual variation, kappa = 0 --
came back at lnVR 0.830 and lnVR* 0.877 instead of 1.000, while lnCVR returned
1.001.

That is not the statistics failing. It is my generator having a coupling of 1
while my calibration assumed 0.29, and it exposes the conceptual hole in the
calibration itself:

  * beta measured ACROSS placebo arms says how SD varies with mean ACROSS
    POPULATIONS.
  * The treated arm is not a different population. It is the same population,
    moved. Whether its SD follows the across-population relation depends on WHY
    that relation exists, and the data cannot say.

So lnVR* is not "the answer". It is a third assumption, no better justified than
the two it replaces. What the data actually support is weaker, and this script
establishes it:

  lnVR  tests ADDITIVE homogeneity:        H0: treatment subtracts a constant
  lnCVR tests MULTIPLICATIVE homogeneity:  H0: treatment multiplies by a constant

Each has power against individual variation only under its own model. Neither can
tell you which model holds. And the two models imply bounds on individual response
variation that differ by a factor of infinity -- 0.00 against 0.59 outcome SDs --
on the same 104 comparisons.

Output: out_two_models.csv
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "..", "tools"))
import statlib  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 20260902
NREP = 250


def corpus_stats(lv, lm, vv, beta):
    w = 1.0 / vv
    return {"lnVR": float((w * lv).sum() / w.sum()),
            "lnCVR": float((w * (lv - lm)).sum() / w.sum()),
            "lnVR*": float((w * (lv - beta * lm)).sum() / w.sum())}


def simulate(kind, kappa, n_d, n_p, m_p, s_p, beta, rng, delta_frac=0.17):
    """kind: 'additive' or 'multiplicative'.
    kappa is the SD of the individual response, expressed in the units natural
    to each model: outcome SDs for additive, proportion for multiplicative."""
    lv, lm, vv = [], [], []
    for i in range(len(n_d)):
        shape = (m_p[i] / s_p[i]) ** 2
        scale = s_p[i] ** 2 / m_p[i]
        c = rng.gamma(shape, scale, n_p[i])
        t0 = rng.gamma(shape, scale, n_d[i])
        if kind == "additive":
            eff = rng.normal(delta_frac * m_p[i], kappa * s_p[i], n_d[i])
            t = np.clip(t0 - eff, 0.0, None)
        else:
            fac = np.clip(rng.normal(1 - delta_frac, kappa, n_d[i]), 0.0, None)
            t = t0 * fac
        y, v = statlib.lnvr(t.std(ddof=1), n_d[i], c.std(ddof=1), n_p[i])
        lv.append(float(y))
        vv.append(float(v))
        lm.append(float(np.log(t.mean() / c.mean())))
    return corpus_stats(np.array(lv), np.array(lm), np.array(vv), beta)


def main():
    C = pd.read_csv(os.path.join(HERE, "out_comparisons.csv"))
    sub = C[~C.is_change]
    n_d = sub.n_drug.values.astype(int)
    n_p = sub.n_pbo.values.astype(int)
    m_p = sub.m_pbo.values
    s_p = sub.sd_pbo.values
    beta = 0.290                                        # w03, raw endpoint arms
    rng = np.random.default_rng(SEED)

    print("SIMULATION with the answer known, on the real corpus's sample sizes")
    print("(%d comparisons, arm n median %d, placebo endpoint mean %.1f SD %.1f)\n"
          % (len(sub), int(np.median(np.r_[n_d, n_p])), m_p.mean(), s_p.mean()))
    rows = []
    for kind in ("additive", "multiplicative"):
        print("  TRUE MODEL: %s treatment effect" % kind.upper())
        print("  %-38s %8s %8s %8s" % ("", "lnVR", "lnCVR", "lnVR*"))
        for kappa in (0.0, 0.10, 0.20, 0.30, 0.40):
            acc = {"lnVR": [], "lnCVR": [], "lnVR*": []}
            for _ in range(NREP):
                r = simulate(kind, kappa, n_d, n_p, m_p, s_p, beta, rng)
                for k in acc:
                    acc[k].append(r[k])
            lab = ("  kappa = %.2f%s" % (kappa, "  <- NEGATIVE CONTROL"
                                         if kappa == 0 else ""))
            print("  %-38s %8.3f %8.3f %8.3f"
                  % (lab, *[np.exp(np.mean(acc[k])) for k in
                            ("lnVR", "lnCVR", "lnVR*")]))
            rows.append({"true_model": kind, "kappa": kappa,
                         **{k: float(np.exp(np.mean(acc[k]))) for k in acc}})
        print()

    print("READING THE TABLE")
    print("  Look at the two kappa = 0 rows. Under an ADDITIVE truth, lnVR")
    print("  returns 1.00 and the other two do not. Under a MULTIPLICATIVE truth,")
    print("  lnCVR returns 1.00 and the other two do not. Each statistic is")
    print("  unbiased under exactly one model and biased under the other, by more")
    print("  than the effect it is looking for.")
    print("  lnVR* sits between them and is unbiased under NEITHER. That is the")
    print("  correction to my own w02/w03: the across-population coupling is not")
    print("  the within-population response of SD to a treatment-induced shift,")
    print("  and calibrating to it does not make a third statistic correct.")

    print("\nWHAT THE REAL DATA SAY UNDER EACH MODEL")
    print("  the same 104 raw-endpoint comparisons, 75 trials, 61,144 adults")
    b = pd.read_csv(os.path.join(HERE, "out_bounds.csv"))
    b = b[(b.kind == "raw ENDPOINT")]
    for _, r in b.iterrows():
        model = {"lnVR": "ADDITIVE homogeneity",
                 "lnCVR": "MULTIPLICATIVE homogeneity",
                 "lnVR*": "coupling-calibrated (unbiased under neither)"}[r.statistic]
        print("  %-46s ratio %.3f [%.3f, %.3f]  ->  individual-effect SD at most "
              "%.2f outcome SDs = %.2f HAMD/MADRS points"
              % (model, r.vr, r.lo, r.hi, r.sigma_int_over_sd, r.sigma_int_points))
    print("  average drug-placebo difference in the same comparisons: 2.70 points")
    print()
    print("  So on identical data the upper bound on how much individual responses")
    print("  can differ is either ZERO or 4.9 points, and the average effect is 2.7.")
    print("  Under one model the paper's conclusion -- 'assume the average effect")
    print("  applies also to the individual patient' -- is licensed. Under the")
    print("  other, individual effects could plausibly range from clearly harmful")
    print("  to twice the average benefit. NOTHING IN THE DATA CHOOSES BETWEEN")
    print("  THEM, and the paper does not say a choice was made.")

    pd.DataFrame(rows).to_csv(os.path.join(HERE, "out_two_models.csv"), index=False)
    print("\nwrote out_two_models.csv")


if __name__ == "__main__":
    main()
