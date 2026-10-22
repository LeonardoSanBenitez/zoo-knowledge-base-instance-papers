"""p04: (A) reproduce the printed eigenvalues behind parallel analysis (F1 29.60, F2 10.71, F3 4.00, F4 2.66,
F5 2.24, F6 1.80, F7 1.74) from the 103 intensity items; (B) is k = 3 the resolution at which factors
replicate, or one of several? Split-half EFA (random halves, 20 splits), k = 2..8, minres + promax
(factor_analyzer), factors matched across halves by the Hungarian algorithm on |Tucker phi|; report
the mean of the worst-matched factor's phi (a solution is only as replicable as its weakest factor).
Same on the final 30 items. Benchmark from gamma2021-mpe92m: the Big Five give phi >= .95 at their k.
Usage: python -I -W ignore p04_factor_stability.py <rds> <out_dir> [splits=20]
"""
import json, os, re, sys, warnings
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_rds import load
import numpy as np
from scipy.optimize import linear_sum_assignment
from factor_analyzer import FactorAnalyzer

warnings.filterwarnings('ignore')
d = load(sys.argv[1]); out = sys.argv[2]
SPLITS = int(sys.argv[3]) if len(sys.argv) > 3 else 20
items = sorted(c for c in d.columns if re.fullmatch(r'UES_\d{3}', c))
X = np.column_stack([d[c].astype(float).to_numpy() for c in items]); X = X[~np.isnan(X).any(1)]
IME30 = ["UES_006", "UES_011", "UES_071", "UES_052", "UES_013", "UES_042", "UES_012", "UES_041", "UES_036", "UES_111",
         "UES_029", "UES_083", "UES_028", "UES_104", "UES_050", "UES_080", "UES_105", "UES_055", "UES_056", "UES_048",
         "UES_044", "UES_075", "UES_078", "UES_063", "UES_072", "UES_065", "UES_067", "UES_043", "UES_062", "UES_095"]
X30 = X[:, [items.index(c) for c in IME30]]
res = {}
ev = np.sort(np.linalg.eigvalsh(np.corrcoef(X, rowvar=False)))[::-1][:7]
res['eigen_pearson_top7'] = [round(float(v), 2) for v in ev]
print('(A) top-7 eigenvalues, Pearson R of 103 items:', res['eigen_pearson_top7'], ' printed: [29.6, 10.71, 4.0, 2.66, 2.24, 1.8, 1.74]')


def tucker(a, b):
    return (a.T @ b) / np.sqrt(np.outer((a ** 2).sum(0), (b ** 2).sum(0)))


def stability(M, ks, label):
    rng = np.random.default_rng(20261023)
    out = {}
    for k in ks:
        worst, mean = [], []
        for _ in range(SPLITS):
            idx = rng.permutation(len(M)); h = len(M) // 2
            L = []
            for part in (idx[:h], idx[h:]):
                fa = FactorAnalyzer(n_factors=k, rotation='promax' if k > 1 else None, method='minres')
                fa.fit(M[part]); L.append(fa.loadings_)
            phi = np.abs(tucker(L[0], L[1]))
            r, c = linear_sum_assignment(-phi)
            m = phi[r, c]
            worst.append(m.min()); mean.append(m.mean())
        out[k] = {'worst_phi_mean': float(np.mean(worst)), 'mean_phi_mean': float(np.mean(mean))}
        print(f'  {label} k={k}: mean matched phi {np.mean(mean):.3f}, weakest factor phi {np.mean(worst):.3f}', flush=True)
    return out


print('(B) split-half replicability, 103 items')
res['split103'] = stability(X, range(2, 9), '103 items')
print('    30 final items')
res['split30'] = stability(X30, range(2, 7), '30 items')
json.dump(res, open(os.path.join(out, 'p04_out.json'), 'w'), indent=1)
