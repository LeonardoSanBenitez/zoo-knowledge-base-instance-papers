"""m12 -- the correction from p05 buys unbiasedness and sells robustness. Measure
the exchange rate before recommending it.

m11 found the HAMD21 subset of this corpus flips sign between the two weights
(-0.554 naive, +0.902 pooled) and that ONE trial does it: Dube2010
(NCT00420004), placebo SD 3.3 on HAMD21 with n = 122, drug SD 8.8 with n = 54,
so d_i = +66.5 squared points against a corpus whose pooled D is under one.
Dropping it moves the naive estimate by -0.490 and the pooled estimate by
-1.924.

That is not a coincidence and it is not a defect of the data. It is the same
mechanism the p05 bias came from, seen from the other side:

    naive weight   v_i grows as s_i^4, so a trial with a large variance in
                   EITHER arm is automatically down-weighted. That is the bias
                   (it shrinks negative deviations harder when the placebo arm
                   is smaller) and it is ALSO an automatic outlier guard.

    pooled weight  v_i uses the across-arm pooled variance, which is moderate
                   whenever the two arms disagree, so a trial with a huge
                   variance RATIO keeps a large weight. Unbiased under the null,
                   and fully exposed to one anomalous trial.

So the recommendation from p05 -- "use the pooled-variance weight" -- is
incomplete. Measure both properties on the same corpora and state the pairing.

Two measurements:
  1. INFLUENCE. Max |leave-one-out delta| for each weight, per scale subset,
     against the half-width of that subset's own interval. An estimator whose
     single most influential point moves it by more than its own CI half-width
     is not reporting a corpus, it is reporting a trial.
  2. CONTAMINATED CALIBRATION. Re-run the p05 known-answer test with ONE trial
     drawn from a variance-inflated world, and see which estimator still
     recovers D = 0.

Run: python m12_bias_vs_robustness.py
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
RNG = np.random.default_rng(1212)


def load():
    rows = []
    with open(REAL, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            try:
                d = dict(study=r["study"], scale=r["scale"],
                         n1=float(r["n_drug"]), s1=float(r["sd_drug"]),
                         n2=float(r["n_pbo"]), s2=float(r["sd_pbo"]))
            except (ValueError, KeyError):
                continue
            if d["n1"] > 2 and d["n2"] > 2 and d["s1"] > 0 and d["s2"] > 0:
                rows.append(d)
    return rows


def d_naive(s1, n1, s2, n2):
    return s1 ** 2 - s2 ** 2, 2 * s1 ** 4 / (n1 - 1) + 2 * s2 ** 4 / (n2 - 1)


def d_pooled(s1, n1, s2, n2):
    sp2 = ((n1 - 1) * s1 ** 2 + (n2 - 1) * s2 ** 2) / (n1 + n2 - 2)
    return s1 ** 2 - s2 ** 2, 2 * sp2 ** 2 * (1.0 / (n1 - 1) + 1.0 / (n2 - 1))


ESTS = (("naive ", d_naive), ("pooled", d_pooled))


def influence(s1, n1, s2, n2, est):
    d, v = est(s1, n1, s2, n2)
    m = re_meta(d, v, method="PM")
    full, half = m["mu"], (m["ci"][1] - m["ci"][0]) / 2.0
    worst, arg = 0.0, -1
    for i in range(len(s1)):
        k = [j for j in range(len(s1)) if j != i]
        mm = re_meta(*est(s1[k], n1[k], s2[k], n2[k]), method="PM")
        if abs(mm["mu"] - full) > abs(worst):
            worst, arg = mm["mu"] - full, i
    return full, half, worst, arg


def main():
    rows = load()
    scales = {}
    for i, r in enumerate(rows):
        scales.setdefault(r["scale"], []).append(i)

    print("=== 1. influence: how much does the single worst trial move each? ===")
    print("    %-10s %4s %-7s  %-9s %-9s %-7s  %s"
          % ("scale", "k", "weight", "pooled D", "CI half", "max LOO", "and which trial"))
    for sc in sorted(scales, key=lambda s: -len(scales[s])):
        idx = np.array(scales[sc])
        if len(idx) < 20:
            continue
        s1 = np.array([rows[i]["s1"] for i in idx])
        n1 = np.array([rows[i]["n1"] for i in idx])
        s2 = np.array([rows[i]["s2"] for i in idx])
        n2 = np.array([rows[i]["n2"] for i in idx])
        for name, est in ESTS:
            full, half, worst, arg = influence(s1, n1, s2, n2, est)
            flag = "  <-- MOVES IT BY MORE THAN ITS OWN CI" if abs(worst) > half else ""
            print("    %-10s %4d %-7s  %+9.3f %9.3f %+7.3f  %s%s"
                  % (sc, len(idx), name, full, half, worst,
                     rows[idx[arg]]["study"][:24], flag))

    print()
    print("=== 2. calibration with ONE contaminated trial, true D = 0 elsewhere ===")
    idx = np.array(scales["HAMD21"])
    n1 = np.array([rows[i]["n1"] for i in idx])
    n2 = np.array([rows[i]["n2"] for i in idx])
    s2 = np.array([rows[i]["s2"] for i in idx])
    print("    HAMD21 arm structure, k = %d, %d simulated corpora per cell." % (len(idx), 300))
    print("    Trial 0 is given a true SD ratio of c; every other trial has D = 0.")
    print("    %-6s %-24s %-24s" % ("c", "naive", "pooled-variance"))
    for c in (1.0, 1.5, 2.0, 2.7):
        res = {}
        for name, est in ESTS:
            hats = []
            for _ in range(300):
                sd1 = s2.copy()
                sd1[0] = s2[0] * c
                e1 = np.array([RNG.normal(0, s, int(a)).std(ddof=1)
                               for a, s in zip(n1, sd1)])
                e2 = np.array([RNG.normal(0, s, int(a)).std(ddof=1)
                               for a, s in zip(n2, s2)])
                hats.append(re_meta(*est(e1, n1, e2, n2), method="PM")["mu"])
            res[name] = (float(np.mean(hats)), float(np.std(hats, ddof=1)))
        print("    %-6.1f %+8.3f (sd %.3f)      %+8.3f (sd %.3f)"
              % (c, res["naive "][0], res["naive "][1],
                 res["pooled"][0], res["pooled"][1]))
    print()
    print("    c = 1.0 is the clean null (the p05 test). c = 2.7 is Dube2010.")
    print("    Truth is D = 0 for 128 of 129 trials in every row.")


if __name__ == "__main__":
    main()
