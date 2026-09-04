"""x01 -- The reported medians imply a large probability on causes nobody asked
about. Is that a belief, or an artifact of taking medians?

THE OBSERVATION. The XPT reports, per group, a median probability for each named
cause AND a median for the total. For extinction by 2100 the superforecasters'
named causes sum to 0.47% while their reported total is 1.00% -- the total is
2.1x the sum of its named parts.

THE PROBLEM WITH CALLING THAT INCOHERENT. Two innocent explanations exist and
both must be dealt with before the interesting one is allowed:

  (a) UNNAMED CAUSES. "Total extinction risk" is extinction from ANY cause. If a
      forecaster puts weight on something the tournament did not ask about, the
      total legitimately exceeds the sum of the named parts. This is not an
      error; it is a quantity, and an interesting one -- how much of the
      probability mass sits outside the questions the field is arguing about.

  (b) THE MEDIAN IS NOT ADDITIVE. Every number here is a median across people,
      taken question by question. The median of the totals is not the sum of the
      medians even if EVERY individual is perfectly coherent. So a positive
      residual can appear with no unnamed-cause weight at all.

This script separates them. It builds populations of perfectly coherent
forecasters with a KNOWN unnamed-cause weight, computes the medians the XPT
would have reported, and reads off the residual. If the residual is inflated at
a true weight of zero, the observed residual is partly artifact and the size of
the artifact is measurable.

DATA: artifacts/xpt_tables_2_3.csv, transcribed by hand from the report's
Tables 2 and 3 using PDF word coordinates, because the linear text extraction
mis-assigns columns (two rows have an empty non-domain-expert cell, and a naive
reader shifts every later value one column left).

Run: python x01_residual.py
"""
import csv
import math
import os

import numpy as np

SRC = os.path.join("..", "artifacts", "xpt_tables_2_3.csv")
RNG = np.random.default_rng(20260904)

CAUSES = ["ai", "engineered_pathogen", "natural_pathogen", "nuclear",
          "non_anthropogenic"]


def load():
    rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
    d = {}
    for r in rows:
        d[(r["outcome"], r["cause"], r["group"])] = (
            float(r["median_pct"]), float(r["ci_low"]), float(r["ci_high"]))
    return d


def observed_residuals(d):
    print("=" * 94)
    print("1. OBSERVED: total vs the sum of the named causes, from the report")
    print("=" * 94)
    out = []
    for outcome in ("catastrophe_by_2100", "extinction_by_2100"):
        print(f"\n  {outcome}")
        print(f"    {'group':<24} {'sum of named':>13} {'reported total':>15} "
              f"{'total/sum':>10} {'implied unnamed':>16}")
        for g in ("superforecasters", "domain_experts", "general_xrisk_experts"):
            parts = [d.get((outcome, c, g)) for c in CAUSES]
            if any(p is None for p in parts):
                continue
            tot = d.get((outcome, "TOTAL", g))
            if tot is None:
                continue
            s = sum(p[0] for p in parts)
            ratio = tot[0] / s
            unnamed = tot[0] - s
            print(f"    {g:<24} {s:12.3f}% {tot[0]:14.3f}% {ratio:10.2f} "
                  f"{unnamed:15.3f}%")
            out.append(dict(outcome=outcome, group=g, sum_named=s,
                            total=tot[0], ratio=ratio, unnamed=unnamed,
                            unnamed_share=unnamed / tot[0]))
    print()
    print("  A ratio above 1 is not an error by itself: the total covers causes")
    print("  the tournament never listed. The question is how much of it is that,")
    print("  and how much is the median refusing to add up.")
    return out


def simulate(medians, cis, n_people, unnamed_frac, reps, rng, sd_log=None):
    """Population of COHERENT forecasters.

    Each person i has, for each named cause c, a probability p_ic drawn
    lognormally around the reported median. Their unnamed-cause probability is
    a fixed fraction of their named total. Their TOTAL is the probability of at
    least one, computed as 1 - prod(1 - p) so it is a genuine union and can
    never exceed the sum. Every individual is therefore coherent by
    construction, and any residual the medians show is an artifact.
    """
    res = []
    for _ in range(reps):
        cols = []
        for m, (lo, hi) in zip(medians, cis):
            mu = math.log(max(m, 1e-9) / 100.0)
            # spread from the reported bootstrap CI, widened: that CI is the
            # uncertainty of the MEDIAN, not the spread of PEOPLE, so using it
            # directly would understate person-to-person variation badly.
            s = sd_log if sd_log is not None else max(
                0.2, (math.log(max(hi, 1e-9)) - math.log(max(lo, 1e-9))) / 3.92 * 6)
            cols.append(np.exp(rng.normal(mu, s, n_people)))
        P = np.clip(np.array(cols), 0, 0.999)          # causes x people
        unnamed = P.sum(axis=0) * unnamed_frac
        allp = np.vstack([P, np.clip(unnamed, 0, 0.999)])
        total = 1.0 - np.prod(1.0 - allp, axis=0)
        med_named = [100 * np.median(P[j]) for j in range(P.shape[0])]
        med_total = 100 * np.median(total)
        res.append((sum(med_named), med_total))
    a = np.array(res)
    return a[:, 0], a[:, 1]


def main():
    d = load()
    obs = observed_residuals(d)

    print()
    print("=" * 94)
    print("2. HOW BIG IS THE MEDIAN ARTIFACT? Coherent people, known unnamed weight")
    print("   Extinction question, superforecaster medians, N = 88 people")
    print("=" * 94)
    meds = [d[("extinction_by_2100", c, "superforecasters")][0] for c in CAUSES]
    cis = [d[("extinction_by_2100", c, "superforecasters")][1:] for c in CAUSES]
    print(f"  {'true unnamed frac':>18} {'sim sum of named':>18} "
          f"{'sim median total':>18} {'sim ratio':>11}   observed ratio 2.13")
    rows = []
    for uf in (0.0, 0.25, 0.5, 1.0, 2.0):
        s, t = simulate(meds, cis, 88, uf, 400, RNG)
        ratio = t / np.maximum(s, 1e-9)
        print(f"  {uf:18.2f} {s.mean():17.3f}% {t.mean():17.3f}% "
              f"{ratio.mean():11.2f}")
        rows.append(dict(question="extinction", unnamed_frac=uf,
                         sim_sum=s.mean(), sim_total=t.mean(),
                         sim_ratio=ratio.mean()))
    print()
    print("  Read the row at true unnamed = 0.00. Whatever ratio appears there")
    print("  is manufactured by the median alone, in a population where every")
    print("  person's numbers add up exactly.")

    print()
    print("=" * 94)
    print("3. SENSITIVITY: the artifact depends on how spread out people are")
    print("   True unnamed weight fixed at ZERO throughout")
    print("=" * 94)
    print(f"  {'sd of log p (people)':>22} {'sim ratio total/sum':>21}")
    for sd in (0.3, 0.6, 1.0, 1.5, 2.0, 3.0):
        s, t = simulate(meds, cis, 88, 0.0, 300, RNG, sd_log=sd)
        r = (t / np.maximum(s, 1e-9)).mean()
        print(f"  {sd:22.1f} {r:21.2f}")
        rows.append(dict(question="extinction_sd_sweep", unnamed_frac=0.0,
                         sd_log=sd, sim_ratio=r))
    print()
    print("  The wider the disagreement between forecasters, the larger the")
    print("  ratio a median produces from nothing. XPT disagreement is very")
    print("  wide -- that is the paper's headline -- so this is not a small term.")

    with open("out_residual_observed.csv", "w", newline="",
              encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(obs[0].keys()))
        w.writeheader()
        w.writerows(obs)
    keys = sorted({k for r in rows for k in r})
    with open("out_residual_sim.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print("\nwrote out_residual_observed.csv, out_residual_sim.csv")


if __name__ == "__main__":
    main()
