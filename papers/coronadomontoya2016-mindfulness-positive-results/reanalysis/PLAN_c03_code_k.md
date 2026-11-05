# PLAN c03 — code k from the trials' own abstracts (written BEFORE reading any abstract, 2026-11-05)

Author: maria. Purpose: replace c01's sweep over k (mental-health outcomes per abstract) with a measured value, so
that the 'honest multiplicity' expected count becomes an estimate.

## Sample
The 75 trials whose first-author/year search in PubMed returned exactly one article in the expected journal
(c02_fetch_abstracts.py, status = matched), plus any of the 17 ambiguous / no-journal-match cases I can resolve by
title (one candidate clearly the MBT RCT). Dissertations and non-PubMed journals (32 no-hit) are NOT coded; this is
a convenience subsample and is reported as such.

## Codes per abstract (one coder: me; no second coder -- stated as a limitation)
- `k_bg`: number of DISTINCT mental-health outcome constructs for which the abstract reports a between-groups
  (or group x time) comparison, significant or not. Distinct = different named measure or construct (depression,
  anxiety, stress, rumination, mindfulness-as-outcome does NOT count, quality of life counts only if mental/psych).
  Subscales of one instrument count once unless reported as separate outcomes.
- `s_bg`: how many of those are reported significant in favour of MBT.
- `within_only`: 1 if the abstract reports no between-groups mental-health result (only pre-post).
- `unclear`: 1 if I cannot code k_bg with confidence (vague: "improved psychological outcomes").
- A trial-level note when the match looks wrong (not an MBT RCT, wrong year) -> excluded.

## What is computed (c03)
1. Distribution of k_bg (median, mean, share k_bg >= 3).
2. Expected positives under honest multiplicity using each trial's OWN k_bg (k_bg = 0 or unclear -> k = 1), at
   d in {.30, .44, .55}, rho in {.3, .5, .7}, compared with the observed positives IN THE SAME SUBSAMPLE.
3. Because the abstract already shows only what authors chose to show, abstract k_bg is a LOWER bound on the number
   of outcomes tested. The estimate is therefore conservative for my critique: true multiplicity is at least this.
4. Report s_bg / k_bg: if abstracts report almost only significant outcomes (s_bg = k_bg nearly always), the abstract
   itself is selected and k_bg understates k.

## Decision rule written now
If at k = own k_bg, d = .44, rho = .5 the expected count is within 15% of observed in the subsample, I will say the
excess in the paper is largely an accounting artifact at plausible d; if it is > 30% below observed, the excess
survives the correction. In between: say so.
