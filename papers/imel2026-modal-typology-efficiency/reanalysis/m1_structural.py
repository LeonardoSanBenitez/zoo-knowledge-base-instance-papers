import random, statistics as st, numpy as np, json
import os
from scipy import stats
from mcore import *
random.seed(3)
IFF = [m for m in range(1, 64) if is_iff(m)]; NON = [m for m in range(1, 64) if not is_iff(m)]
def run(natfile, label):
    N = load_natural(natfile); nat = [v['lang'] for v in N.values()]
    sizes = [len(L) for L in nat]
    nullI = [[random.choice(IFF) for _ in range(random.choice(sizes))] for _ in range(20000)]
    nullR = [[random.randint(1, 63) for _ in range(random.choice(sizes))] for _ in range(20000)]
    out = {}
    for pname, pr in [('Table5 prior (correct)', PRIOR), ('as-run (reversed) prior', PRIOR_AS_RUN), ('uniform', UNIFORM)]:
        for cname, cf in [('atoms (paper)', complexity), ('nodes-1 (code)', complexity_code)]:
            def m(L): return cf(L), informativeness(L, pr)
            Mn = [m(L) for L in nat]; MI = [m(L) for L in nullI]; MR = [m(L) for L in nullR]
            # paired-by-size comparison: for each natural language, IFF-null languages of the same size
            bys = {}
            for L, v in zip(nullI, MI): bys.setdefault(len(L), []).append(v)
            dc = [c - st.mean(x[0] for x in bys[len(L)]) for L, (c, i) in zip(nat, Mn)]
            di = [i - st.mean(x[1] for x in bys[len(L)]) for L, (c, i) in zip(nat, Mn)]
            # Pareto: share of same-size IFF-null languages that weakly dominate (<= complexity, >= inf, one strict) the natural language
            dom = [st.mean(1.0 if (x[0] <= c and x[1] >= i and (x[0] < c or x[1] > i)) else 0.0 for x in bys[len(L)]) for L, (c, i) in zip(nat, Mn)]
            domd = [st.mean(1.0 if (x[0] >= c and x[1] <= i and (x[0] > c or x[1] < i)) else 0.0 for x in bys[len(L)]) for L, (c, i) in zip(nat, Mn)]
            r_iff_inf = np.corrcoef([st.mean(is_iff(x) for x in L) for L in nullR], [v[1] for v in MR])[0, 1]
            r_iff_c = np.corrcoef([st.mean(is_iff(x) for x in L) for L in nullR], [-v[0] for v in MR])[0, 1]
            key = f'{label} | {pname} | {cname}'
            out[key] = dict(nat_minus_IFFnull_complexity=st.mean(dc), p_c=stats.ttest_1samp(dc, 0).pvalue, nat_minus_IFFnull_inf=st.mean(di), p_i=stats.ttest_1samp(di, 0).pvalue,
                            share_null_dominating_nat=st.mean(dom), share_null_dominated_by_nat=st.mean(domd), r_IFFshare_inf_random=r_iff_inf, r_IFFshare_simplicity_random=r_iff_c)
            print(key, {k: round(v, 4) for k, v in out[key].items()}, flush=True)
    return out
o = run(os.path.join(DS, 'natural.yml'), 'drop_syn natural (28)')
o.update(run(os.path.join(DS, 'natural_revisions.yml'), 'revisions natural (28)'))
json.dump(o, open('out/out_m1.json', 'w'), indent=1)
