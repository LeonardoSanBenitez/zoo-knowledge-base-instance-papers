# Local position sweep on the released prompts -- plan fixed 2026-10-17 08:05, BEFORE any call (not yet launched)

Purpose: produce the per-question outputs this area lacks (open question 2 of this record), at a size one local GPU
can finish in a session, and test c1 (U-shape) and c2 (20 documents < closed-book) with paired exact tests.
Model: qwen3.5:4b via local Ollama (same settings as maria2026-word-salad-noise-test: greedy, seed 0, think off),
num_ctx large enough for 20 documents (8192). Data: the repository's 20-document NQ-open prompts (gold at positions
0, 4, 9, 14, 19) plus the closed-book prompt, for the FIRST 200 questions of the released order.
Calls: 200 x 6 = 1,200. Metric: the paper's (any gold answer string in the output) AND exact-match after
normalisation, both reported -- open question 3 of this record asks how much the metric matters.
PRIMARY:
  P1 U-shape: accuracy(position 9) < mean(accuracy(position 0), accuracy(position 19)); paired, exact sign test on
     per-question (mid - ends/2) scores; prediction: holds (it is the paper's most replicated result).
  P2 c2: accuracy(position 9) - closed-book; exact McNemar; prediction: NOT below closed-book for this model.
Holm over P1, P2. Secondary: the same with exact-match; the paired/independent variance ratio for each contrast
(calibration for the n* bounds of maria2026-rag-specification-dispersion).
Stop rule: all 1,200 calls or the session's end; analyse complete questions only (all 6 conditions).
