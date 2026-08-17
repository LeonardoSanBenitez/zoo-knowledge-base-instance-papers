"""Two controls that 07 needs before its two headlines can be quoted.

07 headline A: "conditioning on the estimand-defining choices, or on team,
    explains none of the heterogeneity -- the real within-cell tau sits inside
    the band produced by random partitions of the same sizes."
    MISSING CONTROL: does that comparison have any POWER? If the pooled
    within-cell Paule-Mandel estimator cannot detect heterogeneity structure
    that is really there, 'inside the band' means 'the instrument is blind',
    not 'there is nothing to see'. Positive control below: build data in which
    a known fraction of tau^2 is between-cell, and check the test sees it.

07 headline B: "analytic decisions predict precision (out-of-team R2 = 0.16)
    and predict the estimate not at all (R2 < 0)."
    MISSING CONTROL: the ridge penalty was fixed at lambda = 10 with an
    unstandardised design matrix, which is arbitrary and could manufacture the
    negative R2. Below: standardise, sweep lambda over 8 orders of magnitude,
    and report the best achievable out-of-fold R2 for every outcome. A negative
    best-case is a result; a negative untuned case is a bug.
"""
import os, json
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "cri_model_level.csv")
BLOCKS = os.path.join(HERE, "..", "data", "column_blocks.json")
Z95 = 1.959964
RNG = np.random.default_rng(20260812)


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
    return np.sqrt(sum(n * t for n, t in t2s) / tot) if t2s else np.nan


def load():
    d = pd.read_csv(DATA, low_memory=False)
    a = d[d.AME_Z.notna() & (d.u_teamid != 0)].copy()
    a["se_z"] = (a.upper_Z - a.lower_Z) / (2 * Z95)
    a = a[np.isfinite(a.se_z) & (a.se_z > 0)].copy()
    a["v"] = a.se_z ** 2
    return a


# ---------------------------------------------------------------- control A
def control_a(a, nrep=200):
    print("=" * 74)
    print("CONTROL A - power of the 'conditioning explains nothing' test")
    print("=" * 74)
    se = a.se_z.values
    v = a.v.values
    lab_team = a.groupby(["u_teamid"]).ngroup().values
    sizes = pd.Series(lab_team).value_counts().values
    TAU = 0.0187                                   # the observed one-level PM tau

    def null_band(y):
        out = []
        for _ in range(nrep):
            perm = np.concatenate([np.full(s, i) for i, s in enumerate(sizes)])
            RNG.shuffle(perm)
            out.append(pooled_within_tau(y, v, perm))
        out = np.array([x for x in out if np.isfinite(x)])
        return out

    print("%-52s %9s %9s %9s %7s" %
          ("data generating process", "real tau", "null mean", "null 2.5%", "detect"))
    for frac in (0.0, 0.25, 0.50, 0.75, 0.95, 1.00):
        t2b, t2w = frac * TAU ** 2, (1 - frac) * TAU ** 2
        u = RNG.normal(0, np.sqrt(t2b), len(sizes))[lab_team]
        y = u + RNG.normal(0, np.sqrt(t2w), len(se)) + RNG.normal(0, se)
        real = pooled_within_tau(y, v, lab_team)
        nb = null_band(y)
        det = real < np.percentile(nb, 2.5)
        print("  %-50s %9.5f %9.5f %9.5f %7s"
              % ("%d%% of tau^2 is between-cell" % (100 * frac),
                 real, nb.mean(), np.percentile(nb, 2.5), "YES" if det else "no"))
    print("\n  If 'YES' only appears at high fractions, the test can only detect")
    print("  strong structure and 'inside the band' on the real data is weak")
    print("  evidence, not a null result.")

    # the real data, restated with the same band for reference
    y = a.AME_Z.values
    real = pooled_within_tau(y, v, lab_team)
    nb = null_band(y)
    print("\n  REAL DATA, team partition: real tau = %.5f, null band 2.5%%-97.5%% "
          "= %.5f-%.5f, real percentile = %.0f"
          % (real, np.percentile(nb, 2.5), np.percentile(nb, 97.5),
             100 * (nb < real).mean()))


# ---------------------------------------------------------------- control B
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


def control_b(a):
    print()
    print("=" * 74)
    print("CONTROL B - ridge penalty sweep, standardised design")
    print("=" * 74)
    blocks = json.load(open(BLOCKS))
    dec = [c for c in blocks["decisions"] if c in a.columns]
    X = a[dec].apply(pd.to_numeric, errors="coerce").fillna(0.0).values.astype(float)
    keep = X.std(0) > 0
    X = X[:, keep]
    X = (X - X.mean(0)) / X.std(0)
    groups = a.u_teamid.values
    ug = np.unique(groups)
    RNG.shuffle(ug)
    folds = np.array_split(ug, 10)

    outcomes = {
        "estimate AME_Z": a.AME_Z.values,
        "estimate AME_Z winsorised 1%": np.clip(a.AME_Z.values,
                                                *np.percentile(a.AME_Z.values, [1, 99])),
        "sign of estimate (+1/-1)": np.sign(a.AME_Z.values),
        "precision log SE_Z": np.log(a.se_z.values),
        "|z|": np.abs(a.AME_Z.values / a.se_z.values),
        "not significant (0/1)": ((a.AME_Z - Z95 * a.se_z < 0) &
                                  (a.AME_Z + Z95 * a.se_z > 0)).astype(float).values,
    }
    lams = np.geomspace(1e-2, 1e6, 17)
    print("%-30s %10s %10s %12s" % ("outcome", "best R2", "at lambda", "perm-null R2"))
    for name, y in outcomes.items():
        r2s = [ridge_cv(X, y, groups, l, folds) for l in lams]
        i = int(np.argmax(r2s))
        yp = y.copy()
        RNG.shuffle(yp)
        pn = max(ridge_cv(X, yp, groups, l, folds) for l in lams)
        print("%-30s %10.4f %10.1f %12.4f" % (name, r2s[i], lams[i], pn))
    print("\n  'best R2' is optimistically selected (lambda chosen on the same")
    print("  folds it is scored on), so it is an UPPER bound. The permutation")
    print("  column is selected the same optimistic way, so the comparison is fair.")

    print("\n  same sweep for log SE_Z, split by predictor block:")
    for blockname in ("decisions", "researcher"):
        cols = [c for c in blocks[blockname] if c in a.columns]
        Xb = a[cols].apply(pd.to_numeric, errors="coerce").fillna(0.0).values.astype(float)
        k = Xb.std(0) > 0
        if k.sum() == 0:
            continue
        Xb = (Xb[:, k] - Xb[:, k].mean(0)) / Xb[:, k].std(0)
        y = np.log(a.se_z.values)
        best = max(ridge_cv(Xb, y, groups, l, folds) for l in lams)
        y2 = a.AME_Z.values
        best2 = max(ridge_cv(Xb, y2, groups, l, folds) for l in lams)
        print("    %-12s (%3d predictors): log SE_Z R2 = %+.4f | AME_Z R2 = %+.4f"
              % (blockname, k.sum(), best, best2))


if __name__ == "__main__":
    a = load()
    control_a(a)
    control_b(a)
