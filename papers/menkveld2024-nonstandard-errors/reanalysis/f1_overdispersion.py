"""F1. Is "reports a significant result" a stable team trait in #fincap too?

The NARPS test, transplanted without modification: binarise each team's result for each
hypothesis, permute every hypothesis column independently (which fixes each hypothesis's
significant-rate exactly), and compare the variance of per-team significant-counts to its
permutation distribution.

#fincap is a better setting than NARPS in one way and worse in another. Better: 164 teams
instead of 70, a balanced panel with no attrition, and six hypotheses that are six
DIFFERENT market-quality measures rather than nine of which four share a statistical map.
Worse: significance here is our binarisation of a t-value, not the team's own reported
yes/no, so it is a slightly different object.
"""
import sys, os, json
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import f0_load

NPERM = 100000


def perm_test(D, nperm=NPERM, seed=0):
    A = D.values.astype(np.int8)
    n, k = A.shape
    obs = A.sum(1).var(ddof=1)
    p = A.mean(0)
    rng = np.random.default_rng(seed)
    null = np.empty(nperm)
    for i in range(nperm):
        B = np.empty_like(A)
        for j in range(k):
            B[:, j] = rng.permutation(A[:, j])
        null[i] = B.sum(1).var(ddof=1)
    return dict(n_teams=n, k=k, obs_var=float(obs),
                poisson_binomial_var=float((p * (1 - p)).sum()),
                null_mean=float(null.mean()), null_sd=float(null.std(ddof=1)),
                ratio=float(obs / null.mean()),
                z=float((obs - null.mean()) / null.std(ddof=1)),
                p_one_sided=float((1 + (null >= obs).sum()) / (1 + nperm)),
                marginals=[round(float(x), 4) for x in p],
                mean_distance_from_consensus=float(np.mean(np.minimum(p, 1 - p))))


def main():
    d = f0_load.results()
    out = {}
    for rule, fn in [('two_sided_abs_t_gt_1.96', lambda t: (t.abs() > 1.96)),
                     ('one_sided_t_gt_1.645', lambda t: (t > 1.645)),
                     ('two_sided_abs_t_gt_2.576', lambda t: (t.abs() > 2.576))]:
        for stage in [1, 2, 3, 4]:
            s = d[d.stage == stage]
            W = s.pivot(index='team', columns='hyp', values='t_value')
            B = fn(W).astype(int)
            r = perm_test(B, nperm=20000 if stage > 1 else NPERM, seed=stage)
            out[f'{rule}__stage{stage}'] = r
            print(f"{rule:26s} stage {stage}: n={r['n_teams']} k={r['k']} "
                  f"obs_var={r['obs_var']:.3f} null={r['null_mean']:.3f} "
                  f"ratio={r['ratio']:.3f} z={r['z']:.2f} p={r['p_one_sided']:.5f} "
                  f"| mean dist from consensus {r['mean_distance_from_consensus']:.3f}")
        print()
    # phi matrix between hypotheses at stage 1, two-sided rule
    s = d[d.stage == 1]
    W = s.pivot(index='team', columns='hyp', values='t_value')
    B = (W.abs() > 1.96).astype(int)
    C = B.corr()
    off = [float(C.iloc[i, j]) for i in range(6) for j in range(i + 1, 6)]
    out['phi_offdiag'] = dict(mean=float(np.mean(off)), median=float(np.median(off)),
                              min=float(np.min(off)), max=float(np.max(off)),
                              frac_positive=float(np.mean(np.array(off) > 0)))
    print('between-hypothesis phi (stage 1):', json.dumps(out['phi_offdiag']))
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                           'artifacts', 'f1_overdispersion.json'), 'w') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()
