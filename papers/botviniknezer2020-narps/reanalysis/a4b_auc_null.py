"""A4b. Does map similarity carry ANY information about decision agreement?

The 14,112 team-pairs in A4 are not independent -- they come from 64 teams. The exact
conditional test is at the team level: permute which team holds which decision, within a
hypothesis. That fixes the marginal yes-rate (so Table 1 is unchanged in every permuted
world) and destroys any link between a team's map and its decision, while leaving the
whole correlation matrix untouched.

Statistic: AUC of pairwise map-correlation predicting pairwise decision agreement.
Also reported: disagreement rate among pairs with r >= 0.8, same null.
"""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import load
from a4_threshold_vs_estimate import auc

HYPS = [1, 2, 5, 6, 7, 8, 9]
NPERM = 20000


def stats_for(dec, r, iu, thr=0.8):
    agree = (dec[iu[0]] == dec[iu[1]]).astype(int)
    m = r >= thr
    return auc(r, agree), (float(1 - agree[m].mean()) if m.sum() else np.nan)


def main():
    D = load.decisions()
    out = {'nperm': NPERM, 'per_hypothesis': {}}
    for h in HYPS:
        C = load.unthresh_corr(h)
        teams = [t for t in C.index if t in D.index]
        C = C.loc[teams, teams]
        dec = D.loc[teams, h].values.astype(int)
        n = len(teams)
        iu = np.triu_indices(n, 1)
        r = C.values[iu].astype(float)
        obs_auc, obs_dis = stats_for(dec, r, iu)
        rng = np.random.default_rng(1000 + h)
        na, nd = np.empty(NPERM), np.empty(NPERM)
        for i in range(NPERM):
            d = rng.permutation(dec)
            na[i], nd[i] = stats_for(d, r, iu)
        p_two = (1 + min((na >= obs_auc).sum(), (na <= obs_auc).sum()) * 2) / (1 + NPERM)
        out['per_hypothesis'][h] = dict(
            n_teams=n, n_yes=int(dec.sum()), p_yes=float(dec.mean()),
            n_pairs_r_ge_08=int((r >= 0.8).sum()),
            obs_auc=float(obs_auc),
            null_auc_mean=float(na.mean()), null_auc_sd=float(na.std(ddof=1)),
            null_auc_p2_5=float(np.percentile(na, 2.5)),
            null_auc_p97_5=float(np.percentile(na, 97.5)),
            p_two_sided_auc=float(min(1.0, p_two)),
            obs_disagreement_r_ge_08=None if np.isnan(obs_dis) else float(obs_dis),
            null_disagreement_mean=float(np.nanmean(nd)),
            null_disagreement_p2_5=float(np.nanpercentile(nd, 2.5)),
            null_disagreement_p97_5=float(np.nanpercentile(nd, 97.5)),
        )
        v = out['per_hypothesis'][h]
        print(f"h{h}: AUC={v['obs_auc']:.3f} null={v['null_auc_mean']:.3f} "
              f"[{v['null_auc_p2_5']:.3f},{v['null_auc_p97_5']:.3f}] p={v['p_two_sided_auc']:.4f} | "
              f"disagree(r>=.8) obs={v['obs_disagreement_r_ge_08']} "
              f"null={v['null_disagreement_mean']:.3f} "
              f"[{v['null_disagreement_p2_5']:.3f},{v['null_disagreement_p97_5']:.3f}] "
              f"npairs={v['n_pairs_r_ge_08']}")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                           'artifacts', 'a4b_auc_null.json'), 'w') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()
