<!--kb
id: area:analytic-variability-and-many-analysts
labels: kind:paper-notes, area:analytic-variability-and-many-analysts
triggers: many analysts same data different results; does analytic flexibility change the conclusion; is analyst disagreement idiosyncratic or systematic; nonstandard errors across research teams; do some teams report significant results more often than others; a dispersion statistic computed only from marginals; permutation null that fixes the column margins; mantel test on analyst choices versus results; how much power does a pairwise distance test have; when can I compare IDR over IQR to 1.90; DerSimonian-Laird on a many-analysts corpus; thresholding sets the level not the ranking; do researchers know how idiosyncratic their analysis is; prediction market overestimates replication; forecast discrimination versus calibration; multiverse analysis across research teams; crowdsourced replication initiative reanalysis; NARPS fMRI seventy teams
verified: 2026-09-09
-->

# Analytic variability and many-analysts studies

What happens when independent analysts are handed the same data and the same
hypothesis. Started by maria, 2026-08-12.

Records: `papers/breznau2022-hidden-universe/`, `papers/mathur2023-effect-sizes/`,
`papers/menkveld2024-nonstandard-errors/`,
`papers/maria2026-analytic-variability-reanalysis/`,
`papers/botviniknezer2020-narps/`.
Query them with `python tools/kb.py query --area analytic-variability`.

## The right vocabulary, which finance has and sociology does not

Menkveld et al. 2024 (*J. Finance*, 164 teams) split uncertainty in two and it
is the cleanest framing in the area:

- **standard error** — from the data-generating process. Sampling variation.
  Researchers know about it and account for it.
- **nonstandard error (NSE)** — from the *evidence*-generating process. The
  variation produced by researchers picking different analysis paths.

They measure NSE as the **interquartile range of estimates across teams**,
chosen deliberately because "the distribution of the SD could exhibit fat tails
and thus be prone to outliers."

Both of those — the split, and the robust measure — are what this area needs and
what the sociology side lacks. Breznau et al. report percentages of *variance*;
the first decomposition attempted here returned "sampling error is 102% of the
observed variance", an impossible number caused by exactly the fat tails
Menkveld et al. designed around. They chose the right instrument at the design
stage. **Use NSE and IQR by default in this area.**

## Two quantities that travel between corpora

Nobody had put these two datasets on one scale; they are in different fields and
the citation runs one way only (finance cites sociology, not the reverse).
Applying Menkveld et al.'s own robust recipe, τ = √((IQR/1.349)² − medianSE²),
to both:

| corpus | field | teams | τ / median SE | IDR / IQR |
|---|---|---|---|---|
| #fincap RT-H1 | finance | 164 | **1.72** | **4.07** |
| CRI (Breznau) | sociology | 71 | **1.72** | **2.79** |
| — Gaussian reference | — | any n | — | 1.90 |

**Researcher-induced dispersion is comparable to sampling error, in two fields
sharing nothing but the design.** Agreement to three significant figures is
luck — CRI's ratio runs 0.71 (DerSimonian–Laird) to 3.67 (Paule–Mandel)
depending on the estimator, and the per-DV range is 0.88–2.14 — but the order of
magnitude is the finding.

> **Correction 2026-09-14.** The #fincap 1.72 in this table subtracts a
> sampling-variance term, τ² = (IQR/1.349)² − medianSE², that does not exist in
> a same-data design: all 164 #fincap teams analyse the SAME dataset, so there
> is no independent draw across teams to net out, and τ² comes out **negative
> on 3 of the 6 hypotheses** when computed per-hypothesis rather than for RT-H1
> alone. The direct, defensible ratio is NSE/medianSE without the subtraction:
> **median 1.05 across the six hypotheses (range 0.63–1.98)** — still order-of-
> magnitude "comparable to sampling error", the qualitative finding this table
> exists to make, but the specific 1.72=1.72 coincidence should not be quoted
> as a coincidence worth noting, because one side of it was computed wrong.
> See `menkveld2024-nonstandard-errors#nse_over_median_se_direct`.

**The estimate distribution is heavy-tailed in both.** IDR/IQR is 1.90 for a
Gaussian at *any* sample size (simulated 95% bands: 1.52–2.43 at n=71,
1.79–2.01 at n=1252), so it needs no calibration to compare corpora. Both are
far above it.

> **Caveat added 2026-09-09, because I nearly misused my own statistic.** The
> 1.90 reference is for an *unbounded* Gaussian. Applied to a quantity bounded
> in [−1, 1] it means nothing: the across-team pairwise map correlations in
> NARPS give IDR/IQR of 1.59–2.34, straddling 1.90, and that is a fact about
> the bound, not about tails. **Only compare an IDR/IQR to 1.90 when the
> quantity can in principle run to infinity.** Estimates and standard errors
> qualify; correlations, proportions and probabilities do not.

One nuance available only in CRI, because it has multiple models per team: the
heavy tails live at the **model** level, not the analyst level. One estimate per
team and IDR/IQR falls to 2.08, comfortably inside the Gaussian band. **The
outliers are specifications, not people.**

---

## The through-line, and the sentence in it that turned out to be too strong

The field's headline finding is that analysts do not converge. The reanalysis
here says something more specific and, I think, more useful:

> **Analytic decisions determine how *precisely* an analysis answers the
> question, and say nothing about what the answer is.**

> **CORRECTION 2026-09-09, marked in place.** The second half of that sentence is
> withdrawn. Tested on a third corpus (NARPS, 70 fMRI teams — see the section
> below), the *scalar* half transplants exactly: coded pipeline choices predict
> the precision of the resulting image at out-of-fold R² = 0.507 and the image
> itself at −0.073. But a **pairwise** test on the same data, which uses
> n(n−1)/2 pairs rather than n units, finds a real coupling between choices and
> the estimate: Mantel ρ = 0.193 (p = 0.0021), and **0.142 (p = 0.0117) after
> partialling out the smoothness channel**, so it is not simply a precision
> effect wearing a different hat. Re-run on CRI itself with a correct null it
> gives ρ = 0.120, p = 0.118 — and an injection calibration says that design
> needs ρ ≈ 0.21 for 80% power, so **CRI's "−0.005, i.e. nothing" is a
> non-detection, not an absence, and the two corpora are not shown to differ.**
>
> What survives, and should be quoted instead, is a **ratio with a bound**:
> analytic choices are coupled to precision several times more strongly than to
> the estimate, and to the binary conclusion (in pairwise terms) not at all
> — ρ = 0.252 / 0.193 / 0.007 on one common scale in NARPS. See
> `botviniknezer2020-narps#c6` and `#c8`.

Out-of-fold, cross-validated with folds grouped by team so that no analyst
appears on both sides of the split, the 137 coded decision indicators in the
Crowdsourced Replication Initiative reach **R² = 0.194 ± 0.024 for the log
standard error** (leave-one-team-out 0.205) and **R² = −0.005 ± 0.002 for the
estimate** (permutation nulls −0.002 and −0.001). Researcher survey
characteristics reach −0.028 and −0.003: nothing.

Two obvious deflations were tried and both failed, leaving the finding larger
than it started:

- *"You are just predicting sample size."* No. Sample-composition indicators —
  42 country dummies, 5 survey waves, country count, listwise vs imputation —
  give R² = **−0.012**, i.e. nothing. Modelling choices alone give **0.150**.
  What moves the standard error is the model class: hybrid multilevel (+0.142
  standardised), MLwiN (+0.139), country-year random effects (+0.105) inflate
  it; two-way fixed effects (−0.075) and dichotomising the outcome (−0.074)
  shrink it. **An analyst's choice of model class sets the width of their
  interval, and therefore whether they will report a finding, while leaving the
  point estimate alone.**
- *"Your outcome is your own construction."* No. Breznau et al. also recorded
  what each team concluded *in words*. Out-of-team, those written conclusions
  are predicted at R² = −0.07, −0.08, −0.02 for support / reject / not-testable
  — worse than the base rate. (These are near-constant within a team, so random
  k-fold would have reported a large R² by leakage alone. Grouping the folds by
  team is what makes the number mean anything.)

A conclusion is `estimate / SE` thresholded. So a population of analyses that
agree closely about magnitude and differ by a factor of 36,000 in precision will
*disagree loudly about significance while quietly agreeing about everything
else* — which is exactly the pattern the literature has been arguing about.

That reconciles the two sides of the published exchange without either being
wrong, which is the main reason I believe it.

## The exchange, as it actually stands

| | claim | our assessment |
|---|---|---|
| Breznau et al. 2022 (PNAS) | 73 teams, 1,253 models: 25.4% significant-negative, 57.7% null, 16.9% significant-positive; 95.2% of variance unexplained; the residual is idiosyncratic | core claim **survives two serious attempts to break it**; the variance framing is fragile and Fig. 3 is underpowered |
| Mathur, Covington & VanderWeele 2023 (PNAS letter) | 90% of estimates within ±0.037 SD; population effects within ±0.014; this is variation in *significance*, not in findings | numbers **reproduced**, ±0.014 confirmed by an independent route, but the τ behind it is estimator-fragile by 5× |
| this reanalysis | decisions predict precision, not conclusions | — |

The two published papers are usually cited as a fight. They are not. No number
of Breznau et al. is disputed by Mathur et al.; only the adjective attached to
it. The record uses `cito:qualifies` alongside `cito:critiques` for exactly that
reason, with an `asymmetric_note`, because this is the kind of pair that gets
miscited as a refutation.

## NARPS: the third corpus, and the first with a *joint* structure to look at

`botviniknezer2020-narps` — 70 teams, one fMRI dataset, nine pre-registered
hypotheses, binary yes/no per team per hypothesis, plus every team's
unthresholded whole-brain map. Read in depth 2026-09-09. It is the first corpus
here with **many outcomes per analyst**, which makes a question askable that CRI
and #fincap cannot ask.

**1. The field's headline dispersion statistic is blind to the thing that
matters.** NARPS reports *"on average 20% of teams reported a result that differs
from the majority"*. That number is `mean_h min(p_h, 1-p_h)` over the nine
marginal rates and nothing else: permute each hypothesis column independently and
it is **0.2000 both times**, verified. It is identical whether dissent is
scattered luck or a stable minority of pipelines.

**2. It is a stable minority.** Variance of per-team yes-counts is **2.26x** the
column-permutation null (p < 1e-4, 100k permutations), **1.38x** on the four
hypotheses that share no statistical map (p = 0.009). A logit-normal random
intercept gives sigma = 1.32 (latent ICC 0.345) on all nine, sigma = 0.97
(ICC 0.222) on the map-disjoint four. **A team one SD above the mean propensity
has 13.9x the odds of reporting significance, on identical data.** And the
concentration: **24.3% of teams never dissent at all against a null of 12.1%**,
while the most dissenting quartile carries **57.1%** of the 126 dissenting
decisions.

*Generalisable form, and the reason this belongs in the area file rather than
only in the record:* **a dispersion statistic computed from marginals cannot
distinguish idiosyncratic from systematic variability, and the difference decides
whether the finding is a noise floor or a fixable property of pipelines.** Every
number this area currently quotes — Breznau's 25.4/57.7/16.9, Menkveld's IQR,
the 20% — is of that kind. Ask for the joint structure.

**3. What the trait is: how much the pipeline declares.** Team yes-count against
log median suprathreshold voxels rho = **+0.387** (p = 0.0017); against estimated
smoothness +0.282; against **how much the team's map resembles the consensus,
+0.065 (p = 0.61)**; against the team's own confidence rating, +0.039.

**4. Thresholding sets the LEVEL, the data set the RANKING.** Re-thresholding
every team's map with one common rule (NARPS's own deposited simulation) leaves
the ordering of the nine hypotheses nearly untouched — Spearman 0.919 and
0.783 — and moves the level by up to **0.551** (H2: 21.4% to 76.6% of teams).
The number of hypotheses on which a *majority* of teams find significance goes
**1 -> 3 -> 4 of 9** on identical maps.

**5. Agreement about the estimate barely predicts agreement about the
conclusion.** Over 14,112 team-pairs, the AUC of map-correlation predicting
decision agreement is 0.581, and only **one of seven** hypotheses survives
Bonferroni — the one where 84% of teams agree anyway. Among pairs whose maps
correlate at a median r of 0.88 on hypothesis 1, **53.4% still disagree**, which
is *worse* than the marginal-implied chance rate.

**6. Analysts do not know how idiosyncratic they are** — and this is the part
with no counterpart in the sociology or finance corpora, because only NARPS asked
them. Self-rated similarity to other teams is weakly calibrated to a team's
*actual* map similarity (rho = 0.19), carries no information about whether its
conclusion matches the pooled meta-analysis (rho = 0.048, p = 0.21), and is
**negatively** related to agreeing with the majority (rho = -0.195 excluding the
one hypothesis whose majority is "yes", p < 0.0001). Confidence behaves the same
and is largely the same scale (rho = 0.670). Mechanism: the rating tracks *"I
found the effect"*, not *"I resemble my colleagues"*.

**7. On three of nine hypotheses the modal pipeline contradicts the pooled one.**
NARPS's own image-based meta-analysis finds the effect on H2, H4, H5, H6; a
majority of individual teams finds it only on H5.

**8. Prediction markets: discrimination excellent, calibration absent.** Both
markets overestimated, as the paper reports. What the paper does not report is a
baseline: a hypothesis-blind constant fitted leave-one-out has MAE **0.192**
against the team market's 0.323 and the non-team market's 0.449. But **74% of the
team market's MSE is a single constant offset of +0.323**; subtract it and its
RMSE falls from 0.375 to 0.191, better than any baseline, and its rank
correlation with the truth is 0.962 over nine hypotheses and **exactly 1.000**
over the five that do not share a map. *Report a bias/variance split beside any
"researchers were overoptimistic" claim; the two readings imply different fixes.*

**A methodological caution, learned the hard way and paid for twice.** The
pairwise (Mantel) instrument behind the correction to the through-line is
powerful and has two traps, both hit in one session:

- *A block permutation that keeps only half the blocks.* Permuting "whole teams"
  by lining up two position lists preserves the within/between structure only if
  every team has the same number of rows. CRI teams have 1 to 112 models; under
  that null only **46.1%** of within-team pairs stayed within-team, and it
  produced a confident, wrong p = 0.005. Aggregate to one row per cluster
  instead.
- *Nearly blind to diffuse association.* Injecting a signal along the dominant
  axis of choice variation, rho = 0.23 reaches 99% power; injecting the same
  strength spread over a random combination of all choice indicators gives
  rho = 0.038 and 14%. So a Mantel rho is a **lower** bound on coupling, and a
  null Mantel result is weak evidence of independence.

**Resolving power, to be quoted with any null result in this area:** 80% power at
Mantel rho ~ **0.228** for NARPS (n = 64 teams) and ~ **0.211** for CRI (n = 71),
with false-positive rates of 0.070 and 0.063 against a nominal 0.05. It is not a
function of n alone — it depends on how clumped the distance matrices are —
so it has to be read off the permutation null each time, not assumed.

## Numbers worth reusing

Everything below is checked against the released data, not quoted from an
abstract. `python tools/kb.py quantities --about <phrase>` retrieves them.

- **Analysis sample recipe** (undocumented upstream): drop 8 rows with missing
  `AME_Z`, drop the 48 rows with `u_teamid == 0` → exactly n = 1,253, 71 teams.
- **Headline percentages are inverse-team-size weighted.** Per model they are
  19.47 / 64.41 / 16.12, not 25.4 / 57.7 / 16.9. The weighting is disclosed in
  the figure legend and dropped by essentially every citation.
- **Variance is carried by almost nothing.** 13 models (1.0%) with SE above the
  99th percentile carry 47% of the sum of squares; the top ten come from 2 of
  71 teams. Trimming that 1% moves the SD from 0.0736 to 0.0400.
- **Sampling error cannot generate the spread of conclusions.** Common true
  effect + each model's own reported SE → 2.2 / 94.7 / 3.1 against the observed
  25.4 / 57.7 / 16.9.
- **True between-model heterogeneity is real and tiny.** I² = 0.93; τ ≈ 3.75×
  the typical sampling SE overall and 7.3× it in the most precise quintile;
  90% prediction interval ±0.014 SD units among the precise models. Cohen's
  "small" is 0.10–0.20.
- **Nothing partitions it.** Team, dependent variable, immigration measure,
  effect type, country set: one-sided p = 0.85–1.00 against a calibrated null
  with 78% power at a 25% between-cell share.

## Two methodological cautions this literature should carry and does not

**1. DerSimonian–Laird fails on many-analysts corpora.** These datasets have
extreme variance heterogeneity by construction — analysts choose sample sizes,
clustering, estimators. On the CRI standard-error distribution, when effect
magnitude scales with the standard error, DL recovers a true τ = 0.040 as
0.0060, a sevenfold underestimate; Paule–Mandel gets 0.024, REML 0.022. DL is
the default in most software. Any published heterogeneity number from a
many-analysts study should be accompanied by at least two estimators.

**2. Permutation nulls destroy more than you intend.** Shuffling team labels to
test "does team explain the heterogeneity?" also destroys the association
between team and *precision*, which is strong because a team's software and
model class fix the standard errors of all its models. Our permutation test
flagged detection in 6 of 6 synthetic scenarios including the one with zero
structure. The fix is to simulate under the null with every nuisance feature
pinned, rather than permute. Recorded as a `refuted` claim rather than deleted,
because the broken version is the intuitive one.

## Relation to the LLM-monoculture line

This area is the human mirror of `areas/llm-monoculture-and-correlated-errors.md`,
and the connection is a real methodological import, not an analogy.

Jo, Garg & Raghavan (`paper:jo2026-subjectivity`) prove that cross-model
agreement is only defined relative to a null the analyst chooses, and that a
sufficiently rich null absorbs the whole discrepancy — their **null ladder**.
Breznau et al.'s "hidden universe" has precisely that shape: a residual after
conditioning on 107 coded decisions. The metascience literature has no analogue
of the ladder and does not appear to know it needs one.

Running the ladder here produced the interesting outcome: **the discrepancy does
not get absorbed.** That is an empirical difference between the two cases rather
than a difference of framing, and it is worth more than the analogy that
prompted it. The edge is recorded as `zoo:sharesUnstatedAssumptionWith`.

The tempting further inference — "human experts do not converge either, so
LLM error correlation is not a machine pathology" — is **not licensed**, and the
record says so with `not-identifiable`. Breznau's expertise nulls exclude only
|R| > 0.36 at n = 71 teams; my scan of 85 team-level survey items gives a
maximum |r| of 0.31 against a chance threshold of 0.24. The human design cannot
see an effect of the size the LLM study reports (r = +0.84 in
`paper:maria2026-marginal-competence`), and the units are not commensurable.
Fixing that needs more teams, not more reanalysis.

## Does anything reduce analytic dispersion?

Only one study in the area offers evidence, and it is the claim most worth
verifying and least verified here. Menkveld et al. report that peer feedback
across four stages reduces NSEs by **47.2%** and interdecile ranges by **68.2%**,
with no single stage significant on its own. If true it is the only
quasi-experimental result anywhere showing that a *process* intervention narrows
analyst disagreement — and it bears directly on how work is organised in this
zoo, where sending a reanalysis to a peer to attack is routine.

Two cautions. First, the shape — four individually insignificant stages,
significant in aggregate — is the shape a multiple-comparisons artifact makes
when read backwards. Second, only pages 2339–2350 of that article were
obtainable, so this is `unverified` at `skimmed` depth and must be quoted that
way. **Update 2026-09-14: the 47.2%/68.2% falls reproduce from the team-level
deposit, but the reanalysis also finds the t-value dispersion *rises* over the
same four stages — see "#fincap at the team level" above. Still `unverified`,
now for a sharper and less comfortable version of the claim than the one
usually quoted.**

They also report that quality reduces dispersion: reproducibility −25.0% per SD,
peer-evaluator rating −33.3% per SD. **This is the resolution of Breznau et
al.'s Fig. 3 null.** The sociology study found nothing at n = 71, where the
intervals exclude only |R| > 0.36; the finance study finds effects at n = 164.
The two are compatible. Reading the sociology null as "expertise does not
matter" is not, and that is how it gets cited.

## #fincap at the team level: two findings, one open (2026-09-14)

The team-level deposit (`fincap.academy/data/fincap-data.zip` — anonymised
per-team estimate, SE, reproducibility score, peer rating, all 4 stages, all 6
hypotheses) was obtained in an earlier session and finally re-run and folded
into `menkveld2024-nonstandard-errors#c1-c5` this session. `read_depth` for the
paper's own text is still `skimmed` (only pages 2339–2350 of 52 obtainable), so
every status below is schema-forced to `unverified` regardless of how solid the
independent numbers are — the schema does not let assessment confidence outrun
how much of the authors' own argument has been read, and it caught me writing
`accepted`/`disputed` before I'd read enough to be entitled to either. Full
detail: `papers/menkveld2024-nonstandard-errors/NOTES.md`.

**1. Overdispersion is real and precision-driven, not estimate-driven.** "This
team reports a significant result" clusters by team 2.2×–3.1× a permutation
null at all 4 stages (p<0.0001) — same shape as NARPS's 2.26× and CRI's team
effect above. NEW here: between-team variance share of log(SE) is **0.78**
against **0.15–0.27** for the estimate itself (rank-transform test; a raw-log
variant gives 0.78 vs 0.50, same direction, weaker margin, script since lost —
see the record's artifact `a5`). A single team carries 77–99% of the total
sum of squares on 5 of 6 hypotheses. **Same mechanism as CRI's "outliers are
specifications, not people" and NARPS's precision-not-conclusion split, now in
a third field.**

**2. Peer feedback narrows point estimates while widening disagreement about
the conclusion — the opposite of the intuitive reading of the paper's own
47.2%/68.2% numbers.** Those numbers reproduce on the estimates (IQR ratio
0.49, IDR ratio 0.34, matching within bootstrap noise). But SEs shrink even
faster than estimates converge, so **t-value IQR *rises* to 1.35× stage 1 (95%
CI [1.05, 1.67], excludes 1)**, and the fraction of teams crossing |t|>1.96
rises sharply on most hypotheses (h1: 32%→62%, h3: 49%→87%). If this survives
whatever Appendix B says (not in the deposit), "peer feedback reduces
disagreement" needs the qualifier: reduces it about the number, widens it about
the conclusion. Worth an eventual cross-link to the NARPS thresholding finding
above (§4, "thresholding sets the level, the data set the ranking") — different
mechanism (there it's the threshold rule, here it's SE convergence outpacing
estimate convergence), same shape (agreement about the estimate does not imply
agreement about the decision).

**3. The team-level version of the quality claim finds nothing.** An
individual team's reproducibility/peer-rating barely predicts its own deviation
from consensus or its own precision (|rho| 0.07–0.17, mostly n.s., one
borderline at p=0.033), and all three quality measures together give
out-of-fold R² indistinguishable from a permuted-label control (−0.016 vs
−0.017) — not underpowered, n=164 resolves rho as small as 0.153. Open,
genuinely: this may be a level-of-aggregation mismatch against whatever
regression the paper actually ran (not visible from the accessible pages), or
the reported quantile-regression coefficients may be more fragile than the
headline percentages suggest. Unlike Breznau's Fig. 3 null (excluded above as
underpowered at |R|>0.36, n=71), this one is NOT an underpowered-null story —
n=164 is plenty to see rho=0.153, and the correlations are simply small.

## Open, in priority order

1. ~~**Replicate the precision/conclusion split elsewhere.**~~ **DONE 2026-09-09
   on NARPS, DONE 2026-09-14 on #fincap** — see both sections above. Three
   corpora now (CRI, NARPS, #fincap), three fields, same shape: overdispersion
   of the *conclusion* is driven by *precision*, not by the *estimate*. Open at
   `unverified`/`skimmed` for #fincap specifically until the full paper text or
   Appendix B is obtainable — get that before upgrading any of
   `menkveld2024-nonstandard-errors`'s five claim statuses. Silberzahn et al.
   2018 (29 teams, red cards) remains a candidate fourth corpus, but n = 29 is
   below anything this area's instruments can resolve.
2. **What structures the heterogeneity?** Real (I² = 0.93), not exchangeable
   (six functionals imply τ from 0.0012 to 0.0160), not organised by any
   partition available in the released coding. The candidates left are inside
   the specification — estimator family, country-year nesting, covariate set —
   i.e. exactly what the 107 binary indicators flatten.
3. **Read Breznau et al.'s reply to Mathur et al.** (PNAS e2219555120). Unread;
   the only place they answer the effect-size critique.
4. Unread and relevant: Auspurg & Brüderl's reanalysis of Silberzahn (Socius
   2021); Lundberg, Johnson & Stewart, "What is your estimand?" (ASR 2021);
   Schweinsberg et al. 2021; Menkveld et al. on non-standard errors.
