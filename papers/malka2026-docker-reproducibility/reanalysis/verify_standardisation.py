"""Break-test for the claim about Malka et al. Figure 6.

CLAIM UNDER TEST: because `Results.ipynb` cell 55 applies StandardScaler to the
binary rule-violation dummies before `sm.Logit`, `np.exp(coef)` in cell 56 --
labelled "Odds Ratio" and plotted in Figure 6 -- is the odds ratio per STANDARD
DEVIATION of the dummy, not per violation. The per-violation odds ratio is
exp(beta_std / sd), and for a 0/1 dummy sd <= 0.5, so the per-violation odds
ratio is always FURTHER FROM 1 than the printed one.

This script does not assume that. It fits both parameterisations on synthetic
data with the true coefficients KNOWN, and checks four things:
  1. the raw fit recovers the planted coefficients within 4 SE  (the fitter is correct;
     an ABSOLUTE tolerance was tried first and rejected one coefficient that was 3.5 SE
     out on a single draw -- see validate_fitter.py, which settles the fitter separately
     against a closed-form 2x2 odds ratio, against a generic optimiser, and over 40 seeds)
  2. beta_std == beta_raw * sd                            (the claim's mechanism)
  3. z and p are IDENTICAL under both                     (so no sign/significance
                                                           in the paper is affected)
  4. exp(beta_std) is closer to 1 than exp(beta_raw)      (the direction of the error)
and prints the bound OR_raw >= OR_std**2 that lets the correction be stated for
rules whose prevalence the paper does not print.
"""
import numpy as np
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "..", "tools"))
from statlib import logit_fit, standardise

rng = np.random.default_rng(0)
n = 40000
prev = np.array([0.16, 0.43, 0.30, 0.05])
beta_true = np.log(np.array([2.0, 0.6, 1.5, 3.0]))
X = np.column_stack([rng.binomial(1, p, n) for p in prev]).astype(float)
y = rng.binomial(1, 1 / (1 + np.exp(-(-1.2 + X @ beta_true))))

raw = logit_fit(X, y)
Xs, sd = standardise(X)
std = logit_fit(Xs, y)

ok = True
print("n = %d   outcome prevalence = %.3f" % (n, y.mean()))
print()
print("  j  prev     sd     beta_true  beta_raw   beta_std   beta_std/sd   "
      "OR_true  OR_raw  OR_std  OR_std^2")
for j in range(len(prev)):
    br, bs = raw["beta"][j + 1], std["beta"][j + 1]
    print("  %d  %.3f  %.4f   %+.4f   %+.4f   %+.4f    %+.4f      "
          "%.3f   %.3f   %.3f   %.3f"
          % (j, prev[j], sd[j], beta_true[j], br, bs, bs / sd[j],
             np.exp(beta_true[j]), np.exp(br), np.exp(bs),
             np.exp(bs) ** 2))
    if abs(br - beta_true[j]) / raw["se"][j + 1] > 4.0:
        ok = False; print("     FAIL check 1: raw fit did not recover the planted coefficient")
    if abs(bs - br * sd[j]) > 1e-6:
        ok = False; print("     FAIL check 2: beta_std != beta_raw * sd")
    if abs(np.exp(bs) - 1) >= abs(np.exp(br) - 1) + 1e-9:
        ok = False; print("     FAIL check 4: standardised OR is not closer to 1")
    # bound: for a 0/1 dummy sd<=0.5 so |beta_raw| >= 2|beta_std|
    if br > 0 and np.exp(br) < np.exp(bs) ** 2 - 1e-6:
        ok = False; print("     FAIL bound: OR_raw < OR_std^2")
    if br < 0 and np.exp(br) > np.exp(bs) ** 2 + 1e-6:
        ok = False; print("     FAIL bound: OR_raw > OR_std^2")

print()
print("check 3 -- z and p must be IDENTICAL under both parameterisations")
print("   z raw :", np.round(raw["z"][1:], 4))
print("   z std :", np.round(std["z"][1:], 4))
print("   p raw :", np.format_float_scientific(raw["p"][1], 3),
      np.format_float_scientific(raw["p"][2], 3))
print("   p std :", np.format_float_scientific(std["p"][1], 3),
      np.format_float_scientific(std["p"][2], 3))
if np.max(np.abs(raw["z"][1:] - std["z"][1:])) > 1e-6:
    ok = False; print("   FAIL check 3")

print()
print("NEGATIVE CONTROL -- coefficients truly zero must stay non-significant")
Xn = np.column_stack([rng.binomial(1, p, n) for p in prev]).astype(float)
yn = rng.binomial(1, 0.25, n)
nul = logit_fit(Xn, yn)
print("   p:", np.round(nul["p"][1:], 3), " (expect nothing systematically small)")

print()
print("ALL CHECKS PASS" if ok else "SOMETHING FAILED -- do not use this result")
