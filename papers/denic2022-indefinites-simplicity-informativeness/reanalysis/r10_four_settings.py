import itertools, json, random, statistics as st, numpy as np
from scipy import stats
import os
from core import *
from mdl import closure, HASP, tup2bm
T3 = load_mindesc(os.path.join(REPO, 'Experiment_1i_and_2i', 'data', 'minimum-desc-indef-with-compl.csv'))
SETTINGS = {'1 (lit, 2op)': (COMPLEX, cost), '1-i (lit, 3op)': (T3, cost), '1-ii (rsa, 2op)': (COMPLEX, rsacost), '1-iii (rsa, 3op)': (T3, rsacost)}
items = list(COMPLEX)
parts = []
for S in range(1, 64):
    sub = [j for j in range(6) if S >> j & 1]
    for p in set_partitions(sub): parts.append([tuple(1 if j in b else 0 for j in range(6)) for b in p])
cands = [list(L) for n in range(1, 4) for L in itertools.combinations(items, n)] + parts + [L + [a] for L in parts for a in items if a not in L]
langs, types = load_langs('languages_exp1.csv'); cc = load_cc('all_complexity_cost_exp1.csv')
nat = [langs[L] for L in cc if cc[L]['type'] == 'natural']
random.seed(5)
natshape = [(len(L), coverage(L)) for L in nat if len(L) <= coverage(L)]  # overlap-free impossible when n > coverage (Russian: 7 items/6 flavours)
null1 = []
while len(null1) < 4000:
    n, cv = random.choice(natshape)
    while True:  # retry with the SAME shape, so (n, coverage) matches the natural joint distribution exactly
        S = random.sample(range(6), cv); lab = [random.randrange(n) for _ in S]
        if len(set(lab)) == n: break
    null1.append([tuple(1 if (j in S and lab[S.index(j)] == b) else 0 for j in range(6)) for b in range(n)])
out = {}
for name, (tab, cf) in SETTINGS.items():
    best = {}
    for L in cands:
        c = sum(tab[tuple(i)] for i in L); k = cf(L)
        if c not in best or k < best[c]: best[c] = k
    front = []; m = float('inf')
    for c in sorted(best):
        if best[c] < m - 1e-12: front.append((c, best[c])); m = best[c]
    FX = np.array([k for c, k in front]); FY = np.array([c for c, k in front])
    def d(L): return float(np.min(np.hypot(FX - cf(L), FY - sum(tab[tuple(i)] for i in L))))
    dn = [d(L) for L in nat]; d1 = [d(L) for L in null1]
    t = stats.ttest_ind(dn, d1, equal_var=False)
    perm = []
    for s in itertools.permutations(range(6)):
        P = [[tuple(it[s[j]] for j in range(6)) for it in L] for L in nat]
        perm.append((st.mean(d(L) for L in P), st.mean(sum(tab[tuple(i)] for i in L) for L in P), st.mean(cf(L) for L in P)))
    r = perm[0]
    res = dict(front=front, d_nat=st.mean(dn), d_null1=st.mean(d1), t=t.statistic, p=t.pvalue,
               perm_better_d=sum(x[0] < r[0] - 1e-12 for x in perm), perm_better_c=sum(x[1] < r[1] - 1e-12 for x in perm), perm_better_cost=sum(x[2] < r[2] - 1e-12 for x in perm),
               on_front=sum(1 for x in dn if x < 1e-9))
    out[name] = res
    print(name, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in res.items() if k != 'front'}, 'front', [(c, round(k, 3)) for c, k in front], flush=True)
json.dump(out, open('out/out_r10.json', 'w'), indent=1)
