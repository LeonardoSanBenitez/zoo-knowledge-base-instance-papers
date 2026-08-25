"""Can any two studies in this literature tell each other apart?

WHY. Reading Obels et al. I computed the widest-denominator figure the paper does
not print -- 21/62 = 33.9% -- and noticed it lands on Laurinavichyute et al.'s
20/59 = 33.9%. I wrote in the notes that this was "the third time the harmonised
number has come out near a third", with evident satisfaction.

Then I applied the entry I had written four hours earlier
(instance-general/philosophy-of-science/independence-the-hidden-premise-of-agreement.md)
to my own observation, which is what it is for.

TWO THINGS COME OUT, AND THE SECOND IS BIGGER THAN THE FIRST.

1. THE AGREEMENT IS TOO TIGHT TO MEAN ANYTHING. The two rates differ by 0.027
   percentage points. The standard error OF THE DIFFERENCE is 8.6 points. Two
   independent draws agreeing that closely is about a 1-in-400 event -- and I did
   not pre-specify the comparison, I noticed it because it matched. Across the
   twenty-odd rates in this area file there are two hundred pairs, so the
   probability that SOME pair agrees this tightly is around 0.38. It is not a
   coincidence worth explaining. It is what looking at twenty numbers does.

   This is a SECOND way agreement fails to be evidence, distinct from the shared-
   implementation failure that entry was written about: agreement tighter than
   the sampling error permits is noise that happened to cancel, and the tell is
   |difference| << SE(difference).

2. NO TWO MANUAL STUDIES IN THIS LITERATURE CAN RESOLVE THEIR OWN DISAGREEMENTS.
   At n = 36 to 62 -- which is every by-hand reproduction study in the area file
   -- the smallest difference detectable at 80% power is 24 to 31 percentage
   points. The range the field actually argues about is roughly 28% to 58%, i.e.
   30 points. **The instrument is barely able to see the whole debate, and cannot
   see any part of it.**

   This is the same finding I recorded for information retrieval -- several BEIR
   subsets cannot resolve differences under ~5 NDCG points -- arriving in a
   different field. It would be incoherent to demand resolving power of TREC-COVID
   and not of a literature I am synthesising.

Usage:  python resolving_power.py
"""
import math

from scipy import stats

STUDIES = [
    (20, 59, "Laurinavichyute 2022, strict, all 59 post-policy JML papers"),
    (21, 62, "Obels 2020, main results, all 62 registered reports (computed here)"),
]
AREA_NS = [36, 59, 62, 100, 669, 2060, 7621, 17965]


def main():
    print("THE TWO RATES")
    print("-" * 78)
    for k, n, lab in STUDIES:
        p = k / n
        lo = stats.beta.ppf(0.025, k, n - k + 1)
        hi = stats.beta.ppf(0.975, k + 1, n - k)
        print("  %-62s %2d/%2d = %.4f" % (lab, k, n, p))
        print("  %-62s SE %.4f   95%% [%.3f, %.3f]" % ("", math.sqrt(p * (1 - p) / n), lo, hi))
    (k1, n1, _), (k2, n2, _) = STUDIES
    p1, p2 = k1 / n1, k2 / n2
    d = p1 - p2
    se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    print()
    print("  difference          %+.5f  (%.3f percentage points)" % (d, 100 * abs(d)))
    print("  SE of the difference %.4f  (%.1f percentage points)" % (se, 100 * se))
    pr = 2 * stats.norm.cdf(abs(d) / se) - 1
    print("  P(|diff| <= observed) under independent sampling = %.4f, about 1 in %.0f"
          % (pr, 1 / pr))
    print()
    print("  BUT THE COMPARISON WAS NOT PRE-SPECIFIED. With m rates on the page there")
    print("  are m(m-1)/2 pairs, and the chance that SOME pair agrees this tightly is:")
    for m in (6, 10, 15, 20, 25):
        pairs = m * (m - 1) // 2
        print("     %2d rates -> %3d pairs -> %.2f" % (m, pairs, 1 - (1 - pr) ** pairs))
    print("  This area file holds well over twenty rates.")

    print()
    print("RESOLVING POWER: smallest difference detectable at 80% power, alpha .05")
    print("-" * 78)
    p = 0.34
    for n in AREA_NS:
        delta = (1.96 + 0.84) * math.sqrt(2 * p * (1 - p) / n)
        note = ""
        if n <= 62:
            note = "  <- every by-hand reproduction study in this area"
        elif n >= 7621:
            note = "  <- automated corpora"
        print("  n = %-6d  %5.1f points%s" % (n, 100 * delta, note))
    print()
    print("  The field argues about roughly 28% to 58%, a 30-point range. A study")
    print("  of 60 papers cannot detect a 24-point difference. So the manual studies")
    print("  are, individually and pairwise, unable to adjudicate anything they")
    print("  disagree about -- and their agreements are correspondingly uninformative.")
    print()
    print("  What this does NOT say: that the studies are worthless. Each one's own")
    print("  INTERNAL contrasts are far better powered -- Laurinavichyute's code vs")
    print("  no-code split is 1/19 against 19/32, which is enormous and survives any")
    print("  reasonable correction. Within-study comparisons are the sound part of")
    print("  this literature. BETWEEN-study comparisons of headline rates are not.")


if __name__ == "__main__":
    main()
