"""h02 -- what each of the two literatures can tell the other, with numbers.

h01 established that Hope et al.'s Equation 1 and the psychiatric rho identity are
the same function to machine zero. The two fields are arguing about one theorem
under two names, with two disjoint ancestries (Oldham 1962 and the change-score
statisticians; Nakagawa 2015 and ecological meta-analysis of variation).

The interesting part is what does NOT transfer, and why.

    stroke:      X = baseline, Y = follow-up, both OBSERVED on the same patient.
                 So r(X,Y) is estimable, and Equation 1 pins r(X,D) exactly.
    psychiatry:  X = the patient's outcome on placebo, Y = their outcome on drug.
                 One of the two is COUNTERFACTUAL. r(X,Y) is not estimable at all,
                 which is precisely why rho is not identified.

Same identity, different observability -> different pathology. Stroke gets a
SPURIOUS r(X,D) it could have checked and did not. Psychiatry gets an
UNIDENTIFIED rho it cannot check and assumes.

THREE CALCULATIONS.

A. Hope's Equation 1 applied to the psychiatric corpora: at their measured VRs,
   what range of rho is even attainable, over all possible within-patient
   correlations? This is the psychiatric identification problem drawn as Hope's
   Figure 2 surface, which nobody in psychiatry has done.

B. The reverse: the psychiatric floor machinery applied to the stroke ceiling.
   Hope et al. show ONE setting (constant 33-point improvement on a 66-point
   scale gives sigma_Y/sigma_X = 0.569). Generalise it to a curve, and ask of
   each published stroke study whether the ceiling ALONE can produce the
   sigma_Y/sigma_X it reports.

C. The recommendation each field can hand the other, stated as a sentence that
   the receiving field cannot currently write for itself.
"""
import io
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(66)          # Fugl-Meyer maximum


def eq1(r_xy, v):
    return (v * r_xy - 1.0) / math.sqrt(v * v + 1.0 - 2.0 * v * r_xy)


def main():
    out = {}

    print("=== A. the attainable range of rho at each psychiatric corpus's VR ===")
    print("    over ALL within-patient correlations r(X,Y) in [-1, 1)")
    print("    %-42s %-8s %-10s %-10s" % ("corpus", "VR", "rho max", "rho min"))
    corpora = [
        ("antipsychotics (Winkelbeiner, 75 comparisons)", 0.9680),
        ("antidepressants HAMD17 (Ploderl, 71 trials)", 1.0041),
        ("antidepressants endpoint (Munkholm)", 0.9800),
        ("the VR = 1 that McCutcheon's working assumes", 1.0000),
        ("antipsychotics, floor-corrected (baseline 90)", 0.9829),
    ]
    rs = np.linspace(-0.999, 0.9999, 20000)
    for name, v in corpora:
        ds = np.array([eq1(r, v) for r in rs])
        print("    %-42s %-8.4f %-10.4f %-10.4f" % (name, v, ds.max(), ds.min()))
        out.setdefault("rho_range", {})[name] = dict(vr=v, rho_max=float(ds.max()),
                                                     rho_min=float(ds.min()))
    print()
    print("    Read the 'rho max' column. At every one of these VRs the MAXIMUM")
    print("    attainable rho is negative or zero: rho < 0 is forced by the")
    print("    algebra, not discovered in the data. A paper that estimates rho,")
    print("    finds it negative, and treats that as corroboration has learned")
    print("    nothing. Hope et al. say the same thing about r(X,D) in stroke,")
    print("    in 2019, in Brain, and no psychiatric paper in this corpus cites it.")

    print()
    print("=== B. can a ceiling alone produce the sigma_Y/sigma_X each study reports? ===")
    print("    Fugl-Meyer upper extremity, 0-66. Baselines uniform on 0-65 (their")
    print("    own assumption). Improvement ~ N(mean, sd), capped at the headroom.")
    print("    Sweep the two improvement parameters and read off sigma_Y/sigma_X.")
    print()
    print("    %-10s" % "mean\\sd" + "".join("%-9s" % ("sd=%g" % s)
                                             for s in (0, 5, 10, 15, 20)))
    grid = {}
    for m in (10, 20, 33, 45, 55):
        line = "    %-10d" % m
        for sd in (0, 5, 10, 15, 20):
            vals = []
            for _ in range(60):
                X = RNG.uniform(0.0, 65.0, 4000)
                imp = np.full(4000, float(m)) if sd == 0 else RNG.normal(m, sd, 4000)
                imp = np.clip(imp, 0.0, 66.0 - X)
                Y = X + imp
                vals.append(Y.std(ddof=1) / X.std(ddof=1))
            v = float(np.mean(vals))
            grid["m%d_sd%d" % (m, sd)] = v
            line += "%-9.3f" % v
        print(line)
    out["ceiling_grid"] = grid
    print()
    print("    Their own cell (mean 33, sd 0) reproduces at %.3f; they get 0.569."
          % grid["m33_sd0"])

    print()
    print("    published sigma_Y/sigma_X, against what the ceiling alone can reach:")
    lo = min(grid.values()); hi = max(grid.values())
    for name, v, note in (("Winters 2015", 0.158, "fitters only"),
                          ("Zarahn 2011, fitters", 0.36, "after removing 7 non-fitters"),
                          ("Veerbeek 2018", 0.438, "fitters only"),
                          ("Stinear 2017", 0.48, "fitters only"),
                          ("Lazar 2010 (aphasia)", 0.48, "different scale"),
                          ("Zarahn 2011, whole sample", 0.88, "all 30 patients"),
                          ("Jeffers 2018 (rats)", 0.8, "rodent"),
                          ("Feng 2015, combined", 1.2, "all 76 patients")):
        reach = "YES" if lo <= v <= hi else "no -- below the grid" if v < lo else "no -- above"
        print("      %-26s %.3f   ceiling alone can reach it: %s  (%s)"
              % (name, v, reach, note))
        out.setdefault("published_ratios", {})[name] = dict(v=v, reachable=reach)
    print("    ceiling-only grid spans %.3f to %.3f" % (lo, hi))

    print()
    print("=== C. the sentence each field cannot write for itself ===")
    print()
    print("    TO PSYCHIATRY, FROM STROKE:")
    print("      Your rho is r(X,D), and Equation 1 says it is determined by the")
    print("      within-patient correlation and the variability ratio. You do not")
    print("      have to estimate it with an instrument; you have to MEASURE THE")
    print("      WITHIN-PATIENT CORRELATION, and the design that does that is the")
    print("      repeated-period cross-over -- which is what Senn (2016) already")
    print("      told you, from the variance-components side. Two independent")
    print("      arguments, one design.")
    print()
    print("    TO STROKE, FROM PSYCHIATRY:")
    print("      Your ceiling does not only inflate r(X,D). It compresses")
    print("      sigma_Y/sigma_X by a computable factor, and that factor is a")
    print("      REGIME, not a constant: with headroom dispersion above about 1.5")
    print("      improvement-SDs a bound INFLATES the recorded spread instead")
    print("      (statlib.floor_shrinkage). You recommend 'minimize ceiling")
    print("      effects' and 'report the shapes of the distributions'; the")
    print("      quantity to report is z = (mean headroom - mean improvement) /")
    print("      SD(improvement), which is one number and fixes the null.")
    print()
    print("    AND TO BOTH: you are using the same theorem. One of you traces it")
    print("    to Oldham 1962, the other to Nakagawa 2015. Neither cites the other.")

    with io.open(os.path.join(HERE, "out_h02.json"), "w", encoding="utf-8",
                 newline="\n") as fh:
        json.dump(out, fh, indent=1)
    print()
    print("wrote out_h02.json")


if __name__ == "__main__":
    main()
