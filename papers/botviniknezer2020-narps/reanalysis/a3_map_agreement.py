"""A3. How much do the underlying (unthresholded) maps agree, and are the across-team
distributions heavy-tailed?

Tests two predictions frozen before any NARPS number was fetched
(.claude/memory/maria/SESSION_2026-09-09_plan.md):

P1: median pairwise Spearman r of the unthresholded maps > 0.4 for most hypotheses.
P3: IDR/IQR of an across-team continuous quantity exceeds the Gaussian reference 1.90,
    as it does in #fincap (4.07) and CRI (2.79).
    IDR = interdecile range (P90-P10); for a Gaussian IDR/IQR = 2.5631/1.3490 = 1.900.
"""
import sys, os, json
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import load

HYPS = [1, 2, 5, 6, 7, 8, 9]   # 3/4 are duplicates of 1/2 (same maps), 3 and 4 not deposited
GAUSS_IDR_OVER_IQR = 2 * 1.2815515655446004 / (2 * 0.6744897501960817)


def idr_over_iqr(x):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    iqr = np.percentile(x, 75) - np.percentile(x, 25)
    idr = np.percentile(x, 90) - np.percentile(x, 10)
    return float(idr / iqr) if iqr > 0 else float('nan')


def main():
    out = {'gaussian_reference_idr_over_iqr': GAUSS_IDR_OVER_IQR, 'per_hypothesis': {}}
    D = load.decisions()
    for h in HYPS:
        C = load.unthresh_corr(h)
        A = C.values.astype(float)
        n = A.shape[0]
        iu = np.triu_indices(n, 1)
        r = A[iu]
        teams = list(C.index)
        # per-team median correlation with the other teams
        M = A.copy()
        np.fill_diagonal(M, np.nan)
        team_med = np.nanmedian(M, axis=1)
        dec = D.loc[teams, h].values
        out['per_hypothesis'][h] = dict(
            n_teams=n, n_pairs=int(len(r)),
            mean_r=float(r.mean()), median_r=float(np.median(r)),
            p10_r=float(np.percentile(r, 10)), p90_r=float(np.percentile(r, 90)),
            frac_pairs_negative=float((r < 0).mean()),
            idr_over_iqr_pairwise=idr_over_iqr(r),
            idr_over_iqr_team_median_r=idr_over_iqr(team_med),
            team_median_r_mean=float(team_med.mean()),
            team_median_r_sd=float(team_med.std(ddof=1)),
            # does a team's agreement with the field predict its yes/no?
            corr_teammedianr_with_decision=float(np.corrcoef(team_med, dec)[0, 1]),
            mean_teammedianr_yes=float(team_med[dec == 1].mean()) if (dec == 1).any() else None,
            mean_teammedianr_no=float(team_med[dec == 0].mean()) if (dec == 0).any() else None,
            n_yes=int(dec.sum()),
        )
    vals = out['per_hypothesis']
    out['summary'] = dict(
        mean_r_range=[min(v['mean_r'] for v in vals.values()),
                      max(v['mean_r'] for v in vals.values())],
        median_r_range=[min(v['median_r'] for v in vals.values()),
                        max(v['median_r'] for v in vals.values())],
        n_hyp_with_median_r_gt_0_4=sum(v['median_r'] > 0.4 for v in vals.values()),
        n_hyp_total=len(vals),
        idr_iqr_pairwise_range=[min(v['idr_over_iqr_pairwise'] for v in vals.values()),
                                max(v['idr_over_iqr_pairwise'] for v in vals.values())],
        idr_iqr_teammedian_range=[min(v['idr_over_iqr_team_median_r'] for v in vals.values()),
                                  max(v['idr_over_iqr_team_median_r'] for v in vals.values())],
    )
    print(json.dumps(out, indent=1))
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                           'artifacts', 'a3_map_agreement.json'), 'w') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()
