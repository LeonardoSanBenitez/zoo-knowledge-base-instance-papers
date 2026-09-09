"""A6. Is the choice->map association just the choice->smoothness association wearing
a different hat?

A5 put three responses on one scale against the same pipeline-choice distance:
    precision   |log resels_i - log resels_j|   Mantel rho = +0.259
    answer      1 - r(map_i, map_j), mean over 7 hyps   +0.185
    conclusion  |yes_i - yes_j|                          +0.015 (n.s.)

0.185 is not zero, so the strong form of my Breznau through-line ("decisions say nothing
about what the answer is") is already refuted here. The remaining question is the
mechanism: two maps produced with similar smoothing are more correlated with each other
FOR THAT REASON ALONE -- smoothing raises the correlation between any two images. So the
choice->map link may be entirely a precision effect.

Partial Mantel: rho(choice, map | precision), with the same team-label permutation null.
If it collapses towards zero, the through-line survives in a corrected and more precise
form. If it does not, the through-line is wrong and must be rewritten.
"""
import sys, os, json
import numpy as np
import pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import load
from a5_mantel import gower, CATS, NUMS, HYPS

NPERM = 10000


def upper(A):
    n = A.shape[0]
    return A[np.triu_indices(n, 1)]


def partial_spearman(a, b, c):
    ra, rb, rc = (stats.rankdata(x) for x in (a, b, c))
    def resid(y, x):
        x = np.c_[np.ones(len(x)), x]
        beta, *_ = np.linalg.lstsq(x, y, rcond=None)
        return y - x @ beta
    return float(np.corrcoef(resid(ra, rc), resid(rb, rc))[0, 1])


def mantel_partial(A, B, Cm, nperm=NPERM, seed=0, partial=True):
    """A permuted (rows+cols) against fixed B, controlling for Cm."""
    n = A.shape[0]
    b = upper(B); c = upper(Cm)
    a = upper(A)
    f = (lambda x: partial_spearman(x, b, c)) if partial else \
        (lambda x: float(stats.spearmanr(x, b).statistic))
    obs = f(a)
    rng = np.random.default_rng(seed)
    null = np.empty(nperm)
    for i in range(nperm):
        p = rng.permutation(n)
        null[i] = f(upper(A[np.ix_(p, p)]))
    return dict(stat=float(obs), null_mean=float(null.mean()),
                null_sd=float(null.std(ddof=1)),
                null_p95=float(np.percentile(null, 95)),
                p_one_sided=float((1 + (null >= obs).sum()) / (1 + nperm)),
                nperm=nperm, n_teams=int(n))


def main():
    m = load.metadata(); g = m.groupby('teamID')
    t = pd.DataFrame(index=sorted(m.teamID.unique()))
    for c in CATS:
        t[c] = g[c].first().astype(str).str.strip().str.lower()
    for c in NUMS:
        t[c] = pd.to_numeric(g[c].first(), errors='coerce')
    tv = pd.read_csv(os.path.join(load.ROOT, 'metadata', 'thresh_voxel_data.csv'))
    D = load.decisions()
    t['log_resels'] = np.log(g['resels'].mean())
    t['log_vox'] = np.log1p(tv.groupby('teamID')['n_thresh_vox'].median())
    t['yes_count'] = D.sum(axis=1).astype(float)

    C1 = load.unthresh_corr(1)
    teams = [x for x in C1.index if x in t.index and np.isfinite(t.loc[x, 'log_resels'])
             and np.isfinite(t.loc[x, 'log_vox'])]
    tt = t.loc[teams]
    Dch = gower(tt)
    Dmap = np.mean([1.0 - load.unthresh_corr(h).loc[teams, teams].values.astype(float)
                    for h in HYPS], axis=0)

    def dm(col):
        v = tt[col].values.astype(float)
        return np.abs(v[:, None] - v[None, :])

    Dprec = dm('log_resels')
    Dvox = dm('log_vox')
    Ddec = dm('yes_count')

    out = {'n_teams': len(teams)}
    out['marginal_choice_vs_map'] = mantel_partial(Dch, Dmap, Dprec, partial=False, seed=1)
    out['marginal_choice_vs_precision'] = mantel_partial(Dch, Dprec, Dprec, partial=False, seed=2)
    out['marginal_choice_vs_vox'] = mantel_partial(Dch, Dvox, Dprec, partial=False, seed=3)
    out['marginal_choice_vs_decision'] = mantel_partial(Dch, Ddec, Dprec, partial=False, seed=4)
    out['partial_choice_vs_map_given_resels'] = mantel_partial(Dch, Dmap, Dprec, seed=5)
    out['partial_choice_vs_map_given_vox'] = mantel_partial(Dch, Dmap, Dvox, seed=6)
    out['partial_choice_vs_decision_given_map'] = mantel_partial(Dch, Ddec, Dmap, seed=7)
    out['marginal_map_vs_precision'] = mantel_partial(Dmap, Dprec, Dprec, partial=False, seed=8)
    out['marginal_map_vs_decision'] = mantel_partial(Dmap, Ddec, Dprec, partial=False, seed=9)
    for k, v in out.items():
        if isinstance(v, dict):
            print(f"{k:38s} rho={v['stat']:+.4f} null_mean={v['null_mean']:+.4f} "
                  f"null95={v['null_p95']:+.4f} p={v['p_one_sided']:.4f}")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                           'artifacts', 'a6_partial_mantel.json'), 'w') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()
