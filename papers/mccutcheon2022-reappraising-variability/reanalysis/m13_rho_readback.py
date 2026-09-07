"""m13 -- put every rho this literature has used on one comparable scale.

THE PROBLEM. `rho` -- the correlation between a patient's individual treatment
effect and the outcome they would have had on placebo -- is unobservable in a
parallel-group trial, and papers pick a value for it without any way to say
whether the value is plausible. A reader has no intuition for "rho = -0.32".

THE FIX. rho is equivalent to a quantity everybody DOES have intuition for: the
within-patient correlation `r` between the same patient's drug outcome and their
placebo outcome. Writing Y1 = Y0 + delta, u = sigma_TE/sigma_PL:

    Cov(Y0, Y1) = sigma_0^2 + rho sigma_0 sigma_TE
    r = (1 + rho u) / VR
    u = -rho + sqrt(rho^2 + VR^2 - 1)         (the non-negative root)

At VR = 1 this collapses to the familiar r = 1 - 2 rho^2, which is what the area
file carries. THAT SPECIAL CASE IS NOT ENOUGH any more: three corpora now have
measured VRs and one of them is 0.968, where the algebra behaves differently --
at VR < 1 there is no non-negative u for rho near zero.

**That last point does NOT license "the data reject rho = 0".** It licenses
"the data reject rho = 0 UNDER THE UNBOUNDED-SCALE DECOMPOSITION", and that
condition fails: a bounded scale produces VR < 1 with sigma_TE = 0 and any rho
(winkelbeiner2019#c4). The exclusion column below is printed with that caveat
attached, because the first draft of this script asserted the stronger version
and it was wrong.

Reading the assumption back as r is the whole point: "rho = -0.32" is silent,
"the same patient's drug and placebo outcomes correlate 0.80" is a claim a
clinician can reject.
"""
import io
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# Every rho this literature has put in print or in a sensitivity analysis.
RHOS = [
    (0.00, "assumed by Munkholm 2020, Ploderl 2019, Winkelbeiner 2019 -- silently"),
    (-0.178, "McCutcheon's own study-level method, recomputed by me on 341 "
             "antidepressant comparisons (m06)"),
    (-0.21, "sensitivity value carried in the area file"),
    (-0.32, "McCutcheon 2022 HEADLINE -- the linear-model estimate, used for 13.5 "
            "PANSS points"),
    (-0.39, "McCutcheon 2022 study-level estimate as reported"),
    (-0.62, "McCutcheon 2022 open-label estimate"),
]

# Each corpus with the VR actually measured on it.
CORPORA = [
    ("antipsychotics, Winkelbeiner 75 comparisons", 0.9680),
    ("antipsychotics, VR assumed exactly 1 (McCutcheon's own working)", 1.0000),
    ("antidepressants HAMD17, Ploderl 71 trials", 1.0041),
    ("antidepressants, Munkholm change scores", 1.0000),
    ("antidepressants, Munkholm endpoint scores", 0.9800),
]


def u_of(rho, vr):
    disc = rho * rho + vr * vr - 1.0
    if disc < 0:
        return None
    u = -rho + math.sqrt(disc)
    return u if u >= 0 else None


def main():
    out = {}
    print("u = sigma_TE / sigma_PL, and r = the within-patient correlation between")
    print("the SAME patient's drug outcome and placebo outcome that the rho implies.")
    print()
    for name, vr in CORPORA:
        print("=" * 78)
        print("%s   (VR = %.4f)" % (name, vr))
        print("  %-8s %-10s %-10s  %s" % ("rho", "u", "r", "source of the rho"))
        rows = {}
        for rho, src in RHOS:
            u = u_of(rho, vr)
            if u is None:
                print("  %-8.3f %-10s %-10s  %s" % (rho, "--", "--", src[:44]))
                print("           %s" % ("EXCLUDED: no non-negative sigma_TE exists "
                                         "at this VR and this rho"))
                rows["%.3f" % rho] = dict(u=None, r=None, excluded=True)
                continue
            r = (1.0 + rho * u) / vr
            print("  %-8.3f %-10.3f %-10.3f  %s" % (rho, u, r, src[:44]))
            rows["%.3f" % rho] = dict(u=u, r=r, excluded=False)
        out[name] = dict(vr=vr, rows=rows)

    print()
    print("=" * 78)
    print("READ THE LAST COLUMN. That is what each paper is assuming about a")
    print("quantity no aggregate dataset can check.")
    print()
    print("  rho = -0.32 (the headline) says a patient's drug and placebo outcomes")
    print("  correlate about 0.80 -- i.e. knowing how someone did on placebo tells")
    print("  you most of how they will do on the drug, while ALSO leaving room for")
    print("  individual effects twice the size of the average effect.")
    print()
    print("  rho = -0.62 (their open-label estimate) says they correlate 0.23 --")
    print("  i.e. the same patient measured twice is almost unrelated to himself.")
    print("  On a scale with a test-retest reliability above 0.8, that is not a")
    print("  statement about treatment; it is a statement that the measurement")
    print("  does not work.")
    print()
    print("  At VR = 0.968, the antipsychotic corpus's measured value, rho values")
    print("  near zero are excluded outright: no non-negative sigma_TE is")
    print("  consistent with them. **BUT THAT EXCLUSION IS CONDITIONAL AND THE")
    print("  CONDITION FAILS.** It assumes the additive decomposition on an")
    print("  UNBOUNDED scale. PANSS stops at 30, the treated arm improves more and")
    print("  so meets that bound more often, and the floor-corrected VR at a")
    print("  plausible baseline is 0.983 [0.964, 1.002] -- which includes 1 and")
    print("  therefore does NOT exclude rho = 0. See")
    print("  winkelbeiner2019-antipsychotic-variability#c4.")
    print()
    print("  So the honest reading of this table is narrower than it first looks,")
    print("  and it is still worth having: whatever rho a paper picks, it is also")
    print("  picking the number in the last column, and that number is checkable")
    print("  against test-retest data the trials already collect. Nobody has")
    print("  checked it. That is the recommendation -- not that any particular rho")
    print("  is refuted, but that rho should never be reported without it.")

    with io.open(os.path.join(HERE, "out_m13_rho_readback.json"), "w",
                 encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
    print()
    print("wrote out_m13_rho_readback.json")


if __name__ == "__main__":
    main()
