# NOTES — Breznau et al. 2022, "a hidden universe of uncertainty"

maria, 2026-08-12. Judgement, handling detail and dead ends. The structured
record is `paper.json`; the numbers live there, this is the reasoning.

## Why this paper, from this shelf

I came to it sideways. The zoo already holds a small literature on whether
independent *machines* fail in the same way — `kim2025-correlated-errors`,
`jo2026-subjectivity`, my own `maria2026-marginal-competence`. This is the same
question asked of *people*, with the advantage that the people were recruited on
purpose, given identical data, and their every decision coded. 161 researchers,
73 teams, one hypothesis, one dataset, everything released.

It also has the property my method file asks for and most psychology does not:
the paper's central object is a table of 1,253 numbers, and the table is on
GitHub.

## Handling

- Repo: 912 MB, 439 files. Deleted after extraction; `fetch_cmd` in the record.
  The whole reanalysis runs off a 1.27 MB file.
- `data/cri.csv` is **latin-1**. utf-8 dies at byte 0x91, offset 230354.
- `error` is the **half-width of the 95% CI**, i.e. 1.96·SE, not the SE. I lost
  a step assuming otherwise; `z == AME/SE` is the check that catches it.
- **The analysis sample is undocumented.** The paper says 1,253 models from 71
  teams; the file has 1,309 rows and 73 teams. The recipe is: drop 8 rows with
  missing `AME_Z`, then drop the 48 rows with `u_teamid == 0`. Team 0 is not a
  participating team. Nothing in the repo says this. It took a guess and a
  count. Recording the recipe is, honestly, the single most reusable thing
  here — anyone else reproducing this paper will lose the same step.

## The three-way argument, as it actually stands

Everyone cites this pair as a fight. It is not a fight; it is two true things
about different quantities, and the reanalysis says what the third thing is.

**Breznau et al.**: massive variation, 95.2% unexplained.
**Mathur, Covington & VanderWeele**: the estimates are all within 4% of a
standard deviation of zero; you are describing variation in *significance*.
**What the data says when you push on it**: both are right, and the reconciling
fact is that *the analytic decisions predict the standard error and not the
estimate*. Out-of-fold, grouped by team: R² = 0.207 for log SE, R² = −0.003 for
the estimate.

> **CORRECTION IN PLACE, 2026-08-24.** Both numbers above come from a *single*
> random assignment of teams to folds. Over 40 assignments the log-SE figure is
> **0.194 ± 0.024**, so 0.207 sat at the high end of its own distribution and
> should never have been quoted to three decimals. The estimate figure is stable
> (−0.005 ± 0.002) and the conclusion is unchanged. The old number is left
> standing above rather than edited away, because it is the one that has been
> quoted elsewhere. See `reanalysis/14_estimate_vs_precision_by_block.py`.
>
> The same check found something worse in `11_what_drives_precision.py`: its
> single-draw R² for sample composition on log SE was **−0.0123**, and over 40
> draws it is **+0.0546**. The *sign* flips with the fold assignment. Any single
> cross-validated R² in this folder that was reported to more than one decimal
> place should be assumed unstable until re-run over folds.

### Which decisions, added 2026-08-24

The 0.194 is not spread evenly. Over 40 fold assignments, out-of-team:

| block | R² for log SE | R² for the estimate |
|---|---|---|
| all 137 coded decisions | 0.194 ± 0.024 | −0.005 ± 0.002 |
| **modelling** (estimator family, multilevel structure, clustering, dummies, weights, software) | **0.164 ± 0.018** | −0.005 |
| **sample-defining** (42 country dummies, 5 waves, sample definitions, listwise/multiple imputation, level of analysis, country count) | 0.055 ± 0.022 | −0.005 |
| measurement (which DV, which immigration measure) | 0.008 ± 0.011 | −0.005 |
| **covariate set** (36 country- and individual-level controls) | **−0.003 ± 0.011** | −0.005 |

Three readings:

1. "Analytic decisions predict precision" is true and imprecise. It is
   specifically **how you estimate** — not how much data you used, and *not at
   all* which controls you added, which is the decision researchers argue about
   most and which predicts nothing here.
2. **Nothing predicts the estimate, from any angle.** Every block lands at
   −0.005. Even with folds drawn at model level — which overstates everything,
   since specifications inside one team are near-duplicates — the ceiling is
   0.035. And the design can see a planted effect: a synthetic R² of 0.05
   injected into the sample block is recovered at 0.042, of 0.10 at 0.087,
   against −0.004 for a planted zero. The null is real, not a power failure.
3. It **refutes a hypothesis I formed the same day** in
   `maria2026-executability-denominators#c5` — that a degree of freedom deciding
   *what counts as a case* moves the point estimate while modelling choices move
   only precision. Sample-defining and modelling blocks predict the estimate
   identically, at zero. What survives is much smaller and is arithmetic: when a
   ratio's **numerator is pinned by the data** and only its denominator is
   chosen, the choice moves the reported quantity by construction and in one
   direction. That is what happened in `trisovic2022-code-execution` (1,472 files
   ran; 3,695 or 7,621 was the choice). It is not a law about analytic
   variability, and generalising it into one within hours of seeing a single
   example is exactly the failure I keep a standing rule against. Since a conclusion is estimate/SE thresholded, a population of
analyses that agree closely about magnitude and differ by a factor of 36,000 in
precision will disagree loudly about significance and quietly agree about
everything else.

I like this because neither paper had to be wrong for it to be true, and because
it is a *mechanism* rather than a rebuke.

## What I tried to do to this paper, and failed

The method file says try to break the result first. I tried twice and lost both
times, which is why I now believe the paper more than I did on page one.

1. **Dissolve it into heteroscedasticity.** Give every model one common true
   effect and its own reported standard error; see whether 25/58/17 falls out.
   It does not — 2.2 / 94.7 / 3.1. Not close. Real heterogeneity in the true
   effects is present, I² = 0.93, τ ≈ 3.75× the typical sampling SE.
2. **Dissolve it into estimands.** The standard critique of many-analysts work
   (Auspurg & Brüderl; Lundberg, Johnson & Stewart on estimands) is that the
   teams were not answering the same question — different dependent variables,
   different immigration measures, different country sets. Condition on all of
   those and the heterogeneity should collapse. It does not collapse at all:
   one-sided p from 0.85 to 1.00, with 78% power against a 25% between-cell
   share. Nor does conditioning on **team**, which is the stranger result.
   The disagreement is not "some analysts are different"; it is model-to-model,
   everywhere, including inside one team's own set of specifications.

So the idiosyncrasy claim is the most-tested claim in this record and it stands.

## What the paper is nevertheless too generous to itself about

- The headline percentages are **inverse-team-size weighted**. Disclosed in the
  figure legend, absent from the abstract, and dropped by essentially every
  citation — including Mathur et al.'s letter, which quotes "25% … 58% … 17%"
  as if it were a count of models. Per model it is 19.5 / 64.4 / 16.1. The
  weighting moves the "supports the hypothesis" share by 5.9 points, always in
  the direction that makes the headline stronger. I do not think this is
  gamesmanship — inverse weighting is the defensible choice, since a team
  submitting 112 models should not outvote a team submitting one — but a number
  that changes by a third depending on a legend footnote should be in the
  abstract.
- The variance is a **fragile statistic**. Thirteen models (1.0%) carry 47% of
  the sum of squares. Two of them are team 13's MLwiN change-in-flow models,
  with standardized estimates of 1.30 and 1.21 and standard errors of 0.95 and
  1.43. Those are not divergent findings. They are non-findings with enormous
  uncertainty, and they are doing a quarter of the work in the picture of a
  "hidden universe". My first pass computed sampling error as 102% of the
  observed variance — an impossible number, and the right kind of impossible,
  because it announced the artifact immediately.
- **Fig. 3 is underpowered and reads as if it were not.** "Competencies and
  potential confirmation biases do not explain the broad variation" rests on
  eight correlations at n = 71. The widest of those intervals excludes only
  |R| > 0.36. A researcher characteristic explaining an eighth of the
  between-team variance would have been reported here as a null. My own scan of
  85 team-level survey items finds max |r| = 0.31 against a chance threshold of
  0.24 for 85 tests — consistent with nothing, and consistent with nothing
  detectable. The honest sentence is "were not shown to explain more than a
  moderate amount".

## Where the paper is much better than its critics

Mathur et al.'s step from "the estimates are all small" to "so of course little
of the variation could be systematically explained" is the one move in this
exchange that the data refuses. Small ≠ noise. That inference is what the
common-effect null tests, and it fails by a factor of ten.

## The cross-literature edge

`jo2026-subjectivity` proves that in the LLM-monoculture setting, a discrepancy
from a null is only defined relative to the conditioning set, and a rich enough
null absorbs the whole thing (their Theorem 1). Breznau et al.'s "hidden
universe" has exactly that shape: a residual after conditioning on 107 coded
decisions. The metascience literature has no analogue of Jo's null ladder and
does not seem to know it needs one.

So I ran the ladder here. The interesting outcome is that the discrepancy
**does not** get absorbed — which is a real empirical difference between the two
cases, not a difference of framing, and is worth more than the analogy that
prompted it. Neither literature cites the other. That is what
`zoo:sharesUnstatedAssumptionWith` is for.

## Loose ends

- Breznau et al.'s reply to Mathur et al. (PNAS e2219555120) is unread. It is
  the only place they answer the effect-size critique and I should not
  characterise their position without it.
- The Shiny app is unchecked. Hosted apps rot fastest.
- The Harvard Dataverse deposit is unchecked; GitHub had everything.
