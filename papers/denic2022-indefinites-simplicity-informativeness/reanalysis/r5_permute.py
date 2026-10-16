import itertools, json, statistics as st, numpy as np
from core import *
front = json.load(open('out/out_exact_front_literal.json'))
FX = np.array([k for c, k, L in front]); FY = np.array([c for c, k, L in front])
def mincost_at(c): return min(k for cc, k, L in front if cc <= c)
def mincomp_at(k): return min(cc for cc, kk, L in front if kk <= k + 1e-12)
langs, types = load_langs('languages_exp1.csv'); cc = load_cc('all_complexity_cost_exp1.csv')
nat = [langs[L] for L in cc if cc[L]['type'] == 'natural']
def perm_lang(L, s): return [tuple(it[s[j]] for j in range(6)) for it in L]
rows = []
for s in itertools.permutations(range(6)):
    P = [perm_lang(L, s) for L in nat]
    C = [complexity(L) for L in P]; K = [cost(L) for L in P]
    d = [float(np.min(np.hypot(FX - k, FY - c))) for c, k in zip(C, K)]
    dk = [k - mincost_at(c) for c, k in zip(C, K)]; dc = [c - mincomp_at(k) for c, k in zip(C, K)]
    rows.append(dict(s=s, c=st.mean(C), k=st.mean(K), d=st.mean(d), dk=st.mean(dk), dc=st.mean(dc)))
ident = rows[0]; assert ident['s'] == (0, 1, 2, 3, 4, 5)
print('identity', {k: round(v, 3) for k, v in ident.items() if k != 's'})
for key in ['c', 'k', 'd', 'dk', 'dc']:
    v = np.array([r[key] for r in rows]); rank = int((v < ident[key] - 1e-12).sum())
    print(f"{key:3s} real {ident[key]:.3f} | perm median {np.median(v):.3f} min {v.min():.3f} | permutations strictly better than real: {rank}/720")
# which permutations beat the real one on d
best = sorted(rows, key=lambda r: r['d'])[:5]
FLn = ['sk', 'su', 'ns', 'npi', 'fci', 'nq']
for r in best: print('best-d perm', [FLn[r['s'][j]] for j in range(6)], round(r['d'], 3), round(r['c'], 2), round(r['k'], 3))
json.dump(rows, open('out/out_r5_perm.json', 'w'))
