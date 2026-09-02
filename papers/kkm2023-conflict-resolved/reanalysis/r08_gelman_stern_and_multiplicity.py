#!/usr/bin/env python3
"""r08 -- three inferential questions KKM (2023) does not ask of its own Table 1.

Q1  GELMAN-STERN.  The paper's headline scope claim -- flattening "restricted to
    the least happy 20%" -- is a claim that the above-$100k slope DIFFERS between
    low and middle percentiles. Table 1 supports it only by noting that the low
    ones are non-significant and the middle ones are significant. The difference
    between significant and non-significant is not itself significant (Gelman &
    Stern 2006). Test it directly, using the paired-bootstrap covariance between
    quantile slopes on the same data, which no per-row standard error supplies.

Q2  WHAT DOES "FLAT" EXCLUDE?  A non-significant slope is an interval, not a zero.
    Report the CI on each above-$100k slope, and in particular whether it excludes
    the median's slope.

Q3  MULTIPLICITY.  The paper reports 7 rows x 2 slopes in Table 1 plus 5
    interaction tests in the Fig. 2 text. One of its three findings -- the
    acceleration at the 85th percentile -- is explicitly described as
    unanticipated ("A third pattern, which we had not anticipated"). Post hoc
    findings are exactly the ones multiplicity should discount.

Q4  LOCATION-SCALE LACK OF FIT, done correctly. r04 and r05 tested this with a
    chi-square that assumed the tau-specific estimates were independent. They are
    not, and that test was invalid; it is redone here as a Wald test against the
    bootstrap covariance matrix. (Recording the invalid version and its
    replacement rather than deleting it: CONTRIBUTING.md rule 4.)

Requires out_bootstrap_slopes.npz from r02.
Output: out_gelman_stern.csv
"""
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
NPZ = os.path.join(HERE, "out_bootstrap_slopes.npz")


def main():
    z = np.load(NPZ)
    taus = list(z["taus"])
    A = z["above"]          # [B, ntau]
    Bm = z["below"]
    a0, b0 = z["above_point"], z["below_point"]
    B = A.shape[0]
    print("paired bootstrap: B = %d replicates, %d quantiles\n" % (B, len(taus)))

    # ---------------- Q1 ---------------------------------------------------
    print("Q1  GELMAN-STERN: is the ABOVE-$100k slope different between "
          "percentiles?\n    (KKM call tau<=.20 'flat' and tau>=.25 'not flat')")
    rows = []
    pairs = [(0.05, 0.25), (0.10, 0.25), (0.15, 0.25), (0.15, 0.30), (0.15, 0.35),
             (0.20, 0.25), (0.20, 0.30), (0.15, 0.50), (0.15, 0.85)]
    print("    %-14s %-9s %-9s %-9s %-8s %-9s" %
          ("pair", "slope1", "slope2", "diff", "se(diff)", "p"))
    for t1, t2 in pairs:
        i, j = taus.index(t1), taus.index(t2)
        dif = A[:, j] - A[:, i]
        d0 = a0[j] - a0[i]
        se = dif.std(ddof=1)
        p = 2 * min((dif <= 0).mean(), (dif >= 0).mean())
        p = max(p, 1.0 / B)
        print("    tau %.2f vs %.2f  %-9.3f %-9.3f %-9.3f %-8.3f %-9.4g%s"
              % (t1, t2, a0[i], a0[j], d0, se, p, "  *" if p < 0.05 else ""))
        rows.append({"q": "gelman_stern", "tau1": t1, "tau2": t2,
                     "slope1": a0[i], "slope2": a0[j], "diff": d0,
                     "se": se, "p": p})
    print("    NOTE: p here is the bootstrap two-sided percentile p; the floor is "
          "1/B = %.4f" % (1.0 / B))

    # ---------------- Q2 ---------------------------------------------------
    print("\nQ2  WHAT DOES 'FLAT' EXCLUDE?  95%% CI on the above-$100k slope")
    imed = taus.index(0.50)
    med_slope = a0[imed]
    print("    %-6s %-8s %-20s %-32s" %
          ("tau", "slope", "95% CI", "does the CI exclude ..."))
    for t in taus:
        i = taus.index(t)
        lo, hi = np.percentile(A[:, i], [2.5, 97.5])
        excl = []
        if not (lo <= 0 <= hi):
            excl.append("zero")
        if not (lo <= med_slope <= hi):
            excl.append("the median's slope (%.2f)" % med_slope)
        if not (lo <= b0[i] <= hi):
            excl.append("its own below-100k slope (%.2f)" % b0[i])
        print("    %-6.2f %-8.3f [%6.3f, %6.3f]   %s"
              % (t, a0[i], lo, hi, "; ".join(excl) if excl else "nothing"))
        rows.append({"q": "ci", "tau1": t, "slope1": a0[i], "ci_lo": lo, "ci_hi": hi})

    # ---------------- Q3 ---------------------------------------------------
    print("\nQ3  MULTIPLICITY over the tests the paper reports")
    reported = [("Table1 above-slope tau=.05", 0.62), ("Table1 above tau=.10", 0.16),
                ("Table1 above tau=.15", 0.32), ("Table1 above tau=.20", 0.08),
                ("Table1 above tau=.25", 0.001), ("Table1 above tau=.30", 0.0001),
                ("Table1 above tau=.35", 0.0001),
                ("Fig2 interaction tau=.15", 0.0002),
                ("Fig2 interaction tau=.30", 0.80),
                ("Fig2 interaction tau=.50", 0.52),
                ("Fig2 interaction tau=.70", 0.075),
                ("Fig2 interaction tau=.85", 0.023)]
    ps = np.array([p for _, p in reported])
    order = np.argsort(ps)
    m = len(ps)
    holm = np.empty(m)
    running = 0.0
    for rank, k in enumerate(order):
        v = min(1.0, (m - rank) * ps[k])
        running = max(running, v)
        holm[k] = running
    print("    %-28s %-10s %-12s %-12s" % ("test", "p", "Bonf(12)", "Holm"))
    for (name, p), h in zip(reported, holm):
        print("    %-28s %-10.4g %-12.4g %-12.4g%s"
              % (name, p, min(1, p * m), h, "  survives" if h < 0.05 else ""))
        rows.append({"q": "multiplicity", "test": name, "p": p,
                     "bonferroni": min(1, p * m), "holm": h})

    # ---------------- Q4 ---------------------------------------------------
    print("\nQ4  LOCATION-SCALE LACK OF FIT, with the correct covariance")
    for lab, M, pt in (("above 100k", A, a0), ("below 100k", Bm, b0)):
        f = np.array([stats.norm.ppf(t) for t in taus])
        X = np.column_stack([np.ones(len(taus)), f])
        S = np.cov(M, rowvar=False)
        Sinv = np.linalg.pinv(S)
        beta = np.linalg.solve(X.T @ Sinv @ X, X.T @ Sinv @ pt)
        r = pt - X @ beta
        W = float(r @ Sinv @ r)
        df = len(taus) - 2
        p = 1 - stats.chi2.cdf(W, df)
        # what a rank-deficient bootstrap covariance would do: report the rank
        rank = np.linalg.matrix_rank(S)
        print("    %-11s mu'=%+.3f sigma'=%+.3f   Wald lack-of-fit = %.2f on %d df, "
              "p = %.4f   (cov rank %d/%d)"
              % (lab, beta[0], beta[1], W, df, p, rank, len(taus)))
        se_sig = float(np.sqrt(np.linalg.inv(X.T @ Sinv @ X)[1, 1]))
        print("                sigma' / se = %.2f  -> the WIDTH gradient itself is "
              "%s" % (beta[1] / se_sig,
                      "significant" if abs(beta[1] / se_sig) > 1.96 else "not significant"))
        rows.append({"q": "locscale", "side": lab, "mu_prime": beta[0],
                     "sigma_prime": beta[1], "se_sigma_prime": se_sig,
                     "wald": W, "df": df, "p": p})

    pd.DataFrame(rows).to_csv(os.path.join(HERE, "out_gelman_stern.csv"), index=False)
    print("\nwrote out_gelman_stern.csv")


if __name__ == "__main__":
    main()
