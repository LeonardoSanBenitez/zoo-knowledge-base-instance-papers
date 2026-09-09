"""A5. Do the pipeline CHOICES determine the MAP?

A2b used one scalar summary of a team's map (its median correlation with the consensus)
and found the choices predict it at CV R^2 = -0.07, i.e. not at all. That is one
projection of a 64-dimensional object and it could hide structure.

This is the assumption-light version. Build two team-by-team distance matrices:
    map distance     = 1 - Spearman correlation between unthresholded maps  (NARPS's own)
    choice distance  = Gower distance over the coded pipeline choices
and Mantel-test them, permuting team labels (which is the exact conditional null: it
leaves both matrices intact and only breaks the pairing).

This test CAN fail against me. NARPS itself found a seven-team anticorrelated cluster on
H1/H3 traced to a model misspecification -- a choice that plainly did change the map. So
a positive Mantel statistic is expected somewhere; the question is its size, and whether
it appears on hypotheses with no such misspecification story.
"""
import sys, os, json
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import load

HYPS = [1, 2, 5, 6, 7, 8, 9]
CATS = ['package', 'testing', 'correction_method', 'statistic_type',
        'inter_subject_reg', 'motion_correction', 'model_type',
        'used_fmriprep_data', 'regions_definition']
NUMS = ['smoothing_coef', 'movement_modeling', 'n_participants']
NPERM = 10000


def gower(t):
    n = len(t)
    D = np.zeros((n, n)); W = np.zeros((n, n))
    for c in CATS:
        v = t[c].astype(str).values
        d = (v[:, None] != v[None, :]).astype(float)
        ok = ((v[:, None] != 'nan') & (v[None, :] != 'nan')).astype(float)
        D += d * ok; W += ok
    for c in NUMS:
        v = pd.to_numeric(t[c], errors='coerce').values.astype(float)
        rng = np.nanmax(v) - np.nanmin(v)
        d = np.abs(v[:, None] - v[None, :]) / (rng if rng else 1.0)
        ok = np.isfinite(d).astype(float); d = np.nan_to_num(d)
        D += d * ok; W += ok
    return D / np.maximum(W, 1)


def mantel(A, B, nperm=NPERM, seed=0):
    n = A.shape[0]
    iu = np.triu_indices(n, 1)
    a = A[iu]; b = B[iu]
    from scipy import stats
    r_obs = stats.spearmanr(a, b).statistic
    rng = np.random.default_rng(seed)
    null = np.empty(nperm)
    for i in range(nperm):
        p = rng.permutation(n)
        null[i] = stats.spearmanr(A[np.ix_(p, p)][iu], b).statistic
    pv = (1 + (null >= r_obs).sum()) / (1 + nperm)
    return dict(mantel_rho=float(r_obs), null_mean=float(null.mean()),
                null_sd=float(null.std(ddof=1)),
                null_p95=float(np.percentile(null, 95)),
                p_one_sided=float(pv), n_teams=int(n), nperm=nperm)


def main():
    m = load.metadata()
    g = m.groupby('teamID')
    t = pd.DataFrame(index=sorted(m.teamID.unique()))
    for c in CATS:
        t[c] = g[c].first().astype(str).str.strip().str.lower()
    for c in NUMS:
        t[c] = pd.to_numeric(g[c].first(), errors='coerce')

    out = {}
    for h in HYPS:
        C = load.unthresh_corr(h)
        teams = [x for x in C.index if x in t.index]
        C = C.loc[teams, teams]
        Dmap = 1.0 - C.values.astype(float)
        Dch = gower(t.loc[teams])
        out[f'hyp{h}'] = mantel(Dmap, Dch, seed=h)
        v = out[f'hyp{h}']
        print(f"h{h}: mantel rho={v['mantel_rho']:+.4f} null95={v['null_p95']:+.4f} "
              f"p={v['p_one_sided']:.4f} n={v['n_teams']}")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                           'artifacts', 'a5_mantel.json'), 'w') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()


def main_scaled():
    """Same Mantel statistic, same choice-distance matrix, three different response
    distances, so precision / answer / conclusion are finally on ONE scale."""
    import json as _json
    m = load.metadata()
    g = m.groupby('teamID')
    t = pd.DataFrame(index=sorted(m.teamID.unique()))
    for c in CATS:
        t[c] = g[c].first().astype(str).str.strip().str.lower()
    for c in NUMS:
        t[c] = pd.to_numeric(t.index.map(g[c].first()), errors='coerce')
    tv = pd.read_csv(os.path.join(load.ROOT, 'metadata', 'thresh_voxel_data.csv'))
    D = load.decisions()
    t['log_resels'] = np.log(g['resels'].mean())
    t['log_vox'] = np.log1p(tv.groupby('teamID')['n_thresh_vox'].median())
    t['yes_count'] = D.sum(axis=1)

    C = load.unthresh_corr(1)
    teams = [x for x in C.index if x in t.index]
    tt = t.loc[teams]
    Dch = gower(tt)

    def dmat(col):
        v = tt[col].values.astype(float)
        return np.abs(v[:, None] - v[None, :])

    out = {}
    # map distance averaged over the seven deposited hypotheses
    Dmaps = []
    for h in HYPS:
        Ch = load.unthresh_corr(h).loc[teams, teams]
        Dmaps.append(1.0 - Ch.values.astype(float))
    out['map_distance_mean_over_7hyp'] = mantel(np.mean(Dmaps, axis=0), Dch, seed=101)
    for col in ['log_resels', 'log_vox', 'yes_count']:
        out[col] = mantel(dmat(col), Dch, seed=hash(col) % 1000)
    for k, v in out.items():
        print(f"{k:34s} mantel rho={v['mantel_rho']:+.4f} "
              f"null95={v['null_p95']:+.4f} p={v['p_one_sided']:.4f}")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                           'artifacts', 'a5b_mantel_onescale.json'), 'w') as f:
        _json.dump(out, f, indent=1)
