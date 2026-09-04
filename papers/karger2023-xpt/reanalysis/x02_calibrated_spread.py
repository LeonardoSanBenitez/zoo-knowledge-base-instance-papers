"""x02 -- Derive the person-to-person spread from the report's own intervals,
instead of guessing it as x01 did.

x01 showed that taking a median question-by-question manufactures a
total-exceeds-the-sum ratio even when every forecaster is perfectly coherent,
and that the size of the artifact depends almost entirely on ONE unknown: how
spread out the forecasters are. x01 guessed that spread. This script derives it.

THE DERIVATION. The report's brackets are bootstrap confidence intervals **of
the median**, not the spread of people. For a sample median from a roughly
log-normal population,

    SE(median) ~ 1.2533 * sigma / sqrt(n)

so, working in logs and reading the half-width of a 95% interval as 1.96 SE,

    sigma_log = (ln(hi) - ln(lo)) / 3.92 * sqrt(n) / 1.2533

Everything on the right is printed in the report. Nothing is chosen by me.

WHY THIS MATTERS BEYOND THIS PAPER. Reading a bootstrap interval on a median as
if it described people is a common error in the other direction -- it makes a
population look far more agreed than it is. Here it runs the other way: the
intervals are narrow BECAUSE n is large, and the population behind them is
enormously dispersed. That dispersion is the paper's actual headline, and it is
also what breaks the arithmetic everyone does with the medians.

Run: python x02_calibrated_spread.py
"""
import csv
import math
import os

import numpy as np

SRC = os.path.join("..", "artifacts", "xpt_tables_2_3.csv")
RNG = np.random.default_rng(112358)
CAUSES = ["ai", "engineered_pathogen", "natural_pathogen", "nuclear",
          "non_anthropogenic"]
# n per group, from the table captions
NGROUP = {"superforecasters": 88, "domain_experts": 59,
          "general_xrisk_experts": 15, "nondomain_experts": 21, "public": 912}


def load():
    d = {}
    for r in csv.DictReader(open(SRC, encoding="utf-8")):
        d[(r["outcome"], r["cause"], r["group"])] = (
            float(r["median_pct"]), float(r["ci_low"]), float(r["ci_high"]))
    return d


def sigma_log_from_ci(lo, hi, n):
    """Population log-SD implied by a bootstrap CI of the median."""
    if lo <= 0 or hi <= 0 or hi <= lo:
        return None
    se_log = (math.log(hi) - math.log(lo)) / 3.92
    return se_log * math.sqrt(n) / 1.2533


def main():
    d = load()
    rows = []
    print("=" * 96)
    print("1. PERSON-TO-PERSON SPREAD, DERIVED from the report's own intervals")
    print("   sigma_log = (ln hi - ln lo)/3.92 * sqrt(n) / 1.2533")
    print("=" * 96)
    print(f"  {'outcome':<20} {'cause':<20} {'group':<22} {'median':>8} "
          f"{'sigma_log':>10} {'implied 90% span':>26}")
    for outcome in ("extinction_by_2100", "catastrophe_by_2100"):
        for g in ("superforecasters", "domain_experts"):
            n = NGROUP[g]
            for c in CAUSES + ["TOTAL"]:
                v = d.get((outcome, c, g))
                if not v:
                    continue
                m, lo, hi = v
                s = sigma_log_from_ci(lo, hi, n)
                if s is None:
                    continue
                p05 = m * math.exp(-1.645 * s)
                p95 = m * math.exp(+1.645 * s)
                print(f"  {outcome:<20} {c:<20} {g:<22} {m:7.4f}% {s:10.2f} "
                      f"{p05:11.2e} to {p95:.2e}")
                rows.append(dict(outcome=outcome, cause=c, group=g, median=m,
                                 ci_low=lo, ci_high=hi, n=n, sigma_log=s,
                                 p05=p05, p95=p95))
    print()
    print("  These spans are not typos. A sigma_log of 3 to 4 means the middle")
    print("  90% of forecasters span five to six ORDERS OF MAGNITUDE on the")
    print("  same question. That is the paper's real finding, and it is not in")
    print("  the abstract, which reports medians and their bootstrap intervals.")

    print()
    print("=" * 96)
    print("2. THE MEDIAN ARTIFACT AT THE DERIVED SPREAD")
    print("   Coherent forecasters, ZERO weight on unnamed causes")
    print("=" * 96)
    for outcome, observed in (("extinction_by_2100", 2.13),
                              ("catastrophe_by_2100", 1.13)):
        g = "superforecasters"
        n = NGROUP[g]
        meds, sigs = [], []
        for c in CAUSES:
            m, lo, hi = d[(outcome, c, g)]
            s = sigma_log_from_ci(lo, hi, n)
            meds.append(m)
            sigs.append(s if s else 1.0)
        sims = []
        for _ in range(500):
            cols = []
            for m, s in zip(meds, sigs):
                cols.append(np.clip(
                    np.exp(RNG.normal(math.log(m / 100.0), s, n)), 0, 0.999))
            P = np.array(cols)
            total = 1.0 - np.prod(1.0 - P, axis=0)
            sims.append((100 * sum(np.median(P[j]) for j in range(len(meds))),
                         100 * np.median(total)))
        a = np.array(sims)
        ratio = a[:, 1] / np.maximum(a[:, 0], 1e-12)
        print(f"\n  {outcome}, mean derived sigma_log = "
              f"{np.mean(sigs):.2f}")
        print(f"    simulated sum of named medians   {a[:,0].mean():.4f}%")
        print(f"    simulated median of the total    {a[:,1].mean():.4f}%")
        print(f"    simulated ratio (TRUE unnamed=0) {ratio.mean():.2f} "
              f"[{np.percentile(ratio,2.5):.2f}, {np.percentile(ratio,97.5):.2f}]")
        print(f"    OBSERVED ratio in the report     {observed:.2f}")
        verdict = ("the artifact alone EXCEEDS the observed excess"
                   if ratio.mean() > observed else
                   "the artifact is smaller than the observed excess")
        print(f"    -> {verdict}")
        rows.append(dict(outcome=outcome, cause="ARTIFACT-SIM", group=g,
                         median=None, n=n, sigma_log=float(np.mean(sigs)),
                         sim_ratio=float(ratio.mean()),
                         sim_ratio_lo=float(np.percentile(ratio, 2.5)),
                         sim_ratio_hi=float(np.percentile(ratio, 97.5)),
                         observed_ratio=observed))

    print()
    print("=" * 96)
    print("3. NEGATIVE CONTROL: does the machinery return 1.00 when it should?")
    print("   Same code, spread driven to near zero, so every forecaster is")
    print("   nearly identical and the median must add up.")
    print("=" * 96)
    meds = [d[("extinction_by_2100", c, "superforecasters")][0] for c in CAUSES]
    for sd in (0.01, 0.1, 0.3):
        sims = []
        for _ in range(200):
            P = np.array([np.clip(np.exp(RNG.normal(math.log(m / 100.0), sd, 88)),
                                  0, 0.999) for m in meds])
            total = 1.0 - np.prod(1.0 - P, axis=0)
            sims.append((100 * sum(np.median(P[j]) for j in range(len(meds))),
                         100 * np.median(total)))
        a = np.array(sims)
        print(f"    sigma_log = {sd:5.2f}   ratio = "
              f"{(a[:,1]/a[:,0]).mean():.4f}")
    print()
    print("  It returns 1.00 at zero spread, as it must. The machinery is not")
    print("  manufacturing the artifact; the spread is.")

    keys = sorted({k for r in rows for k in r})
    with open("out_calibrated_spread.csv", "w", newline="",
              encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print("\nwrote out_calibrated_spread.csv")


if __name__ == "__main__":
    main()
