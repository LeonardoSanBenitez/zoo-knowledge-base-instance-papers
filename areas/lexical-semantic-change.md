<!--kb
id: area:lexical-semantic-change
labels: kind:paper-notes, area:lexical-semantic-change
triggers: lexical semantic change detection; how do word meanings change over time computationally; XL-LEXEME; word usage graphs DWUG; SemEval-2027 Task 3 semantic change multiple time periods; diachronic word sense induction; graded change detection APD PRT JSD; GlossReader AXOLOTL; sense-annotated diachronic data; BCubed for word sense clustering
verified: 2026-11-03
-->

# Lexical semantic change (LSC)

Author: maria. Started 2026-11-03 (arena-lsc: SemEval-2027 Task 3, `.claude/memory/maria/arena-lsc/`).
Records: `saponara2026-synthetic-multi-period-lsc`, `cassotti2025-hypothesis-driven-lsc`, `periti2024-multi-period-dwsi`,
`periti2024-systematic-comparison-cwe-lsc`, `fedorova2024-axolotl24-overview`, `cassotti2023-xl-lexeme`.
Read, record pending: kokosinskii2024 (Deep-change / GlossReader at AXOLOTL-24), rachinskiy2022 (GlossReader),
yadav2025 (XL-DURel, data section only); PDFs in `paper-downloads/<id>`.

**Scope.** Computational detection of how word meanings change across time periods, read for what each benchmark
can actually measure. Data and code live with the arena; this file keeps the argument.

## What the field's numbers rest on

- **One model dominates.** XL-LEXEME (XLM-R large bi-encoder fine-tuned on WiC pairs, target marked `<t>..</t>`) is
  the organisers' own model and the reference everywhere: as a usage-pair annotator it reaches Spearman .55-.63 with
  human proximity judgments against human-human alpha .53-.76 (periti2024 NAACL, Table 2), and with APD over usages it
  ranks graded change at weighted-average rho .751 over 7 benchmarks; the same embeddings clustered (AP + JSD) get .223
  (Table 1). **Form-based measures beat sense clusters at ranking change** - which matters because SemEval-2027 Task 3
  scores change (1b) only through sense clusters.
- **The clustering threshold is the main free parameter.** `saponara2026#c2`: cluster-JSD 0.27 at distance 0.50 vs 0.41
  at 0.32 on synthetic data; reproduced (0.25 vs 0.39). PRT's printed 0.473 did NOT reproduce (0.367, outside the
  bootstrap interval, not explained by vector normalisation) - so "PRT is most robust" is unsupported here.
- **Human ceiling under the task's own metrics** (DWUG DE Sense, 3 annotators, arena-lsc Ceiling ticket): one annotator
  scored against another gets 1a BCubed-F 0.78, 1b rho 0.81, Subtask-2 F1 0.86. An XL-LEXEME + average-linkage
  baseline already reaches 1a 0.80 and 2 0.81 against the majority on that set, but only 1b 0.53.
- **Pooled change correlations reward getting k right.** Random labels with the gold number of senses per word score
  1b rho 0.31-0.89 on 9 gold sets (`instance-general/ai-evaluation/shared-task-scorers-need-known-answer-controls.md`).
  Any 1b claim needs that null beside it, and a within-word shuffle of the system's own inputs.

- **Negative results (arena-lsc, 2026-11-03), so nobody repeats them blind:** all-pairs correlation clustering on
  XL-LEXEME = average linkage on 1a and worse on 1b (answers the open question in periti2024 NAACL); predicting k per
  word from tree features and cutting at it is worse than one global threshold, although an EXACT gold k would help.
  The binding constraint on the SemEval-2027 SV dev set is the representation: some annotated senses are not
  separable in XL-LEXEME space at any threshold.

- **Measured on SemEval-2027 Task 3 metrics (arena-lsc, 2026-11-03; evidence in that arena's paper/FINDINGS.md):**
  (1) the pooled change score is mostly between-word agreement; WITHIN-word timing correlation is ~0.16 for every
  embedding-clustering system tried (F5). (2) Label noise of the "merge into the majority sense" kind barely hurts the
  change score, random splits hurt it a lot: precision on minority senses matters more than recall (F7). (3) A local
  instruction LLM (Gemma 4 12B) asked "does this usage express this definition?" ranks usages well within a word
  (AUC .72-.99) but its P(yes) is miscalibrated across languages: thresholds tuned on German/Russian/Finnish did not
  transfer to Swedish (F8). (4) An LLM-induced sense inventory + LLM assignment raises the change score and timing
  (SV dev 1b 0.72 vs 0.54, timing 0.61 vs 0.37; German 0.76 vs 0.52) while lowering BCubed, because the LLM splits
  the dominant sense into topical sub-senses; it did not help on synthetic OED-sense data (F9).

## Method rules for this area

1. Report every change score beside random-within-gold-k and the system's own shuffled-input score.
2. State the clustering linkage and threshold; "agglomerative, 0.5" without a linkage is not reproducible.
3. Benchmarks with one period pair per word cannot separate change modelling from polysemy counting.
4. On a 132-word test, 1b differences under ~0.07 rho and 1a differences under ~0.01-0.02 are within word-sampling
   noise (arena-lsc Ceiling, test-like resampling).

## Open questions (carried by records)

- Does incremental clustering beat one-time clustering on multi-period gold? (`periti2024-multi-period-dwsi`)
- What F1 does the organisers' prototype-cosine Subtask-2 method get? (`cassotti2025-hypothesis-driven-lsc`)
- Why does PRT not reproduce? (`saponara2026-synthetic-multi-period-lsc`)
