"""m11 -- recompute D on this corpus with the corrected weight.

WHY THIS EXISTS. m09 reported D = sigma_AT^2 - sigma_PL^2 = -0.384
[-1.636, +0.868] squared HAMD points for the antidepressant comparisons, pooled
by inverse-variance weighting with v_i = 2 s1^4/(n1-1) + 2 s2^4/(n2-1). On
2026-09-06, working on `ploderl2019-personalised-antidepressants`, that
estimator was fed worlds whose answer was known by construction and found
BIASED: it returned +0.514 points^2 from a corpus with D = 0 exactly, with 90.2%
coverage of a nominal 95% interval.

The mechanism is that the weight is a function of the same random quantities as
the numerator, and the resulting shrinkage is asymmetric whenever the two arms
differ in size: the smaller arm's s^4 dominates v, so whichever side is smaller
gets its deviations down-weighted harder, and the pool drifts the other way.
The sign therefore depends on THIS corpus's own arm-size asymmetry, which is not
the same as Ploderl's. -0.384 is not "too high" or "too low" until measured.

Two corrections at once, because both were live in the same number:

  1. the weight -> 2 s_p^4 (1/(n1-1) + 1/(n2-1)) with s_p the across-arm pooled
     variance, verified unbiased (-0.003) with 96.6% coverage;
  2. the UNITS -> D is in squared points OF A SCALE. m09 pooled HAMD17, HAMD21,
     MADRS and others into one number. Report per scale.

Run: python m11_D_reweighted.py
"""
import csv
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "tools"))
from statlib import re_meta  # noqa: E402

REAL = os.path.join(HERE, "..", "..", "munkholm2020-antidepressant-variability",
                    "reanalysis", "out_comparisons.csv")
RNG = np.random.default_rng(11111)


def load():
    rows = []
    with open(REAL, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            try:
                rows.append(dict(
                    study=r["study"], scale=r["scale"],
                    n1=float(r["n_drug"]), s1=float(r["sd_drug"]),
                    n2=float(r["n_pbo"]), s2=float(r["sd_pbo"])))
            except (ValueError, KeyError):
                continue
    return [r for r in rows if r["n1"] > 2 and r["n2"] > 2
            and r["s1"] > 0 and r["s2"] > 0]


def d_naive(s1, n1, s2, n2):
    return s1 ** 2 - s2 ** 2, 2 * s1 ** 4 / (n1 - 1) + 2 * s2 ** 4 / (n2 - 1)


def d_pooled(s1, n1, s2, n2):
    sp2 = ((n1 - 1) * s1 ** 2 + (n2 - 1) * s2 ** 2) / (n1 + n2 - 2)
    return s1 ** 2 - s2 ** 2, 2 * sp2 ** 2 * (1.0 / (n1 - 1) + 1.0 / (n2 - 1))


def calibrate(n1, n2, s2, true_D, est, B=400):
    """what does `est` return on THIS corpus's arm structure when D is known?"""
    sd1 = np.sqrt(s2 ** 2 + true_D)
    hats, cov = [], 0
    for _ in range(B):
        e1 = np.array([RNG.normal(0, s, int(a)).std(ddof=1)
                       for a, s in zip(n1, sd1)])
        e2 = np.array([RNG.normal(0, s, int(a)).std(ddof=1)
                       for a, s in zip(n2, s2)])
        d, v = est(e1, n1, e2, n2)
        m = re_meta(d, v, method="PM")
        hats.append(m["mu"])
        if m["ci"][0] <= true_D <= m["ci"][1]:
            cov += 1
    return float(np.mean(hats) - true_D), cov / float(B)


def main():
    rows = load()
    n1 = np.array([r["n1"] for r in rows]); s1 = np.array([r["s1"] for r in rows])
    n2 = np.array([r["n2"] for r in rows]); s2 = np.array([r["s2"] for r in rows])
    print("comparisons usable: %d" % len(rows))
    print("arm sizes: drug median %.0f (total %d), placebo median %.0f (total %d)"
          % (np.median(n1), n1.sum(), np.median(n2), n2.sum()))
    print("drug arm SMALLER than placebo in %d of %d comparisons (%.0f%%)"
          % (int(np.sum(n1 < n2)), len(rows), 100 * np.mean(n1 < n2)))
    print("  -> the asymmetry here is the OPPOSITE of Ploderl's corpus, where")
    print("     the placebo arm was the smaller one in 116 of 169 trials.")

    print()
    print("=== calibration on THIS corpus's arm structure, true D = 0 ===")
    for name, est in (("naive (own SDs in weight)", d_naive),
                      ("pooled-variance weight   ", d_pooled)):
        b, c = calibrate(n1, n2, s2, 0.0, est)
        print("    %-26s bias %+7.3f   coverage %5.1f%%" % (name, b, 100 * c))

    print()
    print("=== D by scale, both weights ===")
    scales = {}
    for i, r in enumerate(rows):
        scales.setdefault(r["scale"], []).append(i)
    print("    %-14s %5s   %-26s %-26s"
          % ("scale", "k", "naive weight", "pooled-variance weight"))
    for sc in sorted(scales, key=lambda s: -len(scales[s])):
        idx = np.array(scales[sc])
        if len(idx) < 5:
            continue
        line = "    %-14s %5d " % (sc, len(idx))
        for est in (d_naive, d_pooled):
            d, v = est(s1[idx], n1[idx], s2[idx], n2[idx])
            m = re_meta(d, v, method="PM")
            line += "  %+7.3f [%+7.3f,%+7.3f]" % (m["mu"], m["ci"][0], m["ci"][1])
        print(line)
    line = "    %-14s %5d " % ("ALL (mixed)", len(rows))
    for est in (d_naive, d_pooled):
        d, v = est(s1, n1, s2, n2)
        m = re_meta(d, v, method="PM")
        line += "  %+7.3f [%+7.3f,%+7.3f]" % (m["mu"], m["ci"][0], m["ci"][1])
    print(line)
    print("    (the ALL row is the shape of the m09 number, kept only for")
    print("     comparability; it mixes squared points of different scales)")


if __name__ == "__main__":
    main()
