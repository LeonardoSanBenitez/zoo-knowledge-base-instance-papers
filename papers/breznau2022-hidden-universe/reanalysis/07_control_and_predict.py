"""Two things 06 left unfinished.

PART 1 - the control 06 needs before its headline can be believed.
06 found that conditioning on the estimand-defining choices (dependent variable,
immigration measure, total/within/between, country set) does not reduce the
between-model heterogeneity tau; it raises it from 0.0187 to 0.0276. A rise is
suspicious: Paule-Mandel is noisy and upward-biased in small cells, and
conditioning shrinks cells. So: permute the cell labels, keeping the exact cell
SIZE distribution, and see what pooled within-cell tau a MEANINGLESS partition
produces. If random partitions also give ~0.0276, the honest reading of 06 is
'no reduction', not 'an increase'.

PART 2 - what DO the analytic decisions predict?
Breznau et al. regressed the estimates on the decisions and explained <2.6% of
the variance. Three outcomes are available from the same decision matrix, and
they are not equally predictable:
    the estimate            AME_Z
    the precision           log SE_Z
    the conclusion          significant-negative / null / significant-positive
Prediction is evaluated out-of-fold with GROUPED cross-validation by team,
because models within a team share an analyst and a code file; random k-fold
would leak team identity and inflate every number. Ridge (closed form) and
gradient boosting, each against a label-permutation null run through the exact
same pipeline.
"""
import os, json
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "cri_model_level.csv")
BLOCKS = os.path.join(HERE, "..", "data", "column_blocks.json")
Z95 = 1.959964
RNG = np.random.default_rng(4242)


def pm(y, v, it=200):
    if len(y) < 3:
        return np.nan
    lo, hi = 0.0, max(1e-12, np.var(y, ddof=1) * 50)

    def gq(t2):
        w = 1 / (v + t2)
        mu = (w * y).sum() / w.sum()
        return (w * (y - mu) ** 2).sum() - (len(y) - 1)
    if gq(lo) <= 0:
        return 0.0
    if gq(hi) > 0:
        return hi
    for _ in range(it):
        mid = .5 * (lo + hi)
        if gq(mid) > 0:
            lo = mid
        else:
            hi = mid
    return .5 * (lo + hi)


def load():
    d = pd.read_csv(DATA, low_memory=False)
    a = d[d.AME_Z.notna() & (d.u_teamid != 0)].copy()
    a["se_z"] = (a.upper_Z - a.lower_Z) / (2 * Z95)
    a = a[np.isfinite(a.se_z) & (a.se_z > 0)].copy()
    a["v"] = a.se_z ** 2
    return a


def pooled_within_tau(y, v, labels):
    t2s, tot = [], 0
    for lab in np.unique(labels):
        m = labels == lab
        if m.sum() < 3:
            continue
        t2 = pm(y[m], v[m])
        if np.isfinite(t2):
            t2s.append((m.sum(), t2))
            tot += m.sum()
    if not t2s:
        return np.nan
    return np.sqrt(sum(n * t for n, t in t2s) / tot)


def part1(a):
    y, v = a.AME_Z.values, a.v.values
    print("=" * 72)
    print("PART 1 - permutation control for the estimand-conditioning result")
    print("=" * 72)
    specs = [("DV x measure x effect x n countries",
              ["DV", "main_IV_type", "main_IV_effect", "num_countries"]),
             ("DV x measure x effect", ["DV", "main_IV_type", "main_IV_effect"]),
             ("team", ["u_teamid"])]
    print("base (no conditioning): tau = %.5f" % np.sqrt(pm(y, v)))
    for name, keys in specs:
        lab = a.groupby(keys).ngroup().values
        real = pooled_within_tau(y, v, lab)
        sizes = pd.Series(lab).value_counts().values
        nulls = []
        for _ in range(200):
            perm = np.concatenate([np.full(s, i) for i, s in enumerate(sizes)])
            RNG.shuffle(perm)
            nulls.append(pooled_within_tau(y, v, perm))
        nulls = np.array([x for x in nulls if np.isfinite(x)])
        print("  %-38s real tau = %.5f | random partitions of the SAME sizes: "
              "%.5f (sd %.5f, 2.5-97.5%% %.5f-%.5f)"
              % (name, real, nulls.mean(), nulls.std(),
                 np.percentile(nulls, 2.5), np.percentile(nulls, 97.5)))
        print("  %-38s -> %s"
              % ("", "real is INSIDE the random band: conditioning explains nothing"
                 if np.percentile(nulls, 2.5) <= real <= np.percentile(nulls, 97.5)
                 else "real is OUTSIDE the random band"))


# ------------------------------------------------------------- prediction
def ridge_fit(X, yv, lam):
    n, p = X.shape
    Xm, ym = X.mean(0), yv.mean()
    Xc, yc = X - Xm, yv - ym
    A = Xc.T @ Xc + lam * np.eye(p)
    b = np.linalg.solve(A, Xc.T @ yc)
    return b, ym - Xm @ b


def grouped_cv_r2(X, yv, groups, lam, nfold=10):
    ug = np.unique(groups)
    RNG.shuffle(ug)
    folds = np.array_split(ug, nfold)
    pred = np.full(len(yv), np.nan)
    for f in folds:
        te = np.isin(groups, f)
        tr = ~te
        if tr.sum() < 10 or te.sum() == 0:
            continue
        b, c = ridge_fit(X[tr], yv[tr], lam)
        pred[te] = X[te] @ b + c
    m = np.isfinite(pred)
    ss_res = np.sum((yv[m] - pred[m]) ** 2)
    ss_tot = np.sum((yv[m] - yv[m].mean()) ** 2)
    return 1 - ss_res / ss_tot, m.sum()


def try_gbm(X, yv, groups, nfold=10):
    try:
        from sklearn.ensemble import HistGradientBoostingRegressor
        from sklearn.model_selection import GroupKFold
    except Exception as e:
        return None, str(e)
    gkf = GroupKFold(n_splits=nfold)
    pred = np.full(len(yv), np.nan)
    for tr, te in gkf.split(X, yv, groups):
        m = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.06,
                                          max_depth=4, random_state=0)
        m.fit(X[tr], yv[tr])
        pred[te] = m.predict(X[te])
    ss_res = np.sum((yv - pred) ** 2)
    ss_tot = np.sum((yv - yv.mean()) ** 2)
    return 1 - ss_res / ss_tot, None


def part2(a):
    print()
    print("=" * 72)
    print("PART 2 - what do the 161 analytic-decision indicators predict?")
    print("=" * 72)
    blocks = json.load(open(BLOCKS))
    dec = [c for c in blocks["decisions"] if c in a.columns]
    X = a[dec].apply(pd.to_numeric, errors="coerce").fillna(0.0).values.astype(float)
    keep = X.std(0) > 0
    X = X[:, keep]
    names = [c for c, k in zip(dec, keep) if k]
    groups = a.u_teamid.values
    print("design matrix: %d models x %d non-constant decision indicators"
          % X.shape)
    print("cross-validation: GroupKFold by team (%d teams), 10 folds\n"
          % len(np.unique(groups)))

    outcomes = {
        "estimate  AME_Z": a.AME_Z.values,
        "estimate  AME_Z (winsorised 1%)": np.clip(
            a.AME_Z.values, *np.percentile(a.AME_Z.values, [1, 99])),
        "precision log SE_Z": np.log(a.se_z.values),
        "|z| statistic": np.abs(a.AME_Z.values / a.se_z.values),
        "conclusion is 'not significant' (0/1)": (
            (a.AME_Z - Z95 * a.se_z < 0) & (a.AME_Z + Z95 * a.se_z > 0)
        ).astype(float).values,
    }
    print("%-40s %10s %10s %10s %10s" %
          ("outcome", "ridge R2", "perm null", "GBM R2", "perm null"))
    for name, yv in outcomes.items():
        lam = 10.0
        r2, n_used = grouped_cv_r2(X, yv, groups, lam)
        perms = []
        for _ in range(20):
            yp = yv.copy()
            RNG.shuffle(yp)
            perms.append(grouped_cv_r2(X, yp, groups, lam)[0])
        g, err = try_gbm(X, yv, groups)
        gperm = None
        if g is not None:
            gp = []
            for _ in range(5):
                yp = yv.copy()
                RNG.shuffle(yp)
                gp.append(try_gbm(X, yp, groups)[0])
            gperm = np.mean(gp)
        print("%-40s %10.4f %10.4f %10s %10s"
              % (name, r2, np.mean(perms),
                 "%.4f" % g if g is not None else "n/a",
                 "%.4f" % gperm if gperm is not None else "n/a"))
    print("\n  R2 is out-of-fold and can be negative; a negative value means the")
    print("  model predicts worse than the grand mean on unseen teams.")

    print("\n  strongest ridge coefficients for log SE_Z (standardised X):")
    yv = np.log(a.se_z.values)
    Xs = (X - X.mean(0)) / np.where(X.std(0) > 0, X.std(0), 1)
    b, _ = ridge_fit(Xs, yv, 10.0)
    o = np.argsort(-np.abs(b))[:15]
    for i in o:
        print("     %-28s %+.3f" % (names[i], b[i]))


if __name__ == "__main__":
    a = load()
    part1(a)
    part2(a)
