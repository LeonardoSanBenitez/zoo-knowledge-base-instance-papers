# pawel2020-probabilistic-forecasting-replication — reading notes

Author: maria, 2026-11-05. Chosen to test a hypothesis of mine; the hypothesis died, and that is the most useful
line in this file.

## The paper in one paragraph
Four one-to-one replication projects (econ 18, x-phil 31, RPP 73, SSRP 21). Hierarchical normal model on Fisher z:
theta_o, theta_r ~ N(theta, tau^2). Four forecasters: N (face value), S (empirical-Bayes shrinkage
s = max(1 - 1/t_o^2, 0)), H (tau = .08), SH (both). Evaluated with proper scores, PIT, Spiegelhalter z,
calibration slope, AUC. SH best everywhere, calibrated in econ and x-phil, not in RPP and SSRP. Markets beat all
statistical forecasts in SSRP. Recommendation: stop judging replications by significance alone.

## Reproduction (p01)
All of Tables 2-3 and Fig 7 reproduce to the printed digit in a Python re-implementation of eqs 3-6. One mismatch
in the S column was MY bug (tau set to zero after, not before, computing s). The package's `powerSignificance`
with designPrior = "EB" is exactly SH.

## My hypothesis and how it died (p02)
I expected SH to be miscalibrated because shrinking each study by its own t_o cannot see that the originals were
selected on |t_o| > 1.96. Known-answer worlds at RPP's own (n_o, n_r), honest selection, no heterogeneity:

| world | observed / 73 | N | SH | SA08 (mine) |
|---|---|---|---|---|
| half null, half r = .3, selected | 50.6 | 58.1 | 49.9 | 48.9 |
| all r = .3, selected | 54.6 | 58.7 | 50.8 | 50.7 |
| half null + tau .08 | 45.7 | 57.8 | 49.5 | 47.0 |
| no selection, r ~ N(.2, .15) | 29.8 | 35.4 | 23.5 | 33.2 |
| 80% null, selected | 41.4 | 55.9 | 46.9 | 42.7 |

SH is close to calibrated under selection. The per-study shrinkage factor is a decent proxy for what selection
does at these n. (It is miscalibrated in the opposite direction when there is NO selection: it over-shrinks.)
So selection cannot be the reason for RPP's 45.9 vs 24. First version of p02 had a double-selection bug
(each original had to pass twice), which made nulls vanish and every world look alike; caught because the 80%-null
world replicated as often as the 50% one.

## What does produce RPP's gap (p04)
p-hacking + 80% null, or all-tiny effects, reproduce the count -- but bunch 54-56% of |t_o| in (1.96, 2.5),
against RPP's 34%. Attenuation at replication (replication effect = half the original's) reproduces most of the
gap with little bunching. Reading: the information about RPP's failures is not in the originals' z-distribution.
This is coarse (seven worlds), and it cannot tell "true decline" from "the replication tested something different".

## My forecaster (p03, selection_forecast.py) -- a failed method, kept
NPMLE of g(theta) per project with truncated likelihood. Lowers the overprediction somewhat in RPP (40.1) but
kills discrimination (AUC .61 vs .70; x-phil BS .233 vs .148). Pooled priors from a few dozen originals turn the
forecast into a function of n_r; the per-study rule keeps the ordering. Do not re-propose without a smoother prior
(e.g. a two-component parametric g) and a held-out test.

## Out of sample (FReD, in roseler2024 record)
1,082 pairs: SH expects 638.5 vs 388; AUC .579 vs a .84 ceiling if SH were true; replication n has no signal at all
(AUC .47). The "two of four projects" success does not generalise. With hindsight the paper's own data warned of this:
the calibrated projects are the two smallest.

## Connections
- maglio2014 (same session): within one paper, the five reported tests are too homogeneous -- the per-paper face of the
  same selection. Both records follow the same rule: calibrate the detector in known worlds first.
- kim2025-correlated-errors: same shape of error I made there -- reading an observed-vs-model gap as a fact about the
  world before checking the model family. Here I checked first, and the check refuted me.
- Protzko et al. data ships in the same package; that paper (NHB 2023) was retracted in 2024. Noted in a2's datasheet.
