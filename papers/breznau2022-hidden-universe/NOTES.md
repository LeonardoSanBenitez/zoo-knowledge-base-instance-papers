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
the estimate. Since a conclusion is estimate/SE thresholded, a population of
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
