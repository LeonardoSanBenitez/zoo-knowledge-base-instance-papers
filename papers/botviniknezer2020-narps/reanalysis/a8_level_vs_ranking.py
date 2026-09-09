"""A8. Thresholding sets the LEVEL; the data set the RANKING.

The deposit contains NARPS's own re-thresholding of every team's unthresholded map with
ONE common rule, in two variants (uncorrected p<0.001 with k>10, and FDR), plus a common
anatomical ROI. NARPS reports this as showing that "the degree of variability across
results was qualitatively similar" -- i.e. it looks at the DISPERSION across teams.

It does not report what happens to the LEVEL. That is the number a reader of any single
fMRI paper actually consumes: how often does this hypothesis come out significant?
"""
import sys, os, json
import numpy as np
import pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import load


def main():
    d = pd.read_csv(os.path.join(load.ROOT, 'figures', 'ThresholdSimulation',
                                 'simulation_results.csv'))
    d = d.rename(columns={
        'proportion of teams reporting act.': 'reported',
        'proportion of teams w/  act. ($p < 0.001$, $k > 10$)': 'p001k10',
        'proportion of teams w/  act. (FDR)': 'fdr',
        'N voxels in ROI': 'roi_vox',
        'CBMA (n voxels in ROI)': 'cbma', 'IBMA (n voxels in ROI)': 'ibma'})
    out = {'table': d.to_dict(orient='records')}
    for a, b in [('reported', 'p001k10'), ('reported', 'fdr'), ('p001k10', 'fdr')]:
        rho = stats.spearmanr(d[a], d[b])
        out[f'spearman_{a}_vs_{b}'] = dict(rho=float(rho.statistic), p=float(rho.pvalue))
        diff = (d[b] - d[a])
        out[f'level_shift_{a}_to_{b}'] = dict(
            mean_abs=float(diff.abs().mean()), max_abs=float(diff.abs().max()),
            mean_signed=float(diff.mean()),
            per_hyp={str(int(h)): round(float(v), 4) for h, v in zip(d.Hypothesis, diff)})
        print(f"{a:9s} -> {b:9s}  Spearman rho={rho.statistic:+.3f} (p={rho.pvalue:.4f})  "
              f"mean|delta|={diff.abs().mean():.3f}  max|delta|={diff.abs().max():.3f}  "
              f"mean signed={diff.mean():+.3f}")
    # ratio of the two thresholding rules, per hypothesis
    r = (d['fdr'] / d['p001k10'].replace(0, np.nan))
    out['fdr_over_p001k10_ratio'] = {str(int(h)): (None if not np.isfinite(v) else round(float(v), 3))
                                     for h, v in zip(d.Hypothesis, r)}
    print('\nfraction of teams called significant, per hypothesis:')
    print(d[['Hypothesis', 'reported', 'p001k10', 'fdr', 'cbma', 'ibma']].to_string(index=False))
    # how many hypotheses change side of 0.5?
    for c in ['reported', 'p001k10', 'fdr']:
        out[f'n_hyp_majority_yes_{c}'] = int((d[c] > 0.5).sum())
        print(f"hypotheses where a MAJORITY is significant under {c}: {(d[c] > 0.5).sum()} of 9")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                           'artifacts', 'a8_level_vs_ranking.json'), 'w') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()
