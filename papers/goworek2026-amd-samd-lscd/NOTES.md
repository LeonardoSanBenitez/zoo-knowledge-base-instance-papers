# goworek2026-amd-samd-lscd — notes (maria, 2026-11-26)

Author: maria

## What the paper does
Two new graded-change metrics over usage embeddings of two periods: AMD (mean nearest-neighbour cosine distance, both directions) and SAMD (greedy one-to-one matching on an equal-size subsample). Compared with APD and PRT across eight datasets, many encoders, and four spaces (full, LLM-definition space from Gemini 2.5 Pro definitions, per-word PCA with K = #definitions, K random dimensions). Headline: correspondence metrics are better and more stable on average, best with PCA.

## Breaking it (what I ran)
- `reanalysis/amd_check.py`: the four metrics on XL-LEXEME vectors of DWUG EN/DE/SV (arena-lsc conversions, cluster-JSD gold), FULL and PCA-4, with a within-word period shuffle as the known-answer control.
  - FULL: APD .79/.83/.87, AMD .74/.85/.87, SAMD .77/.85/.86; all CIs vs APD span 0.
  - PCA4: AMD .16/.33/.11 (collapses), SAMD .44/.63/.32, APD .41/.58/.26.
  - Control: period-shuffled APD stays at .74/.80/.87. The control did not come out near 0, and that is the finding.
- `reanalysis/period_blind.py`: dispersion (all-pairs distance, periods ignored) .74/.80/.87; gold K alone .77/.42/.91; APD - dispersion .59/.75/.57; APD beats dispersion only on EN.

## Why it matters beyond this paper
Two-period graded benchmarks built from sense clusterings have gold JSD that grows with the number of senses, so any dispersion-like score correlates well with "change" without looking at time. It is the graded analogue of arena-lsc F1 (random labels within the gold k score high on 1b). Proposed rule for the LSC area: report every graded-change metric beside its period-shuffled copy.

## Not done
Authors' code and definitions not cloned; the per-word K and the official SemEval-2020 graded scores not used (both scope differences, which is why c1/c2 are 'disputed' and not 'refuted').
