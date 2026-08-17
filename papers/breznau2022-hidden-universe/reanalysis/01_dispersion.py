"""Reanalysis 1 of Breznau et al. 2022 PNAS: how much of the 'hidden universe'
survives once each model's own sampling error is subtracted?

Runs on data/cri_model_level.csv (produced by 00_extract.py).

What it does, in order:
  A. Recover the paper's analysis sample and reproduce Fig. 1's three percentages.
  B. Report the SAME percentages unweighted, because the headline is
     inverse-team-size weighted and almost every citation drops that qualifier.
  C. Reproduce Mathur, Covington & VanderWeele (2023 PNAS) 90% range of estimates.
  D. Decompose observed dispersion into sampling error + true heterogeneity
     (DerSimonian-Laird, and a two-level version separating between-team from
     within-team true heterogeneity, fitted by REML).
  E. Outlier sensitivity: how much of the total variance is the top-k models.
  F. Self-test: recover known tau^2 from synthetic data, and confirm the
     estimator returns ~0 when heterogeneity is absent. (CONTRIBUTING rule 3:
     try to break it before believing it.)

Stdlib + numpy + pandas only.
"""
import os, json
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "cri_model_level.csv")
Z95 = 1.959964

# ---------------------------------------------------------------- estimators

def dl_tau2(y, v):
    """DerSimonian-Laird tau^2 for a random-effects meta-analysis."""
    w = 1.0 / v
    mu = np.sum(w * y) / np.sum(w)
    Q = np.sum(w * (y - mu) ** 2)
    k = len(y)
    C = np.sum(w) - np.sum(w ** 2) / np.sum(w)
    return max(0.0, (Q - (k - 1)) / C), Q, k


def i_squared(y, v, tau2):
    """Higgins' I^2 using the typical within-study variance."""
    w = 1.0 / v
    k = len(y)
    s2 = (k - 1) * np.sum(w) / (np.sum(w) ** 2 - np.sum(w ** 2))
    return tau2 / (tau2 + s2), s2


def reml_two_level(y, v, group, iters=500, tol=1e-14):
    """Two-level random-effects meta-analysis fitted by REML, block-diagonal.

    y_ij = mu + u_j + e_ij + eps_ij
      u_j   ~ N(0, tau2_b)   team-level true heterogeneity
      e_ij  ~ N(0, tau2_w)   model-within-team true heterogeneity
      eps_ij~ N(0, v_ij)     sampling error, KNOWN
    Fitted with a simple EM-flavoured fixed-point on the two variance
    components; each team is an independent block so everything is closed form.
    """
    groups = np.unique(group)
    tau2b, tau2w = np.var(y) / 3.0, np.var(y) / 3.0
    for _ in range(iters):
        num_mu = den_mu = 0.0
        for g in groups:
            m = group == g
            d = v[m] + tau2w
            a = np.sum(1.0 / d)
            # marginal precision of the block mean given tau2b
            den_mu += a / (1.0 + tau2b * a)
            num_mu += np.sum(y[m] / d) / (1.0 + tau2b * a)
        mu = num_mu / den_mu
        # E-step: posterior of u_j
        sb = sw = 0.0
        nb = nw = 0
        for g in groups:
            m = group == g
            d = v[m] + tau2w
            a = np.sum(1.0 / d)
            var_u = 1.0 / (1.0 / tau2b + a) if tau2b > 0 else 0.0
            uh = var_u * np.sum((y[m] - mu) / d) if tau2b > 0 else 0.0
            sb += uh ** 2 + var_u
            nb += 1
            r = y[m] - mu - uh
            # posterior of e_ij given r
            var_e = 1.0 / (1.0 / tau2w + 1.0 / v[m]) if tau2w > 0 else np.zeros(m.sum())
            eh = var_e * r / v[m] if tau2w > 0 else np.zeros(m.sum())
            sw += np.sum(eh ** 2 + var_e)
            nw += m.sum()
        ntau2b, ntau2w = sb / nb, sw / nw
        if abs(ntau2b - tau2b) < tol and abs(ntau2w - tau2w) < tol:
            tau2b, tau2w = ntau2b, ntau2w
            break
        tau2b, tau2w = ntau2b, ntau2w
    return mu, tau2b, tau2w


# ---------------------------------------------------------------- self-tests

def selftest(seed=0):
    rng = np.random.default_rng(seed)
    out = {}
    # 1. no heterogeneity at all
    k = 1200
    se = rng.uniform(0.002, 0.02, k)
    y = rng.normal(0.0, se)
    t2, Q, _ = dl_tau2(y, se ** 2)
    i2, _ = i_squared(y, se ** 2, t2)
    out["null_tau2"] = t2
    out["null_I2"] = i2
    # 2. known heterogeneity injected
    TRUE = 0.010 ** 2
    y2 = rng.normal(0.0, np.sqrt(TRUE), k) + rng.normal(0.0, se)
    t2b, _, _ = dl_tau2(y2, se ** 2)
    out["injected_tau2_true"] = TRUE
    out["injected_tau2_hat"] = t2b
    out["injected_ratio"] = t2b / TRUE
    # 3. two-level: known between and within
    TB, TW = 0.008 ** 2, 0.005 ** 2
    grp = np.repeat(np.arange(71), 18)[:k]
    u = rng.normal(0, np.sqrt(TB), 71)[grp]
    e = rng.normal(0, np.sqrt(TW), k)
    y3 = u + e + rng.normal(0, se)
    mu, tb, tw = reml_two_level(y3, se ** 2, grp)
    out["two_level_true"] = (TB, TW)
    out["two_level_hat"] = (tb, tw)
    out["two_level_ratio"] = (tb / TB, tw / TW)
    # 4. two-level with NO true heterogeneity -> must return ~0, not something
    y4 = rng.normal(0, se)
    _, tb0, tw0 = reml_two_level(y4, se ** 2, grp)
    out["two_level_null_hat"] = (tb0, tw0)
    out["two_level_null_as_frac_of_sampling_var"] = ((tb0 + tw0) / np.mean(se ** 2))
    return out


# ---------------------------------------------------------------- main

def main():
    d = pd.read_csv(DATA, low_memory=False)
    print("file rows", len(d), "teams", d.u_teamid.nunique())

    # --- A. recover the analysis sample -----------------------------------
    a = d[d.AME_Z.notna()]
    print("A1. drop non-converged (AME_Z missing):", len(a), "rows,",
          a.u_teamid.nunique(), "teams")
    a = a[a.u_teamid != 0].copy()
    print("A2. drop u_teamid==0 (the PI reference block, 48 models):",
          len(a), "rows,", a.u_teamid.nunique(), "teams")
    print("    paper states n = 1,253 models from 71 teams ->",
          "MATCH" if (len(a) == 1253 and a.u_teamid.nunique() == 71) else "MISMATCH")

    neg = a.upper_Z < 0
    pos = a.lower_Z > 0
    ns = ~(neg | pos)
    w = a.groupby("u_teamid").u_teamid.transform("size").rdiv(1.0)

    def pct(mask, weights=None):
        if weights is None:
            return 100.0 * mask.mean()
        return 100.0 * (weights * mask).sum() / weights.sum()

    print("\nB. Fig. 1 percentages")
    print("   published (corrected Fig.1, 2024): 25.4 neg / 57.7 ns / 16.9 pos")
    print("   reproduced INVERSE-TEAM-SIZE WEIGHTED: %.2f / %.2f / %.2f"
          % (pct(neg, w), pct(ns, w), pct(pos, w)))
    print("   same data UNWEIGHTED (per model):    %.2f / %.2f / %.2f"
          % (pct(neg), pct(ns), pct(pos)))
    print("   team-level (a team counts once, its modal outcome):")
    tm = a.assign(cat=np.where(neg, "neg", np.where(pos, "pos", "ns"))) \
          .groupby("u_teamid").cat.agg(lambda s: s.value_counts().idxmax())
    print("   ", (100 * tm.value_counts(normalize=True)).round(2).to_dict())

    # --- C. Mathur et al. range -------------------------------------------
    q = np.percentile(a.AME_Z, [5, 95])
    print("\nC. Mathur, Covington & VanderWeele 2023 (PNAS letter)")
    print("   they report 90%% of standardized estimates in [-0.037, 0.037]")
    print("   reproduced 5th/95th pct of AME_Z: [%.4f, %.4f]" % (q[0], q[1]))
    print("   (their number is a symmetric summary; |AME_Z| 90th pct = %.4f)"
          % np.percentile(np.abs(a.AME_Z), 90))

    # --- D. sampling error vs true heterogeneity --------------------------
    se = (a.upper_Z - a.lower_Z).values / (2 * Z95)
    ok = np.isfinite(se) & (se > 0)
    print("\nD. dispersion decomposition (n usable = %d of %d)" % (ok.sum(), len(a)))
    y = a.AME_Z.values[ok]
    v = se[ok] ** 2
    g = a.u_teamid.values[ok]
    print("   observed SD of AME_Z          = %.5f" % np.std(y, ddof=1))
    print("   observed VAR of AME_Z         = %.3e" % np.var(y, ddof=1))
    print("   mean sampling variance (SE^2) = %.3e  (mean SE = %.5f)"
          % (v.mean(), np.sqrt(v).mean()))
    t2, Q, k = dl_tau2(y, v)
    i2, s2 = i_squared(y, v, t2)
    print("   DL tau^2 = %.3e  (tau = %.5f);  Q = %.1f on %d df;  I^2 = %.4f"
          % (t2, np.sqrt(t2), Q, k - 1, i2))
    print("   share of observed variance that is NOT sampling error: %.4f"
          % (t2 / np.var(y, ddof=1)))
    mu, tb, tw = reml_two_level(y, v, g)
    tot = tb + tw
    print("   two-level REML: mu = %.5f, tau2_between = %.3e, tau2_within = %.3e"
          % (mu, tb, tw))
    print("   -> of TRUE heterogeneity, between-team = %.1f%%, within-team = %.1f%%"
          % (100 * tb / tot, 100 * tw / tot))
    print("   -> of OBSERVED variance: sampling %.1f%%, between-team %.1f%%, within-team %.1f%%"
          % (100 * v.mean() / np.var(y, ddof=1), 100 * tb / np.var(y, ddof=1),
             100 * tw / np.var(y, ddof=1)))
    print("   90%% prediction interval for a TRUE effect: [%.4f, %.4f]"
          % (mu - 1.645 * np.sqrt(tot), mu + 1.645 * np.sqrt(tot)))
    print("   (Mathur et al. report [-0.014, 0.014] from a one-level model)")

    # same, splitting on the dependent variable the team chose
    print("\nD2. by chosen DV (different estimands, cf. Lundberg et al. 2021)")
    rows = []
    for dv, sub in a[ok].groupby("DV"):
        s = (sub.upper_Z - sub.lower_Z).values / (2 * Z95)
        m = np.isfinite(s) & (s > 0)
        if m.sum() < 12:
            continue
        yy, vv = sub.AME_Z.values[m], s[m] ** 2
        tt, _, _ = dl_tau2(yy, vv)
        ii, _ = i_squared(yy, vv, tt)
        rows.append((dv, m.sum(), yy.mean(), np.std(yy, ddof=1), np.sqrt(tt), ii))
    print(pd.DataFrame(rows, columns=["DV", "n", "mean", "SD", "tau", "I2"])
          .sort_values("n", ascending=False).to_string(index=False,
          float_format=lambda x: "%.5f" % x))

    # --- E. outlier sensitivity -------------------------------------------
    print("\nE. outlier sensitivity of the raw (unstandardized) AME")
    raw = a.AME.dropna().values
    tv = np.sum((raw - raw.mean()) ** 2)
    order = np.argsort(-np.abs(raw - raw.mean()))
    for kk in (1, 5, 10, 25):
        print("   top %2d models contribute %.1f%% of total sum of squares"
              % (kk, 100 * np.sum((raw[order[:kk]] - raw.mean()) ** 2) / tv))
    print("   AME range [%.3f, %.3f]; AME_Z range [%.3f, %.3f]"
          % (raw.min(), raw.max(), a.AME_Z.min(), a.AME_Z.max()))
    yz = a.AME_Z.values
    tvz = np.sum((yz - yz.mean()) ** 2)
    oz = np.argsort(-np.abs(yz - yz.mean()))
    for kk in (1, 5, 10, 25):
        print("   [AME_Z] top %2d models contribute %.1f%% of total SS"
              % (kk, 100 * np.sum((yz[oz[:kk]] - yz.mean()) ** 2) / tvz))

    # --- F. self-tests -----------------------------------------------------
    print("\nF. self-tests of the estimators (must pass before believing D)")
    for k_, v_ in selftest().items():
        print("   ", k_, "=", v_)


if __name__ == "__main__":
    main()
