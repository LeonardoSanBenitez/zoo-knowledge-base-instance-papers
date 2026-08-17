# Gabín, Perez & Parapar 2026, "Lost in the Evidence?" — notes

Author: maria, 2026-08-13. Record: `paper.json`. Code: `reanalysis/07_two_calibrations.py`.

---

## Why I read this immediately after the Powerless Noise work

Hours after deriving a **benchmark saturation size** n\* = 1,134 questions from
Mazuryk et al.'s specification grid, I found a paper that calibrates an
**adequate topic budget** by a completely different route — smallest topic count
at which the F1 difference between ordering strategies stops crossing zero
across random subsets — on different datasets, with a different metric, and
arrives at **1,000 topics for HotpotQA and 2,000 for NQ**.

Three numbers in the same decade from two unrelated derivations is either a
regularity or a coincidence, and the way to tell is to write both criteria down.

## The two criteria are not the same quantity

With σ² the per-item variance of the paired difference, δ its true value, τ the
SD across defensible specifications, z the demanded separation:

```
theirs   n_zc = z² σ² / δ²        mine   n* = σ² / τ²
                        n_zc / n* = z² τ² / δ²
```

They coincide only when τ ≈ δ/z, and there is no reason for that in general.

* **n_zc is a power calculation.** Is my evaluation big enough to resolve *this*
  comparison? Must be redone per comparison. **Diverges as δ → 0** — an
  arbitrarily small true difference demands an arbitrarily large evaluation set.
* **n\* is a variance-decomposition threshold.** Which source of uncertainty
  dominates? Comparison-independent, and **bounded**: past σ²/τ² the answer is
  limited by which pipeline you chose, not by how many questions you asked.

Reporting only n_zc lets you spend the whole budget resolving an effect twenty
times smaller than the spread across configurations — a difference the next
configuration change will overturn. Reporting only n\* lets you declare 1,100
sufficient and then fail to resolve the comparison you actually care about.

**They are complementary. Neither field reports both.**

## I reconstructed their budget to check I had understood them

`reanalysis/07` simulates 10 subsets at their sizes and asks how often all ten
share a sign. At a plausible per-item SD of 0.30:

| δ | n=500 | 1000 | 2000 | 3000 | 5000 |
|---|---|---|---|---|---|
| 0.020 (HotpotQA) | 0.50 | **0.84** | 0.99 | 1.00 | 1.00 |
| 0.010 (NQ) | 0.08 | 0.20 | 0.49 | 0.71 | 0.92 |

Their HotpotQA budget of 1,000 lands where the larger effect first stabilises.
Their NQ budget of 2,000 is more permissive than a strict all-ten rule would
give, which matches their own wording — they *minimise the frequency* of
crossings rather than requiring zero, and read it across all pairs and context
sizes rather than the hardest one.

Right decade for the right reason. That is evidence I have read them correctly,
not a claim to have reproduced their number: σ is a guess and δ is read off a
plot.

## What their own figures imply for the quantity they did not compute

Their Figure 9 plots ΔF1 = F1(reverse) − F1(standard) across six model families
and sizes. **That is a specification grid**, and the spread of ΔF1 across it *is*
τ. Reading τ ≈ 0.025 gives n\* in the hundreds to low thousands for their own
setting — overlapping their calibrated 1,000–2,000, and overlapping my 1,134
from a different corpus.

So their two halves are consistent with each other, which they had no way to
check, because they never wrote τ down.

**Three independent routes to the same decade.** I want to be careful about what
that licenses: three numbers, two from one paper, criteria that are provably
different. It is not a law. It is a consistent indication that open-domain QA
evaluation for 4–70B models saturates around 10³ items — and that the field's
two habits, **500** (Cao et al. and much industry work) and **10,000**
(Cuconasu, Mazuryk), are respectively too small to resolve the comparison and
too large to be the binding constraint. The 10,000 habit is the more expensive
mistake and the less discussed one.

## This paper forced an edit to a record I wrote yesterday

I had written that Cuconasu et al.'s gold-position effect (Near > Far > Mid) was
"the most durable finding in the paper" — large, monotone, four models,
reproduced to a mean gap of +0.0001 over 63 cells.

Gabín et al. §4.1 **fails to reproduce it**: "we do not recover a clear U-shaped
curve: accuracy remains comparatively flat across positions". Figure 4 repeats
the failure for the follow-up claim on standard NQ and HotpotQA.

This is not a refutation and getting that right matters. Cuconasu measured on
Llama2-7B and MPT-7B at 4-bit with a 15-token cap; Gabín measured on
LLaMA-3.1:8B and Mistral-NeMo:12B unquantised. Different populations. And
Cuconasu's effect is *enormous* — 0.3781 Near against 0.1795 Mid at 18
distracting documents. An effect that large does not vanish through noise. It
vanishes through the population changing.

Correct action, taken: **`cuconasu2024-power-of-noise#c3` moved from `accepted`
to `accepted-narrower-scope`**, `by` this record. The resulting statement is more
interesting than either paper's: the position effect is a property of the
2023-generation 7B models under aggressive quantisation and tight decoding.
Which is this whole area's lesson again — an effect indexed to an inference
regime, reported as a property of RAG.

This is the KB doing the one thing a pile of PDFs cannot.

## Two things I hold against an otherwise careful paper

1. **Every result is a figure. There is not one numeric table.** Every quantity
   in this record is an eyeball estimate with about one significant figure, and
   no amount of care on my side changes that. The virtual-appendix repository
   does not fix it: 10 notebooks, 26 PNG figures, **zero** dataframe or table
   outputs, and a README that says the result files are too large to upload and
   are available on request. Re-executable in principle — with an A100, an
   Ollama server and Terrier indices — and not re-analysable at all. Recorded
   `present-but-insufficient` for both artifacts.

2. **The "random" ordering is one permutation, not an average.** Their notebook
   sets `random.seed(1234)` inside the shuffle function with the comment "Always
   use the same random sorting seed". So `random` is a single fixed draw. Part
   of the reported ordering spread could be a property of that draw. This is
   invisible in the paper and I only know it because they released the code —
   which is an argument for releasing code even when the results files are too
   big, and I want to say so plainly rather than only complain about item 1.

## Where they overreach by exactly one clause

§4.2 attributes their disagreement with Cao et al. to "evaluation choices such
as limited topic coverage **and reliance on LLM-based judges**". Their own
250-topic pilot compared F1-token against an LLM judge and found "near-identical
ordering gaps ... the relative separation between ordering schemes is essentially
unchanged". So their evidence supports the topic-coverage half and *refutes* the
judge half, and the sentence states both as though equally supported.

Small. But it is the same failure I keep finding and keep committing: the
conclusion written beside the comparison rather than computed from it.

## Credit where it is unusual

They report their compute cost: **160 A100-80GB hours, 22.6 kgCO₂eq, carbon
intensity 0.432 kgCO₂/kWh, 0% directly offset.** I have now read four papers in
this area and this is the only one that says what it cost. It belongs in the
`cost` block of this record for the same reason our schema has one.
