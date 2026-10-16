import numpy as np, pandas as pd, os
import statsmodels.formula.api as smf
from qcore import *
def prep(name):
    idx = L(f'{name}/language_indices.dill'); tab = pd.read_csv(os.path.join(R, 'tables', f"{'natural' if name=='natural_gradual' else 'random'}_data.csv"), index_col=0)
    tab['opt'] = 1 - tab.pareto_closeness / np.sqrt(2); tab['n'] = [len(l) for l in idx]; return tab
rnd, nat = prep('random'), prep('natural_gradual')
rng = np.random.default_rng(0)
def boot_within(tab, p, B=2000):
    groups = [g for _, g in tab.groupby('n') if g[p].std() > 0]
    est = np.mean([g.opt.corr(g[p]) for g in groups]); bs = []
    for _ in range(B):
        bs.append(np.mean([ (lambda s: s.opt.corr(s[p]))(g.sample(len(g), replace=True, random_state=int(rng.integers(1e9)))) for g in groups]))
    return est, np.percentile(bs, [2.5, 97.5])
print('per-size r(opt, monotonicity), random sample:', [round(g.opt.corr(g.monotonicity), 3) if g.monotonicity.std() > 0 else None for _, g in rnd.groupby('n')])
print('per-size r(opt, conservativity), random sample:', [round(g.opt.corr(g.conservativity), 3) if g.conservativity.std() > 0 else None for _, g in rnd.groupby('n')])
for tab, nm, ps in [(rnd, 'random', ['monotonicity', 'conservativity']), (nat, 'natural_gradual', ['naturalness', 'monotonicity', 'conservativity'])]:
    for p in ps:
        e, ci = boot_within(tab, p, B=300)
        m = smf.ols(f'opt ~ {p} + C(n)', tab).fit()
        print(f"{nm:16s} {p:15s} pooled r {tab.opt.corr(tab[p]):+.4f} | mean within-size r {e:+.4f} CI [{ci[0]:+.4f},{ci[1]:+.4f}] | OLS slope with size FE {m.params[p]:+.5f} (t {m.tvalues[p]:.1f})")
print('SD of optimality by size (random):', [round(g.opt.std(), 4) for _, g in rnd.groupby('n')])
print('mean optimality by size (random):', [round(g.opt.mean(), 4) for _, g in rnd.groupby('n')])
print('SD of monotonicity by size (random):', [round(g.monotonicity.std(), 3) for _, g in rnd.groupby('n')])
