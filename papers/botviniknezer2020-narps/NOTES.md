# NARPS: 70 teams, one fMRI dataset, and what the headline statistic cannot see

Botvinik-Nezer et al., *Nature* 582:84-88 (2020). Read 2026-09-09 from the **submitted
version** (Zenodo 5118420, sha256 f31a08a0...52592) plus the published Extended Data
Table 1 and the freely-downloadable Supplementary Information; the publisher's own PDF
link is a login wall (see section 10). All numbers below were computed here from NARPS's
own deposited derived data (Zenodo 3709275, `results.tgz`, 52.3 MB, sha256
21e07696...3abce1), not transcribed from the paper, except where I say I am reproducing a
published figure to check the deposit.

**Why this paper and not another.** It is an out-of-domain test of something this corpus
already claims. `maria2026-analytic-variability-reanalysis`, built on Breznau et al.'s
sociology corpus, concluded: *"analytic decisions determine how precisely an analysis
answers the question, and say nothing about what the answer is."* NARPS is 70 teams,
9 hypotheses, fMRI - a third field sharing only the design. Four predictions were written
into `.claude/memory/maria/SESSION_2026-09-09_plan.md` before any NARPS number was
fetched, and two more before the deposit was opened. Two hold, one holds partially, one
fails, and **one of the new ones refutes the through-line's strong form**, which is the
most useful thing here.

---

## 1. The headline statistic is a function of the column margins and nothing else

NARPS reports: *"on average across the 9 hypotheses, 20% of teams reported a result that
differs from the majority of teams... midway between complete consistency and completely
random results."*

That 20% is exactly `mean_h min(p_h, 1-p_h)` over the nine marginal yes-rates. Computed
from the deposit: **0.2000**. Permute each hypothesis column independently - which fixes
every rate in Table 1 and destroys every trace of which team dissented where - and it is
**0.2000 again**. Verified, not asserted.

So the statistic is blind to the distinction that decides what the finding means:

- a world where dissent is scattered, each team unlucky now and then - *idiosyncratic
  noise, nothing to fix*;
- a world where a stable minority of pipelines dissents systematically - *an attributable,
  correctable property of pipelines*.

**It is the second world.** Variance of per-team yes-counts is **2.26x** the
column-permutation null (obs 3.007, null mean 1.332, z = 7.98, p < 1e-4, 100,000
permutations). The nine hypotheses are not independent - H1/H3 and H2/H4 are the *same*
statistical map read in two ROIs, H7/H8/H9 are all amygdala-loss - so the test was
repeated on map-disjoint subsets: 1.82 and 2.32 on the two seven-hypothesis subsets,
**1.38 (p = 0.009) on the four hypotheses that share no map and exclude the amygdala.**

In readable units, from a logit-normal random-intercept MLE fitted jointly with the nine
hypothesis effects (60-point Gauss-Hermite; recovery checked against simulated data at
known sigma: 0.0 -> 0.00, 0.5 -> 0.57 +/- 0.15, 1.0 -> 1.08 +/- 0.11, so a small upward
bias at this n):

| subset | k | sigma (logit) | latent ICC | LRT chi2, 1 df |
|---|---|---|---|---|
| all nine | 9 | 1.32 | 0.345 | 39.8 |
| map-disjoint A (1,2,5,6,7,8,9) | 7 | 1.27 | 0.329 | 20.6 |
| map-disjoint, no amygdala (1,2,5,6) | 4 | **0.97** | **0.222** | 6.1 |

The conservative number is the last row. **A team one SD above the mean propensity has
13.9x the odds of reporting significance of a team one SD below**, on identical data.

And the concentration, which is the part I would put in an abstract:

> **126 dissenting decisions. 24.3% of teams never dissent at all - twice the 12.1%
> the permutation null gives (p = 0.0002) - and the most dissenting quartile carries
> 57.1% of the dissent against a null of 47.2% (p < 5e-5).**

The 20% is not seventy teams each being occasionally unlucky. It is a minority of
pipelines that answer "yes" more readily than the rest, on every question.

## 2. What the trait is: how much the pipeline declares, not what it estimated

Team-level Spearman against the team's yes-count out of 9:

| team-level quantity | side | rho | p | n |
|---|---|---|---|---|
| log median suprathreshold voxels | precision | **+0.387** | 0.0017 | 63 |
| estimated smoothness (FWHM) | precision | +0.282 | 0.024 | 64 |
| log resels | precision | +0.283 | 0.024 | 64 |
| **median Spearman r with the consensus map** | **answer** | **+0.065** | **0.61** | 64 |
| self-rated confidence | - | +0.039 | 0.75 | 70 |
| applied smoothing kernel | choice | +0.049 | 0.68 | 70 |

Out-of-fold (10-fold, 25 repeats, ridge): the precision block predicts the yes-count at
**R2 = 0.111 +/- 0.024** (permuted -0.046); the answer variable alone at
**-0.030 +/- 0.011**, i.e. nothing. NARPS's own mixed logistic gives delta pseudo-R2 of
0.037 (smoothness) + 0.040 (software) + 0.024 (correction) ~ 0.10 for the same team-level
factors - two different estimators, two different designs, the same 0.11. That agreement
is the reason I believe the number.

**The Breznau design, transplanted exactly.** Predictors: only the *choices* a team made
(software package, applied smoothing, fMRIPrep, movement modelling, correction family,
statistic type, ROI-definition style, n kept) - 39 dummies, never a property of the image
the team produced. Outcomes: two precision-side, one answer-side, one conclusion-side.

| outcome | side | CV R2 | permuted |
|---|---|---|---|
| log(resels) | precision | **+0.507 +/- 0.046** | -0.048 |
| log(median suprathreshold voxels) | precision | +0.120 +/- 0.048 | -0.019 |
| median r with consensus map | **answer** | **-0.073 +/- 0.033** | -0.109 |
| yes-count out of 9 | conclusion | -0.103 +/- 0.049 | -0.036 |

Compare `maria2026-analytic-variability-reanalysis` on CRI: log SE **+0.194 +/- 0.024**,
point estimate **-0.005**. Same shape, in a field sharing nothing but the design.

One honest wrinkle: on all 70 teams the precision block gives -0.009, not +0.111. Six
teams have no smoothness estimate and enter as imputed medians; six rows of noise out of
seventy is enough to erase an R2 of 0.11. Both numbers are in the record.

## 3. Where the disagreement lives: the estimate and the conclusion are nearly decoupled

For each hypothesis, every pair of teams gives two things at once - the Spearman
correlation between their unthresholded maps, and whether they gave the same yes/no.
14,112 pairs over 7 hypotheses.

First, a check that produced nothing and is reported anyway because it looked like a
finding: raw pairwise agreement minus `p^2 + (1-p)^2` is -0.007 to -0.001 for every
hypothesis. That is the finite-population correction
`[k(k-1)+(n-k)(n-k-1)]/[n(n-1)]` exactly, reproduced to three decimals. It is mechanical
and carries zero information.

The informative statistic is the AUC of map-correlation predicting decision agreement,
with a null that permutes which team holds which decision - leaving the whole correlation
matrix and the published marginal untouched. 20,000 permutations per hypothesis:

| hyp | p(yes) | AUC | permutation p | disagreement among pairs with r >= 0.8 | null |
|---|---|---|---|---|---|
| 1 | 0.344 | 0.462 | 0.064 | **53.4%** (n=294) | 45.8% [35.4, 52.7] |
| 2 | 0.219 | 0.574 | 0.147 | 39.0% (n=251) | 34.7% [19.5, 46.6] |
| 5 | 0.844 | **0.762** | **0.0002** | 5.2% (n=368) | 26.8% [13.3, 38.6] |
| 6 | 0.328 | 0.590 | 0.010 | 42.2% (n=45) | 44.9% [24.4, 60.0] |
| 7 | 0.047 | 0.570 | 0.508 | 1.2% (n=405) | 9.0% |
| 8 | 0.047 | 0.710 | 0.061 | 5.6% (n=54) | 9.1% |
| 9 | 0.031 | 0.397 | 0.489 | 3.2% (n=124) | 6.1% |

With Bonferroni over seven hypotheses (alpha 0.0071) **only H5 survives** - the one
hypothesis where 84% of teams agree. For the five ambiguous ones, how similar two teams'
whole-brain maps are tells you essentially nothing about whether they will reach the same
conclusion; on H1 the pairs whose maps correlate at a median r of 0.88 disagree **53.4%**
of the time, slightly *more* than the marginals alone predict.

NARPS says this in prose - *"teams with highly correlated underlying statistical maps
nonetheless reported highly divergent hypothesis outcomes"*. The number, and the null it
needs, are new here.

## 4. Thresholding sets the LEVEL; the data set the RANKING

The deposit contains NARPS's own re-thresholding of every team's unthresholded map with
one common rule and one common ROI, in two variants. NARPS reports that the *dispersion*
across teams stays similar. It does not report what happens to the *level* - which is the
number a reader of any single fMRI paper actually consumes.

| hypothesis | as reported | common p<0.001, k>10 | common FDR |
|---|---|---|---|
| 1 | 0.371 | 0.734 | 0.594 |
| 2 | 0.214 | 0.391 | **0.766** |
| 4 | 0.329 | 0.234 | 0.609 |
| 5 | 0.843 | 0.906 | 0.859 |
| 6 | 0.329 | 0.563 | 0.359 |
| 8 | 0.057 | 0.016 | 0.125 |

- Spearman between the reported rates and the common-threshold rates: **0.919** and
  **0.783**. The ordering of the hypotheses is nearly invariant.
- Mean absolute shift in the rate: **0.118** and **0.160**; maximum **0.551** (H2:
  0.214 -> 0.766).
- Hypotheses on which a *majority* of teams find significance: **1 of 9 as reported,
  3 of 9, then 4 of 9** - on the same maps, changing only the thresholding rule.

> Which hypotheses look better supported is a property of the data. How many are
> "supported" is a property of the correction rule, and it moves by a factor of four.

## 5. The strong form of my own through-line is wrong, and NARPS is what refutes it

Sections 2-4 all support "decisions determine precision". So does everything I wrote on
CRI. The test that goes the other way is a pairwise one, which uses n(n-1)/2 = 2,016 pairs
rather than 64 units: build a team-by-team **choice distance** (Gower over the coded
pipeline table) and a team-by-team **map distance** (1 - Spearman r, NARPS's own
matrices), and Mantel-test them, permuting team labels.

| relation | Mantel rho | null 95th | p |
|---|---|---|---|
| choices ~ precision (abs diff of log resels) | +0.252 | 0.084 | 0.0001 |
| **choices ~ map distance** | **+0.193** | 0.106 | **0.0021** |
| choices ~ map distance, **partialling out precision** | **+0.142** | 0.104 | **0.0117** |
| choices ~ conclusion (abs diff of yes-count) | +0.007 | 0.072 | 0.41 |
| map ~ conclusion | +0.140 | 0.104 | 0.017 |

Per hypothesis, the choices-vs-map association is significant on 6 of 7 (rho 0.12-0.24).
Only about a quarter of it runs through smoothness - two maps produced with similar
smoothing are more correlated *for that reason alone*, and removing that channel leaves
0.142 standing.

> **Analytic choices in fMRI change the estimate itself, not only its precision.**
> "Decisions determine precision and say nothing about the answer" is not supportable as
> stated. What survives is a comparison of magnitudes: on one common scale, choices are
> coupled to precision at 0.25, to the estimate at 0.19 (0.14 net of smoothness), and to
> the binary conclusion at 0.01.

The last row is the one I did not expect. **The coded choices predict the image and its
precision, and do not predict the team's conclusion at all** - while an *image-derived*
quantity, the median suprathreshold voxel count, predicts it at rho = 0.387. The chain
choices -> precision -> conclusion is consistent with both (0.71 x 0.28 ~ 0.20 induced
correlation, i.e. R2 ~ 0.04, invisible out-of-fold at n=70), so this is a power limit, not
an orthogonality. But it has a practical edge: **a COBIDAS-style methods table lets you
reconstruct the pipeline and not the conclusion. One image diagnostic does better than the
whole table.**

## 6. Then I turned the new instrument on my own old corpus, and caught myself twice

If a Mantel test can see what a CV R2 misses, my published CRI number - *"decisions ->
the point estimate, R2 = -0.005"*, read as "nothing" - deserved re-testing. Prediction
frozen first (session plan, third freeze): I expected CRI to show 0.05-0.15.

**First run said rho = +0.145, p = 0.005 at model level, and 0.20 within each dependent
variable. It was wrong, and the fault was mine.** The model-level null was supposed to
permute whole teams so models stay with their team. It does that only when teams are the
same size. CRI teams run from **1 to 112 models**. Measured directly: under that null only
**46.1%** of within-team pairs remain within-team. The null half-destroys the structure it
exists to preserve, and it inflates significance. **All model-level CRI numbers are
withdrawn** (`artifacts/a10c_block_null_bug.json` records the measurement).

Redone correctly - one row per team within each DV, free permutation of teams, the same
design as NARPS:

| CRI, pooled over 6 DVs, 48 common teams | Mantel rho | null 95th | p |
|---|---|---|---|
| choices ~ estimate | +0.120 | 0.169 | 0.118 |
| choices ~ log SE | +0.140 | 0.141 | 0.051 |

**Second catch: neither of those is a zero, and neither is a detection.** Calibrated by
injection - build a response with a controlled association to the choice distances, sweep
the strength, run the real test 200-300 times at each:

| corpus | n | false-positive rate at zero signal | rho reaching 80% power |
|---|---|---|---|
| NARPS | 64 teams | 0.070 | **0.228** |
| CRI (one DV) | 71 teams | 0.063 | **0.211** |

Power at an observed rho of 0.10 is 0.36; at 0.13, 0.57. **CRI's +0.120 sits at roughly
half power, so p = 0.118 is exactly what one should expect if CRI's true association were
the same size as the one NARPS detects. The two corpora are not shown to differ.** What is
established is that in *at least one* many-analysts corpus the choices demonstrably carry
information about the estimate. My CRI "-0.005, i.e. nothing" must be restated as a bound:
*not detectable, and this design cannot see below rho ~ 0.21 in pairwise terms.*

And a limit of the instrument itself, which cuts against my own conclusion in section 5:
when the injected signal is a *random combination of all* choice indicators rather than
the dominant direction, power collapses - at a strength where the 1-D injection gives
rho ~ 0.23 and 99% power, the multi-directional injection gives rho ~ 0.04 and 14%.
**A Mantel test is sensitive to association along the dominant axis of choice variation
and nearly blind to diffuse association.** So the true choices-estimate coupling is
probably larger than 0.19, not smaller - which strengthens the refutation in section 5 and
weakens any claim that CRI's is small.

## 7. Analysts do not know how idiosyncratic they are

Each team rated, per hypothesis: *"How confident are you about this result?"* and *"How
similar do you think your result is to the other analysis teams?"*, 1-10. NARPS's
supplement relates both to the team's own binary outcome. It does not ask whether the
similarity rating is *calibrated* - and the ground truth is in the deposit.

Everything below is rank-transformed **within hypothesis** and tested by permuting whole
teams, because a team contributes nine rows.

| relation | rho | p |
|---|---|---|
| self-rated similarity ~ **actual** median map r with other teams | +0.190 | 0.013 |
| confidence ~ actual median map r | +0.180 | 0.016 |
| confidence ~ self-rated similarity | **+0.670** | <0.0001 |
| self-rated similarity ~ own yes/no (NARPS's own result) | +0.226 | <0.0001 |
| **self-rated similarity ~ agreeing with the majority** | **-0.143** | **0.0006** |
| - excluding H5, the one hypothesis whose majority is "yes" | **-0.195** | <0.0001 |
| confidence ~ agreeing with the majority | -0.071 | 0.060 |
| - excluding H5 | -0.113 | 0.006 |
| similarity ~ agreeing with the **image-based meta-analysis** | +0.048 | 0.21 |
| confidence ~ agreeing with the IBMA | +0.048 | 0.28 |

Read together:

> The two scales are largely one scale. Both are weakly calibrated to the team's actual
> map similarity (rho ~ 0.19). Both are dominated by whether the team found something.
> Net of that, **a team that believes it resembles the others is, if anything, more likely
> to be the outlier** (rho = -0.195 excluding H5), and neither rating carries any
> information about whether the team's conclusion matches the pooled analysis of all
> seventy pipelines.

Mechanism, visible per hypothesis: for the eight hypotheses whose majority is "no", the
dissenters (who said yes) rate themselves *more* similar; for H5, whose majority is "yes",
the dissenters rate themselves far *less* similar (5.27 vs 8.12). The rating tracks *"I
found the effect"*, not *"I resemble my colleagues"*.

**And the majority is not the aggregate.** The study's own image-based meta-analysis finds
the effect on H2, H4, H5 and H6; a majority of individual teams finds it only on H5. On
**three of nine hypotheses the modal pipeline reaches the opposite conclusion from pooling
all of the pipelines.**

## 8. Extended Data Table 1's two rating columns are transposed

Verified, both directions, 9 of 9 rows, in the submitted version *and* in the published
Extended Data Table 1 (a JPEG at `media.springernature.com`, sha256 3b0c16a5...3987c):

- the column headed **"Median confidence level"** is the median of the deposited
  `Similar` variable - 9/9 exact including the MADs;
- the column headed **"Median similarity estimation"** is the median of `Confidence`
  - 9/9 exact.

The deposited `Table1.tsv` emits the columns in the order `medianSimilar, madSimilar,
medianConfidence, madConfidence` while the paper's table heads them confidence-first,
which is the likely origin. **The Supplementary Information is correct**: its quoted means
(similarity 7.40 / 6.29, confidence 7.59 / 6.93 for significant / non-significant results)
reproduce from the deposited columns to four decimals under those labels. So the defect is
confined to the table.

Consequence: small. Nothing in the paper's argument turns on it, but a reader of Extended
Data Table 1 gets the amygdala hypotheses backwards - teams were *more* confident (8) than
they judged themselves similar (7), and the table prints the reverse.

Corrections check (`retrofit/tools/check_updates.py`, both Crossref paths, 2026-09-09):
no correction, retraction or expression of concern registered.

## 9. The prediction markets: three-quarters of the error is one number

NARPS reports rank correlations (team 0.962, non-team 0.553), a Wilcoxon test that both
markets **overestimated**, and mean absolute error (0.323, 0.449). Both MAEs reproduce
exactly from Supplementary Data 1. What is missing is a baseline.

| predictor | MAE | RMSE | bias | Spearman |
|---|---|---|---|---|
| team-members market | 0.323 | 0.375 | **+0.323** | +0.962 |
| non-team market | 0.449 | 0.470 | +0.414 | +0.553 |
| **constant, leave-one-out (each hypothesis predicted by the mean of the other eight)** | **0.192** | **0.261** | - | - |
| constant 0.5 | 0.300 | 0.323 | +0.224 | - |

**A hypothesis-blind constant beats both markets on absolute error.** The team market is
0.131 worse than the leave-one-out constant, the non-team market 0.257 worse (Wilcoxon
p = 0.43 and 0.074 - n is 9, and 9 is why the paper is right to say power is limited).

But the decomposition rescues the market, and is the more useful reading:

> **bias^2 is 74% of the team market's MSE and 78% of the non-team market's.** Subtract
> the single constant offset and the team market's RMSE falls from 0.375 to **0.191**,
> better than the leave-one-out constant's 0.261.

The team market's ranking is essentially perfect - Spearman 0.962 (permutation p =
0.00025) over nine hypotheses, and **exactly 1.000** on the five that do not share a
statistical map. The non-team market's 0.553 is not distinguishable from chance (p = 0.13).

> Researchers who had analysed the data knew perfectly well *which* hypotheses would come
> out significant more often, and were uniformly wrong about *how often* by 32 percentage
> points. Discrimination excellent, calibration absent. Reporting "overoptimism bias"
> is right; reporting only rank correlation flatters.

One alternative reading I cannot exclude at n=9: traders may have been pricing *"is the
effect real"* rather than *"what fraction of 70 pipelines will say so"*. The team market's
prices correlate +0.78 with the fraction and +0.66 (p = 0.054) with the study's IBMA
verdict. Nine points cannot separate those.

## 10. The article is behind a wall and its data is not

Incidental, and it is a measured extension of `maria2026-shell-or-payload`, which found
that 37.7% of resolving data links do not deliver the resource.

- Unpaywall reports `is_oa: true, oa_status: bronze`, host type **publisher**, version
  **publishedVersion**, `url_for_pdf: https://www.nature.com/articles/s41586-020-2314-9.pdf`.
- That URL answers **303 See Other** to `idp.nature.com/authorize`, and after seven
  redirects returns **HTTP 200, `text/html`, 949,086 bytes**: the article page with
  "Access through your institution" and "This is a preview".
- So an open-access *database* - not just a link checker - asserts a free published PDF
  at a URL that serves a login wall. Briney 2024 counted login walls as resolving; this is
  a step worse, because the assertion is about openness itself.
- Meanwhile every supplementary file, the Extended Data table image, the 1 GB team-results
  deposit and the 52 MB derived-results deposit are all freely downloadable. **The paper
  is the only part of this study that is paywalled.**

Measurable question left open, and it is a small paper: *what fraction of DOIs Unpaywall
labels `bronze` deliver a payload rather than a shell?* The instrument from
`maria2026-shell-or-payload` runs unchanged; only the sampling frame changes.

---

## Predictions, scored

| | prediction (frozen before the data) | outcome |
|---|---|---|
| P1 | maps agree much more than decisions; median pairwise r > 0.4 on most hypotheses | **partial** - the qualitative half holds; median r is 0.281-0.581 and exceeds 0.4 on 4 of 7. The threshold I named was arbitrary and half-missed |
| P2 | variance in *whether* a hypothesis is supported tracks precision/threshold-side choices more than the effect | **held** - 0.387 / 0.282 precision-side vs 0.065 answer-side |
| P3 | IDR/IQR of an across-team quantity exceeds the Gaussian 1.90, as in #fincap (4.07) and CRI (2.79) | **failed, and instructively** - pairwise correlations give 1.59-2.34, straddling 1.90. A correlation is bounded in [-1, 1], so a Gaussian tail reference does not apply to it. My own area file compares two *unbounded* corpora to that reference; applying it to a bounded quantity is invalid and I nearly did |
| P4 | disagreement concentrated at the margin, near 0 or 1 where the signal is strong | **held in direction** - no hypothesis is near 0.5, the maximum is 0.371 |
| A1 | per-team yes-counts over-dispersed relative to a hypothesis-margins-only null | **held, strongly** - 2.26x, and 1.38x on the four map-disjoint non-amygdala hypotheses |
| A2 | choices predict precision far better than the answer | **held for scalars, refuted in its strong form** by the pairwise test: choices ~ map = 0.193, 0.142 net of smoothness |
| A3 (CRI) | the CRI "-0.005" is an underpowered zero; expect 0.05-0.15 | **the point estimate landed at 0.120, inside the predicted range, and is not certifiable** (p = 0.118; 80% power needs 0.21). Predicting a value and being unable to certify it is not the same as being right |

## Open questions

1. The multi-directional injection shows the Mantel test is nearly blind to diffuse
   association. What replaces it? A distance-covariance test, or a permutation test on a
   cross-validated multivariate regression of the map onto the choices - the second needs
   the 1 GB image deposit.
2. The 1 GB `narps_origdata_1.0.tgz` was deliberately not fetched. With it: does the
   team trait survive after re-thresholding every map identically, i.e. is it the
   *threshold* or the *map*? Section 4's table says the level moves; the team-level
   version of that question is unanswered.
3. Whether the same over-dispersion appears in #fincap (Menkveld, 164 teams) - the only
   other corpus here with multiple outcomes per team.
4. Was the Table 1 transposition ever noticed? Nothing was sent to anyone. Both the
   preprint and the published version carry it, six years on.
5. The Unpaywall `bronze` shell rate.

## Reproducing

```sh
cd reanalysis
python mantel_fast.py                 # selftest: matches scipy on observed and permuted
python a1_team_trait.py               # 100k column permutations
python a1b_icc_and_dissent.py         # includes a sigma-recovery selftest, ~6 min
python a1c_sigma_subsets.py
python a2_what_is_the_trait.py
python a2b_breznau_design.py
python a3_map_agreement.py
python a4_threshold_vs_estimate.py
python a4b_auc_null.py                # ~4 min
python a5_mantel.py ; python a6_partial_mantel.py
python a7_self_knowledge.py ; python a7b_ibma_ground_truth.py
python a8_level_vs_ranking.py
python a9_market_scoring.py
python a10c_block_null_bug.py         # measures the defect that withdrew a10/a10b
python a10d_cri_teamlevel_within_dv.py
python a11_mantel_power.py            # ~5 min
```

Data:

```sh
curl -sL -o artifacts/narps_results.tgz \
  https://zenodo.org/api/records/3709275/files/results.tgz/content     # 52.3 MB
mkdir -p artifacts/narps_results
tar xzf artifacts/narps_results.tgz -C artifacts/narps_results
```

`a10*` additionally read `../breznau2022-hidden-universe/data/cri_model_level.csv`,
already in this repository.
