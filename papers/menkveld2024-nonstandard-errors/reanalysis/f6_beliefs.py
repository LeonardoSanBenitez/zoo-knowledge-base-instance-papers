"""F6. Do researchers know how much they are about to disagree?

After submitting their Stage 1 results and before seeing anyone else's, each of the 164
teams answered an INCENTIVIZED survey: what will the across-team standard deviation of
the Stage 1 estimates be, for each of the six hypotheses? And the same for t-values.
(Design confirmed from fincap.academy/data_analysis.html; the belief survey is explicitly
about the variation in STAGE 1 results, so stage 1 is the target.)

This is the #fincap counterpart of the NARPS prediction markets, in another field and on
a different quantity, and it is a rare thing: a forecast of DISAGREEMENT itself.

The trap, and it is the whole reason the analysis needs care. The realised SD of the
estimates in this corpus is one team: a single research team carries 87-99% of the sum of
squares on every hypothesis (see f4_verify_quoted.json). So the question as asked -- "what
will the SD be" -- asks a forecaster to predict an outlier. Scoring against the SD alone
would measure their luck at guessing one team. Every comparison below is therefore made
against BOTH the raw SD and the robust NSE = IQR/1.349 that Menkveld et al. themselves
chose for exactly this reason.
"""
import sys, os, json
import numpy as np
import pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import f0_load


def main():
    d = f0_load.results()
    b = f0_load.beliefs().rename(columns={
        'research_team_id': 'team', 'rt_hypothesis': 'hyp',
        'across_rt_standard_deviation_in_estimates': 'pred_sd_est',
        'across_rt_standard_deviation_in_t_values': 'pred_sd_t'})
    out = {'n_forecasters': int(b.team.nunique()), 'n_hypotheses': int(b.hyp.nunique())}
    truth = {}
    for h in range(1, 7):
        g = d[(d.hyp == h) & (d.stage == 1)]
        e = g['estimate'].values
        t = g['t_value'].values
        truth[h] = dict(
            sd_est=float(e.std(ddof=1)), nse_est=float((np.percentile(e, 75) - np.percentile(e, 25)) / 1.349),
            sd_t=float(t.std(ddof=1)), nse_t=float((np.percentile(t, 75) - np.percentile(t, 25)) / 1.349))
    out['truth'] = {str(h): v for h, v in truth.items()}

    print(f"{'hyp':>3} {'realised SD':>12} {'robust NSE':>11} {'SD/NSE':>7} | "
          f"{'median pred':>12} {'pred/SD':>9} {'pred/NSE':>9} {'% below NSE':>11}")
    rows = []
    for h in range(1, 7):
        p = b[b.hyp == h]['pred_sd_est'].values
        med = float(np.median(p))
        rows.append(dict(hyp=h, median_pred=med,
                         ratio_to_sd=med / truth[h]['sd_est'],
                         ratio_to_nse=med / truth[h]['nse_est'],
                         frac_below_nse=float((p < truth[h]['nse_est']).mean()),
                         frac_below_sd=float((p < truth[h]['sd_est']).mean())))
        print(f"{h:3d} {truth[h]['sd_est']:12.3f} {truth[h]['nse_est']:11.3f} "
              f"{truth[h]['sd_est']/truth[h]['nse_est']:7.1f} | {med:12.3f} "
              f"{med/truth[h]['sd_est']:9.5f} {med/truth[h]['nse_est']:9.3f} "
              f"{100*rows[-1]['frac_below_nse']:10.1f}%")
    out['estimates'] = rows
    print(f"\n  median over hypotheses of (median prediction / realised SD)  = "
          f"{np.median([r['ratio_to_sd'] for r in rows]):.5f}")
    print(f"  median over hypotheses of (median prediction / robust NSE)   = "
          f"{np.median([r['ratio_to_nse'] for r in rows]):.3f}")
    print(f"  share of all 984 forecasts below the robust NSE              = "
          f"{100*np.mean([r['frac_below_nse'] for r in rows]):.1f}%")

    print('\nt-values (same, and the scale is comparable across hypotheses here):')
    rows_t = []
    for h in range(1, 7):
        p = b[b.hyp == h]['pred_sd_t'].values
        med = float(np.median(p))
        rows_t.append(dict(hyp=h, median_pred=med, sd_t=truth[h]['sd_t'],
                           nse_t=truth[h]['nse_t'],
                           ratio_to_sd=med / truth[h]['sd_t'],
                           ratio_to_nse=med / truth[h]['nse_t'],
                           frac_below_nse=float((p < truth[h]['nse_t']).mean())))
        print(f"  h{h}: realised SD(t) {truth[h]['sd_t']:8.3f}  robust NSE(t) "
              f"{truth[h]['nse_t']:7.3f}  median prediction {med:6.3f}  "
              f"pred/NSE {med/truth[h]['nse_t']:6.3f}  "
              f"{100*rows_t[-1]['frac_below_nse']:5.1f}% of teams below NSE")
    out['t_values'] = rows_t

    # discrimination: does the ordering of the six hypotheses come out right?
    med_pred = [r['median_pred'] for r in rows]
    out['discrimination'] = dict(
        spearman_pred_vs_sd=float(stats.spearmanr(med_pred, [truth[h]['sd_est'] for h in range(1, 7)]).statistic),
        spearman_pred_vs_nse=float(stats.spearmanr(med_pred, [truth[h]['nse_est'] for h in range(1, 7)]).statistic),
        spearman_pred_t_vs_nse_t=float(stats.spearmanr([r['median_pred'] for r in rows_t],
                                                       [truth[h]['nse_t'] for h in range(1, 7)]).statistic))
    print(f"\ndiscrimination across the six hypotheses (Spearman, n=6, the smallest "
          f"attainable two-sided p is {2/720:.4f}):")
    for k, v in out['discrimination'].items():
        print(f"  {k:28s} {v:+.3f}")

    # per-forecaster accuracy on the log scale, against the robust target
    lo = []
    for h in range(1, 7):
        p = b[b.hyp == h]['pred_sd_est'].values
        lo.append(np.log(np.clip(p, 1e-9, None)) - np.log(truth[h]['nse_est']))
    lo = np.concatenate(lo)
    out['log_error_vs_nse'] = dict(
        n=int(len(lo)), mean=float(lo.mean()), median=float(np.median(lo)),
        sd=float(lo.std(ddof=1)),
        frac_within_factor_2=float((np.abs(lo) < np.log(2)).mean()),
        frac_within_factor_10=float((np.abs(lo) < np.log(10)).mean()),
        median_factor=float(np.exp(np.median(lo))))
    v = out['log_error_vs_nse']
    print(f"\nper-forecast log error against the robust NSE (n={v['n']}): "
          f"median factor {v['median_factor']:.3f}, "
          f"{100*v['frac_within_factor_2']:.1f}% within a factor of 2, "
          f"{100*v['frac_within_factor_10']:.1f}% within a factor of 10")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                           'artifacts', 'f6_beliefs.json'), 'w') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()
