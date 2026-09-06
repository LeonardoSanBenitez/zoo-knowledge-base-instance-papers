# Winkelbeiner & Homan 2019 — the paper this literature descends from, and the bound nobody subtracted

Read 2026-09-06 by maria. `read-and-reanalysed`. Area:
`treatment-effect-heterogeneity`. Scripts `w01`–`w06` in `reanalysis/`.

## Why this one

It is the origin of the psychiatric variability-ratio literature, the paper
`mccutcheon2022` reanalysed, and the template Plöderl & Hengartner followed by
name. It is also the only one of the three whose authors deposited **data, code
and the manuscript source** (https://osf.io/qarvs/, CC-licensed, with a README
that tells you to knit the .Rmd). That standard matters: the other two
antidepressant corpora each cost a rebuild.

And it is the first corpus in this area that is genuinely independent of the
others — different disease, different drugs, different authors, different data
source, no shared trials. The Munkholm and Plöderl corpora share trials (see
`ploderl2019`), so agreement between those two is worth less than it looks.

## Reproduction

    published:            52 RCTs, 15 360 patients, VR = 0.97 (95% CI 0.95–0.99), P = .01
    per study (their pooling):  VR = 0.9710 [0.9483, 0.9942], p = 0.0145, I² = 4%
    per comparison (k = 75):    VR = 0.9680 [0.9458, 0.9907], p = 0.0061, I² = 0%
    counts:                     75 comparisons in 52 studies, 8 550 + 6 810 = 15 360

Exact. Their within-study pooling (`response_do.R:425-429`) uses the correct
√(Σ sd²(n−1)/(N−k)), not the mean of arm SDs that the antidepressant paper used.

The 75 comparisons sit in 52 studies, so I also ran a cluster bootstrap over
studies: VR = 0.9680 [0.9475, 0.9894], cluster SE / naive SE = **0.93**. Slightly
*narrower*, not wider — clustering is not costing anything here, which is worth
recording because it is the opposite of the usual expectation.

## λ: additive again, on the first independent corpus

    observed slope −0.0110;  null at λ=0  −0.0011;  null at λ=1  +0.4277
    λ = −0.023  [−0.147, 0.078]      (4000 trial-level bootstrap resamples)

lnVR's assumption (λ = 0) is inside; lnCVR's (λ = 1) is far outside. Third corpus
to come back additive, and the first that does not share trials with another.
lnVR is the right statistic here and lnCVR would have been badly wrong — which
matters because the antidepressant paper reported both and interpreted the wrong
one.

## D, and a sign that should not be possible

    D = σ_AT² − σ_PL²  =  −27.5 [−45.1, −10.0] PANSS points²   (pooled weight, I² = 0%)
    naive weight:          −28.2 [−45.6, −10.8]
    cluster bootstrap CI:  [−43.3, −10.9]
    max leave-one-out:     +5.0, 28% of the CI half-width (Litman2016)

**The interval excludes zero from below**, and it is not one study, not the
weight, and not the clustering.

That is not an ordinary result. The decomposition this entire literature runs on
is

    D = σ_TE² + 2ρ σ_PL σ_TE

At **ρ = 0** — the assumption behind every "VR near 1 means no heterogeneity"
reading, including this paper's — D = σ_TE², which **cannot be negative**. So a
significantly negative D says the model is wrong somewhere: either ρ < 0, or
something outside the model is compressing the treated arm.

Winkelbeiner & Homan report VR = 0.97 with p = .01 and read it as *"no evidence
that antipsychotic drugs increased the outcome variance."* True, and it
undersells what they found: VR significantly **below** 1 is not merely "no
increase", it is incompatible with their own null model.

## What compresses the treated arm: the bound on the scale

Before claiming anything about ρ, rule out the boring mechanisms. Three were
tested (`w02`, `w03`), and the third is the one that bit.

**A. Randomisation / negative control — PASSES.** The deposit reports baseline
SDs for 38 of 75 comparisons. Run the identical statistic on them:

    BASELINE  VR = 1.0336 [0.9856, 1.0839], p = 0.173
    BASELINE  D  = +8.5 [−12.6, +29.6]
    ENDPOINT on those same 38:  VR = 0.9752, D = −19.2 [−43.7, +5.4]

No deficit at baseline, as randomisation requires. Not an allocation or
extraction artifact.

**B. Multiplicative shrinkage — EXCLUDED, and by the arithmetic, not a p-value.**
If the drug scaled every patient's *score* by k < 1 the treated SD would scale
too. But the outcome is a *change* score, and on change scores the treated arm's
mean is the larger one, so λ = 1 makes the treated arm **more** variable. A
simulated λ = 1 world gives a large positive D. Wrong sign. (`w02` printed
+12 675 for it, which is meaningless — the mean of the per-trial change ratio is
3.45 because some control arms changed by 0.4 points. The sign is the result; the
magnitude was noise, and `w03` says so.)

**C. The floor — NOT excluded, and it is the size of the whole finding.**
PANSS has a hard minimum of 30. A patient cannot improve by more than
`baseline − 30`. The treated arm improves more, so it runs into that bound more
often, and truncation removes variance. Simulate it with each trial's own
baseline SD from the deposit, the same change SD in both arms, and **σ_TE = 0
exactly**:

| assumed baseline mean | D from a world with no heterogeneity | share of the observed −27.5 |
|---|---|---|
| 75 | −30.9 [−47.9, −15.5] | 112% |
| 80 | −24.4 [−39.6, −8.5] | 88% |
| 85 | −17.9 [−32.1, −3.0] | 65% |
| 90 | −13.0 [−28.5, +2.4] | 47% |
| 95 | −9.2 [−27.8, +6.3] | 33% |
| 100 | −6.4 [−23.0, +9.9] | 23% |

**The answer depends on the baseline mean, and the deposit does not record it.**
`data_dictionary` has `sd0tx` and `sd0ct` but no `mu0`. A dataset built to
compare variances omits the one field that decides whether the comparison means
anything.

The fraction of patients actually hitting the bound is small — at a baseline of
90, 4.6% treated against 2.1% control — and that 2.5-point difference produces
half the headline. It does not take much truncation.

## The general form: a shrinkage curve, and a direction that is not a law

The mechanism has one dimensionless parameter (`w04`, `w05`):

    z = (mean headroom − mean improvement) / SD(improvement)

`f(z) = SD(recorded)/SD(true)`, with the headroom itself varying across subjects
by `hd` improvement-SDs:

| z | hd=0 | hd=0.25 | hd=0.5 | hd=1.0 | hd=1.5 | hd=2.0 |
|---|---|---|---|---|---|---|
| 0.5 | 0.744 | 0.747 | 0.761 | 0.839 | 0.997 | **1.208** |
| 1.0 | 0.867 | 0.864 | 0.857 | 0.872 | 0.962 | **1.127** |
| 1.5 | 0.942 | 0.938 | 0.928 | 0.913 | 0.950 | **1.065** |
| 2.0 | 0.981 | 0.978 | 0.968 | 0.948 | 0.954 | **1.025** |
| 2.5 | 0.995 | 0.994 | 0.990 | 0.973 | 0.963 | 1.002 |
| 3.0 | 1.000 | 0.998 | 0.998 | 0.988 | 0.976 | 0.993 |

**Above about 1.5 SDs of headroom dispersion the bound inflates the recorded SD
instead of shrinking it**, because a variable cap adds variance of its own.
"A floor biases variability downward" is a statement about a regime, not a law —
and w04 asserted it as a law before this table existed.

Each corpus with its own measured headroom dispersion (PANSS: baseline SD 11.70
against change SD 20.12, so hd = 0.58):

| corpus | z treated | z control | VR bias | published VR | floor-corrected |
|---|---|---|---|---|---|
| PANSS, baseline 80 | 1.62 | 2.02 | 0.968 | 0.968 | **1.000** |
| PANSS, baseline 90 | 2.12 | 2.51 | 0.985 | 0.968 | **0.983 [0.964, 1.002]** |
| PANSS, baseline 95 | 2.37 | 2.75 | 0.990 | 0.968 | 0.978 [0.958, 0.997] |
| HAMD17 (k=68) | 1.57 | 1.87 | 0.974 | 1.007 | **1.034 [1.022, 1.046]** |

At a baseline PANSS of 90 — the middle of the plausible range for acute
schizophrenia trials — **the floor-corrected interval includes 1**, and the
published significant result does not survive. At 80 the entire effect is the
floor.

## What I got wrong in this thread, twice, and left visible

**w04's closing paragraph was contradicted by w04's own table.** It read: *"the
antipsychotic corpus sits at low headroom and the antidepressant corpus does
not, which is why the same statistic reads 0.97 in one and 1.01 in the other."*
Four lines above it, z_treated is 2.12 for PANSS and **1.57** for HAMD17 — the
antidepressant corpus has *less* headroom. Withdrawn in `w05`. I wrote the
conclusion I wanted while the refutation was on the screen.

**w06's first null was mis-specified and produced a p < 0.001 artifact.** The
within-corpus test regresses lnVR on a predicted per-trial floor bias — but
`z = (baseline − mean change)/SD` contains the same arm SDs as
`lnVR = log(s1/s2)`, so regressor and outcome are coupled by construction. The
first version held the regressor fixed across simulated replicates, which broke
the coupling *in the null only* and manufactured "observed −1.197 against a null
of +0.010, inconsistent with both". Recomputing the regressor inside each
replicate moves the no-floor null to **−2.189**: the whole −1.2 was coupling.

## And the within-corpus test, honestly: no resolving power

With the null fixed, the two anchors are −2.189 (no floor) and −2.677 (floor
only): **separated by 0.488 against a combined noise of 0.932, a ratio of 0.52.**
The design cannot tell the two worlds apart, and rescaling the observation
against them would divide by noise. The script now refuses to print the ratio
and says why.

Why so weak: the predicted biases span 0.111 log units across the corpus while
the per-trial lnVR sampling SD is 0.104. The signal is at the level of one
trial's noise, and 68 trials do not recover it.

**So the floor correction is model-based and this corpus cannot confirm or
refute it.** Wherever the corrected VR is quoted, that has to be said.

## What this leaves

The published claim — antipsychotics do not increase outcome variance — survives
in the sense that VR is certainly not above 1. What does not survive is the
inference drawn from the *direction* of the deviation, and the comparison used to
draw it:

- **The null is not 1.** On a bounded scale with the treated arm improving more,
  the no-heterogeneity null is a few per cent below 1, and how far below depends
  on a baseline mean the deposit does not record.
- **The published deviation from 1 is the same size as that bias.** VR = 0.97
  [0.95, 0.99], p = .01, against a floor-induced 0.968–0.990.
- **A fifth axis of non-identification**, alongside the four already in the area
  file: VR bounds, additive-vs-multiplicative, ρ, C-vs-D. The fifth is **the
  boundedness of the outcome scale**, and unlike ρ it is estimable — it needs one
  field, the baseline mean, which every trial reports and neither deposit kept.

## TODO out of this record

1. The floor correction needs a real interval, not a point estimate with a
   bootstrap on only one of its two inputs. The model uncertainty (truncated
   normal vs whatever the real response distribution is) is not represented at
   all.
2. Get baseline PANSS means for these 52 trials and settle the sweep. They are in
   the papers; the deposit dropped them. Expensive but decisive.
3. Apply the shrinkage correction to the two remaining psychiatric corpora (PTSD
   psychotherapy, depression psychotherapy) once their data are in hand — both
   use bounded scales and both report VR near 1.
4. `statlib` should carry `floor_shrinkage(z, hd)` so the correction is one call
   and the curve is not re-simulated by whoever needs it next.
