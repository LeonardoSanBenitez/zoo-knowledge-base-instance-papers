# Notes — arslan2026-bodhi-engineering

Author: maria, 2026-09-30. Open-access PDF read; Table 1 transcribed; supplement not fetched.

## design / what it identifies

- **Design:** 200 HealthBench Hard vignettes x 5 seeds x 2 models, single-pass baseline vs. BODHI
  two-pass prompt, temperature 0.7, rubric-graded.
- **Identifies:** the change in rubric scores and in behaviour rates when the BODHI prompt is added. The
  prompt includes content (virtue rules) *and* structure (think first, then answer). With no matched
  two-pass control, the design does not separate the two.

## The finding of this read

DOJO quotes BODHI as "validated ... with very large effect sizes (Cohen's d = 16.38-19.54)". A d of 16
means two distributions whose means are sixteen standard deviations apart. For a yes/no behaviour per
response that is impossible. The largest d a binary outcome can produce at these rates is about 4.

The printed Table 1 settles it. **All eight printed d values reproduce, to rounding, as the difference of
seed means divided by the pooled SD of the five seed means** (`reanalysis/d_from_printed_table1.py`). So
the standardiser is the between-seed spread of a 200-case average. That measures how reproducible the
mean is. It does not measure how large the change in behaviour is, and it grows with cases per seed while
the behaviour stays fixed. The known-answer control in `reanalysis/cohens_d_by_unit.py` (identical arms)
gives d near 0 under every unit, so the simulation is not what manufactures the spread.

Per response, the same rates give:

| metric | printed d | per-response d |
|---|---:|---:|
| context-seeking, 4.1-mini | 16.38 | 4.04 |
| context-seeking, 4o-mini | 19.54 | 2.36 |
| hedging ("humility"), 4.1-mini | 5.80 | **0.66** |
| hedging, 4o-mini | 1.16 | **0.29** |

The humility effect is moderate in one model and small in the other. The risk differences in the paper
(+89.6 pp, +20.3 pp) were always the honest numbers, and they are printed right next to the d values.

A second, quieter issue is construct. "Context-seeking rate" = at least one clarifying question. The
prompt tells the model to write "1-2 specific clarifying questions". Most of the 7.8% to 97.3% jump is
therefore a **manipulation check**: did the model follow the instruction? It is not an outcome that shows
curiosity. The outcome that could carry the virtue claim is whether asking questions changed the clinical
quality of the answer. That is the +16.6 pp overall score, which is real and modest.

A third issue, not identified: the printed seed SDs are larger than binomial sampling on fixed cases
allows (6.8 pp against a 1.9 pp ceiling). Something about the seed procedure is not what the main text
implies. The supplement would say what.

## Why it matters beyond this paper

A standardised effect size depends on the unit it was standardised over, and nobody states the unit.
That is general, and it now has a KB entry:
`instance-general/statistics/standardised-effect-size-depends-on-the-unit.md`.

As a psychoanalyst I will add one line. A framework built to make machines humble advertised its own
result without humility, through an effect size that measures reproducibility. That is not hypocrisy. It
is the ordinary way a good idea overstates itself when nobody inside the room checks its arithmetic. The
idea deserves the check.
