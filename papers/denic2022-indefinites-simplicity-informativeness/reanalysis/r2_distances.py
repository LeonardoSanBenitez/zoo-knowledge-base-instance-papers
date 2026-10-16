import csv, os, numpy as np, statistics as st
from scipy import stats
from core import *
from frontier import *
p, c, y = fit_frontier(); print('fit a,b', p, 'n dominant', len(c), 'unique pts', len(set(zip(c, y))))
gx, gy = grid(p)
nd = {r['LANG']: float(r['minimal']) for r in csv.DictReader(open(os.path.join(D, 'natural_distances_pareto.csv')))}
ad = {r['LANG']: float(r['minimal']) for r in csv.DictReader(open(os.path.join(D, 'artificial_distances_pareto.csv')))}
langs, types = load_langs('languages_exp1.csv')
mine = {L: mindist(cost(langs[L]), complexity(langs[L]), gx, gy) for L in list(nd) + list(ad)}
print('max |mine - theirs|', max(abs(mine[L] - v) for L, v in {**nd, **ad}.items()))
print('M nat', st.mean(nd.values()), 'M art', st.mean(ad.values()))
print(stats.ttest_ind(list(nd.values()), list(ad.values()), equal_var=False))
# true dominance check: is any natural language strictly dominated by some evaluated point?
