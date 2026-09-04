"""m09 -- The estimator this problem actually wants, and the answer it gives.

TWO JOBS.

(1) FIX A WEAKNESS IN MY OWN m08. There, "deletion off" gave incompatible
    trials sigma_TE = 0.001 and then meta-analysed log(sigma_TE). On a log
    scale a zero is minus infinity, so that column was sensitive to a floor I
    chose. The criticism of the deletion stands only if it survives a pooling
    scale on which zero is an ordinary number. So: redo it on one.

(2) BUILD THE ESTIMATOR THE PROBLEM WANTS. The identity underneath everything
    here is

        sigma_AT^2 - sigma_PL^2 = sigma_TE^2 + 2 rho sigma_PL sigma_TE      (*)

    The LEFT side is a difference of two variances. It is estimable without
    assumption, its sampling distribution is known, it is unbiased, IT CAN BE
    NEGATIVE, and it needs no square root, no branch choice and no deletion.
    Every pathology in the published pipeline enters when (*) is inverted for
    sigma_TE before pooling rather than after.

    So: pool D = sigma_AT^2 - sigma_PL^2 across trials, THEN invert once, and
    report sigma_TE as a curve in rho rather than a number. Under rho = 0 the
    inversion is sigma_TE = sqrt(max(D, 0)) and D <= 0 is a perfectly
    intelligible result meaning "no excess variance in the drug arm".

    Var(s^2) = 2 sigma^4 / (n-1) for a normal sample, so
    Var(D_s) = 2 sigma_AT^4/(n_AT - 1) + 2 sigma_PL^4/(n_PL - 1).

(3) Apply it to the real antidepressant corpus and report the sensitivity
    curve, which is the honest output when a parameter is not identified.

Run: python m09_variance_difference.py
"""
import csv
import math
import os
import sys

import numpy as np
from scipy import stats

sys.path.insert(0, os.path.join("..", "..", "..", "..", "tools"))
from statlib import re_meta  # noqa: E402

ARMS = os.path.join("..", "artifacts", "mcc2021_arm_sizes.csv")
REAL = os.path.join("..", "..", "munkholm2020-antidepressant-variability",
                    "reanalysis", "out_comparisons.csv")
RNG = np.random.default_rng(9091)

MEAN_EFFECT = -8.6
TAU_EFFECT = 3.3


def load_arms():
    pl, dr = [], []
    with open(ARMS, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            n_p = float(r["n_placebo"])
            n_d = float(r["n_drug_total"]) / float(r["n_drug_arms"])
            if n_p >= 10 and n_d >= 10:
                pl.append(int(n_p))
                dr.append(int(round(n_d)))
    return np.array(pl), np.array(dr)


def one_world(n_pl, n_dr, sigma_te_true, tau_placebo, rng, sd_change=20.0):
    k = len(n_pl)
    mu_pl = rng.normal(-9.0, tau_placebo, k)
    eff = rng.normal(MEAN_EFFECT, TAU_EFFECT, k)
    out = []
    for s in range(k):
        chg_p = rng.normal(mu_pl[s], sd_change, n_pl[s])
        base_d = rng.normal(mu_pl[s], sd_change, n_dr[s])
        d_i = (np.full(n_dr[s], eff[s]) if sigma_te_true == 0
               else rng.normal(eff[s], sigma_te_true, n_dr[s]))
        chg_d = base_d + d_i
        out.append(dict(n_p=n_pl[s], n_d=n_dr[s],
                        sd_p=chg_p.std(ddof=1), sd_d=chg_d.std(ddof=1)))
    return out


def pool_variance_difference(trials, method="PM"):
    """Pool D = s_AT^2 - s_PL^2. No log, no root, no deletion."""
    y, v = [], []
    for t in trials:
        vp, vd = t["sd_p"] ** 2, t["sd_d"] ** 2
        y.append(vd - vp)
        v.append(2 * vd ** 2 / (t["n_d"] - 1) + 2 * vp ** 2 / (t["n_p"] - 1))
    m = re_meta(np.array(y), np.array(v), method=method)
    return m


def sigma_te_from_D(D, sd_pl, rho):
    """Invert (*) once, after pooling. Returns None where no real solution
    exists -- which is a RESULT, not a trial to delete."""
    disc = rho ** 2 * sd_pl ** 2 + D
    if disc < 0:
        return None
    return math.sqrt(disc) - rho * sd_pl


def main():
    n_pl, n_dr = load_arms()
    reps = 300
    rows = []

    print("=" * 98)
    print("1. THE VARIANCE-DIFFERENCE ESTIMATOR ON KNOWN WORLDS")
    print("   D = sigma_AT^2 - sigma_PL^2. Truth is D = sigma_TE^2 when rho = 0.")
    print("=" * 98)
    print(f"{'true sigma_TE':>14} {'true D':>9} | {'pooled D':>22} | "
          f"{'sqrt(max(D,0))':>15} | {'covers truth':>12}")
    for true_ste in (0.0, 4.0, 8.0, 13.5, 20.0):
        Ds, los, his, cov = [], [], [], 0
        for _ in range(reps):
            tr = one_world(n_pl, n_dr, true_ste, 5.0, RNG)
            m = pool_variance_difference(tr)
            Ds.append(m["mu"])
            los.append(m["ci"][0])
            his.append(m["ci"][1])
            if m["ci"][0] <= true_ste ** 2 <= m["ci"][1]:
                cov += 1
        Ds = np.array(Ds)
        print(f"{true_ste:14.1f} {true_ste**2:9.1f} | {Ds.mean():9.1f} "
              f"[{np.percentile(Ds,2.5):7.1f},{np.percentile(Ds,97.5):7.1f}] | "
              f"{math.sqrt(max(Ds.mean(),0)):15.2f} | {100*cov/reps:11.0f}%")
        rows.append(dict(check="variance-difference", true_sigma_te=true_ste,
                         true_D=true_ste ** 2, pooled_D=Ds.mean(),
                         coverage_pct=100 * cov / reps))
    print()
    print("  Unbiased, and it returns a NEGATIVE or zero D when there is nothing")
    print("  there instead of deleting the trial. CAVEAT: coverage falls below")
    print("  nominal as the true sigma_TE grows, because Var(s^2) = 2 sigma^4/(n-1)")
    print("  assumes normality and the drug arm is a MIXTURE once effects vary.")
    print("  At sigma_TE = 20 the drug arm has excess kurtosis and the interval")
    print("  is too narrow. Use a bootstrap there; the null case, which is what")
    print("  this paper turns on, is unaffected.")

    print()
    print("=" * 98)
    print("2. THE m08 CRITICISM, REDONE ON A SCALE WHERE ZERO IS ORDINARY")
    print("   Null world, true sigma_TE = 0. Published pipeline vs this one.")
    print("=" * 98)
    ds, sts, excl = [], [], 0
    for _ in range(reps):
        tr = one_world(n_pl, n_dr, 0.0, 5.0, RNG)
        m = pool_variance_difference(tr)
        ds.append(m["mu"])
        sts.append(math.sqrt(max(m["mu"], 0.0)))
        if not (m["ci"][0] <= 0.0 <= m["ci"][1]):
            excl += 1
    ds = np.array(ds)
    print(f"  pooled D                 {ds.mean():+8.2f} "
          f"[{np.percentile(ds,2.5):+.2f},{np.percentile(ds,97.5):+.2f}]"
          f"   (true value 0.00)")
    print(f"  implied sigma_TE at rho=0 {np.mean(sts):8.2f} PANSS points")
    print(f"  false-positive rate: 95% CI for D excludes the true 0 in "
          f"{100*excl/reps:.1f}% of runs   (nominal 5%)")
    print()
    print("  Against the published pipeline's 14.8 on the same worlds (m07/m08).")
    print("  So the m08 finding survives a pooling scale on which zero is an")
    print("  ordinary number, and the floor I chose there was not doing the work.")

    print()
    print("=" * 98)
    print("3. REAL DATA -- antidepressants (Cipriani GRISELDA), sensitivity in rho")
    print("=" * 98)
    tri = []
    with open(REAL, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            try:
                t = dict(n_p=float(r["n_pbo"]), n_d=float(r["n_drug"]),
                         sd_p=float(r["sd_pbo"]), sd_d=float(r["sd_drug"]),
                         study=r["study"], is_change=r["is_change"] == "True")
            except ValueError:
                continue
            if t["n_p"] > 2 and t["n_d"] > 2 and t["sd_p"] > 0 and t["sd_d"] > 0:
                tri.append(t)
    for subset, sel in (("all comparisons", lambda t: True),
                        ("change scores", lambda t: t["is_change"]),
                        ("raw endpoints", lambda t: not t["is_change"])):
        sub = [t for t in tri if sel(t)]
        if len(sub) < 10:
            continue
        m = pool_variance_difference(sub)
        sd_pl = float(np.mean([t["sd_p"] for t in sub]))
        print(f"\n  --- {subset}: k = {len(sub)}, "
              f"{len({t['study'] for t in sub})} studies, "
              f"mean SD(placebo) = {sd_pl:.2f} ---")
        print(f"    pooled D = sigma_AT^2 - sigma_PL^2 = {m['mu']:+.3f} "
              f"[{m['ci'][0]:+.3f}, {m['ci'][1]:+.3f}]   "
              f"(units: squared scale points)")
        print(f"    I2 = {100*m['I2']:.0f}%,  tau = {m['tau']:.3f},  "
              f"p = {m['p']:.3g}")
        print(f"    {'rho assumed':>13} | {'implied sigma_TE':>17} | "
              f"{'as a fraction of the 2.7-point mean drug-placebo difference':>16}")
        for rho in (0.0, -0.10, -0.21, -0.32, -0.39, -0.62):
            s = sigma_te_from_D(m["mu"], sd_pl, rho)
            lo = sigma_te_from_D(m["ci"][0], sd_pl, rho)
            hi = sigma_te_from_D(m["ci"][1], sd_pl, rho)
            f = lambda x: "     n/a" if x is None else f"{x:8.2f}"
            frac = "" if s is None else f"{s/2.7:8.2f}x"
            print(f"    {rho:13.2f} | {f(s)} [{f(lo)},{f(hi)}] | {frac:>16}")
            rows.append(dict(check="real-antidepressant", subset=subset,
                             k=len(sub), pooled_D=m["mu"], rho=rho,
                             sigma_te=None if s is None else round(s, 3)))
    print()
    print("  THE HONEST OUTPUT IS THIS CURVE, NOT A NUMBER. sigma_TE is not")
    print("  identified from aggregate data without rho. What the data DO fix is")
    print("  D, and D is what should be reported.")

    keys = sorted({k for r in rows for k in r})
    with open("out_variance_difference.csv", "w", newline="",
              encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print("\nwrote out_variance_difference.csv")


if __name__ == "__main__":
    main()
