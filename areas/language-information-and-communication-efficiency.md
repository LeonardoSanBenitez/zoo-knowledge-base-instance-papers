<!--kb
id: area:language-information-and-communication-efficiency
labels: kind:paper-notes, area:language-information-and-communication-efficiency
triggers: do all languages convey information at the same rate; speech rate versus information density; bits per second of human speech; uniform information density; efficient communication across languages; how much does the entropy estimator change an information rate; Menzerath and compensation in language; channel capacity of language; neuralese versus human language bandwidth
verified: 2026-10-16
-->

# Language, information and communication efficiency

Author: maria. Started 2026-10-16. Records: `coupe2019-information-rate`.

**Scope.** Quantitative claims about how languages encode and transmit information -- rates,
densities, efficiency trade-offs -- read for what is measured versus what is named. Includes, as
a future direction, synthetic and machine-to-machine codes ("neuralese").

## The lead (one record; a hypothesis about the area)

- **Languages compensate for information density, partly.** Languages needing more syllables for
  the same content speak faster; the ID-free elasticity of duration on syllable count across 17
  languages is 0.35 (CI 0.10-0.60) -- about two-thirds compensation. `coupe2019#c3`.
- **Absolute bits-per-second figures belong to the estimator.** The same recordings give 39 or 57
  bits/s depending on one step of context in the entropy model. Cite relative comparisons, never
  the absolute number as a property of speech. `coupe2019#c2`.

## Method notes for this area

- **Pseudo-replication by construction.** Language-level properties (ID, phoneme inventory, word
  order) are tested against speaker- or token-level rows constantly in this literature. Recompute
  at the level where the predictor varies before reading any P. In `coupe2019` the conclusion
  survived; that is not guaranteed.
- **Parallel texts allow an entropy-free check** (time per content), and it should be run first.

## Open threads

1. Longer-context or LM-surprisal ID on the same texts: does the cross-language CV shrink or grow?
2. Spontaneous vs read speech.
3. A second, independent group's data before calling anything here a universal.
