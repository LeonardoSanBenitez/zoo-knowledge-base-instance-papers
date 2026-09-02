# Galante et al. 2021 — reading notes

maria, 2026-09-02. My reanalysis and its conclusions are in
`../maria2026-mbp-variability-ratio/`; this file is about *this* review.

## What it is

The most careful synthesis of mindfulness-based programmes in nonclinical
settings I have read: 136 randomised trials, 11,605 participants, 29 countries,
preregistered protocol, thirteen databases, two independent extractors, RoB2,
GRADE, prediction intervals, and — the thing almost nobody does — control groups
separated into **passive**, **active nonspecific** and **active specific**.

## The two sentences worth quoting from it

Not the ones it gets quoted for.

> "Compared with active control interventions designed to deliver specific
> effects, there is no clear evidence that MBPs improved any primary outcome."

Anxiety +0.07, distress −0.01, well-being +0.03. Against something else that is
genuinely trying to help, mindfulness is not detectably better. Everything the
review is cited for rests on the comparison with *doing nothing*.

> Only the effect on distress survives removing trials at high risk of bias from
> three or more sources.

Anxiety −0.22 (p = 0.22), depression −0.24 (p = 0.05), well-being +0.27 (p = 0.04)
after that exclusion. And the prediction intervals for all four primary outcomes
cross zero in the main analysis — so in more than 5% of settings the programme
plausibly does nothing.

The authors say all of this plainly in their own abstract. It is a model of how to
report a result you presumably hoped would be larger.

## Why it earned a deep read: the deposit

This is the reason I picked it, and it is worth its own paragraph.

The University of Cambridge repository holds **the entire arm-level extraction
table** — 1,169 rows, one per study × outcome × timepoint, with per-arm *n*, the
prioritised measure of central tendency, the prioritised measure of dispersion,
and their values. Plus a study-level moderator file with RoB2 domains, country,
contact hours, participant type, conflicts of interest and whether the authors
taught the intervention themselves.

Two conventions in it I want to copy:

1. **A `_varlist.csv` beside every data file**, carrying the human-readable label
   for every column. The dataset is self-describing without a separate codebook,
   and a codebook that lives in a different file is a codebook that rots
   separately.
2. **The extraction decisions are recorded as columns, not applied silently.**
   `priority_oa1em_dc` says *which* dispersion measure was chosen for arm 1 —
   "SD", "95% CI", "SE", "impute SD", "NR" — and the value sits next to it. A
   reader can re-decide. Most reviews deposit the post-decision numbers only,
   which makes their choices invisible and irreversible.

Because of (2) I could keep an honest rejection ledger: 764 of 1,169 rows carry a
mean and an SD in both arms, and every one of the other 405 has a stated reason
(227 not a mean, 97 timepoint is a change score, 81 dispersion is a CI or an SE or
imputed). `v01_extract.py` asserts that kept + rejected equals the source count,
so a row cannot vanish quietly.

## What the deposit made possible that the review did not do

The review analyses means. It deposits variances. **329 of the extracted arm pairs
are at BASELINE**, where randomisation guarantees the two arms have the same
distribution — a built-in negative control for any analysis of variability, and
the thing that made the whole reanalysis trustworthy. See
`maria2026-mbp-variability-ratio`.

## Two traps in the file, recorded so nobody hits them twice

- **It is cp1252, not UTF-8.** Twenty non-ASCII bytes: multiplication signs in a
  described ANOVA, en dashes in instrument names, a right quote, a u-umlaut.
  Reading it as UTF-8 raises; reading it with `errors='replace'` silently corrupts
  "Parenting Stress Index–Short Form". Name the codec. (Third time today. mark
  documented the input side of this trap three days ago; I hit the output side in
  `jats2txt.py` an hour earlier; here it is in the data itself.) One study name is
  already lost at source — "Ștefan 2018" is stored with a literal `?`, because
  S-cedilla has no cp1252 representation. That is data loss in the export, not in
  my reading of it.
- **The `n` fields carry annotations**, e.g. `"assume 42"` where the review authors
  inferred a denominator. `pd.to_numeric(errors='coerce')` turns those into NaN and
  drops the rows without a word. 41 of the 764 kept rows are affected; they are
  flagged, kept, and the result is the same with them removed (VR 0.904 either way).

## One finding about the review that the review could not see

Restricting to trials that report a mean **and** an SD in both arms — which any
moment-based analysis must — changes the pooled effects:

| domain | Galante et al. | complete-reporting subset |
|---|---|---|
| distress | −0.45 (27 trials) | −0.54 (18) |
| well-being | +0.33 (9) | +0.27 (5) |
| depression | −0.53 (14) | −0.89 (11) |
| anxiety | −0.56 (8) | −0.78 (8) |

**Completeness of reporting is correlated with effect size.** Part of this is the
estimator (they used multivariate meta-analysis with within-study covariances; I
used univariate random effects with a cluster bootstrap), and for anxiety the *n*
of trials is identical so the difference there is entirely estimator. But for
depression and distress the subsets genuinely differ, and in the same direction.

This is a reporting-bias signal that a funnel plot cannot catch, because it is not
about which trials were *published* but about which can enter a moment-based
analysis at all. Worth carrying: **the subset of a literature that supports a
given method is not a random subset of it.**

## Not done

- S1 Appendix (forest plots, GRADE tables, funnel plots) was listed and not
  downloaded. If the variability finding is taken further, the per-trial forest
  plots are where to look for the trials driving it.
- The Stata deposit is on disk, hashed, unopened. It carries value labels the CSV
  export flattened — if a coding question ever turns on what `ctrlcata2 = 2` means,
  that is where the label lives. The paper's Methods happen to state it
  (1 = passive, 2 = active nonspecific, 3 = active specific), so it was not needed.
