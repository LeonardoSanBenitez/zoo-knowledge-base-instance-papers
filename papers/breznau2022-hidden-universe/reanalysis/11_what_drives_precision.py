"""Two ways the headline of this reanalysis could be less than it looks.

Headline (08): out-of-team, the coded analytic decisions reach R^2 = 0.207 for
log standard error and R^2 = -0.003 for the estimate. Decisions determine
precision, not conclusions.

OBJECTION 1 - "you only predicted an arithmetic artifact of sample size".
    A standard error is roughly sigma/sqrt(N). If the R^2 = 0.207 is carried
    entirely by how many countries and survey waves a team included, the finding
    is 'teams that used more data got smaller standard errors', which is not
    interesting. Test: strip the sample-composition indicators (country dummies,
    wave dummies, country count) and re-fit on modelling choices alone; and
    conversely fit on sample composition alone.

OBJECTION 2 - "your outcome is your own construction".
    The significance category was computed by me from the CIs. Breznau et al.
    also collected what each team ACTUALLY CONCLUDED in words: support the
    hypothesis, reject it, or not testable. That is the outcome the paper cares
    about and it is in the released data as `Hresult`. If decisions predict the
    written conclusion out-of-team no better than they predict the estimate, the
    split survives on the field's own outcome rather than on mine.

Also reported: which single blocks of decisions carry the precision signal, so
the claim can be stated as a mechanism rather than an R^2.
"""
import os, json
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "cri_model_level.csv")
BLOCKS = os.path.join(HERE, "..", "data", "column_blocks.json")
Z95 = 1.959964
RNG = np.random.default_rng(808)
LAMS = np.geomspace(1e-2, 1e6, 17)


def load():
    d = pd.read_csv(DATA, low_memory=False)
    a = d[d.AME_Z.notna() & (d.u_teamid != 0)].copy()
    a["se_z"] = (a.upper_Z - a.lower_Z) / (2 * Z95)
    return a[np.isfinite(a.se_z) & (a.se_z > 0)].copy()


def ridge_cv(X, y, groups, lam, folds):
    pred = np.full(len(y), np.nan)
    for f in folds:
        te = np.isin(groups, f)
        tr = ~te
        if tr.sum() < 20 or te.sum() == 0:
            continue
        Xm, ym = X[tr].mean(0), y[tr].mean()
        Xc = X[tr] - Xm
        b = np.linalg.solve(Xc.T @ Xc + lam * np.eye(X.shape[1]), Xc.T @ (y[tr] - ym))
        pred[te] = (X[te] - Xm) @ b + ym
    m = np.isfinite(pred)
    return 1 - np.sum((y[m] - pred[m]) ** 2) / np.sum((y[m] - y[m].mean()) ** 2)


def best_r2(cols, y, a, groups, folds):
    if not cols:
        return np.nan, 0
    X = a[cols].apply(pd.to_numeric, errors="coerce").fillna(0.0).values.astype(float)
    k = X.std(0) > 0
    if k.sum() == 0:
        return np.nan, 0
    X = (X[:, k] - X[:, k].mean(0)) / X[:, k].std(0)
    return max(ridge_cv(X, y, groups, l, folds) for l in LAMS), int(k.sum())


def main():
    a = load()
    blocks = json.load(open(BLOCKS))
    dec = [c for c in blocks["decisions"] if c in a.columns]
    groups = a.u_teamid.values
    ug = np.unique(groups)
    RNG.shuffle(ug)
    folds = np.array_split(ug, 10)

    COUNTRIES = ['AU','AT','BE','BG','CA','CL','HR','CY','CZ','DK','FI','FR','DE','HU',
                 'IS','IN','IE','IL','IT','JP','KR','LV','LT','NT','NZ','NO','PH','PL',
                 'PT','RU','SK','SI','ES','SE','CH','UK','US','ZA','TW','TR','UY','VE']
    WAVES = ['w1985', 'w1990', 'w1996', 'w2006', 'w2016']
    SAMPLE = [c for c in COUNTRIES + WAVES + ['orig13', 'orig17', 'eeurope',
              'allavailable', 'unbalpanel', 'listwise', 'multimpute'] if c in a.columns]
    DVSEL = [c for c in ['Jobs', 'Unemp', 'IncDiff', 'OldAge', 'House', 'Health',
                         'Scale'] if c in a.columns]
    IVSEL = [c for c in ['Stock', 'Flow', 'ChangeFlow', 'main_IV_as_control'] if c in a.columns]
    ESTIM = [c for c in ['logit', 'ologit', 'lpm', 'ols', 'mlogit', 'ml_glm', 'bayes',
                         'mlm_any', 'mlm_re', 'mlm_fe', 'hybrid_mlm', 'twowayfe',
                         'cluster_any', 'weights', 'L2boots', 'pseudo_pnl',
                         'level_cyear', 'level_country', 'level_year',
                         'country_dummies_only', 'year_dummies_only', 'year_as_count',
                         'dichotomize', 'categorical', 'anynonlin'] if c in a.columns]
    COVAR = [c for c in dec if c.endswith('_iv') or c.endswith('_ivC')]
    SOFT = [c for c in ['stata', 'r', 'mplus', 'spss', 'mlwin'] if c in a.columns]

    y_logse = np.log(a.se_z.values)
    y_ame = a.AME_Z.values

    print("OBJECTION 1 -- is log SE predictability just sample size?")
    print("%-34s %5s %12s %12s" % ("predictor block", "p", "R2 log SE", "R2 estimate"))
    for name, cols in [("ALL decisions", dec),
                       ("sample composition only", SAMPLE),
                       ("modelling choices only (no sample)", ESTIM + SOFT),
                       ("covariate set only", COVAR),
                       ("outcome/IV selection only", DVSEL + IVSEL),
                       ("everything EXCEPT sample comp.", [c for c in dec if c not in SAMPLE]),
                       ("num_countries alone", ["num_countries"])]:
        r1, p1 = best_r2(cols, y_logse, a, groups, folds)
        r2, _ = best_r2(cols, y_ame, a, groups, folds)
        print("%-34s %5d %12.4f %12.4f" % (name, p1, r1, r2))
    print("  Read: if 'everything EXCEPT sample composition' keeps most of the")
    print("  signal, the finding is about modelling choices, not about N.\n")

    print("OBJECTION 2 -- does it hold on the team's OWN WRITTEN conclusion?")
    hr = a.Hresult.astype(str)
    print("  Hresult distribution:", hr.value_counts().to_dict())
    outcomes = {
        "wrote 'Support' (0/1)": (hr == "Support").astype(float).values,
        "wrote 'Reject' (0/1)": (hr == "Reject").astype(float).values,
        "wrote 'No test' (0/1)": (hr == "No test").astype(float).values,
        "my significance category is 'negative'":
            ((a.AME_Z + Z95 * a.se_z) < 0).astype(float).values,
        "my significance category is 'null'":
            (((a.AME_Z - Z95 * a.se_z) < 0) & ((a.AME_Z + Z95 * a.se_z) > 0)).astype(float).values,
        "log standard error": y_logse,
        "the estimate": y_ame,
    }
    print("\n%-42s %12s %12s" % ("outcome", "R2 (out-of-team)", "perm null"))
    for name, y in outcomes.items():
        r, _ = best_r2(dec, y, a, groups, folds)
        yp = y.copy()
        RNG.shuffle(yp)
        pn, _ = best_r2(dec, yp, a, groups, folds)
        print("%-42s %12.4f %12.4f" % (name, r, pn))
    print("\n  A written conclusion is a team-level act, so models within a team")
    print("  share it almost perfectly; grouping the folds by team is what stops")
    print("  that from inflating the number.")

    print("\nMECHANISM -- what actually moves the standard error")
    X = a[dec].apply(pd.to_numeric, errors="coerce").fillna(0.0).values.astype(float)
    k = X.std(0) > 0
    names = [c for c, kk in zip(dec, k) if kk]
    Xs = (X[:, k] - X[:, k].mean(0)) / X[:, k].std(0)
    Xm, ym = Xs.mean(0), y_logse.mean()
    b = np.linalg.solve((Xs - Xm).T @ (Xs - Xm) + 1000.0 * np.eye(Xs.shape[1]),
                        (Xs - Xm).T @ (y_logse - ym))
    o = np.argsort(-np.abs(b))[:12]
    for i in o:
        print("   %-26s %+.3f" % (names[i], b[i]))
    print("\n   For comparison, the same coefficients for the ESTIMATE:")
    b2 = np.linalg.solve((Xs - Xm).T @ (Xs - Xm) + 1000.0 * np.eye(Xs.shape[1]),
                         (Xs - Xm).T @ (y_ame - y_ame.mean()))
    print("   max |coefficient| = %.4f (log SE: %.4f) -- a factor of %.0f"
          % (np.abs(b2).max(), np.abs(b).max(), np.abs(b).max() / max(1e-9, np.abs(b2).max())))


if __name__ == "__main__":
    main()
