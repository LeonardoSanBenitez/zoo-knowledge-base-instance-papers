#!/usr/bin/env python3
"""w03 -- three corrections to w02, and the number the paper should have reported.

CORRECTION 1.  w02 applied a coupling estimated on raw ENDPOINT arms to the
CHANGE-score comparisons. The relation between the SD of a change score and the
magnitude of the mean change is not the same relation as between an endpoint SD
and an endpoint mean, and there is no reason for one coefficient to serve both.
Estimated separately here.

CORRECTION 2.  "We cannot reject the null hypothesis of equal variances" is not a
finding, it is the absence of one. What a variability ratio and its interval
actually deliver is a BOUND on the variance of individual treatment effects.
Under the standard additive model

    Var(treated) = Var(control) + Var(individual effects)
    =>  sigma_interaction / sigma_control = sqrt(VR^2 - 1)

so the upper confidence limit on VR converts directly into an upper limit on how
much individual responses can differ. On the HAMD that limit can be stated in
points, next to the roughly 2.7-point average drug-placebo difference, and a
reader can then judge for themselves whether "assume the average effect applies
to the individual patient" follows.

CORRECTION 3.  The claim that lnVR has no power against additive heterogeneity
once the mean moves on a coupled scale is a claim about an estimator, so it is
testable by simulation with the answer known: build corpora that contain a
KNOWN treatment-by-patient interaction AND a known coupling, and see which
statistic finds it.

Output: out_bounds.csv, out_power_simulation.csv
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "..", "tools"))
import statlib  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
B = 4000
SEED = 20260902


def within_group_slope(df, xcol, ycol, gcol):
    x = df[xcol].values.astype(float)
    y = df[ycol].values.astype(float)
    g = pd.Series(df[gcol].values)
    xc = x - pd.Series(x).groupby(g).transform("mean").values
    yc = y - pd.Series(y).groupby(g).transform("mean").values
    d = (xc ** 2).sum()
    return float((xc * yc).sum() / d) if d > 0 else np.nan


def boot(df, xcol, ycol, gcol, clcol, B=B, seed=SEED):
    rng = np.random.default_rng(seed)
    uq = np.unique(df[clcol].values)
    idx = {c: np.flatnonzero(df[clcol].values == c) for c in uq}
    out = []
    for _ in range(B):
        sel = np.concatenate([idx[c] for c in rng.choice(uq, len(uq), replace=True)])
        s = within_group_slope(df.iloc[sel], xcol, ycol, gcol)
        if np.isfinite(s):
            out.append(s)
    return np.array(out)


def bound(vr_upper):
    """sigma_interaction / sigma_control implied by an upper limit on VR."""
    return float(np.sqrt(max(vr_upper ** 2 - 1.0, 0.0)))


def main():
    A = pd.read_csv(os.path.join(HERE, "out_arms.csv"))
    C = pd.read_csv(os.path.join(HERE, "out_comparisons.csv"))
    A["lm"] = np.log(np.abs(A.end_mean))
    A["ls"] = np.log(A.end_sd)
    A = A[np.isfinite(A.lm) & np.isfinite(A.ls)]

    print("1  A SEPARATE COUPLING FOR EACH KIND OF OUTCOME")
    betas = {}
    for kind, ischg in (("raw endpoint", False), ("change score", True)):
        pl = A[(A.is_change == ischg) & (A.drug == "placebo")]
        b = within_group_slope(pl, "lm", "ls", "scale")
        bs = boot(pl, "lm", "ls", "scale", "study")
        lo, hi = np.percentile(bs, [2.5, 97.5])
        betas[ischg] = (b, bs)
        print("   %-13s placebo arms: beta = %.3f  [%.3f, %.3f]  "
              "(%d arms, %d studies)" % (kind, b, lo, hi, len(pl), pl.study.nunique()))
    print("   w02 applied the endpoint coupling to both. That was wrong for the")
    print("   change-score half and is corrected here.")

    print("\n2  THE THREE STATISTICS, each with its own coupling")
    rows = []
    for kind, ischg in (("raw ENDPOINT", False), ("CHANGE score", True)):
        sub = C[C.is_change == ischg]
        pl = A[(A.is_change == ischg) & (A.drug == "placebo")]
        beta, beta_bs = betas[ischg]
        uq = np.unique(sub.study.values)
        idx = {c: np.flatnonzero(sub.study.values == c) for c in uq}
        pl_uq = np.unique(pl.study.values)
        pl_idx = {c: np.flatnonzero(pl.study.values == c) for c in pl_uq}
        rng = np.random.default_rng(SEED + 3)
        est = {"lnVR": [], "lnCVR": [], "lnVR*": []}
        for _ in range(B):
            bsel = np.concatenate([pl_idx[c] for c in
                                   rng.choice(pl_uq, len(pl_uq), replace=True)])
            bb = within_group_slope(pl.iloc[bsel], "lm", "ls", "scale")
            if not np.isfinite(bb):
                bb = beta
            sel = np.concatenate([idx[c] for c in rng.choice(uq, len(uq), replace=True)])
            v_, m_ = sub.lnvr.values[sel], sub.lnmr.values[sel]
            w_ = 1.0 / sub.lnvr_v.values[sel]
            est["lnVR"].append((w_ * v_).sum() / w_.sum())
            est["lnCVR"].append((w_ * (v_ - m_)).sum() / w_.sum())
            est["lnVR*"].append((w_ * (v_ - bb * m_)).sum() / w_.sum())
        w = 1.0 / sub.lnvr_v.values
        pt = {"lnVR": float((w * sub.lnvr).sum() / w.sum()),
              "lnCVR": float((w * (sub.lnvr - sub.lnmr)).sum() / w.sum()),
              "lnVR*": float((w * (sub.lnvr - beta * sub.lnmr)).sum() / w.sum())}
        sd_ctl = float((sub.n_pbo * sub.sd_pbo).sum() / sub.n_pbo.sum())
        print("   %-13s  (k=%d, %d studies; beta %.3f; placebo endpoint SD %.2f "
              "scale points)" % (kind, len(sub), sub.study.nunique(), beta, sd_ctl))
        for name in ("lnVR", "lnCVR", "lnVR*"):
            lo, hi = np.percentile(est[name], [2.5, 97.5])
            bnd = bound(np.exp(hi))
            print("      %-6s VR %.3f [%.3f, %.3f]   -> individual-effect SD at "
                  "most %.2f x outcome SD = %.2f scale points"
                  % (name, np.exp(pt[name]), np.exp(lo), np.exp(hi),
                     bnd, bnd * sd_ctl))
            rows.append({"kind": kind, "statistic": name, "beta": beta,
                         "vr": float(np.exp(pt[name])), "lo": float(np.exp(lo)),
                         "hi": float(np.exp(hi)), "sigma_int_over_sd": bnd,
                         "sigma_int_points": bnd * sd_ctl, "sd_control": sd_ctl,
                         "k": len(sub), "studies": sub.study.nunique()})
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "out_bounds.csv"), index=False)
    print("\n   For scale: the average drug-placebo difference in this corpus is")
    print("   %.2f points (drug %.2f, placebo %.2f on the mixed HAMD/MADRS scale)."
          % (C[~C.is_change].m_pbo.mean() - C[~C.is_change].m_drug.mean(),
             C[~C.is_change].m_drug.mean(), C[~C.is_change].m_pbo.mean()))

    # ---------------- 3  power simulation ---------------------------------
    print("\n3  SIMULATION: which statistic finds a treatment-by-patient")
    print("   interaction that is REALLY THERE, on a scale with a real coupling?")
    print("   Generator: control arm ~ lognormal-ish with mean m and SD s.")
    print("   Treated arm: each patient's score multiplied by a factor drawn with")
    print("   mean (1-k) and SD kappa -- so there IS individual variation in")
    print("   response, of known size, on top of a mean effect of known size.")
    sub = C[~C.is_change]
    n_d = sub.n_drug.values.astype(int)
    n_p = sub.n_pbo.values.astype(int)
    m_p = sub.m_pbo.values
    s_p = sub.sd_pbo.values
    beta_e = betas[False][0]
    rng = np.random.default_rng(SEED)
    sim = []
    for kappa in (0.0, 0.10, 0.20, 0.30):
        acc = {"lnVR": [], "lnCVR": [], "lnVR*": []}
        for rep in range(200):
            lv, lm_, vv = [], [], []
            for i in range(len(sub)):
                # control: gamma with the observed mean and SD -> positive, skewed,
                # and its SD scales with its mean, which is the coupling we want
                shape = (m_p[i] / s_p[i]) ** 2
                scale = s_p[i] ** 2 / m_p[i]
                c = rng.gamma(shape, scale, n_p[i])
                t0 = rng.gamma(shape, scale, n_d[i])
                fac = np.clip(rng.normal(1 - 0.17, kappa, n_d[i]), 0.0, None)
                t = t0 * fac
                y, v = statlib.lnvr(t.std(ddof=1), n_d[i], c.std(ddof=1), n_p[i])
                lv.append(float(y))
                vv.append(float(v))
                lm_.append(float(np.log(t.mean() / c.mean())))
            lv, lm_, vv = np.array(lv), np.array(lm_), np.array(vv)
            w = 1.0 / vv
            acc["lnVR"].append((w * lv).sum() / w.sum())
            acc["lnCVR"].append((w * (lv - lm_)).sum() / w.sum())
            acc["lnVR*"].append((w * (lv - beta_e * lm_)).sum() / w.sum())
        line = "   kappa = %.2f (individual response SD, multiplicative)  " % kappa
        for name in ("lnVR", "lnCVR", "lnVR*"):
            line += "%s %.3f  " % (name, np.exp(np.mean(acc[name])))
            sim.append({"kappa": kappa, "statistic": name,
                        "mean_ratio": float(np.exp(np.mean(acc[name])))})
        print(line)
    pd.DataFrame(sim).to_csv(os.path.join(HERE, "out_power_simulation.csv"),
                             index=False)
    print("   Read the kappa = 0 row first: it is the negative control. A")
    print("   statistic that does not return 1.00 there is measuring the coupling,")
    print("   not the interaction. Then read down each column: the statistic that")
    print("   moves with kappa is the one with power against the thing the")
    print("   analysis exists to detect.")
    print("\nwrote out_bounds.csv, out_power_simulation.csv")


if __name__ == "__main__":
    main()
