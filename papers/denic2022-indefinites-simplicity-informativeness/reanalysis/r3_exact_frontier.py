"""Exact (or near-exact) Pareto frontier: exhaustive over all languages with <=3 items (from the 63 items),
all partial partitions (overlap 0, any coverage; 877), and a local search from partitions adding/removing items."""
import itertools, json, sys
from core import *
items = [k for k in COMPLEX]  # 63
assert len(items) == 63
best = {}  # complexity -> (cost, lang)
def upd(L):
    c = complexity(L); k = cost(L) if literal_inf(L) > 0 else float('inf')
    if c not in best or k < best[c][0] - 1e-12: best[c] = (k, [list(i) for i in L])
for n in range(1, 4):
    for L in itertools.combinations(items, n): upd(list(L))
print('exhaustive <=3 done', flush=True)
parts = []
for S in range(1, 64):
    sub = [j for j in range(6) if S >> j & 1]
    for p in set_partitions(sub):
        L = [tuple(1 if j in b else 0 for j in range(6)) for b in p]; parts.append(L); upd(L)
print('partial partitions', len(parts))
# local search: from each partition, add one or two extra items (overlap allowed)
for L in parts:
    for a in items:
        if a in L: continue
        upd(L + [a])
print('partition+1 done', flush=True)
# exhaustive 4 items is C(63,4)=595665 -- do it
for L in itertools.combinations(items, 4): upd(list(L))
print('exhaustive 4 done', flush=True)
# pareto filter
pts = sorted(best.items())
front = []; m = float('inf')
for c, (k, L) in pts:
    if k < m - 1e-12: front.append((c, k, L)); m = k
for c, k, L in front: print(c, round(k, 4), L)
json.dump([[c, k, L] for c, k, L in front], open('out/out_exact_front_literal.json', 'w'))
