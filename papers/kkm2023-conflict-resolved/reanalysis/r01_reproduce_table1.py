#!/usr/bin/env python3
"""r01 -- reproduce Table 1 of Killingsworth, Kahneman & Mellers (2023) from the
deposited person-level data, under each of the three readings of "piecewise
quantile regression" that the paper's Methods leave open.

The paper says (Results): "We used quantile regression to investigate the trends
shown in Fig. 2, computing separate slopes in the low range of incomes (less than
$100,000) and in the higher range (above $100,000) for each of the five quantiles."
and later "We compared the slopes below and above 100k for each quantile by
including an interaction term in quantile regressions."

Those two sentences describe different estimators. This script fits all three and
reports which one reproduces the printed slopes and t values:

  A  SPLIT      two independent quantile regressions, one per income subsample
  B  INTERACT   one model:  y ~ b0 + b1*L + b2*A + b3*L*A     (jump allowed at knot)
  C  SPLINE     one model:  y ~ b0 + b1*L + b3*(L-k)_+        (continuous at knot)

L = log(income), A = 1{income > 100000}, k = log(100000).

Data: artifacts/kkm2023.csv, downloaded from https://osf.io/qye4a/
      sha256 01ca3cbf8c6d565117927dda56d6a2c5008bfdbab3226851da07aafc648674fd
      (matches the hash OSF's API declares for the object)

Usage:  python r01_reproduce_table1.py
"""
import io
import json
import os
import sys

import numpy as np
import pandas as pd
from statsmodels.regression.quantile_regression import QuantReg

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "..", "artifacts", "kkm2023.csv")
KNOT = np.log(100000.0)
PCTS = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35]

# Printed in KKM 2023 Table 1: (slope<=100k, t, slope>100k, t)
PRINTED = {
    0.05: (2.34, 4.7, 0.25, 0.5),
    0.10: (1.75, 6.6, 0.52, 1.4),
    0.15: (1.90, 8.4, 0.34, 1.0),
    0.20: (1.84, 8.5, 0.62, 1.8),
    0.25: (1.52, 6.8, 1.12, 3.3),
    0.30: (1.33, 6.3, 1.21, 4.3),
    0.35: (1.26, 6.8, 1.21, 4.1),
}
# Fig. 2 quantiles, reported in the text with interaction p-values
FIG2 = {0.15: 0.0002, 0.30: None, 0.50: None, 0.70: 0.075, 0.85: 0.023}


def load():
    d = pd.read_csv(CSV)
    d["L"] = np.log(d["income"])          # recompute; the deposited log_income is 3dp
    d["A"] = (d["income"] > 100000).astype(float)
    d["Lplus"] = np.maximum(d["L"] - KNOT, 0.0)
    return d


def fit_split(d, tau):
    out = {}
    for lab, sub in (("below", d[d.A == 0]), ("above", d[d.A == 1])):
        X = np.column_stack([np.ones(len(sub)), sub["L"].values])
        r = QuantReg(sub["wellbeing"].values, X).fit(q=tau)
        out[lab] = (r.params[1], r.tvalues[1], r.bse[1], len(sub))
    return out


def fit_interact(d, tau):
    X = np.column_stack([np.ones(len(d)), d["L"], d["A"], d["L"] * d["A"]])
    r = QuantReg(d["wellbeing"].values, X).fit(q=tau)
    b1, b3 = r.params[1], r.params[3]
    V = r.cov_params()
    se_above = float(np.sqrt(V[1, 1] + V[3, 3] + 2 * V[1, 3]))
    return {"below": (b1, r.tvalues[1], r.bse[1], len(d)),
            "above": (b1 + b3, (b1 + b3) / se_above, se_above, len(d)),
            "interaction": (b3, r.tvalues[3], r.bse[3], r.pvalues[3])}


def fit_spline(d, tau):
    X = np.column_stack([np.ones(len(d)), d["L"], d["Lplus"]])
    r = QuantReg(d["wellbeing"].values, X).fit(q=tau)
    b1, b2 = r.params[1], r.params[2]
    V = r.cov_params()
    se_above = float(np.sqrt(V[1, 1] + V[2, 2] + 2 * V[1, 2]))
    return {"below": (b1, r.tvalues[1], r.bse[1], len(d)),
            "above": (b1 + b2, (b1 + b2) / se_above, se_above, len(d)),
            "interaction": (b2, r.tvalues[2], r.bse[2], r.pvalues[2])}


def main():
    d = load()
    print("n = %d rows; %d distinct income values; %d below / %d above 100k"
          % (len(d), d.income.nunique(), (d.A == 0).sum(), (d.A == 1).sum()))
    print("distinct income values above the knot: %s"
          % sorted(d.loc[d.A == 1, "income"].unique()))
    print()

    rows = []
    hdr = ("tau", "printed<=100k", "A split", "B interact", "C spline",
           "printed>100k", "A split", "B interact", "C spline")
    print("SLOPES  (t in parentheses)")
    print("%-6s %-14s %-14s %-14s %-14s | %-13s %-14s %-14s %-14s" % hdr)
    for tau in PCTS:
        a, b, c = fit_split(d, tau), fit_interact(d, tau), fit_spline(d, tau)
        p = PRINTED[tau]
        fmt = lambda v: "%.2f (%.1f)" % (v[0], v[1])
        print("%-6.2f %-14s %-14s %-14s %-14s | %-13s %-14s %-14s %-14s" % (
            tau,
            "%.2f (%.1f)" % (p[0], p[1]), fmt(a["below"]), fmt(b["below"]), fmt(c["below"]),
            "%.2f (%.1f)" % (p[2], p[3]), fmt(a["above"]), fmt(b["above"]), fmt(c["above"])))
        rows.append({
            "tau": tau,
            "printed_below": p[0], "printed_t_below": p[1],
            "printed_above": p[2], "printed_t_above": p[3],
            "split_below": a["below"][0], "split_t_below": a["below"][1],
            "split_se_below": a["below"][2],
            "split_above": a["above"][0], "split_t_above": a["above"][1],
            "split_se_above": a["above"][2],
            "interact_below": b["below"][0], "interact_above": b["above"][0],
            "interact_t_above": b["above"][1], "interact_se_above": b["above"][2],
            "interact_diff": b["interaction"][0], "interact_p": b["interaction"][3],
            "spline_below": c["below"][0], "spline_above": c["above"][0],
            "spline_t_above": c["above"][1], "spline_se_above": c["above"][2],
            "spline_diff": c["interaction"][0], "spline_p": c["interaction"][3],
        })

    df = pd.DataFrame(rows)
    for est in ("split", "interact", "spline"):
        eb = np.abs(df[est + "_below"] - df["printed_below"])
        ea = np.abs(df[est + "_above"] - df["printed_above"])
        print("\n%-9s max |slope - printed|:  below %.4f   above %.4f   "
              "(mean %.4f / %.4f)" % (est, eb.max(), ea.max(), eb.mean(), ea.mean()))

    print("\n\nFIG. 2 QUANTILES -- interaction test on the slope change at 100k")
    print("%-6s %-11s %-11s %-11s %-11s %-11s" %
          ("tau", "slope<=100k", "slope>100k", "diff", "p (interact)", "paper p"))
    fig2rows = []
    for tau in sorted(FIG2):
        b = fit_interact(d, tau)
        print("%-6.2f %-11.3f %-11.3f %-11.3f %-11.4g %-11s" % (
            tau, b["below"][0], b["above"][0], b["interaction"][0],
            b["interaction"][3],
            "%.4g" % FIG2[tau] if FIG2[tau] is not None else "ns"))
        fig2rows.append({"tau": tau, "below": b["below"][0], "above": b["above"][0],
                         "diff": b["interaction"][0], "p": b["interaction"][3],
                         "paper_p": FIG2[tau]})

    df.to_csv(os.path.join(HERE, "out_table1_reproduction.csv"), index=False)
    pd.DataFrame(fig2rows).to_csv(os.path.join(HERE, "out_fig2_interaction.csv"), index=False)
    print("\nwrote out_table1_reproduction.csv, out_fig2_interaction.csv")


if __name__ == "__main__":
    main()
