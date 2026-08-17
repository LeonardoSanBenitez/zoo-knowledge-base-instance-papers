# Mazuryk et al. 2026, "The Powerless Noise" — notes

Author: maria, 2026-08-12.
Record: `paper.json`. Code: `reanalysis/01`–`06`. Data: `artifacts/*.csv`.

---

## What the paper is

A student reproduction, done properly and published at SIGIR '26, of Cuconasu et
al. 2024's finding that adding *random* documents to a RAG prompt improves
question-answering accuracy by up to 35% ("the Power of Noise"). The
reproduction confirms the effect inside the original's regime — 4-bit Llama-2
and MPT, a 15-token generation cap, a prompt that demands the model emit `NO-RES`
when it cannot answer — and then shows it evaporates once any of those three
constraints is relaxed.

The conclusion is right and I accept it. What follows is what I found underneath
it, which is more interesting than the conclusion.

---

## 1. The paper is a nonstandard-error study that does not know it is one

Menkveld et al. 2024 named the thing this paper measures: the **nonstandard
error**, dispersion of a result across the evidence-generating process rather
than the data-generating one. Mazuryk et al. have a fully crossed design — five
models × three prompt configurations × four document counts, every cell on the
same fixed 10,000 questions — which is a better instrument for that quantity
than most many-analysts studies, and they use it only to say "the effect is not
robust."

Running Menkveld's instrument over their Table 6 (`reanalysis/03`, `04`, `05`):

| specification subset | k | τ | τ / median SE | n\* | n/n\* |
|---|---|---|---|---|---|
| all 19 | 19 | 0.1480 | 25.3 | 16 | 639× |
| Table 6 balanced 5×3 | 15 | 0.1399 | 23.9 | 18 | 571× |
| Table 6 minus llama3/Base | 14 | 0.0202 | 3.5 | 811 | 12× |
| authors' preferred configs only | 10 | 0.0164 | 3.0 | 1134 | 8.8× |

against **1.72** for both Menkveld's 164 finance teams and Breznau's 71
sociology teams.

The honest headline is the bottom row, not the top: strip every cell anybody
would call a bug and the dispersion is still about twice the many-analysts
benchmark. The top row is carried by one broken cell and I say so in
`04_break_it.py` rather than quoting 25.3 anywhere.

### The quantity I would actually give somebody: n\*

τ/SE is not a property of a field. It scales as √n, so it can be doubled by
quadrupling the evaluation set while changing nothing. Inverting it gives
something invariant:

> **n\*** = the evaluation-set size at which sampling error and specification
> dispersion are equal = median·p(1−p)·2 / τ².
> Below it, more questions help. Above it, the configuration you happened to
> pick dominates and more questions are decoration.

For this task and these models, **n\* ≈ 1,100 questions**. The paper uses
10,000. Menkveld's and Breznau's studies sit at 3× saturation; this one is at
8.8× on its most conservative reading. `n/n* = (τ/SE)²`, so nothing is lost and
the number becomes readable.

I have not seen this reported anywhere in the RAG literature, and computing it
requires running more than one defensible configuration — which is exactly the
cost people avoid by choosing a large n instead.

---

## 2. The dispersion is real and is not organised by anything recorded

Grouped cross-validation (`05` §4), predicting a held-out level from the others:

    R²_cv(model family)         −0.025 to −0.409   across four subsets
    R²_cv(prompt configuration) −0.076 to −0.192

All negative. Knowing which of five 7B models you are using, or which of the
authors' prompt configurations, does not predict the Power-of-Noise effect for a
held-out level better than the grand mean does — while the effects themselves
range over 0.86 in accuracy.

**This is the same shape as my CRI result of 2026-08-12**, where team identity
predicted the estimate at R² = −0.005 grouped-CV across 1,253 sociology models,
and no partition in the released analytic coding absorbed the heterogeneity
(p = 0.85–1.00 on a test calibrated at 2% false positives).

Two literatures, three years and two disciplines apart, no citation between
them, and the identical structure: **large, real, replicable dispersion across
specifications that the recorded dimensions of the specification do not
explain.** In both cases the coded factors are the ones somebody thought to
write down. In neither case do I know where the variance actually lives. That is
the open question I am leaving this session with, and it is now a question with
two independent instances rather than one.

The relation is filed as `zoo:sharesUnstatedAssumptionWith` against
`breznau2022-hidden-universe`, which is the edge type I invented for exactly
this: two papers that never cite each other and stand or fall together.

---

## 3. Where the RAG multiverse is the *mirror image* of the sociology one

In CRI every team chose its own sample, so the standard error varied by a factor
of five across teams, and my result was that analytic choice moves **precision**
(R² = 0.194 for log SE) and not the **estimate** (R² = −0.005).

Here every specification is scored on the identical 10,000 questions. The
standard error is pinned to √(p(1−p)/n) and can only move over a 1.47× range,
entirely as a function of where accuracy sits on the p(1−p) parabola. **There is
no precision channel.** Analytic choice can only move the estimate.

So the two fields' multiverses are structurally complementary, and this is why
the conclusion splits look so different:

    Breznau, 1,253 sociology models:   25.4% sig. neg / 57.7% null / 16.9% sig. pos
    Mazuryk, 19 RAG specifications:    42.1% sig. neg / 31.6% null / 26.3% sig. pos

Same underlying situation — the specification determines the answer — surfacing
as an epidemic of nulls in one field and an epidemic of confident contradictions
in the other. The p-value is doing no work in either. What differs is only which
way n pushes it.

I want to keep this straight because the temptation is to say "ML is worse than
sociology". It is not worse. It is at a different point on the same curve, and
the point is set by how many items you decided to evaluate on.

---

## 4. The artifact audit, which is the part I did not expect

`python -m py_compile` on every Python file in the released repository at HEAD
(`f5a482d`):

    src/generate_answers_llm.py        IndentationError, line 216
    src/generate_answers_llm_mixed.py  IndentationError, line 253
    src/llm_vllm.py                    IndentationError, line 221
    src/compute_search_results.py      SyntaxError, unclosed paren, line 130

Four of sixteen. Both generation entry points and the vLLM wrapper. Git
archaeology across all six commits: the last one was broken from the very first
commit; the other three were valid at `d99e9d5` (2025-12-01) and were broken by
`56dcbda` (2025-12-15) — the commit whose message is **"final experiments"**.

And the same commit, in the same hunk that introduces the syntax error, deletes
this:

```python
# Skip lines that are mostly underscores or placeholders
if line.count('_') / len(line) > 0.7:
    continue
if 'extract' in line.lower() and ('token' in line.lower() or ...):
    break
```

That block strips exactly the output the paper's flagship anomaly consists of —
Llama-3-8B under the Base configuration producing `___ (extract max 5 tokens)`
in 73.6% of its outputs, giving 14.62% accuracy with the gold document alone and
an apparent Power-of-Noise effect of +0.53.

So the single most dramatic number in the paper is downstream of an undocumented
output post-processing choice that the project itself had made the other way a
fortnight earlier. Neither choice is obviously wrong. That is the point: it is a
researcher degree of freedom, it is invisible in the paper, and the version
control shows both branches were live.

The `else:` that fails to parse is the branch that decides what counts as the
model's answer. A reader cannot recover which side of it produced the tables.

---

## 5. Internal inconsistencies the paper's own Δ column exposes

The reproduction prints Δ(%) = (reproduced − original)/reproduced × 100 beside
every cell. Transcribing *both* papers and recomputing Δ (`reanalysis/06`) ties
two independently typed PDFs together through a number printed in one of them.
93/97 overlapping cells agree outright; 2 more agree in magnitude and carry the
**wrong sign in the paper** (one of them is MPT at 6 random documents in the
Near position, inside the Power-of-Noise column itself); 2 differ at the second
decimal of a percentage, which is rounding.

That checksum then settles three things nothing else could:

1. **Table 2 vs Table 7 at k = 12, 14.** They agree exactly at k = 0, 4, 6, 8,
   10 and disagree at 12 and 14. Δ says Table 2 holds the run the column was
   computed from; Table 7's entries are from some other execution. Gap: 0.0101
   and 0.0143, i.e. 1.5 and 2.1 standard errors, comparable to the whole effect.

2. **MPT's gold-only baseline is printed twice, differently.** Table 1 row 0 and
   Table 2 row 0 are the same condition — gold document alone. The original
   prints 0.2148 in both, as it must. The reproduction prints **0.2165 and
   0.1813**, and both printed Δs are internally consistent, so these are two
   real runs, 5.9 standard errors apart. Since that cell is the *reference
   point* of the Power-of-Noise claim for MPT, the effect at k = 8 is either
   +0.0443 or +0.0795 depending on which of the paper's own two printings you
   subtract. A factor of 1.8 in the headline quantity.

3. **MPT did not reproduce.** Llama-2 gaps against the original: mean +0.0001,
   sd 0.0015, max 0.0044 — a faithful re-execution. MPT gaps: mean −0.0123, sd
   0.0136, max 0.0342, systematically negative. The gold-only cell carries
   Δ = −18.48%, printed in bold. Section 4.1 says "We successfully reproduced
   the results of all three core experiments." Half of the models in those
   experiments missed their own baseline by 18% and the paper does not mention
   it.

---

## 6. Where I think the paper is actually wrong (claim c5)

The mechanism it proposes is truncation relief: the 15-token cap cuts off
correct answers, adding random documents makes the model less verbose, so
accuracy rises for a reason that has nothing to do with noise being useful.

Its own Figure 2 runs the other way for the configuration it is invoked to
explain. Llama-2 under `Instruct`: truncation *rises* from 53.6% to 68.8% of
incorrect outputs between 0 and 14 random documents, while accuracy also rises
from 9.10% to 22.87%. The repository's hallucination report shows the same
direction independently — TRIMMED_RESPONSE 22.6% → 36.6% of errors while
accuracy goes 55.42% → 62.33%.

What *does* collapse is DUAL_RESPONSE, 42.5% → 1.4%: the model answering
correctly and then appending `NO-RES`. So the **instruction-hedging** channel is
well supported and the **truncation** channel is not. The paper conflates them
under "restrictive prompt design", and the conflation matters because the two
have different fixes — one is a token budget, the other is a sentence in the
prompt.

Filed as `disputed`, not `refuted`: the overall conclusion (the effect is an
artifact of the inference setup) survives; the specific mechanism does not.

---

## 7. Two errors of my own, kept on the record

1. **Script 04 claimed Table 3 is on the 10,000-item sample.** Its forensic test
   never contained a single Table 3 value. Script 06 §5 runs it properly and
   reaches a hedged conclusion — the *reproduction's* Table 3 is off the k/2889
   grid at 7 of 58 values, which is real; the *original's* is off at 2 of 58,
   which one typo would produce, so I do not assert it. The overclaim is
   annotated in place in `04` and superseded in `06`, not deleted.

2. **I nearly reported a decoding confound that does not exist.** I read
   `generate_answers_llm.py` line 205 passing `repetition_penalty=1.1` on the
   vLLM branch and not on the HuggingFace branch, and started writing it up as
   an uncontrolled difference. `src/llm.py` line 137 hard-codes the same 1.1.
   Reading one call site and not the callee would have put a false claim in a
   permanent record. The rule that saved it is the boring one: open the file the
   function actually lives in.

---

## 8. What could not be done

No GPU, no model weights, no inference. Nothing here re-runs the pipeline; every
number is derived from the published tables, the repository's own aggregate
counts, and the code as text. The per-question generation results — which would
give paired discordance counts, hence exact McNemar standard errors instead of
the unpaired upper bounds used throughout — are on a Google Drive folder linked
from the README and are not retrievable without an interactive session. That is
the single biggest limit on this record and it is recorded as artifact `a5`,
status `gated`.
