"""p03 -- report D, the quantity a parallel-group design actually fixes, on this
corpus; and measure the bias introduced by their multi-arm aggregation rule.

D = sigma_AT^2 - sigma_PL^2 = sigma_TE^2 + 2 rho sigma_PL sigma_TE

D is a difference of two sample variances: unbiased, sampling distribution known
(Var(s^2) = 2 sigma^4/(n-1) under normality), legitimately negative, and needs no
square root, no branch choice and no trial deletion. Nobody in this literature
reports it. It carries UNITS, so it may only be pooled within a measurement
scale -- this corpus mixes HAMD17/21/24/29/31, MADRS and IDS, so the per-scale
tables below are the honest object and the all-scales row is printed only to
show how much the unit mixing moves it.

Also here: their aggregation of multiple antidepressant arms uses the unweighted
MEAN of arm SDs (cipriani-variance-data-generation-2.r line 163). That is a
downward-biased estimate of the SD of the combined arm for two independent
reasons -- Jensen (mean of SDs <= sqrt(mean of variances)) and the omission of
the between-arm mean spread. 84 of 169 trials here have more than one AD arm,
and the placebo side never does, so any bias is one-sided.
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


def d_stat(sd1, n1, sd2, n2):
    """difference of sample variances and its sampling variance."""
    d = sd1 ** 2 - sd2 ** 2
    v = 2 * sd1 ** 4 / (n1 - 1) + 2 * sd2 ** 4 / (n2 - 1)
    return d, v


def show(y, v, label, unit):
    m = statlib.re_meta(y, v, method="PM")
    pi = m["pi"] if m["pi"] else (float("nan"), float("nan"))
    print("%-22s k=%3d  D = %+8.3f  [%+8.3f, %+8.3f] %s   I2=%3.0f%%  PI [%+.2f, %+.2f]"
          % (label, m["k"], m["mu"], m["ci"][0], m["ci"][1], unit,
             100 * (m["I2"] or 0), pi[0], pi[1]))
    return m


def main():
    rows = load()
    A = lambda k, sel=None: np.array(
        [r[k] for r in (rows if sel is None else sel)], float)
    out = {}

    print("=== 1. D by measurement scale (their aggregation, as published) ===")
    print("    units are squared points OF THAT SCALE; do not pool across rows")
    scales = {}
    for r in rows:
        scales.setdefault(r["scale"], []).append(r)
    for sc in sorted(scales, key=lambda s: -len(scales[s])):
        sub = scales[sc]
        if len(sub) < 3:
            continue
        d, v = d_stat(A("all_sd", sub), A("all_n", sub),
                      A("placebo_sd", sub), A("placebo_n", sub))
        m = show(d, v, sc, "pts^2")
        out["D_" + sc] = dict(k=m["k"], mu=m["mu"], ci=list(m["ci"]),
                              I2=m["I2"], tau2=m["tau2"])
    d_all, v_all = d_stat(A("all_sd"), A("all_n"),
                          A("placebo_sd"), A("placebo_n"))
    m = show(d_all, v_all, "ALL SCALES (unit-mixed)", "pts^2")
    out["D_all_unit_mixed"] = dict(k=m["k"], mu=m["mu"], ci=list(m["ci"]),
                                   I2=m["I2"], tau2=m["tau2"])

    print()
    print("=== 2. what D leaves open: sigma_TE as a function of the unmeasured rho ===")
    print("    sigma_TE = sigma_PL * (sqrt(VR^2 - 1 + rho^2) - rho),")
    print("    evaluated at the HAMD17 pooled VR and the median HAMD17 placebo SD")
    h = scales["HAMD17"]
    yv, vv = statlib.lnvr(A("all_sd", h), A("all_n", h),
                          A("placebo_sd", h), A("placebo_n", h))
    mv = statlib.re_meta(yv, vv, method="PM")
    VR = float(np.exp(mv["mu"]))
    sPL = float(np.median(A("placebo_sd", h)))
    print("    HAMD17: k=%d, VR=%.4f [%.4f, %.4f], median placebo SD=%.2f points"
          % (mv["k"], VR, np.exp(mv["ci"][0]), np.exp(mv["ci"][1]), sPL))
    curve = {}
    print("      %-8s %-10s %-14s" % ("rho", "sigma_TE", "as % of the"))
    print("      %-8s %-10s %-14s" % ("", "(points)", "2.0-pt mean effect"))
    for rho in (0.0, -0.10, -0.21, -0.32, -0.50, -0.62):
        inside = VR ** 2 - 1 + rho ** 2
        s_te = sPL * (np.sqrt(inside) - rho) if inside >= 0 else float("nan")
        curve["%.2f" % rho] = float(s_te)
        print("      %-8.2f %-10.3f %-14.0f" % (rho, s_te, 100 * s_te / 2.0))
    out["sigma_TE_curve_HAMD17"] = dict(VR=VR, sd_placebo=sPL, curve=curve)

    print()
    print("=== 3. the multi-arm aggregation rule ===")
    multi = [r for r in rows if r["k_ad_arms"] > 1]
    print("    trials with >1 AD arm: %d of %d (%.0f%%)"
          % (len(multi), len(rows), 100 * len(multi) / len(rows)))
    a_sd, p_sd = A("all_sd"), A("pooled_sd")
    print("    mean(arm SDs) vs correct mixture SD, over the %d multi-arm trials:"
          % len(multi))
    ms = A("all_sd", multi)
    ps = A("pooled_sd", multi)
    print("      their SD is smaller in %d of %d trials; median ratio %.4f"
          % (int(np.sum(ms < ps)), len(multi), float(np.median(ms / ps))))
    print("      biggest single deflation: %.4f" % float(np.min(ms / ps)))
    for lab, sd1 in (("their rule  (mean of arm SDs)", a_sd),
                     ("mixture pooling (correct)   ", p_sd)):
        y, v = statlib.lnvr(sd1, A("all_n"), A("placebo_sd"), A("placebo_n"))
        m2 = statlib.re_meta(y, v, method="DL")
        print("      VR, %s = %.4f [%.4f, %.4f]  p=%.3f"
              % (lab, np.exp(m2["mu"]), np.exp(m2["ci"][0]),
                 np.exp(m2["ci"][1]), m2["p"]))
        out["VR_" + ("theirs" if "mean of" in lab else "mixture")] = dict(
            mu=m2["mu"], exp_mu=float(np.exp(m2["mu"])),
            exp_ci=[float(np.exp(m2["ci"][0])), float(np.exp(m2["ci"][1]))],
            p=m2["p"])
    y1, v1 = statlib.lnvr(a_sd, A("all_n"), A("placebo_sd"), A("placebo_n"))
    y2, v2 = statlib.lnvr(p_sd, A("all_n"), A("placebo_sd"), A("placebo_n"))
    diff = y2 - y1
    print("      per-trial lnVR shift, multi-arm trials only: mean %+.4f, max %+.4f"
          % (float(np.mean(diff[[i for i, r in enumerate(rows) if r["k_ad_arms"] > 1]])),
             float(np.max(diff))))

    print()
    print("=== 4. mean changes, for the record ===")
    m1, m2_ = A("all_m"), A("placebo_m")
    n1, n2 = A("all_n"), A("placebo_n")
    print("    n-weighted mean symptom reduction: AD %.2f pts, placebo %.2f pts"
          % ((n1 * m1).sum() / n1.sum(), (n2 * m2_).sum() / n2.sum()))
    print("    (unit-mixed across scales; HAMD17 only:)")
    hn1, hm1 = A("all_n", h), A("all_m", h)
    hn2, hm2 = A("placebo_n", h), A("placebo_m", h)
    print("    HAMD17: AD %.2f pts, placebo %.2f pts, difference %.2f pts, ratio %.3f"
          % ((hn1 * hm1).sum() / hn1.sum(), (hn2 * hm2).sum() / hn2.sum(),
             (hn1 * hm1).sum() / hn1.sum() - (hn2 * hm2).sum() / hn2.sum(),
             ((hn1 * hm1).sum() / hn1.sum()) / ((hn2 * hm2).sum() / hn2.sum())))
    out["mean_change_HAMD17"] = dict(
        ad=float((hn1 * hm1).sum() / hn1.sum()),
        placebo=float((hn2 * hm2).sum() / hn2.sum()))

    with io.open(os.path.join(HERE, "out_p03.json"), "w", encoding="utf-8",
                 newline="\n") as f:
        json.dump(out, f, indent=1)
    print()
    print("wrote out_p03.json")


if __name__ == "__main__":
    main()
