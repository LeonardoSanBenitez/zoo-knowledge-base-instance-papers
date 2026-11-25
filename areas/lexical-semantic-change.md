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
`kokosinskii2024-deep-change-axolotl`, `yadav2025-xl-durel`, `mosolova2026-wsi-llm-era` (2026-11-06).
Read, record pending: rachinskiy2022 (GlossReader); PDFs in `paper-downloads/<id>`.

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
  (5) For one-definition decisions, a local LLM does well only as MULTIPLE CHOICE against its own induced inventory,
  after mapping its paraphrases of the target to the target (one call per word): DWUG DE Sense F1 0.92 (annotators vs
  each other 0.86); without the mapping the target loses to its paraphrase and F1 collapses to ~0.2 (F10).

**The trivial baseline's strength is a property of the sample (mosolova2026, reproduced 2026-11-06).** On SemCor-WSI
one-cluster-per-lemma (73.6 weighted F-B3) beats every unsupervised WSI system including GPT-4o direct clustering
(66.9); 28% of its instances belong to monosemous lemmas, and on the rest 1cpl scores 63.4. Target-word change
benchmarks select polysemous/changing words, so there 1cpl is weaker (SemEval-2027 Task 3 SV dev 1a 0.756 vs
XL-LEXEME clustering 0.82) -- but the lesson carries: BCubed rewards not splitting, and LLM inventories split
(arena-lsc F9). An external number of senses (Wiktionary) beats an internally chosen k there by 0.5-1.6 points.

**An LLM sense inventory does not reproduce usage-graph clusters (arena-lsc, 2026-11-06; own experiment, not a paper).**
Gemma 4 12B induces 2-6 definitions per word and assigns usages by multiple choice. On two-period DWUG subsets
(ES/EN/IT, 172 words) it loses to XL-LEXEME average-linkage clustering on BCubed (-.16) and on the change ranking
(Spearman of JSD, -.17, CI < 0); its sense count correlates with the gold count worse than the clustering's. It gained
on the change ranking only on two definition-annotated sets (10 + 24 words). Tested the same day on definition-based gold
(AXOLOTL-24 Finnish, 133 words): it loses there too (BCubed -.05; change ranking -.21, CI [-.44, +.01]), so the gold
type alone is not the explanation. Not settled, though: every held-out set has 2 periods (between-word ranking only),
while the 10-word gain sits on multi-period data with the task's own protocol; simulated 10-word dev sets drawn from the
held-out sets almost never show a CI > 0 gain when the true difference is -0.2 (arena tooling/tiny_dev_coverage.py). Gemma 4 12B also loops while listing senses on
22% of Finnish words (7% Spanish). Evidence: `.claude/memory/maria/arena-lsc/tickets/2026-11-06-InventoryBreadth/OUTCOME.md`,
`.../2026-11-06-InventoryDefGold/OUTCOME.md`.

## Method rules for this area

1. Report every change score beside random-within-gold-k and the system's own shuffled-input score.
2. State the clustering linkage and threshold; "agglomerative, 0.5" without a linkage is not reproducible.
3. Benchmarks with one period pair per word cannot separate change modelling from polysemy counting.
4. On a 132-word test, 1b differences under ~0.07 rho and 1a differences under ~0.01-0.02 are within word-sampling
   noise (arena-lsc Ceiling, test-like resampling).
5. Multi-label output (arena-lsc MultiLabelAssign, 2026-11-24): 13.2% of SV-dev gold usages (task protocol) carry 2-3 sense labels, public DWUG/AXOLOTL conversions none. Adding the nearest other cluster as a second label lowers 1a monotonically on SV dev, and an oracle choice of which usages get it gains only +0.0025 (10 words, one clustering system).
6. Post-processing of XL-LEXEME vectors before average linkage (arena-lsc EmbeddingPostprocess, 2026-11-24; leave-one-set-out over seven public sets): set-mean centring +0.0006, removing 1/3/10 principal components -0.001/-0.003/-0.020, a consensus over thresholds +0.0005; centring helps EN/ES/IT (+0.02..+0.03) and hurts FI (-0.05), so the effects cancel and no oracle-threshold macro improves.

7. A decoder LLM as a third encoder (arena-lsc LLMHiddenEncoder, 2026-11-24): Qwen3-4B-Base hidden state of the last token after a one-line prompt (layer 30), concatenated at weight 0.25 with XL-LEXEME, raises leave-one-set-out 1a over seven public sets from 0.7455 to 0.7612 (+0.0157 [+0.0083, +0.0233]) and lowers 1b (0.554 to 0.487); a within-word-shuffled copy of the LLM vectors already gives +0.006..+0.009, so the usage-level part is about +0.010 (qualified by item 10: with a second LLM the usage-level part is +0.003 [-0.002, +0.009], not significant). It did not beat XL-LEXEME + XL-DURel on IT/FI/RU (+0.032/-0.059/-0.001).

8. LLM-induced inventory vs clustering on 1b with 10 periods (arena-lsc InventoryMultiPeriod, 2026-11-24): 40 fresh synthetic words, +0.028 [-0.166, +0.228]; with the earlier 20 pooled -0.049 [-0.188, +0.099]; both systems below the random-labels-within-gold-k 1b. The 10-period question the held-out two-period sets cannot answer is still open; the CI is too wide at this size. (Answered on real multi-period gold by item 13, 2026-11-25: the inventory loses clearly.)

9. A second LLM in the Subtask-2 pipeline (arena-lsc SecondLLM, 2026-11-24): Qwen3-14B Q4 with the prompts tuned on Gemma 4 12B Q4 scores below it on SV dev, DE sense and RU (per-word macro F1 .503/.708/.600 vs .622/.894/.646), and mean-score, AND and OR combinations are not better than Gemma alone (pooled -0.033 [-0.067, +0.001] for the mean score). The two models' errors are correlated (phi .32-.39 on SV dev and RU), so agreement between them is not independent evidence.

10. Replication of item 7 with Qwen2.5-3B (arena-lsc LLMEncoderReplication, 2026-11-24), configuration fixed in advance: +0.0110 [+0.0043, +0.0180] 1a over XL-LEXEME (seven sets, leave-one-set-out), but vectors permuted within each word give +0.0077/+0.0143/+0.0076 (paired real minus shuffled +0.0033 [-0.0019, +0.0090]): the gain is mostly a word-level effect of the LLM space (which also holds for item 7: its usage-level part is +0.003..+0.010). Same model family only; no gain over XL-LEXEME + XL-DURel on IT/FI/RU.

11. Isolating item 10's word-level component (arena-lsc WordLevelCut, 2026-11-24): a per-word cut for XL-LEXEME from the concentration (or offset) of the word's centred Qwen3-4B vectors does not improve leave-one-set-out 1a (-0.0032 [-0.0094, +0.0029]; permuted-statistic control -0.0010), although the learned slope has the predicted sign in every fold. The mechanism behind the shuffled-ensemble gain is therefore not a monotone cut shift.

12. What the within-word shuffle of item 10 keeps (arena-lsc OffsetNoiseControl, 2026-11-24): the word's mean offset alone gives -0.0040 (a rescaling, the control); offset plus Gaussian spread gives +0.0093 [+0.0029, +0.0158] with Qwen2.5-3B (shuffle reference +0.0099) but -0.0070 [-0.0141, +0.0004] with Qwen3-4B (reference +0.0077). The word-level component is model-dependent and not identified.

13. Multi-period human gold built from public data (arena-lsc YearResplit, 2026-11-25): DWUG EN/DE/SV/IT usages carry their year, so each word's usages can be re-binned within each original epoch into near-equal-count bins of >= 18 (at most 5 per epoch), giving 2-10 periods with a median of 20 gold usages per period (SemEval-2027 Task 3's sample size) and 1078 consecutive pairs instead of 165. On it: (a) a leave-one-set-out cut for XL-LEXEME + XL-DURel average linkage does not beat 0.44 (dU +0.10 [-0.35, +0.57] on U = 1a/0.041 + 1b/0.120); (b) the Gemma 4 12B induced inventory is far worse than clustering on 3-5-period subsets (1b 0.46 vs 0.81 EN, 0.41 vs 0.58 IT; 1a -0.18), which answers item 8 for practical purposes; (c) caveat: random labels within the gold sense count already score 1b 0.59-0.81 there (0.31-0.45 on the task's own dev set), because within-epoch periods carry little real change, so this proxy over-rewards getting the sense count right.

14. A supervised probe on decoder-LLM hidden states (arena-lsc LLMProbe, 2026-11-25): a linear map trained leave-one-set-out with a within-word contrastive loss on other sets' cluster gold, concatenated to XL-LEXEME, gains +0.024 (Qwen3-4B) and +0.018 (Qwen2.5-3B) 1a over seven public sets, but the same probe trained on labels permuted within word gains +0.014/+0.015 (real minus shuffled +0.003, CI spans 0 for Qwen2.5); on top of XL-LEXEME + XL-DURel it adds +0.003 [-0.003, +0.011] (Qwen3) and -0.009 [-0.014, -0.003] (Qwen2.5). Together with items 7 and 10-12: the decoder-LLM route adds nothing usable to a two-encoder WiC ensemble at this resolution (one linear probe architecture tested). Method lesson in instance-general ai-evaluation/a-gain-must-beat-its-own-shuffled-copy.md.

## Open questions (carried by records)

- Does incremental clustering beat one-time clustering on multi-period gold? (`periti2024-multi-period-dwsi`) Partly answered, arena-lsc ticket 2026-11-24-TimeAwareClustering (2026-11-24, XL-LEXEME, synth300 = 300 English words x 10 periods, 2-fold cross-fitted parameters): period-by-period incremental clustering 0.634 vs one-time average linkage 0.642 (-0.008, 95% CI [-0.016, -0.001]); a time term added to the distance, -0.001 [-0.008, +0.005], and 1b -0.035. Synthetic data and 10 real SV words only: not settled for real corpora.
- What F1 does the organisers' prototype-cosine Subtask-2 method get? (`cassotti2025-hypothesis-driven-lsc`)
- Why does PRT not reproduce? (`saponara2026-synthetic-multi-period-lsc`)
