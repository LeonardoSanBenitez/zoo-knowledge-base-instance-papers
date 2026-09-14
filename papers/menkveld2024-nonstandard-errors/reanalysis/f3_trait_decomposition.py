"""F3. Is it the ESTIMATE that is a team trait, or the PRECISION?

F1 found that "this team reports a significant result" is strongly clustered within
teams (variance of per-team counts 3.07x the column-permutation null). But t = estimate
/ standard error, so that clustering could come from either side, and the whole
through-line of this area turns on which.

#fincap is the only corpus here that can separate them, because every one of the 984
team-hypothesis cells carries BOTH numbers. The test is the same one, applied three
times on one scale:

  rank-transform within hypothesis (the six hypotheses are six different quantities on
  six different scales, so nothing may be pooled raw), average each team's six ranks,
  and compare the variance of those team means to a null that permutes team labels
  independently within each hypothesis.

  var ratio ~ 1  -> the quantity is not a team property at all
  var ratio >> 1 -> teams differ systematically in it

Reported for: log(standard error), the estimate, |t|, and the signed t.
"""
import sys, os, json, zlib
import numpy as np
import pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import f0_load

NPERM = 20000


def rank_within(d, col, transform=None):
    W = d.pivot(index='team', columns='hyp', values=col)
    if transform is not None:
        W = W.apply(transform)
    R = W.apply(lambda c: stats.rankdata(c) / (len(c) + 1), axis=0)
    return R


def var_ratio(R, nperm=NPERM, seed=0):
    A = R.values.astype(float)
    n, k = A.shape
    obs = A.mean(1).var(ddof=1)
    rng = np.random.default_rng(seed)
    null = np.empty(nperm)
    for i in range(nperm):
        B = np.empty_like(A)
        for j in range(k):
            B[:, j] = rng.permutation(A[:, j])
        null[i] = B.mean(1).var(ddof=1)
    return dict(n_teams=n, k=k, obs_var=float(obs), null_mean=float(null.mean()),
                ratio=float(obs / null.mean()),
                z=float((obs - null.mean()) / null.std(ddof=1)),
                p_one_sided=float((1 + (null >= obs).sum()) / (1 + nperm)),
                icc_like=float(1 - null.mean() / obs) if obs > 0 else None)


def main():
    d = f0_load.results()
    out = {}
    for stage in [1, 4]:
        s = d[d.stage == stage]
        for label, col, tr in [
                ('log_standard_error', 'se', lambda c: np.log(c.clip(lower=1e-12))),
                ('estimate', 'estimate', None),
                ('abs_t', 't_value', lambda c: c.abs()),
                ('signed_t', 't_value', None)]:
            R = rank_within(s, col, tr)
            # zlib.crc32, not hash(): Python's str hash() is randomised per
            # process (PYTHONHASHSEED) unless disabled, so this seed silently
            # differed run to run -- caught 2026-09-14 re-running the script a
            # session later and getting a different 4th-decimal ratio. The
            # conclusions never moved (noise is ~0.001-0.005 on ratios of
            # 1.2-4.5), but "seed=" that isn't one defeats the point of a seed.
            r = var_ratio(R, seed=zlib.crc32(label.encode()) % 997 + stage)
            out[f'stage{stage}__{label}'] = r
            print(f"stage {stage}  {label:20s} var ratio = {r['ratio']:6.3f}  "
                  f"z = {r['z']:7.2f}  p = {r['p_one_sided']:.5f}  "
                  f"between-team share = {r['icc_like']:.3f}")
        print()
    # and the direct question: does a team's precision rank predict its significance?
    s = d[d.stage == 1]
    Rse = rank_within(s, 'se', lambda c: np.log(c.clip(lower=1e-12)))
    W = s.pivot(index='team', columns='hyp', values='t_value')
    sig = (W.abs() > 1.96).astype(int)
    a = Rse.mean(1).values
    b = sig.sum(1).values
    rho = stats.spearmanr(a, b)
    out['spearman_meanSErank_vs_nsignificant'] = dict(
        rho=float(rho.statistic), p=float(rho.pvalue), n=len(a))
    Rest = rank_within(s, 'estimate', lambda c: c.abs())
    rho2 = stats.spearmanr(Rest.mean(1).values, b)
    out['spearman_meanABSestimaterank_vs_nsignificant'] = dict(
        rho=float(rho2.statistic), p=float(rho2.pvalue), n=len(a))
    print(f"team mean rank of log(SE)        vs number of significant results: "
          f"rho = {rho.statistic:+.3f} (p = {rho.pvalue:.2e})")
    print(f"team mean rank of |estimate|     vs number of significant results: "
          f"rho = {rho2.statistic:+.3f} (p = {rho2.pvalue:.2e})")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                           'artifacts', 'f3_trait_decomposition.json'), 'w') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()


def main_scale():
    """The confound that has to be killed before F3 means anything.

    If two teams express the same result in different UNITS -- basis points against
    percent, raw against logged -- their estimate and their standard error both move by
    the same factor and their t is unchanged. Then a large between-team share for
    log(SE) would be a fact about units, not about precision.

    Three checks:
      (1) log|estimate| should show the same between-team share as log(SE) if units are
          doing the work;
      (2) the two team-level ranks should be nearly perfectly correlated in that case;
      (3) |t| = |estimate| / SE is scale-free by construction, so whatever between-team
          structure survives in it cannot be units.
    """
    import json as _json
    d = f0_load.results()
    out = {}
    for stage in [1, 4]:
        s = d[d.stage == stage]
        Rse = rank_within(s, 'se', lambda c: np.log(c.clip(lower=1e-12)))
        Rest = rank_within(s, 'estimate', lambda c: np.log(c.abs().clip(lower=1e-12)))
        Rt = rank_within(s, 't_value', lambda c: c.abs())
        for label, R in [('log_SE', Rse), ('log_abs_estimate', Rest), ('abs_t', Rt)]:
            r = var_ratio(R, seed=stage * 7 + len(label))
            out[f'stage{stage}__{label}'] = r
            print(f"stage {stage}  {label:18s} var ratio {r['ratio']:6.3f}  "
                  f"between-team share {r['icc_like']:.3f}")
        rho = stats.spearmanr(Rse.mean(1), Rest.mean(1))
        out[f'stage{stage}__spearman_teamrank_logSE_vs_logAbsEstimate'] = dict(
            rho=float(rho.statistic), p=float(rho.pvalue))
        print(f"stage {stage}  team mean rank log(SE) vs log|estimate|: "
              f"rho = {rho.statistic:+.3f}")
        # partial: does log(SE) still separate teams once |estimate| is held?
        resid = Rse.values - Rest.values
        Rres = pd.DataFrame(resid, index=Rse.index, columns=Rse.columns)
        r = var_ratio(Rres, seed=stage * 13)
        out[f'stage{stage}__logSE_minus_logAbsEstimate'] = r
        print(f"stage {stage}  rank(log SE) - rank(log|est|)  var ratio {r['ratio']:6.3f}"
              f"  between-team share {r['icc_like']:.3f}")
        print()
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                           'artifacts', 'f3b_scale_confound.json'), 'w') as f:
        _json.dump(out, f, indent=1)
