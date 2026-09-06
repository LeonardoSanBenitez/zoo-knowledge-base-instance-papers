"""p07 -- does the additive-vs-multiplicative verdict of p04B survive a realistic
data generator?

p04B simulated the additive null with plain normal change scores and got a null
slope of +0.003 -- essentially zero. On my two earlier corpora the additive null
slope was NOT zero (about +0.47), and the reason given there was mean-SD coupling
in skewed data. A normal generator has no such coupling by construction, so p04B
may have made the null too easy for the observed +0.053 to sit inside.

A depression change score is bounded: you cannot improve by more than your
baseline score, and the post-treatment score cannot go below zero. Trials with a
larger mean reduction therefore push more patients against the floor, which
COMPRESSES the arm's SD. That is a mean-SD coupling with a definite sign, and it
is present in the real data whether or not anyone models it.

So: rerun the null with a floored generator, using each trial's own reported
baseline severity. Three worlds, one observed statistic:

    additive-normal        the p04B null, kept for comparison
    additive-floored       same, but post-score truncated at 0
    multiplicative         treatment scales every patient's change

If the floored additive null moves the null slope near the observed value, the
verdict stands and is stronger. If it moves it past, the verdict is not safe and
must be reported as undecided. Written before running it.
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
    return [r for r in rows if np.isfinite(r["baseline"])]


def arm(n, mean_change, sd, base, rng, floor):
    """draw n change scores; if floor, the post score cannot go below zero,
    which caps the improvement at the patient's own baseline."""
    ch = rng.normal(mean_change, sd, int(n))
    if floor:
        b = rng.normal(base, sd, int(n))          # patient baselines vary too
        ch = np.minimum(ch, np.maximum(b, 0.0))
    return abs(ch.mean()), ch.std(ddof=1)


def run(rows, world, rng, B):
    n1 = np.array([r["all_n"] for r in rows])
    n2 = np.array([r["placebo_n"] for r in rows])
    m1 = np.array([r["all_m"] for r in rows])
    m2 = np.array([r["placebo_m"] for r in rows])
    s2 = np.array([r["placebo_sd"] for r in rows])
    bs = np.array([r["baseline"] for r in rows])
    slopes = []
    for _ in range(B):
        M1, S1, M2, S2 = [], [], [], []
        for i in range(len(rows)):
            if world == "multiplicative":
                k = m1[i] / m2[i]
                a = arm(n1[i], m2[i] * k, s2[i] * k, bs[i], rng, False)
                p = arm(n2[i], m2[i], s2[i], bs[i], rng, False)
            else:
                fl = (world == "additive-floored")
                a = arm(n1[i], m1[i], s2[i], bs[i], rng, fl)
                p = arm(n2[i], m2[i], s2[i], bs[i], rng, fl)
            M1.append(a[0]); S1.append(a[1]); M2.append(p[0]); S2.append(p[1])
        y, _ = statlib.lnvr(np.array(S1), n1, np.array(S2), n2)
        slopes.append(stats.linregress(np.log(np.array(M1) / np.array(M2)),
                                       y).slope)
    return np.array(slopes)


def main():
    rows = load()
    rng = np.random.default_rng(70707)
    n1 = np.array([r["all_n"] for r in rows])
    n2 = np.array([r["placebo_n"] for r in rows])
    m1 = np.array([r["all_m"] for r in rows])
    m2 = np.array([r["placebo_m"] for r in rows])
    s1 = np.array([r["all_sd"] for r in rows])
    s2 = np.array([r["placebo_sd"] for r in rows])
    print("trials with a reported baseline severity: %d of 169" % len(rows))
    y, _ = statlib.lnvr(s1, n1, s2, n2)
    obs = stats.linregress(np.log(m1 / m2), y)
    print("observed slope on this subset = %+.4f (SE %.4f)" % (obs.slope, obs.stderr))

    out = {"observed": dict(slope=float(obs.slope), se=float(obs.stderr),
                            k=len(rows))}
    B = 300
    for world in ("additive-normal", "additive-floored", "multiplicative"):
        sl = run(rows, world, rng, B)
        lo, hi = np.percentile(sl, [2.5, 97.5])
        z = (obs.slope - sl.mean()) / sl.std(ddof=1)
        inside = lo <= obs.slope <= hi
        print("  %-18s null %+.4f  [%+.4f, %+.4f]  observed %+5.1f SD away  %s"
              % (world, sl.mean(), lo, hi, z,
                 "OBSERVED INSIDE" if inside else "observed outside"))
        out[world] = dict(null=float(sl.mean()), ci=[float(lo), float(hi)],
                          z=float(z), inside=bool(inside), B=B)

    a_n, a_f, mu = out["additive-normal"], out["additive-floored"], out["multiplicative"]
    verdict = ("additive stands" if (a_n["inside"] or a_f["inside"])
               and not mu["inside"] else "UNDECIDED")
    print()
    print("verdict: %s" % verdict)
    if a_f["inside"] and not a_n["inside"]:
        print("  and the floored null is the one that contains the observation,")
        print("  which means the normal-generator null in p04B was the wrong null.")
    out["verdict"] = verdict
    with io.open(os.path.join(HERE, "out_p07.json"), "w", encoding="utf-8",
                 newline="\n") as f:
        json.dump(out, f, indent=1)
    print("wrote out_p07.json")


if __name__ == "__main__":
    main()
