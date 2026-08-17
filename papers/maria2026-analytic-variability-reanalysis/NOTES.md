# NOTES — my reanalysis of the Crowdsourced Replication Initiative

maria, 2026-08-12. Reasoning, order of discovery, and the two things I got
wrong. Numbers in `paper.json`; the scripts live in
`../breznau2022-hidden-universe/reanalysis/`.

## The finding, in one sentence

Analytic decisions determine **how precisely** an analysis will answer the
question and say **nothing** about what the answer will be — out-of-fold and
grouped by team, R² = 0.194 ± 0.024 for log standard error and R² = −0.005 for
the estimate itself.

Everything else in the record is either the evidence for that or the wreckage of
hypotheses that did not survive.

## The two deflations I tried afterwards, which made it bigger

I did not trust it, for two good reasons, and tested both.

**"You are just predicting sample size."** A standard error is roughly
sigma/sqrt(N), so predicting it could be nothing more than predicting how many
countries and waves a team included. It is not. Sample composition — 42 country
dummies, 5 waves, country count, listwise vs multiple imputation — gives
R² = **−0.012**. Modelling choices alone give **0.150**. The signal is entirely
in the model class: hybrid multilevel (+0.142 standardised), MLwiN (+0.139),
country-year random effects (+0.105) inflate the standard error; two-way fixed
effects (−0.075) and dichotomising the outcome (−0.074) shrink it.

So the sentence becomes sharper and, I think, quite unsettling: **an analyst's
choice of model class sets the width of their confidence interval — and
therefore whether they will report a finding at all — while leaving the point
estimate alone.** The decision that governs publishability is close to
orthogonal to the decision that governs what is true.

**"Your outcome is your own construction."** The significance categories in the
main result are mine, computed from the confidence intervals. Breznau et al.
also recorded what each team concluded in words. Out-of-team those written
conclusions come out at R² = −0.07 / −0.08 / −0.02 for support / reject /
not-testable: worse than the base rate. The split holds on the field's own
outcome, not only on mine.

One methodological note that matters more than it looks: the written conclusion
is near-constant within a team. Random k-fold cross-validation would have
reported a large R² here through leakage alone, and it would have looked like a
finding. Grouping folds by team is the whole reason the number means anything.

## Report a range, not a point

The headline R² moved from 0.207 to 0.172 when nothing changed but the shuffle
of 71 teams into 10 folds. Over 40 fold assignments it is 0.194 ± 0.024 (range
0.132–0.236); leave-one-team-out, which has no fold randomness at all, gives
0.205. With 71 clusters, a single grouped-CV R² is itself an estimate with a
standard deviation of about 0.02. I had quoted the first number I got. That is
the same error as quoting one tau estimator, committed by me, two hours after
criticising someone else for it.

## Order of discovery, including the wrong turns

1. Reproduced Fig. 1 exactly, after recovering the undocumented analysis sample.
   Noticed en route that the headline is inverse-team-size weighted and that the
   unweighted numbers are 5.9 points different.
2. Decomposed dispersion into sampling error and true heterogeneity — and got
   **sampling error = 102% of the observed variance**. An impossible number.
   That was the most useful result of the session, because it is the kind of
   wrongness that announces itself. Cause: the standard errors span a factor of
   36,000, so the arithmetic mean of SE² is not a summary of anything; it is a
   report on the two worst models.
3. Chased the outliers. Thirteen models (1%) carry 47% of the sum of squares;
   the top ten come from two teams. Team 13's MLwiN change-in-flow models have
   standardized estimates of 1.30 and 1.21 with standard errors of 0.95 and
   1.43.
4. **Hypothesis A: it's all sampling noise.** Tested with a common-effect null
   keeping each model's own SE. Comprehensively rejected: 2.2/94.7/3.1 against
   25.4/57.7/16.9. Positive control (tau = 0.05) rejected in the other
   direction, so the test has power. Hypothesis A is dead, and Breznau et al.
   gained a lot of credibility with me at that moment.
5. Noticed my tau estimates disagreed by 3×, then 5×. Stopped and built an
   estimator bench: DL, Paule–Mandel, REML, naive moment, tested against known
   tau on the empirical SE distribution with and without effect/precision
   coupling. DL underestimates by 7× under coupling. That is a general warning
   about many-analysts corpora, not a fact about this one.
6. Tried to settle tau by calibration instead of by choosing an estimator: match
   the statistic people actually quote. Six functionals gave tau from 0.0012 to
   0.0160. On synthetic data from the same model they agree to three decimals.
   **The one-parameter random-effects model is rejected.** No single tau is a
   description of this dataset — including mine, and including Mathur et al.'s.
7. **Hypothesis B: it's estimands, not idiosyncrasy.** Condition on dependent
   variable × immigration measure × effect type × country set. tau does not
   drop; it rises. Rising was the tell that my test was broken.
8. Built a permutation control, which said "conditioning explains nothing" —
   and then a positive control, which said the permutation test flagged
   detection in **6 of 6** scenarios including the one with 0% between-cell
   structure. The test was blind. See below.
9. Rebuilt the null correctly (keep the real labels and the real standard
   errors, simulate effects with no between-cell structure). Calibrated: 2%
   false positives at a nominal 2.5%. Powered: 78% at a 25% between-cell share,
   92% at 50%. Result on real data: p = 0.85–1.00 for every partition,
   including **team**. Hypothesis B is dead too.
10. Turned the question around — if decisions don't predict the estimate, what
    do they predict? Precision, strongly. That is the finding.
11. Checked whether the human/LLM comparison I wanted to make is licensed. It
    is not: the design cannot see anything below |r| ≈ 0.36.

## The two mistakes, kept on the record

**Mistake 1 — a permutation null that destroyed the wrong thing.**
Shuffling team labels while preserving cell sizes seemed obviously right. It is
not: teams are internally homogeneous in *precision* (one team's MLwiN
specification produced large standard errors for all of its models), so
permuting labels mixes precise and imprecise models inside a cell and moves the
statistic for a reason unrelated to the hypothesis. Recorded as claim c9 with
status `refuted`, and deliberately not deleted — the broken version is the
intuitive one and someone will write it again. Me, probably.

The general rule I take from it: **a permutation null must be told what to hold
fixed, and the nuisance structure is usually not the thing you were thinking
about.** Simulating under the null hypothesis with every nuisance feature pinned
is safer than permuting, whenever you can write the null down.

**Mistake 2 — an untuned penalty masquerading as a result.**
The first predictive pass used ridge with lambda = 10 on an unstandardised
design matrix and produced R² = −0.23 for the estimate, which I nearly wrote up
as "decisions are anti-predictive". That was my own arbitrary lambda.
Standardising and sweeping lambda over eight orders of magnitude moved it to
−0.003 with a permutation null of −0.001, which is the honest answer: **zero**,
not "negative". A negative best-case is a result; a negative untuned case is a
bug.

## What I still don't know, and it bothers me

The heterogeneity is real (I² = 0.93), not exchangeable (six functionals, 13×
spread), and not organised by team, dependent variable, immigration measure,
effect type or country set. I ran out of partitions. Whatever structures it is
inside the specification itself — estimator family, the treatment of
country-year nesting, the covariate set — and those are precisely the choices
the coding scheme flattens into 107 binary indicators.

The pooled within-cell statistic also sits *above* its own no-structure null for
every partition. That is a misspecification signal and nothing in either paper
models it. I do not have an account of it.

## The next test, and why it is the right one

`c7` is currently a finding about one dataset. NARPS (Botvinik-Nezer et al.
2020, 70 fMRI teams, maps on NeuroVault) and Silberzahn et al. 2018 (29 teams,
red cards) both have open data and both coded analytic decisions. If
"decisions predict precision, not conclusions" replicates in either, it stops
being a curiosity about immigration attitudes and becomes a statement about what
a many-analysts study measures. If it fails there, I have learned that the split
is domain-specific, which is nearly as useful.

That is the first thing I would do with the next block of budget.
