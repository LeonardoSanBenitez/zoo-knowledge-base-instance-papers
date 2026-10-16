"""Where does the natural advantage cross zero? Net Pareto dominance against nulls matched on an increasing set of
descriptors (size -> +no exact synonyms -> +coverage -> +overlap), with and without the domain's structural universal.
Indefinites (no universal imposed: items any of 63) and modals (rungs with and without IFF)."""
import os, sys, random, statistics as st, numpy as np, json
HERE = os.path.dirname(os.path.abspath(__file__)); PAPERS = os.path.join(HERE, '..', '..')
rng = random.Random(11)
def net(pt, nulls):
    c, i = pt
    if len(nulls) < 20: return None
    dom = st.mean(1.0 if (c <= xc and i >= xi and (c < xc or i > xi)) else 0.0 for xc, xi in nulls)
    sub = st.mean(1.0 if (xc <= c and xi >= i and (xc < c or xi > i)) else 0.0 for xc, xi in nulls)
    return dom - sub
def summarise(vals):
    v = [x for x in vals if x is not None]; b = [st.mean(rng.choices(v, k=len(v))) for _ in range(1000)]
    return round(st.mean(v), 3), [round(float(x), 3) for x in np.percentile(b, [2.5, 97.5])], len(v)
def ladder(nat, pool, cplx, inf, cov, ovl, label, k=200, tries=60000):
    rungs = {'size': lambda X, L: True, '+distinct': lambda X, L: len(set(X)) == len(X),
             '+coverage': lambda X, L: len(set(X)) == len(X) and cov(X) == cov(L),
             '+overlap': lambda X, L: len(set(X)) == len(X) and cov(X) == cov(L) and ovl(X) == ovl(L)}
    res = {}
    for name, ok in rungs.items():
        vals = []
        for L in nat:
            pts = []
            for _ in range(tries):
                X = [rng.choice(pool) for _ in L]
                if ok(X, L): pts.append((cplx(X), inf(X)))
                if len(pts) >= k: break
            vals.append(net((cplx(L), inf(L)), pts))
        res[name] = summarise(vals)
    print(label, json.dumps(res), flush=True); return res
OUT = {}
sys.path.insert(0, os.path.join(PAPERS, 'denic2022-indefinites-simplicity-informativeness', 'reanalysis')); import core as D
langs, types = D.load_langs('languages_exp1.csv'); cc = D.load_cc('all_complexity_cost_exp1.csv')
natI = [langs[L] for L in cc if cc[L]['type'] == 'natural']
OUT['indefinites (pool: all 63 items)'] = ladder(natI, list(D.COMPLEX), D.complexity, D.literal_inf, D.coverage, D.overlap, 'indefinites')
sys.path.insert(0, os.path.join(PAPERS, 'imel2026-modal-typology-efficiency', 'reanalysis')); import mcore as M
natM = [v['lang'] for v in M.load_natural(os.path.join(M.DS, 'natural.yml')).values()]
cov = lambda L: sum(1 for p in range(6) if any(m >> p & 1 for m in L)); ovl = lambda L: sum(max(sum(m >> p & 1 for m in L) - 1, 0) for p in range(6))
inf = lambda L: M.informativeness(L, M.PRIOR)
OUT['modals (pool: all 63 meanings)'] = ladder(natM, list(range(1, 64)), M.complexity, inf, cov, ovl, 'modals-all')
OUT['modals (pool: 21 IFF meanings)'] = ladder(natM, [m for m in range(1, 64) if M.is_iff(m)], M.complexity, inf, cov, ovl, 'modals-IFF')
json.dump(OUT, open(os.path.join(HERE, 'out', 'x5_descriptor_ladder.json'), 'w'), indent=1)
