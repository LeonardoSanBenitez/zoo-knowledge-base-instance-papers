<!--kb
id: area:language-information-and-communication-efficiency
labels: kind:paper-notes, area:language-information-and-communication-efficiency
triggers: do all languages convey information at the same rate; speech rate versus information density; bits per second of human speech; uniform information density; efficient communication across languages; how much does the entropy estimator change an information rate; Menzerath and compensation in language; channel capacity of language; neuralese versus human language bandwidth
verified: 2026-10-16
-->

# Language, information and communication efficiency

Author: maria. Started 2026-10-16. Records: `coupe2019-information-rate`, `zaslavsky2018-color-naming-ib`, `imel2026-convexity-efficiency`.

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

- **"Near-optimal" needs a null ladder.** Colour-naming systems sit 0.19 bits from the IB bound;
  random CONVEX partitions of perceptual space sit at 0.29, random partitions at 1.9. Convexity
  closes ~85% of the distance, languages ~5 points more (`zaslavsky2018#c1`). Same shape as the
  speech-rate compression in `coupe2019`: a real residual under a headline that mostly describes
  the null. **Method rule for this area: report the efficiency of a structurally minimal system
  (convex, random-within-constraints) beside every "near-optimal".**
- **Convexity vs efficiency, in principle vs in practice.** `imel2026` proves the two properties
  come apart (existential, constructed priors) and shows efficiency, not convexity, separates real
  systems from hue rotations -- but rotations are convex by construction, so that test cannot
  measure what convexity buys. Their 971k convex systems come partly from adversarial search
  (and the text and Algorithm 1 disagree on the search's direction). Read beside the null ladder
  above: convexity is neither necessary nor sufficient in principle, and gets most of the way in
  practice for colour.

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
