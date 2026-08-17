# Retrieval-augmented generation as a knowledge-management problem

Started by maria, 2026-08-12. Records: `papers/liu2024-lost-in-the-middle/`,
`papers/cuconasu2024-power-of-noise/`, `papers/mazuryk2026-powerless-noise/`,
`papers/gabin2026-lost-in-the-evidence/`,
`papers/maria2026-rag-specification-dispersion/`.

> **Read section 6 first if you are short of time.** It is the one result here
> that none of the five records contains on its own.

This file is the argument. The numbers live in the records; the point of the
prose is to say what the numbers mean together and what is still missing.

---

## The through-line

A RAG pipeline is a chain of researcher degrees of freedom — chunking, embedder,
retrieval depth, reranking, ordering, context length, prompt wording, decoding
limits, output post-processing — and the field evaluates it by reporting one
number from one traversal of that chain, with a confidence interval computed as
if the chain were fixed.

It is the same situation as the many-analysts literature, and the same
instruments apply. What the RAG papers lack is not rigour; several of them are
careful. What they lack is the *vocabulary* that finance and sociology already
built for exactly this, and the habit of measuring dispersion across the chain as
a first-class quantity rather than as a robustness appendix.

The bridge:

| many-analysts | RAG |
|---|---|
| analyst / team | pipeline configuration |
| nonstandard error = IQR across teams | IQR of the effect across configurations |
| specification curve over 1,253 models | 5 models × 3 prompts × 4 doc counts |
| team chose their own sample → SE varies | fixed evaluation set → SE is pinned |

That last row is the interesting asymmetry and it is developed below.

---

## 1. The one effect the area has argued about, and how it dissolved

Cuconasu et al. (SIGIR 2024) reported that adding **random** documents — drawn
uniformly from a 21M-passage Wikipedia corpus, unrelated to the query — improves
RAG question-answering accuracy "by up to 35%". The claim is counter-intuitive
enough that it launched a small literature on beneficial noise.

Mazuryk et al. (SIGIR 2026) reproduced it and showed it is confined to the
original inference regime: 4-bit weights, a 15-token generation cap, and a prompt
that demands the model emit `NO-RES` when it cannot answer. Relax any of the
three and the effect weakens, vanishes, or reverses.

Reading the two together (`maria2026-rag-specification-dispersion`):

* Under the modern configurations Mazuryk et al. themselves argue are correct,
  **1 of 10 (model, prompt) cells shows the effect significantly positive and 4
  show it significantly negative.**
* The "+35%" is a relative gain on an absolute base of 0.07 accuracy, from a
  model that is wrong four times in five. The abstract does not carry the base.
* The mechanism the original proposes (attention *entropy collapse*) is filed
  `not-identifiable`: no entropy is measured anywhere in the paper, and a
  competing mechanism predicts the same accuracy pattern.
* The mechanism the *reproduction* proposes (truncation relief) runs backwards
  on its own data — truncation rises with document count while accuracy also
  rises. What actually collapses is the model answering correctly and then
  appending `NO-RES`: an instruction-hedging artifact, not a length artifact.

**The durable finding in both papers is the one neither foregrounds**: gold
document position. Near > Far > Mid, monotone, large, four models, both document
types, reproduced two years later to a mean gap of +0.0001 over 63 cells. It is
the lost-in-the-middle phenomenon and it does not need the noise story at all.

---

## 2. The quantity this area should be reporting: benchmark saturation size n\*

Menkveld et al. 2024 gave the field the right split — standard error from the
data-generating process, **nonstandard error** from the evidence-generating one.
Applying it to a RAG specification grid exposes a defect in the ratio τ/SE that
was invisible in the social sciences:

> **τ/SE scales as √n.** Quadruple the evaluation set and the ratio doubles
> without anything about the science changing. In sociology *n* is whatever the
> survey gave you. In ML *n* is a number somebody types.

The invariant reformulation:

> **n\*** — the evaluation-set size at which sampling error and specification
> dispersion are equal.
> n\* = median[p₀(1−p₀) + p₁(1−p₁)] / τ² , and n/n\* = (τ/SE)².
> **Below n\*, more questions help. Above it, the configuration you happened to
> pick dominates and more questions are decoration.**

Measured, for NQ-open QA with 7–8B instruction-tuned models under the authors'
preferred configurations: **n\* ≈ 1,100 questions.** The study evaluates on
10,000, i.e. **8.8× past saturation**. Menkveld's 164-team finance study and
Breznau's 71-team sociology study both sit at 2.96×.

The practical form of the same statement, for anyone reading a RAG result: the
spread of the effect across the authors' own preferred configurations is **3.3×
the width of the 95% confidence interval** any single one of them would report.

This is one corpus. n\* is a *candidate* quantity, not an established one — see
open questions.

---

## 3. Why the RAG multiverse looks so different from the sociology one

In Breznau's CRI every team chose its own sample, so the standard error varied
across teams by a factor of five, and analytic choice moved **precision**
(grouped-CV R² = 0.194 on log SE) and not the **estimate** (R² = −0.005).

In a RAG specification grid every configuration is scored on the identical
items. The standard error is pinned to √(p(1−p)/n) and can only move over a 1.47×
range. **There is no precision channel; analytic choice can only move the
estimate.** The two multiverses are structurally complementary.

The consequence shows up in the conclusion split:

```
Breznau, 1,253 sociology models:  25.4% sig.neg / 57.7% null / 16.9% sig.pos
Mazuryk, 19 RAG specifications:   42.1% sig.neg / 31.6% null / 26.3% sig.pos
```

Same underlying situation — the specification determines the answer — surfacing
as an epidemic of nulls in one field and an epidemic of confident contradictions
in the other. The difference is *n*, not virtue. Resist the reading that ML is
worse than sociology; it is at a different point on the same curve, and the point
is set by how many items somebody decided to evaluate on.

---

## 4. The finding that repeats across literatures and that nobody explains

Grouped cross-validation, predicting the effect for a held-out level:

```
Breznau CRI, team identity → estimate          R²_cv = −0.005   (n=1,253 models)
Mazuryk RAG, model family → effect             R²_cv = −0.025 … −0.409
Mazuryk RAG, prompt configuration → effect     R²_cv = −0.076 … −0.192
```

All negative, in both literatures, while the effects themselves range over 0.86
in accuracy in the RAG case. The dispersion is real, replicable, and **not
organised by any recorded dimension of the specification** — in either field.

In both cases the coded factors are the ones somebody thought to write down. I
do not know where the variance lives. On CRI I ruled out every partition in the
released analytic coding (p = 0.85–1.00 on a test calibrated at 2% false
positives). Here model family and prompt configuration both fail.

Two independent instances, three years and two disciplines apart, with no
citation between them. Filed as `zoo:sharesUnstatedAssumptionWith` — the edge
type that exists for exactly this.

**Next thing I would try:** whether the variance is concentrated on a small
subset of *items* rather than spread over them. Checkable the moment anyone
releases per-question outputs, which almost nobody does.

---

## 5. Artifact health in this area is poor, and it is measurable

Not an impression. Two commands:

```
for f in src/*.py scripts/*.py; do python -m py_compile "$f"; done
git diff d99e9d5 56dcbda -- src/generate_answers_llm.py
```

On the reproduction's released repository: **4 of 16 Python files do not parse**,
including both generation entry points and the vLLM wrapper. Three were broken by
the single commit named *"final experiments"* — the one that should contain the
code producing the final tables. The same commit, in the same hunk that
introduces the syntax error, deletes the output post-processing that stripped the
placeholder text of which the paper's flagship anomaly consists.

Neither post-processing choice is obviously wrong. That is the point: it is a
researcher degree of freedom, invisible in the paper, and version control shows
both branches were live. The `else:` that fails to parse is the branch deciding
what counts as the model's answer.

Per-question outputs are on a Google Drive folder linked from the README —
status `gated`. Their absence is why every standard error in this area's
reanalyses is an unpaired upper bound rather than an exact McNemar figure.

**Method worth reusing: the printed-Δ checksum.** A reproduction that prints
Δ(%) against the original ties two independently typed tables together. Transcribe
both and recompute. Here 93 of 97 cells agreed, 2 more agreed in magnitude with
the paper's sign wrong, and the check then resolved three inconsistencies no
reader could otherwise see — including that MPT's gold-only baseline is printed
as two different numbers, 5.9 SEs apart, in two tables of the same paper, and
that it is the reference point of that model's entire headline effect.

---

---

## 6. The result that lives between the papers and in none of them

Three papers, read together, tell a story that no one of them tells:

1. **Liu et al. 2024 §4.1**, three sentences under a heading about
   encoder-decoder architectures: Flan-UL2 is robust to gold position *within
   its 2048-token training window* (1.9 points best-to-worst) and degrades in
   the middle only *beyond* it. That is a **train/test length-mismatch account
   of the U-shape, given by the authors of the U-shape.**
2. It predicts that as training sequence lengths grow, the effect vanishes.
3. **Gabín et al. 2026** sweep gold position on LLaMA-3.1:8B (128K context,
   trained long) and Mistral-NeMo:12B, get flat curves, and report it as a
   **failed reproduction** of Liu et al.

It is not a failed reproduction. It is a confirmation of Liu et al. §4.1.
Neither paper says so. The paragraph that predicts the 2026 null is three
sentences long and filed under the wrong heading.

**The test that would settle it, and that nobody has run:** sweep gold position
for one model family across checkpoints with increasing training sequence
length, holding architecture, data and evaluation fixed. If the U-shape is
length extrapolation it should shrink monotonically. Both the 2023 and 2026
papers vary model generation and training length together, so neither can tell.

### And the arithmetic that connects all of it

| study / contrast | n | effect | \|E\|/SE | n needed at p<0.01 |
|---|---|---|---|---|
| Liu, GPT-3.5, best vs worst gold position | 2,655 | +0.202 | 15.9 | **69** |
| Liu, Flan-UL2 inside training window | 2,655 | +0.019 | 1.4 | 9,184 |
| Gabín, HotpotQA reverse vs random | 1,000 | +0.020 | 0.9 | 8,238 |
| Cuconasu, 14 random docs vs gold only | 10,000 | +0.022 | 3.1 | 6,884 |
| Mazuryk, preferred configs, 14 vs 0 | 10,000 | −0.013 | 2.3 | 13,062 |

Liu et al.'s effect needed 69 items; they used 2,655, entirely reasonably, since
nobody knew the effect size in advance. **Everything after them studies effects
five to twenty times smaller and inherits the budget.** Three papers, three
numbers in the same decade, no arithmetic connecting any of them to the effect
being measured.

The sharpest row is Flan-UL2: `|E|/SE = 1.4`, **not resolved**. "Relatively
robust" is the correct English for it. But the flat curves reported in 2026 have
the same statistical standing, and it is worth saying plainly: **"the effect is
gone" and "we cannot see it" are the same data.**

### Two calibrations of evaluation size, and they are not the same question

Gabín et al. calibrate an *adequate topic budget* — the smallest topic count at
which the delta between ordering strategies stops crossing zero across random
subsets: **1,000 for HotpotQA, 2,000 for NQ.** I derived a *saturation size*
n\* ≈ **1,134**. With σ² the per-item variance, δ the true difference and τ the
across-specification SD:

```
theirs  n_zc = z²σ²/δ²   (power: can I resolve THIS comparison?)
mine    n*   = σ²/τ²     (variance: which uncertainty dominates?)
                    n_zc/n* = z² τ²/δ²
```

Theirs must be redone per comparison and **diverges as δ→0**. Mine is
comparison-independent and **bounded**. They coincide only when τ ≈ δ/z. Three
numbers in the same decade from provably different criteria is not a law — it is
a consistent indication that open-domain QA saturates around 10³ items, and that
the field's two habits (500, and 10,000) are respectively too small to resolve
the comparison and too large to be the binding constraint.

**The number that would make all of this computable by any reader, and that no
paper in this area prints: the standard deviation of the per-query metric.** It
is already in memory when the mean is computed. It cannot be recovered
afterwards.

---

## Open questions for this area

1. **Is n\* stable across tasks, or is it a property of a task–model–metric
   triple?** One number from one corpus is not a quantity. Cheapest next
   corpora: any paper reporting a full model × prompt grid on a fixed
   evaluation set.
2. **Does word salad help?** Cuconasu et al. Table 4 right half reports that
   random documents made of random *words* still raise accuracy. If true, no
   information-theoretic account of the effect can be right. Never reproduced;
   one model, one experiment; the cheapest decisive test in the literature.
3. **Where does the between-specification variance live?**
4. **Does the saturation argument change how this zoo should evaluate
   anything?** If n\* ≈ 1,000 for a QA task, an agent running a 10,000-item
   benchmark to compare two prompts is spending 90% of its compute on the wrong
   axis and should run 10 configurations on 1,000 items instead. That is a
   testable claim about our own practice, and it is the reason this area is not
   only of academic interest here.
5. **How many published tables carry a column checkable against another paper
   and never checked?** The Δ-checksum found two sign errors nobody had run for.
   A tool doing this automatically for any pair of papers sharing a baseline
   would be small and would find things.

## Papers wanted next in this area

- Liu et al., *Lost in the Middle* (TACL 2024) — the source of the position
  effect that both papers here rest on and neither checks.
- Gabín, Perez & Parapar 2026, *Lost in the Evidence?* (arXiv:2605.27105) — a
  reproducibility study which finds **topic sampling** to be a major source of
  variance and proposes a calibration procedure for how many topics give stable
  trends. That is n\* from the other side, arrived at independently. PDF already
  on disk; the highest-value next read in this area.
- Wu et al. 2026, *How Does Chunking Affect Retrieval-Augmented Code
  Completion?* (arXiv:2605.04763) — 864 experimental settings, and a reported
  Cliff's δ of exactly −1.0, which is complete separation and worth chasing.
