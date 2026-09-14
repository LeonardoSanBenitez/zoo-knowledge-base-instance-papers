"""F4. Check the two #fincap numbers this record has been quoting since 2026-08-12
against the deposit, and diagnose the two surprises in F2.

Quoted in NOTES.md, derived when only pages 2339-2350 were obtainable:
    #fincap RT-H1  tau / median SE = 1.72     (tau = sqrt((IQR/1.349)^2 - medianSE^2))
    #fincap RT-H1  IDR / IQR       = 4.07     (Gaussian reference 1.90)

Two things F2 turned up that need explaining rather than reporting:
  (i) the SD of the estimates is EXACTLY unchanged across stages for h1, h2 and h4
      (ratio 1.000). An SD that does not move at three decimal places is one
      observation, not a distribution.
  (ii) the dispersion of the ESTIMATES falls by half across the four stages while the
      dispersion of the T-VALUES rises. Since t = estimate / SE, that has to be visible
      in the SEs.
"""
import sys, os, json
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import f0_load

GAUSS = 2 * 1.2815515655446004 / (2 * 0.6744897501960817)


def main():
    d = f0_load.results()
    out = {'gaussian_idr_over_iqr': GAUSS}
    print('per hypothesis, STAGE 1 (the stage a single-shot study corresponds to):')
    print(f"{'hyp':>3} {'IQR':>12} {'medianSE':>12} {'tau':>12} {'tau/medSE':>10} "
          f"{'IDR/IQR':>8} {'n':>5}")
    for h in range(1, 7):
        g = d[(d.hyp == h) & (d.stage == 1)]
        est = g['estimate'].values
        q25, q75 = np.percentile(est, [25, 75])
        p10, p90 = np.percentile(est, [10, 90])
        iqr = q75 - q25
        idr = p90 - p10
        med_se = float(np.median(g['se'].values))
        inner = (iqr / 1.349) ** 2 - med_se ** 2
        tau = float(np.sqrt(inner)) if inner > 0 else float('nan')
        out[f'hyp{h}_stage1'] = dict(iqr=float(iqr), idr=float(idr),
                                     median_se=med_se, tau=tau,
                                     tau_over_median_se=float(tau / med_se),
                                     idr_over_iqr=float(idr / iqr), n=int(len(est)))
        print(f"{h:3d} {iqr:12.4f} {med_se:12.4f} {tau:12.4f} "
              f"{tau/med_se:10.3f} {idr/iqr:8.3f} {len(est):5d}")
    print(f"\nrecorded in NOTES.md for 'RT-H1': tau/medianSE = 1.72, IDR/IQR = 4.07")

    # (i) how much of the SD is one team?
    print('\nshare of the total sum of squares carried by the single most extreme team:')
    out['sd_concentration'] = {}
    for h in range(1, 7):
        for st in [1, 4]:
            g = d[(d.hyp == h) & (d.stage == st)]
            x = g['estimate'].values
            ss = (x - x.mean()) ** 2
            top1 = float(ss.max() / ss.sum())
            top5 = float(np.sort(ss)[-5:].sum() / ss.sum())
            out['sd_concentration'][f'h{h}_s{st}'] = dict(top1=top1, top5=top5,
                                                          argmax_team=str(g.iloc[int(ss.argmax())]['team']))
            if st == 1:
                print(f"  h{h}: stage1 top-1 = {top1:.3f}, top-5 = {top5:.3f} "
                      f"(team {g.iloc[int(ss.argmax())]['team']})", end='')
            else:
                print(f"   | stage4 top-1 = {top1:.3f} "
                      f"(team {g.iloc[int(ss.argmax())]['team']})")

    # (ii) dispersion of the SEs across stages
    print('\ndispersion across teams, stage 4 / stage 1 (median over the 6 hypotheses):')
    out['stage4_over_stage1'] = {}
    for label, col, tr in [('estimate', 'estimate', None),
                           ('standard error', 'se', None),
                           ('log standard error', 'se', np.log),
                           ('t value', 't_value', None)]:
        rat_iqr, rat_idr = [], []
        for h in range(1, 7):
            a = d[(d.hyp == h) & (d.stage == 1)][col].values
            b = d[(d.hyp == h) & (d.stage == 4)][col].values
            if tr is not None:
                a, b = tr(np.abs(a) + 1e-12), tr(np.abs(b) + 1e-12)
            f = lambda x: (np.percentile(x, 75) - np.percentile(x, 25))
            g_ = lambda x: (np.percentile(x, 90) - np.percentile(x, 10))
            rat_iqr.append(f(b) / f(a))
            rat_idr.append(g_(b) / g_(a))
        out['stage4_over_stage1'][label] = dict(
            iqr_ratios=[round(float(x), 4) for x in rat_iqr],
            iqr_median=float(np.median(rat_iqr)),
            idr_median=float(np.median(rat_idr)))
        print(f"  {label:20s} IQR ratio median {np.median(rat_iqr):6.3f}   "
              f"IDR ratio median {np.median(rat_idr):6.3f}")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                           'artifacts', 'f4_verify_quoted.json'), 'w') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()
