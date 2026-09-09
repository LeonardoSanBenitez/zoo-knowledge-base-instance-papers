"""A10d. The CRI question, redone with a null that is actually correct.

a10c withdrew the model-level numbers: the block permutation kept only 46% of
within-team pairs within-team, because CRI team sizes run from 1 to 112 models.

Correct design, and the same one used on NARPS so the two are comparable:
one row per TEAM, within each dependent variable, and a free permutation of teams.

  unit          = team (n up to 72, fewer for DVs not everyone ran)
  choice space  = the team's mean of each decision indicator for that DV,
                  standardised, Euclidean; DV indicators excluded (constant here anyway)
  estimate      = the team's median AME_Z for that DV
  precision     = the team's median log(standard error) for that DV

Pooled across the six DVs with ONE permutation applied to all six simultaneously, because
the six share the same 72 teams and are not six independent studies.
"""
import sys, os, json
import numpy as np
import pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mantel_fast import _rank_matrix

HERE = os.path.dirname(os.path.abspath(__file__))
CRI = os.path.join(HERE, '..', '..', 'breznau2022-hidden-universe', 'data')
DV_COLS = ['Jobs', 'Unemp', 'IncDiff', 'OldAge', 'House', 'Health']
NPERM = 20000


def dist(P):
    P = np.asarray(P, float)
    sd = P.std(0)
    P = (P - P.mean(0)) / np.where(sd > 0, sd, 1)
    P = np.nan_to_num(P)
    return np.sqrt(((P[:, None, :] - P[None, :, :]) ** 2).sum(-1))


def prep(Dc, Dr):
    RA, iu = _rank_matrix(Dc)
    RB, _ = _rank_matrix(Dr)
    a = RA[iu]; b = RB[iu]
    return RA, RB, iu, a.mean(), a.std(), b.mean(), b.std(), len(a)


def stat(RA, RB, p, ma, sa, mb, sb, m):
    s = float((RA[np.ix_(p, p)] * RB).sum() * 0.5)
    return (s / m - ma * mb) / (sa * sb)


def main():
    d = pd.read_csv(os.path.join(CRI, 'cri_model_level.csv'))
    blocks = json.load(open(os.path.join(CRI, 'column_blocks.json')))
    dec = [c for c in blocks['decisions'] if c in d.columns and c not in DV_COLS]
    d = d[np.isfinite(d['AME_Z']) & np.isfinite(d['error']) & (d['error'] > 0)]
    d = d.copy(); d['log_se'] = np.log(d['error'])

    per_dv, prepped = {}, {}
    all_teams = sorted(d['u_teamid'].unique())
    for dv in DV_COLS:
        sub = d[d[dv] == 1]
        if len(sub) < 60:
            continue
        g = sub.groupby('u_teamid')
        teams = sorted(g.groups)
        P = g[dec].mean().loc[teams]
        P = P.loc[:, P.std() > 0]
        est = g['AME_Z'].median().loc[teams].values
        lse = g['log_se'].median().loc[teams].values
        Dc = dist(P.values)
        De = np.abs(est[:, None] - est[None, :])
        Ds = np.abs(lse[:, None] - lse[None, :])
        prepped[dv] = dict(teams=teams, est=prep(Dc, De), se=prep(Dc, Ds),
                           n=len(teams), ncols=int(P.shape[1]))

    rng = np.random.default_rng(20260909)
    # per-DV tests
    for dv, pk in prepped.items():
        row = {'n_teams': pk['n'], 'n_decision_cols': pk['ncols']}
        for key in ('est', 'se'):
            RA, RB, iu, ma, sa, mb, sb, m = pk[key]
            obs = stat(RA, RB, np.arange(pk['n']), ma, sa, mb, sb, m)
            null = np.array([stat(RA, RB, rng.permutation(pk['n']), ma, sa, mb, sb, m)
                             for _ in range(NPERM)])
            row[key] = dict(rho=float(obs), null_p95=float(np.percentile(null, 95)),
                            p_one_sided=float((1 + (null >= obs).sum()) / (1 + NPERM)))
        per_dv[dv] = row
        print(f"{dv:8s} n={row['n_teams']:3d}  choices~estimate rho={row['est']['rho']:+.4f} "
              f"(p={row['est']['p_one_sided']:.4f})   choices~log_se rho={row['se']['rho']:+.4f} "
              f"(p={row['se']['p_one_sided']:.4f})")

    # pooled: one permutation of the 72 teams applied to every DV at once
    common = sorted(set.intersection(*[set(p['teams']) for p in prepped.values()]))
    pooled_prep = {}
    for dv, pk in prepped.items():
        idx = [pk['teams'].index(t) for t in common]
        for key in ('est', 'se'):
            RA, RB, iu, ma, sa, mb, sb, m = pk[key]
            RA2 = RA[np.ix_(idx, idx)]; RB2 = RB[np.ix_(idx, idx)]
            pooled_prep[(dv, key)] = prep(RA2, RB2)   # re-rank on the common subset
    nc = len(common)
    rng2 = np.random.default_rng(7)
    res = {}
    for key in ('est', 'se'):
        obs = np.mean([stat(*pooled_prep[(dv, key)][:2], np.arange(nc),
                            *pooled_prep[(dv, key)][3:]) for dv in prepped])
        null = np.empty(NPERM)
        for i in range(NPERM):
            p = rng2.permutation(nc)
            null[i] = np.mean([stat(*pooled_prep[(dv, key)][:2], p,
                                    *pooled_prep[(dv, key)][3:]) for dv in prepped])
        res[key] = dict(mean_rho=float(obs), null_p95=float(np.percentile(null, 95)),
                        p_one_sided=float((1 + (null >= obs).sum()) / (1 + NPERM)),
                        n_common_teams=nc, n_dvs=len(prepped))
        print(f"POOLED {key}: mean rho={obs:+.4f} null95={res[key]['null_p95']:+.4f} "
              f"p={res[key]['p_one_sided']:.4f} over {len(prepped)} DVs, {nc} common teams")
    out = {'per_dv': per_dv, 'pooled': res,
           'note': 'supersedes the model-level numbers in a10_cri_mantel.json and '
                   'a10b_cri_dv_confound.json, which used an invalid block null (a10c)'}
    with open(os.path.join(HERE, '..', 'artifacts', 'a10d_cri_teamlevel_within_dv.json'),
              'w') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()
