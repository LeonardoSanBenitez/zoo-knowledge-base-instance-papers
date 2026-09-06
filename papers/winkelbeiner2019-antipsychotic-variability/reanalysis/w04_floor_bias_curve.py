"""w04 -- turn the floor caveat into a general instrument.

w03 showed the PANSS floor can produce most of the observed negative D with zero
heterogeneity, and that the answer swings from 23% to 112% of the observed value over
a baseline mean the deposit does not record. That is a corpus-specific mess. The
mechanism is not corpus-specific and can be stated once.

SETUP. An outcome bounded below (a symptom scale that stops at zero, a count, a
latency, a score with a floor) is measured as an improvement X from a starting point.
The improvement cannot exceed the HEADROOM H = start - floor. What is recorded is
min(X, H). Truncation removes the upper tail of X, so the recorded SD is smaller than
the true one, and the loss grows as the mean improvement approaches the headroom.

The whole effect is governed by one dimensionless number:

        z = (mean headroom - mean improvement) / SD(improvement)

i.e. how many improvement-SDs of room are left. Large z, nothing happens; small z, the
arm is compressed. **The treated arm always has the smaller z**, because it improves
more. So a bounded scale always biases VR DOWNWARD, and always in the direction that
looks like "the treatment reduces variability".

This script computes the shrinkage factor f(z) = SD(recorded)/SD(true) once, on a
grid, then locates each corpus on that grid. The table is reusable by anyone
comparing dispersion on a bounded outcome and is copied into
instance-general/statistics/comparing-dispersion-between-two-groups.md.
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

RNG = np.random.default_rng(4040)
N = 400000


def shrink(z, cv_headroom=0.0):
    """SD(min(X, H)) / SD(X) for X ~ N(m, s) and H ~ N(m + z s, cv_headroom * s).

    Only z matters when the headroom is fixed; cv_headroom adds the realistic case
    where subjects differ in how much room they have.
    """
    s = 1.0
    x = RNG.normal(0.0, s, N)
    h = RNG.normal(z * s, cv_headroom * s, N) if cv_headroom > 0 else np.full(N, z * s)
    y = np.minimum(x, h)
    return float(y.std(ddof=1) / x.std(ddof=1))


def main():
    out = {}
    print("=== f(z) = SD(recorded) / SD(true), X normal, headroom z SDs above the mean ===")
    print("  %-6s %-12s %-12s %-12s" % ("z", "fixed H", "H sd = 1.0", "H sd = 2.0"))
    grid = {}
    for z in (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0):
        a, b, c = shrink(z), shrink(z, 1.0), shrink(z, 2.0)
        grid["%.1f" % z] = dict(fixed=a, h_sd_1=b, h_sd_2=c)
        print("  %-6.1f %-12.4f %-12.4f %-12.4f" % (z, a, b, c))
    out["shrinkage"] = grid
    print()
    print("  Read it as: at z = 1.5 SDs of headroom, an arm's SD is already ~%.0f%%"
          % (100 * grid['1.5']['h_sd_1']))
    print("  of its true value when subjects differ in headroom by 1 SD.")

    print()
    print("=== implied VR bias: both arms on the same curve ===")
    print("  VR_observed / VR_true = f(z_treated) / f(z_control)")
    print("  %-10s %-10s %-14s" % ("z_control", "z_treated", "VR bias"))
    for zc, zt in ((3.0, 2.5), (2.5, 2.0), (2.0, 1.5), (1.5, 1.0), (1.0, 0.5)):
        r = shrink(zt, 1.0) / shrink(zc, 1.0)
        print("  %-10.1f %-10.1f %-14.4f" % (zc, zt, r))
        out.setdefault("vr_bias", {})["%.1f->%.1f" % (zc, zt)] = float(r)

    print()
    print("=== where the two corpora sit ===")
    # antipsychotics
    rows = []
    with io.open(os.path.join(HERE, "..", "artifacts", "response.csv"),
                 encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                rows.append(dict(m1=abs(float(r["mu1tx"])), m2=abs(float(r["mu1ct"])),
                                 s1=float(r["sd1tx"]), s2=float(r["sd1ct"]),
                                 n1=float(r["ntx"]), n2=float(r["nct"])))
            except (ValueError, KeyError):
                continue
    n1 = np.array([r["n1"] for r in rows]); n2 = np.array([r["n2"] for r in rows])
    m1 = np.array([r["m1"] for r in rows]); m2 = np.array([r["m2"] for r in rows])
    s1 = np.array([r["s1"] for r in rows]); s2 = np.array([r["s2"] for r in rows])
    print("  PANSS, floor 30, baseline mean unknown (not in the deposit):")
    for base in (80, 85, 90, 95, 100):
        H = base - 30.0
        zt = float(np.average((H - m1) / s1, weights=n1))
        zc = float(np.average((H - m2) / s2, weights=n2))
        bias = shrink(zt, 1.0) / shrink(zc, 1.0)
        print("    baseline %3d -> headroom %2.0f: z_treated %.2f, z_control %.2f, "
              "VR bias %.4f" % (base, H, zt, zc, bias))
        out.setdefault("panss", {})[str(base)] = dict(z_tx=zt, z_ct=zc, bias=float(bias))
    print("  observed VR = 0.968; published 0.97 [0.95, 0.99]")

    ad = os.path.join(HERE, "..", "..", "ploderl2019-personalised-antidepressants",
                      "reanalysis", "dat.csv")
    if os.path.exists(ad):
        rr = []
        with io.open(ad, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter=";"):
                if r["scale"] != "HAMD17" or not r["baseline"]:
                    continue
                try:
                    rr.append(dict(m1=float(r["all_m"]), m2=float(r["placebo_m"]),
                                   s1=float(r["all_sd"]), s2=float(r["placebo_sd"]),
                                   n1=float(r["all_n"]), n2=float(r["placebo_n"]),
                                   b=float(r["baseline"])))
                except ValueError:
                    continue
        an1 = np.array([r["n1"] for r in rr]); an2 = np.array([r["n2"] for r in rr])
        am1 = np.array([r["m1"] for r in rr]); am2 = np.array([r["m2"] for r in rr])
        as1 = np.array([r["s1"] for r in rr]); as2 = np.array([r["s2"] for r in rr])
        ab = np.array([r["b"] for r in rr])
        zt = float(np.average((ab - am1) / as1, weights=an1))
        zc = float(np.average((ab - am2) / as2, weights=an2))
        bias = shrink(zt, 1.0) / shrink(zc, 1.0)
        print("  HAMD17, floor 0, baseline mean IS reported (n-weighted %.1f):"
              % float(np.average(ab, weights=an1)))
        print("    z_treated %.2f, z_control %.2f, VR bias %.4f  (k = %d)"
              % (zt, zc, bias, len(rr)))
        print("  observed VR on this subset = %.4f"
              % float(np.exp(statlib.re_meta(*statlib.lnvr(as1, an1, as2, an2),
                                             method="DL")["mu"])))
        out["hamd17"] = dict(z_tx=zt, z_ct=zc, bias=float(bias), k=len(rr))

    print()
    print("=== the point ===")
    print("  The antipsychotic corpus sits at low headroom and the antidepressant")
    print("  corpus does not, which is why the same statistic reads 0.97 in one and")
    print("  1.01 in the other WITHOUT any difference in individual response being")
    print("  required. The two literatures have been compared to each other as though")
    print("  the statistic meant the same thing in both.")

    with io.open(os.path.join(HERE, "out_w04.json"), "w", encoding="utf-8",
                 newline="\n") as f:
        json.dump(out, f, indent=1)
    print()
    print("wrote out_w04.json")


if __name__ == "__main__":
    main()
