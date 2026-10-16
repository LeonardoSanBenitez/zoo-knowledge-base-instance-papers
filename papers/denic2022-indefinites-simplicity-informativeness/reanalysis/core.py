"""Python re-implementation of Denic, Steinert-Threlkeld & Szymanik (2022) measures.
Mirrors repo/Experiment_1_and_2/src/Indefinites_functions.R."""
import csv, ast, itertools, math, os
# Point DENIC_REPO at a clone of github.com/milicaden/indefinite-pronouns-simplicity-informativeness @ 1e5c5cc
REPO = os.environ.get('DENIC_REPO', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'repo'))
D = os.path.join(REPO, 'Experiment_1_and_2', 'data')
FL = ['sk', 'su', 'ns', 'npi', 'fci', 'nq']
_pr = list(csv.DictReader(open(os.path.join(D, 'Beekhuizen_priors.csv'))))[0]
PRIOR = {k: float(v) for k, v in _pr.items()}

def load_mindesc(path=None):
    path = path or os.path.join(D, 'minimum-desc-indef.csv')
    out = {}
    for r in csv.DictReader(open(path), delimiter=';'):
        m = r['meaning']
        key = tuple(1 if p != 'X' else 0 for p in m.split('-'))
        out[key] = int(r['complexity'])
    return out
COMPLEX = load_mindesc()

def literal_inf(lang, prior=PRIOR):
    """lang: list of 6-tuples of 0/1. I(L)=sum_f sum_i P(f) L(f|i) S(i|f)."""
    n_f = {f: sum(it[j] for it in lang) for j, f in enumerate(FL)}
    u = 0.0
    for it in lang:
        k = sum(it)
        if k == 0: continue
        for j, f in enumerate(FL):
            if it[j]:
                u += prior[f] * (1 / k) * (1 / n_f[f])
    return u

def rsa_inf(lang, prior=PRIOR):
    # L0 uniform over flavours in item; S1 prop to exp(log L0) = L0 (alpha=1); L1 prop S1*prior
    L0 = [[(it[j] / sum(it)) if sum(it) else 0 for j in range(6)] for it in lang]
    S1 = [[0.0] * 6 for _ in lang]
    for j in range(6):
        den = sum(L0[i][j] for i in range(len(lang)))
        for i in range(len(lang)):
            S1[i][j] = L0[i][j] / den if den else 0
    u = 0.0
    for i in range(len(lang)):
        den = sum(S1[i][j] * prior[FL[j]] for j in range(6))
        for j in range(6):
            if den:
                L1 = S1[i][j] * prior[FL[j]] / den
                u += prior[FL[j]] * L1 * S1[i][j]
    return u

def cost(lang, prior=PRIOR):
    return 1 / literal_inf(lang, prior)
def rsacost(lang, prior=PRIOR):
    return 1 / rsa_inf(lang, prior)
def complexity(lang, table=COMPLEX):
    return sum(table[tuple(it)] for it in lang)
def overlap(lang):
    return sum(max(sum(it[j] for it in lang) - 1, 0) for j in range(6))
def coverage(lang):
    return sum(1 for j in range(6) if any(it[j] for it in lang))

def load_langs(fname, typecol='type'):
    langs, types = {}, {}
    for r in csv.DictReader(open(os.path.join(D, fname))):
        it = tuple(int(r[f + 'flavor']) for f in FL)
        langs.setdefault(r['LANG'], []).append(it)
        types[r['LANG']] = r.get(typecol)
    return langs, types

def load_cc(fname):
    return {r['LANG']: r for r in csv.DictReader(open(os.path.join(D, fname)))}

def set_partitions(s):
    if not s:
        yield []
        return
    first, rest = s[0], s[1:]
    for p in set_partitions(rest):
        for i in range(len(p)):
            yield p[:i] + [[first] + p[i]] + p[i + 1:]
        yield [[first]] + p

def part_to_lang(p):
    return [tuple(1 if j in b else 0 for j in range(6)) for b in p]
