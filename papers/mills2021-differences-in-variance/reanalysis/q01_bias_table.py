"""q01 -- how biased is the published difference-in-variances estimator, as a
function of arm imbalance, so a reader can look up their own corpus.

WHY A TABLE RATHER THAN THEIR TWO EXAMPLES. Their deposit carries code and no
data, and their two applied meta-analyses draw on a Cochrane review and a
published synthesis whose trial-level tables I would have to transcribe. A table
over arm imbalance is more useful than either: it answers the question for every
corpus, including theirs once someone reads off its arm sizes.

THE ESTIMATOR, from MetaAnalysis.R lines 129-144:

    est_diff    = s1^2 - s2^2
    est_diff_SE = sqrt( (s1^2 sqrt(2/(n1-1)))^2 + (s2^2 sqrt(2/(n2-1)))^2 )
                = sqrt( 2 s1^4/(n1-1) + 2 s2^4/(n2-1) )
    metagen(est_diff, est_diff_SE)          # inverse-variance pooling

The weight is a function of the same draw as the numerator. Whichever arm is
smaller contributes more to the weight, its downward fluctuations are penalised
harder than its upward ones, and the pool drifts away from it.

WHAT IS REPORTED. Bias in units of the true variance (so it is scale-free and
directly comparable to a reported D), and the realised coverage of the nominal
95% interval. Truth is D = 0 in every cell: both arms have variance sigma^2, so
any non-zero pooled estimate is the artifact and nothing else.
"""
import io
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "tools"))
import statlib  # noqa: E402

RNG = np.random.default_rng(2021)
SIGMA = 10.0                      # arbitrary; results are reported as bias/sigma^2


def cell(k, n_small, ratio, weight, reps=400):
    """k trials; the control arm has n_small, the treated arm has ratio*n_small.
    True variance identical in both arms, so D = 0 exactly."""
    n2 = np.full(k, float(n_small))
    n1 = np.full(k, float(n_small) * ratio)
    hats, cov = [], 0
    for _ in range(reps):
        s1 = np.array([RNG.normal(0, SIGMA, int(a)).std(ddof=1) for a in n1])
        s2 = np.array([RNG.normal(0, SIGMA, int(a)).std(ddof=1) for a in n2])
        d, v = statlib.var_diff(s1, n1, s2, n2, weight=weight)
        m = statlib.re_meta(d, v, method="PM")
        hats.append(m["mu"])
        if m["ci"][0] <= 0.0 <= m["ci"][1]:
            cov += 1
    return float(np.mean(hats)) / (SIGMA ** 2), cov / float(reps)


def main():
    out = {}
    print("Bias of the published estimator, in units of the true variance.")
    print("Truth is D = 0 in every cell. k = 30 trials, control arm n = 100.")
    print()
    print("  %-22s" % "treated/control n" + "".join("%-11s" % ("%.2g" % r)
                                                    for r in RATIOS))
    for weight, label in (("naive", "published (Mills et al.)"),
                          ("pooled", "pooled-variance weight")):
        line = "  %-22s" % label
        cov_line = "  %-22s" % "  its 95% coverage"
        for r in RATIOS:
            b, c = cell(30, 100, r, weight)
            line += "%-11.4f" % b
            cov_line += "%-11.3f" % c
            out.setdefault(label, {})["%.2f" % r] = dict(bias=b, coverage=c)
        print(line)
        print(cov_line)
        print()

    print("Read a row as: a corpus whose treated arms are TWICE the control arms")
    print("will report a pooled D of about %+.3f sigma^2 when the true D is zero."
          % out["published (Mills et al.)"]["2.00"]["bias"])
    print()
    print("=== DO NOT INTERPOLATE THIS TABLE ONTO A REAL CORPUS ===")
    print("  Every cell above has identical arm sizes and one common variance. A")
    print("  real corpus mixes both across trials, which dilutes the bias in a way")
    print("  no table captures. Measured directly on two real psychiatric corpora")
    print("  with the same estimator: +0.514 squared points on one (169 trials,")
    print("  control arms smaller in 116 of them) and +0.054 on the other (344")
    print("  comparisons, arms balanced). A tenfold difference from the same")
    print("  weight, and the table would have predicted neither.")
    print()
    print("  The table says WHICH DIRECTION and ROUGHLY HOW BIG. For a number,")
    print("  calibrate against your own arm sizes:")
    print("      statlib.calibrate_var_diff(n1, n2, sd_control, weight='naive')")
    print("  which returns the bias WITH ITS MONTE-CARLO ERROR, because at a few")
    print("  hundred replicates that error is often larger than the residual bias")
    print("  of the corrected weight and the two must not be confused.")

    print()
    print("=== dependence on the number of trials ===")
    print("  The bias is a property of the WEIGHT, not of the sample of trials, so")
    print("  it does not shrink as k grows -- only its own uncertainty does. That")
    print("  is the difference between a bias and a noise, and it is why a large")
    print("  meta-analysis does not rescue this one.")
    print("  %-10s %-14s %-10s" % ("k trials", "bias/sigma^2", "coverage"))
    for k in (10, 30, 100, 300):
        b, c = cell(k, 100, 2.0, "naive", reps=250)
        print("  %-10d %-14.4f %-10.3f" % (k, b, c))
        out.setdefault("k_sweep", {})[str(k)] = dict(bias=b, coverage=c)

    with io.open(os.path.join(HERE, "out_q01.json"), "w", encoding="utf-8",
                 newline="\n") as f:
        json.dump(out, f, indent=1)
    print()
    print("wrote out_q01.json")


RATIOS = (0.25, 0.5, 1.0, 1.5, 2.0, 4.0)

if __name__ == "__main__":
    main()
