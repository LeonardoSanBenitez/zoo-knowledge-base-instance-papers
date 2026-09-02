<!--kb
id: area:wellbeing-and-income
labels: kind:paper-notes, area:wellbeing-and-income
triggers: does money buy happiness; is there an income satiation point; the 75000 dollar threshold; experienced versus evaluative well-being; what happened to the happiness plateau; adversarial collaboration income happiness; quantile regression on well-being; does the spread of happiness change with income; how strong is the income happiness correlation actually
verified: 2026-09-02
-->

# Well-being and income

Author: maria. Started 2026-09-02. Records: `kahneman2010-high-income`,
`killingsworth2021-experienced-wellbeing`, `kkm2023-conflict-resolved`,
`maria2026-happiness-income-spread`.

## The lead

**There is no plateau in the central tendency of experienced well-being, at
$75,000, at $100,000, or anywhere in the observed range.** The median rises with
log(income) at about 1.25 points on a 0–100 scale per log unit, and its rate of
increase does not change at the threshold the literature spent thirteen years
arguing about (change z = 0.11). What *does* change at roughly $100,000 is the
**width** of the distribution: below it, income compresses happiness; above it,
income spreads it out. Every published number in the dispute is a projection of
that onto a quantile.

The correlation between individual happiness and log(income) is **0.087**, and the
median gap between the $15,000 and $250,000 bands is **3.8 points on a 100-point
scale**. Anyone quoting this literature for a policy or a life decision should
start there.

---

## The dispute, in three papers

**Kahneman & Deaton 2010** (PNAS), 450,000+ Gallup responses, dichotomous
yes/no items about yesterday's emotions: emotional well-being rises with log income
and shows "no further progress beyond an annual income of ∼$75,000," while life
*evaluation* keeps rising. The $75,000 is the midpoint of the "60 to 90K" survey
band — not an estimate of a threshold, a bin edge. The finding became one of the
most-quoted numbers in social science.

**Killingsworth 2021** (PNAS), 1.7 million momentary reports from 33,391 people
sampled at random moments on their phones, continuous response scale: well-being
rises approximately linearly with log(income), as steep above $80,000 as below.
No plateau.

**Killingsworth, Kahneman & Mellers 2023** (PNAS), an *adversarial collaboration*
with a named facilitator: both patterns are in Killingsworth's data. Flattening
above $100,000 appears in the bottom 15–20% of the happiness distribution;
acceleration appears in the top 30%; they offset to give the linear-log mean.

**maria 2026** (this KB, `maria2026-happiness-income-spread`): full reproduction
from the deposit, then a centre/spread decomposition. The numbers are right and the
interpretation does not follow. See the lead.

---

## What is settled

- **The mean/median relationship is log-linear with no threshold.** Fitting a
  quadratic in log(income) with no knot, the curvature of the location component is
  +0.005 — zero. Killingsworth 2021's central claim survives everything.
- **The lower tail behaves differently from the middle.** The interaction test (the
  *change* in slope at the knot) gives p = 0.001–0.004 at τ = .05/.10/.15/.20 and
  0.30–0.86 at τ = .25/.30/.35. The boundary KKM report is real and sharp.
- **It is a small effect.** r = 0.087 person-level. KKM say so themselves; almost
  nobody quoting them does.
- **The dichotomous Gallup items have a ceiling** and are better read as a measure
  of unhappiness than of happiness. The argument is KKM's, it is sound, and it
  generalises: an unmarked variable name carries a scope quantifier that the number
  does not.

## What is not settled

- **Whether the widening above $100,000 is substantive.** It survives the strongest
  artifact check the public deposits allow (see method note below), but at modest
  strength: z = 2.3 over the full above-$100k range, z = 1.3 restricted to the
  window where the confounder is flat. One self-selected sample, never replicated.
- **Why a monotone dispersion gradient would reverse sign at the number the
  previous literature had already named.** No account of this exists. "The sign
  flips exactly where everyone was already arguing" should raise suspicion.
- **Whether a "flattening" describes people or a rank.** Cross-sectional quantile
  comparisons cannot follow a person. See the standing caution below.

## What has been retired

- **"$75,000" as a threshold.** It is a survey bin midpoint. KKM say so in print:
  "simply the midpoint of the '60 to 90K' income category."
- **"$100,000" as a threshold.** Sweeping the knot across all ten admissible cut
  points gives a smooth decline in the low-quantile slope
  (1.28, 1.20, 0.95, 0.80, 0.59, 0.53, 0.34, 0.54, 0.00, −0.04) and no break. "Flat"
  is declared where the p-value crosses 0.05, between $85,000 and $95,000, which is
  where the above-knot subsample stops resolving a slope of about half a point.
- **The acceleration among the happiest 30% as an established finding.** p = 0.023
  as printed, 0.088 under a paired bootstrap, Holm 0.184 over the twelve tests the
  paper itself reports — and the authors describe it as unanticipated. Under the
  bootstrap the τ = 0.70 test, printed as non-significant at 0.075, becomes
  significant at 0.040 and τ = 0.85 goes the other way. The paper does not name its
  standard-error estimator, and that unstated choice is the difference.

---

## Standing caution: a quantile is not a person

The single most important thing to carry out of this area, and the one most likely
to be forgotten.

Every result here is a comparison of **ranks across different people at different
incomes**. The person at the 15th percentile of the $30,000 band and the person at
the 15th percentile of the $300,000 band share nothing but a rank; nobody was
followed from one to the other. So sentences of the form *"the unhappy stop
benefiting above $100,000"* — which is how this literature is quoted, and how KKM's
own discussion reads — are longitudinal claims made from cross-sectional quantiles.

KKM diagnose exactly this error in Kahneman & Deaton, one level up: a variable's
*name* carries a scope quantifier the number does not. Then they write "There is an
unhappy minority, whose unhappiness diminishes with rising income up to a
threshold." The paper does note once, correctly, that it is "simply describing
cross-sectional associations." One sentence of disclaimer against a discussion built
on the group reading.

Nothing in these data licenses a claim about what happens to a person as their
income rises. Longitudinal designs exist — the lottery-win literature (Gardner &
Oswald 2007, cited by KKM) and the household panels — and are not in this corpus yet.

---

## Method notes worth reusing elsewhere

**Centre/spread decomposition of a quantile slope.** Q_τ(L) = median(L) + D_τ(L)
splits any quantile trend into a location term and a spread term with no model and
no distributional assumption. If someone reports that "the bottom of the
distribution flattens," this says immediately whether the centre stopped rising or
the tail stopped keeping up — and those are different findings with different
interpretations. It answered in one script what a location-scale model, a
simulation ladder and a bootstrap took nine more to confirm.
(`maria2026-happiness-income-spread#c3`, script `r07`.)

**Knot sweep.** Any reported threshold should be re-estimated at every admissible
cut point before it is called a threshold. If the estimate declines smoothly and the
p-value crossing is what moves, the "threshold" is the estimator's resolution limit.
Cheap: ten refits. (`#c4`, script `r05`.) The same argument, independently reached,
is in `gamma2021-mpe92m#c2` about the number of factors in a questionnaire — two
literatures, no citation between them, one point.

**Planned missingness as an exposure proxy.** When a study assigns secondary
measures to *randomly chosen subsets* of occasions, the probability a participant
ever answered one is 1 − (1−p)^k, a monotone function of how many occasions they
contributed. So a per-group *person count* for a secondary measure is a usable proxy
for participation intensity — which is often the confounder you need and never the
column anyone deposits. (`#c5`, script `r10`.)

**The adjudicating artifact is often in a different paper's deposit.** The 2023
four-column deposit reproduces its own paper perfectly and cannot test its own
finding. The 2021 deposit, which does *not* reproduce its own paper, carries thirty
variables nobody needed and is what settles the 2023 question. This cuts against
minimalism in deposits, and it is the reason to cross-check two deposits of the same
study against each other — here, person counts identical across all 15 bands, means
within 0.012, SDs within a factor 1.003, from files deposited two years apart.

---

## Not yet read

- Gardner & Oswald 2007, lottery wins and mental well-being — the longitudinal arm
  this area is missing.
- Jebb, Tay, Diener & Oishi 2018 (*Nat. Hum. Behav.*), "Happiness, income satiation
  and turning points around the world" — the satiation claim outside the US.
- Stevenson & Wolfers 2013, "Subjective well-being and income: is there any evidence
  of satiation?"
- Kushlev, Dunn & Lucas 2015 and Hudson et al. 2016 — income predicts daily sadness
  but not daily happiness, and a replication of it. Directly relevant to the
  asymmetry between the lower and upper tails found here, and neither is in the KB.
