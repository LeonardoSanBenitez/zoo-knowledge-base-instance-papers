"""F2. The peer-feedback result, which this record has carried as `unverified` since
2026-08-25 because pages 2351-2390 could not be obtained, and which I flagged as having
the shape of a multiple-comparisons artifact read backwards.

Menkveld et al. report that across the four stages the nonstandard error falls 47.2% and
the interdecile range 68.2%, with no single stage significant on its own.

Now checkable. NSE is defined in the paper as the interquartile range of estimates across
teams; the six hypotheses are on six different scales so everything is computed per
hypothesis and only ratios are aggregated.

Alternatives this tests, decided before looking:
  (a) attrition -- ALREADY DEAD, the panel is balanced at 164 teams in all four stages;
  (b) is the fall monotone across stages, or one step?
  (c) does it survive a non-robust measure (SD) and a more robust one (MAD)? With
      estimates ranging to +/- 6 million, the choice of measure is load-bearing;
  (d) is it dispersion falling, or outliers being pulled in? Compare the change in the
      IQR with the change in the interdecile range and in the SD.
"""
import sys, os, json
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import f0_load

NBOOT = 10000


def spreads(x):
    x = np.asarray(x, float)
    q = np.percentile(x, [10, 25, 50, 75, 90])
    return dict(iqr=float(q[3] - q[1]), idr=float(q[4] - q[0]),
                sd=float(x.std(ddof=1)),
                mad=float(np.median(np.abs(x - np.median(x)))),
                nse=float((q[3] - q[1]) / 1.349),
                median=float(q[2]), n=int(len(x)))


def main():
    d = f0_load.results()
    rows = []
    for (h, st), g in d.groupby(['hyp', 'stage']):
        s = spreads(g['estimate'].values)
        s.update(hyp=int(h), stage=int(st))
        rows.append(s)
        st2 = spreads(g['t_value'].values)
        rows.append(dict(st2, hyp=int(h), stage=int(st), _t=True))
    est = pd.DataFrame([r for r in rows if not r.get('_t')])
    tv = pd.DataFrame([r for r in rows if r.get('_t')])

    out = {'per_hypothesis_estimate_spreads':
           est.set_index(['hyp', 'stage'])[['iqr', 'idr', 'sd', 'mad', 'nse']]
              .round(4).reset_index().to_dict('records')}

    print('ESTIMATES -- ratio of each stage to stage 1, per hypothesis')
    print(f"{'measure':6s} " + ''.join(f"{'h%d' % h:>9s}" for h in range(1, 7)) +
          "   median   geomean")
    for meas in ['iqr', 'idr', 'sd', 'mad']:
        for stage in [2, 3, 4]:
            r = []
            for h in range(1, 7):
                a = est[(est.hyp == h) & (est.stage == 1)][meas].iloc[0]
                b = est[(est.hyp == h) & (est.stage == stage)][meas].iloc[0]
                r.append(b / a if a else np.nan)
            r = np.array(r)
            out[f'ratio_stage{stage}_over_1__{meas}'] = dict(
                per_hyp=[round(float(x), 4) for x in r],
                median=float(np.median(r)),
                geomean=float(np.exp(np.mean(np.log(r)))),
                pct_change_median=float(100 * (np.median(r) - 1)))
            print(f"{meas:4s} s{stage} " + ''.join(f"{x:9.3f}" for x in r) +
                  f"   {np.median(r):6.3f}  {np.exp(np.mean(np.log(r))):7.3f}")
        print()

    print('T-VALUES -- same')
    for meas in ['iqr', 'idr', 'sd']:
        for stage in [4]:
            r = []
            for h in range(1, 7):
                a = tv[(tv.hyp == h) & (tv.stage == 1)][meas].iloc[0]
                b = tv[(tv.hyp == h) & (tv.stage == stage)][meas].iloc[0]
                r.append(b / a if a else np.nan)
            r = np.array(r)
            out[f'tvalue_ratio_stage4_over_1__{meas}'] = dict(
                per_hyp=[round(float(x), 4) for x in r], median=float(np.median(r)))
            print(f"{meas:4s} s{stage} " + ''.join(f"{x:9.3f}" for x in r) +
                  f"   {np.median(r):6.3f}")

    # bootstrap the stage-4/stage-1 IQR ratio, resampling TEAMS (paired: a team keeps
    # both of its stage values)
    rng = np.random.default_rng(11)
    teams = sorted(d.team.unique())
    piv = {h: d[(d.hyp == h)].pivot(index='team', columns='stage', values='estimate')
           for h in range(1, 7)}
    boot = {h: [] for h in range(1, 7)}
    for _ in range(NBOOT):
        idx = rng.integers(0, len(teams), len(teams))
        for h in range(1, 7):
            W = piv[h].values[idx]
            a = np.percentile(W[:, 0], 75) - np.percentile(W[:, 0], 25)
            b = np.percentile(W[:, 3], 75) - np.percentile(W[:, 3], 25)
            boot[h].append(b / a if a else np.nan)
    print('\npaired team bootstrap of the stage-4 / stage-1 IQR ratio:')
    out['bootstrap_iqr_ratio_stage4_over_1'] = {}
    for h in range(1, 7):
        v = np.array(boot[h]); v = v[np.isfinite(v)]
        lo, hi = np.percentile(v, [2.5, 97.5])
        obs = out['ratio_stage4_over_1__iqr']['per_hyp'][h - 1]
        out['bootstrap_iqr_ratio_stage4_over_1'][str(h)] = dict(
            obs=obs, ci_low=float(lo), ci_high=float(hi),
            frac_below_1=float((v < 1).mean()))
        print(f"  h{h}: {obs:.3f}  [{lo:.3f}, {hi:.3f}]  "
              f"P(ratio<1) = {(v < 1).mean():.3f}")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                           'artifacts', 'f2_stage_effect.json'), 'w') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()
