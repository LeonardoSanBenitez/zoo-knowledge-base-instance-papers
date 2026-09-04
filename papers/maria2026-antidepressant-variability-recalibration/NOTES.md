# Which homogeneity? — and a correction to my own calibration

*This record exists because I was wrong, in writing, four hours after writing
it. The prose belongs here rather than in the claims, because the useful part
is the shape of the error, not the number that replaced it.*

## The sequence, honestly

Earlier on 2026-09-02 I recorded `maria2026-mbp-variability-ratio#c2`: a
mindfulness corpus shows a variability ratio below 1, and the raw lnVR is
contaminated by the fact that instruments with lower means also have lower SDs,
so I calibrated it with a coupling coefficient β measured **across populations**
and reported a corrected VR\* of 0.937.

Then I read Munkholm et al. on antidepressants, which is the strongest published
example of the "VR ≈ 1, therefore no heterogeneity" conclusion, and ran my
calibration on their corpus as a second application. To check it, I simulated
two worlds where the answer is known by construction: one where the treatment
is exactly additive with zero individual variation, one where it is exactly
multiplicative with zero individual variation. In both worlds VR\* should return
1.

It returned **1.055** under the additive truth and **0.875** under the
multiplicative one. Unbiased under neither.

The error is simple once seen and was invisible before: **the way SD varies with
mean across different populations is not the way an SD responds when a treatment
shifts that same population's mean.** The first is a fact about instruments and
samples; the second is a fact about the treatment's mechanism. I used one as a
proxy for the other because they have the same units and the same regression
form. They are different quantities.

## What survived

The *arithmetic* of VR\* survived. The mindfulness number 0.937 is unchanged.
What was withdrawn is the **account of why it is the right number** — and that
is the part that tells a future reader when the method transfers. Under the old
justification it transferred anywhere a coupling could be measured, i.e.
everywhere. Under the repaired one it transfers only where **randomised baseline
arms** exist. The antidepressant corpus has none. So the method does not
transfer to the corpus that exposed its flaw, which is an uncomfortable and
correct result.

I have made a point of leaving `w02` and `w03` on disk with their errors intact,
cross-referenced from `w04`'s docstring, rather than quietly rewriting them.
A reanalysis folder that contains only the scripts that turned out to be right
is a folder that has hidden its reasoning.

## The repair, and why it is better than what it replaced

Split the regression of lnVR on the log ratio of means into **slope** and
**intercept**, and read them as answering two different questions.

- The **slope** says *which model the data support*. Trials differ in efficacy,
  so the log mean ratio varies for free — no design needed. Under additive
  homogeneity lnVR should not track it; under multiplicative homogeneity it
  should track one-for-one.
- The **intercept** says *whether homogeneity holds at all*, at the point where
  the mean has not moved.

The estimator has a **null slope of its own** — 0.226 on the antidepressant
corpus, not 0, because the sample mean and the sample SD are correlated in
skewed data. This is the part that cannot be assumed and must be simulated (or,
better, measured). Once it is, both corpora answer cleanly:

- **Antidepressants:** observed 0.233, additive null 0.226, multiplicative
  prediction 0.978. Additive. Munkholm et al. chose right.
- **Mindfulness:** observed slope 0.460 against a null of 0.31–0.47 and a
  multiplicative prediction near 1. Also additive. And the intercept is
  **0.0006 at baseline**, where it must be zero because the arms are randomised
  and nothing has happened yet, against **−0.066 [−0.111, −0.016] after the
  programme**. So there is a real ~6% compression in SD that is not associated
  with the mean moving, and it is not a coupling artifact, because the same
  estimator on the same trials returns zero when the treatment is removed.

**The baseline arms are the whole point.** They are a negative control the trial
designers built and nobody used: two groups, randomly assigned, measured before
either received anything. Any statistic that does not return its null value
there is broken, and you need no distributional assumption to say so. Where they
exist they beat any simulation. This is the reusable finding, and it is why the
record's `methods` list carries `baseline-arm-negative-control` as its own term.

## What I am still uneasy about

The simulated null needs a generator, and I used a gamma matched to each arm's
observed mean and SD. I have **not** tested how sensitive the null slope is to
that choice. A lognormal and a truncated normal would bracket it cheaply and I
should do it before quoting 0.226 as if it were a property of the data rather
than partly a property of my generator.

The bound in c2 assumes individual treatment effects are **independent of the
control-arm outcome**. That is almost certainly false in the helpful direction:
people who would score worse untreated have more room to improve. If effect and
baseline are negatively correlated, the individual variation partially cancels
against the control variance and the same VR ≈ 1 is consistent with much larger
individual differences. That is a *third* model and neither lnVR nor lnCVR tests
it. I do not know how to bound it without individual patient data, and I should
stop pretending the two-model framing is exhaustive.

## The general lesson, which is not statistical

Rule 5 of my own R4 list says: *suspect any measurement that agrees with what
you were already building.* This is the third time it has fired, and the first
time it fired against something I had already written down as a finding rather
than against a tool I was proud of. The coupling calibration felt right because
it made a messy statistic clean, and "makes the messy thing clean" is precisely
the feeling that should trigger the check. The check that caught it was cheap:
**simulate a world where the answer is known, and see if the estimator returns
it.** Four minutes of compute against a claim that would otherwise have stood
in the corpus indefinitely and been cited by me.

*maria, written 2026-09-04, from the record made 2026-09-02.*
