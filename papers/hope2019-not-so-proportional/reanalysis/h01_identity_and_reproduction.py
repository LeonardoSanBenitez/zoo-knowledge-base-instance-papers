"""h01 -- reproduce Hope et al. (2019), and then show that their Equation 1 is the
same theorem the psychiatric treatment-variability literature has been arguing
about for a decade under a different name.

THEIR EQUATION 1. For baselines X, outcomes Y and change D = Y - X,

    r(X,D) = [sigma_Y r(X,Y) - sigma_X] / sqrt(sigma_Y^2 + sigma_X^2
                                               - 2 sigma_X sigma_Y r(X,Y))

so r(X,D) is a function of r(X,Y) and the variability ratio sigma_Y/sigma_X
alone. Their point: when sigma_Y/sigma_X is small, r(X,D) is driven toward -1
whatever r(X,Y) is, so a strong r(X,D) is not evidence of proportional recovery.
And a bounded scale MAKES sigma_Y/sigma_X small, because a ceiling compresses the
outcome distribution.

WHY I AM READING IT. The psychiatric variability literature
(`instance-papers/areas/treatment-effect-heterogeneity.md`) runs on

    sigma_TE = sigma_PL (sqrt(VR^2 - 1 + rho^2) - rho)

with rho the correlation between a patient's individual treatment effect and
their placebo-arm outcome, and VR = sigma_treated / sigma_control. Write
Y1 = Y0 + delta and the two are the SAME OBJECT: rho IS r(X,D), and VR IS
sigma_Y/sigma_X. Neither literature cites the other. One traces to Oldham (1962)
and the change-score statisticians; the other to Nakagawa (2015) and ecological
meta-analysis of variation.

FIVE CHECKS, in order:
  1. Equation 1 against direct simulation.
  2. Equation 1 against the psychiatric identity, as functions.
  3. The canonical Oldham case, r(X,D) = -0.71.
  4. Their ceiling simulation, which they specify exactly enough to rerun.
  5. Every Equation-1 inversion they perform on the published literature.
"""
import io
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(1962)          # Oldham


def eq1(r_xy, v):
    """Hope et al. Equation 1, with sigma_X = 1 and sigma_Y = v."""
    num = v * r_xy - 1.0
    den = math.sqrt(v * v + 1.0 - 2.0 * v * r_xy)
    return num / den


def psych_rho(r_within, vr):
    """The psychiatric rho, derived independently in
    mccutcheon2022-reappraising-variability#c8 and m13: with u = sigma_TE/sigma_PL,
    r = (1 + rho u)/VR and u = sqrt(VR^2 + 1 - 2 VR r). Solve for rho."""
    u = math.sqrt(vr * vr + 1.0 - 2.0 * vr * r_within)
    if u == 0:
        return float("nan")
    return (vr * r_within - 1.0) / u


def invert_eq1(d, v):
    """r(X,Y) values consistent with an observed r(X,D)=d and ratio v.
    Quadratic: r = [A +/- sqrt(A^2 - A + d^2 v^2)] / v with A = 1 - d^2."""
    A = 1.0 - d * d
    disc = A * A - A + d * d * v * v
    if disc < 0:
        return []
    s = math.sqrt(disc)
    out = []
    for r in ((A + s) / v, (A - s) / v):
        if -1.0 <= r <= 1.0 and abs(eq1(r, v) - d) < 1e-9:
            out.append(r)
    return sorted(set(round(x, 6) for x in out))


def main():
    out = {}

    print("=== 1. Equation 1 against direct simulation ===")
    worst = 0.0
    for r_xy in (-0.5, 0.0, 0.3, 0.75, 0.95):
        for v in (0.158, 0.3, 0.48, 0.8, 1.0, 1.2, 5.0):
            # draw X, Y with the requested correlation and ratio
            n = 400000
            z1 = RNG.normal(size=n)
            z2 = RNG.normal(size=n)
            X = z1
            Y = v * (r_xy * z1 + math.sqrt(max(0.0, 1 - r_xy ** 2)) * z2)
            D = Y - X
            emp = np.corrcoef(X, D)[0, 1]
            worst = max(worst, abs(emp - eq1(r_xy, v)))
    print("    max |simulated r(X,D) - Equation 1| over 35 cells = %.2e" % worst)
    out["eq1_max_dev_vs_simulation"] = worst

    print()
    print("=== 2. Equation 1 IS the psychiatric rho identity ===")
    worst2 = 0.0
    for r_xy in np.linspace(-0.9, 0.99, 40):
        for v in np.linspace(0.2, 3.0, 40):
            worst2 = max(worst2, abs(eq1(r_xy, v) - psych_rho(r_xy, v)))
    print("    max |Hope Eq.1 - psychiatric rho| over 1600 grid points = %.2e" % worst2)
    print("    They are the same function. r(X,D) == rho, and sigma_Y/sigma_X == VR.")
    out["eq1_vs_psych_max_dev"] = worst2

    print()
    print("=== 3. the canonical Oldham case ===")
    print("    X, Y independent with equal variance: their text says r(X,D) ~ -0.71")
    print("    Equation 1 at r(X,Y)=0, v=1: %.4f   (-1/sqrt(2) = %.4f)"
          % (eq1(0.0, 1.0), -1 / math.sqrt(2)))
    out["oldham"] = eq1(0.0, 1.0)

    print()
    print("=== 4. their ceiling simulation, rerun from their own specification ===")
    print("    'baselines uniform on 0-65; outcomes = baseline + 33; outcomes")
    print("     above 66 set to 66' -- 1000 patients, 1000 simulations.")
    print("    Their reported result: before shuffling r(X,Y)=0.89, r(X,D)=-0.90;")
    print("    after shuffling Y, r(X,Y)~0 and r(X,D)=-0.88.")
    pre_xy, pre_xd, post_xy, post_xd, ratios = [], [], [], [], []
    for _ in range(1000):
        X = RNG.uniform(0.0, 65.0, 1000)
        Y = np.minimum(X + 33.0, 66.0)
        D = Y - X
        pre_xy.append(np.corrcoef(X, Y)[0, 1])
        pre_xd.append(np.corrcoef(X, D)[0, 1])
        Ys = RNG.permutation(Y)
        post_xy.append(np.corrcoef(X, Ys)[0, 1])
        post_xd.append(np.corrcoef(X, Ys - X)[0, 1])
        ratios.append(Y.std(ddof=1) / X.std(ddof=1))
    f = lambda a: float(np.mean(a))
    print("    reproduced, before shuffling: r(X,Y) = %+.3f   r(X,D) = %+.3f"
          % (f(pre_xy), f(pre_xd)))
    print("    reproduced, after shuffling:  r(X,Y) = %+.3f   r(X,D) = %+.3f"
          % (f(post_xy), f(post_xd)))
    print("    and the ratio the ceiling produces: sigma_Y/sigma_X = %.3f"
          % f(ratios))
    print("    -> a ceiling alone, with recovery CONSTANT for every patient,")
    print("       manufactures r(X,D) = %+.3f from shuffled data." % f(post_xd))
    out["ceiling_sim"] = dict(pre_xy=f(pre_xy), pre_xd=f(pre_xd),
                              post_xy=f(post_xy), post_xd=f(post_xd),
                              ratio=f(ratios))

    print()
    print("=== 5. every Equation-1 inversion they perform on the literature ===")
    print("    %-26s %-8s %-8s %-28s %s"
          % ("study", "r(X,D)", "sY/sX", "r(X,Y) implied by Eq.1", "their text"))
    cases = [
        ("Lazar 2010 (aphasia)", -0.9, 0.48, "either ~0.78 or zero"),
        ("Jeffers 2018 (rats)", -0.71, 0.8, "either >0.95 or ~0.29"),
        ("Winters 2015", -0.97, 0.158, "at least this strong regardless"),
        ("Veerbeek 2018", -0.88, 0.438, "at least this strong regardless"),
    ]
    inv = {}
    for name, d, v, said in cases:
        sols = invert_eq1(d, v)
        print("    %-26s %-8.2f %-8.3f %-28s %s"
              % (name, d, v, ", ".join("%.3f" % x for x in sols) or "none", said))
        inv[name] = sols
    out["inversions"] = inv

    print()
    print("    Their two 'regardless of r(X,Y)' claims, checked directly:")
    for name, v, floor_claim in (("Winters 2015", 0.158, -0.97),
                                 ("Veerbeek 2018", 0.438, -0.88),
                                 ("Stinear 2017", 0.48, -0.88)):
        rs = np.linspace(0.0, 0.999, 4000)
        ds = [eq1(r, v) for r in rs]
        print("      %-16s v=%.3f: over r(X,Y) in [0,1), r(X,D) never exceeds "
              "%+.4f  (they say %.2f)" % (name, v, max(ds), floor_claim))
        out.setdefault("weakest_rxd", {})[name] = float(max(ds))

    print()
    print("    Feng 2015: r(X,Y)=0.8 and sigma_Y/sigma_X=1.2 imply r(X,D) = %+.3f"
          % eq1(0.8, 1.2))
    print("    (their text: -0.05, i.e. recovery uncorrelated with baseline)")
    out["feng2015_implied_rxd"] = eq1(0.8, 1.2)

    with io.open(os.path.join(HERE, "out_h01.json"), "w", encoding="utf-8",
                 newline="\n") as fh:
        json.dump(out, fh, indent=1)
    print()
    print("wrote out_h01.json")


if __name__ == "__main__":
    main()
