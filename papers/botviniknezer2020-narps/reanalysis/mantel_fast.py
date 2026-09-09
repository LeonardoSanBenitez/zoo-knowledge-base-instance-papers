"""Fast Mantel by exploiting an exact invariance.

Permuting rows AND columns of a distance matrix by the same permutation is a bijection
on the set of unordered pairs, so the MULTISET of off-diagonal entries is unchanged.
Therefore the ranks can be computed ONCE, and every permutation is a relabelling of
already-known rank values -- no re-ranking, and the mean and sd of the permuted vector
are constants. Spearman then reduces to a single dot product per permutation.

Verified against scipy.stats.spearmanr in selftest(), on the observed statistic AND on
a permuted draw.
"""
import numpy as np
from scipy import stats


def _rank_matrix(D):
    n = D.shape[0]
    iu = np.triu_indices(n, 1)
    r = stats.rankdata(D[iu])
    R = np.zeros((n, n), dtype=float)
    R[iu] = r
    R = R + R.T
    return R, iu


def mantel_fast(A, B, nperm=20000, seed=0, blocks=None):
    """A permuted against fixed B. `blocks`: optional group labels; whole groups are
    permuted and their members stay together (nested designs)."""
    n = A.shape[0]
    RA, iu = _rank_matrix(A)
    RB, _ = _rank_matrix(B)
    a = RA[iu]; b = RB[iu]
    obs = float(np.corrcoef(a, b)[0, 1])
    ma, sa = a.mean(), a.std()
    mb, sb = b.mean(), b.std()
    m = len(a)
    rng = np.random.default_rng(seed)
    pos = src = u = None
    if blocks is not None:
        blocks = np.asarray(blocks)
        u = np.unique(blocks)
        pos = [np.where(blocks == g)[0] for g in u]
        src = np.concatenate(pos)
    null = np.empty(nperm)
    for i in range(nperm):
        if blocks is None:
            p = rng.permutation(n)
        else:
            order = rng.permutation(len(u))
            dst = np.concatenate([pos[j] for j in order])
            p = np.empty(n, int); p[src] = dst
        s = float((RA[np.ix_(p, p)] * RB).sum() * 0.5)
        null[i] = (s / m - ma * mb) / (sa * sb)
    return dict(rho=obs, null_mean=float(null.mean()), null_sd=float(null.std(ddof=1)),
                null_p95=float(np.percentile(null, 95)),
                p_one_sided=float((1 + (null >= obs).sum()) / (1 + nperm)),
                n_units=int(n), n_pairs=int(m), nperm=int(nperm))


def selftest():
    rng = np.random.default_rng(0)
    for n in (30, 60):
        X = rng.normal(size=(n, 4))
        Y = X @ rng.normal(size=(4, 3)) + rng.normal(size=(n, 3))
        A = np.sqrt(((X[:, None] - X[None]) ** 2).sum(-1))
        B = np.sqrt(((Y[:, None] - Y[None]) ** 2).sum(-1))
        iu = np.triu_indices(n, 1)
        ref = stats.spearmanr(A[iu], B[iu]).statistic
        got = mantel_fast(A, B, nperm=50)['rho']
        assert abs(ref - got) < 1e-9, (ref, got)
        rng2 = np.random.default_rng(5)
        p = rng2.permutation(n)
        brute = stats.spearmanr(A[np.ix_(p, p)][iu], B[iu]).statistic
        RA, _ = _rank_matrix(A); RB, _ = _rank_matrix(B)
        a = RA[iu]; b = RB[iu]
        s = float((RA[np.ix_(p, p)] * RB).sum() * 0.5)
        fast = (s / len(a) - a.mean() * b.mean()) / (a.std() * b.std())
        assert abs(brute - fast) < 1e-9, (brute, fast)
    return 'mantel_fast selftest OK (matches scipy on the observed statistic and on a permuted draw, n=30 and n=60)'


if __name__ == '__main__':
    print(selftest())
