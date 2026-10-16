import itertools, json, statistics as st, numpy as np
from core import *
FAM = {'Indo-European': 'GERMAN ENGLISH DUTCH ICELAND SWEDISH FRENCH ITALIAN CATALAN PORTUG ROMANIAN LATIN RUSSIAN SERBIAN POLISH BULGARIAN LITHUANIAN LATVIAN IRISH GREEK OSSETIC PERSIAN HINDI',
       'Uralic': 'FINNISH HUNGARIAN', 'Turkic': 'TURKISH KAZAKH YAKUT', 'Tungusic': 'NANAY', 'Kartvelian': 'GEORGIAN', 'NE-Caucasian': 'LEZGIAN',
       'Afroasiatic': 'HEBREW MALTESE HAUSA', 'Isolate-Basque': 'BASQUE', 'Sino-Tibetan': 'CHINESE', 'Japonic': 'JAPANESE', 'Koreanic': 'KOREAN',
       'Dravidian': 'KANNADA', 'Quechuan': 'QUECHUA', 'Niger-Congo': 'SWAHILI'}
fam_of = {l: f for f, ls in FAM.items() for l in ls.split()}
langs, types = load_langs('languages_exp1.csv'); cc = load_cc('all_complexity_cost_exp1.csv')
natn = [L for L in cc if cc[L]['type'] == 'natural']
assert set(natn) == set(fam_of), set(natn) ^ set(fam_of)
front = json.load(open('out/out_exact_front_literal.json'))
FX = np.array([k for c, k, L in front]); FY = np.array([c for c, k, L in front])
w = {L: 1 / sum(1 for x in natn if fam_of[x] == fam_of[L]) for L in natn}; W = sum(w.values())
def perm_lang(L, s): return [tuple(it[s[j]] for j in range(6)) for it in L]
vals = []
for s in itertools.permutations(range(6)):
    d = {L: float(np.min(np.hypot(FX - cost(perm_lang(langs[L], s)), FY - complexity(perm_lang(langs[L], s))))) for L in natn}
    vals.append((sum(w[L] * d[L] for L in natn) / W, st.mean(d.values())))
fw, plain = vals[0]
print('families', len(FAM), 'IE share', 22 / 40)
print('family-weighted mean d_ex real', round(fw, 3), 'perms better', sum(v[0] < fw - 1e-12 for v in vals), '/720')
print('plain mean d_ex real', round(plain, 3), 'perms better', sum(v[1] < plain - 1e-12 for v in vals), '/720')
for f in FAM:
    ls = [L for L in natn if fam_of[L] == f]
    print(f"{f:15s} n={len(ls):2d} mean c={st.mean(complexity(langs[L]) for L in ls):5.2f} cost={st.mean(cost(langs[L]) for L in ls):.3f}")
