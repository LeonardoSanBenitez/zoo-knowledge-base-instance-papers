from core import *
langs, types = load_langs('languages_exp1.csv')
cc = load_cc('all_complexity_cost_exp1.csv')
mx = [0, 0, 0]; n = 0
for L, items in langs.items():
    if L not in cc: continue
    r = cc[L]; n += 1
    d = (abs(complexity(items) - int(r['complexityoflanguages'])), abs(cost(items) - float(r['costoflanguages'])), abs(rsacost(items) - float(r['RSAcostoflanguages'])))
    mx = [max(a, b) for a, b in zip(mx, d)]
print('languages in cc file', len(cc), 'matched+reproduced', n, 'max abs diff (complexity,cost,rsacost)', mx)
for L in ['ENGLISH', 'RUSSIAN']:
    print(L, complexity(langs[L]), round(cost(langs[L]), 3), round(rsacost(langs[L]), 3), langs[L])
nat = [L for L in cc if cc[L]['type'] == 'natural']; art = [L for L in cc if cc[L]['type'] == 'artificial']
import statistics as st
for name, S in [('natural', nat), ('artificial', art)]:
    print(name, len(S), 'mean overlap', round(st.mean(overlap(langs[L]) for L in S), 3), 'mean coverage', round(st.mean(coverage(langs[L]) for L in S), 3),
          'mean n items', round(st.mean(len(langs[L]) for L in S), 2))
# pre-matching artificial
allart = [L for L in langs if types[L] == 'artificial']
print('pre-match artificial', len(allart), round(st.mean(overlap(langs[L]) for L in allart), 2), round(st.mean(coverage(langs[L]) for L in allart), 2))
from collections import Counter
print('overlap dist natural', sorted(Counter(overlap(langs[L]) for L in nat).items()))
print('overlap dist matched art', sorted(Counter(overlap(langs[L]) for L in art).items()))
print('coverage dist natural', sorted(Counter(coverage(langs[L]) for L in nat).items()))
print('coverage dist matched art', sorted(Counter(coverage(langs[L]) for L in art).items()))
print('n items natural', sorted(Counter(len(langs[L]) for L in nat).items()))
print('n items matched art', sorted(Counter(len(langs[L]) for L in art).items()))
