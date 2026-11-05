# maglio2014-spatial-orientation-psychological-distance — reading notes

Author: maria. Read 2026-11-05 (item 6/8 of mark's blinded known-answer control; blocked 10-25 until Leonardo saved the PDF).

## What the paper says
Six field studies (Toronto, Vancouver), n = 45-202, one item each. Moving toward a place makes it feel closer in
space (S1, S2), time (S3a, S3b), probability (S4) and social similarity (S5) -- the four construal-level dimensions.
Sample rule: "a minimum sample size per cell ... collected data until that number was achieved" (20/cell; 50 in 3a).

## What the deposit says (r01_reproduce.py)
Everything reproduces -- this is a clean deposit. Small slips: S3b "no effect of target, F < 1" is F = 1.73-1.77
(every SS type); S4 p for the familiarity r is .0148, printed .02; S3a mean 7.67 vs printed 7.65 (one minute in one
of 52 rows -- the deposit is not exactly the analysed file, or a typo). The S1 simple-effect eta_p^2 are per-station
one-way ANOVAs, not the pooled-error contrasts.

Robustness, one test each: S1 toward-vs-away p = 2e-7 (rank). S2 rank p = .043. S3a rank .0075. **S3b rank p = .11**
(the 120-minute answer carries the parametric F; log1p p = .03). S4 rank .016. **S5 rank p = .068**, 26/45 answers at
the floor -- and the General Discussion counts it as support.

## The set (r02_excess_significance.py)
The five cross-dimension tests have p = .032, .012, .011, .017, .051: z = 2.15, 2.52, 2.56, 2.38, 1.95, var(z) = .067.
Independent studies give var(z) >= 1 in expectation.

**Calibrate first.** Same ns, pooled d = .56:
| world | TIVA flag rate (p < .05) | median var(z) |
|---|---|---|
| no selection | .043 | .91 |
| d = 0, file drawer (publish if p < .06) | .783 | .084 |
| d = .2, file drawer | .627 | .131 |
| d = pooled, file drawer | .202 | .369 |
| d = .8, file drawer | .067 | .686 |

The observed .067 sits below the median of the NULL-file-drawer world. MC p under no selection .0064; P(all five in
(.01,.06)) = .00095; joint power .086. Including S1 (z ~ 5) -> var 1.44, nothing flags. I chose the set after
reading (the five tests that carry the cross-dimension claim). That is a judgement, and it is written down as one.

What it does and does not say: the five reported tests are very likely a selected subset of what was run (studies,
stopping, or analyses). It says nothing about S1, which is strong on its own, and nothing about which mechanism.

## Call for mark (before unblinding)
Checked-type defects: **minor** (F < 1 false; p rounding; S3b rank-fragile). Unchecked-type: **strong** (excess
significance, calibrated detector). Prediction: S1-type spatial effect replicates; the cross-dimension claims (S3-S5)
are the fragile part.

## Connections
- Same TIVA logic is the per-paper version of what pawel2020 does per literature: is the evidence in the originals
  enough to predict the replications? There it is not (see that record's p04).
- experimental-social-and-cognitive-psychology area: second paper of the 8 whose deposit reproduces but whose
  inference does not (cf. faivre2014 #c3, mcnulty2014 null-model share).
