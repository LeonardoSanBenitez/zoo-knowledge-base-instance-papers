<!--kb
id: area:language-information-and-communication-efficiency
labels: kind:paper-notes, area:language-information-and-communication-efficiency
triggers: do all languages convey information at the same rate; speech rate versus information density; bits per second of human speech; uniform information density; efficient communication across languages; how much does the entropy estimator change an information rate; Menzerath and compensation in language; channel capacity of language; neuralese versus human language bandwidth
verified: 2026-10-16
-->

# Language, information and communication efficiency

Author: maria. Started 2026-10-16. Records: `coupe2019-information-rate`, `zaslavsky2018-color-naming-ib`, `imel2026-convexity-efficiency`, `denic2022-indefinites-simplicity-informativeness`, `steinertthrelkeld2021-quantifiers-degrees-universals`.

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
- **Second domain, same shape (function words).** Indefinite pronouns (`denic2022`): the paper's
  test passes random *synonym-free* languages 1000/1000 times, so it detects "no overlap", not
  optimisation. Against the exact Pareto frontier (the paper's GA frontier is 9 distinct points),
  random overlap-free languages close 56% of the gap and real ones 62%. Natural vs structural null
  is n.s. in all four of the paper's settings. Real systems are special only in **complexity**
  (715/720 flavour relabelings beaten, 8/720 better on complexity, 160/720 better on cost), and the
  complexity measure is Haspelmath's own features, built on the same 40 languages. **Two domains
  now: a structural constraint delivers ~9/10 of the headline efficiency.**
- **Where to look for the real residual.** Colour: alignment with the prior and the stimulus
  space. Indefinites: alignment with the theory's feature vocabulary. Both residuals are
  alignment effects, and a hue-rotation-type relabelling is the tool that isolates them. In both
  cases ask whether the thing aligned with was estimated from the same data.
- **Third domain, and the one that claimed the opposite (quantifiers).** `steinertthrelkeld2021`
  reads "degrees of monotonicity/conservativity are not correlated with optimality" as evidence
  that universals are epiphenomenal. Reanalysed on the author's own deposit: the printed CIs
  exclude zero; the single correlation pools sizes 1-10 and hides a sign change (monotonicity
  r -0.21 at one quantifier, +0.57 at nine); the Exp-1-sample degree correlations (0.19/0.23)
  were computed and not reported; and languages built from non-natural quantifiers that HAVE
  both universals, complexity-matched, beat the quasi-natural ones (d 0.0435 vs 0.0486). The
  structural constraint carries the efficiency here too.
- **The through-line, three domains (colour, indefinites, quantifiers):** what is reported as
  the efficiency of natural systems is mostly the efficiency of any system obeying a simple
  structural constraint (convexity; no synonymy; monotone+conservative). Where a residual
  exists it is an alignment effect (with a prior, or with a feature theory built on the same
  languages). Units differ across the three, so this is a pattern, not a pooled estimate.
  **Before citing any "languages are near-optimal" result from this programme, ask what the
  structural null gets.**

## Method notes for this area

- **Pseudo-replication by construction.** Language-level properties (ID, phoneme inventory, word
  order) are tested against speaker- or token-level rows constantly in this literature. Recompute
  at the level where the predictor varies before reading any P. In `coupe2019` the conclusion
  survived; that is not guaranteed.
- **Parallel texts allow an entropy-free check** (time per content), and it should be run first.

## Method notes added 2026-10-16 (indefinites)

- **Never trust a GA- or curve-estimated frontier in a small discrete space; enumerate.** Six
  flavours and 63 items allow exact enumeration of every language up to four items in about a
  minute.
- **Matching on means is not matching on structure.** Check the matched null's size distribution
  before reading any distance comparison.

## Open threads

1. Longer-context or LM-surprisal ID on the same texts: does the cross-language CV shrink or grow?
2. Spontaneous vs read speech.
3. A second, independent group's data before calling anything here a universal.
