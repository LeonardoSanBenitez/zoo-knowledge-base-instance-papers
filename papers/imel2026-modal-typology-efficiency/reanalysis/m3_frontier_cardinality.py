import itertools, random, statistics as st, numpy as np
import statsmodels.api as sm
from mcore import *
ALL = list(range(1, 64))
# exact-ish frontier: all multisets of distinct meanings up to size 4, plus all set partitions of the 6 points (+ subsets)
def parts(s):
    if not s: yield []; return
    f, r = s[0], s[1:]
    for p in parts(r):
        for i in range(len(p)): yield p[:i] + [[f] + p[i]] + p[i + 1:]
        yield [[f]] + p
cands = [list(c) for n in range(1, 5) for c in itertools.combinations(ALL, n)]
for S in range(1, 64):
    sub = [j for j in range(6) if S >> j & 1]
    for p in parts(sub): cands.append([sum(1 << j for j in b) for b in p])
for pname, pr in [('correct', PRIOR), ('as-run', PRIOR_AS_RUN)]:
    for cname, cf in [('atoms', complexity), ('code', complexity_code)]:
        best = {}
        for L in cands:
            c = cf(L); i = informativeness(L, pr)
            if c not in best or i > best[c][0] + 1e-12: best[c] = (i, L)
        front = []; m = -1
        for c in sorted(best):
            if best[c][0] > m + 1e-12: front.append((c, best[c][0], best[c][1])); m = best[c][0]
        print(f"{pname:8s} {cname:6s} frontier pts {len(front):2d}; all-IFF: {all(all(is_iff(x) for x in L) for _, _, L in front)}; non-IFF frontier langs: {[ (c, [bin(x) for x in L]) for c, i, L in front if not all(is_iff(x) for x in L)][:3]}")
# cardinality control for the IFF-informativeness correlation (uniform prior, binary utility -> relabel-invariant)
random.seed(9)
R = [[random.randint(1, 63) for _ in range(random.randint(1, 10))] for _ in range(20000)]
y = np.array([informativeness(L, UNIFORM, u_bin) for L in R]); iff = np.array([st.mean(is_iff(m) for m in L) for L in R])
msize = np.array([st.mean(bin(m).count('1') for m in L) for L in R]); n = np.array([len(L) for L in R])
ovl = np.array([sum(max(sum(m >> p & 1 for m in L) - 1, 0) for p in range(6)) for L in R])
print('uniform+binary: r(IFF share, informativeness) =', round(np.corrcoef(iff, y)[0, 1], 3))
X = sm.add_constant(np.column_stack([iff, msize, n, ovl])); f = sm.OLS(y, X).fit()
print('  OLS inf ~ IFFshare + mean meaning size + n + overlap: IFF coef', round(f.params[1], 4), 't', round(f.tvalues[1], 2), '| msize t', round(f.tvalues[2], 1))
print('  r(IFF share, mean meaning size) =', round(np.corrcoef(iff, msize)[0, 1], 3))
