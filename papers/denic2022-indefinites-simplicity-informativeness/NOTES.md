# Denić, Steinert-Threlkeld & Szymanik (2022), *Indefinite pronouns optimize the simplicity/informativeness trade-off* — notes

Author: maria, 2026-10-16. Read in full (lingbuzz PDF); authors' repo cloned and every number
I quote re-computed in Python (R is not on this host). Chosen to test, in a second domain, the
rule this area adopted the same morning from colour naming: *report a structurally minimal null
beside every "near-optimal".*

## What happened

The rule held, and in a sharper form than in colour.

1. **Exact reproduction.** Cost, pragmatic cost and complexity of all 519 Experiment-1 languages
   match the authors' CSV to 5e-15; my exact shortest-formula DP reproduces both 63-item complexity
   tables with zero mismatches; t(82.8) = −16.0 comes out as printed.
2. **The comparison set is degenerate.** Matching 10,000 random languages to the natural *mean*
   overlap (0.68) keeps 479 of them, and to have so little overlap they must be tiny: 1.82 items
   against 3.27, and 183 of the 479 have one item. Matching a mean is not matching a structure.
3. **Known-answer test.** Forty random languages with *no* synonymy pass the paper's Experiment-1
   test at p < .001 in 1000 of 1000 draws. The test detects "no overlap, near-full coverage".
4. **The frontier is not the frontier.** The GA's "dominant" file has 2,011 rows and 9 distinct
   points, 1,998 of them the single point (cost 4.78, complexity 1); the least-squares curve is
   pinned there. Enumeration gives the real frontier: cost 1.00 at complexity 11 (GA 1.21), 1.19
   at 8 (GA 1.49). The GA point at complexity 4 *is English*. No natural language lies on the exact
   frontier, in any of the four settings.
5. **Ladder** (setting 1, exact frontier, the paper's own Euclidean distance): random items with
   exact (size, coverage, overlap) match 1.88 → random overlap-free languages of natural size and
   coverage 0.83 → natural 0.72 → frontier 0. Natural vs overlap-free: p = .33, .21, .60, .46 in
   the four settings. Not distinguishable.
6. **Where the real signal is.** Relabelling the six flavours of every real language (720
   permutations; the analogue of hue rotation) keeps size, overlap, coverage. Real languages beat
   715/720 on distance, but **entirely on complexity** (8/720 better) and **not on informativeness**
   (160/720 better, the 22nd percentile; 270/720 under pragmatic cost). Family weighting changes
   nothing (9/720).
7. **Experiment 2 survives** a flavour-count-matched swap control. The complexity part is large
   (t = −44.7); the informativeness part is real but smaller (t = −13.8 literal, −5.9 pragmatic).

## What I think it means

The informativeness side of the trade-off does not distinguish real indefinite systems from
random synonym-free ones. What does distinguish them is that their items are short formulas in
Haspelmath's feature vocabulary. Haspelmath built that vocabulary for these same languages. So the
paper's strongest true result partly confirms that Haspelmath's features describe Haspelmath's
data. That is not nothing, but it is not a measured pressure toward simplicity. An independently
motivated feature theory would separate the two readings. That is the open question I most want
answered.

Experiment 2's informativeness half is the cleanest independent evidence in the paper: items that
respect the semantic map are more informative under an English-corpus prior, with the number of
flavours per item held fixed. Small, and real.

## Across papers

Colour (`zaslavsky2018`): a random convex partition closes 85% of the gap to the bound and real
systems 90%. Indefinites: a random synonym-free system closes 56% and real systems 62%. The
pattern repeats: a structural constraint delivers about nine-tenths of the headline. Two
differences: here real systems stay far from the optimum, and the residual sits in a complexity
measure that is not independent of the theory. Two domains is not a law. It is enough to make the
null ladder the default in this area.

Self-correction during the session: I first wrote "89%" for the indefinite gap share, which
used a different denominator from the colour figure. Corrected before commit to the same
definition (56% / 62%). The sampler for the overlap-free null first re-drew the language
shape on failure, which skewed sizes (0.96 instead of 0.83). Corrected to keep the shape fixed,
skipping Russian (7 items over 6 flavours, so no partition exists).
