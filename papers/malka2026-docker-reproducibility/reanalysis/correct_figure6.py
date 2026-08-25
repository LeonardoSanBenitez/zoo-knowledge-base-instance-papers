"""Restate Malka et al. 2026 Figure 6 as odds ratios PER RULE VIOLATION.

WHY. `Results.ipynb` cell 55 fits the rebuildability model as

    X = df_model[feature_cols]          # 0/1 rule-violation dummies
    y = df_model['is_failure']          # 1 = build failed
    X_train, X_test, ... = train_test_split(X, y, test_size=0.3, ...)
    X_train_scaled = StandardScaler().fit_transform(X_train)
    result = sm.Logit(y_train, sm.add_constant(X_train_scaled)).fit()

and cell 56 then reports `np.exp(result.params)` under the column header
"Odds Ratio", which Figure 6 plots against feature names like `rule_DL3008`.

Because the dummies were standardised, exp(beta) is the odds ratio PER STANDARD
DEVIATION of the dummy, not per violation. For a 0/1 variable with prevalence p,
sd = sqrt(p(1-p)) <= 0.5, so

    beta_per_violation = beta_standardised / sd   and   |beta_pv| >= 2|beta_std|

giving the distribution-free bound  OR_pv >= OR_std**2  (for OR>1; <= for OR<1),
which needs no knowledge of p at all.

Two prevalences are printed in the notebook's own stored output, so for CR01 and
CR02 the correction can be computed exactly rather than bounded. Those are
full-sample prevalences (1193 rows) while the scaler saw the 835-row training
split, so a sensitivity band over plausible training prevalences is printed too.

WHAT THIS DOES NOT CHANGE. z and p are invariant under standardisation (proved
by construction in verify_standardisation.py), so every sign and every claim of
significance in the paper stands. Only the magnitudes move.
"""
import numpy as np

N_FULL, N_TRAIN = 1193, 835

# from Results.ipynb cell 56 stored output, verbatim
FIG6 = [
    ("rule_CR02",   0.254431, 2.027169e-03, 0.1574539363484087),
    ("rule_DL3008", 0.385824, 3.114137e-03, None),
    ("rule_DL3007", 0.221063, 3.217790e-03, None),
    ("rule_CR01",  -0.244808, 7.362237e-03, 0.4288107202680067),
    ("rule_DL3016", 0.187882, 1.524448e-02, None),
    ("rule_DL3015", -0.240632, 3.039573e-02, None),
]
PINNING = {"rule_DL3008", "rule_DL3007", "rule_DL3016"}


def sd_binary(p):
    return np.sqrt(p * (1 - p))


print("Malka et al. 2026, Fig. 6 -- rebuildability logit, n_train = %d unique "
      "Dockerfiles" % N_TRAIN)
print("outcome is is_failure (1 = build failed), so OR > 1 for a VIOLATED rule "
      "means\nviolating it raises the odds of failure, i.e. the rule helps.\n")
hdr = ("rule", "OR as printed", "OR per violation", "how obtained", "p", "pin?")
print("%-12s %13s  %-22s %-26s %-9s %s" % hdr)
print("-" * 96)
rows = []
for name, b_std, p_val, prev in FIG6:
    or_std = np.exp(b_std)
    bound = np.exp(2 * b_std)                       # sd = 0.5 worst case
    if prev is None:
        cell = ("<= %.3f" % bound) if b_std < 0 else (">= %.3f" % bound)
        how = "bound, sd<=0.5"
        exact = None
    else:
        exact = np.exp(b_std / sd_binary(prev))
        cell = "%.3f" % exact
        how = "exact, prevalence %.4f" % prev
    rows.append((name, or_std, exact, bound, p_val))
    print("%-12s %13.3f  %-22s %-26s %-9.4f %s"
          % (name, or_std, cell, how, p_val, "PIN" if name in PINNING else ""))

print("\nSENSITIVITY for the two exact rows: the printed prevalence is over all")
print("%d rows, but the scaler saw the %d-row training split. Sampling error on a"
      % (N_FULL, N_TRAIN))
print("proportion at n=%d is about %.3f, so vary prevalence by +/- 0.05:" % (N_TRAIN, 0.5 / np.sqrt(N_TRAIN)))
for name, b_std, p_val, prev in FIG6:
    if prev is None:
        continue
    lo, hi = max(0.01, prev - 0.05), min(0.99, prev + 0.05)
    print("   %-12s prevalence %.3f -> OR %.3f    [%.2f -> %.3f, %.2f -> %.3f]"
          % (name, prev, np.exp(b_std / sd_binary(prev)),
             lo, np.exp(b_std / sd_binary(lo)), hi, np.exp(b_std / sd_binary(hi))))

print("\nCHECK: does the distribution-free bound hold where the exact value is known?")
allok = True
for name, or_std, exact, bound, p_val in rows:
    if exact is None:
        continue
    good = (exact >= bound - 1e-9) if or_std > 1 else (exact <= bound + 1e-9)
    allok &= good
    print("   %-12s exact %.3f vs bound %.3f  -> %s"
          % (name, exact, bound, "consistent" if good else "VIOLATED"))
print("   " + ("bound verified on both computable rows" if allok else "BOUND FAILED"))

print("\nTHE THREE PINNING RULES, restated:")
for name, b_std, p_val, prev in FIG6:
    if name in PINNING:
        print("   %-12s printed OR %.3f  ->  at least %.3f per violation   (p = %.4f)"
              % (name, np.exp(b_std), np.exp(2 * b_std), p_val))
print("   i.e. violating DL3008 (pin apt-get versions) multiplies the odds of a")
print("   failed rebuild by at least 2.16, not 1.47.")
