# DeSteno, Li, Dickens & Lerner (2014), *Gratitude: A Tool for Reducing Economic Impatience* — notes

Author: maria, 2026-10-25. Read in full: the **in-press manuscript dated 2014-03-05** (Harvard Kennedy
School copy). The published PDF is behind SAGE's bot wall, so wording may differ slightly from print.
Data and code come from Harvard Dataverse doi:10.7910/DVN/24885, v1.0, released 2014-03-10. The published
article's open-data link was not visible to me. I found the deposit by searching Dataverse for the
authors, and its date and title match the paper.

## Why this paper

Item 2 of 8 in mark's blinded known-answer control (identifiers only). No prior knowledge and no
search for third-party checks.

## What the paper claims

N = 75 undergraduates, 25 per condition: gratitude, happiness or neutral recall. They then made 27 Kirby
intertemporal choices with real incentives, one paid per session. An exponential discount factor was fitted
by maximum likelihood to each participant.

1. Gratitude increases patience. Planned contrast (2, −1, −1): t(72) = 2.18, p = .03, d = 0.62.
2. Gratitude's effect is "differentiable from those of happiness".

## What survived

- **Everything reproduces from the deposit**: N per cell, gender (32/43), age, both alphas (.92, .74),
  r = .57, the manipulation-check interaction F(2,72) = 22.48, both focused ANCOVAs (34.08, 10.81), the cell
  means (.166 / .296 / .177), the contrast t(72) = 2.18 (p = .033), the pairwise p-values (.052 and .077,
  which are LSD tests with pooled MSE), the rank contrast t = 1.93, the regression (β = .316, t = 2.29,
  R² = .068) and the dollar translation ($63 vs $55). The SPSS file (served as `.tab`) and the xlsx agree
  cell for cell.
- **The discount factors re-derive from raw choices.** The 2,025 choices are embedded in `fitIT_Gratitude.m`
  and also stored as item columns. My port of `expdiscountMLE.m`, fitted to the item columns, correlates
  r = .986 with the deposited factors (3 of 75 differ by more than .05).
- **The effect is not an artefact of the outcome model.** It is *stronger* model-free: the proportion of
  later-larger choices gives contrast t = 2.60, p = .011, and the permutation p is .011. The parametric
  contrast is calibrated on this skewed, bounded outcome: under a resampled null it rejects 4.9% of the
  time. Its permutation p (.0315) matches the parametric one (.033).

## What did not, or not as written

1. **d = 0.62 does not reproduce.** No standard standardiser gives it. Gratitude vs the other two pooled
   gives 0.54, 2t/√df gives 0.51, and vs neutral alone gives 0.52. The nearest values are Glass-type
   (0.65 using the others' SD, 0.67 using neutral's SD). The honest effect is d ≈ 0.5.
2. **The manipulation-check means are labelled ambiguously.** "M_grateful = 4.47" is the mean of *both*
   positive indices in the gratitude condition, not the gratitude index (which is 4.80). Same for happy
   (4.11) and neutral (3.17). Recomputed exactly; a labelling issue only.
3. **"Differentiable from happiness" is not established by a direct test.** Gratitude vs happiness is
   p = .077 (LSD) or .10 (t-test) on the discount factor, and p = .048 on the model-free measure. The
   regression offered as support ("only gratitude emerged as a reliable predictor") compares a significant
   coefficient with a non-significant one. The test of β_grat = β_hap is t = 1.81, p = .075.
4. **The regression is not further evidence; it restates the condition effect.** Within conditions,
   gratitude intensity does not predict the discount factor (r = .06 in the gratitude cell, −.03 in
   neutral). Adding condition dummies takes the gratitude coefficient to t = 1.12, p = .27. "Increasing
   intensities of gratitude corresponded to increasing annual discount factors" reads like a dose-response
   finding, but it is the between-cell difference read a second time.
5. **One study, n = 25 per cell, p = .03.** Fine for a 2014 short report. It is not the "potentially
   profound consequences" the discussion claims.

## For the known-answer control (my prediction, written before unblinding)

Checked-type: **everything reproduces**, except d (0.62 printed vs ≈0.53 computed) and an ambiguous label
on the manipulation means. Unchecked-type: claim 2 over-stated (a difference in significance, not a tested
difference), and the regression double-counts the main effect. My call: **reproducible, main effect robust
to outcome and test choice, secondary claim over-stated.** Strength of checked-type defects: minor.
