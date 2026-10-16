"""Re-implementation of Imel, Guo & Steinert-Threlkeld (2026) modal measures (literal agents, half-credit/indicator utility)."""
import os, csv, itertools, yaml
DS = os.environ.get('MODALS_DS', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'artifacts'))
FORCES = ['weak', 'strong']; FLAVORS = ['epistemic', 'deontic', 'circumstantial']
POINTS = [f'{fo}+{fl}' for fo in FORCES for fl in FLAVORS]  # 6 points, index j
IDX = {p: j for j, p in enumerate(POINTS)}
def load_prior(path=None):
    rows = list(csv.DictReader(open(path or os.path.join(DS, 'prior.csv'))))
    return [float({r['name']: r['probability'] for r in rows}[p]) for p in POINTS]
PRIOR = load_prior(); UNIFORM = [1 / 6] * 6
def bm(points): return sum(1 << IDX[p] for p in points)
FULL = 63
def lit_sets():
    s = {}
    for fo in FORCES: s[bm([f'{fo}+{fl}' for fl in FLAVORS])] = 1
    for fl in FLAVORS: s[bm([f'{fo}+{fl}' for fo in FORCES])] = 1
    for m in list(s): s[FULL & ~m] = 1  # negated atoms
    return s
def closure(prims):
    best = dict(prims); changed = True
    while changed:
        changed = False; ks = list(best.items())
        for a, ca in ks:
            for b, cb in ks:
                for m in (a | b, a & b):
                    if m and (m not in best or ca + cb < best[m]): best[m] = ca + cb; changed = True
    return best
CPLX = closure(lit_sets())  # complexity of each non-empty meaning (bitmask)
def u_half(i, j):
    fi, li = divmod(i, 3); fj, lj = divmod(j, 3)
    return 0.5 * (fi == fj) + 0.5 * (li == lj)
def u_bin(i, j): return 1.0 if i == j else 0.0
def informativeness(lang, prior=PRIOR, u=u_half):
    """lang: list of bitmasks (multiset). literal speaker uniform over modals expressing p; literal listener uniform over m's points."""
    I = 0.0
    for p in range(6):
        ms = [m for m in lang if m >> p & 1]
        if not ms: continue
        for m in ms:
            pts = [q for q in range(6) if m >> q & 1]
            I += prior[p] * (1 / len(ms)) * sum(u(p, q) for q in pts) / len(pts)
    return I
def complexity(lang): return sum(CPLX[m] for m in lang)
def is_iff(m):
    pts = [q for q in range(6) if m >> q & 1]
    fos = {q // 3 for q in pts}; fls = {q % 3 for q in pts}
    return len(pts) == len(fos) * len(fls)
def load_natural(path):
    y = yaml.safe_load(open(path)); out = {}
    for entry in y['languages']:
        (name, v), = entry.items()
        out[name] = dict(lang=[bm(e['meaning']) for e in v['expressions']], data=v['data'], lots=[e.get('lot') for e in v['expressions']])
    return out

# --- the measure the published code actually computes (num_atoms bug: sums len(child) = node counts) ---
def closure_nodes():
    """min node count of a formula over {atoms, not, and, or}; returns (nodes, root_is_atom)"""
    best = {}
    for fo in FORCES: best[bm([f'{fo}+{fl}' for fl in FLAVORS])] = (1, True)
    for fl in FLAVORS: best[bm([f'{fo}+{fl}' for fo in FORCES])] = (1, True)
    changed = True
    while changed:
        changed = False; ks = list(best.items())
        for a, (na, _) in ks:
            m = FULL & ~a
            if m and (m not in best or na + 1 < best[m][0]): best[m] = (na + 1, False); changed = True
            for b, (nb, _) in ks:
                for m in (a | b, a & b):
                    if m and (m not in best or na + nb + 1 < best[m][0]): best[m] = (na + nb + 1, False); changed = True
    return best
_NODES = closure_nodes()
CPLX_CODE = {m: (n if atom else n - 1) for m, (n, atom) in _NODES.items()}
def complexity_code(lang): return sum(CPLX_CODE[m] for m in lang)

def informativeness_bayes(lang, prior=PRIOR, u=u_half):
    """literal listener weights the meaning's points by the prior (ultk LiteralListener)."""
    I = 0.0
    for p in range(6):
        ms = [m for m in lang if m >> p & 1]
        if not ms: continue
        for m in ms:
            pts = [q for q in range(6) if m >> q & 1]; Z = sum(prior[q] for q in pts)
            I += prior[p] * (1 / len(ms)) * sum(prior[q] / Z * u(p, q) for q in pts)
    return I

# The prior the published pipeline actually applied: Table 5 values in REVERSED point order
# (found 2026-10-16: the unique one of 720 assignments reproducing all 28 natural informativities to 3e-16).
PRIOR_AS_RUN = list(reversed(PRIOR))
