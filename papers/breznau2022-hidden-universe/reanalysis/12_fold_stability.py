"""How stable is the headline R^2 to the fold assignment?

08 reported R^2 = 0.2068 for log standard error; 11, with a different shuffle of
the 71 teams into 10 folds, reported 0.1716 for the same model on the same data.
A 20% swing from nothing but the fold split means the point estimate is not the
right object to quote. This script repeats the whole grouped-CV procedure over
many random fold assignments and reports the distribution.

Rule this enforces: with 71 clusters and 10 folds, each held-out fold contains
about 7 teams, so a single cross-validated R^2 is itself an estimate with
non-trivial variance. Quote a range.
"""
import os, json
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "cri_model_level.csv")
BLOCKS = os.path.join(HERE, "..", "data", "column_blocks.json")
Z95 = 1.959964
LAMS = np.geomspace(1e-2, 1e6, 17)
NREP = 40


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


def main():
    d = pd.read_csv(DATA, low_memory=False)
    a = d[d.AME_Z.notna() & (d.u_teamid != 0)].copy()
    a["se_z"] = (a.upper_Z - a.lower_Z) / (2 * Z95)
    a = a[np.isfinite(a.se_z) & (a.se_z > 0)].copy()
    blocks = json.load(open(BLOCKS))
    dec = [c for c in blocks["decisions"] if c in a.columns]
    X = a[dec].apply(pd.to_numeric, errors="coerce").fillna(0.0).values.astype(float)
    k = X.std(0) > 0
    X = (X[:, k] - X[:, k].mean(0)) / X[:, k].std(0)
    groups = a.u_teamid.values

    outcomes = {
        "log standard error": np.log(a.se_z.values),
        "the estimate (AME_Z)": a.AME_Z.values,
        "conclusion is 'null' (0/1)": (((a.AME_Z - Z95 * a.se_z) < 0) &
                                       ((a.AME_Z + Z95 * a.se_z) > 0)).astype(float).values,
    }
    print("grouped 10-fold CV by team, %d random fold assignments, ridge penalty"
          % NREP)
    print("swept over 1e-2..1e6 and selected optimistically on each split\n")
    print("%-30s %8s %8s %8s %8s %8s" %
          ("outcome", "mean", "sd", "min", "max", "perm"))
    for name, y in outcomes.items():
        r2s, perms = [], []
        for rep in range(NREP):
            rng = np.random.default_rng(1000 + rep)
            ug = np.unique(groups).copy()
            rng.shuffle(ug)
            folds = np.array_split(ug, 10)
            r2s.append(max(ridge_cv(X, y, groups, l, folds) for l in LAMS))
            if rep < 10:
                yp = y.copy()
                rng.shuffle(yp)
                perms.append(max(ridge_cv(X, yp, groups, l, folds) for l in LAMS))
        r2s = np.array(r2s)
        print("%-30s %8.4f %8.4f %8.4f %8.4f %8.4f"
              % (name, r2s.mean(), r2s.std(), r2s.min(), r2s.max(), np.mean(perms)))

    print("\nleave-one-team-out (71 folds, no fold randomness at all):")
    ug = np.unique(groups)
    folds = [np.array([g]) for g in ug]
    for name, y in outcomes.items():
        print("   %-28s %.4f" % (name, max(ridge_cv(X, y, groups, l, folds) for l in LAMS)))


if __name__ == "__main__":
    main()
