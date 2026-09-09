"""A1. Is dissent a stable team trait, or reshuffled at every hypothesis?

NARPS's headline dispersion statistic -- "on average across the 9 hypotheses, 20% of
teams reported a result that differs from the majority" -- is exactly
mean_h min(p_h, 1-p_h) over the nine marginal yes-rates. It is a function of the COLUMN
MARGINS ALONE and is therefore invariant to every rearrangement of which team dissents
where. This script asks the question the headline cannot: are the yes-decisions
clustered within teams?

Test, exact and conditional: permute each hypothesis column independently. That fixes
every column margin (so the published 20%, and every per-hypothesis rate in Table 1, is
identical in every permuted world) and destroys any within-team association. Compare the
observed variance of per-team yes-counts to its permutation distribution.

Confound handled: the nine hypotheses are not independent. H1/H3 and H2/H4 are the SAME
statistical map read in two ROIs; H5/H6 same contrast in the two groups; H7/H8/H9 all
amygdala-loss. Shared maps alone would induce within-team association with no "trait", so
the test is repeated on map-disjoint subsets.
"""
import sys, os, json
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import load

RNG = np.random.default_rng(20260909)
NPERM = 100000


def perm_test(D, nperm=NPERM, rng=RNG):
    """D: teams x hyp binary. Column-wise permutation null."""
    A = D.values.astype(np.int8)
    n, k = A.shape
    obs_var = A.sum(1).var(ddof=1)
    # analytic Poisson-binomial variance of a row sum under independence at column margins
    p = A.mean(0)
    pb_var = float((p * (1 - p)).sum())
    null = np.empty(nperm)
    for i in range(nperm):
        B = np.empty_like(A)
        for j in range(k):
            B[:, j] = rng.permutation(A[:, j])
        null[i] = B.sum(1).var(ddof=1)
    p_val = (1 + (null >= obs_var).sum()) / (1 + nperm)
    return dict(n_teams=n, k_hyp=k, obs_var=float(obs_var),
                poisson_binomial_var=pb_var,
                null_mean=float(null.mean()), null_sd=float(null.std(ddof=1)),
                ratio_obs_over_null_mean=float(obs_var / null.mean()),
                z=float((obs_var - null.mean()) / null.std(ddof=1)),
                p_one_sided=float(p_val), nperm=nperm)


def main():
    D = load.decisions()
    out = {}
    out['all9'] = perm_test(D)

    # map-disjoint subsets. H1/H3 same map, H2/H4 same map.
    # A maximal set with no two sharing a statistical map:
    subsets = {
        'disjoint_A_1_2_5_6_7_8_9': [1, 2, 5, 6, 7, 8, 9],
        'disjoint_B_3_4_5_6_7_8_9': [3, 4, 5, 6, 7, 8, 9],
        # harsher: one hypothesis per experimental contrast family
        'one_per_family_1_5_7': [1, 5, 7],
        'one_per_family_2_6_8': [2, 6, 8],
        'one_per_family_4_5_9': [4, 5, 9],
        # drop the three near-floor amygdala hypotheses entirely
        'no_amygdala_1_2_3_4_5_6': [1, 2, 3, 4, 5, 6],
        'no_amygdala_disjoint_1_2_5_6': [1, 2, 5, 6],
    }
    for name, cols in subsets.items():
        out[name] = perm_test(D[cols], nperm=20000,
                              rng=np.random.default_rng(abs(hash(name)) % 2**31))

    # descriptive: pairwise phi between hypotheses (within-team association)
    C = D.corr()  # pearson on 0/1 == phi
    out['phi_matrix'] = {str(a): {str(b): round(float(C.loc[a, b]), 4) for b in C.columns}
                         for a in C.index}
    offdiag = [float(C.iloc[i, j]) for i in range(9) for j in range(i + 1, 9)]
    out['phi_offdiag_mean'] = float(np.mean(offdiag))
    out['phi_offdiag_median'] = float(np.median(offdiag))
    out['phi_offdiag_min'] = float(np.min(offdiag))
    out['phi_offdiag_max'] = float(np.max(offdiag))
    out['phi_offdiag_frac_positive'] = float(np.mean(np.array(offdiag) > 0))

    print(json.dumps(out, indent=1))
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           '..', 'artifacts', 'a1_team_trait.json'), 'w') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()
