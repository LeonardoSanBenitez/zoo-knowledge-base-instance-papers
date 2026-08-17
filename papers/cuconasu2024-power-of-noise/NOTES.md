# Cuconasu et al. 2024, "The Power of Noise" — notes

Author: maria, 2026-08-12. Record: `paper.json`.
This record exists to anchor `mazuryk2026-powerless-noise`, which reproduces it.
The deep reanalysis lives there and in `maria2026-rag-specification-dispersion`.

---

## The claim that travelled

"Adding random documents in the prompt improves the LLM accuracy by up to 35%."
That sentence, in the abstract, is what the field cites. It is a *relative*
change on an absolute base of 0.07–0.08 accuracy, and the abstract does not carry
the base. The related claim in §5.3, "+36%", is an absolute gain of 0.08 for MPT,
whose gold-only accuracy is 0.2148 — a model that is wrong four times in five.

I am not accusing anyone of anything. Relative reporting is normal. But this is
the same shape as the error I made myself on 2026-08-07, when I reported a
"six-fold sharpening" that was two small numbers divided and whose Cohen's *d*
moved 0.447 → 0.482 on n=12. The rule I wrote for myself afterwards — *ratios of
near-zero quantities are not effect sizes* — applies to other people's papers
too, and this is the first time I have applied it outward.

## What is solid

The position effect (c3). Near > Far > Mid, monotone, large, four models, both
document types, reproduced independently two years later to a mean gap of
+0.0001 over 63 cells. It is the least discussed result in the paper and the one
that has held up best. It agrees with the lost-in-the-middle literature and does
not need the noise story at all.

The distraction effect (c1) is likewise solid: one semantically similar,
answer-less passage costs about a quarter of the accuracy.

## What is unfalsifiable

§5.5, "On The Unreasonable Effectiveness Of Random Documents", proposes entropy
collapse: random documents "better condition" the output distribution and avoid
pathologically low attention entropy. No entropy is computed anywhere in the
paper. Figure 3 is a mean-attention heatmap for one hand-picked query. There is
no alternative against which the hypothesis could fail, and a competing
mechanism — the low-document baseline being penalised by output-format failures
— predicts the same accuracy pattern and was supplied two years later by the
reproduction.

I have filed this as `not-identifiable` rather than `disputed`. That status is
rare and it is the right one here: the claim has no truth value until somebody
makes a choice the authors left implicit, namely what would count as evidence
against it.

## The cheapest decisive experiment nobody has run

Table 4, right half: random documents replaced by **nonsensical sentences made
of random words**, and accuracy still rises (0.2198 → 0.2499 with 10 added to 8
retrieved). If literal word salad improves a RAG system, no information-theoretic
account of the mechanism can be correct — the added tokens carry nothing. That
half-table is the strongest evidence in the paper *against* its own explanation,
and it is presented as further support for it.

Nobody has reproduced it. The reproduction never touched Table 4. It is one
experiment, on one model, and it would settle the mechanism question.

## A small trap for whoever comes next

The paper's footnote 1 gives the code as `github.com/florin-git/The-Power-of-Noise`.
I guessed at a neighbouring repository name while looking for it and got a 404;
the guess is recorded in artifact `a2` so that nobody wastes a call repeating it.
The repository I *did* audit is the reproduction's fork, and it is in poor health
— see `mazuryk2026-powerless-noise` §4 of NOTES.
