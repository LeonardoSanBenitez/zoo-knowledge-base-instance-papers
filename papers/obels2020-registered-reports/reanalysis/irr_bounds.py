"""How much does "this artifact reproduced" mean, if two coders barely agree?

Obels, Lakens, Coles, Gottfried & Gottfried (AMPPS 2020) is, as far as I can
find, the ONLY study in the computational-reproducibility literature that
measured inter-rater reliability on its own outcome. It reports:

    "After the initial coding, inter-rater reliability was low (60% agreement on
     executability, and 55% agreement on reproducibility for SPSS scripts, 75%
     agreement on executability, and 56% agreement on reproducibility for R
     scripts)."

Every reproduction rate in this area -- Trisovic, Samuel & Mietchen, Hardwicke,
Laurinavichyute, and Obels' own 21/36 -- rests on a judgement of that kind. If
two trained coders looking at the same artifact agree barely more often than
chance, the outcome variable itself has a ceiling on how much it can mean.

WHAT THIS SCRIPT DOES, AND WHAT IT REFUSES TO DO.

The paper gives percentage agreement and not the 2x2 tables, so Cohen's kappa is
NOT identified. It depends on the coders' marginals, which are unreported. So:

  1. compute kappa under EQUAL marginals at the observed base rate (the usual
     tacit assumption, and the one that makes kappa smallest);
  2. compute the FULL RANGE of kappa consistent with the reported agreement over
     every marginal pair, by enumeration -- an honest interval rather than a
     point estimate presented as one;
  3. put a confidence interval on the agreement proportion itself, because the
     denominators turn out to be 20 and 16 and the reported percentages are
     two-digit precision on a denominator of twenty.

The third is the one that matters most and is the easiest to forget. It is very
easy to write "kappa = 0.09, essentially chance" and much harder to write "11 of
20, and the interval runs from 0.32 to 0.77".
"""
import itertools
import math

from scipy import stats


def feasible(po, m1, m2):
    """Can a 2x2 table with these marginals produce this observed agreement?

    Agreement is bounded below by |m1 + m2 - 1| and above by 1 - |m1 - m2|.
    Ignoring this printed an "equal-marginal kappa" of -0.93 for a case where
    equal marginals cannot produce the reported 60% agreement AT ALL -- a number
    computed from an impossible table, sitting outside the feasible range printed
    three lines below it. That is the same failure as every other one today: an
    expression evaluated without asking whether its inputs could occur.
    """
    return abs(m1 + m2 - 1) - 1e-9 <= po <= 1 - abs(m1 - m2) + 1e-9


def kappa(po, m1, m2):
    """Cohen's kappa given observed agreement and each coder's positive rate."""
    pe = m1 * m2 + (1 - m1) * (1 - m2)
    if pe >= 1:
        return float("nan")
    return (po - pe) / (1 - pe)


def clopper_pearson(k, n, alpha=0.05):
    lo = stats.beta.ppf(alpha / 2, k, n - k + 1) if k > 0 else 0.0
    hi = stats.beta.ppf(1 - alpha / 2, k + 1, n - k) if k < n else 1.0
    return lo, hi


# Denominators are RECOVERED, not the article counts stated elsewhere in the
# paper. Neither 55% nor 60% is attainable as k/17 and neither 75% nor 56% as
# k/13; 20 and 16 are the unique n<=25 admitting both percentages of each
# language group, and they equal 17+3 and 13+3 (the papers using each language,
# including the 3 that used both), summing to the 36 articles with data and code.
# See recover_denominators.py. The first version of this file used 17 and 13,
# which the record checksum rejected -- correctly, because those counts were
# fabricated by multiplying a rounded percentage by an n I had lying around.
CASES = [
    # label,                  agreement, k,  n,  base rate
    ("SPSS  executability",     12 / 20, 12, 20, 15 / 17),
    ("SPSS  reproducibility",   11 / 20, 11, 20, 0.583),
    ("R     executability",     12 / 16, 12, 16, 10 / 13),
    ("R     reproducibility",    9 / 16,  9, 16, 0.583),
]

print("OBELS et al. 2020 -- inter-rater reliability on the outcome, unpacked")
print("=" * 78)
print("Reported percentages are the INITIAL coding, before the scheme was refined")
print("and disagreements adjudicated. The published 21/36 is post-adjudication.")
print()
print("%-24s %8s %6s %10s %14s %s"
      % ("what", "agree%", "n", "k of n", "95% CI on agr.", "kappa (equal marginals)"))
print("-" * 100)
for label, po, k, n, base in CASES:
    lo, hi = clopper_pearson(k, n)
    if feasible(po, base, base):
        kap = "%+6.2f" % kappa(po, base, base)
    else:
        kap = " INFEAS"      # equal marginals cannot produce this agreement
    print("%-24s %7.0f%% %6d %10s %6.2f - %-6.2f %s"
          % (label, 100 * po, n, "%d/%d" % (k, n), lo, hi, kap))

print()
print("KAPPA IS NOT IDENTIFIED FROM PERCENTAGE AGREEMENT. Range over all marginal")
print("pairs (grid of 0.05) consistent with each reported agreement:")
print()
grid = [i / 20 for i in range(21)]
for label, po, k, n, base in CASES:
    ks = []
    for m1, m2 in itertools.product(grid, grid):
        # a 2x2 table with these marginals can only reach agreement po if po is
        # attainable: |m1 - m2| <= 1 - po  and  po <= 1 - |m1 - m2|
        if not feasible(po, m1, m2):
            continue
        v = kappa(po, m1, m2)
        if not math.isnan(v):
            ks.append(v)
    if ks:
        eq = ("%+.2f" % kappa(po, base, base)) if feasible(po, base, base) else "INFEASIBLE"
        print("  %-24s kappa in [%+.2f, %+.2f]   (equal marginals at the base rate: %s)"
              % (label, min(ks), max(ks), eq))

print()
print("READ IT THIS WAY. For the two EXECUTABILITY rows the equal-marginal table is")
print("INFEASIBLE -- with ~88% of scripts called executable by each coder, chance")
print("agreement alone would exceed the agreement actually observed. The coders'")
print("marginals therefore differed substantially, which is consistent with the")
print("paper saying their expertise did. For the two REPRODUCIBILITY rows the")
print("equal-marginal kappa is 0.07 and 0.10 and the feasible range straddles zero.")
print()
print("So this is NOT evidence that kappa was 0.1. It is evidence that:")
print()
print("  (a) percentage agreement on this outcome was 55-56% on a base rate near")
print("      58%, i.e. close to what two independent coders drawing at the base")
print("      rate would achieve by construction;")
print("  (b) the interval on that percentage, at n = 13 and 17, is enormous;")
print("  (c) NOBODY ELSE IN THIS LITERATURE MEASURED IT AT ALL.")
print()
print("(c) is the finding. A field that reports reproduction rates to three")
print("significant figures has exactly one measurement of whether two people")
print("looking at the same artifact call it the same thing, and it is 55%, on")
print("seventeen papers, and it was reported as an aside about coder training.")
