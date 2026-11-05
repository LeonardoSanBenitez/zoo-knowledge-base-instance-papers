<!--kb
id: area:replicability-and-selective-reporting
labels: kind:paper-notes, area:replicability-and-selective-reporting
triggers: will this finding replicate; forecast replication outcome from the original; excess significance in a multi-study paper; too many significant results for the power; does a larger replication succeed more often; selection on significance publication bias detector; TIVA z-curve p-curve calibrated by simulation; replication database original replication pairs
verified: 2026-11-05
-->

# Replicability and selective reporting (detectors, forecasts, and the data to test them)

Author: maria. Started 2026-11-05. The question that organises this area: **when a detector or a forecaster says
something about a literature, has it first been shown to say the right thing on a world where the answer is known?**

Records:
- `pawel2020-probabilistic-forecasting-replication` — replication forecasts (N/S/H/SH) on 4 projects; reproduced
  exactly; tested out of sample on FReD.
- `roseler2024-replication-database` — FReD; 2023 counts reproduced; used (blinded) as the out-of-sample test bed.
- `maglio2014-spatial-orientation-psychological-distance` (area: experimental-social-and-cognitive-psychology) —
  per-paper excess significance, TIVA calibrated before use.

## Measured so far (numbers with their records)

| question | answer | where |
|---|---|---|
| Do the best statistical replication forecasts generalise? | No. SH: 638.5 expected vs 388 observed on 1,082 FReD pairs; AUC .579 vs .84 if the model were true | pawel2020 #c7 |
| Does a bigger replication succeed more often? | Not in FReD: AUC .47, logit coef -0.05 (SE .075). The standard model says it should (AUC .66) | roseler2024 #c3 |
| Does the original's evidence predict success? | Weakly: AUC .625; 27% -> 51% success from bottom to top |t_o| quintile | roseler2024 #c3 |
| Is SH's miscalibration in RPP caused by ignoring selection? | No (my hypothesis, refuted): under honest selection SH is ~calibrated at RPP's design | pawel2020 #c4 |
| What reproduces RPP's gap? | Attenuation at replication fits with RPP's moderate bunching; p-hacking worlds over-bunch (55% vs 34% of |t_o| in 1.96-2.5) | pawel2020 #c6 |
| TIVA operating characteristics at small n (5 studies, n 45-100) | flags 4.3% honest sets, 78% null file-drawer, 20% file-drawer at d = .56 | maglio2014 #c7 |

## Lessons that generalise (read before building the next detector)

1. **Calibrate the detector in known worlds before believing it — and expect it to refute you.** In this area the
   first two known-answer runs refuted my prior (selection-blindness) and found two bugs of mine (S-method ordering,
   double selection). Same as kim2025 in the monoculture area.
2. **A forecast can be calibrated in the large and useless in discrimination.** tau can be tuned until expected =
   observed; that does not give the inputs information they do not have. Report AUC against a simulated ceiling.
3. **"Calibrated in two of four projects" was the two smallest projects.** Check the power of the calibration test
   before reading its silence as calibration (Spiegelhalter at n = 18 cannot see much).
4. **Replication databases are not independent samples.** Many Labs per-lab rows: 72.8% of usable FReD pairs share
   an original (max 35). Cluster or weight 1/k.
5. **The outcome variable is a choice.** FReD's own verdict and "p <= .05, not coded failed" disagree on 16% of pairs,
   and the forecast's AUC flips from .58 to .48 between them.

## Open
- FReD closeness_* codings vs success (the direct test of the heterogeneity explanation).
- z-curve ERR/EDR vs FReD success (Roeseler 2023 preprint, osf.io/ewb2t) on the same blinded copy.
- Coronado-Montoya et al. 2016 (mindfulness RCTs: observed vs expected positive trials) — the clinical face of
  excess significance; candidate for a contemplative-neuroscience bridge.
