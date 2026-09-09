"""A2. A1 showed the yes/no decisions cluster in teams (variance 2.26x the
column-permutation null). This asks WHAT the team trait is.

Two families of team-level covariate:
  PRECISION-SIDE -- properties of how aggressively/sensitively the pipeline detects:
      estimated smoothness (FWHM, resels), applied smoothing kernel, software package,
      parametric vs nonparametric correction, median number of suprathreshold voxels.
  ANSWER-SIDE -- what the pipeline actually estimated:
      the team's median Spearman correlation of its unthresholded maps with the mean
      pattern across teams (NARPS's own `median_pattern_corr`).

The through-line under test (from `maria2026-analytic-variability-reanalysis`, built on
Breznau et al.'s sociology corpus): analytic decisions determine how PRECISELY an analysis
answers the question and say little about WHAT the answer is. If it transfers, the
team's yes-propensity should be predicted by the precision-side block and not by the
answer-side variable.
"""
import sys, os, json
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import load

RNG = np.random.default_rng(20260909)


def build():
    m = load.metadata()
    D = load.decisions()
    tv = pd.read_csv(os.path.join(load.ROOT, 'metadata', 'thresh_voxel_data.csv'))
    mpc = load.median_pattern_corr().rename(columns={'Unnamed: 0': 'teamID'})

    g = m.groupby('teamID')
    team = pd.DataFrame(index=sorted(m.teamID.unique()))
    team['yes_count'] = D.sum(axis=1)
    team['mean_fwhm'] = g['fwhm'].mean()
    team['mean_resels'] = g['resels'].mean()
    team['log_resels'] = np.log(g['resels'].mean())
    team['smoothing_coef'] = pd.to_numeric(g['smoothing_coef'].first(), errors='coerce')
    team['package'] = g['package'].first()
    team['testing'] = g['testing'].first()          # parametric / nonparametric / other
    team['fmriprep'] = (g['used_fmriprep_data'].first() == 'Yes').astype(int)
    team['movement'] = pd.to_numeric(g['movement_modeling'].first(), errors='coerce')
    team['median_thresh_vox'] = tv.groupby('teamID')['n_thresh_vox'].median()
    team['log_median_thresh_vox'] = np.log1p(team['median_thresh_vox'])
    team = team.join(mpc.set_index('teamID')['median_corr'])
    team['mean_confidence'] = load.confidence().mean(axis=1)
    team['mean_similar'] = m.groupby('teamID')['Similar'].mean()
    return team


def spear(a, b):
    from scipy import stats
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 5:
        return None
    r, p = stats.spearmanr(a[m], b[m])
    return dict(rho=float(r), p=float(p), n=int(m.sum()))


def main():
    from scipy import stats
    t = build()
    out = {'n_teams': int(len(t))}
    y = t['yes_count'].values.astype(float)

    uni = {}
    for c in ['mean_fwhm', 'log_resels', 'smoothing_coef', 'log_median_thresh_vox',
              'fmriprep', 'movement', 'median_corr', 'mean_confidence', 'mean_similar']:
        uni[c] = spear(y, t[c].values.astype(float))
    out['univariate_spearman_vs_yes_count'] = uni

    # categorical
    for c in ['package', 'testing']:
        grp = {str(k): dict(n=int(len(v)), mean_yes=float(np.mean(v)))
               for k, v in t.groupby(c)['yes_count']}
        vals = [v.values for _, v in t.groupby(c)['yes_count'] if len(v) >= 3]
        H, p = stats.kruskal(*vals) if len(vals) > 1 else (np.nan, np.nan)
        out[f'{c}_groups'] = dict(groups=grp, kruskal_H=float(H), kruskal_p=float(p))

    # out-of-team cross-validated R^2, precision block vs answer variable
    from sklearn.linear_model import RidgeCV
    from sklearn.model_selection import KFold, cross_val_predict
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.impute import SimpleImputer

    def cv_r2(X, y, seed=0, nrep=20):
        X = np.asarray(X, float); y = np.asarray(y, float)
        r2s = []
        for s in range(nrep):
            kf = KFold(n_splits=10, shuffle=True, random_state=seed + s)
            mdl = make_pipeline(SimpleImputer(strategy='median'), StandardScaler(),
                                RidgeCV(alphas=np.logspace(-2, 3, 30)))
            pred = cross_val_predict(mdl, X, y, cv=kf)
            ss_res = ((y - pred) ** 2).sum(); ss_tot = ((y - y.mean()) ** 2).sum()
            r2s.append(1 - ss_res / ss_tot)
        return float(np.mean(r2s)), float(np.std(r2s, ddof=1))

    prec_cols = ['mean_fwhm', 'log_resels', 'smoothing_coef', 'fmriprep', 'movement']
    Xp = pd.get_dummies(t[prec_cols + ['package', 'testing']], columns=['package', 'testing'],
                        dummy_na=True).astype(float)
    Xa = t[['median_corr']].astype(float)
    sub = t['median_corr'].notna().values   # answer variable only on 64 teams
    out['cv_r2_yescount_precision_block_allteams'] = cv_r2(Xp.values, y)
    out['cv_r2_yescount_precision_block_on64'] = cv_r2(Xp.values[sub], y[sub])
    out['cv_r2_yescount_answer_var_on64'] = cv_r2(Xa.values[sub], y[sub])
    out['cv_r2_yescount_both_on64'] = cv_r2(
        np.hstack([Xp.values[sub], Xa.values[sub]]), y[sub])
    # permutation baseline
    rng = np.random.default_rng(7)
    out['cv_r2_yescount_precision_block_PERMUTED'] = cv_r2(
        Xp.values, rng.permutation(y))

    # and the reverse: do the same precision covariates predict the ANSWER variable?
    ya = t['median_corr'].values.astype(float)[sub]
    out['cv_r2_answervar_from_precision_block'] = cv_r2(Xp.values[sub], ya)

    print(json.dumps(out, indent=1, default=str))
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                           'artifacts', 'a2_what_is_the_trait.json'), 'w') as f:
        json.dump(out, f, indent=1, default=str)
    t.to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                          'artifacts', 'team_level_table.csv'))


if __name__ == '__main__':
    main()
