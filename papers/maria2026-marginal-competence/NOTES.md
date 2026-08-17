# Notes — our own reanalysis

Author: maria. Session 2026-08-07. Structured record: `paper.json`.
Full write-up with tables: `../kim2025-correlated-errors/reanalysis/FINDINGS.md`.
Code: `../kim2025-correlated-errors/reanalysis/` — it lives with the paper it re-runs.

## What this is

Not a paper. An internal reanalysis given a record because it produces numbers nobody
else has, it is cited by two KB entries, and it should be findable and challengeable on
the same terms as anything else here.

## The one-sentence result

Competence concentrates error (r = +0.84 between accuracy and the tendency to pick the
popular wrong answer), so ~77% of the "correlated errors" effect is what conditional
independence predicts, and the ~23% residual is where real kinship — mostly
same-provider — shows up, *more* visibly than in the uncorrected statistic.

## Why I trust the fourth attempt more than the first three

1. Uniform baseline (theirs) — replicates, but assumes flat distractors.
2. Leave-pair-out nonparametric item null — **algebraically zero power**. I believed it
   for a while, because it agreed with me.
3. Anchored null from a disjoint model set — has power, but is antisymmetric in the
   direction of comparison, so it measures the capability gap rather than kinship.
4. Calibrated conditional-independence model — each model's pull toward the modal
   distractor is *identified* by its own leave-self-out measured rate, never fitted to
   the agreement data. Closed form, no simulation, no free parameters.

The progression matters more than the endpoint. Each null failed differently and each
failure said something about what the statistic can mean.

## Honest weaknesses

- **Multiple choice.** Everything depends on an enumerated option set with a designed
  near-miss. Our agents do open-ended work. I believe the mechanism generalises and
  generalises *more* strongly — an open task has a wider space to converge in — but
  belief is not measurement, and the KB entry says so.
- **n = 12 same-provider pairs.** Cohen's d = +0.789 on twelve pairs. Directionally
  clear, not precise. Extending to all 71 HELM models fixes it and needs nothing missing.
- **Two unexplained anomalies.** llama-3.1-8b sits far below the trend (q = 0.388 at
  accuracy 0.509) and olmo-7b has s < 0 — it picks the popular trap *less* often than
  random, so its errors are anti-correlated with the population. Both deviate in the
  same direction. I have no account of either and would rather say so than smooth it.
- **The modal distractor is defined from this model population.** Leave-self-out removes
  the worst circularity, not all of it. A genuinely external anchor would be human
  distractor-choice data on the same items, which I do not have. That is the real fix
  and it is the sort of thing psychometrics has had for fifty years.

## Sent to cidral for attack

The zero-power proposition (claim c1), with three questions I cannot settle: whether it
is a named U-statistic degeneracy, whether equal-weighting-over-pairs is doing hidden
work, and whether it survives item-weighted aggregation when w varies across items.
