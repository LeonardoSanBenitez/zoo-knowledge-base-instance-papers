#!/usr/bin/env python3
"""w02 -- what VR = 0.98 means once you know how much a depression scale's SD
tracks its mean.

w01 reproduced the paper: raw endpoint VR 0.981 [0.962, 1.001], change score
1.006 [0.994, 1.018], I2 = 0% for both, 344 comparisons against their 345.

The raw-endpoint comparison has the drug arm's mean 17% BELOW the placebo arm's
(13.30 against 16.00, ln ratio -0.181). If a depression scale's SD travels with
its mean at all, some of that VR below 1 is the mean moving, not the treatment
homogenising. lnVR assumes the coupling is exactly zero. Nobody tested it.

THREE ROUTES TO THE COUPLING, all internal to this dataset:

  R1  across PLACEBO arms, within scale. They received no drug, so any relation
      between their endpoint mean and their endpoint SD is the scale's and the
      populations', with no treatment in it.
  R2  across ACTIVE arms, within scale. If the coupling is a property of the
      instrument it should be the same.
  R3  the paper's own two analyses. On raw endpoint scores the drug arm's mean is
      LOWER than placebo's; on change scores its mean change is LARGER in
      magnitude. A coupling predicts VR < 1 in the first and VR > 1 in the second,
      by beta times the respective log mean ratios. That is exactly the pattern
      the paper reports and does not comment on.

Then the calibrated statistic, with beta's uncertainty propagated:

      lnVR* = lnVR - beta_hat * ln(m_drug / m_placebo)

Output: out_beta.csv, out_calibrated.csv
"""
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "..", "tools"))
import statlib  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
B = 4000
SEED = 20260902


def within_group_slope(df, xcol, ycol, gcol):
    """OLS of y on x with group fixed effects (group-mean centring)."""
    x = df[xcol].values.astype(float)
    y = df[ycol].values.astype(float)
    g = df[gcol].values
    xc = x - pd.Series(x).groupby(pd.Series(g)).transform("mean").values
    yc = y - pd.Series(y).groupby(pd.Series(g)).transform("mean").values
    denom = (xc ** 2).sum()
    if denom <= 0:
        return np.nan
    return float((xc * yc).sum() / denom)


def boot_slope(df, xcol, ycol, gcol, clcol, B=B, seed=SEED):
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


def main():
    A = pd.read_csv(os.path.join(HERE, "out_arms.csv"))
    C = pd.read_csv(os.path.join(HERE, "out_comparisons.csv"))
    A = A[~A.is_change].copy()          # raw endpoint arms only
    A["lm"] = np.log(A.end_mean)
    A["ls"] = np.log(A.end_sd)
    A = A[np.isfinite(A.lm) & np.isfinite(A.ls)]

    print("1  THE COUPLING, three routes")
    rows = []
    for lab, sub in (("R1 placebo arms only", A[A.drug == "placebo"]),
                     ("R2 active arms only", A[A.drug != "placebo"]),
                     ("   all raw-endpoint arms", A)):
        if len(sub) < 20:
            continue
        b = within_group_slope(sub, "lm", "ls", "scale")
        bs = boot_slope(sub, "lm", "ls", "scale", "study")
        lo, hi = np.percentile(bs, [2.5, 97.5])
        print("   %-26s beta = %.3f  95%% cluster bootstrap [%.3f, %.3f]  "
              "(%d arms, %d studies)"
              % (lab, b, lo, hi, len(sub), sub.study.nunique()))
        rows.append({"route": lab, "beta": b, "lo": lo, "hi": hi,
                     "n_arms": len(sub), "n_studies": sub.study.nunique()})
    for sc, sub in A[A.drug == "placebo"].groupby("scale"):
        if len(sub) < 12:
            continue
        sl, ic, r_, p_, se = stats.linregress(sub.lm, sub.ls)
        print("      placebo arms on %-7s beta = %.3f (se %.3f, n = %d)"
              % (sc, sl, se, len(sub)))
        rows.append({"route": "placebo, " + sc, "beta": sl,
                     "lo": sl - 1.96 * se, "hi": sl + 1.96 * se,
                     "n_arms": len(sub), "n_studies": sub.study.nunique()})
    pl = A[A.drug == "placebo"]
    beta = within_group_slope(pl, "lm", "ls", "scale")
    beta_bs = boot_slope(pl, "lm", "ls", "scale", "study")
    print("\n   USING R1 (placebo arms, scale fixed effects): beta = %.3f "
          "[%.3f, %.3f]" % (beta, *np.percentile(beta_bs, [2.5, 97.5])))
    print("   lnVR assumes 0: %.1f bootstrap SEs away.  lnCVR assumes 1: %.1f away."
          % (beta / beta_bs.std(ddof=1), (1 - beta) / beta_bs.std(ddof=1)))
    print("   for comparison, the mindfulness corpus gave 0.473 [0.255, 0.904]")
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "out_beta.csv"), index=False)

    # ---------------- 2  calibrated estimates -----------------------------
    print("\n2  THE THREE STATISTICS, drug vs placebo")
    out = []
    for lab, sub in (("raw ENDPOINT scores", C[~C.is_change]),
                     ("baseline-to-endpoint CHANGE scores", C[C.is_change])):
        uq = np.unique(sub.study.values)
        idx = {c: np.flatnonzero(sub.study.values == c) for c in uq}
        pl_uq = np.unique(pl.study.values)
        pl_idx = {c: np.flatnonzero(pl.study.values == c) for c in pl_uq}
        rng = np.random.default_rng(SEED + 7)
        est = {"lnVR": [], "lnCVR": [], "lnVR*": []}
        for _ in range(B):
            bsel = np.concatenate([pl_idx[c] for c in
                                   rng.choice(pl_uq, len(pl_uq), replace=True)])
            bb = within_group_slope(pl.iloc[bsel], "lm", "ls", "scale")
            if not np.isfinite(bb):
                bb = beta
            sel = np.concatenate([idx[c] for c in rng.choice(uq, len(uq), replace=True)])
            v_ = sub.lnvr.values[sel]
            m_ = sub.lnmr.values[sel]
            w_ = 1.0 / sub.lnvr_v.values[sel]
            est["lnVR"].append((w_ * v_).sum() / w_.sum())
            est["lnCVR"].append((w_ * (v_ - m_)).sum() / w_.sum())
            est["lnVR*"].append((w_ * (v_ - bb * m_)).sum() / w_.sum())
        w = 1.0 / sub.lnvr_v.values
        pt = {"lnVR": float((w * sub.lnvr).sum() / w.sum()),
              "lnCVR": float((w * (sub.lnvr - sub.lnmr)).sum() / w.sum()),
              "lnVR*": float((w * (sub.lnvr - beta * sub.lnmr)).sum() / w.sum())}
        print("   %-36s  mean log ratio of means %+.4f  (k=%d, %d studies)"
              % (lab, sub.lnmr.mean(), len(sub), sub.study.nunique()))
        rec = {"subset": lab, "k": len(sub), "studies": sub.study.nunique(),
               "ln_mean_ratio": float(sub.lnmr.mean()), "beta": beta}
        for name in ("lnVR", "lnCVR", "lnVR*"):
            lo, hi = np.percentile(est[name], [2.5, 97.5])
            star = "  <- excludes 1" if not (lo <= 0 <= hi) else ""
            print("      %-6s  ratio %.3f  95%% [%.3f, %.3f]%s"
                  % (name, np.exp(pt[name]), np.exp(lo), np.exp(hi), star))
            rec[name] = pt[name]
            rec[name + "_lo"] = lo
            rec[name + "_hi"] = hi
        out.append(rec)
    pd.DataFrame(out).to_csv(os.path.join(HERE, "out_calibrated.csv"), index=False)

    # ---------------- 3  the paper's own internal check --------------------
    print("\n3  THE PAPER'S OWN TWO ANALYSES, as a test of the coupling")
    raw, chg = C[~C.is_change], C[C.is_change]
    print("   A coupling of beta predicts lnVR = beta * ln(mean ratio) under a")
    print("   PURE location shift with no variance effect at all:")
    for lab, sub in (("raw endpoint", raw), ("change score", chg)):
        w = 1.0 / sub.lnvr_v.values
        obs = float((w * sub.lnvr).sum() / w.sum())
        mr = float((w * sub.lnmr).sum() / w.sum())
        print("     %-13s ln(mean ratio) %+.4f -> predicted lnVR %+.4f, "
              "observed %+.4f, difference %+.4f"
              % (lab, mr, beta * mr, obs, obs - beta * mr))
    print("   The two analyses have mean ratios of OPPOSITE SIGN, and their")
    print("   variability ratios differ in the direction the coupling predicts.")
    print("   The paper reports both and treats the difference as unremarkable.")

    print("\n4  WHAT THIS DOES AND DOES NOT SHOW")
    print("   It does NOT show that antidepressants have heterogeneous effects.")
    print("   It shows that VR = 0.98 on raw endpoint scores is what a PURE")
    print("   LOCATION SHIFT produces on a scale with this coupling, so the")
    print("   analysis has no power to detect the additive heterogeneity it was")
    print("   built to detect -- the compression from the mean moving and any")
    print("   expansion from a treatment-by-patient interaction are confounded,")
    print("   and only one of the two has been estimated.")


if __name__ == "__main__":
    main()
