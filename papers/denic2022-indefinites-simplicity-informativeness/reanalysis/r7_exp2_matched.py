import statistics as st, random, json
from collections import defaultdict
from scipy import stats
from core import *
random.seed(3)
langs, types = load_langs('languages_exp2.csv'); cc = load_cc('all_complexity_cost_exp2.csv')
ok = [langs[L] for L in cc if cc[L]['type'] == 'Haspel-ok']
okset = set(it for L in ok for it in L)
nonok_by_k = defaultdict(list)
for it in COMPLEX:
    if it not in okset: nonok_by_k[sum(it)].append(it)
ok_by_k = defaultdict(list)
for it in okset: ok_by_k[sum(it)].append(it)
def swap(L, pool):
    out = []
    for it in L:
        k = sum(it); out.append(random.choice(pool[k]) if pool[k] else it)
    return out
res = defaultdict(list)
for L in ok:
    if not any(nonok_by_k[sum(it)] for it in L): continue
    S = swap(L, nonok_by_k); R = swap(L, ok_by_k)  # R: re-draw from ok pool with same flavour counts (sampling-noise control)
    for name, X in [('orig', L), ('swap_nonok', S), ('redraw_ok', R)]:
        res[name + '_cost'].append(cost(X) if literal_inf(X) > 0 else float('nan')); res[name + '_c'].append(complexity(X))
        res[name + '_rsacost'].append(rsacost(X) if rsa_inf(X) > 0 else float('nan'))
        res[name + '_ovl'].append(overlap(X)); res[name + '_cov'].append(coverage(X))
for k, v in res.items():
    v = [x for x in v if x == x]; print(f"{k:22s} {st.mean(v):.3f}")
for m in ['cost', 'rsacost', 'c']:
    a = res['redraw_ok_' + m]; b = res['swap_nonok_' + m]
    pairs = [(x, y) for x, y in zip(a, b) if x == x and y == y]
    print(m, 'paired t redraw_ok vs swap_nonok', stats.ttest_rel([p[0] for p in pairs], [p[1] for p in pairs]))
