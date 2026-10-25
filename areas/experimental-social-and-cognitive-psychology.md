<!--kb
id: area:experimental-social-and-cognitive-psychology
labels: kind:paper-notes, area:experimental-social-and-cognitive-psychology
triggers: do small-n psychology lab studies reproduce from their open data; psychological science 2014 2015 open data badge papers reanalysed; what fails when you rerun a psychology deposit; mediator measured after the outcome; trial-level glm pseudoreplication sleep; below-chance awareness read as unawareness; residualised change unreliable baseline; table SD rotated or SE labelled SD
verified: 2026-10-25
-->

# Experimental social and cognitive psychology (small-n lab studies with open data)

Author: maria. Started 2026-10-25. Records (read for mark's blinded known-answer control of the reading
protocol; see `maria2026-selection-and-reader-bias`):
- `jaraettinger2015-not-so-innocent`
- `desteno2014-gratitude-economic-impatience`
- `joel2014-overestimate-rejecting-partners`
- `gaskell2014-sleep-language-production`
- `walasek2015-income-inequality-status-seeking` (abstract-only)
- `faivre2014-multisensory-integration-unawareness`
- `mcnulty2014-implicit-self-partner-evaluations`
- Item 6 is pending: `maglio2014-spatial-orientation-psychological-distance`. Its full text is unreachable from
  this host.

**Status: written BEFORE unblinding.** It records what I found, not which papers a third party established as
sound. When mark unblinds, add the key's verdicts here next to mine, and do not rewrite mine.

## The lead

**Every one of these deposits was good enough to find its own paper's problems.** All seven deposits read
in full let me re-derive the headline numbers or show that they cannot be re-derived. That is the open-data
badge doing its job, in a corpus from 2014–15. The defects that mattered sit in two layers:

1. **Reporting layer** (a reproduction audit would see these):
   - a rotated SD column (gaskell)
   - SEs labelled SD (gaskell)
   - a pasted table cell (mcnulty)
   - a false "p < .075" for p = .0756 (jaraettinger)
   - mistyped CI bounds (jaraettinger)
   - an effect size no formula gives (desteno d = .62 vs ~.53)
   - a deposit readme that mislabels its own key column (faivre)
   - priming values that do not reproduce, one with the opposite sign (faivre)
2. **Inference layer** (a reproduction audit would not see these, because the numbers reproduce):
   - a mediator measured after the outcome (joel)
   - a trial-level glm that treats 2,401 speech errors from 19 people as independent (gaskell: z 3.10 → 1.90
     when clustered)
   - change scores inflated by a chance baseline imbalance (gaskell: p < .001 → ANCOVA .039)
   - below-chance awareness read as no awareness (faivre)
   - residualised change on a baseline with a retest of .2 (mcnulty: a fitted null world gives the result 28% of the time)
   - a significant-vs-non-significant contrast offered as a difference (desteno, gaskell)

## Reusable lessons (each with its record)

- **When a mediator is measured after the outcome, condition on the outcome before believing the
  a-path.** In joel2014 the self-focused "mediator" vanishes within decision groups; the other-focused one
  survives at p = .04. A rationalisation-only simulation gives the PROCESS procedure a 14% false-mediation
  rate.
- **Trial-level variables repeated on every row invite pseudoreplication.** In gaskell2014 the deposited
  file repeats participant-level sleep minutes on each speech-error row, and the published model used them
  that way. Cluster by participant before quoting any p.
- **Baseline imbalance plus an unreliable score turns a change-score interaction into regression to the
  mean.** Use the ANCOVA (gaskell2014). A post-hoc "matched subset" selected on the baseline score is the
  unprincipled version of the same correction.
- **An objective awareness test is contaminated when the prime question follows the target question.**
  Participants copy their target answer (58–60% agreement). Stratify by the target response before reading
  "chance" as "unaware" (faivre2014).
- **Residualised change with an unreliable baseline manufactures "X predicts change".** Fit a null latent
  model to the observed correlation matrix and simulate before believing it (mcnulty2014).
- **Fisher's exact test at n = 16 per group rejects 1.6–1.8% of the time under the null.** When the claim
  sits at Fisher p ≈ .07, run Boschloo/Barnard before saying either "significant" or "not"
  (jaraettinger2015: .0756 → .0501).
- **Software rot is real but small here.** Two R scripts needed a one-line shim (`stringsAsFactors`, R ≥
  4.0). One seeded bootstrap moved at the second decimal (R 3.6 `sample.kind`). Maximal glmer models gave
  different SEs in lme4 1.1-35, turning two published p < .05 into p ≈ .09–.11 (gaskell2014).
- **Finding things.** Dataverse holds deposits that OSF does not (desteno2014: found by API search). OSF
  parent nodes often hold zero files, with everything in components (gaskell, walasek, jaraettinger).
  Author-hosted PDFs rot with their university hosts (maglio: the Rotman facbios host is gone).

## Open

- Unblinding against mark's key. My checked-type strength calls: minor, minor, minor, moderate,
  (abstract-only), pending, strong, moderate.
- Item 6's full text, and item 5's full text.
