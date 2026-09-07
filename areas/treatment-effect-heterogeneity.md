<!--kb
id: area:treatment-effect-heterogeneity
labels: kind:paper-notes, area:treatment-effect-heterogeneity
triggers: does this treatment help some people more than others; heterogeneity of treatment effect from aggregate data; variability ratio meta-analysis; coefficient of variation ratio interpretation; should we personalise this intervention; does an intervention change the variance or only the mean; how do I test whether the SD tracks the mean; using baseline arms as a negative control; what does VR near 1 actually rule out; correlation between placebo response and treatment effect; is sigma_TE identified from aggregate data; mathematical coupling in meta-analysis; a meta-analysis that deletes trials incompatible with its own parameter; additive versus multiplicative homogeneity; which null hypothesis does lnVR test; do antidepressants work better for some people than others; null slope of a variability ratio regression
verified: 2026-09-04
-->

# Treatment-effect heterogeneity from aggregate data

Author: maria. Started 2026-09-02. Records: `galante2021-mbp-nonclinical`,
`maria2026-mbp-variability-ratio`, `munkholm2020-antidepressant-variability`,
`maria2026-antidepressant-variability-recalibration`,
`mccutcheon2022-reappraising-variability`, `senn2016-mastering-variation`,
`marwick2018-nof1-schizophrenia`, `ploderl2019-personalised-antidepressants`,
`winkelbeiner2019-antipsychotic-variability`. Adjacent by method:
`maria2026-happiness-income-spread` (same location-versus-scale question, an
exposure rather than an intervention).

## The lead

**The two statistics this field runs on test two different null hypotheses, the
choice between them is load-bearing, and no paper in this literature says a choice
was made.** lnVR tests *additive* homogeneity (the treatment subtracts the same
amount from everyone); lnCVR tests *multiplicative* homogeneity (it multiplies
everyone by the same factor). Simulated on a real corpus with **zero** individual
variation by construction, each returns ≈ 1.00 under its own model and is badly
wrong under the other: an additive truth gives lnVR 0.999 / lnCVR 1.204; a
multiplicative truth gives lnVR 0.829 / lnCVR 0.999. A 17–20% apparent effect can
be manufactured by the choice alone, against real signals in this literature of a
few per cent.

The corpus can choose. Regress lnVR on the log ratio of arm means: under additive
homogeneity it should not track, under multiplicative homogeneity it should track
one-for-one — but **the estimator has a nonzero null slope of its own** (mean and
SD are correlated in skewed data), so the null must be measured or simulated, never
assumed to be 0. Done on two corpora, both say **additive**, so lnVR was the right
statistic in both and lnCVR would have been badly wrong.

Until the model is named and the bound reported, "VR ≈ 1, therefore no
heterogeneity of treatment effect" is a conclusion about an unstated assumption,
not about a treatment.

> **CORRECTION 2026-09-02, marked in place.** This section previously read: *"The
> assumption is a single number — how much a group's standard deviation travels
> with its mean — … measured here in three independent ways it is about 0.47,
> which is between the 0 that lnVR assumes and the 1 that lnCVR assumes, and
> significantly different from both."* **That inference was wrong and is
> withdrawn.** The number 0.47 is real and correctly measured; what was wrong was
> reading it as a coupling that adjudicates between the two statistics, and hence
> concluding that both are rejected. It is the *estimator's own null slope under
> additive homogeneity* — the value the regression returns when nothing is
> happening. Comparing it to 0 and 1 compares an estimator artifact to two
> substantive hypotheses. The adjudication requires the **observed** slope against
> the **null** slope, and when done that way lnVR is vindicated, not rejected. See
> `maria2026-antidepressant-variability-recalibration#c4` (the refutation) and
> `#c5` (the repair). The refuting evidence was a simulation on a second corpus in
> which the answer was known by construction.

## The same theorem, discovered twice, in two fields that do not cite each other

**2026-09-07.** `hope2019-not-so-proportional` (Brain) attacks the *proportional
recovery rule* in stroke: the claim that patients recover a fixed fraction of
lost function, supported by correlations between baseline and change that explain
80-94% of variance. Their Equation 1, for baselines X, outcomes Y, change
D = Y - X:

    r(X,D) = [s_Y r(X,Y) - s_X] / sqrt(s_Y^2 + s_X^2 - 2 s_X s_Y r(X,Y))

**That is this area's rho identity.** Write a patient's active outcome as
Y1 = Y0 + delta: then **rho IS r(X,D)** and **VR IS s_Y/s_X**. Checked as
functions on a 40x40 grid:

    max | Hope Equation 1  -  the sigma_TE / rho identity |  =  0.00e+00

Exactly zero. Two literatures, two ancestries -- Oldham (1962), Lord (1956),
Cronbach & Furby (1970) on one side; Nakagawa (2015) and ecological meta-analysis
of variation on the other -- arguing about one theorem under two names.

**The asymmetry is the useful part.** In stroke, X and Y are both *observed* on
the same patient, so r(X,Y) is estimable and Equation 1 pins r(X,D) exactly. In a
parallel-group drug trial one of the two is *counterfactual*, r(X,Y) is not
estimable at all, and **that is precisely why rho is not identified here.** Same
identity, different observability, different pathology: stroke gets a *spurious*
correlation it could have checked and did not; psychiatry gets an *unidentified*
parameter it cannot check and assumes.

**What this settles for us.** The attainable range of rho at each corpus's
measured VR, over ALL within-patient correlations:

| corpus | VR | max attainable rho |
|---|---|---|
| antipsychotics (Winkelbeiner) | 0.968 | **-0.251** |
| antidepressants endpoint (Munkholm) | 0.980 | -0.199 |
| antipsychotics, floor-corrected | 0.983 | -0.184 |
| VR = 1 (McCutcheon's own working) | 1.000 | -0.007 |
| antidepressants HAMD17 (Ploderl) | 1.004 | +0.271 |

At every one of these the *maximum* attainable rho is at or below zero.
**rho < 0 is forced by the algebra, not discovered in the data**, so estimating
rho, finding it negative and reading that as corroboration learns nothing. This
area already said that; what is new is that it was published about r(X,D) in
*Brain* in 2019 and nobody here cites it.

**And the fix is a design both fields already name.** r(X,Y) becomes observable
in a repeated-period cross-over -- Hope et al. reach it from the algebra of
correlations, `senn2016-mastering-variation` from variance components. Two
independent arguments, one experiment, still not run.

**Going the other way**, my floor work extends theirs: they show one ceiling
setting; `statlib.floor_shrinkage(z, headroom_dispersion)` gives the curve, and
the direction is a regime rather than a law. But their emphasis needs moving.
At the improvements stroke studies actually report (10-25 Fugl-Meyer points), the
ceiling alone yields s_Y/s_X in **[0.73, 1.00]** -- and every *fitters-only*
published value (0.158, 0.36, 0.438, 0.48) is BELOW that band while every
*whole-sample* value (0.80, 0.88, 1.20) is inside or above it. **The compression
is the fitter selection, not the ceiling.** A mixture with a genuine non-fitter
subpopulation fits four Zarahn targets to L1 = 0.084; one held-out statistic
matches and one misses by 0.23, so it is the right shape and not the right world.

**And the dispute in that field is a null-specification dispute, exactly like ours.**
Bonkhoff et al. (2023) rebut Hope et al. and their three simulations reproduce
exactly, including the strongest: error-coupled amplification is *completely*
offset when the two error magnitudes match (-0.707 at every level tested). But
Hope simulate `X` independent of `Y` and Bonkhoff simulate `X` independent of
`Y - X`; the second gives zero by construction and therefore settles nothing
about the first. Two statistics, two nulls, nobody stating which was chosen --
**the same failure this area found between lnVR and lnCVR, in a field with no
connection to ours.** That the shape recurs across unconnected literatures is the
reason to treat "which null?" as the first question rather than a technicality.

**The test neither side ran, and it went against my expectation.** Draw recovery
independently of baseline, clip it to the headroom, apply the field's own fitter
rule. Whole sample: the constraint alone gives -0.51 against an observed -0.49 --
indistinguishable -- but adding 30% non-fitters moves the null to -0.20, so **the
null shifts by 0.31 on a parameter the analyst chooses and nobody reports.**
Fitters only: no independent-recovery world gets near the observed -0.95 and 0.36
(best: -0.73 and 0.68), while a mixture *with* 70% proportional recovery matches
to L1 = 0.084. On the one dataset with individual data, **the rule is supported.**
I began sympathetic to the critique; the arithmetic partly vindicates the thing
being criticised, and that is worth more than a confirmation.

## The second statistic in this literature measures the treatment effect

`ploderl2019-personalised-antidepressants` reports, alongside VR = 1.01, a
coefficient-of-variation ratio CVR = 0.82 (0.80-0.84) and says of it: *"There is
no immediately plausible explanation for this finding."* There is one, and it is
arithmetic. Both statistics carry the same Nakagawa small-sample correction and
it cancels, so per trial

    lnCVR_i - lnVR_i = ln(m_PL,i / m_AD,i)      exactly

measured max deviation **2.8e-16** over 169 trials. CVR is VR divided by the
ratio of arm means, and the ratio of arm means is the treatment effect.

**The decisive test is in their own supplement.** On the 169 trials reporting a
pre-post CHANGE the drug arm's mean is the larger one, so CVR < VR. On the 84
reporting an ENDPOINT score the drug arm's mean is the smaller one, so CVR > VR:

| convention | k | VR | CVR |
|---|---|---|---|
| change scores | 169 | 1.01 | **0.82** |
| endpoint scores | 84 | 0.98 | **1.15** |
| tricyclics, change | 11 | 1.04 | **0.65** |
| tricyclics, endpoint | 13 | 0.93 | **1.37** |

**VR is stable. CVR crosses 1, and for tricyclics moves by a factor of 2.1** —
same drugs, same patients, same authors. Nothing changed except which of two
equivalent summaries a trial happened to publish. Both subsets were rebuilt from
upstream and reproduce to four significant figures.

This is not repaired by a better scale. An endpoint score has a meaningful zero,
so a CV is computable; a CV *ratio between arms* still carries the mean ratio.
**Do not use lnCVR for a two-arm comparison of dispersion.** If the worry is
that SD scales with the mean, estimate how much it does — see lambda below —
rather than dividing by the mean and hoping.

**And the justification usually given for switching to CVR does not survive.**
Ploderl & Hengartner cite r(M, SD) = 0.55 across trials. Within measurement
scale that correlation is +0.135 (Fisher-z pooled), so **75% of it is
between-scale mixing** in a corpus spanning HAMD17/21/24 and MADRS. Worse, an
across-trial correlation cannot license a within-trial, between-arm division:
the relevant statistic is r(ln mean ratio, ln SD ratio) = +0.110, p = 0.154.

**How much correction the data support: lambda.** Model the arm SD as a power of
the arm mean, SD proportional to mean^lambda, so lnVR = lambda * ln(m_AD/m_PL).
lnVR assumes lambda = 0, lnCVR assumes lambda = 1, and nobody in this literature
estimates it. It is estimable -- but the raw regression slope is NOT lambda: the
same regression returns +0.002 and +0.517 on simulated worlds where lambda is 0
and 1, so the estimator's own scale is 0.515 and must be calibrated against both
anchors. On the Ploderl corpus **lambda = 0.098 [-0.024, 0.241]** (4000
trial-level bootstrap resamples): lnVR's assumption is inside the interval,
lnCVR's is far outside, and **the published CVR applies 10.2 times the
correction the data support.** Report lambda beside every VR. It costs one
regression and two simulated worlds.

## Read this before anything else: what the design identifies

`senn2016-mastering-variation` settles the question this whole area is about,
and it was in print in 2015. Four components of variation in a trial:

    A between treatments   B between patients
    C patient-by-treatment interaction   D within patients, occasion to occasion

**C is sigma_TE^2. C is what "some patients respond better than others" means.**
And by design:

| design | identifies | error term |
|---|---|---|
| parallel group | A | **B + C + D** |
| classical cross-over | A, B | **C + D** |
| repeated-period cross-over | A, B, **C** | D |

*"Identification of differential response to treatment requires replication at
the level at which differential response is claimed."* Every paper in this area
reads C off a parallel-group trial, where it is not poorly estimated but **not
estimated at all**. Everything below is an audit of estimators for a quantity
the design does not identify. That is still worth having -- the design argument
has been available for a decade and has not moved the field -- but it is the
second question, and the order matters. Ask what the design identifies first.

Senn's own two worlds: 1000 patients, double cross-over, same mean difference
(0.5 L) and same SD of that difference (0.2 L), differing only in how well a
patient's effect in periods 1-2 predicts their effect in periods 3-4.
r = 0.90 gives sigma_C = 0.19 L; r = 0.02 gives sigma_C = 0.03 L. **A
parallel-group trial sees identical data in both. So does a classical
cross-over.** Only the replicate separates them.

**And the design that WOULD identify it has never been run on the question.**
`marwick2018-nof1-schizophrenia` inventories every n-of-1 trial in schizophrenia
to January 2017: **six studies, nine patients.** Zero compared an antipsychotic
against placebo. Two used replicated cycles -- the design feature that identifies
the interaction -- and those two patients were on donepezil and on a cognitive
intervention. **Zero reported comprehensive raw data.**

    17,202 patients of argument.  9 patients of evidence.
    2 in the right design.  0 on the drug.

This does NOT show that individual response is absent -- absence of the design is
not absence of the effect. It shows the field has spent a decade arguing about
the answer to a question for which nobody has run the experiment. Munkholm's
"assume the average applies to the individual" is the safer default given that,
but it is not better evidenced; it is the position that claims less.
*Forward search run 2026-09-04 rather than leaving the caveat standing: since
2017 the n-of-1 psychosis literature has added eszopiclone (a hypnotic, and
self-described as an unintended n-of-1), five music-therapy trials, and one
hypothetical case. **Still zero antipsychotic-vs-placebo. Nine years on.**
My search was title-restricted, so a trial described as a "single-case
experimental design" would be missed — the honest claim is "nothing under this
name".*

**FIVE axes of non-identification.** The fourth is Senn's and is
different in kind from the others -- it is not about the estimator but about
what an inflated variance can physically mean. The fifth is different again:
it is not about the estimator or the design but about **the measuring scale**,
and it is the only one of the five that could be removed with data every trial
already has.

1. VR **bounds** heterogeneity rather than measuring it (two arms with the same
   two moments are consistent with a uniform effect and with a mixture that
   transforms a third of people);
2. lnVR and lnCVR test **different nulls** and no paper says which was chosen;
3. **rho**, the correlation between individual effect and control outcome, which
   no parallel-group trial observes -- and at VR = 1 it *is* the answer, not an
   input to it (see below);
4. an inflated treated-arm variance may be **C or D**: patients differing from
   each other, or one patient differing from occasion to occasion. Senn's
   example is oral versus intravenous absorption. VR is identical either way.
5. **the outcome scale is BOUNDED, and the null for VR is therefore not 1**
   (added 2026-09-06, and this one is mine). PANSS cannot fall below 30; HAMD17
   cannot fall below 0. A patient cannot improve by more than their headroom, so
   the recorded improvement is min(X, H) and truncation removes variance. The
   treated arm improves more, so it meets the bound more often, so **a bounded
   scale always pushes VR in the same direction** at these headrooms. Size, on
   the two corpora that can be measured: **1 to 3 per cent**, which is the size
   of every effect either literature has ever reported. On the antipsychotic
   corpus a simulated world with sigma_TE = 0 EXACTLY reproduces 23% to 112% of
   the observed variance deficit, the range spanned by the baseline mean —
   **which the deposit does not record**. Unlike rho, this one is estimable: it
   needs one field that every trial reports.

   The governing parameter is `z = (mean headroom - mean improvement) / SD`, and
   `statlib.floor_shrinkage(z, headroom_dispersion)` returns the factor.
   **The direction is a regime, not a law**: a headroom that varies across
   subjects adds variance of its own, and above about 1.5 improvement-SDs of
   dispersion the bound INFLATES the recorded SD instead of shrinking it.

   | corpus | z treated | z control | VR bias | published VR | floor-corrected |
   |---|---|---|---|---|---|
   | PANSS, baseline 90 | 2.12 | 2.51 | 0.985 | 0.968 | **0.983 [0.964, 1.002]** |
   | PANSS, baseline 80 | 1.62 | 2.02 | 0.968 | 0.968 | **1.000** |
   | HAMD17 (k=68) | 1.57 | 1.87 | 0.974 | 1.007 | **1.034 [1.022, 1.046]** |

   At a plausible baseline the antipsychotic paper's significant result
   (VR = 0.97, p = .01) no longer excludes 1. **This correction is MODEL-BASED**:
   the within-corpus test that would confirm it has no resolving power on the
   available data (anchors separated by 0.52 of their own noise at k = 68), and
   that has to be said wherever the corrected number is quoted.

## The third axis, and it is the biggest one

**Everything above assumes the individual treatment effect is uncorrelated with
how the patient would have done on placebo. That assumption is not innocuous and
it is never stated.** Write the identity out:

    Var(Y_treated) = Var(Y_control) + Var(d) + 2 rho SD(Y_control) SD(d)
    => sigma_TE = sigma_PL ( sqrt(VR^2 - 1 + rho^2) - rho )

At rho = 0 and VR = 1 this gives **zero**. At rho = -0.32 and VR = 1 it gives
**0.64 sigma_PL**. The same data, the same VR, an answer that moves from "no
heterogeneity" to "individual effects twice the average effect", on one
parameter no trial reports. `mccutcheon2022-reappraising-variability` is the
paper that noticed this, and **its diagnosis is correct**. Its instrument is not.

- **All three of its rho estimators return a negative number when the true rho
  is zero**, for one shared reason: a quantity estimated from the placebo arm
  sits on both sides of the correlation with opposite signs. Open-label:
  Y(DBend) closes the placebo period and opens the drug period. Linear model:
  the placebo-arm slope's own estimation noise enters both the fitted effect and
  the placebo response — this one needs **no measurement error at all** and
  survives at reliability 1.00 (rho-hat = -0.141). Study level: T_s = D_s - P_s
  is correlated against P_s. **They are not three independent checks; they are
  one error in three costumes, which is why they agree.** Confirmed by removing
  it: split the placebo information into independent halves and every bias goes
  to zero.
- **The linear-model estimator, which carries their headline, has no sensitivity
  to rho at all** — it returns -0.142, -0.151, -0.150 while the truth moves 0,
  -0.29, -0.58. Its "individual treatment effect" is a deterministic function of
  age, sex and baseline severity, so it cannot see idiosyncratic response, which
  is the only kind large enough to matter.
- **The load-bearing error is a deletion, not the correlation.** Trials whose
  VR falls below sqrt(1 - rho^2) = 0.947 are "not compatible" and were removed —
  i.e. exactly the trials arguing hardest against heterogeneity. Feed the whole
  published pipeline a world where **every patient gets an identical benefit**
  (sigma_TE = 0.000 by construction) and it reports **14.9 [9.5, 21.0] PANSS
  points**, against their published 13.5 [12.7, 14.3]. With rho fixed at its
  TRUE value of zero it still reports 11.5; with the deletion turned off, 0.08.
- **On real data the correlation is entirely shared sampling error.** On 341
  antidepressant comparisons in 219 studies, computed their way rho = -0.178
  [-0.332, -0.028]; with the shared sampling variance removed analytically
  (it is just sd^2/n, printed in every forest plot) rho = **+0.001**
  [-0.209, +0.202].

**Report D, not VR.** The quantity aggregate data actually fix is

    D = sigma_AT^2 - sigma_PL^2 = sigma_TE^2 + 2 rho sigma_PL sigma_TE

D is unbiased, has a known sampling distribution, **can legitimately be
negative**, and needs no square root, no branch choice and no deletion. Every
pathology above enters when the identity is inverted for sigma_TE *before*
pooling instead of after.

**D carries UNITS and two corpora now have it, per scale.** Squared points of
HAMD17 are not squared points of MADRS.

| corpus | scale | k | D | I2 |
|---|---|---|---|---|
| Munkholm (via `mccutcheon2022`, m11) | HAMD17 | 166 | **-0.540 [-2.067, +0.986]** | 0% |
| Plöderl & Hengartner (`ploderl2019`, p06) | HAMD17 | 71 | **+0.444 [-1.748, +2.637]** | 0% |
| Munkholm | MADRS | 49 | +0.816 [-3.508, +5.141] | 0% |
| Plöderl | HAMD21 | 52 | *not estimable — see Dube2010 below* | |

Opposite signs, both straddling zero, intervals overlapping over most of their
length. **Two corpora, one conclusion: D is not distinguishable from zero.**

> **CORRECTED IN PLACE 2026-09-06.** This paragraph previously read *"For
> antidepressants **D = -0.384 [-1.636, +0.868]** squared HAMD points, I2 = 0%"*.
> That number pooled squared HAMD17, HAMD21, HAMD24 and MADRS points into one
> figure; its own unit string read "squared HAMD/MADRS points" and I wrote it
> anyway. Marked `superseded` in `mccutcheon2022#c6`, and `kb.py stale-claims`
> found this copy of it. **Two candidate defects were checked and cleared**: the
> inverse-variance weight (a real bias, found on Plöderl's corpus, but it needs
> unequal arm sizes and the Munkholm arms are balanced) and the heterogeneity
> estimator. Only the units mattered.

**Pooling a difference of variances is not free, and the obvious way is biased.**
`v_i = 2 s1^4/(n1-1) + 2 s2^4/(n2-1)` makes the weight a function of the same
draw as the numerator, so whichever arm is smaller has its deviations shrunk
harder and the pool drifts the other way. On Plöderl's corpus (placebo arm
smaller in 116 of 169 trials) the naive estimator returns **+0.514 squared points
from a world with D = 0 by construction**, with 90.2% coverage of a nominal 95%
interval. Three predictions of that mechanism were stated and all held: equal
arm sizes cut the bias to +0.064; swapping the arms reversed it to -0.567; a
weight built from the across-arm pooled variance removes it (-0.003, coverage
96.6%). `statlib.var_diff(..., weight="pooled")` is the fix and its docstring
carries the numbers.

**And simulation validates the estimator, not the corpus.** A contaminated-null
simulation built specifically to catch the loss of robustness caught nothing —
both weights survived one trial at an SD ratio of 2.7 among 129. Yet on the real
HAMD21 data the two weights differ by 1.46 and **one trial explains all of it**:
`Dube2010 (NCT00420004)`, drug SD 8.8, placebo SD 3.3, n 54 vs 122. Deleting it
moves Plöderl's HAMD21 D by -3.18 (73% of its own CI half-width, sign flip) and
Munkholm's by -1.92. Always report `statlib.max_loo_influence` beside D. On the
HAMD17 subsets it is 14% and 18% of the CI half-width, which is why those two
rows are in the table above and HAMD21 is not.

**The same anomalous trial sits in both corpora, and that is the more important
finding.** Plöderl & Hengartner name it themselves, in a Table 1 footnote,
having found it through the heterogeneity index of a different statistic. I
found it through leave-one-out in a different corpus. Munkholm et al. and
Plöderl & Hengartner assembled their trial sets from different reviews, and I
had been reading their agreement as replication. **They share trials**, because
both draw on the same registries and the same FDA submissions. Agreement between
two meta-analyses of overlapping trial sets is worth much less than it looks,
and this is the first hard evidence of the overlap in this area.

Then publish the curve, not a number. On Plöderl's HAMD17 corpus, with a median
placebo-arm SD of 7.76 points against a 1.88-point mean drug-placebo difference,
the upper confidence limit of D bounds sigma_TE at **1.62 points at rho = 0**,
2.58 at -0.10, 3.93 at -0.21, **5.45 at -0.32** and 9.89 at -0.62 — a **six-fold
range from one unmeasured parameter**.

**And at VR = 1 the formula is an identity, not an estimator.** With equal arm
variances, writing r for the within-patient correlation between a patient's
placebo and active outcomes,

    rho = -sqrt((1 - r)/2)        and        sigma_TE = -2 rho sigma_PL   exactly

so rho is **negative by construction for every r < 1** -- across the whole grid
of plausible r (0.4 to 0.95) and observed VR (0.95 to 1.05), rho is negative in
every cell. Finding a negative rho therefore confirms nothing whatever, and
"a negative correlation was a priori expected" is true in a way that destroys
rather than supports the argument: what is expected a priori cannot also be
evidence. Worse, rho and sigma_TE are the same unknown in different units, so
estimating rho "independently" and substituting it is not combining two pieces
of evidence -- it is assuming the answer. Read back: rho = -0.32 is the
assumption that a patient's drug and placebo outcomes correlate **0.795**;
rho = -0.62 is the assumption that they correlate **0.231**. No aggregate
dataset can check either.

**The honest state of this field: sigma_TE is not identified from aggregate
trial data.** Munkholm et al. assume rho = 0 silently. McCutcheon et al. estimate
rho with instruments that cannot measure it and delete the data that disagree.
Ten years of argument about the answer to a question the design cannot answer.

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
- **The regression of lnVR on the log ratio of means has a nonzero slope under the
  null, and that slope is measurable.** ~~The coupling coefficient β is real, is
  about 0.47, and nobody reports it … lnVR (β = 0) is rejected at 2.8 bootstrap SEs;
  lnCVR (β = 1) at 3.2.~~ **Withdrawn 2026-09-02** — see the CORRECTION above; the
  measurements stand, the inference from them does not. What the three
  measurements in `maria2026-mbp-variability-ratio` actually give is the estimator's
  null slope from data where no treatment has acted: randomised baseline arm pairs
  (0.473, 95% CI [0.255, 0.904], 232 pairs, 74 trials), untreated control arms'
  baseline-to-post change (0.394, se 0.162), and the same over all control types
  (0.508, se 0.091). **Randomised baseline arms give this without any distributional
  assumption; a simulated null needs a generator and inherits its choice.**
- **The model diagnostic: compare the observed slope to that null.** Antidepressants
  (`munkholm2020-antidepressant-variability`, 104 comparisons): observed 0.233,
  additive null 0.226, multiplicative prediction 0.978 — eleven SEs from
  multiplicative. Mindfulness (212 outcomes): observed 0.460, additive null
  0.31–0.47, multiplicative near 1. **Both additive. lnVR was right both times.**
- **Split the regression: the slope picks the model, the intercept tests
  homogeneity.** On the mindfulness corpus the intercept is 0.0006 at baseline,
  where it must be zero because nothing has happened yet, against −0.066
  [−0.111, −0.016] after the programme — a real ~6% compression in SD not
  associated with the mean moving, and not a coupling artifact, because the same
  estimator on the same trials returns zero when the treatment is removed.
- **The calibrated statistic `lnVR* = lnVR − β̂·ln(m₁/m₂)` keeps its arithmetic and
  loses its original justification.** Justified as an across-population coupling it
  is unbiased under *neither* model (bias +0.055 under an additive truth, −0.133
  under a multiplicative one). Justified as the regression intercept referenced to
  the estimator's own null slope, with β̂ from **randomised baseline arms**, it is
  defensible — and the mindfulness number is unchanged. **Consequence: the method
  does not transfer to corpora without baseline arms**, which includes the
  antidepressant corpus that exposed the flaw. On 212 mindfulness
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
  *proportional* one, i.e. it assumes multiplicative homogeneity rather than
  correcting for anything. Where the truth is additive it over-corrects badly:
  simulated with zero individual variation, lnCVR returns **1.204**. On the
  mindfulness corpus that is what turns a real difference into a null.
- **"β ≈ 0.47 rejects both lnVR and lnCVR."** Withdrawn 2026-09-02 — 0.47 is the
  estimator's null slope, not a substantive coupling, and comparing it to 0 and 1
  compares an artifact to two hypotheses. Both corpora tested so far support the
  additive model and therefore lnVR. Retained here rather than deleted because I
  published the wrong version first and someone may have read it.
- **"We cannot reject the null of equal variances" as a reportable result.** It is
  the absence of a finding. The same data support a **bound**, which is a finding:
  on 104 antidepressant comparisons the implied ceiling on the SD of individual
  treatment effects is 0.00 outcome SDs (additive) or 4.91 HAMD points
  (multiplicative), against an average drug-placebo difference of 2.70 points.
  Report the bound and name the model.

## Not yet read, and the obvious next step

The single cheapest valuable thing available: **run the model diagnostic on the
variability-ratio meta-analyses that already exist.** ~~antidepressant analyses~~
**Done 2026-09-02 for antidepressants** (`munkholm2020-antidepressant-variability`,
222 RCTs / 61,144 adults — verdict: additive, lnVR correct, conclusion stands).
Remaining: Winkelbeiner et al. 2019
(antipsychotics, JAMA Psychiatry — same group, same design, the obvious third
corpus), the PTSD variance-ratio analysis (2022), and the
depression-psychotherapy database (k = 306). **Caveat learned the hard way: the
GRISELDA deposit has no baseline SDs, so the antidepressant diagnostic had to be
simulated rather than measured. Check for baseline SDs before promising a
measured null.** All report VR near 1 and treat that
as the answer. All have arm-level baselines. If β is about a half in those corpora
too, then their published VR and CVR bracket an estimate nobody has computed, in
four literatures at once, for one regression apiece.

Also unread and relevant: Nakagawa et al. 2015 (the source of lnVR and lnCVR and
their small-sample corrections — the derivations are used here from
reimplementation and testing, not from the paper) and Volkmann et al. 2020 on
reappraising treatment-effect heterogeneity in schizophrenia.
