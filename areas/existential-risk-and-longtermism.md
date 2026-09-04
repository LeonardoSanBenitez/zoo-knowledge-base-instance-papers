<!--kb
id: area:existential-risk-and-longtermism
labels: kind:paper-notes, area:existential-risk-and-longtermism
triggers: how likely is human extinction by 2100; where do existential risk probabilities come from; do experts and superforecasters disagree about AI risk; does discussion make forecasters converge; how should I aggregate expert probability judgements; is a median of expert probabilities a coherent belief; elicitation format changes a probability estimate; probability estimates that differ by orders of magnitude; are expert risk judgements across domains independent; what does a bootstrap interval on a median say about people; should I do expected value arithmetic on elicited probabilities
verified: 2026-09-04
-->

# Existential risk and longtermism, as a measurement problem

Author: maria. Started 2026-09-04. Records: `karger2023-xpt`.
Adjacent by method: `kim2025-correlated-errors` and
`bommasani2022-homogenization` (correlated judgements from nominally
independent assessors), `maria2026-analytic-variability-reanalysis` and
`menkveld2024-nonstandard-errors` (independent judges, shared information,
stable divergence), `jo2026-subjectivity` (a construct that does not exist
apart from the instrument).

**Scope note.** This area is not about whether the risks are real. It is about
the numbers, because the numbers are what enter policy, and every one of them is
an *elicited probability of an unresolvable event*. That is a measurement
object with known pathologies, and this literature reports it as if it were a
measurement of the world.

## The lead

**The format sets the number.** The same 405 people, in the same survey, on the
same questions, gave probabilities up to **800,000 times larger** when asked to
type a percentage than when asked to fill in X in "1 in X":

| question | textbox | 1-in-X | ratio |
|---|---|---|---|
| total extinction by 2100 | 4% | 1 in 20,000,000 | **800,000×** |
| AI extinction by 2100 | 1.5% | 1 in 40,000,000 | **600,000×** |
| total catastrophe by 2100 | 10% | 1 in 2,000 | 200× |
| AI catastrophe by 2100 | 5% | 1 in 50,000 | 2,500× |

The gap **grows with the rarity of the event**, which is the signature of a
floor rather than of two noisy measurements of one thing: nobody types 0.000005
into a percentage box, and changing the units removes the floor.

**Which format is right is not the finding, and assuming the small numbers are
the sober ones is a mistake.** The 1-in-X answers imply that a catastrophe
killing eight hundred million people escalates to extinction with probability
0.0001 — its own strong and unargued claim. What survives the format change is
the **ranking** (4 of 4) and **1 of 6 pairwise ratios**. So these answers carry
ordinal information about which risk is bigger and essentially none about how
much bigger — while every policy use of them is cardinal.

## What is established here

- **The headline disagreement.** Domain experts: 20% catastrophe, 6% extinction
  by 2100. Superforecasters: 9.05% and 1%. On AI extinction, 3% against 0.38%.
  Four months of incentivised argument moved neither group materially.
- **The disagreement WITHIN each group dwarfs the disagreement between them.**
  The published brackets are bootstrap intervals *of the median*, and
  `SE(median) ≈ 1.2533σ/√n`, so a narrow interval on a large sample hides an
  enormous population. Inverted, the derived person spread on the extinction
  questions is **σ_log ≈ 2.3 to 6.5**: the middle 90% of forecasters span
  **five to six orders of magnitude** on the same question. A reader who sees
  "1% [0.55, 1.23]" pictures a group that roughly agrees. They do not.
- **A set of medians taken question by question is not a probability
  distribution.** The superforecasters' five named extinction causes sum to
  0.47% while their reported total is 1.00%. The tempting reading — that half
  their probability sits on causes nobody asked about — does not survive: at the
  spread derived from their own intervals, the median artifact alone produces a
  ratio of **7.77 [3.64, 15.83]** in a population where every individual is
  coherent and no unnamed cause exists, against an observed 2.13. Negative
  control at near-zero spread returns 0.9993.
  **Consequence: summing these medians, taking their ratios, or feeding them to
  an expected-value calculation is arithmetic on numbers that belong to no
  single belief state.**
- **The five risks are not five judgements.** Inverting the residual gives a
  within-person correlation across causes of **ρ ≈ 0.5–0.9**, and the report's
  own key takeaway says the same in words. Five domain assessments correlated at
  that level are not five pieces of independent evidence. Same structure as
  `kim2025-correlated-errors`: nominally independent assessors agreeing for a
  shared reason, so averaging overstates the information.
  *Held as disputed:* Gaussian equicorrelation gives 0.67, one-factor 0.66, a
  heavy-tailed t-copula 0.47. Quote the direction, not the number.

## Method notes worth reusing elsewhere

**A bootstrap interval on a median is not the spread of people, and inverting it
is one line.** `σ ≈ (ln hi − ln lo)/3.92 · √n / 1.2533`. Every input is normally
printed. Do this before believing that a field agrees about anything — the
narrowness of published intervals is very often a statement about n.

**Before interpreting a residual, simulate the aggregation.** Any statistic
computed question-by-question and then compared across questions inherits the
non-additivity of the aggregator. The check is cheap: build a population where
the residual is zero *by construction* and see what the aggregator returns.

**An elicitation-format contrast is a free measurement-validity experiment, and
almost nobody reports it.** Where a paper happens to run one, the ratio between
formats bounds how much of the reported number is the instrument. Here it was in
a footnote.

**Reading tables from a PDF: use word coordinates, not linear text.** Linear
extraction of the XPT's Tables 2 and 3 mis-assigns columns wherever a cell is
empty, silently shifting every later value one column left. The columns are only
recoverable from x-positions.

## What has been retired

- **"Experts think extinction risk is 6%."** A median of a group whose middle
  90% spans five orders of magnitude, elicited in a format that moves the answer
  by six. Both halves of that sentence need saying, every time.
- **"The total exceeds the sum of named causes, so forecasters weight unknown
  risks heavily."** Not supported. The median artifact exceeds the observed
  excess.

## Not yet read, and the obvious next steps

- **The XPT near-term accuracy follow-up (2024)**, which resolves the
  short-horizon questions. The only external check on which group was better
  calibrated, and it bears directly on how much the 6%-versus-1% gap deserves.
- **Whether forecaster-level data exists.** `forecastingresearch.org` did not
  resolve from this machine. One successful request would turn most of
  `karger2023-xpt`'s derived quantities into measured ones.
- **The anchor question.** The 1-in-X format showed ten reference classes with a
  smallest anchor of 1 in 10,000,000, and the elicited extinction probability
  (1 in 20,000,000) sits *below* it. Whether the anchors dragged the answers
  down is the obvious alternative to the floor explanation, and it is testable.
- **Discount-rate expert surveys** (Drupp et al. and successors) and the
  empirical population-ethics literature. Both report elicited numbers, and the
  format finding here applies to them directly.
