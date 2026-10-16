# Word-salad experiment — analysis plan, fixed 2026-10-16 15:46 BEFORE looking at any outcome
Author: maria. Written after 32 of 600 planned questions had completed; no outcome inspected
(only per-call timings, checked at 5 questions to diagnose speed).

Stop rule: analyse whatever has completed at 17:45 local, or 600 questions, whichever comes first.
No interim significance tests.

Primary contrasts (paired, same questions):
  C1 (gold + 5 word-salad docs) vs C0 (gold only)   -- the Power-of-Noise word-salad claim (cuconasu2024#c4)
  C2 (gold + 5 unrelated Wikipedia passages) vs C0 -- the random-document claim (cuconasu2024#c2)
Test: exact McNemar (binomial on discordant pairs), two-sided; report difference in accuracy with
a 95% CI (Newcombe/Tango for paired proportions, or bootstrap over questions, 10,000 resamples).
Secondary: C1 vs C2; NO-RES rate per condition; answer-length per condition.

Pre-stated interpretation:
- Cuconasu's word-salad effect is +3.0 points (0.2198 -> 0.2499) in a different setting
  (8 retrieved + 10 added, Llama2). If C1 - C0 is >= +2 points with a CI excluding 0, that is a
  replication in this setting; if the CI excludes +2 points, it is evidence against an effect of
  that size HERE. Otherwise inconclusive at this n, and I say so.
- One small local model (qwen3.5:4b), the gold-oracle setting, K=5: a narrow test.
  Nothing generalises beyond that without more models.

## Addendum 2026-10-16 20:01 -- second model, fixed before any gemma4 outcome is seen
Replication with gemma4:latest (local, 9.6 GB). Identical design, prompt, seeds and question order; N fixed at the FIRST 200
questions of the same shuffled order (time budget). Same tests (exact McNemar, bootstrap CI). Interpretation: report as a
second model; with n = 200 only effects of ~ +/- 5 points are detectable; anything smaller is inconclusive and said so.
One timing call on question 0 (gold only and gold + 5 real docs) was made to measure speed; its correctness was seen
(correct in both) and question 0 is included as usual.
