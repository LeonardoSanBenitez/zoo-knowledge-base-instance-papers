import numpy as np, pandas as pd, os
from qcore import *
mono = np.array(L('monotonicities_max.dill')); cons = np.array(L('conservativities_max.dill'), dtype=float)
idx = L('random/language_indices.dill')
tab = pd.read_csv(os.path.join(R, 'tables', 'random_data.csv'), index_col=0)
assert len(idx) == len(tab), (len(idx), len(tab))
tab['opt'] = 1 - tab.pareto_closeness / np.sqrt(2)
tab['n'] = [len(l) for l in idx]
tab['share_mono1'] = [np.mean(mono[l] >= 1 - 1e-9) for l in idx]
tab['share_cons1'] = [np.mean(cons[l] >= 1 - 1e-9) for l in idx]
tab['share_mc1'] = [np.mean((mono[l] >= 1 - 1e-9) & (cons[l] >= 1 - 1e-9)) for l in idx]
# check graded degree recomputation matches table
print('graded mono recompute max err', float(np.max(np.abs(np.array([mono[l].mean() for l in idx]) - tab.monotonicity))))
for p in ['monotonicity', 'conservativity', 'share_mono1', 'share_cons1', 'share_mc1']:
    r_all = tab.opt.corr(tab[p])
    r_within = np.mean([g.opt.corr(g[p]) for _, g in tab.groupby('n') if g[p].std() > 0])
    print(f"{p:15s} r(all) {r_all:+.4f}   mean within-size r {r_within:+.4f}   mean {tab[p].mean():.3f}")
print('languages with ANY fully monotone+conservative quantifier:', (tab.share_mc1 > 0).mean())
