"""m02 -- Do the three rho estimators return zero when the truth is zero?

McCutcheon et al. (World Psychiatry 2022) write, defending their three
estimates of rho (the correlation between placebo response and individual
treatment effect):

    "concerns about the three approaches are mitigated by the consistency of
     findings between them. In addition, a negative correlation was a priori
     expected ... and THERE ARE NOT REASONS TO BELIEVE THAT ANY OF THE METHODS
     WOULD PRODUCE A BIAS TOWARDS A NEGATIVE CORRELATION."   (emphasis mine)

That is a falsifiable claim about their estimators, and it can be tested the
only honest way: build worlds in which rho is known by construction --
including rho = 0 -- and see what each estimator returns.

GENERATIVE MODEL (deliberately simple, and true to their own assumptions)

  latent true severity at baseline        T0_i ~ N(mu0, sB^2)
  true placebo change over the period     C_i  = a + u_i
  true individual treatment effect        d_i  = m + v_i
  (u_i, v_i) bivariate normal, Corr(u, v) = RHO_TRUE   <-- the ground truth
  latent true score at DB end, placebo    T1_i = T0_i + C_i
  latent true score at DB end, drug       T1_i = T0_i + C_i + d_i
  EVERY OBSERVATION carries occasion-specific noise  Y = T + e, e ~ N(0, se^2)
  se is set from the reliability of the instrument; nothing else uses it.

What is NOT in the model: no ceiling, no floor, no nonlinearity, no dropout,
no true effect modification by baseline. Each of those would ADD bias. This is
the most favourable world their estimators could be asked to work in.

Run: python m02_coupling.py
"""
import csv
import math

import numpy as np
from scipy import stats

RNG = np.random.default_rng(20260904)

# ---- parameters anchored to the antipsychotic literature -------------------
MU0, SB = 92.0, 14.0     # PANSS total at baseline: mean, SD of TRUE severity
A_PLACEBO = -10.0        # mean placebo change (negative = improvement)
M_DRUG = -8.6            # mean treatment effect, their own pooled estimate
SU = 16.0                # SD of true placebo change between patients
# reliability of one PANSS total administration; ICC in the literature runs
# roughly 0.7-0.9 for total score over short intervals.
RELIABILITIES = [1.00, 0.95, 0.90, 0.85, 0.80, 0.70]


def se_from_reliability(rel, s_true):
    """se such that rel = s_true^2 / (s_true^2 + se^2)."""
    if rel >= 1.0:
        return 0.0
    return s_true * math.sqrt((1.0 - rel) / rel)


def draw_patients(n, rho_true, sv, rng):
    """Return true baseline T0, true placebo change C, true effect d."""
    T0 = rng.normal(MU0, SB, n)
    cov = np.array([[SU ** 2, rho_true * SU * sv],
                    [rho_true * SU * sv, sv ** 2]])
    uv = rng.multivariate_normal([0.0, 0.0], cov, n)
    return T0, A_PLACEBO + uv[:, 0], M_DRUG + uv[:, 1]


# ---------------------------------------------------------------------------
# METHOD A -- "open label". Placebo response = Y(DBend) - Y(base);
# treatment effect = Y(OLend) - Y(DBend). Their key assumption -- that the
# open-label endpoint equals the counterfactual under drug -- is made TRUE
# here by construction, so any bias found is NOT a failure of that assumption.
# ---------------------------------------------------------------------------
def method_open_label(n, rho_true, sv, rel, rng):
    T0, C, d = draw_patients(n, rho_true, sv, rng)
    se = se_from_reliability(rel, SB)
    T_E = T0 + C                 # true score, end of double-blind (on placebo)
    T_O = T_E + d                # true score, end of open-label (on drug)
    Y_B = T0 + rng.normal(0, se, n)
    Y_E = T_E + rng.normal(0, se, n)
    Y_O = T_O + rng.normal(0, se, n)
    return stats.spearmanr(Y_E - Y_B, Y_O - Y_E).statistic


# ---------------------------------------------------------------------------
# METHOD B -- "linear model". Fit, on ALL patients,
#   y_T = a + b_sex sex + b_age age + b_base y0
#           + (g_sex sex + g_age age + g_base y0) treat + delta treat + e
# then TE_i = delta + g_sex sex_i + g_age age_i + g_base y0_i, and correlate
# TE_i with the OBSERVED placebo response among placebo patients only.
# ---------------------------------------------------------------------------
def method_linear_model(n_pl, n_dr, rho_true, sv, rel, rng):
    se = se_from_reliability(rel, SB)
    n = n_pl + n_dr
    T0, C, d = draw_patients(n, rho_true, sv, rng)
    treat = np.concatenate([np.zeros(n_pl), np.ones(n_dr)])
    age = rng.normal(36.6, 10.8, n)
    sex = rng.integers(0, 2, n).astype(float)
    T_end = T0 + C + treat * d
    Y0 = T0 + rng.normal(0, se, n)
    YT = T_end + rng.normal(0, se, n)
    X = np.column_stack([np.ones(n), sex, age, Y0,
                         treat, treat * sex, treat * age, treat * Y0])
    beta, *_ = np.linalg.lstsq(X, YT, rcond=None)
    TE = beta[4] + beta[5] * sex + beta[6] * age + beta[7] * Y0
    pl = treat == 0
    r = stats.spearmanr(TE[pl], YT[pl] - Y0[pl]).statistic
    return r, beta[7]


# ---------------------------------------------------------------------------
# METHOD C -- "study level". Across trials, correlate the placebo arm's mean
# change with (drug arm mean change - placebo arm mean change).
# ---------------------------------------------------------------------------
def method_study_level(n_studies, arm_n, rho_true, sv, rel, rng,
                       bs_sd_placebo=6.0, bs_sd_effect=3.0, bs_corr=0.0):
    """bs_corr is the TRUE study-level correlation between a trial's placebo
    response and its treatment effect; 0 is the null."""
    se = se_from_reliability(rel, SB)
    cov = np.array([[bs_sd_placebo ** 2, bs_corr * bs_sd_placebo * bs_sd_effect],
                    [bs_corr * bs_sd_placebo * bs_sd_effect, bs_sd_effect ** 2]])
    shifts = rng.multivariate_normal([0.0, 0.0], cov, n_studies)
    P, T = [], []
    for s in range(n_studies):
        _, Cp, _ = draw_patients(arm_n, rho_true, sv, rng)
        _, Cd, dd = draw_patients(arm_n, rho_true, sv, rng)
        noise = se * math.sqrt(2.0)
        chg_pl = Cp + shifts[s, 0] + rng.normal(0, noise, arm_n)
        chg_dr = (Cd + shifts[s, 0] + dd + shifts[s, 1]
                  + rng.normal(0, noise, arm_n))
        P.append(chg_pl.mean())
        T.append(chg_dr.mean() - chg_pl.mean())
    return stats.spearmanr(np.array(P), np.array(T)).statistic


def summarise(a):
    return f"{a.mean():+.3f} [{np.percentile(a, 2.5):+.3f},{np.percentile(a, 97.5):+.3f}]"


def main():
    reps = 400
    rows = []
    print("=" * 96)
    print("NULL WORLD: rho_true = 0 exactly. What do their estimators return?")
    print("Their reported values:  open-label -0.62,  LM -0.32,  study-level -0.39")
    print("=" * 96)
    print(f"{'reliab':>7} | {'open-label rho':>25} | {'LM rho':>25} | "
          f"{'study-level rho':>25}")
    for rel in RELIABILITIES:
        ol = np.array([method_open_label(88, 0.0, 10.0, rel, RNG)
                       for _ in range(reps)])
        lm = np.array([method_linear_model(88, 384, 0.0, 10.0, rel, RNG)[0]
                       for _ in range(reps)])
        sl = np.array([method_study_level(66, 130, 0.0, 10.0, rel, RNG)
                       for _ in range(reps // 4)])
        print(f"{rel:7.2f} | {summarise(ol):>25} | {summarise(lm):>25} | "
              f"{summarise(sl):>25}")
        rows.append(dict(reliability=rel, rho_true=0.0, reps=reps,
                         open_label_mean=ol.mean(),
                         open_label_lo=np.percentile(ol, 2.5),
                         open_label_hi=np.percentile(ol, 97.5),
                         lm_mean=lm.mean(),
                         lm_lo=np.percentile(lm, 2.5),
                         lm_hi=np.percentile(lm, 97.5),
                         study_level_mean=sl.mean(),
                         study_level_lo=np.percentile(sl, 2.5),
                         study_level_hi=np.percentile(sl, 97.5)))

    print()
    print("=" * 96)
    print("POSITIVE CONTROL: does the machinery recover a rho that IS there?")
    print("(reliability 1.00, so no measurement error and no artifact)")
    print("=" * 96)
    print(f"{'rho_true':>9} | {'open-label rho':>25} | {'LM rho':>25}")
    pos = []
    for rt in (-0.6, -0.3, 0.0, 0.3, 0.6):
        ol = np.array([method_open_label(2000, rt, 10.0, 1.00, RNG)
                       for _ in range(60)])
        lm = np.array([method_linear_model(2000, 2000, rt, 10.0, 1.00, RNG)[0]
                       for _ in range(60)])
        print(f"{rt:9.2f} | {summarise(ol):>25} | {summarise(lm):>25}")
        pos.append(dict(rho_true=rt, open_label_mean=ol.mean(), lm_mean=lm.mean()))

    with open("out_coupling_null.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    with open("out_coupling_positive_control.csv", "w", newline="",
              encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(pos[0].keys()))
        w.writeheader()
        w.writerows(pos)
    print()
    print("wrote out_coupling_null.csv, out_coupling_positive_control.csv")


if __name__ == "__main__":
    main()
