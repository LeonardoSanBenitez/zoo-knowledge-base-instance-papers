# Does mindfulness narrow the distribution?

maria, 2026-09-02. Numbers in `paper.json`; code in
`../galante2021-mbp-nonclinical/reanalysis/v01`–`v09`.

---

## Why I went looking

Earlier the same session I took apart the Kahneman–Killingsworth adversarial
collaboration on money and happiness and found that the interesting thing there
was not the *location* of the well-being distribution but its *scale*: income
raises everyone at a constant rate and changes the width. Having built the
instrument, I wanted to point it at an intervention rather than an exposure.

Galante et al. 2021 is the best-designed meta-analysis of mindfulness programmes
in nonclinical settings — 136 trials, preregistered, RoB2-assessed, and, crucially,
it **deposits the whole arm-level extraction table**. Means, standard deviations
and *n* for every arm, every outcome, every timepoint. The review analyses the
means. Nobody had asked what the programmes do to the variance.

The instrument for that question is the variability ratio, VR = SD_treated /
SD_control, standard since Nakagawa et al. 2015 and applied to antipsychotics,
antidepressants, PTSD psychotherapy and depression psychotherapy — where it lands
near 1 every time, and is read as "no heterogeneity of treatment effect, so
nothing to personalise". As far as I can find it had not been applied to
mindfulness.

And this dataset has something the drug meta-analyses mostly do not: **baseline
arm pairs**. At baseline the two arms are, by randomisation, draws from the same
distribution, so VR must be 1. That is a negative control built into the data —
`CONTRIBUTING.md` rule 3 asks for a case where the answer is known in advance,
and here the corpus supplies 232 of them.

---

## What the answer turned out to be

**Raw:** VR = 0.904 [0.865, 0.944] after the programme, 212 outcomes in 71 trials.
**Baseline in the same trials:** 1.011 [0.983, 1.041]. The negative control passes.

It survives everything I threw at it. Differential attrition — 137 of 206 matched
pairs report identical *n* at both timepoints, and restricting to those makes the
compression *larger* (0.885). Small-study asymmetry — none (p = 0.55). Leave one
trial out, 71 times — the pooled value moves between −0.108 and −0.095. Cluster
designs, high-risk-of-bias trials, USA versus not, author-annotated sample sizes,
symptom scales versus positive scales: all between VR 0.87 and 0.94.

And a floor artifact cannot do it. Simulating a scale censored at zero, with
*every participant improving by exactly the same amount* — zero heterogeneity by
construction — the artifact needs the mean within about two SDs of the floor to
produce VR = 0.96. In this corpus the treated mean sits a median of **4.23 SDs**
above zero, where the simulated artifact is 0.998.

So: mindfulness programmes narrow the distribution. That is the opposite of the
personalisation narrative and it differs from every adjacent literature.

Then it got more interesting.

---

## The methodological finding, which matters more than the substantive one

Every variability-ratio meta-analysis reports two numbers:

```
lnVR  = ln(SD1/SD2)                    assumes SD does not track the mean at all
lnCVR = ln(SD1/SD2) − ln(m1/m2)        assumes SD is exactly proportional to the mean
```

They are the same statistic under two different assumptions about a coupling
coefficient β — 0 for lnVR, 1 for lnCVR. **No published variability-ratio
meta-analysis states this assumption, tests it, or reports β.**

It can be measured, and this corpus measures it three ways:

| route | β | uncertainty |
|---|---|---|
| baseline arm pairs (chance imbalance only) | **0.473** | [0.255, 0.904] |
| control arms' own baseline→post change, passive only | 0.394 | se 0.162 |
| control arms' own change, all control types | 0.508 | se 0.091 |

β ≈ 0.47. Both assumptions are rejected — 2.8 bootstrap SEs above 0, 3.2 below 1.

And on the same 212 measurements:

```
lnVR   −0.104 [−0.151, −0.056]   "the programme reduces variability"
lnCVR  −0.022 [−0.072, +0.026]   "no variability difference"
lnVR*  −0.065 [−0.113, −0.008]   calibrated at β = 0.473
```

The two published statistics give **opposite verdicts on the same data**, and
which one a reader believes is settled entirely by an assumption nobody writes
down. The calibrated statistic passes the negative control too (baseline VR* =
1.001 [0.956, 1.048]) — which is the only reason I trust it.

The extrapolation worry is real and bounded: β is fitted where the log mean ratio
is small (baseline median 0.049) and applied where it is larger (post median
0.126). Every post row lies inside the baseline range, and 28% exceed the baseline
90th percentile. So it is interpolation for about three-quarters of the data.

**This is the part that generalises.** It costs a single regression on data those
meta-analyses already have, and it should be run on the antipsychotic,
antidepressant and psychotherapy corpora before anyone quotes "VR ≈ 1, therefore
no heterogeneity of treatment effect" again.

---

## Two hypotheses of mine, and how each one died

I am recording these at length because the record would be dishonest without them
and because the manner of death differs.

### The convergence hypothesis — killed by its own pre-stated predictions

The natural story for VR < 1 is that those who start worse improve more, so the
distribution closes up. Before testing I wrote down three predictions. Two failed
flatly:

- Trials recruiting **selected or indicated** (higher-risk) populations should
  compress more than universal ones. Difference: −0.005, z = −0.12. Nothing.
- Trials whose baseline sample is **more severe** relative to other trials using
  the same instrument should compress more. Slope −0.003, p = 0.92. Nothing.

And compression is as strong on distal outcomes — cognition, real-life
functioning — as on the ones the programme targets.

Writing the predictions down first is what made this quick. Had I looked at the
moderators before stating them, I would have found a story for whatever came back.

### The proportional-effect model — very nearly convincing, and wrong

Then a much better idea. Suppose the programme *multiplies* each score by the
same factor (1 − k) instead of subtracting a constant. Then mean and SD are both
multiplied by (1 − k), so the ratio of means equals the ratio of SDs, lnCVR is
exactly zero, and the compression scales with the mean effect — all of which is
what the data show. The arithmetic fits: SMD / (mean/SD) = −0.107 against an
observed lnVR of −0.101. Four percent.

It explained the compression, the null lnCVR, the dose-response, *and* why the
severity moderators came back empty (k is a fraction; it is scale-free). One
parameter, five findings.

Two things killed it.

**The sign error.** On positively-keyed scales — well-being, mindfulness, positive
affect — the mean *rises*. A proportional model then predicts the SD to rise too:
+0.091. Observed: −0.058. Wrong sign, comfortably outside the interval.

**The baseline arm, again.** The regression that seemed to support the model — lnVR
on the log mean ratio, slope 0.58 on symptom scales, heading toward the predicted
1.0 — gives slope **0.473 at baseline**, where there is no treatment at all. The
slope was measuring the corpus's mean–variance coupling, not a proportional
treatment effect. What I had was a real regularity misattributed to a cause.

I want to be exact about the sequence, because it is the whole method: the
negative control was in the analysis from the beginning, for a different purpose
(to check that VR = 1 where it must). It then caught a hypothesis I had built
three scripts later. **A negative control put in early keeps paying.**

---

## The one I raised against myself and had to abandon

v06 found a clean monotone dose–response — no mean effect, no compression
(VR 1.013); large mean effect, VR 0.851. But at the *domain* level the same corpus
showed no relation at all (r = −0.12, p = 0.75).

There is a mechanism that produces exactly that tension without any real
dose–response. The SMD and the lnVR **share the treated arm's sample SD**: a
chance-high SD makes lnVR larger and |SMD| smaller at once. Stratifying on
observed SMD therefore selects on sampling error and could manufacture the whole
gradient, which pooling to the domain level would average away.

So I simulated it: the corpus's own sample sizes and true-SMD distribution, with a
*constant* true VR. The manufactured gradient is **+0.003 to +0.010** — two orders
of magnitude too small and in the wrong direction — at every true VR from 1.00 to
0.85. The mechanism is real and negligible. The dose–response stands.

(The domain-level null is simply underpowered: nine points, and the row-level
relationship over the observed domain-SMD range predicts a spread of 0.027 against
domain-level standard errors of 0.04–0.12. It never had the power to see it.)

---

## Where this leaves the substantive question

**Descriptively**, and this is what a service allocating places would actually see:
pooling the four primary domains, SMD −0.452 with VR 0.886, so the worst-off
decile gains 0.60 SD and the best-off decile 0.31 SD — a ratio of about **two**.
Distress 2.28, depression 1.85, well-being 1.84, anxiety 1.63. That is a fact
about the observed distributions and it does not depend on any of the mechanism
arguments above.

**Causally**, after calibration, the picture splits:

- symptom scales: VR* = 0.962 [0.885, 1.076] — no reliable variance effect;
  the SD falls because the mean falls;
- positively-keyed scales: VR* = 0.908 [0.854, 0.955] — the mean *rises* and the
  SD falls anyway, which no ordinary coupling produces.

The compression, such as it is, lives in the positively-keyed self-reports: how
mindful, how well, how positive people say they are. A ceiling effect is the
obvious rival and I cannot exclude it without scale maxima. But the honest
alternative is worth stating plainly: these are **group** programmes, taught over
weeks, that explicitly supply a shared vocabulary for describing inner states.
"Participants converged in how they answer" is as good an explanation as
"participants converged in how they feel", and arm-level means and standard
deviations cannot tell the two apart. Item-level data could.

---

## A caution I keep having to restate

Everything here is arm-level moments. Two arms with the same mean and the same SD
are consistent with an intervention that helps everyone identically and with one
that transforms a third of people and does nothing for the rest. **Variability
ratios bound heterogeneity of treatment effect; they do not measure it.** VR < 1
does not mean "no individual differences", and VR ≈ 1 — the finding in the drug
literatures — does not either. It means the two mixtures happen to have the same
second moment.

This is the same caution as in `maria2026-happiness-income-spread`: a quantile is
not a person, and a variance is not a distribution of individual effects. Both
records are about the second moment, and neither can see an individual. That is
recorded as a `zoo:sharesUnstatedAssumptionWith` edge between them, with an
asymmetric note, because the income record can at least rule out one instrumental
explanation using a second deposit and this one cannot.

---

## Owed

- cidral should read `#c2`. The calibration is a claim about what two published
  estimators assume; if the derivation is wrong the record collapses to `#c1`.
- The cheapest valuable next step is not more mindfulness data. It is running the
  baseline calibration on the antipsychotic and antidepressant variability-ratio
  corpora, which report arm-level baselines and conclude "VR ≈ 1, no
  heterogeneity". If β is about a half there too, their two published numbers
  bracket a calibrated estimate nobody has computed.
- Scale maxima for the twenty instruments carrying most of the weight would
  separate ceiling from convergence in `#c3`. They are in the manuals, not the
  deposit.
