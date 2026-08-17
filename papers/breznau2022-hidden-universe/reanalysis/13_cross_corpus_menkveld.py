"""Put the Crowdsourced Replication Initiative on the same scale as #fincap.

Menkveld et al. 2024 (J. Finance, 164 teams, six hypotheses on 17 years of
EuroStoxx 50 futures data) define the *nonstandard error* (NSE) of a hypothesis
as the INTERQUARTILE RANGE of estimates across research teams, deliberately
choosing a robust dispersion measure because "the distribution of the SD could
exhibit fat tails and thus be prone to outliers". For their first hypothesis
they report, on p. 2345:

    median estimate      -1.1 %
    NSE (IQR)             6.7 percentage points
    IDR (interdecile)    27.3 percentage points
    median SE across RTs  2.5 %
    and note that a Gaussian with that SE implies an IQR of 1.35 x 2.5 = 3.4,
    "which compares to an NSE of 6.7".

Two quantities can be computed from that and compared with CRI, which nobody has
done because the two literatures do not cite each other in this direction:

  1. tau / median SE -- how large is researcher-induced dispersion relative to
     sampling error. Menkveld's numbers imply tau = sqrt((6.7/1.349)^2 - 2.5^2).

  2. IDR / IQR -- a distribution shape statistic. For a Gaussian it is
     2.563/1.349 = 1.90, and NOTHING about the number of teams changes that.
     Menkveld's H1 gives 27.3/6.7 = 4.07, i.e. drastically heavier tailed than
     Gaussian. If CRI shows the same, then heavy tails are a property of
     many-analysts corpora rather than of one dataset -- which would mean the
     variance-decomposition framing used by Breznau et al. (and by anyone
     reporting '% of variance explained') is the wrong instrument by default,
     not by accident.

This script computes both for CRI. Their numbers are entered by hand from the
paper because only pages 2339-2350 were obtainable; they are marked as such.
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "cri_model_level.csv")
Z95 = 1.959964
GAUSS_IQR = 1.3490          # IQR of a standard normal
GAUSS_IDR = 2.5631          # interdecile range of a standard normal


def pm(y, v, it=200):
    if len(y) < 3:
        return np.nan
    lo, hi = 0.0, max(1e-12, np.var(y, ddof=1) * 50)

    def gq(t2):
        w = 1 / (v + t2)
        mu = (w * y).sum() / w.sum()
        return (w * (y - mu) ** 2).sum() - (len(y) - 1)
    if gq(lo) <= 0:
        return 0.0
    if gq(hi) > 0:
        return hi
    for _ in range(it):
        mid = .5 * (lo + hi)
        if gq(mid) > 0:
            lo = mid
        else:
            hi = mid
    return .5 * (lo + hi)


def shape(x):
    q10, q25, q75, q90 = np.percentile(x, [10, 25, 75, 90])
    iqr, idr = q75 - q25, q90 - q10
    return iqr, idr, idr / iqr if iqr > 0 else np.nan


def main():
    d = pd.read_csv(DATA, low_memory=False)
    a = d[d.AME_Z.notna() & (d.u_teamid != 0)].copy()
    a["se_z"] = (a.upper_Z - a.lower_Z) / (2 * Z95)
    a = a[np.isfinite(a.se_z) & (a.se_z > 0)].copy()
    y, se = a.AME_Z.values, a.se_z.values
    v = se ** 2

    print("=" * 72)
    print("MENKVELD ET AL. 2024, #fincap, RT-H1 (entered by hand from p. 2345)")
    print("=" * 72)
    m_nse, m_idr, m_medse = 6.7, 27.3, 2.5
    m_sd_total = m_nse / GAUSS_IQR
    m_tau = np.sqrt(max(0.0, m_sd_total ** 2 - m_medse ** 2))
    print("  NSE (IQR of estimates across 164 teams) = %.1f pp" % m_nse)
    print("  median SE across teams                  = %.1f pp" % m_medse)
    print("  implied total SD (IQR / 1.349)          = %.2f pp" % m_sd_total)
    print("  implied between-team tau                = %.2f pp" % m_tau)
    print("  tau / median SE                         = %.2f" % (m_tau / m_medse))
    print("  IDR / IQR                               = %.2f  (Gaussian: %.2f)"
          % (m_idr / m_nse, GAUSS_IDR / GAUSS_IQR))

    print()
    print("=" * 72)
    print("CRI (Breznau et al. 2022), computed here, n = %d models, %d teams"
          % (len(a), a.u_teamid.nunique()))
    print("=" * 72)
    iqr, idr, ratio = shape(y)
    print("  NSE, i.e. IQR of standardized estimates = %.5f SD units" % iqr)
    print("  IDR                                     = %.5f" % idr)
    print("  median SE                               = %.5f" % np.median(se))
    print("  implied total SD (IQR / 1.349)          = %.5f" % (iqr / GAUSS_IQR))
    print("  IDR / IQR                               = %.2f  (Gaussian: %.2f)"
          % (ratio, GAUSS_IDR / GAUSS_IQR))
    for name, t in [("DL", 0.00363), ("REML", 0.01185), ("PM", np.sqrt(pm(y, v)))]:
        print("  tau / median SE  [%-4s tau = %.5f]      = %.2f"
              % (name, t, t / np.median(se)))
    print("  robust tau from the IQR, sampling removed = %.5f -> tau/medSE = %.2f"
          % (np.sqrt(max(0.0, (iqr / GAUSS_IQR) ** 2 - np.median(se) ** 2)),
             np.sqrt(max(0.0, (iqr / GAUSS_IQR) ** 2 - np.median(se) ** 2)) / np.median(se)))

    print("\n  per dependent variable (the closest analogue to their six")
    print("  separate RT hypotheses, since each DV is a distinct question):")
    rows = []
    for dv, sub in a.groupby("DV"):
        if len(sub) < 20:
            continue
        yy, ss = sub.AME_Z.values, sub.se_z.values
        i, dd, r = shape(yy)
        tot = i / GAUSS_IQR
        med = np.median(ss)
        tau = np.sqrt(max(0.0, tot ** 2 - med ** 2))
        rows.append((dv, len(sub), i, dd, r, med, tau, tau / med if med else np.nan))
    print(pd.DataFrame(rows, columns=["DV", "n", "NSE(IQR)", "IDR", "IDR/IQR",
                                      "med SE", "tau", "tau/medSE"])
          .sort_values("n", ascending=False)
          .to_string(index=False, float_format=lambda x: "%.4f" % x))

    print("\n  same, at TEAM level (one estimate per team, their unit):")
    tm = a.groupby("u_teamid").AME_Z.median().values
    i, dd, r = shape(tm)
    print("    n teams = %d, NSE(IQR) = %.5f, IDR = %.5f, IDR/IQR = %.2f"
          % (len(tm), i, dd, r))

    print("\n" + "=" * 72)
    print("SANITY: IDR/IQR of samples DRAWN from a normal, at these n")
    print("=" * 72)
    rng = np.random.default_rng(5)
    for n in (71, 164, 1252):
        vals = [shape(rng.normal(size=n))[2] for _ in range(2000)]
        print("  n = %4d -> IDR/IQR = %.2f (sd %.2f, 2.5-97.5%%: %.2f-%.2f)"
              % (n, np.mean(vals), np.std(vals),
                 np.percentile(vals, 2.5), np.percentile(vals, 97.5)))
    print("  A ratio far above this band cannot be explained by sample size and")
    print("  is evidence of genuinely heavy tails.")


if __name__ == "__main__":
    main()
