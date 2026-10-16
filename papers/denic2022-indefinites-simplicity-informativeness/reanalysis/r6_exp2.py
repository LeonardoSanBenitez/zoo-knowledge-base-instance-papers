import statistics as st, json, numpy as np, random
from scipy import stats
from core import *
random.seed(2)
front = json.load(open('out/out_exact_front_literal.json'))
def mincost_at(c): return min(k for cc, k, L in front if cc <= c)
langs, types = load_langs('languages_exp2.csv'); cc = load_cc('all_complexity_cost_exp2.csv')
G = {'Haspel-ok': [], 'Not Haspel-ok': []}
for L in cc: G[cc[L]['type']].append(langs[L])
for g, S in G.items():
    print(g, len(S), 'mean n', round(st.mean(len(L) for L in S), 2), 'cov', round(st.mean(coverage(L) for L in S), 2), 'ovl', round(st.mean(overlap(L) for L in S), 2),
          'complexity', round(st.mean(complexity(L) for L in S), 2), 'cost', round(st.mean(cost(L) for L in S), 3), 'dk', round(st.mean(cost(L) - mincost_at(complexity(L)) for L in S), 3))
# per-item: complexity by number of flavours, ok vs not items
items = {}
for g, S in G.items():
    for L in S:
        for it in L: items.setdefault(g, []).append(it)
okset = set(it for it in items['Haspel-ok'])
print('distinct Haspel-ok item types (flavour level):', len(okset), 'of 63')
from collections import defaultdict
byk = defaultdict(lambda: [[], []])
for it in COMPLEX:
    byk[sum(it)][0 if it in okset else 1].append(COMPLEX[it])
for k in sorted(byk):
    a, b = byk[k]
    print(f"items with {k} flavours: ok-types n={len(a)} mean c={st.mean(a) if a else float('nan'):.2f} | other n={len(b)} mean c={st.mean(b) if b else float('nan'):.2f}")
# Known-answer-ish decomposition: matched on n items, does cost differ?
for n in range(1, 8):
    a = [cost(L) for L in G['Haspel-ok'] if len(L) == n]; b = [cost(L) for L in G['Not Haspel-ok'] if len(L) == n]
    ca = [complexity(L) for L in G['Haspel-ok'] if len(L) == n]; cb = [complexity(L) for L in G['Not Haspel-ok'] if len(L) == n]
    if len(a) > 5 and len(b) > 5:
        print(f"n={n}: cost ok {st.mean(a):.3f} vs not {st.mean(b):.3f} | complexity ok {st.mean(ca):.2f} vs not {st.mean(cb):.2f} | N {len(a)}/{len(b)}")
