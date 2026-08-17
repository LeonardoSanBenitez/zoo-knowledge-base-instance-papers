"""Estimate the true between-model heterogeneity tau by simulated method of
moments, matching the statistic people actually quote, instead of trusting any
one meta-analytic estimator.

04 showed the estimators disagree by 5x on this data (DL 0.0036, REML 0.0119,
PM 0.0187) and that DL in particular collapses when effect magnitude scales with
the standard error. Rather than adjudicate on theory, calibrate: for each
candidate tau, simulate theta ~ N(0, tau^2) plus each model's OWN reported
sampling error, and ask which tau reproduces

    (a) the inverse-team-size-weighted %neg / %ns / %pos = 25.4 / 57.7 / 16.9
    (b) the SD of the observed z statistics
    (c) the slope of log|estimate| on log SE (= 1 under pure sampling noise,
        flatter as tau grows)

The three targets are different functionals, so agreement between them is
evidence the one-parameter model is adequate; disagreement is evidence it is not
and is worth more than a point estimate.

Also reports what Mathur, Covington & VanderWeele's published prediction
interval [-0.014, 0.014] implies for tau, so the two papers can be compared on
one scale.
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "cri_model_level.csv")
Z95 = 1.959964
NSIM = 400


def load():
    d = pd.read_csv(DATA, low_memory=False)
    a = d[d.AME_Z.notna() & (d.u_teamid != 0)].copy()
    a["se_z"] = (a.upper_Z - a.lower_Z) / (2 * Z95)
    return a[np.isfinite(a.se_z) & (a.se_z > 0)]


def stats(y, se, w):
    lo, hi = y - Z95 * se, y + Z95 * se
    neg, pos = hi < 0, lo > 0
    ns = ~(neg | pos)
    tot = w.sum()
    z = y / se
    slope = np.polyfit(np.log(se), np.log(np.abs(y) + 1e-15), 1)[0]
    return np.array([100 * (w * neg).sum() / tot, 100 * (w * ns).sum() / tot,
                     100 * (w * pos).sum() / tot, np.std(z, ddof=1),
                     np.median(np.abs(z)), slope])


NAMES = ["%neg", "%ns", "%pos", "SD(z)", "median|z|", "slope log|y|~logSE"]


def main():
    a = load()
    y, se = a.AME_Z.values, a.se_z.values
    w = a.groupby("u_teamid").u_teamid.transform("size").rdiv(1.0).values
    obs = stats(y, se, w)
    print("OBSERVED  " + "  ".join("%s=%.3f" % (n, v) for n, v in zip(NAMES, obs)))
    print()

    rng = np.random.default_rng(99)
    grid = np.concatenate([[0.0], np.geomspace(0.001, 0.12, 26)])
    rows = []
    for tau in grid:
        S = np.array([stats(rng.normal(0, tau, len(se)) + rng.normal(0, se), se, w)
                      for _ in range(NSIM)])
        rows.append([tau] + list(S.mean(0)) + list(S.std(0)))
    R = pd.DataFrame(rows, columns=["tau"] + NAMES + [n + "_sd" for n in NAMES])
    pd.set_option("display.width", 200)
    print(R[["tau"] + NAMES].to_string(index=False, float_format=lambda x: "%.4f" % x))

    print("\nTAU THAT MATCHES EACH TARGET (linear interpolation on the grid):")
    for i, n in enumerate(NAMES):
        col = R[n].values
        t = R["tau"].values
        # monotone in tau for all these targets except %ns which decreases
        order = np.argsort(col)
        if col[order][0] <= obs[i] <= col[order][-1]:
            est = np.interp(obs[i], col[order], t[order])
            print("   %-20s observed %8.3f  ->  tau = %.4f" % (n, obs[i], est))
        else:
            print("   %-20s observed %8.3f  ->  OUT OF GRID RANGE [%.3f, %.3f]"
                  % (n, obs[i], col.min(), col.max()))

    print("\nCOMPARISON ON ONE SCALE")
    print("   Mathur et al. 2023 report a 90%% interval for population effects of")
    print("   [-0.014, 0.014]; a symmetric normal 90%% interval is +-1.645*tau,")
    print("   so their implied tau = %.4f" % (0.014 / 1.645))
    for name, t in [("DL (04)", 0.00363), ("REML (04)", 0.01185), ("PM (04)", 0.01868)]:
        print("   %-11s tau = %.4f -> 90%% interval [%+.4f, %+.4f]"
              % (name, t, -1.645 * t, 1.645 * t))

    print("\nSANITY: recover a known tau through the whole pipeline")
    for true_tau in (0.004, 0.012, 0.030):
        ysim = rng.normal(0, true_tau, len(se)) + rng.normal(0, se)
        o = stats(ysim, se, w)
        best = {}
        for i, n in enumerate(NAMES):
            col, t = R[n].values, R["tau"].values
            order = np.argsort(col)
            if col[order][0] <= o[i] <= col[order][-1]:
                best[n] = np.interp(o[i], col[order], t[order])
        print("   true tau = %.3f -> recovered " % true_tau
              + ", ".join("%s:%.4f" % (k, v) for k, v in best.items()))


if __name__ == "__main__":
    main()
