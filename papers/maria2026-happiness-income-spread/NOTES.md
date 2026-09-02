# Nothing about happiness flattens

maria, 2026-09-02. Judgement and reasoning; the numbers are in `paper.json` and the
code in `../kkm2023-conflict-resolved/reanalysis/`.

---

## What I set out to do, and what I actually found

I went looking for an **adversarial collaboration** because my corpus has a hole in
it. `breznau2022-hidden-universe` measures how far 73 teams' answers spread on one
dataset and stops there. `menkveld2024-nonstandard-errors` does the same in finance
and calls the spread a "nonstandard error". `mathur2023-effect-sizes` points out
that the spread looked worse than it was because everyone was reading significance
patterns instead of magnitudes. What none of them contains is a case where the
people who disagreed **sat down together over the union of the data and produced a
model that explains both of their results**. Killingsworth, Kahneman & Mellers 2023
is exactly that, with a named facilitator and a footnote recording that one of the
original authors declined to participate.

So the first thing to say is that the design worked. Two published, contradictory
claims — a $75,000 plateau in emotional well-being and no plateau at all — and a
joint reanalysis that finds both patterns in the same data. That is more than the
many-analysts literature has managed anywhere else in this corpus, and it took a
two-page paper.

The second thing to say is that I do not believe its interpretation, and it took
eleven scripts to say why in a form that can be checked.

---

## The finding, in one paragraph

Income raises the whole distribution of experienced well-being at a constant rate —
about 1.25 points per unit of log income, on a 0–100 scale, with **no change
whatsoever at $100,000** (median slope 1.231 below, 1.273 above, difference z =
0.11). What changes at $100,000 is the distribution's **width**: below it, income
compresses happiness — the 15th percentile closes on the median at 0.67 points per
log unit; above it, income spreads happiness out — the 15th percentile falls away
from the median at 0.94 points per log unit. Every number in KKM's Table 1 is a
projection of that single fact onto seven quantiles.

The decisive demonstration is the one I like best, because it needs no model.
Take the real data. Subtract each income band's own median and add back a straight
line in log income, so that the centre is *exactly* linear and no threshold in level
can possibly exist. Leave every conditional shape untouched. Re-run KKM's estimator.
It reports the flattening again, with an above-$100k slope at the 15th percentile of
**0.316** against the observed **0.336**. The flattening is not in the centre. It
was never in the centre.

---

## Where I was wrong, twice, and what caught it

**First.** I arrived expecting a Gelman–Stern error. Table 1 draws its boundary —
"restricted to the least happy 20%" — by noting that rows at τ ≤ .20 fail
significance and rows at τ ≥ .25 pass it, which is the textbook version of the
mistake. I built the paired bootstrap to demonstrate it. The test came back
**supporting KKM**: τ=.15 versus τ=.30 differ at p = 0.008, τ=.20 versus τ=.25 at
p = 0.006. The boundary is real. What is true is narrower and duller: the *table*
does not establish it, the *text* does, because the text runs the interaction test
and the interaction is far better powered than the level test. The paper reaches the
right conclusion through the weaker of its own two arguments.

That is worth holding onto. "This looks like a known statistical fallacy" is a
hypothesis, not a finding, and I have now twice watched it fail when actually tested.

**Second, and worse.** I ran a saturated location-scale simulation, got a mean
above-slope of 0.766 against an observed 0.336 and a pure-location expectation of
1.464, computed (1.464 − 0.766)/(1.464 − 0.336) = 62%, and started writing "the
width account explains only 62% of the flattening; the rest is a shape change."
It is not a decomposition. It is a ratio of differences of three numbers each with a
standard error near 0.34, and the gap it is built on — 0.43 — is 1.3 standard
errors. The correctly-specified test says a location-scale model is **not rejected**
on either side (Wald against the bootstrap covariance, p = 0.23 and 0.35). I had
manufactured a finding out of the distance between two point estimates.

`CONTRIBUTING.md` rule 3 names this exactly — "ratios of near-zero quantities are
not effect sizes" — and I wrote that rule after making the mistake once before. It
is recorded as `#c9` with status `disputed` against my own claim rather than
deleted, because the version of this note in which it never happened would be a
worse document.

Third, smaller: `r09`'s comparison of ESM-aggregated against intake-measured
variables pooled *binary* variables into the intake group. For a binary variable
SD = √(p(1−p)) is a deterministic function of the mean, so its "dispersion
gradient" is its mean gradient wearing a hat; `married` produced z = −21 on that
basis alone and dominated the pool. And the pooling was inverse-variance
fixed-effect across variables measuring different constructs, which assumes
between-construct heterogeneity is zero and returned z = −34 for a quantity whose
between-variable standard error is six times larger. Both corrected in `r10`, both
left in `r09` with the correction cross-referenced.

---

## The threshold that is not a threshold

KKM open by saying that a replication of Kahneman & Deaton should "not only
demonstrate the flattening; it should also reproduce its coordinates," and the
coordinates are the point of the exercise. So I swept the knot across all ten
admissible cut points. The above-knot slope of the 15th percentile goes

    $45k  $55k  $65k  $75k  $85k  $95k  $112.5k  $137.5k  $175k  $250k
    1.28  1.20  0.95  0.80  0.59  0.53   0.34     0.54    0.00   -0.04

A smooth decline. "Flat" is declared where the p-value crosses 0.05, between $85,000
(p = 0.045) and $95,000 (p = 0.103) — which is where the above-knot subsample stops
being able to resolve a slope of about half a point. Drop the knot entirely and fit
a quadratic in log income at every quantile: the curvature of the location component
is **+0.005**, and all the τ-dependence of curvature is carried by a term
proportional to the standardised quantile — the signature of a width change.

The provenance of the number is worth stating plainly, because it is a small
monument to how thresholds get built. Kahneman & Deaton's $75,000 is, in KKM's own
words, "simply the midpoint of the '60 to 90K' income category." KKM inflate that
to $97,000, note that $97,000 falls inside Killingsworth's "90 to 100K" band, and
split at $100,000. A survey designer's bin edge, adjusted for CPI, rounded to a
different survey designer's bin edge, and then reported as a coordinate that a
replication must reproduce. It reproduces because the estimator's resolution happens
to run out near there.

---

## The threat I could not dismiss cheaply, and how the second deposit killed it

Every person-level well-being value is a **mean over that person's momentary
reports**. Var(person mean) = between-person variance + within-person variance / k.
If k falls with income — high earners are busier, and Killingsworth's own deposit
shows the mean work week rising from 33.1 hours at $15,000 to 42.2 at $625,000 —
then the conditional variance rises with income for an entirely instrumental reason
and my whole result is an artifact.

KKM's deposit has four columns and cannot answer it. Killingsworth's **2021**
deposit can, by a route neither paper anticipated. The secondary feelings (good,
sad, afraid, …) were "assessed in independently randomized subsets of surveys," so
whether a participant ever answered one is 1 − (1 − p)^k — a monotone function of
how many reports they gave. The 2021 file stores per-band person counts for every
variable, so coverage = n(feeling)/n(well-being) is a usable proxy for k.

It says: coverage is flat at ≈0.48 through the $250,000 band and drops to 0.428 in
the top band. So high earners *did* report less, by about 16%, and the threat was
real. Three arguments then kill it.

1. Any k-gradient must hit the **sparse** measures hardest, because for them the
   noise term dominates the person-level variance. The twelve secondary feelings
   have roughly 35× fewer reports per person than the primary measure. They show
   **no widening at all** (−0.0005) while the primary measure shows +0.0413; the
   gap is z = 8.96. That is the opposite of the prediction.
2. The arithmetic. A coverage drop from 0.487 to 0.428 implies k falling from 30 to
   25.1. At a generous within-person SD of 30 that buys 5.8 of the 34.0 variance
   units observed — 17%, and 3–12% under more plausible assumptions.
3. Restrict to $100k–$250k, where the proxy is flat (slope −0.016 ± 0.060). The
   widening is still there and slightly larger (+0.049 versus +0.042 over the full
   range) — though on four income bands, so z = 1.3. This is the honest limitation:
   the finding survives at modest strength, not at overwhelming strength.

**The general lesson is the one I want to carry forward: the artifact that
adjudicates a paper is often in a different paper's deposit.** Neither file alone
could settle this. Together they could, and only because the 2021 deposit included
thirty variables nobody needed for its own argument. That is an argument for
depositing more than the analysis uses — the exact opposite of the minimalism that
made KKM's four columns so admirable in `#c1`.

---

## A quantile is not a person

This is the part that is not statistics.

KKM's own central lesson is about the scope quantifier hidden in a variable's name.
Kahneman & Deaton measured something, called it "happiness," and wrote "happiness
rises with income, but there is no further progress beyond ~$75,000." Had they
called the same numbers "unhappiness," the sentence would have been "unhappiness
diminishes with income, but there is no further progress beyond ~$75,000," and
every reader would have understood it as a claim about unhappy people only.
Identical numbers; different scope; and the difference lives in the noun.

The paper then writes: *"There is an unhappy minority, whose unhappiness diminishes
with rising income up to a threshold, then shows no further progress."* And: *"The
suffering of the unhappy group diminishes as income increases up to 100k but very
little beyond that. This income threshold may represent the point beyond which the
miseries that remain are not alleviated by high income. Heartbreak, bereavement, and
clinical depression may be examples of such miseries."*

There is no unhappy minority in these data. There is a 15th percentile. The person
at the 15th percentile of the $30,000 band and the person at the 15th percentile of
the $300,000 band have nothing in common except a rank, and nobody was followed from
one to the other. The paper says once, correctly, that it is "simply describing
cross-sectional associations." That disclaimer is one sentence; the group language
is the entire discussion, and it is what the sentence about heartbreak and
bereavement depends on.

I want to be careful about how hard to press this, because I have spent a career
listening to people who were, in fact, unhappy in ways money would not touch, and I
think the underlying intuition is likely true. But it is not what was measured. What
was measured is that above $100,000 the lower half of the happiness distribution
stops keeping pace with a middle that never slows down. Whether that is because a
stable group of sufferers stops benefiting, or because high income buys a wider
range of outcomes, or because people in distress are less likely to answer a
smartphone prompt at all — the design cannot distinguish, and only the third of
those was testable here.

**And the trap comes home.** My own knowledge base stores measurements under a
`quantities:` name. `quantile_slope_above_100k_tau15` is safe. Something like
`unhappy_group_income_benefit` would not be, and nothing in the schema would stop me
writing it. A quantity name is a variable name, and KKM's lesson is that a variable
name carries a scope quantifier the number does not. The `scope:` field exists on
claims and not on quantities. That is now the strongest argument I have for
extending the record format, and it came from a paper about money.

---

## What this is not

It is not a refutation. Every printed number in KKM 2023 reproduces from its deposit
to within the privacy rounding. The scope boundary is real. The homogeneity point in
their Discussion is correct and better stated than anywhere else I have read it.
What I dispute is one parenthesis — "not statistically significant (i.e., flat)",
where the 95% interval is [−0.24, +1.07] and admits three quarters of the median's
rate — and one inference, that a change in the shape of a distribution is a fact
about a group of people.

And one of their two "complementary nonlinearities" should not be in the abstract.
The acceleration at the 85th percentile is p = 0.023 as printed, p = 0.088 under a
paired bootstrap, and Holm 0.184 over the twelve tests the paper itself reports. It
is also the one the authors describe as "a third pattern, which we had not
anticipated." Under the bootstrap the τ=0.70 test, reported as non-significant at
0.075, becomes significant at 0.040, and the τ=0.85 test goes the other way. The
paper does not say which standard-error estimator its quantile regressions used, and
that unstated choice is the whole difference.

---

## Open, and owed

- Nobody has reviewed this. cidral should read `#c3` and `#c9`.
- One dataset, self-selected into an app for tracking one's own happiness, and every
  claim here is about a second moment. SOEP and Understanding Society would answer it.
- Why would a single monotone quantity turn around at exactly the threshold the
  previous literature had already named? I have no answer, and "the sign flips at the
  number everyone was already arguing about" should make me more suspicious, not less.
