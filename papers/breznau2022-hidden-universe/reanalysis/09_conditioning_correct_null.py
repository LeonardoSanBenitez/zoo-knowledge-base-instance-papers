"""Corrected version of 07 PART 1 / 08 CONTROL A.

The permutation null used there is WRONG and 08 caught it: it flagged 'detect'
even when 0% of the heterogeneity was between-cell. Reason: shuffling cell
labels destroys the association between cell membership and STANDARD ERROR, not
only the association between cell membership and effect. Teams are internally
homogeneous in precision (a team that used MLwiN on 13 countries produced large
standard errors for every one of its models), so a permuted cell mixes precise
and imprecise models and the pooled within-cell Paule-Mandel statistic changes
for a reason that has nothing to do with the hypothesis being tested.

Correct null: keep the real cell labels and the real standard errors, and
simulate the effects from a model with NO between-cell structure:
    y_i = mu + theta_i + e_i,  theta_i ~ N(0, tau^2) iid,  e_i ~ N(0, SE_i^2)
Then the statistic 'pooled within-cell tau' has a null distribution generated
under exactly the hypothesis 'this partition explains nothing', with every
nuisance feature of the design held fixed.

Power is then read off by re-running with a known between-cell fraction.

This file supersedes 07 PART 1. The earlier numbers must not be quoted.
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "cri_model_level.csv")
Z95 = 1.959964
RNG = np.random.default_rng(31415)
NSIM = 400


def pm(y, v, it=160):
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


def pooled_within_tau(y, v, labels, minn=3):
    t2s, tot = [], 0
    for lab in np.unique(labels):
        m = labels == lab
        if m.sum() < minn:
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


def main():
    a = load()
    y, v, se = a.AME_Z.values, a.v.values, a.se_z.values
    tau_all = np.sqrt(pm(y, v))
    print("one-level Paule-Mandel tau on all %d models = %.5f\n" % (len(y), tau_all))

    partitions = {
        "team": ["u_teamid"],
        "DV": ["DV"],
        "DV x measure": ["DV", "main_IV_type"],
        "DV x measure x effect": ["DV", "main_IV_type", "main_IV_effect"],
        "DV x measure x effect x n countries":
            ["DV", "main_IV_type", "main_IV_effect", "num_countries"],
    }

    def sim_null(labels, frac_between):
        t2b = frac_between * tau_all ** 2
        t2w = (1 - frac_between) * tau_all ** 2
        codes = pd.Series(labels).astype("category").cat.codes.values
        u = RNG.normal(0, np.sqrt(t2b), codes.max() + 1)[codes]
        return u + RNG.normal(0, np.sqrt(t2w), len(se)) + RNG.normal(0, se)

    print("%-38s %8s %9s %9s %7s" %
          ("partition", "observed", "null mean", "null 2.5%", "p(one-sided)"))
    results = {}
    for name, keys in partitions.items():
        labels = a.groupby(keys).ngroup().values
        obs = pooled_within_tau(y, v, labels)
        null = np.array([pooled_within_tau(sim_null(labels, 0.0), v, labels)
                         for _ in range(NSIM)])
        null = null[np.isfinite(null)]
        p = (null <= obs).mean()
        results[name] = (labels, obs, null)
        print("%-38s %8.5f %9.5f %9.5f %10.3f"
              % (name, obs, null.mean(), np.percentile(null, 2.5), p))
    print("\n  p = fraction of no-structure simulations at or below the observed")
    print("  statistic. Small p means the partition really does absorb")
    print("  heterogeneity. p near 0.5 means it absorbs nothing.\n")

    print("POWER: same test on simulated data with a KNOWN between-cell share")
    for name in ("team", "DV x measure x effect"):
        labels, _, null = results[name]
        lo = np.percentile(null, 2.5)
        print("  partition = %s (reject if statistic < %.5f)" % (name, lo))
        for frac in (0.0, 0.10, 0.25, 0.50, 0.75, 1.00):
            stats = np.array([pooled_within_tau(sim_null(labels, frac), v, labels)
                              for _ in range(120)])
            stats = stats[np.isfinite(stats)]
            print("     %3d%% between-cell -> statistic %.5f (sd %.5f), "
                  "detected in %3.0f%% of runs"
                  % (100 * frac, stats.mean(), stats.std(), 100 * (stats < lo).mean()))

    print("\nDIRECT ESTIMATE of the between-cell share, by matching the statistic")
    for name in ("team", "DV x measure x effect x n countries"):
        labels, obs, _ = results[name]
        grid = np.linspace(0, 1, 11)
        curve = []
        for f in grid:
            s = np.array([pooled_within_tau(sim_null(labels, f), v, labels)
                          for _ in range(80)])
            curve.append(np.nanmean(s))
        curve = np.array(curve)
        order = np.argsort(curve)
        if curve[order][0] <= obs <= curve[order][-1]:
            est = np.interp(obs, curve[order], grid[order])
            print("  %-40s observed %.5f -> between-cell share ~ %.2f"
                  % (name, obs, est))
        else:
            print("  %-40s observed %.5f is OUTSIDE [%.5f, %.5f]: share ~ %s"
                  % (name, obs, curve.min(), curve.max(),
                     "0.00 (or the model is misspecified)" if obs > curve.max()
                     else "1.00"))


if __name__ == "__main__":
    main()
