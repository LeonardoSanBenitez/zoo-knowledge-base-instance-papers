"""p05 -- p04A found my own D estimator biased upward (+0.58 pts^2 from a world
where D = 0 exactly, and 88.8% coverage of a nominal 95% interval). Diagnose the
mechanism, fix it, and re-verify on the same known worlds.

HYPOTHESIS. D_i = s1^2 - s2^2 is weighted by 1/v_i with
v_i = 2 s1^4/(n1-1) + 2 s2^4/(n2-1), estimated from the same draw. The weight is
therefore a function of the very quantity in the numerator. In THIS corpus the
placebo arms are smaller than the drug arms (18,746 vs 32,650 over 169 trials),
so the s2^4/(n2-1) term dominates v: a trial that happens to draw a large
placebo SD gets a large NEGATIVE d and a large v, and is down-weighted. Negative
deviations are shrunk more than positive ones, so the pooled estimate rides up.

If that is the mechanism, then:
  (P1) forcing n1 = n2 should shrink the bias sharply;
  (P2) making the placebo arm the LARGER one should reverse its sign;
  (P3) weights built from a quantity that does not contain the difference --
       the trial's pooled-across-arms variance -- should remove it.

Three predictions, each falsifiable. Then a corrected estimator, re-calibrated.
"""
import csv
import io
import json
import os
import sys

import numpy as np

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


def d_own(s1, n1, s2, n2):
    """the naive estimator: each trial's own SDs in its own weight."""
    return s1 ** 2 - s2 ** 2, 2 * s1 ** 4 / (n1 - 1) + 2 * s2 ** 4 / (n2 - 1)


def d_pooled_w(s1, n1, s2, n2):
    """CORRECTED: same d, but the weight uses the trial's ACROSS-ARM pooled
    variance, which does not contain the arm difference. Under H0 (equal arm
    variances) it is the efficient weight; under H1 it is still consistent and
    is no longer correlated with the sign of d."""
    sp2 = ((n1 - 1) * s1 ** 2 + (n2 - 1) * s2 ** 2) / (n1 + n2 - 2)
    v = 2 * sp2 ** 2 * (1.0 / (n1 - 1) + 1.0 / (n2 - 1))
    return s1 ** 2 - s2 ** 2, v


def d_n_weight(s1, n1, s2, n2):
    """weight by information only, with one common scale for the whole corpus."""
    d = s1 ** 2 - s2 ** 2
    sig4 = np.median(np.concatenate([s1, s2])) ** 4
    v = 2 * sig4 * (1.0 / (n1 - 1) + 1.0 / (n2 - 1))
    return d, v


ESTIMATORS = [("naive (own SDs in weight)", d_own),
              ("pooled-variance weight   ", d_pooled_w),
              ("common-scale weight      ", d_n_weight)]


def sim(n1, n2, s2_true, true_D, rng, B, est, method="PM"):
    v1 = s2_true ** 2 + true_D
    sd1 = np.sqrt(v1)
    hats, cov, ses = [], 0, []
    for _ in range(B):
        e1 = np.array([rng.normal(0, s, int(a)).std(ddof=1)
                       for a, s in zip(n1, sd1)])
        e2 = np.array([rng.normal(0, s, int(a)).std(ddof=1)
                       for a, s in zip(n2, s2_true)])
        d, v = est(e1, n1, e2, n2)
        m = statlib.re_meta(d, v, method=method)
        hats.append(m["mu"]); ses.append(m["se"])
        if m["ci"][0] <= true_D <= m["ci"][1]:
            cov += 1
    hats = np.array(hats)
    return dict(bias=float(hats.mean() - true_D), sd=float(hats.std(ddof=1)),
                coverage=float(cov) / B, mean_se=float(np.mean(ses)))


def main():
    rows = load()
    rng = np.random.default_rng(4242)
    n1 = np.array([r["all_n"] for r in rows])
    n2 = np.array([r["placebo_n"] for r in rows])
    s2 = np.array([r["placebo_sd"] for r in rows])
    B = 500
    out = {}

    print("=== 0. the asymmetry the hypothesis rests on ===")
    print("    AD arm n:      total %6d, median %5.0f" % (n1.sum(), np.median(n1)))
    print("    placebo arm n: total %6d, median %5.0f" % (n2.sum(), np.median(n2)))
    print("    trials with n_placebo < n_AD: %d of %d"
          % (int(np.sum(n2 < n1)), len(rows)))

    print()
    print("=== 1. three predictions of the mechanism (naive estimator, true D = 0) ===")
    cases = [("as observed (n_PL < n_AD)", n1, n2),
             ("P1: n1 = n2 = n_placebo ", n2, n2),
             ("P2: arms swapped         ", n2, n1)]
    for label, a, b in cases:
        r = sim(a, b, s2, 0.0, rng, B, d_own)
        print("    %-26s bias %+7.3f   coverage %5.1f%%"
              % (label, r["bias"], 100 * r["coverage"]))
        out["mech_" + label.split(":")[0].strip()] = r

    print()
    print("=== 2. P3: three weightings, five known worlds ===")
    print("    %-26s %8s %8s %8s %8s"
          % ("estimator / world", "bias", "sd", "coverage", "mean SE"))
    for name, est in ESTIMATORS:
        for true_D in (0.0, 5.0, -5.0):
            r = sim(n1, n2, s2, true_D, rng, B, est)
            print("    %-26s %+8.3f %8.3f %7.1f%% %8.3f"
                  % (("%s D=%+.0f" % (name.strip()[:18], true_D)),
                     r["bias"], r["sd"], 100 * r["coverage"], r["mean_se"]))
            out["%s|D=%+.0f" % (name.strip(), true_D)] = r
        print()

    print("=== 3. the real corpus, under all three weightings ===")
    scales = {}
    for r in rows:
        scales.setdefault(r["scale"], []).append(r)
    real = {}
    for sc in ["HAMD17", "HAMD21", "MADRS", None]:
        sub = rows if sc is None else scales[sc]
        a1 = np.array([r["all_sd"] for r in sub])
        b1 = np.array([r["all_n"] for r in sub])
        a2 = np.array([r["placebo_sd"] for r in sub])
        b2 = np.array([r["placebo_n"] for r in sub])
        label = sc or "ALL (unit-mixed)"
        line = "    %-16s k=%3d " % (label, len(sub))
        for name, est in ESTIMATORS:
            d, v = est(a1, b1, a2, b2)
            m = statlib.re_meta(d, v, method="PM")
            line += "  %s %+6.3f [%+6.3f,%+6.3f]" % (
                name.strip().split()[0][:6], m["mu"], m["ci"][0], m["ci"][1])
            real["%s|%s" % (label, name.strip().split()[0])] = dict(
                k=m["k"], mu=m["mu"], ci=list(m["ci"]), I2=m["I2"])
        print(line)
    out["real"] = real

    with io.open(os.path.join(HERE, "out_p05.json"), "w", encoding="utf-8",
                 newline="\n") as f:
        json.dump(out, f, indent=1)
    print()
    print("wrote out_p05.json")


if __name__ == "__main__":
    main()
