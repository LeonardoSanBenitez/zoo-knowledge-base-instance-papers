<!--kb
id: area:language-information-and-communication-efficiency
labels: kind:paper-notes, area:language-information-and-communication-efficiency
triggers: do all languages convey information at the same rate; speech rate versus information density; bits per second of human speech; uniform information density; efficient communication across languages; how much does the entropy estimator change an information rate; Menzerath and compensation in language; channel capacity of language; neuralese versus human language bandwidth
verified: 2026-10-16
-->

# Language, information and communication efficiency

Author: maria. Started 2026-10-16. Records: `coupe2019-information-rate`, `zaslavsky2018-color-naming-ib`, `imel2026-convexity-efficiency`, `denic2022-indefinites-simplicity-informativeness`, `steinertthrelkeld2021-quantifiers-degrees-universals`, `imel2026-modal-typology-efficiency`, `maria2026-structural-null-semantic-efficiency`, `chaabouni2021-emergent-colour-naming`, `xu2020-numeral-systems-efficiency`.

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
  is n.s. at the paper's unit weighting -- but that ordering flips with the axis weighting (natural
  closer when cost is weighted x3-10 more, farther when complexity is), so distance cannot rank
  them; per axis, natural systems are simpler and slightly LESS informative than the null. Real systems are special only in **complexity**
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
- **PRIOR ART for the whole through-line:** Moscoso del Prado Martin (2013), 'The missing
  baselines in arguments for the optimal efficiency of languages' (CogSci 35) -- random-system
  baselines for frequency-length efficiency arguments. Not yet read in full (download blocked
  2026-10-16). The structural-null work here is an extension to category-partition analyses,
  not a new idea. Chaabouni et al. 2019 (anti-efficient encoding) already use a monkey-typing
  baseline: good practice exists in this literature.
- **CORRECTED LATER THE SAME DAY (`maria2026-structural-null-semantic-efficiency`).** The
  "~9/10 in every domain" wording below compared gap shares from different geometries. Measured
  instead by net Pareto dominance (weighting-free, a probability): natural vs random of the same
  size is +0.92 / +0.96 / +0.62 (indefinites / modals / quantifiers); vs the structural null it
  is +0.15 [0.02, 0.28] / -0.25 [-0.42, -0.08] / +0.37 [0.34, 0.39]. So structure removes 84%,
  more than 100%, and 41% of the advantage. Colour in the same metric: +0.95 vs random, +0.17
  [0.12, 0.21] vs random convex partitions -- 83% removed -- with a small residual on BOTH axes
  (0.065 bits simpler, 0.024 bits more accurate). So 'the residual is always on a theorist-built
  complexity axis' (first draft) holds for quantifiers and mostly for indefinites, NOT for colour.
  Read the next bullet with this correction.
- **Colour's residual is prior-dependent (19:40).** Under a uniform source, instead of the LI prior
  estimated from the WCS naming data, mode maps no longer beat random convex partitions (net
  dominance -0.048 [-0.072, -0.025]; simpler but less accurate). So the one domain with a residual
  informativeness edge owes it to a prior built from the same languages. Working hypothesis for
  the area (tested only for colour): **every surviving edge over the structural null comes from a
  quantity estimated from the systems being judged** (need priors from usage, features or LoTs from
  the same typology).
- **Neuralese (`chaabouni2021-emergent-colour-naming`).** Emergent NN colour codes are called
  efficient because their distance to the IB bound falls within the human range. 93.5% of random
  convex partitions of CIELAB also fall within it (random partitions 0%). With a linear Listener
  over CIELAB, convexity is close to architectural. The part convexity does NOT explain is the
  low, narrow complexity band and its dependence on channel discreteness. That is the
  neuralese-relevant finding, and it is unverifiable: the models the paper says are deposited are
  not in the repository.
- **Numerals (`xu2020-numeral-systems-efficiency`).** Exact-restricted systems ('one, two, three,
  many') are the unique cost optimum among all 161,700 placements of three exact terms under the
  paper's own need (84% of need on 1-3). Counting from one is efficient by construction; the
  model cannot say why a language stops at 3 rather than 6. Need is estimated from English
  numeral frequencies, so the circle is visible (the result fails under uniform need, as the
  authors show). Sixth instance of the class-defining structure carrying the efficiency.
- **The through-line, three domains (colour, indefinites, quantifiers):** what is reported as
  the efficiency of natural systems is mostly the efficiency of any system obeying a simple
  structural constraint (convexity; no synonymy; monotone+conservative). Where a residual
  exists it is an alignment effect (with a prior, or with a feature theory built on the same
  languages). Units differ across the three, so this is a pattern, not a pooled estimate.
  **Before citing any "languages are near-optimal" result from this programme, ask what the
  structural null gets.**
- **Fourth domain, chosen to break it (modals, `imel2026-modal-typology-efficiency`).** A loose
  structural null (random IFF-only systems of the same size) IS beaten by attested systems,
  clearly. Matched also on coverage and overlap, the advantage disappears (real systems -0.02
  informativeness; random IFF systems dominate them 50% vs 25%). So the through-line survives,
  but only once the null is matched on descriptors, and **which descriptors to match is the
  unexamined choice**: low overlap is itself a route to informativeness, so matching on it
  decomposes efficiency rather than dissolving it. Stated precisely, then: attested systems show
  no efficiency advantage beyond a handful of structural descriptors.
- **Implementation defects are a live risk in this literature.** In `imel2026-modal-typology-efficiency` the
  published run used the need prior in REVERSED point order (1 of 720 assignments reproduces the
  outputs to 3e-16), and a complexity function that counts nodes, not atoms. Neither overturned a
  conclusion. Both were found only by re-deriving a single number from raw inputs. **Do that
  first, before any reanalysis.**

## Method notes for this area

- **Pseudo-replication by construction.** Language-level properties (ID, phoneme inventory, word
  order) are tested against speaker- or token-level rows constantly in this literature. Recompute
  at the level where the predictor varies before reading any P. In `coupe2019` the conclusion
  survived; that is not guaranteed.
- **Parallel texts allow an entropy-free check** (time per content), and it should be run first.

## Method notes added 2026-10-16 (indefinites)

- **Any 'closer to the frontier' comparison in a (cost, complexity) plane must be re-run across
  axis weightings.** The axes are incommensurable; in `denic2022` the natural-vs-null ordering
  reverses between weights 0.3 and 3. Report per-axis differences and Pareto dominance, which
  are weighting-free, before any distance.

- **Never trust a GA- or curve-estimated frontier in a small discrete space; enumerate.** Six
  flavours and 63 items allow exact enumeration of every language up to four items in about a
  minute.
- **Matching on means is not matching on structure.** Check the matched null's size distribution
  before reading any distance comparison.

## Open threads

1. Longer-context or LM-surprisal ID on the same texts: does the cross-language CV shrink or grow?
2. Spontaneous vs read speech.
3. A second, independent group's data before calling anything here a universal.
