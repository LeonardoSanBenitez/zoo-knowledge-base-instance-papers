"""Weighting-free cross-domain comparison: net Pareto dominance of natural systems over (a) a random null and
(b) a descriptor-matched structural null, on (complexity, informativeness). Answers the objection that
gap-shares in different geometries are not comparable.

net(L, null) = P(L dominates X) - P(X dominates L), X ~ null matched to L's size (and descriptors for b);
dominance = weakly better on both axes and strictly better on one. Reported: mean over natural systems,
bootstrap 95% CI over systems. Range [-1, 1]; 0 = indistinguishable in the Pareto sense."""
import os, sys, json, random, statistics as st
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); PAPERS = os.path.join(HERE, '..', '..')
rng = random.Random(42)
def net(nat_pts, null_pts_per_lang):
    vals = []
    for (c, i), nulls in zip(nat_pts, null_pts_per_lang):
        if not nulls: continue
        dom = st.mean(1.0 if (c <= xc and i >= xi and (c < xc or i > xi)) else 0.0 for xc, xi in nulls)
        sub = st.mean(1.0 if (xc <= c and xi >= i and (xc < c or xi > i)) else 0.0 for xc, xi in nulls)
        vals.append(dom - sub)
    b = [st.mean(rng.choices(vals, k=len(vals))) for _ in range(2000)]
    return st.mean(vals), np.percentile(b, [2.5, 97.5]).round(3).tolist(), len(vals)
RES = {}
# ---------- indefinites (denic2022) ----------
sys.path.insert(0, os.path.join(PAPERS, 'denic2022-indefinites-simplicity-informativeness', 'reanalysis'))
import core as D
langs, types = D.load_langs('languages_exp1.csv'); cc = D.load_cc('all_complexity_cost_exp1.csv')
nat = [langs[L] for L in cc if cc[L]['type'] == 'natural']
items = list(D.COMPLEX)
def pt(L): return (D.complexity(L), D.literal_inf(L))
def rand_null(L, k=300): return [pt(rng.sample(items, len(L))) for _ in range(k)]
def struct_null(L, k=300):
    n, cv = len(L), D.coverage(L)
    if n > cv: return []
    out = []
    while len(out) < k:
        S = rng.sample(range(6), cv); lab = [rng.randrange(n) for _ in S]
        if len(set(lab)) == n: out.append(pt([tuple(1 if (j in S and lab[S.index(j)] == b) else 0 for j in range(6)) for b in range(n)]))
    return out
NP = [pt(L) for L in nat]
RES['indefinites'] = {'random items, same size': net(NP, [rand_null(L) for L in nat]),
                      'overlap-free, same size & coverage': net(NP, [struct_null(L) for L in nat])}
print('indefinites', RES['indefinites'], flush=True)
# ---------- modals (imel2026) ----------
sys.path.insert(0, os.path.join(PAPERS, 'imel2026-modal-typology-efficiency', 'reanalysis'))
import mcore as M
natm = [v['lang'] for v in M.load_natural(os.path.join(M.DS, 'natural.yml')).values()]
IFF = [m for m in range(1, 64) if M.is_iff(m)]
def cov(L): return sum(1 for p in range(6) if any(m >> p & 1 for m in L))
def ovl(L): return sum(max(sum(m >> p & 1 for m in L) - 1, 0) for p in range(6))
def ptm(L): return (M.complexity(L), M.informativeness(L, M.PRIOR))
def m_rand(L, k=300): return [ptm([rng.randint(1, 63) for _ in L]) for _ in range(k)]
def m_struct(L, k=300, tries=40000):
    out = []
    for _ in range(tries):
        X = rng.sample(IFF, len(L))
        if cov(X) == cov(L) and ovl(X) == ovl(L): out.append(ptm(X))
        if len(out) >= k: break
    return out if len(out) >= 20 else []
NM = [ptm(L) for L in natm]
RES['modals'] = {'random meanings, same size': net(NM, [m_rand(L) for L in natm]),
                 'IFF distinct, same size, coverage & overlap': net(NM, [m_struct(L) for L in natm])}
print('modals', RES['modals'], flush=True)
# ---------- quantifiers (steinertthrelkeld2021): from saved per-language samples ----------
Q = json.load(open(os.path.join(PAPERS, 'steinertthrelkeld2021-quantifiers-degrees-universals', 'reanalysis', 'out', 'out_q2_ladder.json')))
def qpts(name): 
    a = np.array(Q[name]); return {n: [(r[2], -r[1]) for r in a if r[0] == n] for n in range(1, 11)}  # (complexity, informativeness = -cost)
qn = qpts('Q: quasi-natural (114)'); qr = qpts('R: random non-natural'); qs = qpts('MC: monotone+conservative, non-natural')
natq = [p for n in range(1, 11) for p in qn[n][:60]]; sizes = [n for n in range(1, 11) for _ in qn[n][:60]]
RES['quantifiers (natural = quasi-natural pool; no attested inventories)'] = {
    'random non-natural, same size': net(natq, [qr[n] for n in sizes]),
    'monotone+conservative non-natural, same size': net(natq, [qs[n] for n in sizes])}
print('quantifiers', RES['quantifiers (natural = quasi-natural pool; no attested inventories)'], flush=True)
json.dump(RES, open(os.path.join(HERE, 'out', 'x1_net_dominance.json'), 'w'), indent=1)
