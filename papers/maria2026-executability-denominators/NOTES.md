# Does research code work? A denominator-harmonised synthesis of seven studies

maria, 2026-08-24. Own work, not a paper by anyone else. Record id
`maria2026-executability-denominators`. Code: `reanalysis/pool.py`. Data:
`artifacts/funnels.csv`, every row transcribed from a primary source read the same
day, never from another paper's summary of a third paper — which is the failure mode
this whole record is about.

---

## Why this exists

I read three large-scale artifact-execution studies in one session and found the same
structural problem in each: **the headline is a proportion whose denominator is chosen
partway down a multi-stage funnel, and the choice is not the same choice twice.** The
literature nevertheless quotes across studies as if the numbers were commensurable
("close to the 24.9% that Collberg achieved", "comparable to our 25%").

So: put every study on one scale, twice — once at the rate it printed, once at the
widest denominator it defines *itself* — and see what survives.

Seven studies, all read in primary form except one (flagged):

| study | field | unit | event measured |
|---|---|---|---|
| Trisovic et al. 2022 | social science, R on Dataverse | R file | script runs to completion |
| Samuel & Mietchen 2024 | biomedical, notebooks via PubMed Central | notebook | notebook runs; and output matches |
| Pimentel et al. 2019 | general GitHub | notebook | notebook runs; and output matches |
| Collberg & Proebsting 2015 | ACM systems | paper | code obtained and **builds** |
| Chang & Li 2015 | economics | paper | reported result recovered |
| Hardwicke et al. 2018 | psychology (*Cognition*) | article | data present / usable / result recovered |
| Stodden, Seiler & Ma 2018 | *Science* | paper | artifacts obtained / result reproduced |

Stodden is **abstract-only** — PNAS is paywalled, I did not get the full text, and its
counts are back-computed from two printed percentages. Flagged in the data file and
dropped in a sensitivity analysis.

---

## Finding 1 — the denominator multiplier

For each study: rate at its printed denominator ÷ rate at the widest denominator it
defines. Median over 15 study-events: **1.28**. For the three automated execution
studies, the ones with a real multi-stage pipeline:

| study | printed | widest denominator the study itself defines | multiplier |
|---|---|---|---|
| Trisovic 2022 | 39.8% (1472/3695) | 19.3% (1472/7621) | **×2.06** |
| Samuel & Mietchen 2024 | 7.61% (1203/15818) | 4.41% (1203/27271) | **×1.72** |
| Pimentel 2019 | 24.11% (208323/863878) | 17.97% (208323/1159166) | **×1.34** |

These are not errors. Every rung is defensible and in two of the three cases every rung
is printed somewhere in the paper. The multiplier is the size of the reader's inherited
choice.

## Finding 2 — harmonising halves the pooled execution rate, and does *not* remove the heterogeneity

Random-effects (DerSimonian–Laird and Paule–Mandel), logit scale, clustering-corrected,
stratified by event. Event = **"the artifact runs to completion"**, k = 3:

| convention | pooled | 95% CI | τ (logit) | I² |
|---|---|---|---|---|
| as printed | **20.6%** | [10.2, 37.1] | 0.73 | 99.8% |
| widest denominator | **11.9%** | [6.4, 21.0] | 0.60 | 99.6% |

So the number the field carries around is about **twice** the rate over the corpora
those same studies define. But heterogeneity stays at I² ≈ 99.6% after harmonisation:
at the widest denominator the three studies are 4.4%, 18.0% and 19.3%, a factor of 5.2
in odds. **The fields really do differ. The level is systematically overstated. Both
are true and the literature reports neither.**

## Finding 3 — harmonising *creates* an agreement that the printed numbers hide

Event = **"runs AND the output matches what the notebook recorded"**, k = 2:

| convention | Samuel & Mietchen | Pimentel | pooled | I² |
|---|---|---|---|---|
| as printed | 5.56% (879/15818) | 4.03% (34814/863878) | 4.7% | 96.6% |
| widest | 3.22% (879/27271) | 3.00% (34814/1159166) | **3.0%** | **0.0%** |

Two entirely independent corpora — biomedical notebooks found by mining PubMed Central
full texts, and general-purpose notebooks scraped off GitHub — **agree to 0.2 percentage
points once each is expressed over its own full corpus**, and appear to disagree by 38%
in relative terms as printed. This is the constructive half of the argument:
denominator harmonisation is not only a debunking tool.

**Do not over-read it.** k = 2, both are Jupyter notebooks, the two "widest"
populations are not identical in construction (deduplicated GitHub notebooks vs all
notebooks found in PMC-linked repos), and the pooled CI printed by the code ([3.0, 3.1])
is a fixed-effect interval on n in the millions and is not credible as an uncertainty
statement. The honest claim is *the two point estimates agree*, not *the pooled interval
is ±0.05 points*.

## Finding 4 — the most stable number in this literature is a human one

Event = **"the reported result was recovered, without author assistance"**, k = 3,
three different fields, three different decades of policy, three different research
teams:

| study | field | rate |
|---|---|---|
| Chang & Li 2015 | economics | 32.8% (22/67) |
| Hardwicke et al. 2018 | psychology, *Cognition* | 31.4% (11/35) |
| Stodden et al. 2018 | *Science*, multidisciplinary | 26.0% (53/204) |

Pooled **28.2% [23.4, 33.5], I² = 0.0%, τ² = 0**. Dropping the abstract-only study
moves it to 32.4% [24.0, 42.0].

And **with author assistance** (k = 2): pooled 54.9% [41.5, 67.7] — Chang & Li 49%,
Hardwicke 63%.

This is the most interesting result of the whole exercise and I did not expect it.
Everything automated diverges by a factor of five and carries I² ≈ 99.8%; the three
human attempts converge with zero measurable heterogeneity. The reason is not that
humans are more careful. It is that **the human studies all measure the same event on
the same unit**: a competent person, given whatever a paper supplies, tries to get the
paper's own headline number back out. That is a stable target. "A script exited 0 in
our container" is not — it is a property of the container, the time limit, the language,
and the funnel.

**The practical consequence**, and it is the one line I would want a repository or a
journal to take away: *if you want a reproducibility number that means something, define
it at the level of the paper's claim and let a competent person attempt it. Automated
execution rates measure your pipeline at least as much as they measure the corpus.*

## Finding 5 — the denominator moves the number more than the field does, for the human event

Within-study spread available from denominator choice alone (log odds, same numerator):
median 0.56, up to 1.04 (Samuel & Mietchen, a factor of 2.8 in odds).

Between-study spread at a fixed convention:

| event | as printed | widest |
|---|---|---|
| runs | 2.08 (×8.0 in odds) | 1.65 (×5.2) |
| builds | 0.90 (×2.5) | 0.72 (×2.0) |
| reported result recovered | **0.33 (×1.4)** | 0.33 (×1.4) |

For the human-attempt event, the entire between-field range (0.33) is *smaller than the
median within-study denominator range* (0.56). Stated plainly: **for that event, which
denominator an analyst picks moves the number more than which field is being studied.**

## Finding 6 — three documented cases of a proportion travelling without its denominator

Found while reading, not sought:

1. **Pimentel 2019 → Collberg & Proebsting.** "Our 24.11% is close to the reproducibility
   rate of 24.9% that Collberg et al. achieved". The Collberg TR reports 32.3% / 48.3% /
   54.0% of 402 code-backed papers; 24.9% is from the superseded 2014 version they cite.
   And the events are not the same event — a C/C++ project *building* against a notebook
   *running to completion*.
2. **Trisovic 2022 → Chang & Li 2015.** Trisovic: "33% without contacting the authors and
   43% with the authors' assistance". Chang & Li's own abstract says **29 of 59 = 49%**
   with assistance. 43% is 29/67 — a denominator the citing authors substituted silently.
   Both defensible; neither flagged.
3. **Samuel & Mietchen 2024, internally.** The abstract's narrative implies 11.6%
   (1203/10388); the Results print 7.61% (1203/15818); the corpus rate is 4.4%
   (1203/27271). All three are in one paper and all three are correct.

Three cases in one reading pass, in a literature whose subject is other people's
numerical carelessness. The mechanism is not carelessness. It is that **a proportion is
not a number; it is a pair, and only one half of the pair survives a citation.**

---

## Did I break it before believing it?

`pool.py` section 7 runs the machinery on three cases whose answers I set:

| synthetic case | truth | pooled | τ (logit) | I² |
|---|---|---|---|---|
| (a) all studies really are 12%, with the real spread of sample sizes | 12% | 11.9–12.0% | 0.01–0.02 | 19–39% |
| (b) true rates genuinely 4%→40% | — | 17.0–17.4% | 0.41–0.44 | 99.7% |
| (c) truth 12% everywhere, each study printing it over a denominator shrunk by a random factor in [1.0, 2.1] | 12% | **17.1–21.1%** | 0.12–0.24 | 94–99% |

Case (c) is the situation I claim the literature is in, and it reproduces the observed
pattern closely: a pooled estimate near 20% against a truth near 12%, with spurious
heterogeneity. That the real "as printed" pool is 20.6% and the real "widest" pool is
11.9% is exactly the signature.

Section 8 sweeps the intra-class correlation, which is measured on **one** corpus
(Samuel & Mietchen, ICC = 0.435 for "executes", from
`papers/samuel2024-jupyter-pmc/reanalysis/cluster_and_age.py`) and *assumed* for the
other two. Over ICC ∈ {0, 0.2, 0.435, 0.7, 1.0} the pooled point estimates move by less
than 0.1 percentage points; only the intervals move. **The headline contrast does not
depend on the borrowed ICC.** Good — because borrowing it was the weakest step.

## What this is not

- Not a systematic review. Seven studies I could obtain and read in one session, chosen
  because they measure a rate at scale and release enough to check. There is no search
  protocol, no inclusion criteria beyond that, and therefore **no claim that this is the
  literature**. Publication bias, language, and my own reading order are uncontrolled.
- Not new measurement. Every numerator here is somebody else's. What is mine is the
  harmonisation, the clustering correction, the stratification by event, and the
  arithmetic.
- Not a claim that any of these studies is wrong. Trisovic 2022 has a specific,
  demonstrable analytic problem (recorded separately). The other six do not; they simply
  each chose a rung.

## Where this sits against what I already had

- **`maria2026-analytic-variability-reanalysis` / `breznau2022-hidden-universe` /
  `menkveld2024-nonstandard-errors`.** My through-line there: analytic choices predict
  *precision*, not the *estimate*. This is the sharpest counterexample I have found. The
  reason, which I now think is the general rule and is in neither literature: **when the
  researcher degree of freedom is a modelling choice over a fixed set of cases it moves
  the standard error; when it is a choice about *what counts as a case*, it moves the
  estimate.** Denominator choice is the purest instance of the second kind.
- **`maria2026-rag-specification-dispersion`.** There I introduced the *benchmark
  saturation size* n\* — the evaluation-set size past which specification dispersion
  overtakes sampling error. Here the same idea has a cleaner form: Pimentel's n is
  1.16 million and its denominator range is a factor of 1.6 in odds, so it is
  astronomically past saturation. **A million notebooks buy nothing that one clear
  definition of the denominator would not have bought better.**
- **`jo2026-subjectivity`.** Their Theorem 1 — a rich enough null absorbs the whole
  discrepancy — is the same shape as: a permissive enough denominator absorbs the whole
  failure. The reference class is the free parameter in both.
- **My own KB stewardship rule** about tools that silently drop what they cannot handle.
  This session found it in three published studies. The version here is one level up: it
  is not that anyone dropped anything silently — Samuel & Mietchen print everything — it
  is that **a printed funnel protects the headline and does not protect what is computed
  downstream of it, nor what a citation carries away.**

## Open

- Add the studies I did not obtain: Konkol et al. 2019 (geoscience, n=39), Stodden's full
  text, Zhao et al. on web services, the 2026 Nature-repositories notebook study (n=19
  for reproducibility, too small to matter but worth recording), Obels et al. on
  registered reports.
- **Nobody has measured executability with the environment *preserved* rather than
  *declared*** — the rate for artifacts shipping a container image. Every study here
  measures declared environments. If that rate is not far above 12%, containerisation
  advice is unsupported; if it is, it is the only intervention with evidence.
- The human-attempt convergence at 28% (I² = 0, k = 3) deserves more studies. If it holds
  at k = 6, it is the single most useful number in metascience and nobody is quoting it,
  because everyone quotes the automated figures instead.
- Every "widest" denominator here is the widest *the study defines*. The true population
  is wider still — papers that deposit nothing at all. Trisovic's corpus is packages that
  contain R code; Samuel's is publications that mention a GitHub repo. Adding the
  no-artifact stratum would push all of these down again, and the studies that do measure
  it (Stodden: 44% supply anything; Chang & Li: 42% at non-mandating journals) suggest
  by roughly a further factor of two.
