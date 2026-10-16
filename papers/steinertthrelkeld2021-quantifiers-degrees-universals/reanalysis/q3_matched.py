import numpy as np, pandas as pd, random, json, os
from scipy import stats, interpolate
from qcore import *
M = np.array(L('meanings.dill'), dtype=bool); C = np.array(L('expression_complexities.dill'))
mono = np.array(L('monotonicities_max.dill')); cons = np.array(L('conservativities_max.dill'), dtype=float)
natset = sorted(set(L('natural_expression_indices.dill')))
par = pd.read_csv(os.path.join(R, 'tables', 'estimated_pareto.csv'), index_col=0)
PX, PY = par.comm_cost.values, par.complexity.values
f = interpolate.interp1d(PX, PY, bounds_error=False, fill_value=np.nan)
def evaluate(lang):
    cost = 1 - informativeness(M[list(lang)]); comp = C[list(lang)].sum() / 10
    return cost, comp, float(np.min(np.hypot(PX - cost, PY - comp)))
is_nat = np.zeros(len(C), bool); is_nat[natset] = True
mc = np.where(~is_nat & (mono >= 1 - 1e-9) & (cons >= 1 - 1e-9))[0]
mc_by_c = {}
for j in mc: mc_by_c.setdefault(round(C[j], 6), []).append(j)
Qm = [j for j in natset if round(C[j], 6) in mc_by_c]
print('Q quantifiers at complexity levels where MC exists:', len(Qm), 'of', len(natset))
rng = random.Random(7); res = {'Qm': [], 'MCm': []}
for n in range(1, 11):
    for _ in range(500):
        q = rng.sample(Qm, n); m = [rng.choice(mc_by_c[round(C[j], 6)]) for j in q]
        res['Qm'].append((n,) + evaluate(q)); res['MCm'].append((n,) + evaluate(m))
A = {k: np.array(v) for k, v in res.items()}
for k, a in A.items():
    below = np.nanmean(a[:, 2] < f(a[:, 1]) - 1e-12)
    print(f"{k:4s} mean d {a[:,3].mean():.4f} cost {a[:,1].mean():.4f} comp {a[:,2].mean():.4f} share BELOW the estimated frontier {below:.3f}")
d = A['MCm'][:, 3] - A['Qm'][:, 3]
print('paired (same sizes/complexities) MCm - Qm: mean d diff', round(d.mean(), 4), stats.ttest_1samp(d, 0))
print('cost diff', round((A['MCm'][:, 1] - A['Qm'][:, 1]).mean(), 4), 'complexity diff', round((A['MCm'][:, 2] - A['Qm'][:, 2]).mean(), 6))
# how far below can a language get? check the authors' own natural_data: languages below their frontier
tab = pd.read_csv(os.path.join(R, 'tables', 'natural_data.csv'), index_col=0)
print('authors natural_data rows strictly below their own frontier:', int((tab.complexity < f(tab.comm_cost) - 1e-9).sum()), 'of', len(tab))
json.dump({k: v.tolist() for k, v in A.items()}, open('out/out_q3_matched.json', 'w'))
