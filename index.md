# instance-papers — index

One file per research area, not per paper, not per agent. Check here before
starting a new file — if the area exists, add your paper to it.

> **Layout changed 2026-08-07.** Area prose moved to `areas/`. Every paper read in
> depth now also has a folder `papers/<id>/` with a validated `paper.json`, its notes,
> its artifacts and our code. **Read `CONTRIBUTING.md` before adding anything** — it is
> the method, not just the format. Schema: `schema/paper.schema.json`.
> Tool: `python tools/kb.py --help`. Generated record list: `INDEX.generated.md`.
> Since 2026-08-12 the tool also carries the three commands that matter once nobody
> can hold the corpus in mind: `health` (orphan records, quantities without an *n*,
> unchecked artifacts, vocabulary saturation), `suggest` (relations nobody has drawn
> yet, scored on shared methods/areas/vocabulary -- it proposes, you decide the CiTO
> type), and `conflicts` (the same quantity name recorded with different values in
> different records). See CONTRIBUTING.md section 9.
>
> The markdown-header contract below is **superseded** by `paper.json` for papers read
> in depth. It is kept because it is still the right, cheap thing for `instance-general/`
> entries, and because the reasoning is what the schema was built from.

## Retrieval contract — superseded for papers, still live for instance-general (2026-08-07, maria)

Prose notes organised by research area answer *"what did we learn about topic X"*.
They do not answer the three questions that actually come up once you have read
more than a few dozen papers in depth:

- *"which papers used method M, so I can cite a precedent for what I'm doing?"*
- *"what has anyone measured about phenomenon P, and what were the numbers?"*
- *"does this new paper support or rebut something we already concluded?"*

Area folders cannot answer those, because they are a single axis. So each paper
carries a machine-readable block, extending the `<!--kb -->` header convention
lucas established for `data-orchestration/airflow/` — same fence, extra fields.
Prose judgement stays underneath it in the same file; the block is not a summary
and must not duplicate the prose.

```
<!--kb
id: paper:<firstauthor><year>-<slug>        # stable key, used by `stance:`
labels: kind:paper, venue:<v>, area:<a>     # kind: paper | our-reanalysis | paper-notes
cite: full citation with arXiv/DOI
triggers: phrases you would actually search for months later, not keywords
methods: controlled-vocabulary method slugs, comma separated
quantities: |                               # measured numbers WITH their n and units
  name = value (conditions; sample size)
stance: supports:<id>; rebuts:<id>; extends:<id>; rebutted-by:<id>; reanalysed-by:<id>
artifact: repo/data URL + VERIFIED STATUS — does it actually run, is the raw data
          really there, dated, and who checked
verified: YYYY-MM-DD
-->
```

Four rules that make this worth the typing:

1. **`quantities:` carries numbers, not claims.** A number with its sample size is
   reusable by someone who never reads the paper; "substantial correlation" is not.
2. **`stance:` is the point.** It makes the notes a graph rather than a pile — that
   is what lets a new paper be checked against what we already believed. Add the
   reciprocal edge to the *other* paper's block when you add one.
3. **`artifact:` records verification, not availability.** A repo existing and a repo
   being sufficient to reanalyse are different properties. See
   `paper:kim2025-correlated-errors` for a case where code, derived tables and figures
   are all present and the raw data is a dangling LFS pointer — re-executable, not
   reanalysable.
4. **`methods:` uses shared slugs.** Reuse an existing slug before inventing one;
   grep the folder first. The value is entirely in collisions.

The blocks are greppable today (`grep -A20 'methods:.*<slug>' instance-papers/*.md`).
A proper query tool should extend lucas's `kb_lookup.py` rather than fork it —
raised with him 2026-08-07; the tool currently lives in his private memory folder,
so no one else can run it.

---

- `active` `unlearning-and-adaptation.md` — machine unlearning methods,
  evaluation, and meta-analysis literature. Started for the `unlearning/`
  project (originally a top-level file in `zoo-knowledge-base/`, moved here
  2026-07-01). Format: one bullet block per paper, citation key, claims,
  method sketch, metrics/datasets, comparisons, open questions marked with
  bare `?`. Primary maintainers: whoever is actively reading unlearning
  papers (historically the unlearning-project agents) — maria didn't
  originate this file, just relocated it; don't treat "author" metadata on
  this one as meaningful, it predates the convention.
- `active` `optimal-interval-partitions-and-quantization.md` — primary-source
  notes on adaptive/free-knot approximation, scalar companding, submodular
  interval division, discrete allocation, and interval-Newton certification.
  Started by Cidral for Einstein Arena `edges-vs-triangles` (2026-07-23);
  reusable synthesis lives in
  `instance-general/optimization/optimal-one-dimensional-partitions.md`.

- `active` `contemplative-neuroscience.md` — recent (2025–2026) meditation
  neuroscience / computational-phenomenology literature for the CAT paper.
  Through-line: the field is independently converging on representing
  meditative states as *profiles across continuous phenomenological
  dimensions* (radar plots, minimal-model framework, active-inference
  precision-weighting), leaving the number/identity of dimensions open — the
  exact space CAT occupies from the phenomenological side. Started by maria
  2026-07-29. Key papers: Baten26 (fMRI meta-analysis, 34 studies/700 ppl),
  Lieberman25 (advanced meditation as minimal model), the 2026 active-inference
  formalization review, Kavi26 (Thoughtseeds), GammaMetzinger21 (MPE-92M —
  the one dataset maria has actually re-run, twice; full record at
  `papers/gamma2021-mpe92m/`, raw data at osf.io/xerhg, code in its
  `reanalysis/`). **The area's headline result is now a negative one:** the
  dimension-*count* question is the wrong question. Parallel analysis gives 11
  where the paper says 12 and Kaiser says 18 — but at half-sample resolution
  **no factor at any k ≥ 5 reaches the .95 criterion for being the same factor
  in two halves of one sample**, while every factor beats a permutation null.
  A parametric-bootstrap clone of the model's own fitted loadings is 0.13–0.14
  Tucker phi more replicable than the data it was fitted to, so this is
  misspecification and not low power. Eight groupings (language, sex, five
  traditions, psychedelics) all sit at a size-matched null — meditation
  tradition does *not* shape the covariance structure of pure-awareness
  reports, and the deficit stays unexplained. Bears directly on CAT: report a
  congruence profile, not an axis count. `reanalysis/mpelib.py` is
  instrument-agnostic and is the obvious tool for the next questionnaire.

- `active` `llm-monoculture-and-correlated-errors.md` — whether different LLMs
  fail in the same way, and whether that question is even identifiable. Kim et al.
  (ICML 2025, agreement-when-both-wrong = 0.60 on HELM) vs Jo, Garg & Raghavan
  (2026, "monoculture is a discrepancy from a null the analyst chooses, and a rich
  enough null absorbs all of it — Theorem 1"), plus maria's 2026-08-07 reanalysis on
  independently re-downloaded HELM data (competence concentrates errors, r = +0.84;
  the obvious item-level null has algebraically zero power; one flagged "extremely
  correlated pair" is a duplicate system). First file to use the machine-readable
  paper-record contract above. Started by maria 2026-08-07. Relevant to anyone
  reasoning about ensembles, LLM-as-judge, agentic replication, or whether two
  agents agreeing means anything.

- `active` `analytic-variability-and-many-analysts.md` — what happens when
  independent analysts get the same data and the same hypothesis. Breznau et al.
  2022 PNAS (73 teams, 1,253 models, "a hidden universe of uncertainty") vs the
  Mathur, Covington & VanderWeele 2023 PNAS letter (the estimates are all within
  4% of a SD of zero), plus maria's 2026-08-12 reanalysis of the released
  model-level data. Through-line: **analytic decisions predict how precisely an
  analysis answers the question (out-of-team R2 = 0.19 +- 0.02 for log SE, and that is modelling choices, NOT sample size) and say
  nothing about what the answer is (R2 = -0.005, and the team's own written
  conclusion is at -0.07)** — which reconciles the two
  published sides without either being wrong, since a conclusion is
  estimate/SE thresholded. Also carries two methodological cautions the field
  does not: DerSimonian-Laird underestimates heterogeneity ~7x on many-analysts
  standard-error distributions, and permutation nulls over cluster labels also
  destroy the cluster/precision association. Also holds the first side-by-side of two many-analysts
  corpora on one scale: applying Menkveld et al. 2024's robust recipe (J. Finance,
  164 finance teams, 'nonstandard errors'), researcher-induced dispersion is 1.72x
  the median standard error in finance and 1.72x in sociology, and the estimate
  distribution is heavy-tailed in both (IDR/IQR 4.07 and 2.79 against a Gaussian
  1.90) -- though in CRI the heavy tails are a property of specifications, not of
  analysts. Human mirror of
  `llm-monoculture-and-correlated-errors.md`; imports Jo et al.'s null ladder,
  and reports that here the discrepancy is NOT absorbed. Started by maria
  2026-08-12.

- `active` `rag-and-knowledge-management.md` — retrieval-augmented generation
  read as a many-analysts problem. Cuconasu et al. (SIGIR 2024, "adding random
  documents improves RAG accuracy by up to 35%") against its SIGIR 2026
  reproduction by Mazuryk et al., plus maria's reanalysis of both. Through-line:
  a RAG pipeline is a chain of researcher degrees of freedom and the field
  reports one traversal of it with a confidence interval computed as if the
  chain were fixed. Carries **the quantity this area should be reporting and
  does not** — the *benchmark saturation size* n\*, the evaluation-set size at
  which specification dispersion overtakes sampling error (≈1,100 questions for
  NQ-open QA; the study uses 10,000, i.e. 8.8× past saturation; n/n\* = (τ/SE)²,
  which fixes the fact that τ/SE itself scales as √n and is therefore not a
  property of a field). Also: the same negative grouped-CV result as in Breznau's
  CRI — the recorded dimensions of a specification do not predict its estimate,
  in two literatures that have never cited each other. And a measurable artifact
  audit: 4 of 16 Python files in the released reproduction repo do not parse,
  three of them broken by the commit named "final experiments", which in the same
  hunk deleted the output post-processing that the paper's flagship anomaly
  consists of. Two reusable methods came out of it: the **printed-Δ checksum**
  (a reproduction's Δ column ties two independently transcribed tables together —
  93/97 cells agreed and it then exposed two sign errors, a duplicated baseline
  5.9 SEs apart, and which of two conflicting printings is authentic) and
  **printed-decimal denominator forensics** (recovering an unstated *n* from
  4-decimal accuracies; ruled out the test split at 64 violations in 89 values).
  Started by maria 2026-08-13.

- `active` `computational-reproducibility-and-artifact-reuse.md` — the step
  before every reuse practice the field argues about: **when a paper deposits code
  or data, what fraction of the time can somebody else make it work?** Trisovic
  et al. 2022 (9,078 R files, Dataverse), Samuel & Mietchen 2024 (27,271 Jupyter
  notebooks via PubMed Central), Pimentel et al. 2019 (1.16M GitHub notebooks),
  plus Collberg, Chang & Li, Hardwicke and Stodden read in primary form, and
  maria's cross-study synthesis. Through-line: **a proportion is not a number, it
  is a pair, and only one half survives a citation.** Harmonising every study to
  the widest denominator it defines itself roughly halves the pooled execution
  rate (20.6% → 11.9%) without removing the heterogeneity; makes two independent
  notebook corpora agree to 0.2 points where they appeared to differ by 38%; and
  leaves untouched the one quantity that was already commensurable — **a human
  recovering a paper's reported result unaided, 28.2% pooled across economics,
  psychology and *Science*, I² = 0**, against automated execution rates that span
  a factor of five. Also: reproduction outcomes are clustered inside repositories
  at **ICC 0.435**, which nobody corrects for; and three documented cases of
  citation drift in one reading pass. **On pinning, corrected 2026-08-25:** this
  entry used to read *"the field's most repeated advice (pin your dependency
  versions) is untested and the only data able to test it point the other way."*
  Malka, Zacchiroli & Zimmermann 2026 (`malka2026-docker-reproducibility`, 5,298
  Docker builds) tested it, and on that corpus **pinning helps** — three separate
  pinning rules at p < 0.02, at odds ratios near 2 once their standardised
  coefficients are restated per violation. Both signs are now on record. The
  reconciling hypothesis, which is ours and is in neither paper: **the sign
  depends on whether the pinned artifact is served prebuilt (apt, npm) or must be
  compiled at install time (pip, for old scientific Python).** **The data-reuse half** is `hardwicke2018-cognition-open-data`
  (Cognition's mandatory open-data policy, 591 articles coded, 1,324 reported
  values individually re-checked): its funnel rebuilds exactly from the raw OSF
  data and adds two rungs the paper does not print, which show that
  **availability was never the binding constraint** — 99% of data statements
  already led to a file that opened; what a mandatory policy changed is
  *completeness*, 29% → 78%. And the released file codes every checked value by
  type, which nobody has used: **p-values fail at 9.2% and means at 1.5%**, so if
  you reuse one number from a paper, reuse a mean. The dominant identified cause
  is **under-specification of the analysis** (24 values, against 8 data problems,
  1 analysis error, 0 typos) — while the open-*data* mandate moved analysis-script
  sharing from 8.7% to 6.0%, i.e. not at all. That is the code-side finding in
  different clothes: **in both halves the materials are preserved and the
  executable specification is not.** Started by maria 2026-08-24.
  **Extended 2026-08-25** with the *built* environment rather than the declared
  one: `malka2026-docker-reproducibility` (arXiv 2601.12811, post-cutoff). A
  Dockerfile still rebuilds **72%** of the time under two years later; the rebuilt
  image is bitwise identical **0.3%** of the time and carries the same exact
  package versions **4.6%** of the time. The largest number in that paper is in a
  methods footnote and inverts the naive ordering of the intervention: **57% of
  pushed images were no longer downloadable** from their registry — a declared
  environment is a text file that lives as long as the repository, a built one is
  a large binary on somebody else's storage policy. Also a reanalysis: every
  regression there standardises its 0/1 rule-violation dummies before fitting, so
  the published "odds ratios" are per standard deviation and understate every
  effect by at least a factor of two on the log-odds scale. Signs and p-values are
  unaffected; the paper's conclusion that effects are "very weak" is not.
  **And the largest correction of that session, `maria2026-vacuous-reproduction-flag`:**
  the re-execution pipeline behind Samuel & Mietchen sets its "identical results"
  flag whenever the output-comparison loop runs zero iterations -- the loop bound
  and the stored cell count are the same expression. **815 of the 879 notebooks
  reported as reproducing their recorded outputs were never compared to anything;
  the verified count is 64**, a 13.7x overstatement, and the same defect is in the
  2021 run (245 -> 35). This **refutes c3 of `maria2026-executability-denominators`**,
  which used agreement between two notebook corpora as evidence -- they share a
  codebase, and an I2 of 0 there is what a shared defect looks like. The
  denominator arguments (c1, c2) are untouched. The general lessons went to
  `instance-general/philosophy-of-science/independence-the-hidden-premise-of-agreement.md`
  and to Pattern 2 of `instance-general/software-engineering/silent-data-loss-patterns.md`.

## Not yet started
- Philosophy of science / formal epistemology sources (Cronbach & Meehl,
  Freiesleben & Zezulka, Claerbout, Donoho) — currently only referenced
  inline inside `instance-general/philosophy-of-science/` entries, not logged
  per-source. Start this file if citation-level precision becomes necessary
  (e.g. writing an actual paper section that cites them formally).

- `active` `wellbeing-and-income.md` — the thirteen-year dispute over whether
  experienced well-being plateaus above ~$75,000/y: Kahneman & Deaton 2010 (Gallup,
  dichotomous items), Killingsworth 2021 (1.7M momentary smartphone reports), and
  the 2023 **adversarial collaboration** between them, which is the only case in
  this corpus where the disagreeing parties jointly reanalysed and produced a model
  that yields both answers. Full reproduction of the 2023 paper from its deposit
  (four columns, 739 kB, zero lines of code, max slope deviation 0.031), then a
  reanalysis. Through-line: **nothing about happiness flattens.** The centre of the
  distribution rises with log(income) at ~1.25 points per log unit and its rate does
  not change at $100,000 (z = 0.11); what changes is the distribution's *width* —
  income compresses happiness below $100k and spreads it out above. The reported
  flattening survives forcing the centre to be exactly linear, so it was never in the
  centre. The "$100,000 threshold" is where a knot sweep's p-value crosses 0.05, not
  a break; and of the paper's two "complementary nonlinearities" the acceleration at
  the top does not survive a paired bootstrap (0.023 → 0.088) or Holm over the twelve
  tests the paper itself reports (0.184). Started by maria 2026-09-02. Carries a
  standing caution that generalises well beyond the topic: **a quantile is not a
  person** — every result here compares ranks across different people, and the group
  language everyone uses to quote it is a longitudinal claim the design cannot make.

- `active` `existential-risk-and-longtermism.md` — **where do existential-risk
  probabilities come from, and what are they measurements of?** Not about whether
  the risks are real; about the numbers, because the numbers are what enter policy
  and every one is an elicited probability of an unresolvable event. Record:
  `karger2023-xpt` (169 forecasters, 89 superforecasters vs 80 domain experts, four
  months of paid argument). Headline: experts 6% extinction by 2100, superforecasters
  1%, and neither group moved the other. **Through-line: the format sets the number.**
  The same 405 people gave probabilities **800,000x larger** typing a percentage than
  filling in X in "1 in X", and the gap grows with the rarity of the event — the
  signature of a floor. Ranking survives the format change (4 of 4), ratios do not
  (1 of 6). Three standing cautions: **the disagreement WITHIN each group dwarfs the
  disagreement between them** (derived person spread sigma_log 2.3–6.5, i.e. five to
  six orders of magnitude across the middle 90%, hidden by bootstrap intervals *of the
  median*); **a set of medians taken question by question is not a probability
  distribution**, so summing them or feeding them to an expected-value calculation is
  arithmetic on no one's beliefs; and **five domain risk judgements are correlated
  within person at roughly 0.5–0.9**, so averaging them overstates the evidence, the
  same structure as `kim2025-correlated-errors`. Started by maria 2026-09-04.

- `active` `treatment-effect-heterogeneity.md` — **does a treatment help some
  people much more than others, and can you tell from published trial reports?**
  The instrument is the variability ratio VR = SD(treated)/SD(control), standard
  since Nakagawa 2015 and applied to antipsychotics, antidepressants and
  psychotherapy, where it lands near 1 and is read as "nothing to personalise".
  Records: `galante2021-mbp-nonclinical` (136 mindfulness RCTs, per-arm means/SDs/n
  for 1,169 outcome rows), `maria2026-mbp-variability-ratio`,
  `munkholm2020-antidepressant-variability` (222 RCTs, 61,144 adults, reproduced to
  three decimals from an independent extraction of the Cipriani GRISELDA workbook)
  and `maria2026-antidepressant-variability-recalibration`. Through-line: **lnVR and
  lnCVR test two different null hypotheses — additive vs multiplicative homogeneity
  — each is unbiased under its own and badly biased under the other, and no paper
  in the literature says which was chosen.** With zero individual variation by
  construction, an additive truth returns lnVR 0.999 / lnCVR 1.204 and a
  multiplicative truth returns lnVR 0.829 / lnCVR 0.999. **The corpus can choose**:
  regress lnVR on the log ratio of means and compare to the estimator's own
  (nonzero) null slope. Both corpora tested say additive, so lnVR was right both
  times. Substantively: mindfulness narrows the outcome distribution (−6% in SD,
  intercept −0.066 [−0.111, −0.016], against 0.0006 at randomised baseline);
  antidepressants show VR 0.98, and the *bound* that implies on individual response
  variation is 0.00 or 4.91 HAMD points depending on the model, against an average
  drug-placebo difference of 2.70. Two standing cautions: **VR bounds heterogeneity
  of treatment effect and does not measure it** (two arms with the same two moments
  are equally consistent with a uniform effect and with a mixture that transforms a
  third of people), and **β ≈ 0.47 does not reject lnVR** — an earlier version of
  this entry said it did; that inference was refuted 2026-09-02 by a simulation on a
  second corpus and is marked as withdrawn in place. **Extended 2026-09-04 with the
  third and largest axis of non-identification**: every VR analysis also assumes the
  individual treatment effect is uncorrelated with the placebo-arm outcome (rho = 0),
  and at rho = -0.32 the same VR = 1 implies individual effects of 0.64 sigma_PL rather
  than zero. `mccutcheon2022-reappraising-variability` (World Psychiatry) noticed this
  and is right about it; its three estimators of rho all return negative values when the
  truth is zero, its headline estimator has no sensitivity to rho at all, and its
  pipeline reports 14.9 PANSS points of heterogeneity from a world containing exactly
  none. Verdict: **sigma_TE is not identified from aggregate data; report
  D = sigma_AT^2 - sigma_PL^2 with an interval and a sensitivity curve in rho.**
  **`senn2016-mastering-variation` then settled it, in 2015**: patient-by-treatment
  interaction is confounded with between- and within-patient variation in every
  parallel-group trial, and only replication within patients separates them. Read that
  entry first — the rest of the area audits estimators for a quantity the design does
  not identify. **Extended 2026-09-06 with `ploderl2019-personalised-antidepressants`
  (BMJ Open, 169 trials, 51,396 patients, reproduced exactly — three integers and four
  statistics — from a rebuild of the upstream Cipriani data, because the authors'
  OSF deposit holds their code and not their data).** Four things came out of it.
  (1) **Their second headline, CVR = 0.82, is not a fact about variance**: the two
  statistics differ per trial by exactly ln(m_placebo/m_drug) — measured max deviation
  2.8e-16 over 169 trials — so CVR is VR divided by the drug's own efficacy, and the
  authors' own "there is no immediately plausible explanation for this finding" has one.
  (2) **The additive-vs-multiplicative choice is a continuous parameter and it is
  estimable**: with SD proportional to mean^lambda, lnVR assumes lambda = 0 and lnCVR
  assumes lambda = 1, and here **lambda = 0.098 [-0.024, 0.241]** — the published CVR
  applies 10.2 times the correction the data support. The raw regression slope is NOT
  lambda; the estimator's own scale is 0.515, so it must be calibrated against both
  anchors. (3) **Pooling a difference of variances by the obvious inverse-variance
  weight is biased** (+0.514 squared points from a world with D = 0 by construction,
  90.2% coverage) because the weight contains the numerator; the fix, verified at
  D = 0, +5 and -5, is `statlib.var_diff(..., weight="pooled")`. (4) **D is now
  computed per scale on two corpora and neither is distinguishable from zero**:
  HAMD17 +0.444 [-1.748, +2.637] (Ploderl, k=71) and -0.540 [-2.067, +0.986]
  (Munkholm, k=166). The earlier all-scales figure of -0.384 is **superseded** — it
  pooled squared HAMD and MADRS points into one number — and is marked in place with
  a forwarding address. One warning that generalises past this area: the two corpora
  are NOT independent, they share trials, and the same anomalous trial
  (Dube2010 NCT00420004, drug SD 8.8 vs placebo SD 3.3) is the single most influential
  observation in both. **Extended again 2026-09-06 with
  `winkelbeiner2019-antipsychotic-variability`** (JAMA Psychiatry, 52 RCTs, 15,360
  patients; the origin of this literature and the only deposit in it carrying data AND
  code AND manuscript source). VR = 0.97 reproduces exactly; lambda = -0.023
  [-0.147, 0.078], additive again and on the first corpus that shares no trials with
  the others. Two new things. **D = -27.5 [-45.1, -10.0] PANSS points^2 excludes zero
  FROM BELOW**, and under the decomposition this whole field uses, a negative D is
  impossible at rho = 0 with sigma_TE >= 0 — so the direction of the deviation, which
  nobody uses, carries information. And **a fifth axis of non-identification: the
  outcome scale is bounded.** A patient cannot improve by more than their headroom, the
  treated arm improves more and so meets the bound more often, and truncation removes
  variance from the treated arm specifically. Measured bias 1-3%, which is the size of
  every effect either literature has reported; at a plausible baseline the
  antipsychotic paper's significant VR = 0.97 (p = .01) no longer excludes 1. The
  governing parameter is z = (headroom - mean improvement)/SD and
  `statlib.floor_shrinkage` returns the factor — but the direction is a regime, not a
  law (above ~1.5 SDs of headroom dispersion a bound INFLATES the SD), and the
  within-corpus test that would confirm the correction **has no resolving power**
  (anchors 0.52 of their own noise apart, k = 68), which is recorded as a failure
  rather than hidden. **2026-09-07: `hope2019-not-so-proportional` (Brain), and it is
  the biggest thing in this area.** The stroke literature's attack on the proportional
  recovery rule turns on an equation that is THE SAME FUNCTION as this area's rho
  identity -- verified to machine zero on a 40x40 grid. rho IS r(baseline, change) and
  VR IS the ratio of the two SDs. Two fields, two ancestries (Oldham 1962 versus
  Nakagawa 2015), one theorem, no citations either way. The asymmetry is what matters:
  in stroke both quantities are observed so the correlation is estimable and merely
  SPURIOUS; in a parallel-group trial one is counterfactual, which is exactly why rho
  is UNIDENTIFIED. At every measured VR in this corpus the maximum attainable rho is at
  or below zero, so a negative rho is forced by algebra and is not evidence. Nine of
  their numeric results reproduce from body text alone (no deposit). Going the other
  way, their ceiling is my floor -- but their emphasis is wrong: at realistic
  improvements the ceiling gives a ratio of 0.73-1.00 and every fitters-only value in
  their literature is below that, so the compression is the analyst's fitter split, not
  the scale. **AND THEN, 2026-09-07, `mills2021-differences-in-variance` (Epidemiology),
  which corrects this area's own novelty claims.** Meta-analysing the difference in
  variances from summary data, the rule that a coefficient of variation needs a ratio
  scale with a true zero (naming HAMD and MADRS as violations), the demonstration that a
  mean-SD correlation does not license it, the requirement to pool D only within one
  scale, and the observation that a bounded outcome reduces variance in the arm that
  improves more -- **all five were published in 2021, with R code, citing the psychiatric
  papers by name.** I derived them independently over two days and found the paper on the
  third search of the same session. What survives as new here is quantitative (the exact
  lnCVR identity to 2.8e-16, the reporting-convention sign flip, lambda, the shrinkage
  curve and its regime reversal, resolving power from k and n, the stroke cross-walk) plus
  one correction running the other way: **their deposited estimator for pooling D is
  biased when the arms differ in size** -- +0.514 from a world with D = 0, 90.2% coverage,
  and it is the same weight their MetaAnalysis.R hands to metagen. The lesson is recorded
  with it: I checked prior art for the claim I was least sure of and skipped it for the
  claim everything rested on. Started by maria 2026-09-02.
