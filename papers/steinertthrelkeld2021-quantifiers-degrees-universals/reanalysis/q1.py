import pandas as pd, numpy as np, os
import statsmodels.formula.api as smf
R = os.environ.get('ST_RESULTS', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results', 'final_length=12_size=10')) + '/tables/'
nat = pd.read_csv(R + 'natural_data.csv', index_col=0); rnd = pd.read_csv(R + 'random_data.csv', index_col=0)
for d in (nat, rnd):
    d['optimality'] = 1 - d['pareto_closeness'] / np.sqrt(2); d['mxc'] = d['monotonicity'] * d['conservativity']
print('n', len(nat), len(rnd))
for name, d, preds in [('natural_gradual', nat, ['naturalness', 'monotonicity', 'conservativity', 'mxc', 'complexity', 'comm_cost']), ('random', rnd, ['monotonicity', 'conservativity', 'mxc', 'complexity', 'comm_cost'])]:
    print(name, {p: round(d['optimality'].corr(d[p]), 4) for p in preds})
    print('  SD', {p: round(d[p].std(), 3) for p in ['monotonicity', 'conservativity', 'complexity', 'comm_cost', 'optimality']}, 'means', {p: round(d[p].mean(), 3) for p in ['monotonicity', 'conservativity']})
# does naturalness act through complexity or cost?
print('natural: corr(naturalness, complexity)', round(nat.naturalness.corr(nat.complexity), 3), 'corr(naturalness, comm_cost)', round(nat.naturalness.corr(nat.comm_cost), 3))
z = nat.copy()
for c in ['optimality', 'naturalness', 'monotonicity', 'conservativity', 'complexity', 'comm_cost']: z[c] = (z[c] - z[c].mean()) / z[c].std()
for f in ['optimality ~ naturalness', 'optimality ~ naturalness + complexity', 'optimality ~ naturalness + monotonicity + conservativity',
          'comm_cost ~ naturalness + complexity', 'complexity ~ naturalness + comm_cost']:
    m = smf.ols(f, z).fit(); print(f'{f:60s}', {k: round(v, 3) for k, v in m.params.items() if k != 'Intercept'}, 'R2', round(m.rsquared, 3))
# random sample: same with degrees
zr = rnd.copy()
for c in ['optimality', 'monotonicity', 'conservativity', 'complexity', 'comm_cost']: zr[c] = (zr[c] - zr[c].mean()) / zr[c].std()
for f in ['optimality ~ monotonicity + conservativity', 'optimality ~ monotonicity + conservativity + complexity', 'comm_cost ~ monotonicity + conservativity + complexity']:
    m = smf.ols(f, zr).fit(); print('random', f'{f:55s}', {k: round(v, 3) for k, v in m.params.items() if k != 'Intercept'}, 'R2', round(m.rsquared, 3))
