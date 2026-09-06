# Plöderl & Hengartner 2019 — what the second antidepressant variance meta-analysis measures

Read 2026-09-06 by maria. `read-and-reanalysed`. Area:
`treatment-effect-heterogeneity`. Scripts `p01`–`p08` in `reanalysis/`.

## Why this paper

TODO T3 from the 2026-09-04 session: *recompute `D = sigma_AT^2 - sigma_PL^2`
with an interval for the psychiatric variability meta-analyses; none of them
reports it, and it is the quantity a parallel-group design actually fixes.*
This is the open-access one with the largest antidepressant corpus, and it is
independent of `munkholm2020` (different data source, different authors, same
question).

It turned into more than that, because the paper contains a result its own
authors call unexplained, and the explanation is arithmetic.

## Reproduction first

Their OSF deposit is cited in the paper as *"The R-code and data of this
publication are available online"*. It holds ten files: five R scripts and two
supplementary PDFs and three manuscript versions. **The data file the code reads
(`Cipriani et al_GRISELDA_Lancet 2018_Open data_averaged_doses.csv`) is not
there.** The code documents every transformation applied to it, so `p01`
rebuilds it from the public upstream — Cipriani et al. (2018) GRISELDA, Mendeley
`83rthbp8ys` v2, 189 KB, sha256 `16743cad…`.

The rebuild lands exactly on their published counts:

| | theirs (Table 1) | reconstruction |
|---|---|---|
| trials | 169 | **169** |
| patients, drug arms | 32 650 | **32 650** |
| patients, placebo arms | 18 746 | **18 746** |
| VR | 1.01 (0.99–1.02) | **1.006 (0.995–1.017)** |
| CVR | 0.82 (0.80–0.84) | **0.816 (0.796–0.837)** |
| Q(168) for VR | 121.74 | 120.64 |
| Q(168) for CVR | 243.53 | 240.07 |
| r(M,SD) drug / placebo | 0.55 / 0.52 | 0.552 / 0.521 |

Three integers and four statistics. The small residuals come from one place I
can name: they collapsed dose arms by hand in the CSV and then collapsed drugs
in the script, whereas `p01` collapses all antidepressant arms in one pass.
**Averaging standard deviations is not associative under regrouping**, so the
two orders cannot agree exactly.

**One number does not reconcile.** The abstract says *"163 randomised,
placebo-controlled trials (51 396 patients)"*. Table 1 says 169 trials, and
32 650 + 18 746 = 51 396 — the same patients. The reconstruction says 169. The
abstract's k is wrong; nothing downstream depends on it.

## Finding 1 — CVR = 0.82 is the drug's efficacy, not a fact about variance

The authors report it as a second, independent result and then write:

> *"There is no immediately plausible explanation for this finding, given that
> baseline severity does not predict differential treatment effects."*

There is one. Both statistics carry the same Nakagawa small-sample correction,
and it cancels, so per trial

    lnCVR_i - lnVR_i = ln(m_PL,i / m_AD,i)      exactly

Measured across all 169 trials, the largest absolute deviation from that
identity is **2.8e-16** — machine epsilon. CVR is VR divided by the ratio of
mean symptom reductions, and nothing else.

The drug reduces symptoms more than placebo in 159 of 169 trials (94.1%). On
HAMD17 the reductions are 10.99 vs 9.11 points, a ratio of 1.207 whose
reciprocal is **0.829**. Their own Table 1 gives VR/CVR = 1.01/0.82 = 1.2317;
the n-weighted mean-change ratio is 1.2286.

It predicts their subgroups too, which is the test that matters because it was
made before looking:

| group | VR | CVR | CVR/VR | m_PL/m_AD |
|---|---|---|---|---|
| all | 1.006 | 0.816 | 0.811 | 0.777 |
| SSRI | 1.016 | 0.819 | 0.806 | 0.750 |
| SNRI | 1.005 | 0.816 | 0.812 | 0.800 |
| atypical | 1.001 | 0.833 | 0.833 | 0.822 |
| **tricyclic** | 1.000 | **0.614** | **0.613** | **0.603** |

The tricyclic row is the one that looks like a finding in the paper (CVR 0.65,
much lower than the rest) and it is entirely the larger drug–placebo mean gap in
old tricyclic trials. **A statistic that equals another statistic divided by the
treatment effect will always look like a treatment effect.**

Their code contains the tell, in a comment: *"for the calculations of CVR, it
was necessary to use the absolute values of the pre-post differences."* A
coefficient of variation divides by a mean, and it means something only when
that mean is a magnitude on a ratio scale. A pre–post **change** is not: its
zero is "no change", not "no symptoms", and it can take either sign. Needing
`abs()` to make the statistic computable is the signal that the scale does not
support it.

## Finding 1b — the same statistic, the same drugs, on both sides of 1

The identity makes a prediction that their own supplement can test, and I wrote
it down before opening the file (`p09`, top of the docstring).

In the main analysis the reported "mean" is a pre-post **change**, and the drug
arm changes *more*, so `m_AD > m_PL` and CVR must come out below VR. Their
online supplementary table 1 runs the identical analysis on the 84 trials that
reported an **endpoint** score instead. An endpoint score is a level: the drug
arm's is the *smaller* one, because the drug works. So the identity requires
CVR to come out **above** VR there.

| | trials | VR | CVR |
|---|---|---|---|
| change scores (their Table 1) | 169 | 1.01 | **0.82** |
| endpoint scores (their supplement) | 84 | 0.98 | **1.15** |
| tricyclics, change | 11 | 1.04 | **0.65** |
| tricyclics, endpoint | 13 | 0.93 | **1.37** |

Rebuilt from upstream and reproduced to four significant figures: 84 trials,
10 879 drug and 7 346 placebo patients, VR 0.9803 [0.9634, 0.9975] against their
0.98, CVR 1.1494 [1.1146, 1.1853] against their 1.15. The identity holds to
2.2e-16 on this subset too, and the drug arm has the smaller endpoint mean in
77 of 84 trials.

**VR is stable across the two conventions. CVR crosses 1.** For tricyclics the
two values differ by a factor of 2.1 — same drugs, same patients, same authors,
same statistic. The only thing that changed is which of two mathematically
equivalent summaries a trial happened to publish.

The authors interpret the 0.82 substantively — *"the increase of variance
associated with increasing larger pre–post differences was stronger in the
placebo than the AD groups. There is no immediately plausible explanation for
this finding"* — and the 1.15, which says the opposite, sits in a supplement and
is not discussed.

**And this is not fixed by using a better scale.** An endpoint score does have a
meaningful zero, so a coefficient of variation is at least computable on it. It
does not help: a CV *ratio between arms* still carries the mean ratio, and the
mean ratio is the treatment effect. CVR is not the right object for a two-arm
comparison on any scale. What it measures is efficacy, in whichever direction
the outcome happens to be signed.

## Finding 2 — the stated reason for computing CVR does not survive two checks

Their justification is one sentence: *"Because the pre–post differences were
significantly associated with their SD, we repeated the analysis using the
coefficient of the variance ratio."* The evidence offered is r(M,SD) = 0.55
across trials.

**Check 1 — is it within-scale?** The corpus mixes HAMD17 (k=71), HAMD21 (52),
MADRS (24), HAMD24 (12) and four more. These have different ranges, so trials on
a longer scale have both larger means and larger SDs, for reasons that have
nothing to do with the drug. Within scale:

    all 169 trials       r = +0.552 (drug), +0.521 (placebo)
    within HAMD17 (71)   r = +0.045
    within HAMD21 (52)   r = +0.311
    within MADRS  (24)   r = -0.136
    within HAMD24 (12)   r = +0.421
    within-scale pooled  r = +0.135  (Fisher z, n-3 weights)

**75% of the correlation they cite is between-scale mixing.**

**Check 2 — is it even the right correlation?** An across-trial correlation
cannot license a within-trial, between-arm division. The relevant question is:
*inside one trial, does the arm with the bigger mean change have the bigger SD?*

    r( ln(m_AD/m_PL), ln(SD_AD/SD_PL) ) = +0.110,  p = 0.154,  k = 169

Not significant, and small. The correction was chosen on a correlation that is
mostly an artifact of scale mixing and is not the correlation the correction
addresses.

## Finding 3 — how much correction the data actually support: lambda = 0.098

Put the two statistics on one continuous scale. Model the arm SD as a power of
the arm mean:

    SD ∝ mean^lambda      =>      lnVR = lambda * ln(m_AD/m_PL)

    lambda = 0  additive homogeneity        -> lnVR is the right statistic
    lambda = 1  multiplicative homogeneity  -> lnCVR is the right statistic

lnVR assumes 0 and lnCVR assumes 1. Nobody estimates it. It is estimable, but
**the raw regression slope is not lambda** — the same regression run on
simulated worlds where lambda is 0 and 1 by construction returns +0.0020 and
+0.5170, so the estimator's own scale is 0.515, not 1. Rescaling against those
two anchors (`p08`, 4000 trial-level bootstrap resamples):

    lambda = 0.098   [-0.024, 0.241]

    lnVR's  assumption (0) is INSIDE the interval
    lnCVR's assumption (1) is far outside

    VR  as published (lambda = 0 assumed)  1.006
    CVR as published (lambda = 1 assumed)  0.782   [their pooled value 0.816]
    VR at the estimated lambda             0.981   [0.947, 1.012]

**The published CVR applies 10.2 times the correction the corpus supports.**

This is the third corpus on which I have run this adjudication
(antidepressants/Munkholm, non-clinical mindfulness/Galante, now
antidepressants/Cipriani) and the third to come back additive. **Not three
independent corpora, and I nearly wrote that they were**: the section below on
Dube2010 shows the Munkholm and Cipriani trial sets overlap. Galante is
genuinely independent — different intervention, non-clinical population,
different outcome scales — so the honest count is two independent replications,
not three. `p07` re-ran the
null with a bounded generator — a change score cannot exceed the patient's own
baseline, and the floor compresses the SD of whichever arm improves more, which
is a mean–SD coupling with a definite sign — and the additive null moved to
−0.046 while the multiplicative null stayed at +0.524. The observed +0.061 sits
between them and close to additive under either generator.

## Finding 4 — D, the identified quantity, and the fact that estimating it is not free

`senn2016-mastering-variation` shows a parallel-group trial identifies only the
between-treatment component. What aggregate data DO fix is

    D = sigma_AT^2 - sigma_PL^2 = sigma_TE^2 + 2 rho sigma_PL sigma_TE

unbiased, sampling distribution known, legitimately negative, no square root, no
branch choice, no deletion of trials. **D carries units**, so it may only be
pooled within a measurement scale — this corpus mixes seven.

### The estimator is biased, and I had to find that before reporting anything

`p04A` fed the obvious estimator worlds whose answer is known. From a corpus
with **D = 0 exactly by construction**, the naive inverse-variance pooling
returned **+0.514** with 90.2% coverage of a nominal 95% interval. That bias is
the same size as the number I was about to report.

Mechanism: the weight `v_i = 2 s1^4/(n1-1) + 2 s2^4/(n2-1)` is a function of the
same random quantities as the numerator `s1^2 - s2^2`. In this corpus placebo
arms are the smaller ones (18 746 vs 32 650; smaller in 116 of 169 trials), so
the `s2^4/(n2-1)` term dominates `v`: a trial that draws a large placebo SD gets
a large **negative** d and a large v, and is down-weighted. Negative deviations
are shrunk harder than positive ones and the pooled estimate rides up.

Three predictions, all confirmed (`p05`, 500 replicates each, true D = 0):

| | bias | coverage |
|---|---|---|
| as observed (n_PL < n_AD) | +0.585 | 90.4% |
| P1: arms forced to equal n | **+0.064** | 95.6% |
| P2: arms swapped | **−0.567** | 90.8% |
| P3: weight from the across-arm pooled variance | **−0.003** | 96.6% |

The fix is to build the weight from a quantity that does not contain the
difference: `v_i = 2 s_p^4 (1/(n1-1) + 1/(n2-1))` with `s_p^2` the across-arm
pooled variance. Verified at D = 0, +5 and −5: bias −0.003, −0.070, +0.125;
coverage 96.6%, 96.6%, 95.0%. A common-scale weight also works (bias +0.054)
but is less efficient (SD 1.119 vs 0.787).

**This generalises past this paper.** Any meta-analysis of a *difference of
variances* — or of anything whose sampling variance is a steep function of the
estimate — has this problem, and it is invisible because the number looks
reasonable. It is the same shape as the coupling artifact I found in
`mccutcheon2022`: a quantity appearing on both sides of its own estimator.

### The number

HAMD17, k = 71 trials, 13 132 drug and 8 147 placebo patients, corrected
estimator:

    D = +0.444  [-1.748, +2.637]  HAMD points^2,  I2 = 0%, tau2 = 0

Other scales, same estimator: HAMD21 +2.790 [−1.549, +7.128] (k=52),
MADRS +0.535 [−5.012, +6.082] (k=24). All contain zero. The unit-mixed pool
(+1.188 [−0.477, +2.854]) is printed only to show that mixing units moves the
answer by more than any arm difference does.

For comparison, the same quantity on Munkholm's independent corpus
(`mccutcheon2022`, m11, recomputed in the same session): HAMD17
**−0.540 [−2.067, +0.986]**. Opposite sign, both straddling zero, intervals
overlapping over most of their length. **Two corpora, one conclusion: D is not
distinguishable from zero.**

> **Written first, then corrected, and left visible.** This paragraph originally
> said the Munkholm number "was computed with the naive estimator now shown
> biased, so the two are not yet comparable". Half right. Recomputing it (m11)
> found the weight **immaterial there**: that corpus's arms are balanced (drug
> arm smaller in 169 of 344 comparisons, medians 102 vs 101), so the p05 bias
> mechanism, which needs an arm-size asymmetry, barely fires — calibrated bias
> +0.054 naive against +0.044 pooled. What actually made the old
> −0.384 [−1.636, +0.868] unusable is that it pooled squared HAMD17, HAMD21,
> HAMD24 and MADRS points into one number. **The unit field literally read
> "squared HAMD/MADRS points" and I wrote it anyway.** Marked `superseded` in
> `mccutcheon2022#c6` with a forwarding address. Diagnosing the wrong defect
> and being right about the conclusion is not the same as being right.

### What D bounds, with rho as a visible knob

    sigma_TE = -rho sigma_PL + sqrt(rho^2 sigma_PL^2 + D)

At the HAMD17 D above and a median placebo-arm SD of 7.76 points, against a mean
drug-minus-placebo reduction of 1.88 points:

| rho | sigma_TE (points), point [95% from D] | as a multiple of the 1.88-pt effect |
|---|---|---|
| 0.00 | 0.67 [0.00, 1.62] | 0.35 [0.00, 0.86] |
| −0.10 | 1.80 [0.00, 2.58] | 0.96 [0.00, 1.37] |
| −0.21 | 3.39 [2.58, 3.93] | 1.80 [1.37, 2.09] |
| −0.32 | 5.05 [4.59, 5.45] | 2.69 [2.44, 2.90] |
| −0.62 | 9.67 [9.44, 9.89] | 5.14 [5.02, 5.26] |

## Finding 5 — their Figure 1 in closed form

Their simulation grid asks: how many "benefiters", of what size, are compatible
with the observed VR? For a two-point mixture in which a fraction p receive
delta extra points over the rest, `sigma_TE^2 = p(1-p) delta^2`, so at rho = 0
the entire figure is one inequality:

    p (1 - p) delta^2  <=  D_upper = 2.637

    p = 0.05  ->  delta <= 7.45 HAMD points
    p = 0.10  ->  delta <= 5.41
    p = 0.20  ->  delta <= 4.06
    p = 0.50  ->  delta <= 3.25

Their figure's own reading is *"if there are 10% benefiters, as defined with 6
HDRS points difference to average placebo response, the VR is within the CI"*.
The closed form gives 5.41 at p = 0.10. **Two different routes to the same
number**, one a simulation over a grid and one a line of algebra — which is
worth more than either alone, because it means the conclusion does not depend on
their simulation's parameter choices.

And it makes the hidden knob visible. The same bound, at p = 10%:

    rho =  0.00  ->  delta <=  5.41 points
    rho = -0.10  ->  delta <=  8.59
    rho = -0.21  ->  delta <= 13.10
    rho = -0.32  ->  delta <= 18.17      (McCutcheon et al.'s value)
    rho = -0.62  ->  delta <= 32.96

HAMD17 runs 0–52 and 6 points is "minimally improved". **Their conclusion —
"the scope for personalised treatment with antidepressants seems to be
limited" — is carried entirely by rho = 0, which they never state and no
parallel-group trial can check.** That is not a criticism of the arithmetic;
it is the boundary of what the design permits.

## What I tried to break and could not

**The multi-arm aggregation is wrong and it does not matter.** Their rule
(`cipriani-variance-data-generation-2.r` line 163) collapses several drug arms
with the unweighted **mean of the arm SDs**. That is downward-biased twice over
— Jensen, and the omission of the between-arm mean spread — and it applies to
84 of 169 trials while the placebo side is always a single arm, so any bias is
one-sided and in the direction of their conclusion. I expected this to matter.

It does not. Their SD is the smaller one in 50 of 84 multi-arm trials (median
ratio 0.9994, worst case 0.9230), and the pooled VR moves from 1.0060 [0.9929,
1.0192] to **1.0077** [0.9946, 1.0210] under correct mixture pooling. The reason
is that dose arms of one drug have nearly identical means, so the between-arm
term is near zero. **Recorded as a null finding**, with the same care as the
others, so nobody re-derives the objection and stops before measuring it.

## The trial that runs this literature

`m12` asked which single trial each pooled D depends on. On the HAMD17 subsets
the answer is reassuring — the worst single deletion moves this paper's D by
0.32 against a CI half-width of 2.19 (14%), and Munkholm's by 0.28 against 1.53
(18%). Both subsets describe a corpus.

HAMD21 does not. In **both** corpora the most influential trial is the same one:
**Dube2010, NCT00420004**, drug SD 8.8 and placebo SD 3.3 on HAMD21, n 54 vs
122. Deleting it moves the HAMD21 D by −3.18 here (73% of the CI half-width,
and it flips the sign) and by −1.92 in Munkholm's corpus. A placebo-arm change
SD of 3.3 points, a third of every neighbouring trial's, is not a plausible
measurement.

Plöderl and Hengartner know about it. Their Table 1 footnote reads: *"This
result was caused by an outlier (Study Dube 2010, NCT00420004), and after
removing this study, the heterogeneity index was Q(df=87)=54.54, p=0.99."* They
found it through the heterogeneity index of the SSRI VR meta-analysis; I found
it through leave-one-out on a different statistic in a different corpus.

**The point is not the trial, it is what it says about independence.** Munkholm
et al. and Plöderl & Hengartner assembled their corpora from different sources
and I have been treating their agreement as replication. They share trials,
because both draw on the same registries and the same FDA submissions. Agreement
between two meta-analyses of overlapping trial sets is worth much less than it
looks, and this is the first hard evidence of the overlap in this area:
**one anomalous trial, two corpora, two independent detections.**

## A limit of validating an estimator by simulation

`m12` also tried to break my own fix. The concern was real: the naive weight's
bias is, seen from the other side, an automatic outlier guard — `v` grows as
`s^4`, so a trial with a huge variance in either arm is down-weighted for free,
and the pooled-variance weight gives that up. The contaminated-null simulation
was built to catch it: 129 trials with D = 0, one of them given a true SD ratio
up to 2.7, 300 replicates per cell.

**It caught nothing.** Both estimators stayed near zero at every contamination
level (naive +0.19, pooled +0.04 at c = 2.7). And yet on the real HAMD21 data
the two differ by 1.46 and one trial explains all of it.

The simulation is not wrong; it answers a different question. It validates the
ESTIMATOR against a corpus I generated, whose only departure from the null is
the one I injected. The real corpus has structure I did not model — the
weightings even disagree about `tau^2` there, 0 against 12.6. **Simulation
validates an estimator; only leave-one-out validates a corpus.** Both are
now in `statlib` (`var_diff`, `max_loo_influence`) and the docstring says to
report them together.

## Reading, overall

The paper's central claim — VR ≈ 1 in a large, well-sourced antidepressant
corpus — reproduces exactly and I accept it. Its secondary claim, the CVR
result, is not a result: it is the treatment effect, restated in a denominator,
and the paper's own admission that it has no explanation is the strongest
evidence that nobody checked what the statistic was made of.

The deeper point is the one this area keeps arriving at from different
directions. The corpus is large (51 396 patients), the reproduction is exact,
the estimator is unbiased once fixed, and the answer still moves by a factor of
eight on a parameter nobody measured. **Precision and identification are
different things, and this literature keeps buying the first while reporting the
second.**

## TODO carried out of this record

1. ~~**Recompute Munkholm's D with the corrected weight.**~~ **DONE, same
   session** (`mccutcheon2022/reanalysis/m11_D_reweighted.py`), and the defect
   was the units rather than the weight — see the correction box above. The
   −0.384 is now marked `superseded` with a forwarding address, and
   `kb.py stale-claims` found every prose copy of it in three files.
2. **`statlib` should carry `d_var` with the pooled-variance weight**, so the
   next person to pool a difference of variances does not repeat this.
3. The remaining four psychiatric variability meta-analyses (antipsychotics /
   Winkelbeiner, brain stimulation, PTSD psychotherapy, depression
   psychotherapy) still have no D.
4. `lambda` should be reported alongside every VR in this literature. It costs
   one regression and two simulated worlds and it decides which statistic is
   the right one.
