"""Diagnostics for 01_dispersion.py, which produced two mutually contradictory
numbers and therefore cannot be believed yet:

    I^2 = 0.934            "93% of variability is real heterogeneity"
    tau^2 / Var(y) = 0.002 "0.2% of variability is real heterogeneity"
    mean(SE^2) / Var(y) = 1.021   -- a share above 1, which is impossible

All three are ratios over a wildly skewed standard-error distribution. This
script finds out which of them is the artifact, by:

  1. describing the SE distribution and checking the CIs are internally
     consistent (z == AME/SE);
  2. identifying the models that dominate the variance and printing what they
     actually are;
  3. re-running the tau^2 estimators on the EMPIRICAL SE distribution with a
     known injected tau^2 (the synthetic test in 01 used a tame uniform SE
     distribution and therefore did not test the case that matters);
  4. recomputing everything with the 1% most imprecise models trimmed.
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "cri_model_level.csv")
Z95 = 1.959964


def load():
    d = pd.read_csv(DATA, low_memory=False)
    a = d[d.AME_Z.notna() & (d.u_teamid != 0)].copy()
    a["se_z"] = (a.upper_Z - a.lower_Z) / (2 * Z95)
    a["se_raw"] = (a.upper - a.lower) / (2 * Z95)
    return a


def dl_tau2(y, v):
    w = 1.0 / v
    mu = np.sum(w * y) / np.sum(w)
    Q = np.sum(w * (y - mu) ** 2)
    k = len(y)
    C = np.sum(w) - np.sum(w ** 2) / np.sum(w)
    return max(0.0, (Q - (k - 1)) / C)


def i2_of(y, v, t2):
    w = 1.0 / v
    k = len(y)
    s2 = (k - 1) * np.sum(w) / (np.sum(w) ** 2 - np.sum(w ** 2))
    return t2 / (t2 + s2), s2


def main():
    a = load()
    se = a.se_z.values
    ok = np.isfinite(se) & (se > 0)
    a = a[ok]
    se = a.se_z.values
    y = a.AME_Z.values

    print("1. STANDARD ERROR DISTRIBUTION (standardized scale), n =", len(a))
    qs = [0, 1, 5, 25, 50, 75, 95, 99, 100]
    print("   percentiles of SE_Z:",
          dict(zip(qs, np.round(np.percentile(se, qs), 6))))
    print("   mean SE_Z = %.6f, median = %.6f  -> ratio %.1f"
          % (se.mean(), np.median(se), se.mean() / np.median(se)))
    print("   mean SE^2 = %.3e, median SE^2 = %.3e -> ratio %.0f"
          % ((se ** 2).mean(), np.median(se ** 2),
             (se ** 2).mean() / np.median(se ** 2)))
    print("   => the arithmetic mean of SE^2 is NOT a summary of this "
          "distribution; the >100% share in 01.D is that artifact.")

    zc = a.AME_Z.values / se
    zr = a.z.values
    finite = np.isfinite(zc) & np.isfinite(zr)
    print("\n   internal consistency: corr(AME_Z/SE_Z, reported z) = %.4f on n=%d"
          % (np.corrcoef(zc[finite], zr[finite])[0, 1], finite.sum()))
    print("   max |AME_Z/SE_Z - z| = %.4f" % np.nanmax(np.abs(zc[finite] - zr[finite])))

    print("\n2. WHICH MODELS DOMINATE THE VARIANCE")
    ss = (y - y.mean()) ** 2
    idx = np.argsort(-ss)[:10]
    cols = ["u_teamid", "DV", "main_IV_type", "main_IV_measurement", "package",
            "num_countries", "AME", "AME_Z", "se_z", "p"]
    t = a.iloc[idx][[c for c in cols if c in a.columns]].copy()
    t["pct_of_total_SS"] = 100 * ss[idx] / ss.sum()
    print(t.to_string(index=False, float_format=lambda x: "%.5f" % x))
    print("   models in the top-10-variance list belong to %d distinct teams: %s"
          % (a.iloc[idx].u_teamid.nunique(), sorted(a.iloc[idx].u_teamid.unique())))
    big = np.abs(y - y.mean()) > 0.1
    print("   n models with |AME_Z - mean| > 0.10 : %d (%.2f%% of models, %d teams)"
          % (big.sum(), 100 * big.mean(), a[big].u_teamid.nunique()))
    print("   their median SE_Z = %.4f vs %.4f for the rest"
          % (np.median(se[big]), np.median(se[~big])))

    print("\n3. ESTIMATOR TEST ON THE EMPIRICAL SE DISTRIBUTION")
    rng = np.random.default_rng(11)
    for true_tau in (0.0, 0.002, 0.010, 0.050):
        hats, i2s = [], []
        for _ in range(200):
            s = rng.choice(se, size=len(se), replace=True)
            yy = rng.normal(0, true_tau, len(s)) + rng.normal(0, s)
            t2 = dl_tau2(yy, s ** 2)
            hats.append(np.sqrt(t2))
            i2s.append(i2_of(yy, s ** 2, t2)[0])
        print("   true tau = %.3f -> DL tau_hat = %.4f (sd %.4f), I^2 = %.3f"
              % (true_tau, np.mean(hats), np.std(hats), np.mean(i2s)))
    print("   => read off whether DL is biased under THIS SE distribution.")

    print("\n4. TRIMMING THE MOST IMPRECISE MODELS")
    for cut in (100, 99, 95, 90):
        thr = np.percentile(se, cut)
        m = se <= thr
        t2 = dl_tau2(y[m], se[m] ** 2)
        i2, s2 = i2_of(y[m], se[m] ** 2, t2)
        print("   keep SE <= p%-3d (n=%4d): SD(y)=%.5f  tau=%.5f  typical SE=%.5f"
              "  I^2=%.3f  tau^2/Var=%.4f"
              % (cut, m.sum(), np.std(y[m], ddof=1), np.sqrt(t2), np.sqrt(s2),
                 i2, t2 / np.var(y[m], ddof=1)))

    print("\n5. THE NUMBER THAT SHOULD BE QUOTED")
    t2 = dl_tau2(y, se ** 2)
    i2, s2 = i2_of(y, se ** 2, t2)
    print("   typical (Higgins) within-model sampling SE = %.5f" % np.sqrt(s2))
    print("   between-model true heterogeneity SD tau    = %.5f" % np.sqrt(t2))
    print("   ratio tau / typical SE                     = %.2f" % (np.sqrt(t2 / s2)))
    print("   90%% prediction interval for the true effect of a randomly")
    print("   chosen analysis: [%.4f, %.4f] in SD units of the outcome"
          % (-1.645 * np.sqrt(t2), 1.645 * np.sqrt(t2)))


if __name__ == "__main__":
    main()
