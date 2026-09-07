"""h04 -- adjudicate Hope et al. (2019) against Bonkhoff et al. (2023), and run
the test neither of them ran.

THE DISPUTE. Hope et al. say r(X, Y-X) is spurious when it exceeds r(X,Y), which
happens when sigma_Y/sigma_X is small, which a ceiling causes. Bonkhoff et al.
reply that (a) coupling of the true value is a notational construct with no effect
on any correlation, (b) the canonical demonstration covers only one corner of the
parameter space, (c) coupling of the MEASUREMENT ERROR is real but small, and
(d) ceiling-induced compression reflects genuine recovery dynamics rather than an
artifact.

WHAT IS ACTUALLY GOING ON, and neither paper says it: **they are using different
null hypotheses.**

    Hope's null:     X and Y independent      ("how predictable are outcomes?")
    Bonkhoff's null: X and Z independent      ("does recovery depend on baseline?")
                     where Z = Y - X

Both simulations are correct about their own setup and they are not the same
setup. Under X independent of Z, r(X,Z) = 0 by construction and no coupling
appears -- which is exactly Bonkhoff's Figure 4 (left), and it settles nothing
about Hope's case. This is the same structure as the lnVR/lnCVR dispute in the
psychiatric variability literature: two statistics, two nulls, nobody states
which was chosen. See instance-papers/areas/treatment-effect-heterogeneity.md.

THREE CALCULATIONS.

A. Bonkhoff's own criterion, applied to the studies. They concede the problem for
   beta1 > 0.5 (equivalently beta2 < 0.5) and argue it is not general because
   beta2 > 0.5 is possible. beta2 = r(X,Y) * sigma_Y/sigma_X. So: where do the
   published analyses actually sit?

B. Reproduce their measurement-error simulations, which are specified precisely
   enough to rerun and which carry their "negligible in practice" conclusion.

C. The test neither side ran. Bonkhoff say the ceiling-induced dependence is real
   and should not be called a confound. Fine -- then the null for "recovery is
   proportional" is not r(X,Z) = 0, it is **whatever the mechanical constraint
   alone produces**. Compute that, and compare it with the published values.
"""
import io
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(2023)
MAXFM = 66.0


def eq1(r_xy, v):
    return (v * r_xy - 1.0) / math.sqrt(v * v + 1.0 - 2.0 * v * r_xy)


def main():
    out = {}

    print("=== A. Bonkhoff's own criterion, applied to the published analyses ===")
    print("    Their equations (2) and (4): beta2 = r(X,Y) * sigma_Y/sigma_X, and")
    print("    beta1 = 1 - beta2. They concede r(X,Y-X) > r(X,Y) exactly when")
    print("    beta2 < 0.5, and argue this is 'only one of many combinations'.")
    print()
    print("    %-30s %-9s %-9s %-9s %-9s %s"
          % ("analysis", "r(X,Y)", "sY/sX", "beta2", "beta1", "in the zone?"))
    studies = [
        ("Zarahn 2011, whole sample", 0.80, 0.88),
        ("Zarahn 2011, FITTERS ONLY", 0.75, 0.36),
        ("Lazar 2010 (root 1)", 0.773, 0.48),
        ("Lazar 2010 (root 2)", 0.019, 0.48),
        ("Jeffers 2018 rats (root 1)", 0.957, 0.80),
        ("Jeffers 2018 rats (root 2)", 0.283, 0.80),
        ("Feng 2015, combined sample", 0.80, 1.20),
    ]
    zone = {}
    for name, rxy, v in studies:
        b2 = rxy * v
        b1 = 1.0 - b2
        inz = "YES -- r(X,Y-X) exceeds r(X,Y)" if b2 < 0.5 else "no"
        print("    %-30s %-9.3f %-9.3f %-9.3f %-9.3f %s"
              % (name, rxy, v, b2, b1, inz))
        zone[name] = dict(rxy=rxy, ratio=v, beta2=b2, in_zone=b2 < 0.5)
    out["bonkhoff_criterion"] = zone
    print()
    print("    Every FITTERS-ONLY analysis is inside the zone Bonkhoff concede.")
    print("    Every WHOLE-SAMPLE analysis is outside it. Their rebuttal shows the")
    print("    problem is not universal; it does not show it is absent where this")
    print("    literature reports its results, and the fitters-only analyses ARE")
    print("    the reported results.")

    print()
    print("=== B. reproduce their measurement-error simulations ===")
    print("    Their spec: X_true uniform 0-100; errors uniform 0-k, independent;")
    print("    three scenarios for Y_true. 200,000 draws each.")
    n = 200000

    def emp(xt, yt, kx, ky):
        x = xt + (RNG.uniform(0, kx, n) if kx else 0.0)
        y = yt + (RNG.uniform(0, ky, n) if ky else 0.0)
        return np.corrcoef(x, y - x)[0, 1]

    print("    %-34s %-10s %-10s %-10s" % ("scenario", "k=0", "kX=50", "kX=100"))
    Xt = RNG.uniform(0, 100, n)
    scen = {}
    # 1. canonical coupling: Y_true independent of X_true, same spread
    Yt1 = RNG.uniform(0, 100, n)
    row = [emp(Xt, Yt1, 0, 0), emp(Xt, Yt1, 50, 0), emp(Xt, Yt1, 100, 0)]
    print("    %-34s %-10.3f %-10.3f %-10.3f" % ("canonical, r_true(X,Y-X)=-0.71", *row))
    print("      their text: -0.71 -> about -0.74 at kX=50 -> -0.82 at kX=100")
    scen["canonical"] = row
    # 2. random recovery: Z independent of X
    Z = RNG.uniform(0, 100, n)
    Yt2 = Xt + Z
    row = [emp(Xt, Yt2, 0, 0), emp(Xt, Yt2, 50, 0), emp(Xt, Yt2, 100, 0)]
    print("    %-34s %-10.3f %-10.3f %-10.3f" % ("random recovery, r_true(X,Y-X)=0", *row))
    print("      their text: 0 -> about -0.2 at kX=50 -> about -0.5 at kX=100")
    scen["random_recovery"] = row
    # 3. true 70% proportional recovery
    Yt3 = Xt + 0.7 * (100.0 - Xt)
    row = [emp(Xt, Yt3, 0, 0), emp(Xt, Yt3, 50, 0), emp(Xt, Yt3, 100, 0)]
    print("    %-34s %-10.3f %-10.3f %-10.3f" % ("true 70% proportional, r_true=-1", *row))
    print("      their text: -1, attenuated by kY, partly restored by kX")
    scen["proportional"] = row
    out["measurement_error"] = scen
    print()
    print("    And the offsetting they report, kX = kY:")
    for k in (25, 50, 100):
        print("      canonical at kX=kY=%3d: r_emp(X,Y-X) = %+.3f  (true -0.707)"
              % (k, emp(Xt, Yt1, k, k)))
        out.setdefault("offsetting", {})[str(k)] = float(emp(Xt, Yt1, k, k))

    print()
    print("=== C. the test neither side ran ===")
    print("    Bonkhoff: the ceiling-induced dependence is REAL, so it is not a")
    print("    confound. Accept that. Then the null for 'recovery is proportional'")
    print("    is not r(X,Z) = 0 -- it is whatever the mechanical constraint ALONE")
    print("    produces. Nobody computes it. Here it is.")
    print()
    print("    World: baselines uniform 0-65 on a 66-point scale; each patient")
    print("    recovers an amount drawn INDEPENDENTLY of baseline, clipped to the")
    print("    headroom. That is Bonkhoff's own null plus their own constraint.")
    print("    %-16s %-12s %-12s %-12s" % ("mean recovery", "sd", "r(X,Y-X)", "sY/sX"))
    nulls = {}
    for mean_r, sd_r in ((15, 8), (20, 8), (23, 10), (33, 0), (33, 10)):
        rs, vs = [], []
        for _ in range(300):
            X = RNG.uniform(0, 65, 500)
            Z = (np.full(500, float(mean_r)) if sd_r == 0
                 else RNG.normal(mean_r, sd_r, 500))
            Z = np.clip(Z, 0.0, MAXFM - X)
            Y = X + Z
            rs.append(np.corrcoef(X, Y - X)[0, 1])
            vs.append(Y.std(ddof=1) / X.std(ddof=1))
        print("    %-16d %-12d %-12.3f %-12.3f"
              % (mean_r, sd_r, float(np.mean(rs)), float(np.mean(vs))))
        nulls["m%d_sd%d" % (mean_r, sd_r)] = dict(rxd=float(np.mean(rs)),
                                                  ratio=float(np.mean(vs)))
    out["mechanical_null"] = nulls
    print()
    print("    THE NULL IS NOT ZERO, and it is not a single number either. At a")
    print("    20-point mean recovery the constraint alone gives r(X,Y-X) = %+.3f."
          % nulls["m20_sd8"]["rxd"])
    print("    Testing published values against 0, as this literature does, tests")
    print("    against a hypothesis the scale already rules out. But the null moves")
    print("    with parameters the studies do not report -- see D.")

    print()
    print("=== D. does anything published EXCEED its own null? ===")
    print("    Null world: recovery drawn INDEPENDENTLY of baseline, clipped to the")
    print("    headroom, with a non-fitter subpopulation, then the non-fitters")
    print("    removed the way the literature removes them. n = 30, as Zarahn.")
    print("    TARGET (Zarahn 2011 via Hope et al.):")
    print("      whole   sY/sX 0.88, r(X,Y-X) -0.49, r(X,Y) 0.80")
    print("      fitters sY/sX 0.36, r(X,Y-X) -0.95, r(X,Y) 0.75")
    print()
    print("    %-40s %-22s %s" % ("null world", "whole  ratio/rxd/rxy",
                                  "fitters  ratio/rxd/rxy"))
    dres = {}
    for mean_r, sd_r, p_non in ((20, 8, 0.30), (23, 10, 0.30), (25, 12, 0.30),
                                (33, 10, 0.30), (20, 8, 0.0)):
        W = [[], [], []]
        F = [[], [], []]
        for _ in range(4000):
            X = RNG.uniform(0, 60, 30)
            head = MAXFM - X
            non = RNG.random(30) < p_non
            Z = np.where(non, np.abs(RNG.normal(0, 2, 30)),
                         RNG.normal(mean_r, sd_r, 30))
            Z = np.clip(Z, 0.0, head)
            Y = X + Z
            if X.std(ddof=1) == 0 or Y.std(ddof=1) == 0:
                continue
            W[0].append(Y.std(ddof=1) / X.std(ddof=1))
            W[1].append(np.corrcoef(X, Y - X)[0, 1])
            W[2].append(np.corrcoef(X, Y)[0, 1])
            b = np.polyfit(head, Y - X, 1)
            res = (Y - X) - np.polyval(b, head)
            keep = np.zeros(30, bool)
            keep[np.argsort(res)[7:]] = True
            Xf, Yf = X[keep], Y[keep]
            if Xf.std(ddof=1) == 0 or Yf.std(ddof=1) == 0:
                continue
            F[0].append(Yf.std(ddof=1) / Xf.std(ddof=1))
            F[1].append(np.corrcoef(Xf, Yf - Xf)[0, 1])
            F[2].append(np.corrcoef(Xf, Yf)[0, 1])
        m = lambda a: float(np.mean(a))
        lab = "recovery N(%d,%d), %d%% non-fitters" % (mean_r, sd_r, 100 * p_non)
        print("    %-40s %5.2f /%6.2f /%5.2f   %5.2f /%6.2f /%5.2f"
              % (lab, m(W[0]), m(W[1]), m(W[2]), m(F[0]), m(F[1]), m(F[2])))
        dres[lab] = dict(whole=[m(W[0]), m(W[1]), m(W[2])],
                         fitters=[m(F[0]), m(F[1]), m(F[2])])
    out["independent_recovery_null"] = dres

    print()
    print("    READ THE FITTERS COLUMN. No independent-recovery null gets near")
    print("    Zarahn's fitters statistics: the best reaches ratio 0.68 and")
    print("    r(X,Y-X) = -0.73 against the observed 0.36 and -0.95. The mixture in")
    print("    h03 that DOES match -- to L1 = 0.084 -- has 70% proportional")
    print("    recovery built into it.")
    print()
    print("    So, against my own expectation when I started: **on the one dataset")
    print("    in this literature with individual data, proportional recovery among")
    print("    fitters is SUPPORTED.** It is not reproducible by the ceiling, not")
    print("    by the selection, and not by the two together.")
    print()
    print("    The whole-sample value is a different story and depends on a")
    print("    parameter nobody reports: with no non-fitters the constraint alone")
    print("    gives -0.51 and the observed -0.49 is indistinguishable from it;")
    print("    with 30% non-fitters the null is -0.20 and -0.49 is well beyond it.")
    print("    The non-fitter fraction is exactly what the analysis chooses.")

    print()
    print("=== VERDICT ON THE DISPUTE ===")
    print("    Bonkhoff et al. are right that coupling of the true value is")
    print("    notational (h01 confirms r(X,Y-X) is an exact function of r(X,Y) and")
    print("    the ratio, which is what 'notational' means here), and right that")
    print("    error coupling is offset when the two error magnitudes match --")
    print("    reproduced above at -0.707 for kX = kY at every level tested.")
    print()
    print("    Hope et al. are right that the reported correlations were never")
    print("    compared against a non-zero null, and that at the ratios this")
    print("    literature reports the statistic is nearly determined.")
    print()
    print("    Neither ran the test that settles it, and it settles it in favour")
    print("    of the rule for the fitters and against the whole-sample claim.")
    print("    One simulation, in every paper in this field: draw recovery")
    print("    independently of baseline, clip it to the headroom, apply your own")
    print("    fitter rule, and report what your statistic returns there.")

    with io.open(os.path.join(HERE, "out_h04.json"), "w", encoding="utf-8",
                 newline="\n") as fh:
        json.dump(out, fh, indent=1)
    print()
    print("wrote out_h04.json")


if __name__ == "__main__":
    main()
