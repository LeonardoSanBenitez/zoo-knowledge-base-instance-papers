# McNulty, Baker & Olson (2014), *Implicit Self-Evaluations Predict Changes in Implicit Partner Evaluations* — notes

Author: maria, 2026-10-25. Read in full: the **NIH author manuscript** (PMC4275414, NIHMS594629), fetched as
JATS XML from NCBI efetch. Europe PMC's fullTextXML answered HTTP 500, the trap already recorded in
archive-api-traps. Data: OSF hdi8p, one SPSS file with 104 spouses and both waves; measures on OSF qfgn6.
No analysis code is deposited. All analyses were rebuilt in Python with random-intercept models by couple.

## Why this paper

Item 8 of 8 in mark's blinded known-answer control. No prior knowledge and no search for third-party checks.

## What the paper claims

56 newlywed couples were measured at baseline and 3 years later, with explicit measures (self-esteem,
satisfaction, partner evaluation) and implicit priming measures (self, partner). Explicit self-esteem
predicts no change. **Baseline implicit self-evaluation predicts less decline in implicit partner
evaluation** (B = .26, r = .35), robust to ~20 covariates. The discussion calls it "long-awaited evidence that
self-evaluations positively predict relationship evaluations".

## What survived

- **Reproduces from the deposit.**
  - All Table 2 means except one cell (see below).
  - Both implicit changes (−16.74, −26.32) and the test-retest values (.19 vs .20; .06).
  - The key coefficient: raw B = .200 (SE .075, p = .007) is .26 standardised, and baseline partner .11.
  - The full-covariate model (standardised ≈ .30, p = .003).
- **It survives multiplicity across the six self → relationship tests**: Holm p = .043.

## What did not

1. **Table 2 has a pasted cell.** The implicit-partner follow-up is printed as 35.67 (62.83), which is
   the implicit-*self* follow-up. The true value is **32.50 (61.08)**. The printed change (−16.74) was always
   right, which is how a reader can see the cell is wrong (49.24 − 35.67 ≠ 16.74).
2. **Other numbers in the tables.**
   - The d column uses a between-groups formula (≈ 2t/√df) for within-person change, and the self-esteem row
     (d = 1.67 for a 0.09-point change, SD .45) fits nothing.
   - Several CIs are impossible or truncated: B .20, SE .12 → "(−.04, .34)"; "(−.14, .30"; "(.10, 50)".
   - Marital satisfaction at baseline recounts as 42.47 (3.24) on the 104 analysed, against 42.18 (4.20)
     printed. The paper presumably used a different n, which it does not say.
3. **The key result is fragile.**
   - Rank-based model: p = .17.
   - Removing one couple can raise it to p = .19 (leave-one-couple-out maximum).
   - Winsorised, p = .043.
4. **It is not distinguishable from a measurement artefact.** The design is residualised change (T2 partner ~
   T1 partner + T1 self). The baseline partner measure is unreliable (retest .19–.23), and the predictor
   comes from the same priming session. I fitted a **null model** to the observed correlation matrix:
   stable latent constructs, no effect of self on change, shared session method variance. The best fit
   needs self and partner positivity to be one latent construct. Simulating it at n = 104, the paper's model
   finds a positive significant "self predicts change" effect **28% of the time**, median standardised β .14,
   95th percentile .31. The observed β is .25. The one pattern that would favour a directional effect is
   cross-lagged asymmetry: r(s1, p2) = .30 vs r(p1, s2) = .12. Its couple-bootstrap CI is [−.17, .42], so it is
   not distinguishable from symmetry.
5. **The robustness model has ~24 predictors for ~50 couple clusters (t(24)).** That a coefficient stays
   significant there is weak reassurance.
6. **A covariate outlier**: one baseline implicit evaluation of strangers is 2,715.9 ms, on a measure whose other
   values fall within a few hundred. It enters the covariate model.

## For the known-answer control (my prediction, written before unblinding)

Checked-type:
- The key analysis reproduces (B .26, the covariate model).
- Table 2 has a pasted cell, an unreproducible d column, and malformed CIs.
- One baseline mean differs, probably from an unstated n.
Unchecked-type:
- The central longitudinal claim cannot be distinguished from a residualised-change artefact with an
  unreliable baseline; a null world produces it 28% of the time.
- It is fragile to one couple.
My call: **reproducible headline, but not evidence of what it claims; reporting errors in Tables 2 and 3.**
Strength of checked-type defects: moderate.
