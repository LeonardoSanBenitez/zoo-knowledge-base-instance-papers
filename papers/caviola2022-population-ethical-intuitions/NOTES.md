# Caviola, Althaus, Mogensen & Goodwin (2022), *Population ethical intuitions* — notes

Author: maria, 2026-10-16. Read in full (PDF), all nine studies re-run from the OSF deposit
(`reanalysis/run_all.sh`). Record: `paper.json`. Numbers below come from `out/*.txt`.

## Why this paper

It is the empirical paper the longtermist literature cites when it says "ordinary people are not
person-affecting": people think creating happy people is good, and they are not averagist all the
way down. If that sentence is load-bearing for priority-setting, it is worth knowing exactly
what the data hold. They hold less than the sentence and, in one place, more.

## What reproduces

All of it, to the printed decimal: every N, every exclusion count, every mean, SD and t I checked
in nine studies, from R scripts ported line by line to Python. A clean deposit: version-pinned,
hashes match, nothing modified after publication. This is the reproducibility literature's best
case and it should be said plainly, because the interesting findings below are about
*interpretation*, which is where re-running someone's data has moved my reading in every deep read
so far (MPE-92M, HELM, KKM, now this). The numbers are fine. What they are numbers *of* is the
question.

## Four things the deposit says that the paper does not

**1. The headline asymmetry is a median of a two-cluster mixture (c1).** With equal intensities
stipulated (1c), 37% put the threshold at 50 or 51 — exact symmetry — and the modal answer is 51.
The rest spread out. "People weigh suffering 1.5×" is the median; few individuals gave it. In 1a
the individual trade ratios are heavy-tailed: median 3.0, arithmetic mean 9.2, and 5% say no
amount of happiness offsets torture-level suffering. Cite the shape, not the centre.

**2. "No interaction" lives on one scale only (c2).** On the percentage scale the 1b intensity
interaction is p = .09. On the log-ratio scale — the one the paper itself uses to state its result
— it is ~1.0 log-odds, p ≈ .005, stable to every clipping choice, and a known-answer simulation
shows the logit test is calibrated (5.2% false-positive rate). Reading: the intensity of happiness
barely matters against mild suffering and matters a great deal against extreme suffering. An
interaction without crossover is removable by a monotone transform, so neither scale is "the
truth"; the paper simply did not say which scale its null was on. This is the same lesson as
"a non-significant slope is not a flat slope" in the KKM record, in a new costume.

**3. The neutral-person preference is half made of careless answers, and only exists for an empty
world (c3).** In 2a, 11.5% rated adding a −100 life as an *improvement* or a +100 life as a
worsening. That group supplies 51% of the "weak general preference to add a neutral person". In
2b the preference is there for an empty world (4.25) and absent for a world of 10 billion (4.02,
p = .21). It is a preference for there being *someone*, not for *more* people. The Unjournal's
Evaluator 2 reportedly singled out this number; the data agree with the suspicion.

And the symmetry result is *stronger* than reported: at the level of individual types the
McMahan asymmetry (7.6%) is matched by its own mirror (6.4%). But about one in five are neutral
about creating a maximally happy person (12% fully neutral + 7.6% asymmetric). "People reject the
intuition of neutrality" is a majority statement, not a consensus.

**4. The growing asymmetry in scope sensitivity is not identified (c4) — the finding I most want
kept.** Study 3a's unhappy arm is reverse-coded before comparison. Any valence-neutral preference
for *smaller* populations — crowding, which participants mention in their comments despite the
instructions — then lowers the happy arm and *raises* the reversed unhappy arm. A symmetric world
with a size aversion that grows with scale and an asymmetric world with no size aversion give the
*identical six cell means*, and the authors' test rejects in both (98% / 99.7%).

The design contained the instrument to separate them: every participant also rated *neutral*
populations at the same three sizes. But those items were asked *after* the main task, and they
are contaminated — identical items, yet their size trend differs by arm (p = 2×10⁻⁶), and 35% of
the happy arm copied their happy answers to the neutral items verbatim. A post-treatment variable
cannot be a baseline. If one uses it anyway (the paper's own covariate logic, applied per size),
the growing asymmetry disappears (t 5.04 → 0.38) and the famous reversal at a billion vanishes
(welfare-attributable preference +0.53, t = 7.5). So the honest status is not "refuted" but
`not-identifiable`, with the weight of the contaminated evidence on the side of a size aversion.
The authors' script contains a commented-out per-participant neutral adjustment; they were one
uncommented line from seeing this.

**General lesson, worth more than the paper:** *in a valence-mirrored design, reverse-coding one
arm converts any common directional bias into an apparent valence asymmetry.* The check is a
neutral arm that is randomised separately, never one asked after the valenced items. Filed as
methods `post-treatment-baseline-check` and `transformation-dependence-of-interaction`.

## What survives, and what it means for longtermism

- A **level** asymmetry: the effect of the number of unhappy people is about three times that of
  happy people, at every size, in raw and in differenced scores. This is robust to everything
  I tried.
- **Saturation for happy numbers** (3c): multiplying a happy population by 10,000 recovers about a
  quarter of what a 20-point fall in average costs, and beyond a million people each further
  factor of ten moves the answer by ~0.02 scale points. If lay axiology were the input to
  longtermist priority-setting, the astronomical-numbers argument would get almost no purchase on
  it. The numbers of *sufferers* behave differently, but that contrast carries the c4 confound.
- **Averagism is not innumeracy** (3b): it is as strong among the 5.6% who demonstrably computed
  that the totals were equal.

## How this stands to what I had read before

- `karger2023-xpt` — `zoo:sharesUnstatedAssumptionWith`. Both treat an elicited number as a
  measurement of a format-independent quantity. Karger's data show format moving extinction
  probabilities by 800,000×; this paper mentions unreported preliminary studies in which the
  trade ratio "heavily depends on the framing" and a button-press framing raised it. The
  longtermist argument stands on both kinds of number.
- `maria2026-happiness-income-spread` and `maria2026-mbp-variability-ratio` — the same habit, a
  centre reported as if it were a person. Third construct in which the shape carried the content.
- The Unjournal evaluated this paper in 2025. I could not read the reports (Cloudflare); by the EA
  Forum summary neither evaluator raised the reverse-coding problem. A reminder that review by two
  domain experts and a re-run of the data find different things, and both are needed.

## Errata-level slips found (none changes a conclusion)

- §11.1.2 says Study 2a used a world of "10 million"; the 2a materials and methods say 1 million.
- Study 3d gender test: t(571), means 3.41/3.22 are the *unexcluded* sample (N = 613), while the
  section states analyses use N = 482.
- 1b script line computing "% at 50/51" divides by all four cells (14.9%); the printed 19.6% is the
  mild-mild cell and is correct. I nearly reported this as an error before computing both.
