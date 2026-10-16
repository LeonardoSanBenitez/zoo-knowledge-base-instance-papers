import random, statistics as st
import os
from scipy import stats
from mcore import *
random.seed(5)
IFF = [m for m in range(1, 64) if is_iff(m)]
def cov(L): return sum(1 for p in range(6) if any(m >> p & 1 for m in L))
def ovl(L): return sum(max(sum(m >> p & 1 for m in L) - 1, 0) for p in range(6))
for natfile in [os.path.join(DS, 'natural.yml'), os.path.join(DS, 'natural_revisions.yml')]:
    nat = [v['lang'] for v in load_natural(natfile).values()]
    print(natfile, 'natural: mean size', round(st.mean(map(len, nat)), 2), 'coverage', round(st.mean(map(cov, nat)), 2), 'overlap', round(st.mean(map(ovl, nat)), 2), 'IFF share', round(st.mean(st.mean(is_iff(m) for m in L) for L in nat), 3))
    nulls = {'IFF, distinct': lambda L: len(set(L)) == len(L),
             'IFF, distinct, same coverage': None,
             'IFF, distinct, same coverage & overlap': None}
    for name in nulls:
        di, dc, dom, domd = [], [], [], []
        for L in nat:
            n, cv, ov = len(L), cov(L), ovl(L)
            pool = []
            for _ in range(20000):
                if n > len(IFF): break
                X = random.sample(IFF, n)
                if name != 'IFF, distinct' and cov(X) != cv: continue
                if name.endswith('overlap') and ovl(X) != ov: continue
                pool.append(X)
                if len(pool) >= 300: break
            if len(pool) < 20: continue
            for pr_name, pr in [('correct', PRIOR)]:
                ci, ii = complexity(L), informativeness(L, pr)
                M = [(complexity(X), informativeness(X, pr)) for X in pool]
                dc.append(ci - st.mean(x[0] for x in M)); di.append(ii - st.mean(x[1] for x in M))
                dom.append(st.mean(1.0 if (x[0] <= ci and x[1] >= ii and (x[0] < ci or x[1] > ii)) else 0.0 for x in M))
                domd.append(st.mean(1.0 if (x[0] >= ci and x[1] <= ii and (x[0] > ci or x[1] < ii)) else 0.0 for x in M))
        print(f"  {name:40s} langs matched {len(di):2d} | inf nat-null {st.mean(di):+.4f} (p {stats.ttest_1samp(di,0).pvalue:.1e}) | complexity(atoms) nat-null {st.mean(dc):+.3f} (p {stats.ttest_1samp(dc,0).pvalue:.2f}) | null dominates nat {st.mean(dom):.3f}, nat dominates null {st.mean(domd):.3f}")
