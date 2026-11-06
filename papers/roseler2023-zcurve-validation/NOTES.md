# roseler2023-zcurve-validation — reading notes

Author: maria, 2026-11-05. Preprint (Meta-Psychology submission, OSF k4d6w, version 231024). Code + data deposited.

## The paper
1,072 FReD entries (223 originals; my count from the deposit: 1,004 with a computable z, 202 unique refs). For
10,000 draws: pick a target replication rate P ~ U(0,1); draw 30%·P of the successes and 30%·(1-P) of the failures;
fit z-curve (EM) to the originals' z; record ERR, EDR and the realised RR. Result: r(ERR, RR) = .945 (abstract: .933),
ERR "tends to the mean"; a linear recalibration RR = 1.85 ERR - .573 "deviates by < +-16%"; CI coverage 44.9%.
Conclusion: z-curve is "a valid and economic method to compare replicability estimates for large sets of studies".
The author is careful in the discussion (exploratory, multilevel structure ignored, linear model not validated).

## Reproduced (z01, Docker zoo-r-zcurve:4.4.1 = zoo-r-psych + CRAN zcurve)
r .942 (paper .945), slope 1.79 (1.85), intercept -.547 (-.573), M RR .431 (.43), M ERR .546 (.54). Two text slips:
abstract r .933 vs results .945; "samples from 322 studies" -- the code draws 30%·P of one pool plus 30%·(1-P) of the
other, i.e. 127-195 rows (median 150), not 322.

## Known-answer controls -- what r measures in this design
| control | r(ERR, RR) | reads as |
|---|---|---|
| A paper design, real z | .942 | -- |
| K1 same design, z permuted ONCE (no z-outcome link) | **.645** | one draw: see z03 (corrected 2026-11-06) |
| K2 same design, trivial statistic share(z > 2.8) instead of z-curve | **.945** | r is not specific to z-curve |
| K3 natural random 30% subsamples | .369 (SD RR .025) | real-world variation is tiny; ERR overestimates RR by .13 |
| F1 fixed n = 150, real z | .942 | fixing n changes nothing for the real r |
| F3 permuted z, natural mix, n 100-220 | r(n, ERR) = -.063 | ERR barely depends on n: K1's .645 is NOT an n-confound |
| F2 fixed n = 150, z permuted ONCE | **-.296** | one random split of z between the two pools already gives |r| ~ .3 |
| F4 one row per original, fixed n = 60 | .684 | the multilevel structure is not what makes r high |
| K4 six source projects (natural literatures) | Pearson .58, Spearman .60, mean abs(ERR - RR) .27, signed +.24 | ranks roughly, overestimates by a quarter |

K1 (.645) and F2 (-.296) are single draws from the permutation null of this design: one random split of the z values
between the two pools already differs enough to be amplified into |r| of .3-.6 (z03 measures the spread).

**z03 (2026-11-06), the measured spread.** 30 permutations x 120 samples at n = 150: r(ERR, RR) mean -.002, SD .283,
range -.573..+.524, |r| > .5 in 10%; share(z > 2.8) mean .034, SD .273. Real data: .943 / .944, above every permuted
draw. **Correction to my 11-05 reading:** K1 (.645) was a 2.3-SD draw, not what the design typically gives with no
information. What stands: the design makes |r| of .3-.5 common from nothing (an iid null at 120 samples would have
SD ~.09); a trivial statistic matches z-curve exactly; and the real r measures row-level discrimination (pools differ on
z), not literature-level calibration (K3, K4).

The mechanism: samples are mixtures of two FIXED pools (successful and failed replications) in proportion P. Any
statistic f whose mean differs between the pools tracks P linearly, and with 150 rows per sample its noise is small,
so r -> 1 whatever f is and however small the pool difference, as long as it is not zero. The design measures
"do the two pools differ on f", amplified into a correlation. That is a test of discrimination at the row level
(AUC of z for the outcome here: .737), dressed as a test of calibration at the literature level. It cannot validate
the use the conclusion proposes (comparing real literatures), where RR varies for other reasons and ERR is off by .27.

## What survives
- z in this deposit discriminates replicated from failed findings at the row level (AUC .737; FReD 2026 with p-based z:
  .625 -- the gap is partly that z = r/se here contains n).
- ERR overestimates RR: by .12 in the paper's own means, .13 in natural subsamples, .27 on average across projects (signed +.24).
- The linear recalibration is fitted to an artificial mixture design; its slope is a property of the pools, not of
  z-curve, and should not be applied to a real literature.

## Connections
pawel2020 #c7 (forecasts on FReD: AUC .58 vs .84 ceiling) is the same fact from the forecasting side.
The design artifact belongs in instance-general statistics with the other "detector finds signal in a null world"
cases (kb.py instruments --verdict artifact).
