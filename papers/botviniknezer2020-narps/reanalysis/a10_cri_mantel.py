"""A10. Turn the new instrument on my own old corpus.

`maria2026-analytic-variability-reanalysis` reported, on the Crowdsourced Replication
Initiative data (Breznau et al. 2022): out-of-fold, folds grouped by team,
    137 coded decision indicators -> log standard error   R^2 = +0.194 +/- 0.024
    137 coded decision indicators -> the point estimate   R^2 = -0.005
and read the second as "analytic decisions say nothing about what the answer is".

NARPS just showed that a CV R^2 at n=70 can miss an association a Mantel test finds
(choices vs map: CV R^2 = -0.07 on a scalar summary, Mantel rho = +0.19 on the pairwise
structure). So the -0.005 may be an underpowered zero. Same instrument, same corpus,
team level so the two are comparable.

Data on disk: ../breznau2022-hidden-universe/data/cri_model_level.csv (1309 models),
column_blocks.json marks which columns are decisions and which are researcher traits.
"""
import sys, os, json
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
CRI = os.path.join(HERE, '..', '..', 'breznau2022-hidden-universe', 'data')
NPERM = 20000


sys.path.insert(0, HERE if 'HERE' in dir() else os.path.dirname(os.path.abspath(__file__)))
from mantel_fast import mantel_fast


def mantel(A, B, nperm=NPERM, seed=0, blocks=None):
    return mantel_fast(A, B, nperm=nperm, seed=seed, blocks=blocks)


def main():
    d = pd.read_csv(os.path.join(CRI, 'cri_model_level.csv'))
    blocks = json.load(open(os.path.join(CRI, 'column_blocks.json')))
    dec_cols = [c for c in blocks['decisions'] if c in d.columns]
    d = d[np.isfinite(d['AME_Z']) & np.isfinite(d['error']) & (d['error'] > 0)]
    out = {'n_models': int(len(d)), 'n_decision_cols': len(dec_cols)}

    g = d.groupby('u_teamid')
    t = pd.DataFrame({
        'estimate': g['AME_Z'].median(),
        'log_se': np.log(g['error'].median()),
        'n_models': g.size(),
    })
    # team profile in decision space: mean of each 0/1 indicator over the team's models
    P = g[dec_cols].mean()
    P = P.loc[t.index]
    keep = P.columns[(P.std() > 0)]
    P = P[keep]
    out['n_teams'] = int(len(t))
    out['n_decision_cols_used'] = int(P.shape[1])

    Pz = (P - P.mean()) / P.std()
    Pz = Pz.fillna(0.0).values
    n = len(t)
    Dch = np.sqrt(((Pz[:, None, :] - Pz[None, :, :]) ** 2).sum(-1))
    Dest = np.abs(t['estimate'].values[:, None] - t['estimate'].values[None, :])
    Dse = np.abs(t['log_se'].values[:, None] - t['log_se'].values[None, :])

    out['choice_vs_estimate'] = mantel(Dch, Dest, seed=1)
    out['choice_vs_log_se'] = mantel(Dch, Dse, seed=2)
    out['estimate_vs_log_se'] = mantel(Dest, Dse, seed=3)
    for k in ['choice_vs_estimate', 'choice_vs_log_se', 'estimate_vs_log_se']:
        v = out[k]
        print(f"CRI  {k:22s} mantel rho={v['rho']:+.4f} null95={v['null_p95']:+.4f} "
              f"p={v['p_one_sided']:.4f} n_teams={v['n_units']}")

    # robustness: teams with at least 5 models, so the team profile is not one model
    m5 = t['n_models'] >= 5
    idx = np.where(m5.values)[0]
    out['n_teams_ge5models'] = int(m5.sum())
    out['choice_vs_estimate_ge5'] = mantel(Dch[np.ix_(idx, idx)], Dest[np.ix_(idx, idx)], seed=4)
    out['choice_vs_log_se_ge5'] = mantel(Dch[np.ix_(idx, idx)], Dse[np.ix_(idx, idx)], seed=5)
    for k in ['choice_vs_estimate_ge5', 'choice_vs_log_se_ge5']:
        v = out[k]
        print(f"CRI  {k:22s} mantel rho={v['rho']:+.4f} null95={v['null_p95']:+.4f} "
              f"p={v['p_one_sided']:.4f} n_teams={v['n_units']}")

    # and the MODEL level, where n is 1309 and power is not the issue at all,
    # permuting whole teams so models stay with their team
    dm = d.reset_index(drop=True)
    Pm = dm[keep].astype(float)
    Pm = ((Pm - Pm.mean()) / Pm.std()).fillna(0.0).values
    est = dm['AME_Z'].values; lse = np.log(dm['error'].values)
    teams = dm['u_teamid'].values
    uteams = np.unique(teams)
    Dc = np.sqrt(((Pm[:, None, :] - Pm[None, :, :]) ** 2).sum(-1))
    De = np.abs(est[:, None] - est[None, :])
    Ds = np.abs(lse[:, None] - lse[None, :])

    out['model_level_choice_vs_estimate'] = mantel(Dc, De, nperm=2000, seed=11,
                                                   blocks=teams)
    out['model_level_choice_vs_log_se'] = mantel(Dc, Ds, nperm=2000, seed=12,
                                                 blocks=teams)
    for k in ['model_level_choice_vs_estimate', 'model_level_choice_vs_log_se']:
        v = out[k]
        print(f"CRI  {k:34s} rho={v['rho']:+.4f} null95={v['null_p95']:+.4f} "
              f"p={v['p_one_sided']:.4f} (n={v['n_units']} models, teams permuted whole)")
    with open(os.path.join(HERE, '..', 'artifacts', 'a10_cri_mantel.json'), 'w') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()
