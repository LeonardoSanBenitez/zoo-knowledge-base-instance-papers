"""How much structural heterogeneity would be needed to produce the observed
replicability deficit?

The group tests found NO observable grouping (language, sex, five traditions,
Buddhist identification, psychedelic use) whose between-group congruence falls
below its size-matched null. So if the deficit is heterogeneity, it is not
heterogeneity along any variable the questionnaire recorded.

This calibrates the magnitude. Simulate two subpopulations whose loading
matrices differ by +/- c * mean|L|, sweep c, and find the c at which the clone's
split-half profile drops to the real data's. Reporting that c turns "the data
are less replicable than the model implies" into a number a future study can
target: this is the size of latent structural variation that would be required.

Run: python run_perturbation_sweep.py -> results_sweep.json
"""
import json
import numpy as np
import pandas as pd
from factor_analyzer import FactorAnalyzer
import mpelib as M

K = 12
N_SPLITS = 15
CS = [0.0, 0.6, 1.0, 1.5, 2.0, 3.0]

X, cov = M.load()
N, P = X.shape
rng = np.random.default_rng(67)

fa = FactorAnalyzer(n_factors=K, method='principal', rotation='oblimin')
fa.fit(X.rank(axis=0).values)
L, Phi = fa.loadings_, fa.phi_
uniq = np.sqrt(1 - np.clip((L ** 2).sum(1), 0, 0.99))
scale = np.abs(L).mean()
C = np.linalg.cholesky(Phi + 1e-9 * np.eye(K))


def gen(Lx, n):
    F = rng.standard_normal((n, K)) @ C.T
    return F @ Lx.T + rng.standard_normal((n, P)) * uniq


real = np.median(M.split_half_congruence(X, K, N_SPLITS, seed=777), 0)
print(f"k={K}  mean|L|={scale:.4f}")
print(f"REAL          mean phi={real.mean():.3f}  >=.85:{int((real>=.85).sum())}")

out = {'k': K, 'n_splits': N_SPLITS, 'mean_abs_loading': float(scale),
       'real_mean_phi': float(real.mean()), 'real': real.tolist(), 'sweep': {}}

for c in CS:
    pert = rng.standard_normal(L.shape) * c * scale
    h = N // 2
    Xh = pd.DataFrame(np.vstack([gen(L + pert, h), gen(L - pert, N - h)]),
                      columns=X.columns)
    v = np.median(M.split_half_congruence(Xh, K, N_SPLITS, seed=800), 0)
    print(f"c={c:4.1f}  mean phi={v.mean():.3f}  >=.85:{int((v>=.85).sum()):2d}  "
          f"gap vs real={v.mean()-real.mean():+.3f}")
    out['sweep'][str(c)] = {'mean_phi': float(v.mean()),
                            'n_ge_85': int((v >= .85).sum()),
                            'profile': v.tolist()}

json.dump(out, open('results_sweep.json', 'w'), indent=1)
print("\nwrote results_sweep.json")
