"""Is natural-vs-structural-null ordering an artefact of the Euclidean axis scale? Rescale complexity by k and recompute."""
import json, random, statistics as st, numpy as np
from scipy import stats
from core import *
front = json.load(open('out/out_exact_front_literal.json'))
FX = np.array([k for c, k, L in front]); FY = np.array([c for c, k, L in front], float)
langs, types = load_langs('languages_exp1.csv'); cc = load_cc('all_complexity_cost_exp1.csv')
nat = [langs[L] for L in cc if cc[L]['type'] == 'natural']
random.seed(11)
shape = [(len(L), coverage(L)) for L in nat if len(L) <= coverage(L)]
null1 = []
while len(null1) < 4000:
    n, cv = random.choice(shape)
    while True:
        S = random.sample(range(6), cv); lab = [random.randrange(n) for _ in S]
        if len(set(lab)) == n: break
    null1.append([tuple(1 if (j in S and lab[S.index(j)] == b) else 0 for j in range(6)) for b in range(n)])
def pts(Ls): return np.array([cost(L) for L in Ls]), np.array([complexity(L) for L in Ls], float)
nk, nc = pts(nat); uk, uc = pts(null1)
for k in [0.03, 0.1, 0.3, 1, 3, 10]:
    dn = np.array([np.min(np.hypot(FX - a, k * (FY - b))) for a, b in zip(nk, nc)])
    du = np.array([np.min(np.hypot(FX - a, k * (FY - b))) for a, b in zip(uk, uc)])
    t = stats.ttest_ind(dn, du, equal_var=False)
    print(f"complexity axis x{k:<5} natural {dn.mean():.4f}  overlap-free {du.mean():.4f}  ratio {dn.mean()/du.mean():.3f}  p {t.pvalue:.4f}")
