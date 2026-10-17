"""EXPLORATORY (not in ANALYSIS_PLAN.md, written after the primary analysis): paired abstention ('NO-RES') by condition."""
import json, sys
from scipy.stats import binomtest
R = [json.loads(l) for l in open(sys.argv[1], encoding='utf-8')]
nr = lambda r, k: 'NO-RES' in r[k]['resp'].upper()
for a, b in (('C1', 'C0'), ('C2', 'C0'), ('C2', 'C1')):
    up = sum(nr(r, a) and not nr(r, b) for r in R); dn = sum(nr(r, b) and not nr(r, a) for r in R)
    print(f'EXPLORATORY abstention {a} vs {b}: {a}-only {up}, {b}-only {dn}, exact p {binomtest(up, up + dn, .5).pvalue:.3f}')
c0 = [r for r in R if nr(r, 'C0')]
print('C0 abstained', len(c0), '-> correct under C1', sum(r['C1']['ok'] for r in c0), 'under C2', sum(r['C2']['ok'] for r in c0))
