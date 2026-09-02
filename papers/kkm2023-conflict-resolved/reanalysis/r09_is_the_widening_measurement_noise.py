#!/usr/bin/env python3
"""r09 -- the widening of the happiness distribution above $100k: substantive, or
an artifact of high earners contributing fewer experience-sampling reports?

THE THREAT.  Every person-level well-being value in KKM (2023) is a MEAN over that
person's momentary reports. Var(person mean) = between-person variance +
within-person variance / k_i. If k_i falls as income rises -- high earners are
busier; K2021's own deposit shows the mean work week rising from 33.1 h at $15,000
to 42.2 h at $625,000 -- then the conditional variance of the person-level measure
rises with income for a purely instrumental reason, and the entire "distribution
widens above $100k" finding (r04, r07, r08) is measurement noise.

The KKM deposit has four columns and no report counts, so it cannot settle this.
But Killingsworth's SEPARATE 2021 deposit can, indirectly and rather well. It
carries, for each of the 15 income bands, the mean, standard error and person
count of ~32 variables. Two kinds:

  ESM-AGGREGATED  a mean over many momentary smartphone reports per person
                  (experienced well-being, good, sad, stressed, ...). Subject to
                  the k_i artifact.
  INTAKE-ONCE     measured a single time on the intake survey (age, male, married,
                  education level, work week, Satisfaction With Life Scale, ...).
                  NOT subject to it: one measurement, no aggregation.

  PREDICTION IF THE ARTIFACT ACCOUNT IS RIGHT: the dispersion of ESM-aggregated
  variables widens with income above $100k; the dispersion of INTAKE-ONCE
  variables does not.
  PREDICTION IF IT IS SUBSTANTIVE AND SPECIFIC TO WELL-BEING: only well-being
  widens, and the other ESM feelings need not.

Also computes two arithmetic bounds:
  B1  how much within-band income heterogeneity would be needed to fake the
      observed variance rise (the categories get much wider at the top);
  B2  how far reports-per-person would have to fall to fake it.

Output: out_widening_diagnostic.csv
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

# classification is from the Methods sections of K2021 and KKM2023, quoted in NOTES.md
ESM = ["experienced_wellbeing", "life_satisfaction", "good", "inspired", "proud",
       "interested", "confident", "bad", "bored", "upset", "afraid", "angry",
       "sad", "stressed", "control.life", "control.situation", "optimistic",
       "moneyimportance", "moneyissuccess"]
INTAKE = ["satisfaction_with_life_scale", "life_satisfaction_1_to_4",
          "billtrouble.last15days.b", "workweek.num", "toolittletime.b",
          "age", "male", "married", "education_level"]


def main():
    k = pd.read_csv(K21)
    L = np.log(k.household_income.values)
    hi = k.household_income.values > 100000
    lo = ~hi
    rows = []
    for v in ESM + INTAKE:
        se, n = k.get(v + ".std.error"), k.get(v + ".personcount")
        if se is None or n is None:
            continue
        sd = se.values * np.sqrt(n.values)
        if np.any(~np.isfinite(sd)) or np.any(sd <= 0):
            continue
        out = {"variable": v, "kind": "ESM" if v in ESM else "INTAKE",
               "n_median": float(np.median(n.values))}
        for lab, m in (("below", lo), ("above", hi)):
            # log-sd regressed on log-income; weight by df of each sd estimate
            w = (n.values[m] - 1) / 2.0
            X = np.column_stack([np.ones(m.sum()), L[m]])
            W = np.diag(w)
            XtWX = X.T @ W @ X
            b = np.linalg.solve(XtWX, X.T @ W @ np.log(sd[m]))
            resid = np.log(sd[m]) - X @ b
            s2 = float((w * resid ** 2).sum() / (m.sum() - 2))
            cov = np.linalg.inv(XtWX) * s2
            out["dlogsd_" + lab] = b[1]
            out["se_" + lab] = float(np.sqrt(cov[1, 1]))
        out["change"] = out["dlogsd_above"] - out["dlogsd_below"]
        out["se_change"] = float(np.hypot(out["se_above"], out["se_below"]))
        out["z_change"] = out["change"] / out["se_change"]
        rows.append(out)
    df = pd.DataFrame(rows)
    print("d log(SD) / d log(income), fitted separately below and above $100,000")
    print("a positive 'above' gradient is the widening; 'change' is the U-turn\n")
    print(df[["variable", "kind", "n_median", "dlogsd_below", "se_below",
              "dlogsd_above", "se_above", "change", "z_change"]]
          .to_string(index=False, float_format=lambda v: "%+.4f" % v))

    print("\nGROUPED")
    for kind in ("ESM", "INTAKE"):
        g = df[df.kind == kind]
        for col in ("dlogsd_below", "dlogsd_above", "change"):
            w = 1.0 / g["se_" + col.split("_")[-1] if col != "change" else "se_change"] ** 2 \
                if col != "change" else 1.0 / g.se_change ** 2
            if col == "dlogsd_below":
                w = 1.0 / g.se_below ** 2
            elif col == "dlogsd_above":
                w = 1.0 / g.se_above ** 2
            m = float((w * g[col]).sum() / w.sum())
            sem = float(np.sqrt(1.0 / w.sum()))
            print("  %-7s  %-14s  %+.4f  (se %.4f, z=%.2f)  over %d variables"
                  % (kind, col, m, sem, m / sem, len(g)))
    # a between-kind contrast
    ge, gi = df[df.kind == "ESM"], df[df.kind == "INTAKE"]
    we, wi = 1 / ge.se_above ** 2, 1 / gi.se_above ** 2
    me, mi = (we * ge.dlogsd_above).sum() / we.sum(), (wi * gi.dlogsd_above).sum() / wi.sum()
    sd_ = np.sqrt(1 / we.sum() + 1 / wi.sum())
    print("\n  ESM minus INTAKE, above-$100k dispersion gradient: %+.4f (se %.4f, z=%.2f)"
          % (me - mi, sd_, (me - mi) / sd_))
    print("  -- if the widening were an artifact of aggregating fewer reports, this")
    print("     contrast should be strongly positive.")
    df.to_csv(os.path.join(HERE, "out_widening_diagnostic.csv"), index=False)

    # ---------------- arithmetic bounds -------------------------------------
    d = pd.read_csv(KKM)
    g = d.groupby("income").wellbeing
    sd = g.std(ddof=1)
    v_lo = sd.loc[112500] ** 2
    v_hi = sd.loc[625000] ** 2
    gap = v_hi - v_lo
    mu_prime = 1.29                     # median slope per log(income), r07
    print("\nBOUND B1 -- within-band income heterogeneity")
    print("  variance to explain: SD %.2f -> %.2f, i.e. %.1f variance units"
          % (sd.loc[112500], sd.loc[625000], gap))
    print("  a spread of TRUE income inside a band contributes mu'^2 * Var(log income | band)")
    print("  with mu' = %.2f that needs Var(log inc | band) = %.1f, i.e. an SD of"
          " %.2f log units = a %.0f-fold spread at one SD."
          % (mu_prime, gap / mu_prime ** 2, np.sqrt(gap) / mu_prime,
             np.exp(np.sqrt(gap) / mu_prime)))
    print("  -> not credible; the grouping artifact cannot produce this.")

    print("\nBOUND B2 -- unequal reports per person")
    print("  within-person SD of momentary well-being is not in either deposit."
          " Solve for the k that would be needed, over a plausible range:")
    print("  %-10s %-14s %-14s" % ("within-SD", "k at low income", "k at high income"))
    for wsd in (15, 20, 25, 30):
        for k_lo in (30, 40, 50):
            k_hi = 1.0 / (1.0 / k_lo + gap / wsd ** 2)
            if k_hi > 0:
                print("  %-10d %-14d %-14.1f" % (wsd, k_lo, k_hi))
            else:
                print("  %-10d %-14d %-14s" % (wsd, k_lo, "impossible"))
    print("  1,725,994 reports / 33,391 people = %.1f reports per person on average."
          % (1725994 / 33391))
    print("  -> the required drop is large but NOT impossible for within-SD >= 25.")
    print("  The deposit cannot decide it. The one column that would: reports per person.")


if __name__ == "__main__":
    main()
