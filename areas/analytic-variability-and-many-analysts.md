# Analytic variability and many-analysts studies

What happens when independent analysts are handed the same data and the same
hypothesis. Started by maria, 2026-08-12.

Records: `papers/breznau2022-hidden-universe/`, `papers/mathur2023-effect-sizes/`,
`papers/menkveld2024-nonstandard-errors/`,
`papers/maria2026-analytic-variability-reanalysis/`.
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

**The estimate distribution is heavy-tailed in both.** IDR/IQR is 1.90 for a
Gaussian at *any* sample size (simulated 95% bands: 1.52–2.43 at n=71,
1.79–2.01 at n=1252), so it needs no calibration to compare corpora. Both are
far above it.

One nuance available only in CRI, because it has multiple models per team: the
heavy tails live at the **model** level, not the analyst level. One estimate per
team and IDR/IQR falls to 2.08, comfortably inside the Gaussian band. **The
outliers are specifications, not people.**

---

## The through-line

The field's headline finding is that analysts do not converge. The reanalysis
here says something more specific and, I think, more useful:

> **Analytic decisions determine how *precisely* an analysis answers the
> question, and say nothing about what the answer is.**

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
way.

They also report that quality reduces dispersion: reproducibility −25.0% per SD,
peer-evaluator rating −33.3% per SD. **This is the resolution of Breznau et
al.'s Fig. 3 null.** The sociology study found nothing at n = 71, where the
intervals exclude only |R| > 0.36; the finance study finds effects at n = 164.
The two are compatible. Reading the sociology null as "expertise does not
matter" is not, and that is how it gets cited.

## Open, in priority order

1. **Replicate the precision/conclusion split elsewhere.** #fincap is now the
   best candidate — 164 clusters, a different field, pre-registered, and each
   team reports an estimate *and* a standard error, which is exactly the pair
   the test needs. Look at `fincap.academy` and `osf.io/h82aj` for the
   team-level table. Failing that, NARPS
   (Botvinik-Nezer et al. 2020, *Nature*, 70 fMRI teams, maps on NeuroVault) and
   Silberzahn et al. 2018 (29 teams, red cards) both released data and coded
   decisions. This is the test that turns a finding about immigration attitudes
   into a statement about what many-analysts studies measure.
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
