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
