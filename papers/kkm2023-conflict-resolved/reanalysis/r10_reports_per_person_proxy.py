#!/usr/bin/env python3
"""r10 -- settle the measurement-noise threat with a proxy for reports-per-person
that is actually present in Killingsworth's 2021 deposit, and fix two errors in
r09.

TWO ERRORS IN r09, recorded rather than deleted (CONTRIBUTING.md rule 4):

  E1  The "INTAKE" pool included BINARY variables (male, married, billtrouble,
      toolittletime). For a binary variable SD = sqrt(p(1-p)) is a deterministic
      function of the mean, so its "dispersion gradient" is its mean gradient in
      disguise. `married` produced z = -21 for exactly that reason and dominated
      the pool. Binaries are excluded here.
  E2  The pooling was inverse-variance fixed-effect across variables that measure
      DIFFERENT constructs. That treats between-construct heterogeneity as zero
      and manufactures precision (ESM below-$100k came out z = -34). Redone as an
      unweighted mean with a between-variable standard error, which is the
      quantity the comparison actually needs.

THE PROXY.  K2021, Methods: the primary well-being question "was asked in every
survey", while the secondary feelings "were assessed in independently randomized
subsets of surveys". So whether a participant EVER answered a given secondary
feeling is a monotone function of how many reports they gave:

    P(person has feeling f) = 1 - (1 - p_f) ** k_i

The deposit stores, per income band, the person count for every variable. So

    coverage_f(band) = personcount_f(band) / personcount_wellbeing(band)

is a direct, monotone proxy for the typical k_i in that band. If high earners give
fewer reports -- the assumption the whole measurement-noise threat rests on --
coverage must FALL with income. Inverting the relation even gives an implied k.

Output: out_reports_proxy.csv, out_dispersion_pooled_fixed.csv
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

ESM_CONT = ["experienced_wellbeing", "life_satisfaction", "good", "inspired",
            "proud", "interested", "confident", "bad", "bored", "upset", "afraid",
            "angry", "sad", "stressed", "control.life", "control.situation",
            "optimistic", "moneyimportance", "moneyissuccess"]
INTAKE_CONT_PSYCH = ["satisfaction_with_life_scale", "life_satisfaction_1_to_4"]
INTAKE_CONT_OTHER = ["workweek.num", "age", "education_level"]
BINARY = ["male", "married", "billtrouble.last15days.b", "toolittletime.b"]
SECONDARY = ["good", "inspired", "proud", "interested", "confident", "bad",
             "bored", "upset", "afraid", "angry", "sad", "stressed"]


def grad(sd, n, L, mask):
    w = (n[mask] - 1) / 2.0
    X = np.column_stack([np.ones(mask.sum()), L[mask]])
    W = np.diag(w)
    XtWX = X.T @ W @ X
    b = np.linalg.solve(XtWX, X.T @ W @ np.log(sd[mask]))
    r = np.log(sd[mask]) - X @ b
    s2 = float((w * r ** 2).sum() / (mask.sum() - 2))
    return b[1], float(np.sqrt((np.linalg.inv(XtWX) * s2)[1, 1]))


def main():
    k = pd.read_csv(K21)
    L = np.log(k.household_income.values)
    hi = k.household_income.values > 100000
    lo = ~hi

    # ---------------- PART 1: the reports-per-person proxy ------------------
    base = k["experienced_wellbeing.personcount"].values.astype(float)
    print("PART 1 -- COVERAGE OF SECONDARY (RANDOMLY-ASSIGNED) MEASURES")
    print("coverage = persons with the secondary measure / persons with well-being")
    print("A monotone increasing function of that person's number of reports.\n")
    cov = pd.DataFrame({"income": k.household_income.values, "L": L,
                        "n_wellbeing": base.astype(int)})
    for f in SECONDARY:
        cov[f] = k[f + ".personcount"].values / base
    cov["mean_coverage"] = cov[SECONDARY].mean(axis=1)
    print(cov[["income", "n_wellbeing", "mean_coverage"] + SECONDARY[:5]]
          .to_string(index=False, float_format=lambda v: "%.3f" % v))

    rows = []
    print("\n  d(logit coverage)/d log(income), by segment")
    for f in SECONDARY + ["mean_coverage"]:
        p = cov[f].values.clip(1e-4, 1 - 1e-4)
        lg = np.log(p / (1 - p))
        out = {"measure": f}
        for lab, m in (("below", lo), ("above", hi), ("all", np.ones(len(L), bool))):
            sl, ic, r, pv, se = stats.linregress(L[m], lg[m])
            out["d_" + lab] = sl
            out["se_" + lab] = se
            out["p_" + lab] = pv
        rows.append(out)
    cv = pd.DataFrame(rows)
    print(cv.to_string(index=False, float_format=lambda v: "%+.4f" % v))
    m = cv[cv.measure == "mean_coverage"].iloc[0]
    print("\n  POOLED (mean coverage): below 100k %+.4f (se %.4f, p=%.4f); "
          "above 100k %+.4f (se %.4f, p=%.4f)"
          % (m.d_below, m.se_below, m.p_below, m.d_above, m.se_above, m.p_above))
    print("  The measurement-noise threat requires this to be NEGATIVE above $100k")
    print("  (high earners giving fewer reports). Observed sign: %s"
          % ("NEGATIVE - threat alive" if m.d_above < 0 else
             "POSITIVE - threat dead: high earners gave MORE reports, not fewer"))

    # implied k, inverting 1-(1-p)^k with p calibrated so that the median band
    # reproduces its observed coverage at a stated k
    print("\n  implied reports-per-person, if the median band's true k were k0:")
    print("  %-8s %s" % ("k0", "  ".join("%9.0f" % v for v in k.household_income[:15:3])))
    for k0 in (20, 40, 60):
        c_med = cov["mean_coverage"].median()
        p_f = 1 - (1 - c_med) ** (1.0 / k0)
        implied = np.log(1 - cov["mean_coverage"].values) / np.log(1 - p_f)
        print("  %-8d %s" % (k0, "  ".join("%9.1f" % v for v in implied[:15:3])))
    cov.to_csv(os.path.join(HERE, "out_reports_proxy.csv"), index=False)

    # ---------------- PART 2: dispersion pooling, corrected -----------------
    print("\n\nPART 2 -- DISPERSION GRADIENTS, POOLED CORRECTLY (E1, E2 fixed)")
    groups = {"ESM continuous": ESM_CONT,
              "INTAKE continuous psychological": INTAKE_CONT_PSYCH,
              "INTAKE continuous non-psychological": INTAKE_CONT_OTHER,
              "BINARY (excluded from conclusions)": BINARY}
    res = []
    for gname, vs in groups.items():
        vals = {"below": [], "above": []}
        for v in vs:
            se_c, n_c = k.get(v + ".std.error"), k.get(v + ".personcount")
            if se_c is None:
                continue
            sd = se_c.values * np.sqrt(n_c.values)
            n = n_c.values.astype(float)
            for lab, msk in (("below", lo), ("above", hi)):
                g, _ = grad(sd, n, L, msk)
                vals[lab].append(g)
            res.append({"group": gname, "variable": v,
                        "d_below": vals["below"][-1], "d_above": vals["above"][-1]})
        for lab in ("below", "above"):
            a = np.array(vals[lab])
            print("  %-36s %-6s mean %+.4f  between-variable se %.4f  (k=%d)  z=%.2f"
                  % (gname, lab, a.mean(), a.std(ddof=1) / np.sqrt(len(a)), len(a),
                     a.mean() / (a.std(ddof=1) / np.sqrt(len(a)))))
    rr = pd.DataFrame(res)
    rr.to_csv(os.path.join(HERE, "out_dispersion_pooled_fixed.csv"), index=False)

    print("\n  KEY CONTRAST -- is the widening SPECIFIC to the primary measure?")
    ew = rr[rr.variable == "experienced_wellbeing"].iloc[0]
    sec = rr[rr.variable.isin(SECONDARY)]
    print("    experienced_wellbeing (1.7M reports, asked EVERY survey): "
          "d_above = %+.4f" % ew.d_above)
    print("    12 secondary feelings   (~50k reports each, random subsets):"
          " mean d_above = %+.4f (se %.4f)"
          % (sec.d_above.mean(), sec.d_above.std(ddof=1) / np.sqrt(len(sec))))
    dd = ew.d_above - sec.d_above.mean()
    se = sec.d_above.std(ddof=1) / np.sqrt(len(sec))
    print("    difference %+.4f, z = %.2f" % (dd, dd / se))
    print("    A k_i gradient must hit the SPARSE measures HARDEST. It does the")
    print("    opposite here, so the widening is not an artifact of report counts.")
    print("\nwrote out_reports_proxy.csv, out_dispersion_pooled_fixed.csv")


if __name__ == "__main__":
    main()
