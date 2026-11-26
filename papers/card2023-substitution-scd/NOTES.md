# card2023-substitution-scd — notes (maria, 2026-11-27)

Author: maria

## What it does
Per mention of a term: mask it, take BERT's top-5 substitutes (stopwords and word pieces excluded). Per period: the distribution of substitutes over all mentions. Raw change = JSD between periods. Final score = quantile of the raw JSD among ~10,000 random background terms of similar frequency (within factor 2). Best average Spearman over GEMS + SemEval-2020 EN/DE/LA/SV, by small margins.

## Why it matters to arena-lsc
It is the one LSC method that corrects JSD against an empirical null, here for frequency (n). The plug-in bias formula says K (diversity) drives the bias as much as n; the correction ignores K. Our 1b gold has the same structure at much smaller n (~20 per period), with K = number of senses.

## Planned reproduction (reduced scale, decided 2026-11-27 night)
Goal: the missing ablation, raw vs frequency-scaled JSD, on SemEval-2020 English (37 targets, gold graded scores in the corpus zip).
Scale-downs, each stated in advance: bert-base-uncased (paper: bert-large-uncased per appendix? check), NO continued MLM fine-tuning in the first pass (a second pass with fine-tuning if the first runs), max 500 mentions per term per corpus (paper 4,000 total), 2,000 background terms (paper 10,000), top-5 substitutes, F = 2.
Pre-registered readout: Spearman(raw JSD, gold), Spearman(scaled, gold), and Spearman(scaled with a K-matched null, gold) where K = number of distinct substitutes. No claim of reproducing .547 at this scale; if scaled comes out within .1 of .547 that is recorded as consistent, not reproduced.
Scripts go in reanalysis/; downloads in paper-downloads/card2023-substitution-scd.
