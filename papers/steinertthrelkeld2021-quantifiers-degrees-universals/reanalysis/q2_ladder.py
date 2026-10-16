import numpy as np, pandas as pd, random, json, os
from collections import Counter
from qcore import *
M = np.array(L('meanings.dill'), dtype=bool); C = np.array(L('expression_complexities.dill'))
mono = np.array(L('monotonicities_max.dill')); cons = np.array(L('conservativities_max.dill'), dtype=float)
nat_idx = L('natural_expression_indices.dill')
par = pd.read_csv(os.path.join(R, 'tables', 'estimated_pareto.csv'), index_col=0)
PX, PY = par.comm_cost.values, par.complexity.values
def closeness(cost, comp): return float(np.min(np.hypot(PX - cost, PY - comp)))
def evaluate(lang):
    inf = informativeness(M[list(lang)]); comp = C[list(lang)].sum() / 10; cost = 1 - inf
    return cost, comp, closeness(cost, comp)
# verify closeness against the authors' table (row order = language_indices order)
idx = L('natural_gradual/language_indices.dill'); tab = pd.read_csv(os.path.join(R, 'tables', 'natural_data.csv'), index_col=0)
random.seed(0); err = max(abs(evaluate(idx[i])[2] - tab.pareto_closeness.iloc[i]) for i in random.sample(range(len(idx)), 200))
print('max closeness err vs natural_data.csv', err)
natset = set(nat_idx)
is_nat = np.zeros(len(C), bool); is_nat[list(natset)] = True
pools = {
  'R: random non-natural': np.where(~is_nat)[0],
  'M: monotone (deg 1), non-natural': np.where(~is_nat & (mono >= 1 - 1e-9))[0],
  'C: conservative (deg 1), non-natural': np.where(~is_nat & (cons >= 1 - 1e-9))[0],
  'MC: monotone+conservative, non-natural': np.where(~is_nat & (mono >= 1 - 1e-9) & (cons >= 1 - 1e-9))[0],
  'Q: quasi-natural (114)': np.array(sorted(natset)),
}
for k, v in pools.items():
    print(f"{k:42s} n={len(v):6d} mean complexity {C[v].mean():.3f}  mono {mono[v].mean():.3f} cons {cons[v].mean():.3f}")
print('quasi-natural: share mono==1', (mono[list(natset)] >= 1 - 1e-9).mean(), 'share cons==1', (cons[list(natset)] >= 1 - 1e-9).mean())
# complexity-matched MC pool: for each Q quantifier, MC quantifiers of the same complexity
mc = pools['MC: monotone+conservative, non-natural']; mc_by_c = {}
for j in mc: mc_by_c.setdefault(round(C[j], 6), []).append(j)
qc = Counter(round(C[j], 6) for j in natset)
print('Q complexity levels', sorted(qc.items())); print('MC available at those levels', {c: len(mc_by_c.get(c, [])) for c in qc})
rng = random.Random(1); out = {}
SAMPLES = int(os.environ.get('Q_SAMPLES', 300))
for name, pool in list(pools.items()) + [('MCc: MC, complexity-matched to Q', None)]:
    rows = []
    for n in range(1, 11):
        for _ in range(SAMPLES):
            if pool is None:
                q = rng.sample(sorted(natset), n)
                lang = [rng.choice(mc_by_c[round(C[j], 6)]) if mc_by_c.get(round(C[j], 6)) else j for j in q]
            else:
                lang = rng.sample(list(pool), n) if len(pool) >= n else None
            if lang is None: continue
            cost, comp, d = evaluate(lang); rows.append((n, cost, comp, d))
    a = np.array(rows); out[name] = a.tolist()
    print(f"{name:42s} mean d {a[:,3].mean():.4f}  cost {a[:,1].mean():.4f}  comp {a[:,2].mean():.4f}  | d by size n=1,3,5,10: " + ' '.join(f"{a[a[:,0]==n,3].mean():.3f}" for n in (1, 3, 5, 10)), flush=True)
json.dump(out, open('out/out_q2_ladder.json', 'w'))
