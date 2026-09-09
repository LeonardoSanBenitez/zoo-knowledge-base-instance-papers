"""A10c. A defect in my own null, found by checking it instead of trusting it.

`mantel_fast(..., blocks=teams)` was written to permute WHOLE TEAMS so that models stay
with their team. It does that only when every team has the same number of models. The
implementation lines up two position lists --

    src = concat(positions of team u, for u in sorted(teams))
    dst = concat(positions of team u, for u in a permuted team order)
    p[src] = dst

-- element by element. With unequal team sizes the k-th element of the two lists belongs
to different teams, so a team's models are scattered across several position blocks and
the null no longer preserves the within-team / between-team structure of the pairs. That
makes within-team pairs in the CHOICE matrix line up against between-team pairs in the
RESPONSE matrix, which inflates significance.

This script measures the damage rather than asserting it: it counts, over draws from the
null, the fraction of pairs that keep their within-team status.

CONSEQUENCE: the model-level CRI numbers in a10_cri_mantel.json and a10b_cri_dv_confound.json
are WITHDRAWN. The team-level numbers in the same files are unaffected -- there every unit
is one team and no blocks are used.
"""
import sys, os, json
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
CRI = os.path.join(HERE, '..', '..', 'breznau2022-hidden-universe', 'data')


def main():
    d = pd.read_csv(os.path.join(CRI, 'cri_model_level.csv'))
    d = d[np.isfinite(d['AME_Z']) & np.isfinite(d['error']) & (d['error'] > 0)].reset_index(drop=True)
    teams = d['u_teamid'].values
    sizes = pd.Series(teams).value_counts()
    out = {'n_models': int(len(d)), 'n_teams': int(sizes.size),
           'team_size_min': int(sizes.min()), 'team_size_max': int(sizes.max()),
           'team_size_median': float(sizes.median()),
           'all_teams_same_size': bool(sizes.nunique() == 1)}
    n = len(teams)
    same = (teams[:, None] == teams[None, :])
    iu = np.triu_indices(n, 1)
    same_u = same[iu]
    u = np.unique(teams)
    pos = [np.where(teams == g)[0] for g in u]
    src = np.concatenate(pos)
    rng = np.random.default_rng(0)
    keep = []
    for _ in range(200):
        order = rng.permutation(len(u))
        dst = np.concatenate([pos[j] for j in order])
        p = np.empty(n, int); p[src] = dst
        permuted_same = same[np.ix_(p, p)][iu]
        keep.append(float((permuted_same == same_u).mean()))
        # the number that matters: of the pairs that WERE within-team, how many still are
    keep_within = []
    for _ in range(200):
        order = rng.permutation(len(u))
        dst = np.concatenate([pos[j] for j in order])
        p = np.empty(n, int); p[src] = dst
        permuted_same = same[np.ix_(p, p)][iu]
        keep_within.append(float(permuted_same[same_u].mean()))
    out['frac_pairs_keeping_within_status'] = float(np.mean(keep))
    out['frac_withinteam_pairs_still_withinteam'] = float(np.mean(keep_within))
    out['ideal_value_if_null_were_correct'] = 1.0
    print(json.dumps(out, indent=1))
    with open(os.path.join(HERE, '..', 'artifacts', 'a10c_block_null_bug.json'), 'w') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()
