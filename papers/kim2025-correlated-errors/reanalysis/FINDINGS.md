# Findings — 2026-08-07, maria

Sample: 22 HELM models × 2,918 MMLU items (10 subjects), re-downloaded from the
public GCS bucket. 64,196 model-item cells, 0.5% missing. All numbers below are
from `analyze.py`, `followup.py`, `anchored.py`, `marginal.py`; rerunnable.

## 0. The replication package is broken, and in an instructive way

`github.com/nikhgarg/llm_correlated_errors_public` is complete except for
`data/helm/all_mmlu_data_limitedcols.csv` — the per-question × per-model response
matrix that every other artifact is derived from. It is a Git LFS pointer
(335,231,032 bytes) whose object **404s on GitHub's LFS endpoint**
(`git lfs fetch --all` → "Object does not exist on the server"). Verified
2026-08-07.

What survives: code, the pair-level derived tables, the regressions, the figures.
So you can **re-execute** the paper. What is gone: the raw item-level data. So you
cannot **change the null model** — the one thing a critic needs to do.

This is Mark's 2026-08-05 prediction happening in miniature, inside one hour:
the cheap bar (re-execution) passes, the expensive one (independent judgement) is
blocked. It is also a sharper version of the "~26% computational reproducibility"
number in `philosophy-of-science/verification-economics-of-open-science.md`:
artifact *presence* and artifact *sufficiency for reanalysis* are different
properties, and only the first is what badging checks.

I reconstructed the raw data independently from `storage.googleapis.com/crfm-helm-public`
(`fetch_helm.py`), which is the source their own script used. So the loss is
recoverable here — but only because the upstream benchmark is itself open.

## 1. The headline statistic replicates

Kim et al. (2025) report mean agreement-when-both-wrong of **0.60** on HELM
(71 models, 14,042 items) against a uniform-over-wrong baseline of 1/3.
On my independent 22-model / 2,918-item subsample: **0.5528**. Same magnitude,
same direction. Their number is not in doubt.

Methodological check that *passed*: I compared answers by answer **text**
(`mapped_output`), not by letter, in case HELM shuffles option order per model.
It does not — 0/2,918 items have differing option order across models. Their
letter-based comparison is sound.

## 2. My first null was a tautology. This is the main methodological result.

I built what seemed the obvious improvement on their uniform baseline: a
nonparametric per-item null in which each model draws its wrong answer
independently from that item's *own* empirical distractor-attractiveness
distribution, estimated **leave-this-pair-out** from the other models.

It reported "93.8% of the excess agreement is explained by item structure," and
then reported **exactly 100.0%** in every robustness stratum and every subject.
Exactly 1.0000, ten times. That is not robustness; that is an identity.

**Proposition.** For one item, let *W* be the models answering it wrongly,
|*W*| = *w* ≥ 4, and *c* the number of concordant pairs in *W*. Observed collision
rate is *c*/C(*w*,2). For pair (*i*,*j*) the leave-pair-out null is
*c*₋ᵢⱼ/C(*w*−2,2). Each concordant pair {*k*,*l*} is disjoint from exactly
C(*w*−2,2) pairs {*i*,*j*}, so Σᵢⱼ *c*₋ᵢⱼ = *c*·C(*w*−2,2), hence
mean over pairs of the null = *c*/C(*w*,2) = mean over pairs of the observed.

**The leave-pair-out nonparametric item null has exactly zero expected excess
agreement on any dataset whatsoever.** Zero power. Confirmed numerically
(`anchored.py` A) on synthetic data with injected monoculture: with 99% of models
forced onto the same trap, observed = 0.9790, null = 0.9790, excess = −0.00000.

This is a concrete, algebraic instance of Jo, Garg & Raghavan (2026) Theorem 1 /
Proposition 2 — a sufficiently expressive null absorbs all cross-model correlation.
Their version is asymptotic in the null-ladder dimension *K*; this one is exact
and holds at *n* = 1 item. I did not set out to demonstrate their theorem; I walked
into it, which is better evidence than agreeing with it would have been.

Consequence: the "93.8%" in `analyze.py` is **not a finding** and must not be
quoted. Only *relative* comparisons within a pinned-mean statistic survive
(e.g. which pairs deviate most), and even those need care.

## 3. Anchored nulls are wildly antisymmetric — the effect is marginal, not pairwise

Estimating item attractiveness from a **disjoint anchor set** of models breaks the
identity, so the statistic can be nonzero:

| null estimated from | excess measured among | mean excess | % positive |
|---|---|---|---|
| weakest 8 models | strongest 8 | **+0.212** | 100% |
| strongest 8 models | weakest 8 | **−0.206** | 0% |
| middle 6 | strongest 8 | +0.044 | 82% |
| middle 6 | weakest 8 | −0.206 | 11% |

The sign flips with the *direction* of the comparison, at nearly equal magnitude.
An anchored null is therefore measuring the capability gap between anchor and
target, not kinship. Any leave-others-out design where the anchor population has
mixed ability will show high-accuracy pairs as "excessively correlated" almost
mechanically — which is exactly the design that produces the widely-quoted result
that **more capable models have more correlated errors**. In my leave-provider-out
run, corr(excess, min accuracy of the pair) = **+0.801**, reproducing that claim,
and I believe the claim is largely this artifact.

Note this is *not* the critique Jo et al. make. Their IRT null carries a model
ability parameter θⱼ, which absorbs differences in *marginal accuracy*. But their
outcome is binary correctness, so nothing in their null describes **which** wrong
answer a model gives. The ability-dependence of the wrong-answer distribution is
invisible to it.

## 4. What actually drives it: competence concentrates errors (r = +0.84)

Per model, over items where it is wrong, how often does it choose the *modal*
wrong answer of the other 21 models? This is a **marginal** quantity — no pairwise
information in it at all.

| model | acc | P(modal distractor \| wrong) |
|---|---|---|
| meta/llama-3.1-405b | 0.853 | 0.778 |
| qwen2.5-72b | 0.817 | 0.722 |
| claude-3-5-sonnet | 0.872 | 0.702 |
| gpt-4o | 0.816 | 0.652 |
| gpt-3.5-turbo | 0.571 | 0.628 |
| mistral-7b-v0.1 | 0.499 | 0.555 |
| llama-3.1-8b | 0.509 | 0.368 |
| **olmo-7b** | **0.290** | **0.267** |

**corr(accuracy, P(modal distractor | wrong)) = +0.835** across 22 models
(+0.841 excluding the duplicate pair below).

So: the better a model is, the more its *errors* concentrate on the single most
seductive distractor. Two strong models can be conditionally independent given
the item and still agree ~70% of the time when both are wrong, because each
independently puts ~0.7 of its error mass on the same trap. **The agreement is a
marginal consequence of shared competence meeting a structured test, not evidence
of dependence between the models.**

This reframes the whole literature's headline: "models agree 60% of the time when
both err" is compatible with complete conditional independence, and the observed
positive relationship between capability and correlation is the *expected*
signature of that independence, not a warning sign.

### 4b. The decomposition, once the model is calibrated (`calibrated.py`, added later same session)

The fix specified in §7 was carried out. Every item here has 4 options, so parameterise
model *m* as: when wrong, pick the item's modal wrong answer *M* with probability *s_m*,
else uniformly among the 3 wrong options. Then
*q_m* = P(picks *M* | wrong) = *s_m* + (1−*s_m*)/3, so **s_m is identified by the
measured q_m**: *s_m* = (3*q_m* − 1)/2. *q_m* is measured leave-self-out so it is not
self-fulfilling. Under conditional independence the pair agreement is then exact, with
no simulation:

  P(agree | both wrong) = *q₁q₂* + 2·[(1−*s₁*)/3]·[(1−*s₂*)/3]

| quantity | value |
|---|---|
| observed agreement-when-both-wrong | 0.5634 |
| predicted under **conditional independence** | 0.5115 |
| uniform-over-wrong baseline (Kim et al.) | 0.3333 |
| excess over uniform | +0.2301 |
| **reproduced with zero dependence** | **+0.1781 (77.4%)** |
| **residual requiring dependence** | **+0.0520 (22.6%)** |

So roughly **three quarters of the headline effect is marginal** — shared competence
meeting a structured test — and a quarter is genuine dependence between models.
80% of pairs have a positive residual, sd 0.064. `corr(acc, q_m) = +0.823` under
leave-self-out, confirming §4.

**This partly reverses the retraction in §6.** With a legitimate null the provenance
signal does sharpen, and now it is measured with the right statistic rather than a
ratio of near-zero quantities:

| | same-provider | cross-provider | Cohen's *d* |
|---|---|---|---|
| raw agreement | 0.600 | 0.550 | +0.447 |
| **calibrated residual** | **+0.0981** (n=12) | **+0.0494** (n=218) | **+0.789** |

Discrimination nearly doubles. The earlier "six-fold sharpening" claim was still wrong
(wrong statistic, wrong magnitude); the direction was right.

And on Kim et al.'s capability claim: `corr(min pair accuracy, predicted independent
agreement) = +0.863` versus `corr(min pair accuracy, observed) = +0.820`. The marginal
model **fully accounts** for the ability gradient — slightly over-accounts. But the
residual still carries `corr = +0.353`, so a real, smaller, capability-linked dependence
survives. "More capable models have more correlated errors" is mostly an artifact and
not entirely one.

Largest residuals: deepseek-67b/gpt-3.5-turbo (+0.204), llama-405b/llama-70b (+0.201),
claude-3.5/llama-405b (+0.178). The duplicate pair sits at +0.393, still an order apart.

Two model-level anomalies worth a second look: `llama-3.1-8b` has *q* = 0.388 at accuracy
0.509 (far below the trend), and `olmo-7b` has *s* < 0 — it picks the popular trap *less*
often than random, i.e. its errors are anti-correlated with everyone's. Both are off the
`corr = +0.823` line in the same direction and neither is explained here.

### Failed check — reported because it failed (superseded by §4b, kept for the record)

`marginal.py` Test 2 tried to quantify this: simulate a population that is
conditionally independent by construction, each model drawing from its own fitted
attractiveness profile, and see how much agreement appears. It produced 0.845 vs
observed 0.551 — a 236% overshoot. My tilt parameterisation adds the sharpness *t*
as raw probability mass on the top distractor, which drives p(top) far above each
model's measured p_modal. **The simulation is miscalibrated and its number must not
be quoted.** The fix is to solve *t* per model so simulated P(modal | wrong) matches
the measured value in Test 1, then re-run. Not done. Until then, Test 2 supports
only the weak, directional claim that conditional independence can easily *exceed*
the observed agreement level — i.e. that the observed level is not by itself
evidence of dependence.

## 5. One pair is not correlated — it is the same system

Kim et al. flag `google/text-unicorn@001` and `writer/palmyra-x-v3` as agreeing on
0.9987 of items where both are wrong, "to our knowledge no publicly stated direct
relationship." On my sample:

- identical answer on **2,917 of 2,918 items — 99.97% overall**, not just when wrong
- accuracies 0.70966 vs 0.70938 (they differ on exactly one item)
- next-highest overall identical-answer rate of any pair: 0.8705

This is not a correlated pair. It is one system appearing twice, or a provenance
error in the benchmark. It should be excluded from any correlation statistic
rather than counted as the extreme of a continuum — including it inflates every
aggregate and supplies the most dramatic single data point for the monoculture
thesis. Every number above excludes it where noted.

## 6. What survives, honestly

- Same-provider pairs do show a residual (+0.066 vs +0.007 cross-provider under the
  leave-provider-out null), and the largest genuine residual is
  llama-3.1-405b/llama-3.1-70b (+0.274) — same family. Family kinship is real.
- But Cohen's *d* for same-provider is only +0.447 → +0.482 when moving from the raw
  statistic to the item-corrected one, with **n = 12 same-provider pairs**. My earlier
  reading that the correction "sharpens the provenance signal six-fold" was wrong —
  it came from a ratio of two near-zero quantities. Retracted.
- Direction of travel: the monoculture literature's central statistic is dominated
  by (a) item structure, (b) an ability-graded marginal effect, (c) at least one
  data-integrity case; genuine pairwise kinship is the smallest of the four terms.

## 7. Open

- [ ] Recalibrate `marginal.py` Test 2 (solve *t* per model). This is the one number
      that would turn §4 from a mechanism into a decomposition.
- [ ] The mechanism predicts something testable and cheap: on items where the
      *correct* answer is unambiguous but one distractor is designed to be seductive,
      capability should raise agreement-on-error; on items where wrongness is
      unstructured (arithmetic slips), it should not. Split MMLU accordingly.
- [ ] Extend to all 71 HELM models / 57 subjects. Nothing here needs the LFS file.
