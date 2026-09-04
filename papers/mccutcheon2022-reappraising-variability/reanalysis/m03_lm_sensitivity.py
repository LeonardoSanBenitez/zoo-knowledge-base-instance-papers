"""m03 -- Is the linear-model method an estimator of rho at all?

m02 turned up something I did not go looking for, and which matters more than
the bias I did go looking for. In the null world the LM method returned about
-0.14 at their sample size AND about -0.02 at n = 2000 -- and in the positive
control it returned about -0.02 for EVERY true rho from -0.6 to +0.6.

That is not a biased estimator. That is an estimator with no sensitivity to
the quantity it names.

Before believing it I have to rule out the obvious ways my own simulation
could have rigged it:

  H1  In m02 the individual treatment effect d_i was independent of baseline,
      age and sex. The LM method estimates TE_i from exactly those three
      covariates, so of course it saw nothing. If the true rho ARISES THROUGH
      baseline severity -- which is the mechanism the paper's own verbal story
      appeals to ("greater placebo response leaves less room") -- the method
      should recover it. This is the fair test and it is the one that decides
      whether the method is useless or merely narrow.

  H2  The residual -0.14 at n = 88 could be an artifact of fitting the model
      on the same placebo patients whose correlation is then computed. Test by
      fitting on the drug arm only, or on a held-out sample.

  H3  My implementation might not be theirs. Their spec (supplementary, eq.
      for the LM method) is reproduced verbatim in the docstring of
      method_linear_model in m02 and is followed exactly.

Run: python m03_lm_sensitivity.py
"""
import csv
import math

import numpy as np
from scipy import stats

RNG = np.random.default_rng(4090226)

MU0, SB = 92.0, 14.0
A_PLACEBO = -10.0
M_DRUG = -8.6
SU = 16.0


def se_from_reliability(rel, s_true):
    if rel >= 1.0:
        return 0.0
    return s_true * math.sqrt((1.0 - rel) / rel)


def simulate_trial(n_pl, n_dr, rel, rng, sv=10.0,
                   rho_direct=0.0, beta_base_on_effect=0.0,
                   beta_base_on_placebo=0.0):
    """One trial.

    rho_direct              correlation between the IDIOSYNCRATIC parts of
                            placebo change and treatment effect (invisible to
                            any covariate model, by construction)
    beta_base_on_effect     d_i depends on TRUE baseline severity with this
                            slope -- an effect modification the LM method
                            has the covariates to see
    beta_base_on_placebo    placebo change depends on true baseline severity
    """
    n = n_pl + n_dr
    se = se_from_reliability(rel, SB)
    T0 = rng.normal(MU0, SB, n)
    z = T0 - MU0
    cov = np.array([[SU ** 2, rho_direct * SU * sv],
                    [rho_direct * SU * sv, sv ** 2]])
    uv = rng.multivariate_normal([0.0, 0.0], cov, n)
    C = A_PLACEBO + beta_base_on_placebo * z + uv[:, 0]
    d = M_DRUG + beta_base_on_effect * z + uv[:, 1]
    treat = np.concatenate([np.zeros(n_pl), np.ones(n_dr)])
    age = rng.normal(36.6, 10.8, n)
    sex = rng.integers(0, 2, n).astype(float)
    Y0 = T0 + rng.normal(0, se, n)
    YT = T0 + C + treat * d + rng.normal(0, se, n)
    return dict(Y0=Y0, YT=YT, treat=treat, age=age, sex=sex, C=C, d=d)


def lm_rho(tr, fit_on="all"):
    """Their LM method. fit_on: 'all' (as published) or 'drug' (leave the
    placebo arm out of the fit, to test the in-sample dependence)."""
    Y0, YT, treat, age, sex = (tr["Y0"], tr["YT"], tr["treat"], tr["age"],
                               tr["sex"])
    if fit_on == "all":
        m = np.ones(len(Y0), dtype=bool)
    else:
        m = treat == 1
        # a treat-only design is rank-deficient for the interaction terms, so
        # fit the drug arm plus a disjoint placebo sample instead
        m = m | (np.cumsum(treat == 0) <= 0)
    X = np.column_stack([np.ones(m.sum()), sex[m], age[m], Y0[m],
                         treat[m], treat[m] * sex[m], treat[m] * age[m],
                         treat[m] * Y0[m]])
    beta, *_ = np.linalg.lstsq(X, YT[m], rcond=None)
    TE = beta[4] + beta[5] * sex + beta[6] * age + beta[7] * Y0
    pl = treat == 0
    return stats.spearmanr(TE[pl], YT[pl] - Y0[pl]).statistic


def truth_rho(tr):
    """The correlation the method CLAIMS to estimate, computed on the latent
    truth for the placebo patients: Corr(true placebo change, true effect)."""
    pl = tr["treat"] == 0
    return stats.spearmanr(tr["C"][pl], tr["d"][pl]).statistic


def block(label, reps, rel, **kw):
    got, want = [], []
    for _ in range(reps):
        tr = simulate_trial(88, 384, rel, RNG, **kw)
        got.append(lm_rho(tr))
        want.append(truth_rho(tr))
    got, want = np.array(got), np.array(want)
    print(f"{label:<46} truth {want.mean():+.3f}   LM returns "
          f"{got.mean():+.3f} [{np.percentile(got,2.5):+.3f},"
          f"{np.percentile(got,97.5):+.3f}]")
    return dict(scenario=label, reliability=rel, truth_rho=want.mean(),
                lm_rho=got.mean(), lm_lo=np.percentile(got, 2.5),
                lm_hi=np.percentile(got, 97.5), reps=reps)


def main():
    reps = 400
    rows = []
    print("=" * 100)
    print("H1 -- can the LM method see a rho that runs THROUGH baseline")
    print("      severity, which is the mechanism the paper's own story names?")
    print("      (reliability 1.00: no measurement error anywhere)")
    print("=" * 100)
    rows.append(block("idiosyncratic rho = 0 (m02 null)", reps, 1.00))
    for rd in (-0.3, -0.6):
        rows.append(block(f"idiosyncratic rho = {rd:+.1f}, no covariate route",
                          reps, 1.00, rho_direct=rd))
    for bb in (0.3, 0.6):
        rows.append(block(f"d_i depends on baseline, slope {bb:+.1f}",
                          reps, 1.00, beta_base_on_effect=bb))
    rows.append(block("both: d_i on baseline +0.6, C_i on baseline -0.6",
                      reps, 1.00, beta_base_on_effect=0.6,
                      beta_base_on_placebo=-0.6))
    rows.append(block("both, with measurement error (rel 0.85)",
                      reps, 0.85, beta_base_on_effect=0.6,
                      beta_base_on_placebo=-0.6))

    print()
    print("=" * 100)
    print("H2 -- is the residual negative value an in-sample dependence?")
    print("      sample size sweep, rho_true = 0, reliability 1.00")
    print("=" * 100)
    sweep = []
    for n_pl, n_dr in ((44, 192), (88, 384), (176, 768), (352, 1536),
                       (704, 3072)):
        vals = np.array([lm_rho(simulate_trial(n_pl, n_dr, 1.00, RNG))
                         for _ in range(300)])
        print(f"  n_placebo = {n_pl:5d}, n_drug = {n_dr:5d}   LM rho = "
              f"{vals.mean():+.4f}  (se {vals.std(ddof=1)/math.sqrt(len(vals)):.4f})")
        sweep.append(dict(n_placebo=n_pl, n_drug=n_dr, lm_rho=vals.mean(),
                          se=vals.std(ddof=1) / math.sqrt(len(vals))))
    print()
    print("  A value that shrinks toward 0 as n grows is a finite-sample")
    print("  dependence, not a structural bias. A value that does not shrink")
    print("  is structural. Read the column.")

    with open("out_lm_sensitivity.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    with open("out_lm_nsweep.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(sweep[0].keys()))
        w.writeheader()
        w.writerows(sweep)
    print("\nwrote out_lm_sensitivity.csv, out_lm_nsweep.csv")


if __name__ == "__main__":
    main()
