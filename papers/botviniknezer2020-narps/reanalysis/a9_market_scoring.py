"""A9. The prediction markets, scored against baselines nobody reported.

NARPS reports for the two markets: rank correlation with the truth (team 0.962,
non-team 0.553), a Wilcoxon test that both OVERESTIMATED, and mean absolute error
(team 0.323, non-team 0.449). Rank correlation is DISCRIMINATION -- did they order the
hypotheses correctly. MAE is ACCURACY. A forecast can be perfect on one and useless on
the other, and here it is.

The baseline nobody computed: predict the SAME number for all nine hypotheses.
That is the least informative forecast that exists. If it beats a market on MAE, the
market's absolute predictions carry no usable information, however well it ranks.

Data: Supplementary Data 1 (41586_2020_2314_MOESM3_ESM.csv), fetched from
media.springernature.com -- freely downloadable although the article itself is paywalled.
    fv       = fundamental value = fraction of the 70 teams reporting significance
    price.1  = final price, "team members" market   (range 0.073-0.952, matches paper)
    price.0  = final price, "non-team members" market (range 0.476-0.882, matches paper)
"""
import sys, os, json
import math
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, '..', 'artifacts', 'narps_MOESM3_ESM.csv')
NPERM = 200000


def scores(pred, fv):
    pred = np.asarray(pred, float); fv = np.asarray(fv, float)
    return dict(mae=float(np.abs(pred - fv).mean()),
                rmse=float(np.sqrt(((pred - fv) ** 2).mean())),
                brier_like=float(((pred - fv) ** 2).mean()),
                bias=float((pred - fv).mean()),
                spearman=float(stats.spearmanr(pred, fv).statistic))


def main():
    d = pd.read_csv(CSV).sort_values('hid')
    fv = d['fv'].values
    out = {'n_hypotheses': int(len(d)),
           'fv': [round(float(x), 4) for x in fv]}
    preds = {
        'team_market': d['price.1'].values,
        'nonteam_market': d['price.0'].values,
        'constant_mean_of_truth': np.full(len(fv), fv.mean()),
        'constant_median_of_truth': np.full(len(fv), np.median(fv)),
        'constant_0.5_coinflip': np.full(len(fv), 0.5),
        'constant_0.276_matched_to_grand_mean': np.full(len(fv), 0.2762),
    }
    for k, v in preds.items():
        out[k] = scores(v, fv)
        s = out[k]
        print(f"{k:38s} MAE={s['mae']:.3f} RMSE={s['rmse']:.3f} "
              f"bias={s['bias']:+.3f} spearman={s['spearman']:+.3f}")

    out['paper_reported'] = dict(team_mae=0.323, nonteam_mae=0.449,
                                 team_spearman=0.962, nonteam_spearman=0.553)
    print("\npaper reports team MAE 0.323 / non-team 0.449 -- reproduced above to 3 dp:",
          round(out['team_market']['mae'], 3), round(out['nonteam_market']['mae'], 3))

    # how much of the constant baseline's advantage is hindsight? A constant fitted to
    # the truth is not available ex ante. Leave-one-out version: predict each hypothesis
    # with the mean of the other eight.
    loo = np.array([np.delete(fv, i).mean() for i in range(len(fv))])
    out['constant_leave_one_out'] = scores(loo, fv)
    print("leave-one-out constant (honest, no hindsight)   "
          f"MAE={out['constant_leave_one_out']['mae']:.3f}")

    # exact permutation p for the team market's rank correlation, n=9
    rng = np.random.default_rng(0)
    for k in ['team_market', 'nonteam_market']:
        p = preds[k]
        obs = stats.spearmanr(p, fv).statistic
        null = np.array([stats.spearmanr(rng.permutation(p), fv).statistic
                         for _ in range(20000)])
        out[k + '_spearman_perm_p'] = float((1 + (np.abs(null) >= abs(obs)).sum()) / 20001)
        print(f"{k} spearman perm p = {out[k + '_spearman_perm_p']:.5f} "
              f"(smallest attainable at n=9 is {2/math.factorial(9):.2e})")

    # paired test: is the market's absolute error larger than the LOO constant's?
    for k in ['team_market', 'nonteam_market']:
        a = np.abs(preds[k] - fv); b = np.abs(loo - fv)
        w = stats.wilcoxon(a, b)
        out[k + '_vs_loo_constant_wilcoxon'] = dict(stat=float(w.statistic),
                                                    p=float(w.pvalue),
                                                    mean_diff=float((a - b).mean()))
        print(f"{k} abs-error vs LOO-constant: mean diff {a.mean()-b.mean():+.3f}, "
              f"Wilcoxon p={w.pvalue:.4f}")

    # the five NON-redundant hypotheses (H1/H3 and H2/H4 share a statistical map,
    # H7/H8/H9 are all amygdala-loss): does the ranking result survive?
    keep = d[d.hid.isin([1, 2, 5, 6, 7])]
    out['nonredundant_subset'] = dict(
        n=int(len(keep)),
        team_spearman=float(stats.spearmanr(keep['price.1'], keep['fv']).statistic),
        nonteam_spearman=float(stats.spearmanr(keep['price.0'], keep['fv']).statistic),
        team_mae=float(np.abs(keep['price.1'] - keep['fv']).mean()))
    print("\nnon-redundant subset (H1,H2,H5,H6,H7):", out['nonredundant_subset'])
    with open(os.path.join(HERE, '..', 'artifacts', 'a9_market_scoring.json'), 'w') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()


def main_b():
    """A9b. Decompose the error, and test the obvious alternative reading:
    were the traders forecasting the SOCIOLOGY (how many teams will say yes) or the
    SCIENCE (is the effect there)? The study's own image-based meta-analysis gives a
    verdict on the second."""
    import json as _json
    d = pd.read_csv(CSV).sort_values('hid')
    fv = d['fv'].values
    ibma = {1: 0, 2: 1, 3: 0, 4: 1, 5: 1, 6: 1, 7: 0, 8: 0, 9: 0}   # >0 voxels in ROI
    cbma = {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 0, 8: 1, 9: 1}
    iv = np.array([ibma[h] for h in d.hid])
    cv = np.array([cbma[h] for h in d.hid])
    out = {}
    for k, col in [('team', 'price.1'), ('nonteam', 'price.0')]:
        p = d[col].values
        mse = float(((p - fv) ** 2).mean()); bias = float((p - fv).mean())
        var = float(((p - fv) - bias).var(ddof=0))
        deb = p - bias
        out[k] = dict(
            mse=mse, bias=bias, bias2=bias ** 2,
            bias2_share_of_mse=float(bias ** 2 / mse), residual_var=var,
            debiased_mae=float(np.abs(deb - fv).mean()),
            debiased_rmse=float(np.sqrt(((deb - fv) ** 2).mean())),
            pearson_with_fv=float(np.corrcoef(p, fv)[0, 1]),
            mean_price_where_ibma_yes=float(p[iv == 1].mean()),
            mean_price_where_ibma_no=float(p[iv == 0].mean()),
            pointbiserial_with_ibma=float(stats.pointbiserialr(iv, p).statistic),
            pointbiserial_with_ibma_p=float(stats.pointbiserialr(iv, p).pvalue),
            pointbiserial_with_cbma=float(stats.pointbiserialr(cv, p).statistic),
            spearman_with_fv=float(stats.spearmanr(p, fv).statistic))
        s = out[k]
        print(f"{k:8s} MSE={s['mse']:.4f}  bias={s['bias']:+.3f}  "
              f"bias^2 is {100*s['bias2_share_of_mse']:.0f}% of MSE  "
              f"debiased RMSE={s['debiased_rmse']:.3f}  "
              f"r(price, fv)={s['pearson_with_fv']:+.3f}  "
              f"r_pb(price, IBMA)={s['pointbiserial_with_ibma']:+.3f} "
              f"(p={s['pointbiserial_with_ibma_p']:.3f})")
    loo = np.array([np.delete(fv, i).mean() for i in range(len(fv))])
    out['loo_constant_rmse'] = float(np.sqrt(((loo - fv) ** 2).mean()))
    print(f"leave-one-out constant RMSE = {out['loo_constant_rmse']:.3f}")
    with open(os.path.join(HERE, '..', 'artifacts', 'a9b_market_decomposition.json'),
              'w') as f:
        _json.dump(out, f, indent=1)
