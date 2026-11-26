# schlechtweg2024-more-dwugs — notes (maria, 2026-11-27)

Author: maria

## What the paper does
Continues the SemEval-2020 DWUG annotation for EN/DE/SV for two more rounds (V2, V3), re-annotates DiscoWUG, and resamples 15 words per language with 25 fresh uses per period, annotated densely with random edges (DWUG resampled). Tests cluster validity over rounds (against DWUG DE Sense and against V3), robustness to random edges, and replicability (Table 4). Conclusion: more edges beat more uses; V3 is near-optimal; the cheap resampled procedure approximates the SemEval result.

## Why I read it
arena-lsc F37 says the SemEval-2027 Task 3 change gold (~20 uses per period) is mostly sampling noise by a permutation test. This paper's resample is a real human replication at that sample size.

## Breaking it (what I ran)
- `reanalysis/table4.py`: Table 4 approximately reproduced (per-period reading closest). Its distance compares frequency-sorted profiles after trimming, so (i) every zero is a word with one cluster on one side, by construction; (ii) a different-word control gives about the same distance on SV. Table 4 shows similar frequency profiles, not recovered senses. -> c1 disputed.
- `reanalysis/resample_replication.py`: the replication the paper did not report, i.e. do graded change SCORES agree across the two usage samples? Spearman .79 EN / .80 DE / .65 SV (n = 15 each, wide CIs). Usage sampling alone predicts .82 / .93 / .90. DE and SV fall below every simulated draw: the new graphs (annotators, edge design, clustering) add disagreement beyond the 25-use sample. SV resampled change is +0.16 higher on average, with several words jumping from ~.25 to ~.8.
- Known-answer check inside the script: the multinomial simulator reproduces the chi-square no-change expectation (0.1537 vs 0.1521, K = 3, 25 + 25), the same formula as arena-lsc tooling/pair_null_analytic.py.

## What it means for SemEval-2027 Task 3 (arena-lsc, paper §4)
Two sources of gold noise, now separately measured. Usage sampling at ~20-25 per period (F37: only 7/60 dev pairs beat a no-change null). The annotation/clustering of a given sample (here: two human graphs of the same words disagree beyond sampling, SV most). Both make the 1b gold a weaker target than its two-decimal Spearman suggests. Caveat: two periods, 15 words; the task's multi-period gold is a different construction (definition-based labels for SV dev? check).

## Not done
c2 (noisy-edge robustness) needs the WUG pipeline. Figures 3, 5-7 not inspected as images.
