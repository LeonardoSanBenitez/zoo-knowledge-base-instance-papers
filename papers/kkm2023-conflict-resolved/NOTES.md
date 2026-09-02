# Killingsworth, Kahneman & Mellers 2023 — reading notes

maria, 2026-09-02. Reanalysis and my own conclusions live in
`../maria2026-happiness-income-spread/`; this file is about *this* paper.

## What it is

Two published papers said opposite things. Kahneman & Deaton (2010): emotional
well-being rises with log income and stops at about $75,000. Killingsworth (2021):
it rises linearly with log income and does not stop. Killingsworth and Kahneman
then ran an **adversarial collaboration** — a joint reanalysis with a third party,
Barbara Mellers, as facilitator — over Killingsworth's experience-sampling data, and
published the result in two pages.

The answer: both patterns are in the same data. Flattening above ~$100,000 appears
in the bottom 15–20% of the happiness distribution; acceleration appears in the top
30%; the two offset to give the linear-log relation Killingsworth reported in the
mean.

## Why it earned a deep read

Not for the substance — the entire effect is a few points on a 100-point scale, and
the authors say so themselves, which is rare enough to be worth noting on its own.
It earned it for three structural reasons.

1. **It is the only reconciliation in this corpus.** `breznau2022-hidden-universe`
   and `menkveld2024-nonstandard-errors` measure how far analysts spread and stop.
   `mathur2023-effect-sizes` argues the spread was overstated. None of them is a case
   of the disagreeing parties jointly building a model that produces both answers.
   This is, and it took two pages and one figure.
2. **The deposit is a limiting case.** Four columns, 739 kB, zero lines of code, and
   every number in the paper falls out of it (max slope deviation 0.031). Set against
   `trisovic2022-code-execution` and `samuel2024-jupyter-pmc`, that is a useful
   counterexample: sufficiency is about whether the deposited columns span the
   analysis, not about size or the presence of code.
3. **Its methodological lesson is about naming, not about statistics.** The claim is
   that Kahneman & Deaton's dichotomous items have a ceiling, so they measure
   unhappiness rather than happiness, and that the *label* determines the scope
   readers give the result. That is a claim about how a variable name carries a
   quantifier the number does not — which is a knowledge-representation problem, and
   it applies directly to how this knowledge base names its own quantities.

## What I checked and what it cost

`../kkm2023-conflict-resolved/reanalysis/r01`–`r11`. The full text is JATS from
Europe PMC, rendered with the `tools/jats2txt.py` written this session; the
publisher PDF is not retrievable from this machine and neither is Kahneman & Deaton
2010 (see that record — six routes, three OA indexes asserting availability, no PDF).

Reproduction is exact. The three readings of "piecewise quantile regression" the
Methods leave open turn out not to matter: two of them (separate subsample fits, and
a saturated interaction model) are numerically identical and match the printed
values; the third (a continuous spline at the knot) does not, and can be ruled out.

## What I think is right in it

- The flattening exists and is confined to the bottom of the distribution. The
  boundary between τ ≤ 0.20 and τ ≥ 0.25 is sharp under the correct test (bootstrap
  interaction p = 0.001–0.004 below, 0.30–0.86 above).
- The ceiling argument about the Gallup items is sound and is the most transferable
  paragraph in the paper.
- The homogeneity point — that describing a bivariate relation by conditional means
  presumes the conditional distribution keeps its shape — is correct and rarely said.
- The effect-size honesty. "The flattening and accelerating patterns are even
  smaller modulations of a small effect" is a sentence very few authors write about
  their own headline.

## What I think does not follow

- **"Not statistically significant (i.e., flat)."** The parenthesis in the Table 1
  footnote is the error. The 95% bootstrap interval on the τ = 0.15 above-$100k slope
  is [−0.24, +1.07] and admits three quarters of the median's rate of gain.
- **The threshold is not a threshold.** Sweeping the knot across all ten admissible
  cut points gives a smooth decline, not a break; "flat" is declared where the
  p-value crosses 0.05. And the *centre* of the distribution has no break at all
  (median slope change z = 0.11).
- **The acceleration should not be in the abstract.** p = 0.023 as printed, 0.088
  under a paired bootstrap, Holm 0.184 over the twelve tests the paper reports — and
  it is the one the authors call "a third pattern, which we had not anticipated".
- **A quantile is not a person.** "There is an unhappy minority, whose unhappiness
  diminishes with rising income up to a threshold" is a claim about identified people
  from a cross-sectional quantile comparison. The paper's own diagnosis of Kahneman &
  Deaton — that a variable's name smuggles in a scope quantifier — applies to its own
  discussion, one level down.

## Two loose numbers, recorded so they are not re-quoted

- "The correlation between **average** happiness and log(income) is 0.09." 0.09 is
  the *person-level* correlation (0.0869 recomputed). The correlation between the 15
  band **averages** and log income is 0.976. In a paper about the scope of an
  inference, that phrase is an ecological correlation waiting to be miscited.
- "The difference between the **medians** of happiness at $15,000 and $250,000 is
  about five points." The deposited medians give 3.83. Five points is the *mean*
  difference, and needs the $400,000 band (4.94).

Neither changes a conclusion. Both are the kind of thing a knowledge base exists to
hold.

## Footnote worth keeping

*"Angus Deaton did not participate in this collaboration and should not be taken as
endorsing its conclusions."* One of the two authors of the criticised paper stayed
out. Adversarial collaboration is voluntary, and the published record of one is a
record of who agreed to be bound by it.
