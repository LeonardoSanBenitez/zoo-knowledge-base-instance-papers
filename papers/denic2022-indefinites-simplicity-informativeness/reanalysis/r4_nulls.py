import json, random, statistics as st, numpy as np, csv, os
from scipy import stats
from core import *
from frontier import *
random.seed(1)
front = json.load(open('out/out_exact_front_literal.json'))
FX = np.array([k for c, k, L in front]); FY = np.array([c for c, k, L in front])
mincost = {c: k for c, k, L in front}
def mincost_at(c):  # best cost achievable at complexity <= c
    return min(k for cc, k, L in front if cc <= c) if c >= 1 else float('inf')
def mincomp_at(k):
    return min(cc for cc, kk, L in front if kk <= k + 1e-12)
p, _, _ = fit_frontier(); gx, gy = grid(p)
langs, types = load_langs('languages_exp1.csv')
cc = load_cc('all_complexity_cost_exp1.csv')
nat = [langs[L] for L in cc if cc[L]['type'] == 'natural']
art = [langs[L] for L in cc if cc[L]['type'] == 'artificial']
def metrics(L):
    c, k = complexity(L), cost(L)
    return dict(c=c, k=k, d_ga=mindist(k, c, gx, gy), d_ex=float(np.min(np.hypot(FX - k, FY - c))),
                dk=k - mincost_at(c), dc=c - mincomp_at(k))
def summ(name, S):
    M = [metrics(L) for L in S]
    out = {key: st.mean(m[key] for m in M) for key in ['c', 'k', 'd_ga', 'd_ex', 'dk', 'dc']}
    out['share_on_exact_front'] = st.mean(1.0 if m['dk'] < 1e-9 else 0.0 for m in M)
    print(f"{name:34s} n={len(S):5d} " + ' '.join(f"{k}={v:.3f}" for k, v in out.items()))
    return M
Mn = summ('natural (40)', nat)
Ma = summ('matched artificial (479)', art)
# structural null 1: overlap-free languages (random partial partitions), n-items and coverage drawn from the natural joint distribution
natshape = [(len(L), coverage(L)) for L in nat]
def rand_partition_lang(n, cov):
    for _ in range(1000):
        S = random.sample(range(6), cov)
        if n > cov: return None
        # random set partition of S into exactly n non-empty blocks
        lab = [random.randrange(n) for _ in S]
        if len(set(lab)) < n: continue
        return [tuple(1 if (j in S and lab[S.index(j)] == b) else 0 for j in range(6)) for b in range(n)]
null1 = []
while len(null1) < 4000:
    n, cv = random.choice(natshape)
    L = rand_partition_lang(n, cv)
    if L: null1.append(L)
M1 = summ('null1: overlap-free, (n,cov) as natural', null1)
# null 2: random items (any of 63) but n-items matched to natural, then keep only those with overlap/coverage equal to some natural lang's (exact joint match)
items = list(COMPLEX)
natjoint = set((len(L), coverage(L), overlap(L)) for L in nat)
null2 = []; tries = 0
while len(null2) < 4000 and tries < 5_000_000:
    tries += 1
    n, cv = random.choice(natshape)
    L = random.sample(items, n)
    if (n, coverage(L), overlap(L)) in natjoint: null2.append(L)
M2 = summ('null2: random items, exact (n,cov,ovl) match', null2)
# null 3: full partitions of all 6 flavours with n blocks as natural (coverage 6)
null3 = []
while len(null3) < 4000:
    n, _ = random.choice(natshape)
    if n > 6: continue
    L = rand_partition_lang(n, 6)
    if L: null3.append(L)
M3 = summ('null3: full partitions, n as natural', null3)
for key in ['d_ga', 'd_ex', 'dk', 'dc']:
    a = [m[key] for m in Mn]
    for nm, M in [('art', Ma), ('null1', M1), ('null2', M2), ('null3', M3)]:
        b = [m[key] for m in M]
        t = stats.ttest_ind(a, b, equal_var=False)
        # percentile of the natural mean in the null distribution of 40-language means
        boots = [st.mean(random.sample(b, 40)) for _ in range(2000)]
        pct = st.mean(1.0 if x <= st.mean(a) else 0.0 for x in boots)
        print(f"{key:5s} nat {st.mean(a):.3f} vs {nm:5s} {st.mean(b):.3f}  t={t.statistic:7.2f}  P(null 40-mean <= nat mean)={pct:.3f}")
json.dump({'nat': Mn, 'art': Ma, 'null1': M1[:500], 'null2': M2[:500], 'null3': M3[:500]}, open('out/out_r4.json', 'w'))
