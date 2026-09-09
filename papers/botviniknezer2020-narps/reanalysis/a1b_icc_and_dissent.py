"""A1b. How big is the team trait, in units anyone can read?

A1 established over-dispersion (variance of per-team yes-counts 2.26x the
column-permutation null, p<1e-4). This converts it into three interpretable forms:

 1. beta-binomial / logit-normal random-intercept SD and the latent-scale ICC;
 2. concentration: what share of all 140 dissenting decisions is contributed by the
    most dissenting quartile of teams, observed vs the same permutation null;
 3. the counterfactual NARPS's headline cannot see: how much would the reported
    "20% of teams differ from the majority" change if the team trait were removed?
    (Answer by construction: not at all. That is the point -- it is the same 20% in
    every permuted world, which is why the statistic cannot distinguish the two.)
"""
import sys, os, json
import numpy as np
import pandas as pd
from scipy import optimize, special
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import load

NPERM = 20000


def _gh(n=60):
    from numpy.polynomial.hermite import hermgauss
    x, w = hermgauss(n)
    return x, w / np.sqrt(np.pi)


def nll_joint(params, Y):
    """params = [a_1..a_k, log sigma]. Random intercept per team ~ N(0, sigma^2),
    integrated by 60-point Gauss-Hermite. Fixed effects estimated JOINTLY with sigma
    (estimating them from the raw margins and holding them fixed would bias sigma)."""
    k = Y.shape[1]
    a = params[:k]
    s = np.exp(params[k])
    x, w = _gh()
    b = np.sqrt(2) * s * x
    eta = a[None, :] + b[:, None]              # (G, k)
    lp1 = -np.logaddexp(0, -eta)               # log p
    lp0 = -np.logaddexp(0, eta)                # log(1-p)
    ll = 0.0
    for i in range(Y.shape[0]):
        lpi = Y[i][None, :] @ lp1.T + (1 - Y[i])[None, :] @ lp0.T   # (1,G)
        ll += special.logsumexp(lpi.ravel() + np.log(w))
    return -ll


def fit_sigma(Y, fix_sigma_zero=False):
    k = Y.shape[1]
    p = np.clip(Y.mean(0), 1e-3, 1 - 1e-3)
    a0 = np.log(p / (1 - p))
    if fix_sigma_zero:
        return 0.0, float(nll_joint(np.r_[a0, np.log(1e-8)], Y))
    x0 = np.r_[a0, np.log(0.8)]
    r = optimize.minimize(nll_joint, x0, args=(Y,), method='Nelder-Mead',
                          options=dict(maxiter=20000, maxfev=20000,
                                       xatol=1e-6, fatol=1e-8))
    return float(np.exp(r.x[k])), float(r.fun)


def selftest(nrep=8):
    """Break it before believing it: simulate at known sigma and check recovery."""
    rng = np.random.default_rng(3)
    a = np.array([-0.5, -1.3, -1.2, -0.7, 1.7, -0.7, -2.8, -2.8, -2.8])
    res = {}
    for true_s in [0.0, 0.5, 1.0]:
        est = []
        for _ in range(nrep):
            b = rng.normal(0, true_s, 70)
            p = special.expit(a[None, :] + b[:, None])
            Y = (rng.random(p.shape) < p).astype(float)
            est.append(fit_sigma(Y)[0])
        res[str(true_s)] = dict(mean=float(np.mean(est)), sd=float(np.std(est, ddof=1)),
                                values=[round(e, 3) for e in est])
    return res


def main():
    D = load.decisions()
    Y = D.values.astype(float)
    n, k = Y.shape
    out = {'n_teams': n, 'k_hyp': k}

    out['selftest_sigma_recovery'] = selftest()
    print('selftest:', json.dumps(out['selftest_sigma_recovery']))
    s, nll = fit_sigma(Y)
    _, nll0 = fit_sigma(Y, fix_sigma_zero=True)
    out['random_intercept_sd_logit'] = s
    out['nll_with_random_intercept'] = nll
    out['nll_sigma_zero'] = float(nll0)
    out['lrt_chi2'] = float(2 * (nll0 - nll))
    out['latent_icc'] = float(s ** 2 / (s ** 2 + np.pi ** 2 / 3))
    # odds-ratio between a team 1 SD above and 1 SD below the mean propensity
    out['odds_ratio_plus1sd_vs_minus1sd'] = float(np.exp(2 * s))

    # concentration of dissent
    maj = (Y.mean(0) > 0.5).astype(float)
    dis = (Y != maj[None, :]).astype(int)
    per_team = dis.sum(1)
    out['total_dissenting_decisions'] = int(dis.sum())
    out['mean_dissent_rate'] = float(dis.mean())
    q = int(np.ceil(n / 4))
    top_share = np.sort(per_team)[::-1][:q].sum() / dis.sum()
    rng = np.random.default_rng(4242)
    null_share = np.empty(NPERM)
    null_zero = np.empty(NPERM)
    for i in range(NPERM):
        B = np.empty_like(Y)
        for j in range(k):
            B[:, j] = rng.permutation(Y[:, j])
        d = (B != maj[None, :]).astype(int)
        pt = d.sum(1)
        null_share[i] = np.sort(pt)[::-1][:q].sum() / d.sum()
        null_zero[i] = (pt == 0).mean()
    out['top_quartile_share_of_dissent'] = float(top_share)
    out['top_quartile_share_null_mean'] = float(null_share.mean())
    out['top_quartile_share_null_p95'] = float(np.percentile(null_share, 95))
    out['top_quartile_share_p'] = float((1 + (null_share >= top_share).sum()) / (1 + NPERM))
    out['frac_teams_never_dissenting'] = float((per_team == 0).mean())
    out['frac_teams_never_dissenting_null_mean'] = float(null_zero.mean())
    out['frac_teams_never_dissenting_p'] = float(
        (1 + (null_zero >= (per_team == 0).mean()).sum()) / (1 + NPERM))
    out['max_dissent_by_a_team'] = int(per_team.max())
    out['dissent_count_distribution'] = {str(int(v)): int(c) for v, c in
                                         zip(*np.unique(per_team, return_counts=True))}
    # the invariance claim, verified rather than asserted
    marg = Y.mean(0)
    out['headline_20pct_from_margins'] = float(np.mean(np.minimum(marg, 1 - marg)))
    B = np.empty_like(Y)
    rng2 = np.random.default_rng(1)
    for j in range(k):
        B[:, j] = rng2.permutation(Y[:, j])
    out['headline_20pct_after_permutation'] = float(
        np.mean(np.minimum(B.mean(0), 1 - B.mean(0))))
    print(json.dumps(out, indent=1))
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                           'artifacts', 'a1b_icc_and_dissent.json'), 'w') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()
