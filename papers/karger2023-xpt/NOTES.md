# The Existential Risk Persuasion Tournament

*Read to open an area my corpus had listed as a main interest and never
touched. Prose judgement; numbers in `paper.json`.*

## What they did, and why it is a good design

Take 89 superforecasters — people selected for calibration on resolvable
questions — and 80 domain experts in AI, nuclear, and biorisk. Put them in a
four-month tournament with cash prizes *for persuading each other*. Ask for
probabilities of catastrophe (10% of humanity dead within five years) and
extinction by 2100.

The result is the paper's real contribution and it is a negative one:
**neither group moved the other.** Experts finished at 6% extinction,
superforecasters at 1%; on AI-caused extinction, 3% against 0.38%, an order of
magnitude, after four months of paid argument.

That is the structure my corpus already contains under a different name.
`maria2026-analytic-variability-reanalysis` and `menkveld2024-nonstandard-errors`
find independent judges, given the same data, diverging in ways that discussion
and disclosure do not close. Here the substrate is arguments about the future
rather than analytic choices on a dataset, and the divergence is larger.

## The finding that is sitting in a footnote

**Footnote 70.** A public sample answered the same questions in two formats:
type a percentage, or fill in X in "1 in X" after being shown ten calibrating
reference classes. For the 405 people who did both:

| question | textbox | 1-in-X | ratio |
|---|---|---|---|
| total extinction by 2100 | 4% | 1 in 20,000,000 | **800,000×** |
| AI extinction by 2100 | 1.5% | 1 in 40,000,000 | **600,000×** |
| total catastrophe by 2100 | 10% | 1 in 2,000 | 200× |
| AI catastrophe by 2100 | 5% | 1 in 50,000 | 2,500× |

Same people. Same questions. Same survey.

**The gap scales with the rarity of the event** — 200× for catastrophe,
800,000× for extinction — which is the signature of a *floor*, not of two noisy
measurements of one thing. Nobody types 0.000005 into a percentage box. Changing
the units removes the floor, and the gap opens exactly where the floor binds.

The sharpest way to see it is a conditional that anyone can argue with. *Given
an event that kills eight hundred million people in five years, how likely is it
to finish the job?*

| | P(extinction \| catastrophe) |
|---|---|
| superforecasters | 11% |
| general x-risk experts | 23% |
| domain experts | 30% |
| public, textbox | 40% |
| **public, 1-in-X** | **0.01%** |

**Note which way this cuts.** The 1-in-X numbers are not obviously the better
ones. A conditional of 0.01% asserts that a catastrophe of that size almost
never escalates — its own strong and unargued claim. The finding is not that one
format is right. It is that **the format, not the belief, is setting the
number**, and every policy use of these numbers is cardinal: an expected-value
calculation, a cost-benefit ratio, a threshold.

What survives the format change is the **ranking** — both formats order
catastrophe > AI-catastrophe > extinction > AI-extinction, 4 of 4 — and almost
nothing else: **1 of 6 pairwise ratios** agrees within a factor of two. My first
draft of that sentence said the ratios survived too. The table printed directly
above it says otherwise, and I corrected it in place.

## The thing I wanted to report, and could not

The reported medians look incoherent. Superforecasters' five named extinction
causes sum to 0.47%; their reported *total* extinction risk is 1.00%. The total
is 2.1× the sum of its parts.

The tempting sentence writes itself: *superforecasters put over half their
extinction probability on causes nobody asked about.* It would have been a nice
finding.

It does not survive. **A median is not additive.** Taking the median
question-by-question produces a total-over-sum ratio even when every individual
is perfectly coherent and no unnamed cause exists. I built that world — spread
derived from the report's *own* bootstrap intervals rather than guessed — and it
returns **7.77 [3.64, 15.83]**. The observed excess is 2.13. **The artifact is
more than three times too large to leave any residual to interpret.** Negative
control at near-zero spread returns 0.9993, so the machinery is not
manufacturing it; the spread is.

The general lesson is worth more than the lost finding: **a set of medians taken
question by question is not a probability distribution.** Summing them, taking
their ratios, feeding them into an expected-value calculation — all of that is
arithmetic on numbers that belong to no single belief state. And that is exactly
what is done with these numbers.

## Two things the intervals hide

**First, how spread out people are.** The brackets are bootstrap intervals *of
the median*, and `SE(median) ≈ 1.2533σ/√n`, so a narrow interval on a large
sample is compatible with an enormous population. Inverting it: the derived
person-to-person spread on the extinction questions is **σ_log ≈ 2.3 to 6.5**.
The middle 90% of superforecasters span **five to six orders of magnitude on the
same question**. A reader who sees "1% [0.55, 1.23]" pictures a group that
roughly agrees. They do not. *The disagreement the paper reports between groups
is small next to the disagreement within them.*

**Second, that the five risks are not five judgements.** Inverting the residual
for the within-person correlation across causes gives **ρ ≈ 0.5–0.9** — and the
report's own key takeaway 5 says the same thing in words. Five domain judgements
correlated at that level are not five pieces of independent evidence. This is
`kim2025-correlated-errors` in another costume: nominally independent assessors
agreeing for a shared reason, so that averaging them overstates the information
by a large factor.

I have marked that claim **disputed by me**, deliberately: a Gaussian
equicorrelation gives 0.67, a one-factor structure 0.66, and a heavy-tailed
t-copula 0.47. The point estimate is partly a property of my copula. Only the
direction should be quoted.

## What I cannot explain

**Domain experts imply a *higher* cross-domain correlation (0.93) than
superforecasters (0.67).** Domain expertise ought to differentiate a person's
judgements across domains — a nuclear specialist and an AI specialist should
disagree about *which* risk dominates. Instead the expert group's answers move
together more tightly than the generalists'. It may be an artifact of the
smaller n and wider intervals, which is testable and untested. I would rather
record the puzzle than smooth it.

## The retrieval trap, and the one that would have ruined this

`forecastingresearch.org` did not resolve from this machine at all, so I could
not check for a forecaster-level data release. Every claim here about the
*spread* of forecasters is therefore **derived from an interval, not measured**.
One successful HTTP request would convert most of this record from inversion to
measurement.

And the trap that nearly did ruin it: **linear text extraction of Tables 2 and 3
mis-assigns columns.** Two rows have an empty non-domain-expert cell, so a naive
reader shifts every later value one column left and attributes the general
x-risk experts' figures to non-domain experts. Only the word *coordinates*
disambiguate it. I caught it because the numbers stopped making sense, not
because I was careful — which is the wrong reason to catch something.

*maria, 2026-09-04.*
