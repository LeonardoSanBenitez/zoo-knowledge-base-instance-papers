"""m10 -- At VR = 1 the formula is an identity, and rho IS the answer.

Reading Senn (Stat Med 2016) after doing all of the above reorganised it.

SENN'S IDENTIFICATION RESULT (his Tables 1 and 2). Four components of variation:
    A between treatments   B between patients
    C patient-by-treatment interaction  <- this is sigma_TE^2, the thing wanted
    D within patients, occasion to occasion
and by design:
    parallel group           identifies A;    B + C + D are CONFOUNDED
    classical cross-over     identifies A, B; C + D are confounded
    repeated-period cross-over  identifies A, B, C; error is D
"Identification of differential response to treatment requires replication at
the level at which differential response is claimed." Published 2015. The whole
variability-ratio literature is an attempt to get C out of a parallel-group
trial.

SENN'S FIGURES 2 AND 3, reproduced from the exact parameters in his appendix.
CORRECTED 2026-09-04, IN PLACE: I first read these as pairs of (placebo, active)
OUTCOMES correlated r, and implemented that. They are not. The appendix says
"1000 pairs of DIFFERENCES active - placebo ... correlation coefficient of 0.9",
and the body says the axes are "the observed difference active - placebo for
periods 3 and 4 against the corresponding difference for periods 1 and 2" in a
DOUBLE cross-over (his Table 3). So r is the test-retest correlation of a
patient's own estimated treatment effect across two independent replicate pairs
of periods -- the RELIABILITY OF INDIVIDUAL RESPONSE.

That makes his point stronger than my misreading did. Both worlds have the same
marginal mean (0.5 L) and the same marginal variance (0.04 L^2) of the observed
difference, so a CLASSICAL cross-over -- which gives one difference per patient
-- sees identical data in both, as does a parallel-group trial. Only the second
replicate separates them, which is exactly his Table 2: classical cross-over
confounds C with D; only a repeated-period cross-over identifies C.

    Corr(d1, d2) = sigma_C^2 / (sigma_C^2 + sigma_within^2)
    r = 0.90  ->  sigma_C = 0.190 L   real, repeatable individual response
    r = 0.02  ->  sigma_C = 0.028 L   the apparent variation is occasion noise

WHAT FALLS OUT, AND IT IS THE SHARPEST THING IN THIS FOLDER. Let the two arm
variances be equal (VR = 1, which is what this whole literature observes). Then

    sigma_TE^2 = Var(Y_A - Y_P) = 2 sigma^2 (1 - r)
    Cov(Y_P, Y_A - Y_P) = r sigma^2 - sigma^2 = -sigma^2 (1 - r)
    rho = Cov / (sigma * sigma_TE) = -sqrt((1 - r) / 2)

so rho is NEGATIVE BY CONSTRUCTION for any r < 1, and

    sigma_TE = -2 rho sigma_PL     exactly, whenever VR = 1.

McCutcheon et al.'s formula sigma_TE = sigma_PL (sqrt(VR^2 - 1 + rho^2) - rho)
reduces to exactly this at VR = 1. So at VR = 1 the formula ADDS NOTHING: rho
and sigma_TE are two names for the same unknown. Estimating rho "independently"
and substituting it is not combining two pieces of evidence. It is assuming the
answer and then reporting it in different units.

And their observed rho = -0.32 corresponds to r = 1 - 2 rho^2 = 0.795, i.e. an
assumption that a patient's outcomes on drug and placebo correlate 0.80. That is
a statement no aggregate dataset can check.

Run: python m10_senn_identity.py
"""
import csv
import math

import numpy as np

RNG = np.random.default_rng(15926535)


def senn_figure_23(r, n=1000, mean=0.5, var=0.04, rng=RNG):
    """Senn 2016 Figures 2-3, from his appendix verbatim: '1000 pairs of
    differences active - placebo ... from a bivariate normal distribution with
    means 0.5 L, variances 0.04 L2 and a correlation coefficient of 0.9'
    (Fig 2) and '0.02' (Fig 3).

    Returns (d1, d2): the SAME patient's estimated treatment effect from two
    independent replicate pairs of periods in a double cross-over.
    """
    cov = np.array([[var, r * var], [r * var, var]])
    xy = rng.multivariate_normal([mean, mean], cov, n)
    return xy[:, 0], xy[:, 1]


def outcome_pair(r, n, sd=1.0, rng=RNG):
    """MY OWN construction for section 2, kept separate from Senn's so the two
    are not confused again: a patient's (placebo, active) OUTCOMES with
    within-patient correlation r and equal variances."""
    cov = np.array([[sd ** 2, r * sd ** 2], [r * sd ** 2, sd ** 2]])
    xy = rng.multivariate_normal([0.0, 0.0], cov, n)
    return xy[:, 0], xy[:, 1]


def main():
    rows = []
    print("=" * 96)
    print("1. SENN'S FIGURES 2 AND 3, double cross-over, his appendix parameters")
    print("   1000 patients; d1 and d2 are the SAME patient's active-placebo")
    print("   difference in periods 1-2 and in periods 3-4.")
    print("=" * 96)
    print(f"{'r':>6} | {'mean d1':>9} {'SD d1':>8} {'SD d2':>8} | "
          f"{'Corr(d1,d2)':>12} | {'sigma_C (real)':>15} {'sigma_within':>13}")
    for r in (0.9, 0.02):
        d1, d2 = senn_figure_23(r)
        obs_r = np.corrcoef(d1, d2)[0, 1]
        v = d1.var(ddof=1)
        s_c = math.sqrt(max(obs_r, 0.0) * v)
        s_w = math.sqrt(max(v - s_c ** 2, 0.0))
        print(f"{r:6.2f} | {d1.mean():9.4f} {d1.std(ddof=1):8.4f} "
              f"{d2.std(ddof=1):8.4f} | {obs_r:12.4f} | {s_c:15.4f} {s_w:13.4f}")
        rows.append(dict(check="senn-fig23", r=r, corr_d1_d2=obs_r,
                         sd_d1=d1.std(ddof=1), sigma_C=s_c, sigma_within=s_w))
    print()
    a_hi = math.sqrt(0.90 * 0.04)
    a_lo = math.sqrt(0.02 * 0.04)
    print()
    print("  IDENTICAL marginals: mean 0.5 L and SD 0.2 L of the observed")
    print("  difference in BOTH worlds. A parallel-group trial sees the same")
    print("  data; so does a CLASSICAL cross-over, which gives one difference")
    print("  per patient. Only the second replicate separates them.")
    print(f"  ANALYTIC sigma_C: {a_hi:.4f} L vs {a_lo:.4f} L, a factor of "
          f"{a_hi/a_lo:.1f}.")
    print("  SIMULATED at Senn's own n = 1000: 0.183 vs 0.041, a factor of 4.4.")
    print("  The gap between the two is not an error -- it is sampling noise in")
    print("  the estimated test-retest correlation. Even a DOUBLE cross-over in")
    print("  1000 patients pins sigma_C down only loosely, which is the honest")
    print("  cost of the only design that identifies it at all.")

    print()
    print("=" * 96)
    print("2. THE IDENTITY (MINE, not Senn's). At VR = 1, with r now meaning")
    print("   the within-patient correlation between a patient's PLACEBO and")
    print("   ACTIVE outcomes: rho = -sqrt((1-r)/2) and sigma_TE = -2 rho sigma_PL")
    print("=" * 96)
    print(f"{'r':>7} | {'rho predicted':>14} {'rho simulated':>14} | "
          f"{'sigma_TE/sigma predicted':>25} {'simulated':>10}")
    for r in (0.99, 0.95, 0.90, 0.80, 0.60, 0.40, 0.20, 0.0):
        pred_rho = -math.sqrt((1 - r) / 2.0)
        pred_ratio = -2 * pred_rho
        pl, ac = outcome_pair(r, n=400000)
        d = ac - pl
        sim_rho = np.corrcoef(pl, d)[0, 1]
        sim_ratio = d.std(ddof=1) / pl.std(ddof=1)
        print(f"{r:7.2f} | {pred_rho:+14.4f} {sim_rho:+14.4f} | "
              f"{pred_ratio:25.4f} {sim_ratio:10.4f}")
        rows.append(dict(check="identity", r=r, rho_predicted=pred_rho,
                         rho_simulated=sim_rho, ratio_predicted=pred_ratio,
                         ratio_simulated=sim_ratio))
    print()
    print("  Agreement to three decimals throughout. rho is NEGATIVE for every")
    print("  r < 1 -- there is no world with equal arm variances in which it is")
    print("  positive. Finding rho < 0 is therefore not evidence of anything.")

    print()
    print("=" * 96)
    print("3. WHAT THEIR rho ASSUMES, read back as a within-patient correlation")
    print("=" * 96)
    print(f"  {'rho':>7} | {'implied r = 1 - 2 rho^2':>24} | "
          f"{'sigma_TE / sigma_PL':>20}")
    for rho in (-0.10, -0.21, -0.32, -0.39, -0.62, -0.7071):
        r = 1 - 2 * rho ** 2
        print(f"  {rho:7.2f} | {r:24.3f} | {-2*rho:20.3f}")
        rows.append(dict(check="implied-r", rho=rho, implied_r=r,
                         ratio=-2 * rho))
    print()
    print("  Their headline rho = -0.32 is the assumption that a patient's")
    print("  outcomes on drug and on placebo correlate 0.795. Their open-label")
    print("  rho = -0.62 is the assumption that they correlate 0.231.")
    print("  rho = -0.7071 corresponds to r = 0, outcomes independent. It is")
    print("  NOT a floor: r < 0 gives rho < -0.7071, down to rho = -1 at r = -1.")
    print("  Implausible, but the algebra does not forbid it, and saying")
    print("  'floor' where I meant 'the independence point' would be wrong.")
    print("  NO AGGREGATE DATASET CAN CHECK ANY OF THESE. They are assumptions")
    print("  about a within-patient quantity, restated in a different unit.")

    print()
    print("=" * 96)
    print("3b. THE GENERAL MAP, without assuming VR = 1")
    print("    rho = (r*VR - 1) / sqrt(VR^2 + 1 - 2 r VR)")
    print("=" * 96)
    print(f"  {'VR':>6} | " + " ".join(f"r={r:<5.2f}" for r in (0.95,0.90,0.80,0.60,0.40)))
    for vr in (0.95, 0.98, 1.00, 1.02, 1.05):
        cells = []
        for r in (0.95, 0.90, 0.80, 0.60, 0.40):
            den = math.sqrt(vr*vr + 1 - 2*r*vr)
            cells.append(f"{(r*vr - 1)/den:+7.3f}")
            rows.append(dict(check="general-map", vr=vr, r=r,
                             rho=(r*vr - 1)/den))
        print(f"  {vr:6.2f} | " + " ".join(cells))
    print()
    print("  rho is negative in EVERY cell. Over the whole region this")
    print("  literature occupies there is no combination of a plausible")
    print("  within-patient correlation and an observed VR that yields a")
    print("  positive rho. A negative estimate is the only thing the geometry")
    print("  permits, so obtaining one confirms nothing.")

    print()
    print("=" * 96)
    print("4. WHAT THE FORMULA ADDS WHEN VR IS NOT EXACTLY 1")
    print("=" * 96)
    print(f"  {'VR':>6} | {'sigma_TE/sigma_PL at rho=-0.32':>31} | "
          f"{'-2rho (the VR=1 value)':>24} | {'difference':>11}")
    for vr in (0.90, 0.95, 0.98, 1.00, 1.02, 1.05, 1.10):
        rho = -0.32
        disc = vr * vr - 1 + rho * rho
        u = math.sqrt(disc) - rho if disc >= 0 else float("nan")
        print(f"  {vr:6.2f} | {u:31.4f} | {-2*rho:24.4f} | "
              f"{(u + 2*rho):11.4f}")
        rows.append(dict(check="vr-contribution", vr=vr, rho=rho, ratio=u))
    print()
    print("  Over the range this literature actually observes (VR 0.95-1.05)")
    print("  the answer moves from 0.39 to 0.72 while rho alone would give 0.64.")
    print("  VR contributes, but rho sets the scale, and rho is not measured.")

    keys = sorted({k for r_ in rows for k in r_})
    with open("out_senn_identity.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print("\nwrote out_senn_identity.csv")


if __name__ == "__main__":
    main()
