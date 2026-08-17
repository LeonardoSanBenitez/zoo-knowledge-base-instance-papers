"""Which estimate of the true between-model heterogeneity tau do I believe?

01 and 03 produced three incompatible numbers on the same 1,252 models:
    DerSimonian-Laird (one level)        tau = 0.0036
    moment split on team means           tau_between = 0.0094  (> the total!)
    two-level EM                         tau = 0.0123
A between-team component larger than the total is arithmetically impossible, so
at least one estimator is broken on this data. This script finds out which.

The suspect is a feature of the real data that the 02 simulation did NOT have:
    corr(log SE, |AME_Z|) = +0.50
i.e. imprecise models are also the ones with big estimates. DerSimonian-Laird
assumes the effect and its variance are independent; when they are not, the
inverse-variance weights systematically downweight exactly the deviating
observations, and tau^2 is pulled toward the precise cluster.

Estimators compared: DerSimonian-Laird, Paule-Mandel (iterative, generalised Q),
REML (Newton on the profile likelihood), and a simple untransformed
variance-of-effects minus mean-sampling-variance moment estimator.

The test: simulate data with a KNOWN tau and a tunable effect/precision
correlation, using the empirical SE distribution, and see which estimators
survive.
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "cri_model_level.csv")
Z95 = 1.959964


# ------------------------------------------------------------- estimators
def dl(y, v):
    w = 1 / v
    mu = (w * y).sum() / w.sum()
    Q = (w * (y - mu) ** 2).sum()
    C = w.sum() - (w ** 2).sum() / w.sum()
    return max(0.0, (Q - (len(y) - 1)) / C)


def pm(y, v, lo=0.0, hi=None, it=200):
    """Paule-Mandel: solve sum w_i (y_i - mu_w)^2 = k-1 for tau^2, w = 1/(v+tau2)."""
    if hi is None:
        hi = max(1e-12, np.var(y, ddof=1) * 50)

    def gq(t2):
        w = 1 / (v + t2)
        mu = (w * y).sum() / w.sum()
        return (w * (y - mu) ** 2).sum() - (len(y) - 1)
    if gq(lo) <= 0:
        return 0.0
    if gq(hi) > 0:
        return hi
    for _ in range(it):
        mid = 0.5 * (lo + hi)
        if gq(mid) > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def reml(y, v, it=500, tol=1e-16):
    """REML for the one-level random-effects model, fixed-point iteration."""
    t2 = max(1e-12, np.var(y, ddof=1) - v.mean())
    for _ in range(it):
        w = 1 / (v + t2)
        mu = (w * y).sum() / w.sum()
        num = (w ** 2 * ((y - mu) ** 2 - v)).sum() + 1 / w.sum()
        den = (w ** 2).sum()
        nt = max(0.0, num / den)
        if abs(nt - t2) < tol:
            return nt
        t2 = nt
    return t2


def naive(y, v):
    return max(0.0, np.var(y, ddof=1) - v.mean())


EST = {"DL": dl, "PM": pm, "REML": reml, "naive-moment": naive}


# ------------------------------------------------------------- simulation
def simulate(se, true_tau, rho_mode, rng):
    """rho_mode: 'none'  -> true effects independent of SE
                 'scale' -> true effect SD proportional to SE^0.5 (so big-SE
                            models really do have bigger true effects), while
                            keeping the MARGINAL true-effect variance = tau^2
    """
    n = len(se)
    if rho_mode == "none":
        theta = rng.normal(0, true_tau, n)
    else:
        s = np.sqrt(se / se.mean())
        s = s / np.sqrt((s ** 2).mean())       # keep mean(s^2)=1 => Var(theta)=tau^2
        theta = rng.normal(0, true_tau * s)
    return theta + rng.normal(0, se)


def main():
    d = pd.read_csv(DATA, low_memory=False)
    a = d[d.AME_Z.notna() & (d.u_teamid != 0)].copy()
    a["se_z"] = (a.upper_Z - a.lower_Z) / (2 * Z95)
    a = a[np.isfinite(a.se_z) & (a.se_z > 0)]
    y, se, team = a.AME_Z.values, a.se_z.values, a.u_teamid.values
    v = se ** 2

    print("OBSERVED DATA, n = %d" % len(y))
    print("  corr(log SE, |AME_Z|)   = %+.3f" % np.corrcoef(np.log(se), np.abs(y))[0, 1])
    print("  corr(log SE, log|AME_Z|)= %+.3f"
          % np.corrcoef(np.log(se), np.log(np.abs(y) + 1e-12))[0, 1])
    print("  slope of log|AME_Z| on log SE = %.3f"
          % np.polyfit(np.log(se), np.log(np.abs(y) + 1e-12), 1)[0])
    print("  (slope 1.0 would mean the z-statistic is constant: every model")
    print("   equally 'significant' regardless of precision)\n")
    print("  tau estimates on the real data:")
    for name, f in EST.items():
        t2 = f(y, v)
        print("    %-13s tau = %.5f   (tau^2 = %.3e)" % (name, np.sqrt(t2), t2))

    print("\n  trimmed at SE <= p95 (n=%d):" % (se <= np.percentile(se, 95)).sum())
    m = se <= np.percentile(se, 95)
    for name, f in EST.items():
        print("    %-13s tau = %.5f" % (name, np.sqrt(f(y[m], v[m]))))

    print("\nSIMULATION: which estimator recovers a KNOWN tau under this SE distribution?")
    rng = np.random.default_rng(7)
    for rho_mode in ("none", "scale"):
        print("  effect/precision coupling: %s" % rho_mode)
        for true_tau in (0.0, 0.004, 0.012, 0.040):
            res = {k: [] for k in EST}
            cors = []
            for _ in range(300):
                yy = simulate(se, true_tau, rho_mode, rng)
                for k, f in EST.items():
                    res[k].append(np.sqrt(f(yy, v)))
                cors.append(np.corrcoef(np.log(se), np.abs(yy))[0, 1])
            print("    true tau=%.3f  corr(logSE,|y|)=%+.2f  " % (true_tau, np.mean(cors))
                  + "  ".join("%s=%.4f" % (k, np.mean(res[k])) for k in EST))

    print("\nTWO-LEVEL, done properly: PM applied to team means")
    t2 = pm(y, v)
    rows = []
    for g in np.unique(team):
        mm = team == g
        w = 1 / (v[mm] + t2)
        rows.append((g, mm.sum(), (w * y[mm]).sum() / w.sum(), 1 / w.sum()))
    tm = pd.DataFrame(rows, columns=["team", "n", "mean", "var"])
    t2b = pm(tm["mean"].values, tm["var"].values)
    print("  one-level PM tau        = %.5f" % np.sqrt(t2))
    print("  between-team PM tau_b   = %.5f  (from %d team means)"
          % (np.sqrt(t2b), len(tm)))
    print("  between-team share      = %.2f" % (t2b / t2 if t2 > 0 else np.nan))
    print("\n  most extreme team means:")
    print(tm.reindex(tm["mean"].abs().sort_values(ascending=False).index)
            .head(8).to_string(index=False, float_format=lambda x: "%.5f" % x))


if __name__ == "__main__":
    main()
