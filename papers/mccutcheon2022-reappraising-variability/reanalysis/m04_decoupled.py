"""m04 -- One structure, three disguises; and an estimator that removes it.

m02 and m03 established that all three of McCutcheon et al.'s estimators of rho
return a negative number when the true rho is zero. This script asks WHY, and
answers it the only way a mechanism claim can be honestly answered: by removing
the suspected mechanism and checking the bias goes with it.

THE CLAIMED MECHANISM. In each method a quantity estimated from the PLACEBO ARM
appears on both sides of the correlation, with opposite signs:

  open label   P_i = Y(E)_i - Y(B)_i        T_i = Y(O)_i - Y(E)_i
               Y(E)_i is added to P and subtracted from T. Any occasion-level
               noise in it contributes -Var(e_E) to Cov(P, T).

  linear model P_i = YT_i - Y0_i has Y0 coefficient (beta_base - 1), where
               beta_base is the PLACEBO-ARM slope; TE_i has Y0 coefficient
               gamma_base = (drug slope) - (placebo slope). The placebo-arm
               slope's estimation noise enters both with opposite signs, so
               Cov contains -Var(placebo slope noise). This one needs NO
               measurement error, which is why m02 found it at reliability 1.0.

  study level  P_s = mean placebo change     T_s = mean drug change - P_s
               P_s is added to P and subtracted from T; sampling error in it
               contributes -Var(sampling error of P_s).

THE TEST. Split the placebo information in two independent halves and use one
half on each side. If the mechanism is what I say it is, the bias vanishes and
the estimator becomes unbiased for the true rho. If it does not vanish, my
mechanism is wrong and I should say so.

Run: python m04_decoupled.py
"""
import csv
import math

import numpy as np
from scipy import stats

RNG = np.random.default_rng(77315)

MU0, SB = 92.0, 14.0
A_PLACEBO = -10.0
M_DRUG = -8.6
SU = 16.0


def se_from_reliability(rel, s_true):
    if rel >= 1.0:
        return 0.0
    return s_true * math.sqrt((1.0 - rel) / rel)


# ---------------------------------------------------------------------------
# 1. OPEN-LABEL: coupled vs de-coupled
# ---------------------------------------------------------------------------
def open_label_pair(n, rho_true, sv, rel, rng):
    """Return (coupled rho, de-coupled rho).

    De-coupling: assume the end-of-double-blind visit is measured TWICE
    (two independent ratings, which PANSS trials with two raters do have).
    Use rating 1 to close the placebo period and rating 2 to open the drug
    period. Nothing else changes.
    """
    T0 = rng.normal(MU0, SB, n)
    cov = np.array([[SU ** 2, rho_true * SU * sv],
                    [rho_true * SU * sv, sv ** 2]])
    uv = rng.multivariate_normal([0.0, 0.0], cov, n)
    C, d = A_PLACEBO + uv[:, 0], M_DRUG + uv[:, 1]
    se = se_from_reliability(rel, SB)
    T_E, T_O = T0 + C, T0 + C + d
    Y_B = T0 + rng.normal(0, se, n)
    Y_E1 = T_E + rng.normal(0, se, n)
    Y_E2 = T_E + rng.normal(0, se, n)     # independent second rating
    Y_O = T_O + rng.normal(0, se, n)
    coupled = stats.spearmanr(Y_E1 - Y_B, Y_O - Y_E1).statistic
    decoupled = stats.spearmanr(Y_E1 - Y_B, Y_O - Y_E2).statistic
    return coupled, decoupled


# ---------------------------------------------------------------------------
# 2. LINEAR MODEL: coupled vs de-coupled by sample splitting
# ---------------------------------------------------------------------------
def lm_pair(n_pl, n_dr, rho_true, sv, rel, rng, beta_base_on_effect=0.0,
            beta_base_on_placebo=0.0):
    n = n_pl + n_dr
    se = se_from_reliability(rel, SB)
    T0 = rng.normal(MU0, SB, n)
    z = T0 - MU0
    cov = np.array([[SU ** 2, rho_true * SU * sv],
                    [rho_true * SU * sv, sv ** 2]])
    uv = rng.multivariate_normal([0.0, 0.0], cov, n)
    C = A_PLACEBO + beta_base_on_placebo * z + uv[:, 0]
    d = M_DRUG + beta_base_on_effect * z + uv[:, 1]
    treat = np.concatenate([np.zeros(n_pl), np.ones(n_dr)])
    age = rng.normal(36.6, 10.8, n)
    sex = rng.integers(0, 2, n).astype(float)
    Y0 = T0 + rng.normal(0, se, n)
    YT = T0 + C + treat * d + rng.normal(0, se, n)

    def fit(mask):
        X = np.column_stack([np.ones(mask.sum()), sex[mask], age[mask],
                             Y0[mask], treat[mask], treat[mask] * sex[mask],
                             treat[mask] * age[mask], treat[mask] * Y0[mask]])
        b, *_ = np.linalg.lstsq(X, YT[mask], rcond=None)
        return b

    pl = treat == 0
    all_mask = np.ones(n, dtype=bool)
    b_all = fit(all_mask)
    TE_all = b_all[4] + b_all[5] * sex + b_all[6] * age + b_all[7] * Y0
    coupled = stats.spearmanr(TE_all[pl], YT[pl] - Y0[pl]).statistic

    # de-coupled: split the placebo arm; fit using half A + all drug, then
    # evaluate the correlation only on half B, which the fit never saw.
    idx_pl = np.where(pl)[0]
    rng.shuffle(idx_pl)
    half = len(idx_pl) // 2
    A, B = idx_pl[:half], idx_pl[half:]
    m = np.zeros(n, dtype=bool)
    m[A] = True
    m[treat == 1] = True
    b_split = fit(m)
    TE_split = b_split[4] + b_split[5] * sex + b_split[6] * age + b_split[7] * Y0
    decoupled = stats.spearmanr(TE_split[B], YT[B] - Y0[B]).statistic
    truth = stats.spearmanr(C[pl], d[pl]).statistic
    return coupled, decoupled, truth


# ---------------------------------------------------------------------------
# 3. STUDY LEVEL: coupled vs de-coupled by splitting the placebo arm
# ---------------------------------------------------------------------------
def study_level_pair(n_studies, arm_n, rel, rng, bs_sd_placebo=6.0,
                     bs_sd_effect=3.0, bs_corr=0.0):
    se = se_from_reliability(rel, SB)
    cov = np.array([[bs_sd_placebo ** 2, bs_corr * bs_sd_placebo * bs_sd_effect],
                    [bs_corr * bs_sd_placebo * bs_sd_effect, bs_sd_effect ** 2]])
    shifts = rng.multivariate_normal([0.0, 0.0], cov, n_studies)
    P1, P2, T_c, T_d = [], [], [], []
    for s in range(n_studies):
        noise = math.sqrt(SU ** 2 + 2 * se ** 2)
        chg_pl = shifts[s, 0] + rng.normal(0, noise, arm_n)
        chg_dr = (shifts[s, 0] + shifts[s, 1] + M_DRUG
                  + rng.normal(0, noise, arm_n))
        h = arm_n // 2
        pA, pB = chg_pl[:h].mean(), chg_pl[h:].mean()
        P1.append(chg_pl.mean())
        P2.append(pA)
        T_c.append(chg_dr.mean() - chg_pl.mean())   # coupled: same P both sides
        T_d.append(chg_dr.mean() - pB)              # de-coupled: other half
    coupled = stats.spearmanr(np.array(P1), np.array(T_c)).statistic
    decoupled = stats.spearmanr(np.array(P2), np.array(T_d)).statistic
    return coupled, decoupled


def fmt(a):
    return (f"{a.mean():+.3f} [{np.percentile(a, 2.5):+.3f},"
            f"{np.percentile(a, 97.5):+.3f}]")


def main():
    reps = 500
    rows = []

    print("=" * 100)
    print("1. OPEN-LABEL. Coupled uses one rating of the double-blind endpoint")
    print("   on both sides; de-coupled uses two independent ratings.")
    print("=" * 100)
    print(f"{'rho_true':>9} {'reliab':>7} | {'coupled':>24} | {'de-coupled':>24}")
    for rho_true in (0.0, -0.3):
        for rel in (1.00, 0.90, 0.80):
            res = np.array([open_label_pair(88, rho_true, 10.0, rel, RNG)
                            for _ in range(reps)])
            print(f"{rho_true:9.2f} {rel:7.2f} | {fmt(res[:,0]):>24} | "
                  f"{fmt(res[:,1]):>24}")
            rows.append(dict(method="open-label", rho_true=rho_true,
                             reliability=rel, coupled=res[:, 0].mean(),
                             decoupled=res[:, 1].mean()))

    print()
    print("=" * 100)
    print("2. LINEAR MODEL. Coupled fits on all patients and correlates on the")
    print("   same placebo patients; de-coupled holds half the placebo arm out.")
    print("=" * 100)
    print(f"{'scenario':>34} | {'truth':>7} | {'coupled':>23} | {'de-coupled':>23}")
    for label, kw in (("null", {}),
                      ("idiosyncratic rho -0.3", dict(rho_true=-0.3)),
                      ("via baseline (+0.6 / -0.6)",
                       dict(beta_base_on_effect=0.6, beta_base_on_placebo=-0.6))):
        out = np.array([lm_pair(88, 384, kw.get("rho_true", 0.0), 10.0, 1.00, RNG,
                                beta_base_on_effect=kw.get("beta_base_on_effect", 0.0),
                                beta_base_on_placebo=kw.get("beta_base_on_placebo", 0.0))
                        for _ in range(reps)])
        print(f"{label:>34} | {out[:,2].mean():+7.3f} | {fmt(out[:,0]):>23} | "
              f"{fmt(out[:,1]):>23}")
        rows.append(dict(method="linear-model", scenario=label,
                         truth=out[:, 2].mean(), coupled=out[:, 0].mean(),
                         decoupled=out[:, 1].mean()))

    print()
    print("=" * 100)
    print("3. STUDY LEVEL. Coupled subtracts the same placebo mean it")
    print("   correlates against; de-coupled uses independent halves.")
    print("   True study-level correlation = 0 in every row.")
    print("=" * 100)
    print(f"{'arm n':>7} {'reliab':>7} | {'coupled':>24} | {'de-coupled':>24}")
    for arm_n in (40, 80, 130, 300):
        res = np.array([study_level_pair(66, arm_n, 0.90, RNG)
                        for _ in range(reps // 5)])
        print(f"{arm_n:7d} {0.90:7.2f} | {fmt(res[:,0]):>24} | "
              f"{fmt(res[:,1]):>24}")
        rows.append(dict(method="study-level", arm_n=arm_n,
                         coupled=res[:, 0].mean(), decoupled=res[:, 1].mean()))

    keys = sorted({k for r in rows for k in r})
    with open("out_decoupled.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print("\nwrote out_decoupled.csv")


if __name__ == "__main__":
    main()
