"""F5. The finding that has to be attacked before it is believed.

F4: across #fincap's four stages the IQR of the ESTIMATES falls to 0.494 of its stage-1
value while the IQR of the T-VALUES rises to 1.347 of its stage-1 value, because the
standard errors converge far harder than the estimates (SE IQR ratio 0.173).

Since t decides whether a team reports a finding, that says the intervention reported as
cutting nonstandard errors by 47% widened disagreement about the conclusion by a third.
Before believing it:

  A. LOCATION. If |t| simply got bigger -- teams converging on a better-powered
     specification -- its IQR would grow with it and mean nothing. Report the location
     alongside, and a scale-free ratio IQR(t)/median|t|.
  B. NOISE. Six hypotheses is few. Bootstrap teams (paired: a team keeps all four of its
     stage values) and report an interval for each ratio.
  C. DECISION TERMS. Dispersion of t is a proxy. The thing itself is the spread of
     "reports a significant result" across teams -- report the significant-rate per
     stage and the mean distance from consensus.
  D. DIRECTION. Is it the same teams moving, or churn? Report the rank correlation of
     team t between stage 1 and stage 4.
"""
import sys, os, json
import numpy as np
import pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import f0_load

NBOOT = 10000


def iqr(x):
    return float(np.percentile(x, 75) - np.percentile(x, 25))


def main():
    d = f0_load.results()
    out = {}
    print('A. location and scale of |t| and t, per hypothesis and stage')
    print(f"{'hyp':>3} {'stage':>5} {'median|t|':>10} {'IQR(t)':>10} "
          f"{'IQR(t)/med|t|':>14} {'pct |t|>1.96':>13}")
    loc = {}
    for h in range(1, 7):
        for st in [1, 2, 3, 4]:
            t = d[(d.hyp == h) & (d.stage == st)]['t_value'].values
            m = float(np.median(np.abs(t)))
            loc[(h, st)] = dict(median_abs_t=m, iqr_t=iqr(t),
                                scale_free=iqr(t) / m if m else np.nan,
                                pct_sig=float((np.abs(t) > 1.96).mean()))
            if st in (1, 4):
                v = loc[(h, st)]
                print(f"{h:3d} {st:5d} {v['median_abs_t']:10.3f} {v['iqr_t']:10.3f} "
                      f"{v['scale_free']:14.3f} {100*v['pct_sig']:12.1f}%")
    out['location'] = {f'h{h}_s{s}': v for (h, s), v in loc.items()}
    sf = [loc[(h, 4)]['scale_free'] / loc[(h, 1)]['scale_free'] for h in range(1, 7)]
    med_abs = [loc[(h, 4)]['median_abs_t'] / loc[(h, 1)]['median_abs_t'] for h in range(1, 7)]
    out['scale_free_iqr_ratio_s4_over_s1'] = dict(
        per_hyp=[round(float(x), 4) for x in sf], median=float(np.median(sf)))
    out['median_abs_t_ratio_s4_over_s1'] = dict(
        per_hyp=[round(float(x), 4) for x in med_abs], median=float(np.median(med_abs)))
    print(f"\n  median|t| ratio s4/s1 per hyp: {[round(x,3) for x in med_abs]}  "
          f"median {np.median(med_abs):.3f}")
    print(f"  scale-free IQR(t)/median|t| ratio s4/s1: {[round(x,3) for x in sf]}  "
          f"median {np.median(sf):.3f}")

    print('\nB. paired team bootstrap of the stage-4/stage-1 IQR ratio')
    rng = np.random.default_rng(202609)
    teams = sorted(d.team.unique())
    piv = {(h, c): d[d.hyp == h].pivot(index='team', columns='stage', values=c)
           for h in range(1, 7) for c in ['estimate', 'se', 't_value']}
    res = {}
    for c in ['estimate', 'se', 't_value']:
        meds = np.empty(NBOOT)
        for b in range(NBOOT):
            idx = rng.integers(0, len(teams), len(teams))
            r = []
            for h in range(1, 7):
                W = piv[(h, c)].values[idx]
                a1 = iqr(W[:, 0]); a4 = iqr(W[:, 3])
                r.append(a4 / a1 if a1 else np.nan)
            meds[b] = np.nanmedian(r)
        lo, hi = np.percentile(meds, [2.5, 97.5])
        obs = np.median([iqr(piv[(h, c)].values[:, 3]) / iqr(piv[(h, c)].values[:, 0])
                         for h in range(1, 7)])
        res[c] = dict(obs=float(obs), ci_low=float(lo), ci_high=float(hi),
                      frac_above_1=float((meds > 1).mean()))
        print(f"  {c:10s} median IQR ratio {obs:.3f}  95% CI [{lo:.3f}, {hi:.3f}]  "
              f"P(ratio>1) = {(meds > 1).mean():.3f}")
    out['bootstrap_median_iqr_ratio'] = res

    print('\nC. in decision terms')
    out['decision'] = {}
    for st in [1, 2, 3, 4]:
        s = d[d.stage == st]
        W = s.pivot(index='team', columns='hyp', values='t_value')
        B = (W.abs() > 1.96)
        p = B.mean(0).values
        cnt = B.sum(1).values
        out['decision'][f'stage{st}'] = dict(
            sig_rate_per_hyp=[round(float(x), 4) for x in p],
            mean_sig_rate=float(p.mean()),
            mean_distance_from_consensus=float(np.mean(np.minimum(p, 1 - p))),
            sd_of_team_counts=float(cnt.std(ddof=1)))
        v = out['decision'][f'stage{st}']
        print(f"  stage {st}: mean significant rate {v['mean_sig_rate']:.3f}  "
              f"mean distance from consensus {v['mean_distance_from_consensus']:.3f}  "
              f"SD of per-team counts {v['sd_of_team_counts']:.3f}")

    print('\nD. is it the same teams? rank correlation of t between stage 1 and 4')
    out['stability'] = {}
    for h in range(1, 7):
        W = piv[(h, 't_value')]
        r1 = stats.spearmanr(W[1], W[4])
        We = piv[(h, 'estimate')]
        r2 = stats.spearmanr(We[1], We[4])
        Ws = piv[(h, 'se')]
        r3 = stats.spearmanr(Ws[1], Ws[4])
        out['stability'][f'h{h}'] = dict(t=float(r1.statistic), estimate=float(r2.statistic),
                                         se=float(r3.statistic))
        print(f"  h{h}: t {r1.statistic:+.3f}   estimate {r2.statistic:+.3f}   "
              f"se {r3.statistic:+.3f}")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                           'artifacts', 'f5_t_divergence.json'), 'w') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()
