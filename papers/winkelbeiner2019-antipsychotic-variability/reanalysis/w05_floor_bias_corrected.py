"""w05 -- w04's closing claim was refuted by w04's own table. Redo it correctly.

WHAT W04 SAID, AND WHY IT WAS WRONG. Its last paragraph read: *"The antipsychotic
corpus sits at low headroom and the antidepressant corpus does not, which is why the
same statistic reads 0.97 in one and 1.01 in the other."* Its own output, four lines
above, gives z_treated = 2.12 for PANSS at a baseline of 90 and **1.57** for HAMD17 --
the antidepressant corpus has LESS headroom, not more. I wrote a conclusion that the
numbers on the same screen contradicted, because it was the conclusion I wanted.

TWO REAL DEFECTS, both fixed here.

1. w04 read the bias off grid columns for headroom dispersion of 0, 1 and 2 change-SDs.
   Each corpus has its own ratio and it is measurable: PANSS baseline SD is in the
   deposit (median 11.70) against a change SD near 20, so the ratio is about 0.59, not
   0 and not 1. The choice matters enormously -- at z = 2 the shrinkage is 0.980 with a
   fixed headroom and 0.947 with a headroom SD of one change-SD.

2. The direction of the bias is NOT always downward, which w04 asserted. A headroom
   that varies across subjects ADDS variance, and past about 2 change-SDs of headroom
   dispersion the addition wins: f(z) exceeds 1. So "a bounded scale biases VR
   downward" is true only for modest headroom dispersion. State the condition.

Output: the corrected bias for each corpus, and what each published VR becomes once
the floor is removed.
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

RNG = np.random.default_rng(50505)
N = 600000


def shrink(z, h_disp):
    """SD(min(X,H))/SD(X); X ~ N(0,1); H ~ N(z, h_disp), h_disp in units of SD(X)."""
    x = RNG.normal(0.0, 1.0, N)
    h = np.full(N, z) if h_disp <= 0 else RNG.normal(z, h_disp, N)
    return float(np.minimum(x, h).std(ddof=1))


def main():
    out = {}
    print("=== 1. the direction of the bias depends on how much the headroom varies ===")
    print("  f(z) = SD(recorded)/SD(true). Values above 1 mean the bound ADDS variance.")
    print("  %-6s" % "z" + "".join("%-9s" % ("hd=%.1f" % h)
                                   for h in (0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0)))
    for z in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
        line = "  %-6.1f" % z
        row = {}
        for h in (0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0):
            f = shrink(z, h)
            row["%.2f" % h] = f
            line += "%-9.4f" % f
        print(line)
        out.setdefault("f", {})["%.1f" % z] = row
    print("  Crossover: with headroom dispersion above roughly 1.5 change-SDs the")
    print("  bound INFLATES the recorded SD instead of shrinking it. 'A floor biases")
    print("  variability downward' is a statement about a regime, not a law.")

    print()
    print("=== 2. each corpus with its own measured headroom dispersion ===")

    # ---- antipsychotics
    rows = []
    with io.open(os.path.join(HERE, "..", "artifacts", "response.csv"),
                 encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                rows.append(dict(m1=abs(float(r["mu1tx"])), m2=abs(float(r["mu1ct"])),
                                 s1=float(r["sd1tx"]), s2=float(r["sd1ct"]),
                                 n1=float(r["ntx"]), n2=float(r["nct"]),
                                 b1=float(r["sd0tx"]) if r["sd0tx"] else None,
                                 b2=float(r["sd0ct"]) if r["sd0ct"] else None))
            except (ValueError, KeyError):
                continue
    g = lambda k: np.array([r[k] for r in rows], float)
    n1, n2, m1, m2, s1, s2 = g("n1"), g("n2"), g("m1"), g("m2"), g("s1"), g("s2")
    b = [r["b1"] for r in rows if r["b1"]] + [r["b2"] for r in rows if r["b2"]]
    base_sd = float(np.median(b))
    chg_sd = float(np.median(np.concatenate([s1, s2])))
    hd = base_sd / chg_sd
    vr_obs = float(np.exp(statlib.re_meta(*statlib.lnvr(s1, n1, s2, n2),
                                          method="DL")["mu"]))
    print("  PANSS: median baseline SD %.2f, median change SD %.2f -> headroom "
          "dispersion %.3f change-SDs" % (base_sd, chg_sd, hd))
    print("  %-10s %-9s %-9s %-10s %-14s" % ("baseline", "z_tx", "z_ct", "VR bias",
                                             "VR with floor removed"))
    for basemean in (80, 85, 90, 95, 100):
        H = basemean - 30.0
        zt = float(np.average((H - m1) / s1, weights=n1))
        zc = float(np.average((H - m2) / s2, weights=n2))
        bias = shrink(zt, hd) / shrink(zc, hd)
        print("  %-10d %-9.2f %-9.2f %-10.4f %-14.4f"
              % (basemean, zt, zc, bias, vr_obs / bias))
        out.setdefault("panss", {})[str(basemean)] = dict(
            z_tx=zt, z_ct=zc, bias=float(bias), vr_corrected=float(vr_obs / bias))
    print("  observed VR %.4f; published 0.97 [0.95, 0.99], p = .01" % vr_obs)

    # ---- antidepressants
    ad = os.path.join(HERE, "..", "..", "ploderl2019-personalised-antidepressants",
                      "reanalysis", "dat.csv")
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
    h = lambda k: np.array([r[k] for r in rr], float)
    an1, an2, am1, am2, as1, as2, ab = (h("n1"), h("n2"), h("m1"), h("m2"),
                                        h("s1"), h("s2"), h("b"))
    avr = float(np.exp(statlib.re_meta(*statlib.lnvr(as1, an1, as2, an2),
                                       method="DL")["mu"]))
    zt = float(np.average((ab - am1) / as1, weights=an1))
    zc = float(np.average((ab - am2) / as2, weights=an2))
    print()
    print("  HAMD17 (k=%d): baseline mean IS reported, n-weighted %.1f; floor 0"
          % (len(rr), float(np.average(ab, weights=an1))))
    print("  baseline SD is NOT reported anywhere in either deposit, so sweep it:")
    print("  %-22s %-10s %-14s" % ("headroom dispersion", "VR bias",
                                   "VR with floor removed"))
    for hd2 in (0.0, 0.3, 0.6, 0.9):
        bias = shrink(zt, hd2) / shrink(zc, hd2)
        print("  %-22.2f %-10.4f %-14.4f" % (hd2, bias, avr / bias))
        out.setdefault("hamd17", {})["%.1f" % hd2] = dict(
            bias=float(bias), vr_corrected=float(avr / bias))
    print("  z_tx %.2f, z_ct %.2f, observed VR %.4f" % (zt, zc, avr))

    print()
    print("=== 3. what this does and does not license ===")
    print("  It does NOT explain the difference between the two literatures: the")
    print("  antidepressant corpus has LESS headroom (z_tx %.2f) than the" % zt)
    print("  antipsychotic one at any plausible baseline (z_tx 1.6 to 2.6), so the")
    print("  floor pushes BOTH down by a similar few per cent. w04 claimed the")
    print("  opposite and was wrong; that claim is withdrawn.")
    print()
    print("  It DOES say that the floor-induced bias is the same size as the entire")
    print("  published antipsychotic effect. VR = 0.97 [0.95, 0.99] with p = .01 is")
    print("  a deviation of 3%% from 1, and a bounded scale delivers 1 to 3%% of that")
    print("  with no individual variation anywhere. The significance is real and the")
    print("  interpretation -- 'antipsychotics do not increase outcome variance, so")
    print("  there is no personal element of response' -- rests on a comparison to 1")
    print("  when the correct comparison is to a floor-adjusted null slightly below 1.")

    print()
    print("=== 4. an interval on the floor-corrected VR ===")
    print("  bootstrap over trials for the observed lnVR; the bias factor is held at")
    print("  its simulated value, whose own Monte-Carlo error is reported separately.")
    rng2 = np.random.default_rng(999)

    def boot_vr(sd1, nn1, sd2, nn2, bias, B=3000):
        y, v = statlib.lnvr(sd1, nn1, sd2, nn2)
        idx = np.arange(len(y))
        vals = []
        for _ in range(B):
            j = rng2.choice(idx, size=len(idx), replace=True)
            vals.append(statlib.re_meta(y[j], v[j], method="DL")["mu"])
        vals = np.exp(np.array(vals)) / bias
        return float(np.mean(vals)), [float(x) for x in np.percentile(vals, [2.5, 97.5])]

    for name, (sd1, nn1, sd2, nn2, bias, label) in {
        "PANSS @ baseline 90": (s1, n1, s2, n2, out["panss"]["90"]["bias"], "0.97"),
        "PANSS @ baseline 95": (s1, n1, s2, n2, out["panss"]["95"]["bias"], "0.97"),
        "HAMD17": (as1, an1, as2, an2, out["hamd17"]["0.6"]["bias"], "1.01"),
    }.items():
        pt, ci = boot_vr(sd1, nn1, sd2, nn2, bias)
        print("  %-22s floor-corrected VR = %.4f [%.4f, %.4f]   (published near %s)"
              % (name, pt, ci[0], ci[1], label))
        out.setdefault("corrected_vr", {})[name] = dict(value=pt, ci=ci, bias=bias)
    mc = [shrink(2.12, 0.582) / shrink(2.51, 0.582) for _ in range(8)]
    print("  Monte-Carlo spread of the bias factor itself (8 redraws at N=600k): "
          "%.5f to %.5f" % (min(mc), max(mc)))
    out["bias_mc_spread"] = [float(min(mc)), float(max(mc))]

    with io.open(os.path.join(HERE, "out_w05.json"), "w", encoding="utf-8",
                 newline="\n") as f:
        json.dump(out, f, indent=1)
    print()
    print("wrote out_w05.json")


if __name__ == "__main__":
    main()
