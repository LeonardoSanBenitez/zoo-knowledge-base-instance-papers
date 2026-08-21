# Gamma & Metzinger 2021 (MPE-92M) — reanalysis notes

Author: maria. Reanalysis session 2026-08-16. An earlier pass (2026-07-31)
established the eigenvalue and parallel-analysis results now summarised in
`areas/contemplative-neuroscience.md`; this pass asks a different question and
reaches a conclusion that changes how the earlier one should be quoted.

## The question

The 2026-07-31 pass established that the *number* of factors in the MPE-92M is a
resolution choice: Horn parallel analysis gives 11, the authors report 12, Kaiser
gives 18, on one dataset. That is a statement about decision rules.

It leaves the prior question untouched. **Which of these factors would appear
again in a second sample?** A dimension that does not replicate is not a
dimension of the phenomenon; it is a dimension of this dataset. For a taxonomy —
CAT included — that is the question that actually binds.

## What was measured

Split-half congruence. Divide N=1403 into two independent halves, run the
paper's own EFA on each (Spearman correlations, principal extraction, oblique
quartimin — `oblimin` with gamma=0 *is* quartimin), match the two factor sets by
Tucker's phi under the Hungarian algorithm, repeat over 30 random splits, report
the median matched phi per factor rank. Conventional reading (Lorenzo-Seva &
ten Berge 2006): phi >= .95 the factors are the same, .85-.94 fair, below .85
not the same factor.

One implementation note that is a real finding about the tooling: `factor_analyzer`
refuses `method='principal'` on a correlation matrix. Rather than silently switch
estimator and stop reproducing the paper, the items are **rank-transformed and
passed as raw data** — Pearson on ranks *is* Spearman. Verified: max absolute
difference between the two correlation matrices is 1.9e-15.

## Result

The instrument was validated before use, on data whose answer I control
(`validate_synthetic.py`). Given 92 items generated from exactly 5 factors and
asked for 12, it returns five factors at phi = .99 and a **cliff** to .76 and
below. Given pure noise it returns .10–.33 at every k and never approaches .85.
Given one general factor plus four weak specifics — the shape this data has —
spurious factors stay at the noise floor. The instrument sees structure when
structure is there and does not manufacture it when it is not.

On the real data there is **no cliff**. At k=12 the median profile is
.90 .88 .86 .85 .83 .81 .78 .75 .71 .64 .57 .39 — a smooth gradient. And at
every k >= 5, **zero factors reach the .95 criterion**; even the strongest never
exceeds ~.93. Meanwhile every factor at every k sits above the column-permuted
null, so every factor carries some real signal. The picture is not "eleven real
factors and seven fake ones". It is a continuum in which nothing is cleanly a
factor and nothing is cleanly noise.

## Trying to kill it

The obvious rival: nothing interesting is happening, the loadings are simply
weak (mean |loading| = .124 at k=12) and n=701 per half is too small for .95.

The test that settles it is a **clone** — a parametric bootstrap. Fit the
k-factor model to all N=1403; generate a synthetic dataset from those fitted
loadings and uniquenesses, same N, same k, same 92 items. The clone is by
construction a true k-factor world *with the real data's own loading strengths*.
If the deficit were estimation noise, the clone would show the same profile.

It does not. At k=12 the clone reaches mean phi .93 with 10–11 factors above .85
and 6 above .95, against the real data's .76 with 4 above .85 and none above .95.
The gap is +0.13 to +0.14 and is stable across k = 5, 8, 12.

Second rival, and the one I thought most likely to revive the null: my clones had
**orthogonal** factors while the real solution is oblique, and correlated factors
are harder to separate and match. Rebuilt the clone drawing factor scores from
N(0, Phi_hat) with the estimated factor correlation matrix. This does not close
the gap — it *widens* it at k=5 (oblique clone .954 vs orthogonal .866 vs real
.811). Obliquity makes recovery easier here, not harder.

**So the MPE-92M's factor structure is substantially less reproducible than any
factor model fitted to it predicts it should be.** That is a misspecification
result, not a power result.

## Where the instability comes from — a clean negative

The natural mechanism is that the sample is a mixture of populations whose
phenomenology is structured differently. Meditators trained in different
traditions are taught different vocabularies for inner events; that ought to show
up in how their reports covary.

Tested directly on eight groupings — questionnaire language, sex, Vipassana, Zen,
metta, Mahamudra/Dzogchen, Buddhist identification, psychedelic use — with the
control that makes such a test honest: between-group congruence compared against
**random splits of the pooled sample at exactly the same two group sizes**, so
that sample size is held fixed and only group membership is destroyed.

Essentially nothing. Of 16 comparisons, only language at k=12 falls below its
size-matched null (p = .040, which does not survive 16 tests), and Zen and metta
at k=5 sit *above* their nulls. Between-group congruence tracks the size-matched
null almost exactly.

Two things follow, and they point in opposite directions, which is why both must
be said:

1. **Positive, and interesting for the field:** the covariance structure of
   pure-awareness reports is not detectably shaped by the tradition or the
   language that taught the person to describe them. The obvious "they are just
   reciting their doctrine" objection to this literature does not survive contact
   with these data. Note the design caveat that bounds this: traditions are not
   mutually exclusive in this questionnaire (respondents tick several), so each
   is tested as practises-X vs does-not — a weaker contrast that biases toward
   finding no difference. The conclusion is bounded in the safe direction.
2. **Negative:** the replicability deficit is therefore *not explained* by any
   heterogeneity the questionnaire recorded. It remains unexplained.

## How much heterogeneity would be needed — and why I will not quote the number

Calibration sweep: simulate two subpopulations whose loadings differ by
+/- c * mean|L| and find the c reproducing the observed deficit. c = 2.0 matches
to three decimals (.757 vs .758).

**I do not report c = 2.0 as an estimate, because the curve is not monotonic:**
c = 3.0 returns to .837, above the target. At least two values of c produce the
observed phi, so c is not identified by this statistic. What survives is a
directional statement: reproducing the deficit by two-group heterogeneity needs
loading differences of roughly twice the mean loading itself — i.e. the two
groups would have to be answering nearly different questionnaires — which is not
credible and is a further argument against the mixture explanation, rather than
for it.

Recorded because it is exactly the shape of error CONTRIBUTING warns about: a
number that matches to three decimals and means less than it appears to.

## What this does to the earlier pass

It does not refute it. The eigenvalues, the N=1403 reproduction, the 11/12/18
count, the self/subject-object factor and the luminosity factor all stand as
computed. What changes is the *force* of the count claim, and the change is in
the direction of strengthening it:

> Earlier: "the dimension count is a resolution choice — three defensible rules
> give 11, 12, 18 on one dataset."
> Now: the count is not merely under-determined by the choice of rule. At the
> resolution of a half-sample, **this data does not contain discretely
> identifiable factors at all** — not 11, not 12, not 18. Every extracted factor
> beats a permutation null; none reaches the criterion for being the same factor
> in two halves of the same sample.

Consequence for CAT, and it is a sharp one: a fixed axis count was already going
to be indefensible. The stronger obligation is that **CAT must report the
split-half congruence of its own dimensions**, and must expect them to look like
this, because it is scoring an object of the same kind. A taxonomy paper that
publishes a dimension count without a replicability profile is publishing the
part that does not replicate.

The self/subject-object recommendation is unaffected: at k=5 and k=7 that factor
is consistently among the top-ranked and most stable, and the case for it never
rested on the count.

> **⚠ CORRECTION, 2026-08-21.** The claim above ("consistently among the
> top-ranked and most stable") was an eyeball read of a loading table, never
> actually computed as a phi/rank number, and it was wrong. Properly computed
> in `run_self_factor_stability.py` (30 independent split-halves, self-factor
> identified within each half separately by its own item loadings, no
> full-sample leakage, matched via the same Hungarian assignment the official
> pipeline uses): median rank **3rd of 5** factors at k=5, **5th of 7** at k=7
> — average to slightly below-average stability, not exceptional. The factor
> IS real (median phi 0.76–0.80, decisively above a correctly-implemented
> permutation null whose median is 0.14 — a first attempt at that null had a
> silent bug, `pandas .apply(axis=0)` failing to actually reshuffle rows,
> which produced a spuriously high null and would have suggested the opposite
> error had it gone unchecked). So: real signal, ordinary stability. Not
> "one of the more stable axes." Full derivation and consequences for the CAT
> project in `.claude/memory/maria/cat_lutz_crosswalk.md` §6.2 — an argument
> in that file was built on the wrong version of this claim and has been
> corrected in place there too. Recorded here, not silently fixed, because
> the original wrong sentence is still readable two paragraphs above.

## Limits I am not hiding

- One dataset, one sample, one questionnaire. "Less replicable than its own
  fitted model" is demonstrated here; whether it generalises to other
  phenomenology instruments is untested and is the obvious next study.
- Split-half congruence at 30 splits gives a stable median but the p05/p95 band
  at high k is wide; the k=12 rank-12 factor in particular swings a lot.
- The clone is generous to the null in one respect (normal factor scores) and
  strict in another (it inherits the real uniquenesses). I judge the net bias
  to favour the clone, i.e. against my conclusion, which is the safe direction.
- I did not re-read the paper's own text this session. The methodological
  description (Spearman, principal factor, quartimin, over85items, the 2024
  correction to the data link) comes from the 2026-07-31 pass, which did read it.
  Claims attributed to the authors carry that provenance.
