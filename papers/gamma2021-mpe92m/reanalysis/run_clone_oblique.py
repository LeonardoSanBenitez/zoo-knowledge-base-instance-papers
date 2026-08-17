"""Clone test, round 2: the confound that could revive H2.

run_clone_test.py generated clones with ORTHOGONAL factors. The real solution
is oblique (quartimin), and correlated factors are intrinsically harder to
separate and match -- so part of the +0.13 gap might be obliquity, not
misspecification. If a clone built with the ESTIMATED factor correlation matrix
Phi closes the gap, the finding dies.

Three worlds, same fitted loadings, same N, same k:
  ORTH   factors ~ N(0, I)          -- round 1
  OBLIQ  factors ~ N(0, Phi_hat)    -- the real solution's own factor correlations
  HETERO factors ~ N(0, Phi_hat) but the loading matrix is PERTURBED per
         subject-group (two halves of the population get slightly different
         loadings). This is the positive control for the mechanism I suspect:
         a MIXTURE of populations with non-identical structure. If HETERO
         reproduces the real profile, that is a candidate explanation, and it
         is testable directly on the real covariates (language, tradition).

Run: python run_clone_oblique.py  ->  results_clone_oblique.json
"""
import json
import numpy as np
import pandas as pd
from factor_analyzer import FactorAnalyzer
import mpelib as M

KS = [5, 12]
N_SPLITS = 20
X, cov = M.load()
N, P = X.shape
rng = np.random.default_rng(31)
out = {'n': int(N), 'ks': KS, 'n_splits': N_SPLITS, 'cmp': {}}


def fit_full(k):
    fa = FactorAnalyzer(n_factors=k, method='principal', rotation='oblimin')
    fa.fit(X.rank(axis=0).values)
    return fa.loadings_, fa.phi_


def gen(L, uniq, Fcov, n):
    k = L.shape[1]
    C = np.linalg.cholesky(Fcov + 1e-9 * np.eye(k))
    F = rng.standard_normal((n, k)) @ C.T
    return F @ L.T + rng.standard_normal((n, L.shape[0])) * uniq


for k in KS:
    L, Phi = fit_full(k)
    comm = np.clip((L ** 2).sum(1), 0, 0.99)
    uniq = np.sqrt(1 - comm)
    offdiag = Phi[~np.eye(k, dtype=bool)]
    print(f"\n=== k={k}  factor correlations: mean|r|={np.abs(offdiag).mean():.3f} "
          f"max|r|={np.abs(offdiag).max():.3f}")

    Xo = pd.DataFrame(gen(L, uniq, np.eye(k), N), columns=X.columns)
    Xb = pd.DataFrame(gen(L, uniq, Phi, N), columns=X.columns)

    # HETERO: two subpopulations whose loadings differ by a modest perturbation
    h = N // 2
    pert = rng.standard_normal(L.shape) * 0.6 * np.abs(L).mean()
    Xh = pd.DataFrame(np.vstack([gen(L + pert, uniq, Phi, h),
                                 gen(L - pert, uniq, Phi, N - h)]),
                      columns=X.columns)

    real = np.median(M.split_half_congruence(X, k, N_SPLITS, seed=500 + k), 0)
    orth = np.median(M.split_half_congruence(Xo, k, N_SPLITS, seed=501 + k), 0)
    obli = np.median(M.split_half_congruence(Xb, k, N_SPLITS, seed=502 + k), 0)
    hete = np.median(M.split_half_congruence(Xh, k, N_SPLITS, seed=503 + k), 0)

    for nm, v in [('REAL  ', real), ('ORTH  ', orth), ('OBLIQ ', obli),
                  ('HETERO', hete)]:
        print(f"  {nm} mean={v.mean():.3f}  >=.85:{int((v>=.85).sum()):2d}  "
              f">=.95:{int((v>=.95).sum()):2d}  | " +
              " ".join(f"{x:.2f}" for x in v))

    out['cmp'][str(k)] = {
        'mean_abs_factor_corr': float(np.abs(offdiag).mean()),
        'real': real.tolist(), 'orth': orth.tolist(),
        'obliq': obli.tolist(), 'hetero': hete.tolist()}

json.dump(out, open('results_clone_oblique.json', 'w'), indent=1)
print("\nwrote results_clone_oblique.json")
