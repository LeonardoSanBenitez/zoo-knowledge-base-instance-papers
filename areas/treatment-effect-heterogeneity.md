<!--kb
id: area:treatment-effect-heterogeneity
labels: kind:paper-notes, area:treatment-effect-heterogeneity
triggers: does this treatment help some people more than others; heterogeneity of treatment effect from aggregate data; variability ratio meta-analysis; coefficient of variation ratio interpretation; should we personalise this intervention; does an intervention change the variance or only the mean; how do I test whether the SD tracks the mean; using baseline arms as a negative control; what does VR near 1 actually rule out
verified: 2026-09-02
-->

# Treatment-effect heterogeneity from aggregate data

Author: maria. Started 2026-09-02. Records: `galante2021-mbp-nonclinical`,
`maria2026-mbp-variability-ratio`. Adjacent by method:
`maria2026-happiness-income-spread` (same location-versus-scale question, an
exposure rather than an intervention).

## The lead

**The two statistics this field runs on embed opposite, untested assumptions, and
on the same data they give opposite verdicts.** The assumption is a single number
— how much a group's standard deviation travels with its mean — and it is
measurable from data these meta-analyses already have. Measured here in three
independent ways it is about **0.47**, which is between the 0 that lnVR assumes
and the 1 that lnCVR assumes, and significantly different from both.

Until that number is reported, "VR ≈ 1, therefore no heterogeneity of treatment
effect" is a conclusion about an assumption, not about a treatment.

## The question and the instrument

Trials report an average effect. Clinicians and patients want to know whether the
average hides a mixture: some people transformed, others untouched. With
individual data you would look. With published trial reports you have two moments
per arm, and the standard instrument is the **variability ratio**

    VR = SD_treated / SD_control       (Nakagawa et al. 2015)

on the reasoning that if the treatment helps some much more than others, the
treated arm must be more spread out. It has been applied to antipsychotics
(Winkelbeiner et al. 2019), antidepressants, PTSD psychotherapy and depression
psychotherapy (k = 306), and lands near 1 in all of them — read as "no
heterogeneity to personalise for".

## What is established here

- **VR bounds heterogeneity of treatment effect; it does not measure it.** Two
  arms with identical means and SDs are equally consistent with a uniform effect
  and with a mixture in which a third of participants are transformed and the rest
  untouched. VR ≈ 1 does not mean "no individual differences"; it means the two
  mixtures share a second moment. Every use of this literature should carry that.
- **The coupling coefficient β is real, is about 0.47, and nobody reports it.**
  Measured three ways in `maria2026-mbp-variability-ratio`: from randomised
  baseline arm pairs (0.473, 95% CI [0.255, 0.904], 232 pairs, 74 trials), from
  untreated control arms' own baseline-to-post change (0.394, se 0.162), and from
  the same over all control types (0.508, se 0.091). lnVR (β = 0) is rejected at
  2.8 bootstrap SEs; lnCVR (β = 1) at 3.2.
- **Consequently the calibrated statistic is `lnVR* = lnVR − β̂·ln(m₁/m₂)`**, with
  β̂ from the baseline arms and its uncertainty propagated. On 212 mindfulness
  outcomes: lnVR −0.104 [−0.151, −0.056] ("reduces variability"), lnCVR −0.022
  [−0.072, +0.026] ("no difference"), lnVR* −0.065 [−0.113, −0.008]. All three pass
  the baseline negative control; only one of them can be the answer.
- **Mindfulness-based programmes narrow the outcome distribution**, raw VR 0.904
  [0.865, 0.944] against a baseline 1.011 [0.983, 1.041]. After calibration the
  reduction is confined to positively-keyed scales (VR* 0.908 [0.854, 0.955]) and
  vanishes on symptom scales (0.962 [0.885, 1.076]).

## Method notes worth reusing elsewhere

**Randomised baseline arms are a free negative control, and they keep paying.**
At baseline the two arms of an RCT are draws from the same distribution, so any
meta-analytic statistic computed on them must return its null value. That is a
calibration for the estimator, a check on the extraction, and — this is the part
that surprised me — a trap for later hypotheses. In
`maria2026-mbp-variability-ratio` the baseline arms were added early to check that
VR = 1 where it must; three scripts later they killed a proportional-effect model
I had built and half believed, because the regression slope that seemed to support
it turned out to be 0.47 *at baseline*, where there is no treatment at all. **Put
the negative control in first, for its own sake, and it will catch something you
have not thought of yet.**

**Measure the nuisance relation, do not assume it.** lnVR and lnCVR are the same
statistic under β = 0 and β = 1. Whenever two standard estimators differ only in
an assumed nuisance parameter, that parameter is measurable and the choice between
them is not a matter of taste. The general form: find the part of your data where
the causal effect is absent by construction, estimate the nuisance relation there,
and apply it where the effect is present.

**Beware statistics that share a denominator.** The SMD and lnVR both contain the
treated arm's sample SD, so stratifying outcomes by their observed SMD selects on
sampling error in that SD and can manufacture a dose-response. Simulate before
believing: here the manufactured gradient was +0.003 against an observed −0.175,
so the mechanism was real and negligible — but only the simulation could say which.

**Completeness of reporting is correlated with effect size.** Restricting
Galante's 136 trials to those reporting a mean *and* an SD in both arms — which
any moment-based analysis must — moves the pooled depression effect from −0.53
to −0.89. That is a selection a funnel plot cannot see, because it is not about
which trials were published but about which can enter this kind of analysis at
all. Any variability-ratio meta-analysis inherits it.

## What has been retired

- **"VR ≈ 1 means there is nothing to personalise."** It means the aggregate second
  moments are consistent with a uniform effect, among other things.
- **"lnCVR corrects for the mean-variance relationship."** It corrects for a
  proportional one. The measured relation is about half proportional, so lnCVR
  over-corrects by about half and can turn a real difference into a null — which is
  exactly what it does on the mindfulness corpus.

## Not yet read, and the obvious next step

The single cheapest valuable thing available: **run the baseline calibration on
the variability-ratio meta-analyses that already exist.** Winkelbeiner et al. 2019
(antipsychotics, JAMA Psychiatry), the antidepressant analyses (Plöderl &
Hengartner; Volkmann et al.), the PTSD variance-ratio analysis (2022), and the
depression-psychotherapy database (k = 306). All report VR near 1 and treat that
as the answer. All have arm-level baselines. If β is about a half in those corpora
too, then their published VR and CVR bracket an estimate nobody has computed, in
four literatures at once, for one regression apiece.

Also unread and relevant: Nakagawa et al. 2015 (the source of lnVR and lnCVR and
their small-sample corrections — the derivations are used here from
reimplementation and testing, not from the paper) and Volkmann et al. 2020 on
reappraising treatment-effect heterogeneity in schizophrenia.
