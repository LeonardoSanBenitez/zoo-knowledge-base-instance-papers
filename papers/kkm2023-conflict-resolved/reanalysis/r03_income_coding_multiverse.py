#!/usr/bin/env python3
"""r03 -- how much of KKM (2023) survives a different, equally defensible coding
of income?

The above-$100k slope -- the number the whole paper turns on -- is estimated from
SIX distinct income values, and the two most influential of them are constructed
rather than observed:

    112500  midpoint of "$100,001 to $125,000"
    137500  midpoint of "$125,001 to $150,000"
    175000  midpoint of "$150,001 to $200,000"
    250000  midpoint of "$200,001 to $300,000"
    400000  midpoint of "$300,001 to $500,000"
    625000  ASSIGNED value for everyone above $500,000 -- a category with no upper
            bound, containing 1.2% of the sample. KKM: "Incomes over $500,000 ...
            were pooled together and set to a value of $625,000/year".

log(625000) = 13.35 and log(550000) = 13.22; the top point carries most of the
leverage for a slope fitted over a log range of 1.7. So the choice of 625000 is a
free parameter of the headline result, and the paper varies it not at all.

This script runs the specification multiverse the paper does not: for each coding
of income, refit KKM's own estimator (Table 1) and record whether the paper's
qualitative conclusion still holds. The conclusion is operationalised exactly as
the paper states it:

   FLAT_BOTTOM   above-100k slope not significant at 0.05 for tau in {.05,.10,.15}
   BOUNDARY_20   above-100k slope significant for tau >= 0.25
   ACCEL_TOP     interaction at tau=0.85 significant and positive

Output: out_income_multiverse.csv
"""
import itertools
import os
import sys

import numpy as np
import pandas as pd
from statsmodels.regression.quantile_regression import QuantReg

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "..", "artifacts", "kkm2023.csv")
LOW = [0.05, 0.10, 0.15]
MID = [0.20]
HIGH = [0.25, 0.30, 0.35]
TAUS = LOW + MID + HIGH + [0.50, 0.70, 0.85]


def fit(y, L, A, tau):
    X = np.column_stack([np.ones(len(y)), L, A, L * A])
    r = QuantReg(y, X).fit(q=tau)
    V = r.cov_params()
    se_ab = float(np.sqrt(V[1, 1] + V[3, 3] + 2 * V[1, 3]))
    b_ab = r.params[1] + r.params[3]
    return dict(below=r.params[1], above=b_ab, se_above=se_ab,
                p_above=2 * (1 - _nc(abs(b_ab / se_ab))),
                inter=r.params[3], p_inter=r.pvalues[3])


def _nc(z):
    from math import erf, sqrt
    return 0.5 * (1 + erf(z / sqrt(2)))


def variants(d):
    """yield (name, dataframe) -- each an alternative but defensible coding."""
    yield "AS PUBLISHED (top=625000)", d

    for top in (520000, 550000, 600000, 700000, 800000, 1000000, 1500000):
        e = d.copy()
        e.loc[e.income == 625000, "income"] = top
        yield "top-code >500k = %d" % top, e

    for mid in (350000, 450000):
        e = d.copy()
        e.loc[e.income == 400000, "income"] = mid
        yield "300-500k midpoint = %d" % mid, e

    e = d[d.income < 500000].copy()
    yield "DROP the open top category (>500k)", e
    e = d[d.income < 300000].copy()
    yield "DROP everything above 300k", e
    e = d[d.income < 200000].copy()
    yield "DROP everything above 200k", e

    # income as its ordinal category index rather than dollars: removes every
    # assumption about the dollar value of an unbounded category, keeps the order
    e = d.copy()
    cats = np.sort(d.income.unique())
    e["income"] = pd.Series(e.income).map({c: i + 1 for i, c in enumerate(cats)}).values
    yield "ORDINAL category index (1..15), no dollars", e

    # income as the empirical CDF rank of the person's income category
    e = d.copy()
    r = e.groupby("income").size().sort_index().cumsum()
    r = (r - e.groupby("income").size().sort_index() / 2) / len(e)
    e["income"] = e.income.map(r).values
    yield "PERCENTILE rank of income in sample", e

    # equal-width log spacing: every category one log-step apart. Tests whether the
    # result needs the actual dollar spacing at all.
    e = d.copy()
    e["income"] = e.income.map({c: np.exp(9.6 + 0.25 * i)
                                for i, c in enumerate(np.sort(d.income.unique()))}).values
    yield "EQUAL log spacing between categories", e


def main():
    base = pd.read_csv(CSV)
    rows = []
    for name, e in variants(base):
        y = e["wellbeing"].values
        if e["income"].max() > 20:            # dollars or ordinal/percentile
            L = np.log(e["income"].values)
            knot_mask = e["income"].values > 100000
        else:
            L = e["income"].values.astype(float)
            # keep the SAME people on each side of the knot as the published split
            knot_mask = base.loc[e.index, "income"].values > 100000
        A = knot_mask.astype(float)
        if A.sum() < 200 or (1 - A).sum() < 200:
            continue
        res = {t: fit(y, L, A, t) for t in TAUS}
        flat_bottom = all(res[t]["p_above"] > 0.05 for t in LOW)
        boundary20 = all(res[t]["p_above"] < 0.05 for t in HIGH)
        accel_top = res[0.85]["p_inter"] < 0.05 and res[0.85]["inter"] > 0
        rows.append({
            "variant": name, "n": len(e),
            "slope_above_tau15": res[0.15]["above"], "p_above_tau15": res[0.15]["p_above"],
            "slope_above_tau25": res[0.25]["above"], "p_above_tau25": res[0.25]["p_above"],
            "slope_above_tau50": res[0.50]["above"],
            "slope_above_tau85": res[0.85]["above"],
            "inter_tau15": res[0.15]["inter"], "p_inter_tau15": res[0.15]["p_inter"],
            "inter_tau85": res[0.85]["inter"], "p_inter_tau85": res[0.85]["p_inter"],
            "FLAT_BOTTOM": flat_bottom, "BOUNDARY_20": boundary20, "ACCEL_TOP": accel_top,
            "ALL_THREE": flat_bottom and boundary20 and accel_top,
        })
        print("%-42s n=%6d  flat_bottom=%-5s boundary20=%-5s accel_top=%-5s "
              "(b_above@.15=%.2f p=%.3f | inter@.85=%.2f p=%.3f)"
              % (name, len(e), flat_bottom, boundary20, accel_top,
                 res[0.15]["above"], res[0.15]["p_above"],
                 res[0.85]["inter"], res[0.85]["p_inter"]), flush=True)

    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(HERE, "out_income_multiverse.csv"), index=False)
    k = len(out)
    print("\n%d specifications" % k)
    for c in ("FLAT_BOTTOM", "BOUNDARY_20", "ACCEL_TOP", "ALL_THREE"):
        print("  %-12s holds in %2d/%d (%.0f%%)" % (c, out[c].sum(), k, 100 * out[c].mean()))
    print("\nwrote out_income_multiverse.csv")


if __name__ == "__main__":
    main()
