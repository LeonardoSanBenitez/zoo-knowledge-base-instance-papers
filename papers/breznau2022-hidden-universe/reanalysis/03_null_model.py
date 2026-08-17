"""Can the 'hidden universe of uncertainty' be generated WITHOUT any researcher
idiosyncrasy at all?

Breznau et al. 2022 headline: across 1,253 models from 71 teams testing the same
hypothesis on the same data, 25.4% of results were significant-negative, 57.7%
null, 16.9% significant-positive (inverse-team-size weighted), and 95.2% of the
variance in the estimates is unexplained by any identified analytic decision.
They read this as idiosyncratic researcher variability.

02_diagnostics.py established two facts that make a much duller explanation
available:
  * the standard errors of these 1,253 models span 4e-05 to 1.43 -- a factor of
    ~36,000 -- so the models differ enormously in PRECISION;
  * the precision-weighted true between-model heterogeneity is tau = 0.0036 SD
    units, tiny in absolute terms though 3.75x the typical sampling SE.

So: take each model's OWN reported standard error, draw its estimate from a
common true effect, and see whether the famous three percentages fall out.
If they do, the distribution of conclusions is a fact about the precision the
analysts chose, not about what they concluded.

Four nulls, in increasing generosity:
  N0  every model estimates exactly mu (precision-weighted mean), no heterogeneity
  N1  N0 + the estimated true heterogeneity tau (one level)
  N2  N1 with heterogeneity split between-team / within-team
  N3  N2 + team-specific true effects drawn from the fitted between-team variance
Plus a positive control: a world with LARGE true heterogeneity (tau = 0.05),
which must NOT reproduce the data if the test has any power.
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "cri_model_level.csv")
Z95 = 1.959964
NSIM = 2000


def load():
    d = pd.read_csv(DATA, low_memory=False)
    a = d[d.AME_Z.notna() & (d.u_teamid != 0)].copy()
    a["se_z"] = (a.upper_Z - a.lower_Z) / (2 * Z95)
    a = a[np.isfinite(a.se_z) & (a.se_z > 0)]
    return a


def dl_tau2(y, v):
    w = 1.0 / v
    mu = np.sum(w * y) / np.sum(w)
    Q = np.sum(w * (y - mu) ** 2)
    C = np.sum(w) - np.sum(w ** 2) / np.sum(w)
    return max(0.0, (Q - (len(y) - 1)) / C), mu


def shares(y, se, w):
    """weighted %neg / %ns / %pos using each model's own 95% CI"""
    lo, hi = y - Z95 * se, y + Z95 * se
    neg, pos = hi < 0, lo > 0
    ns = ~(neg | pos)
    tot = w.sum()
    return (100 * (w * neg).sum() / tot,
            100 * (w * ns).sum() / tot,
            100 * (w * pos).sum() / tot)


def main():
    a = load()
    y = a.AME_Z.values
    se = a.se_z.values
    team = a.u_teamid.values
    w = a.groupby("u_teamid").u_teamid.transform("size").rdiv(1.0).values
    n = len(y)

    tau2, mu = dl_tau2(y, se ** 2)
    tau = np.sqrt(tau2)
    obs = shares(y, se, w)
    print("n = %d models, %d teams" % (n, a.u_teamid.nunique()))
    print("precision-weighted mean effect mu = %.5f" % mu)
    print("DL tau = %.5f\n" % tau)
    print("OBSERVED      neg %.2f  ns %.2f  pos %.2f   (published 25.4 / 57.7 / 16.9)"
          % obs)

    # split tau^2 between and within team by a moment decomposition of the
    # precision-weighted team means
    tmeans, tvars = {}, {}
    for g in np.unique(team):
        m = team == g
        ww = 1.0 / (se[m] ** 2 + tau2)
        tmeans[g] = np.sum(ww * y[m]) / np.sum(ww)
        tvars[g] = 1.0 / np.sum(ww)
    tm = np.array(list(tmeans.values()))
    tv = np.array(list(tvars.values()))
    tau2_b = max(0.0, np.var(tm, ddof=1) - tv.mean())
    tau2_w = max(0.0, tau2 - tau2_b)
    print("   between-team share of true heterogeneity: %.2f (tau_b = %.5f, tau_w = %.5f)\n"
          % (tau2_b / tau2 if tau2 > 0 else float("nan"),
             np.sqrt(tau2_b), np.sqrt(tau2_w)))

    rng = np.random.default_rng(2026)
    gidx = {g: i for i, g in enumerate(np.unique(team))}
    tcode = np.array([gidx[g] for g in team])
    ng = len(gidx)

    def run(name, gen):
        out = np.array([shares(gen(), se, w) for _ in range(NSIM)])
        m, s = out.mean(0), out.std(0)
        hit = [(obs[i] >= np.percentile(out[:, i], 2.5)) and
               (obs[i] <= np.percentile(out[:, i], 97.5)) for i in range(3)]
        print("%-46s neg %5.2f+-%.2f  ns %5.2f+-%.2f  pos %5.2f+-%.2f   obs in 95%% band: %s"
              % (name, m[0], s[0], m[1], s[1], m[2], s[2],
                 "".join("Y" if h else "n" for h in hit)))
        return m, s

    print("SIMULATED (each model keeps its OWN reported standard error)")
    run("N0  common effect mu, no heterogeneity",
        lambda: rng.normal(mu, se))
    run("N1  mu + one-level tau = %.4f" % tau,
        lambda: rng.normal(mu, np.sqrt(se ** 2 + tau2)))
    run("N2  mu + between/within split",
        lambda: rng.normal(0, np.sqrt(tau2_b), ng)[tcode]
                + rng.normal(mu, np.sqrt(se ** 2 + tau2_w)))
    run("N3  team means fixed at their observed values",
        lambda: np.array([tmeans[g] for g in team]) + rng.normal(0, se))
    print("POSITIVE CONTROL (must fail, or the test has no power)")
    run("PC  mu + tau = 0.050 (14x the estimate)",
        lambda: rng.normal(mu, np.sqrt(se ** 2 + 0.05 ** 2)))
    run("PC  mu = 0, no heterogeneity, ALL SE set to median",
        lambda: rng.normal(mu, np.median(se)))

    # how much of the spread in CONCLUSIONS is precision alone?
    print("\nDECOMPOSITION OF THE CONCLUSION SPREAD")
    print("  If every model had the median SE (%.5f) and the observed estimates:"
          % np.median(se))
    print("    -> neg %.2f  ns %.2f  pos %.2f" % shares(y, np.full(n, np.median(se)), w))
    print("  If every model had its own SE and the SAME estimate mu:")
    print("    -> neg %.2f  ns %.2f  pos %.2f" % shares(np.full(n, mu), se, w))
    print("  Observed:")
    print("    -> neg %.2f  ns %.2f  pos %.2f" % obs)

    print("\n  correlation between log SE and |AME_Z|: %.3f"
          % np.corrcoef(np.log(se), np.abs(y))[0, 1])
    print("  correlation between log SE and being 'not significant': %.3f"
          % np.corrcoef(np.log(se),
                        ((y - Z95 * se < 0) & (y + Z95 * se > 0)).astype(float))[0, 1])


if __name__ == "__main__":
    main()
