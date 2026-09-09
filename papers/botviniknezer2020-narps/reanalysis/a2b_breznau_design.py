"""A2b. The exact Breznau design, transplanted.

`maria2026-analytic-variability-reanalysis` regressed, out-of-fold with folds grouped by
team, the CRI corpus's 137 coded analytic-decision indicators onto two outcomes:
    log standard error (PRECISION)  ->  R^2 = 0.194 +/- 0.024
    the point estimate (ANSWER)     ->  R^2 = -0.005 (permutation null -0.002)

Same design here. Predictors: only the CHOICES a team made, never a property of the
image they produced. Outcomes: one precision-side, one answer-side, one conclusion-side.

  X  : software package, applied smoothing kernel, use of fMRIPrep, movement modelling,
       correction family, statistic type, region-definition style, n participants kept.
  Y1 : log(resels)                      -- precision / effective resolution  [image-derived]
  Y2 : log1p(median suprathreshold vox) -- precision / how much gets declared  [image-derived]
  Y3 : median Spearman r with the consensus unthresholded map  -- THE ANSWER
  Y4 : yes-count out of 9               -- THE CONCLUSION
"""
import sys, os, json
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import load
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

CHOICE_CATS = ['package', 'testing', 'correction_method', 'statistic_type',
               'inter_subject_reg', 'motion_correction', 'model_type',
               'used_fmriprep_data', 'regions_definition']
CHOICE_NUMS = ['smoothing_coef', 'movement_modeling', 'n_participants']


def cv_r2(X, y, nrep=25, seed=0):
    X = np.asarray(X, float); y = np.asarray(y, float)
    ok = np.isfinite(y)
    X, y = X[ok], y[ok]
    r2s = []
    for s in range(nrep):
        kf = KFold(n_splits=10, shuffle=True, random_state=seed + s)
        mdl = make_pipeline(SimpleImputer(strategy='median'), StandardScaler(),
                            RidgeCV(alphas=np.logspace(-2, 4, 40)))
        pred = cross_val_predict(mdl, X, y, cv=kf)
        r2s.append(1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum())
    return dict(n=int(ok.sum()), r2=float(np.mean(r2s)), sd=float(np.std(r2s, ddof=1)))


def main():
    m = load.metadata()
    D = load.decisions()
    tv = pd.read_csv(os.path.join(load.ROOT, 'metadata', 'thresh_voxel_data.csv'))
    mpc = load.median_pattern_corr().rename(columns={'Unnamed: 0': 'teamID'})
    g = m.groupby('teamID')

    t = pd.DataFrame(index=sorted(m.teamID.unique()))
    for c in CHOICE_CATS:
        t[c] = g[c].first().astype(str).str.strip().str.lower()
    for c in CHOICE_NUMS:
        t[c] = pd.to_numeric(g[c].first(), errors='coerce')
    t['Y1_log_resels'] = np.log(g['resels'].mean())
    t['Y2_log_vox'] = np.log1p(tv.groupby('teamID')['n_thresh_vox'].median())
    t = t.join(mpc.set_index('teamID')['median_corr'].rename('Y3_median_corr'))
    t['Y4_yes_count'] = D.sum(axis=1)

    # collapse rare categorical levels (< 3 teams) into 'rare'
    for c in CHOICE_CATS:
        vc = t[c].value_counts()
        t[c] = t[c].where(t[c].map(vc) >= 3, 'rare')
    X = pd.get_dummies(t[CHOICE_CATS + CHOICE_NUMS], columns=CHOICE_CATS,
                       dummy_na=True).astype(float)
    out = {'n_teams': int(len(t)), 'n_predictors': int(X.shape[1]),
           'predictor_names': list(X.columns)}
    rng = np.random.default_rng(11)
    for y in ['Y1_log_resels', 'Y2_log_vox', 'Y3_median_corr', 'Y4_yes_count']:
        out[y] = cv_r2(X.values, t[y].values)
        yy = t[y].values.copy()
        ok = np.isfinite(yy)
        perm = yy.copy(); perm[ok] = rng.permutation(yy[ok])
        out[y + '_PERMUTED'] = cv_r2(X.values, perm)
        v = out[y]; p = out[y + '_PERMUTED']
        print(f"{y:18s} n={v['n']:3d}  CV R2 = {v['r2']:+.4f} +/- {v['sd']:.4f}   "
              f"(permuted {p['r2']:+.4f})")
    t.to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                          'artifacts', 'a2b_choices_table.csv'))
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                           'artifacts', 'a2b_breznau_design.json'), 'w') as f:
        json.dump(out, f, indent=1)
    print('\npredictors:', out['n_predictors'])


if __name__ == '__main__':
    main()
