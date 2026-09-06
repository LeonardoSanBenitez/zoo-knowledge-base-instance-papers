"""p08 -- put the additive/multiplicative question on a continuous scale and
estimate where this corpus actually sits, with an interval.

Model the arm SD as a power of the arm mean:

        SD  proportional to  mean^lambda        =>   lnVR = lambda * ln(m1/m2)

    lambda = 0  additive homogeneity      -> lnVR is the right statistic
    lambda = 1  multiplicative homogeneity -> lnCVR is the right statistic

lnVR assumes lambda = 0 and lnCVR assumes lambda = 1. Nobody in this literature
estimates lambda. It is estimable: regress lnVR on ln(m1/m2), then rescale the
slope against what the SAME regression returns in simulated worlds where lambda
is 0 and 1 by construction (p04B/p07 showed the raw slope is not lambda -- the
estimator has its own null).

        lambda_hat = (b_obs - b_0) / (b_1 - b_0)

Interval: nonparametric bootstrap over trials for b_obs, with b_0 and b_1 held
at their simulated means (they are estimated on 300 replicates each and their
Monte-Carlo error is folded in separately and reported).
"""
import csv
import io
import json
import os
import sys

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "tools"))
import statlib  # noqa: E402

NUM = ("all_n all_sd all_m pooled_sd pooled_m placebo_n placebo_sd placebo_m "
       "k_ad_arms year baseline weeks").split()


def load():
    rows = []
    with io.open(os.path.join(HERE, "dat.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter=";"):
            for k in NUM:
                r[k] = float(r[k]) if r[k] not in ("", "None") else np.nan
            rows.append(r)
    return rows


def slope(s1, n1, m1, s2, n2, m2):
    y, _ = statlib.lnvr(s1, n1, s2, n2)
    return stats.linregress(np.log(m1 / m2), y).slope


def simulate(n1, n2, m1, m2, s2, lam, rng, B):
    """world with SD proportional to mean^lam; lam=0 additive, lam=1 multiplicative."""
    out = []
    for _ in range(B):
        M1, S1, M2, S2 = [], [], [], []
        for i in range(len(n1)):
            k = (m1[i] / m2[i]) ** lam
            a = rng.normal(m1[i], s2[i] * k, int(n1[i]))
            p = rng.normal(m2[i], s2[i], int(n2[i]))
            M1.append(abs(a.mean())); S1.append(a.std(ddof=1))
            M2.append(abs(p.mean())); S2.append(p.std(ddof=1))
        out.append(slope(np.array(S1), n1, np.array(M1),
                         np.array(S2), n2, np.array(M2)))
    return np.array(out)


def main():
    rows = load()
    rng = np.random.default_rng(880808)
    A = lambda k, sub=None: np.array([r[k] for r in (sub or rows)], float)
    n1, s1, m1 = A("all_n"), A("all_sd"), A("all_m")
    n2, s2, m2 = A("placebo_n"), A("placebo_sd"), A("placebo_m")

    b_obs = slope(s1, n1, m1, s2, n2, m2)
    B = 300
    b0 = simulate(n1, n2, m1, m2, s2, 0.0, rng, B)
    b1 = simulate(n1, n2, m1, m2, s2, 1.0, rng, B)
    print("raw regression slope of lnVR on ln(m_AD/m_PL)")
    print("  observed                = %+.4f" % b_obs)
    print("  simulated at lambda = 0 = %+.4f  (MC SE %.4f, B=%d)"
          % (b0.mean(), b0.std(ddof=1) / np.sqrt(B), B))
    print("  simulated at lambda = 1 = %+.4f  (MC SE %.4f, B=%d)"
          % (b1.mean(), b1.std(ddof=1) / np.sqrt(B), B))
    print("  -> the estimator's own scale is %.3f, not 1.0; a raw slope is not lambda"
          % (b1.mean() - b0.mean()))

    lam = (b_obs - b0.mean()) / (b1.mean() - b0.mean())
    idx = np.arange(len(rows))
    boots = []
    for _ in range(4000):
        j = rng.choice(idx, size=len(idx), replace=True)
        bb = slope(s1[j], n1[j], m1[j], s2[j], n2[j], m2[j])
        boots.append((bb - b0.mean()) / (b1.mean() - b0.mean()))
    boots = np.array(boots)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    print()
    print("lambda = %.3f  [%.3f, %.3f]   (4000 trial-level bootstrap resamples)"
          % (lam, lo, hi))
    print("  lnVR  assumes lambda = 0:  %s"
          % ("inside the interval" if lo <= 0 <= hi else "OUTSIDE the interval"))
    print("  lnCVR assumes lambda = 1:  %s"
          % ("inside the interval" if lo <= 1 <= hi else "OUTSIDE the interval"))

    lr = float(np.mean(np.log(m1 / m2)))
    yv, vv = statlib.lnvr(s1, n1, s2, n2)
    mv = statlib.re_meta(yv, vv, method="DL")
    print()
    print("consequence for the reported numbers (mean ln(m_AD/m_PL) = %+.4f):" % lr)
    print("  VR   as published, lambda = 0 assumed : %.4f" % np.exp(mv["mu"]))
    print("  CVR  as published, lambda = 1 assumed : %.4f" % np.exp(mv["mu"] - lr))
    print("  VR   at the estimated lambda = %.3f    : %.4f  [%.4f, %.4f]"
          % (lam, np.exp(mv["mu"] - lam * lr),
             np.exp(mv["mu"] - hi * lr), np.exp(mv["mu"] - lo * lr)))
    print("  the published CVR applies %.1f times the correction the data support"
          % (1.0 / lam))

    out = dict(b_obs=float(b_obs), b_lambda0=float(b0.mean()),
               b_lambda1=float(b1.mean()),
               b0_mc_se=float(b0.std(ddof=1) / np.sqrt(B)),
               b1_mc_se=float(b1.std(ddof=1) / np.sqrt(B)),
               lam=float(lam), lam_ci=[float(lo), float(hi)],
               mean_log_mean_ratio=lr,
               VR_published=float(np.exp(mv["mu"])),
               CVR_published=float(np.exp(mv["mu"] - lr)),
               VR_at_lambda=float(np.exp(mv["mu"] - lam * lr)),
               VR_at_lambda_ci=[float(np.exp(mv["mu"] - hi * lr)),
                                float(np.exp(mv["mu"] - lo * lr))],
               overcorrection_factor=float(1.0 / lam))
    with io.open(os.path.join(HERE, "out_p08.json"), "w", encoding="utf-8",
                 newline="\n") as f:
        json.dump(out, f, indent=1)
    print()
    print("wrote out_p08.json")


if __name__ == "__main__":
    main()
