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

Operational (added 08:05, before launch): qa_data/20_total_documents/nq-open-20_total_documents_gold_at_{0,4,9,14,19}.jsonl.gz
are ~15 MB each (76 MB total). Stream only the first 200 records of each with Python gzip over HTTP (no large file
stored, so no assets.py registration needed); closed-book prompts are built from qa_data/nq-open-oracle.jsonl.gz
(0.9 MB) questions. Pin the repository commit SHA at launch.

## Launch log (append-only)
- 2026-11-12 ~12:35Z: pilot N=2 -> `out/l1_pilot_n2.jsonl` (12 calls, 129 s wall; 3.3-22 s per call, first call
  includes model load). Pilot is NOT part of the analysis. Observed: the model is verbose and `num_predict: 32` can cut
  an answer before the gold string. This is a fixed property of the pre-registered runner and applies equally to every
  condition, so paired contrasts stay fair. Absolute accuracies are a lower bound and are reported as such.
- 2026-11-12 ~12:37Z: full run launched, pinned repo SHA 29b8a6d042ce29abccee3db1a73171a107d7e6af, model qwen3.5:4b
  (Ollama 0.40.11), N=200 -> `out/l1_local_positions.jsonl`, log `out/l1_run.log`. Expected wall ~3.3 h.
  Analysis script (`l2_analyse.py`) is written while the run is going, against the plan above, without looking at outputs.
- 2026-11-12 ~12:50Z, DEVIATION decided on synthetic data only, before any real output was read: **P1's pre-registered
  "exact sign test on (mid - ends/2)" is invalid.** Under H0 (all positions the same accuracy p), the sign of d is
  not 50/50 unless p = 0.5: P(d>0) = p(1-p^2) and P(d<0) = (1-p)(2p-p^2), so at p = .6 they are .384 vs .336. The
  sign test tests a median of 0, not a mean of 0. `l2_analyse.py --selftest` measured it: 110/1000 false positives
  at alpha .05 in null worlds. The bias runs toward "mid better" when p > .5, i.e. AGAINST the predicted U, and
  toward the U when p < .5. Replaced by an exact within-question permutation test over the labels {0, 9, 19}
  (H0: the three scores are exchangeable within a question): 44/1000 false positives, and power 177/300 vs the
  sign test's 99/300 for a 10-point U at n=200. Both p-values are reported; the permutation p is primary and enters
  Holm. P2 (McNemar) unchanged: 44/1000.
- Correction to the two timestamps above: from file mtimes, the pilot ended 12:24:23Z and the full run started 12:24:36Z (I had estimated 12:35/12:37). The deviation note was written at ~12:50Z, about 25 min into the run. The outputs were not opened, only line counts and per-call seconds. Expected end ~15:35Z at ~9.5 s/call.
- 2026-11-12 15:42Z: run complete (1,200/1,200, exit 0). Analysis: `l2_analyse.py out/l1_local_positions.jsonl > out/l2_analyse.json`. P1 holds (permutation p .0003; sign test as pre-registered .0002, reported but invalid). P2 holds (mid not below closed-book; +0.19, McNemar 2e-6). Holm applied.
