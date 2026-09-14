"""F7. Does team quality reduce disagreement, or reduce standard errors?

Menkveld et al. report that a one-SD increase in reproducibility cuts the nonstandard
error by 25.0% and a one-SD increase in peer rating by 33.3%, while team quality itself
does nothing (+2.8%). Those are dispersion-level statements. The deposit carries all
three measures per team at stage 1, so the team-level version is checkable:

  (a) DEVIATION FROM CONSENSUS -- |estimate - median estimate| for that hypothesis,
      rank-transformed within hypothesis. This is the thing an NSE is made of.
  (b) log STANDARD ERROR, rank-transformed within hypothesis.
  (c) NUMBER OF SIGNIFICANT RESULTS out of six.

If quality predicts (b) much better than (a), then "quality reduces the nonstandard
error" is a statement about precision rather than about agreement -- which is this area's
through-line, and would be the third corpus to show it. If (a) comes out strong, the
through-line is wrong here and I should say so.
"""
import sys, os, json
import numpy as np
import pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import f0_load


def rank_within(W):
    return W.apply(lambda c: stats.rankdata(c) / (len(c) + 1), axis=0)


def main():
    d = f0_load.results()
    s = d[d.stage == 1].copy()
    out = {}
    est = s.pivot(index='team', columns='hyp', values='estimate')
    se = s.pivot(index='team', columns='hyp', values='se')
    t = s.pivot(index='team', columns='hyp', values='t_value')
    dev = (est - est.median(axis=0)).abs()
    Rdev = rank_within(dev)
    Rse = rank_within(np.log(se.clip(lower=1e-12)))
    nsig = (t.abs() > 1.96).sum(axis=1)

    q = s.groupby('team')[['quality', 'repro', 'peer']].first()
    q = q.loc[Rdev.index]
    out['n_teams'] = int(len(q))
    out['covariate_availability'] = {c: int(q[c].notna().sum()) for c in q.columns}

    targets = {'deviation_from_consensus_rank': Rdev.mean(axis=1),
               'log_standard_error_rank': Rse.mean(axis=1),
               'n_significant_of_6': nsig.astype(float)}
    print(f"{'covariate':10s} " + "".join(f"{k:>34s}" for k in targets))
    for cov in ['quality', 'repro', 'peer']:
        line = f"{cov:10s} "
        out[cov] = {}
        for name, y in targets.items():
            m = q[cov].notna() & y.notna()
            r = stats.spearmanr(q[cov][m], y[m])
            out[cov][name] = dict(rho=float(r.statistic), p=float(r.pvalue),
                                  n=int(m.sum()))
            line += f"{r.statistic:+8.3f} (p={r.pvalue:6.4f}, n={m.sum():3d})"
        print(line)

    # multivariate, out-of-fold, so the comparison is not three separate p-values
    from sklearn.linear_model import RidgeCV
    from sklearn.model_selection import KFold, cross_val_predict
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.impute import SimpleImputer
    X = q[['quality', 'repro', 'peer']].values.astype(float)

    def cv_r2(y, nrep=25):
        y = np.asarray(y, float)
        ok = np.isfinite(y) & np.isfinite(X).all(1)
        Xo, yo = X[ok], y[ok]
        r2 = []
        for sd_ in range(nrep):
            mdl = make_pipeline(SimpleImputer(strategy='median'), StandardScaler(),
                                RidgeCV(alphas=np.logspace(-2, 3, 30)))
            pred = cross_val_predict(mdl, Xo, yo,
                                     cv=KFold(10, shuffle=True, random_state=sd_))
            r2.append(1 - ((yo - pred) ** 2).sum() / ((yo - yo.mean()) ** 2).sum())
        return dict(n=int(ok.sum()), r2=float(np.mean(r2)), sd=float(np.std(r2, ddof=1)))

    print('\nout-of-fold R2 from the three quality measures together:')
    rng = np.random.default_rng(3)
    for name, y in targets.items():
        out[f'cv_r2__{name}'] = cv_r2(y)
        yy = np.asarray(y, float).copy()
        out[f'cv_r2__{name}__PERMUTED'] = cv_r2(rng.permutation(yy))
        v, p = out[f'cv_r2__{name}'], out[f'cv_r2__{name}__PERMUTED']
        print(f"  {name:32s} n={v['n']:3d}  R2 = {v['r2']:+.4f} +/- {v['sd']:.4f}   "
              f"(permuted {p['r2']:+.4f})")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                           'artifacts', 'f7_quality.json'), 'w') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()
