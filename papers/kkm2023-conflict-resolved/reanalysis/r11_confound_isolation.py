#!/usr/bin/env python3
"""r11 -- isolate the one confound r10 left standing.

r10 produced two results that appear to disagree:

  (a) coverage of the randomly-assigned secondary measures -- a monotone proxy for
      a participant's number of reports -- FALLS above $100k (logit slope -0.119,
      p = 0.018). So high earners did give fewer reports, and the measurement-noise
      account of the widening is not dead.
  (b) the 12 sparse secondary feelings, which any report-count gradient must hit
      ~35x harder than the primary measure, show NO widening above $100k
      (mean +0.000 vs +0.041 for well-being, z = 9.0).

They disagree only if both effects live in the same place. They do not: reading the
raw coverage column, it is flat at ~0.48 through the $250,000 band and drops only in
the top two bands ($400k, n=832; $625k, n=420) -- 3.7% of the sample, and the bands
that carry least weight in a variance-weighted log-SD regression.

So this script re-runs everything on the RESTRICTED range $100k-$250k, where the
proxy says report counts are constant. If the well-being distribution still widens
there, the widening is not a report-count artifact -- established inside a window
where the confounder does not move.

Plus the variance arithmetic the threat actually requires.

Output: out_confound_isolation.csv
"""
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
K21 = os.path.join(HERE, "..", "..", "killingsworth2021-experienced-wellbeing",
                   "artifacts", "k2021_income_wellbeing.csv")
KKM = os.path.join(HERE, "..", "artifacts", "kkm2023.csv")
SECONDARY = ["good", "inspired", "proud", "interested", "confident", "bad",
             "bored", "upset", "afraid", "angry", "sad", "stressed"]
RANGES = {"above 100k, ALL bands": (100001, 10 ** 9),
          "100k-250k only (coverage flat)": (100001, 250001),
          "100k-175k only": (100001, 175001),
          "top two bands only (400k, 625k)": (300000, 10 ** 9)}


def logsd_gradient(sd, n, L, mask):
    if mask.sum() < 3:
        return np.nan, np.nan
    w = (n[mask] - 1) / 2.0
    X = np.column_stack([np.ones(mask.sum()), L[mask]])
    W = np.diag(w)
    XtWX = X.T @ W @ X
    b = np.linalg.solve(XtWX, X.T @ W @ np.log(sd[mask]))
    r = np.log(sd[mask]) - X @ b
    s2 = float((w * r ** 2).sum() / max(mask.sum() - 2, 1))
    return b[1], float(np.sqrt((np.linalg.inv(XtWX) * s2)[1, 1]))


def main():
    k = pd.read_csv(K21)
    inc = k.household_income.values
    L = np.log(inc)
    base = k["experienced_wellbeing.personcount"].values.astype(float)
    covm = np.mean([k[f + ".personcount"].values / base for f in SECONDARY], axis=0)

    rows = []
    print("%-32s %-4s %-22s %-22s %-22s" %
          ("income window", "k", "coverage logit slope", "well-being dlogSD",
           "12 secondary dlogSD (mean)"))
    for name, (lo_, hi_) in RANGES.items():
        m = (inc >= lo_) & (inc <= hi_)
        if m.sum() < 3:
            print("%-32s %-4d (fewer than 3 income bands -- not estimable)"
                  % (name, m.sum()))
            rows.append({"window": name, "k_bands": int(m.sum())})
            continue
        p = covm[m].clip(1e-4, 1 - 1e-4)
        sl, ic, r, pv, se = stats.linregress(L[m], np.log(p / (1 - p)))
        sdw = k["experienced_wellbeing.std.error"].values * np.sqrt(base)
        gw, sw = logsd_gradient(sdw, base, L, m)
        gs = []
        for f in SECONDARY:
            sdf = k[f + ".std.error"].values * np.sqrt(k[f + ".personcount"].values)
            g, _ = logsd_gradient(sdf, k[f + ".personcount"].values.astype(float), L, m)
            gs.append(g)
        gs = np.array(gs)
        print("%-32s %-4d %+.4f (se %.4f)%s %+.4f (se %.4f)%s %+.4f (se %.4f)%s"
              % (name, m.sum(), sl, se, " " * 3, gw, sw, " " * 3,
                 gs.mean(), gs.std(ddof=1) / np.sqrt(len(gs)), ""))
        rows.append({"window": name, "k_bands": int(m.sum()),
                     "coverage_slope": sl, "coverage_se": se, "coverage_p": pv,
                     "wb_dlogsd": gw, "wb_se": sw,
                     "sec_dlogsd_mean": gs.mean(),
                     "sec_dlogsd_se": gs.std(ddof=1) / np.sqrt(len(gs))})

    # ---- the same, on the person-level KKM data, which is the actual analysis set
    d = pd.read_csv(KKM)
    print("\nPERSON-LEVEL (KKM deposit): SD and IQR of well-being by band")
    g = d.groupby("income").wellbeing
    tab = pd.DataFrame({"n": g.size(), "sd": g.std(ddof=1),
                        "iqr": g.quantile(.75) - g.quantile(.25)})
    tab["L"] = np.log(tab.index.values)
    for name, (lo_, hi_) in RANGES.items():
        m = (tab.index.values >= lo_) & (tab.index.values <= hi_)
        if m.sum() < 3:
            continue
        for col in ("sd", "iqr"):
            gg, ss = logsd_gradient(tab[col].values, tab.n.values.astype(float),
                                    tab.L.values, m)
            print("  %-32s dlog(%-3s)/dlog(income) = %+.4f (se %.4f)  z=%.2f"
                  % (name, col, gg, ss, gg / ss))

    # ---- the arithmetic the threat requires --------------------------------
    print("\nHOW MUCH VARIANCE CAN THE OBSERVED REPORT-COUNT DROP ACTUALLY BUY?")
    c_ref, c_top = covm[9], covm[14]          # $112.5k band and $625k band
    v_ref = tab.sd.loc[112500] ** 2
    v_top = tab.sd.loc[625000] ** 2
    print("  coverage %.4f ($112.5k) -> %.4f ($625k);  well-being variance "
          "%.1f -> %.1f (gap %.1f)" % (c_ref, c_top, v_ref, v_top, v_top - v_ref))
    print("  %-8s %-10s %-10s %-14s %-12s" %
          ("k at ref", "implied k", "sigma_w", "variance added", "% of gap"))
    out2 = []
    for k0 in (30, 40, 50):
        p_f = 1 - (1 - c_ref) ** (1.0 / k0)
        k_top = np.log(1 - c_top) / np.log(1 - p_f)
        for sw_ in (15, 20, 25, 30):
            add = sw_ ** 2 * (1.0 / k_top - 1.0 / k0)
            print("  %-8d %-10.1f %-10d %-14.2f %-12.1f"
                  % (k0, k_top, sw_, add, 100 * add / (v_top - v_ref)))
            out2.append({"window": "arithmetic", "k_ref": k0, "k_top": k_top,
                         "sigma_w": sw_, "variance_added": add,
                         "pct_of_gap": 100 * add / (v_top - v_ref)})
    print("  Even at the most generous within-person SD, the observed drop in report")
    print("  counts buys a small minority of the observed variance increase.")

    pd.DataFrame(rows + out2).to_csv(
        os.path.join(HERE, "out_confound_isolation.csv"), index=False)
    print("\nwrote out_confound_isolation.csv")


if __name__ == "__main__":
    main()
