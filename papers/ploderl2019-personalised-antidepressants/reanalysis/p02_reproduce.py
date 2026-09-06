"""p02 -- reproduce Table 1 of Plöderl & Hengartner (2019) before criticising it,
then show what the CVR row is actually made of.

Target values (their Table 1, "AD all", 169 trials, 32650 vs 18746):
    VR  = 1.01 (0.99 to 1.02), p = 0.33, Q(168) = 121.74
    CVR = 0.82 (0.80 to 0.84), p = 0.00, Q(168) = 243.53
    r(M,SD) = 0.55 (AD), 0.52 (placebo)

Their estimator, from cipriani-variance-2.r lines 38-44 (Nakagawa et al. 2015
eq. 9-12) with rma(method="DL", test="knha").
"""
import csv
import io
import os
import sys

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "tools"))
import statlib  # noqa: E402


def load():
    rows = []
    with io.open(os.path.join(HERE, "dat.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter=";"):
            for k in ("all_n", "all_sd", "all_m", "pooled_sd", "pooled_m",
                      "placebo_n", "placebo_sd", "placebo_m", "k_ad_arms",
                      "year", "baseline", "weeks"):
                r[k] = float(r[k]) if r[k] not in ("", "None") else np.nan
            rows.append(r)
    return rows


def knha(y, v, tau2):
    """rma(..., method='DL', test='knha'): Knapp-Hartung t interval."""
    w = 1.0 / (v + tau2)
    mu = (w * y).sum() / w.sum()
    k = len(y)
    s2 = (w * (y - mu) ** 2).sum() / (k - 1)
    se = np.sqrt(s2 / w.sum())
    t = stats.t.ppf(0.975, k - 1)
    p = 2 * (1 - stats.t.cdf(abs(mu / se), k - 1))
    return mu, se, (mu - t * se, mu + t * se), p


def pooled(y, v, label):
    m = statlib.re_meta(y, v, method="DL")
    mu, se, ci, p = knha(y, v, m["tau2"])
    print("%-28s k=%3d  exp(mu)=%.4f  CI %.4f to %.4f  p=%.3f  Q(%d)=%.2f  tau2=%.5f"
          % (label, m["k"], np.exp(mu), np.exp(ci[0]), np.exp(ci[1]), p,
             m["df"], m["Q"], m["tau2"]))
    return dict(mu=mu, ci=ci, p=p, Q=m["Q"], df=m["df"], tau2=m["tau2"],
                exp_mu=float(np.exp(mu)),
                exp_ci=(float(np.exp(ci[0])), float(np.exp(ci[1]))))


def main():
    rows = load()
    A = lambda k: np.array([r[k] for r in rows], float)
    n1, sd1, m1 = A("all_n"), A("all_sd"), A("all_m")
    n2, sd2, m2 = A("placebo_n"), A("placebo_sd"), A("placebo_m")
    print("k = %d, AD n = %d, placebo n = %d, total = %d"
          % (len(rows), n1.sum(), n2.sum(), n1.sum() + n2.sum()))

    print()
    print("== 1. reproduce their Table 1 row 'AD all' ==")
    yv, vv = statlib.lnvr(sd1, n1, sd2, n2)
    yc, vc = statlib.lncvr(m1, sd1, n1, m2, sd2, n2)
    res_vr = pooled(yv, vv, "VR  (theirs: 1.01, .99-1.02)")
    res_cvr = pooled(yc, vc, "CVR (theirs: 0.82, .80-.84)")
    print("r(M,SD) AD      = %+.3f   (theirs 0.55)"
          % stats.pearsonr(m1, sd1)[0])
    print("r(M,SD) placebo = %+.3f   (theirs 0.52)"
          % stats.pearsonr(m2, sd2)[0])

    print()
    print("== 2. what the CVR row is made of ==")
    d = yc - yv
    lr = np.log(m2 / m1)
    print("max |lnCVR_i - lnVR_i - log(m_PL/m_AD)| over 169 trials = %.2e"
          % np.abs(d - lr).max())
    print("  (the small-sample corrections are identical in eq.9 and eq.11 and cancel,")
    print("   so the two statistics differ by the log mean-ratio EXACTLY, per trial)")
    print("mean log(m_AD/m_PL)          = %+.4f  -> ratio %.4f"
          % (np.mean(-lr), np.exp(np.mean(-lr))))
    print("pooled lnVR - pooled lnCVR   = %+.4f  -> ratio %.4f"
          % (res_vr["mu"] - res_cvr["mu"],
             np.exp(res_vr["mu"] - res_cvr["mu"])))
    print("VR / CVR (their own Table 1) = 1.01 / 0.82 = %.4f" % (1.01 / 0.82))
    print("m_AD / m_PL, n-weighted      = %.4f"
          % ((n1 * m1).sum() / n1.sum() / ((n2 * m2).sum() / n2.sum())))
    print("share of trials with m_AD > m_PL: %.1f%%  (%d of %d)"
          % (100 * np.mean(m1 > m2), int(np.sum(m1 > m2)), len(m1)))

    print()
    print("== 3. their Table 1, all five rows, as a prediction ==")
    print("If CVR is only VR divided by the mean ratio, then for every subgroup")
    print("CVR/VR must equal the (pooled) placebo/AD mean-change ratio.")
    print("%-12s %6s %6s %6s %8s %8s" %
          ("group", "k", "VR", "CVR", "CVR/VR", "m_PL/m_AD"))
    groups = [("AD all", lambda r: True),
              ("SSRI", lambda r: r["cls"] == "SSRI"),
              ("SNRI", lambda r: r["cls"] == "SNRI"),
              ("atypical", lambda r: r["cls"] == "atypical"),
              ("tricyclic", lambda r: r["cls"] == "tricyclic")]
    table = {}
    for name, sel in groups:
        idx = [i for i, r in enumerate(rows) if sel(r)]
        if len(idx) < 3:
            continue
        i = np.array(idx)
        a = statlib.re_meta(*statlib.lnvr(sd1[i], n1[i], sd2[i], n2[i]), method="DL")
        b = statlib.re_meta(*statlib.lncvr(m1[i], sd1[i], n1[i],
                                           m2[i], sd2[i], n2[i]), method="DL")
        vr_, cvr_ = np.exp(a["mu"]), np.exp(b["mu"])
        ratio = np.exp(np.mean(np.log(m2[i] / m1[i])))
        print("%-12s %6d %6.3f %6.3f %8.3f %8.3f"
              % (name, len(idx), vr_, cvr_, cvr_ / vr_, ratio))
        table[name] = dict(k=len(idx), vr=float(vr_), cvr=float(cvr_),
                           ratio_pl_ad=float(ratio))

    import json
    with io.open(os.path.join(HERE, "out_p02.json"), "w", encoding="utf-8",
                 newline="\n") as f:
        json.dump(dict(vr=res_vr, cvr=res_cvr, by_group=table,
                       identity_max_abs_dev=float(np.abs(d - lr).max())),
                  f, indent=1)
    print()
    print("wrote out_p02.json")


if __name__ == "__main__":
    main()
