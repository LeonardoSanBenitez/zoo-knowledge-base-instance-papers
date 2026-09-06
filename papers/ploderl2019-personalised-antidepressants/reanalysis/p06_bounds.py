"""p06 -- the deliverable: what the identified quantity D actually bounds.

Uses the estimator p05 verified (pooled-variance weight; bias -0.003 and 96.6%
coverage on a world with D = 0 by construction, against +0.514 and 90.2% for the
naive one), on HAMD17 only, which is the largest single-scale subset (k = 71) and
the scale the 2-point mean effect is quoted on.

Three outputs:

1. sigma_TE as a BAND, not a curve, by propagating the confidence limits of D
   through sigma_TE = -rho sigma_PL + sqrt(rho^2 sigma_PL^2 + D).

2. Plöderl & Hengartner's Figure 1 ("how many benefiters, of what size, are
   compatible with our VR?") restated as a closed-form constraint on the
   identified quantity. For a two-point mixture in which a fraction p receive
   an extra delta points of benefit over the rest,
        sigma_TE^2 = p (1 - p) delta^2
   so at rho = 0 the whole of their figure is the single inequality
        p (1 - p) delta^2  <=  D_upper.
   No simulation grid, and the rho = 0 assumption their figure makes silently
   becomes a visible knob.

3. The same bound at the rho values this literature has actually used, so the
   reader can see how much of the "no room for personalisation" conclusion is
   the data and how much is the untested independence assumption.
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
MEAN_EFFECT = 1.88   # HAMD17 drug-minus-placebo mean symptom reduction, p03


def load(scale=None):
    rows = []
    with io.open(os.path.join(HERE, "dat.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter=";"):
            for k in NUM:
                r[k] = float(r[k]) if r[k] not in ("", "None") else np.nan
            if scale is None or r["scale"] == scale:
                rows.append(r)
    return rows


def d_pooled_w(s1, n1, s2, n2):
    sp2 = ((n1 - 1) * s1 ** 2 + (n2 - 1) * s2 ** 2) / (n1 + n2 - 2)
    return s1 ** 2 - s2 ** 2, 2 * sp2 ** 2 * (1.0 / (n1 - 1) + 1.0 / (n2 - 1))


def sigma_te(D, rho, s_pl):
    """positive root of sigma_TE^2 + 2 rho s_pl sigma_TE - D = 0."""
    disc = (rho * s_pl) ** 2 + D
    if disc < 0:
        # No real root. At rho = 0 this is just D < 0, which is a legal draw
        # from a world with sigma_TE = 0; the constrained estimate is the
        # boundary, not "undefined".
        return 0.0
    v = -rho * s_pl + np.sqrt(disc)
    return v if v >= 0 else 0.0


def main():
    rows = load("HAMD17")
    A = lambda k: np.array([r[k] for r in rows], float)
    s1, n1, s2, n2 = A("all_sd"), A("all_n"), A("placebo_sd"), A("placebo_n")
    d, v = d_pooled_w(s1, n1, s2, n2)
    m = statlib.re_meta(d, v, method="PM")
    s_pl = float(np.median(s2))
    D, Dlo, Dhi = m["mu"], m["ci"][0], m["ci"][1]
    print("HAMD17, k = %d trials, %d drug and %d placebo patients"
          % (m["k"], int(n1.sum()), int(n2.sum())))
    print("median placebo-arm SD of the change score = %.2f HAMD points" % s_pl)
    print("D = sigma_AT^2 - sigma_PL^2 = %+.3f  [%+.3f, %+.3f] HAMD points^2"
          "   (I2 = %.0f%%, tau2 = %.3f)"
          % (D, Dlo, Dhi, 100 * (m["I2"] or 0), m["tau2"]))
    print("mean drug-minus-placebo symptom reduction on this subset = %.2f points"
          % MEAN_EFFECT)
    out = dict(D=D, D_ci=[Dlo, Dhi], k=m["k"], I2=m["I2"], tau2=m["tau2"],
               sd_placebo=s_pl, mean_effect=MEAN_EFFECT)

    print()
    print("=== 1. sigma_TE as a band ===")
    print("    %-7s %-24s %-24s" % ("rho", "sigma_TE (HAMD points)",
                                    "as a multiple of the"))
    print("    %-7s %-24s %-24s" % ("", "point [95% from D]", "1.88-point mean effect"))
    band = {}
    for rho in (0.0, -0.10, -0.21, -0.32, -0.50, -0.62):
        p, lo, hi = (sigma_te(D, rho, s_pl), sigma_te(Dlo, rho, s_pl),
                     sigma_te(Dhi, rho, s_pl))
        band["%.2f" % rho] = dict(point=p, lo=lo, hi=hi)
        print("    %-7.2f %6.2f [%5.2f, %5.2f]        %6.2f [%5.2f, %5.2f]"
              % (rho, p, lo, hi, p / MEAN_EFFECT, lo / MEAN_EFFECT,
                 hi / MEAN_EFFECT))
    out["sigma_TE_band"] = band
    print("    (at rho = 0 the lower limit is 0 whenever D's lower limit is negative;")
    print("     a negative D is a perfectly legal draw and is NOT evidence of anything)")

    print()
    print("=== 2. their Figure 1, closed form, at rho = 0:  p(1-p) delta^2 <= D_hi ===")
    print("    D_hi = %.3f points^2, so delta <= sqrt(%.3f / (p(1-p)))" % (Dhi, Dhi))
    print("    %-12s %-16s %-28s" % ("fraction p", "max extra benefit",
                                     "for reference"))
    print("    %-12s %-16s %-28s" % ("of benefiters", "delta (HAMD pts)", ""))
    fig = {}
    for p in (0.05, 0.10, 0.20, 0.33, 0.50):
        dmax = np.sqrt(Dhi / (p * (1 - p))) if Dhi > 0 else 0.0
        note = ""
        if abs(p - 0.10) < 1e-9:
            note = "their figure says 6 pts at p = 10%"
        if abs(p - 0.50) < 1e-9:
            note = "6 pts = the anchor for 'minimally improved'"
        fig["%.2f" % p] = float(dmax)
        print("    %-12.2f %-16.2f %-28s" % (p, dmax, note))
    out["benefiter_bound_rho0"] = fig

    print()
    print("=== 3. the same bound, with rho as a visible knob ===")
    print("    delta_max for p = 10%% of patients, at each rho this field has used:")
    for rho in (0.0, -0.10, -0.21, -0.32, -0.62):
        st = sigma_te(Dhi, rho, s_pl)
        dmax = st / np.sqrt(0.10 * 0.90)
        print("    rho = %+.2f  ->  sigma_TE <= %5.2f  ->  delta <= %6.2f HAMD points"
              % (rho, st, dmax))
        out.setdefault("delta_max_p10_by_rho", {})["%.2f" % rho] = float(dmax)
    print()
    print("    the HAMD17 range is 0-52 and 6 points is 'minimally improved';")
    print("    a delta of 33 points is not a clinical hypothesis, it is the")
    print("    statement that aggregate data cannot exclude one.")

    with io.open(os.path.join(HERE, "out_p06.json"), "w", encoding="utf-8",
                 newline="\n") as f:
        json.dump(out, f, indent=1)
    print()
    print("wrote out_p06.json")


if __name__ == "__main__":
    main()
