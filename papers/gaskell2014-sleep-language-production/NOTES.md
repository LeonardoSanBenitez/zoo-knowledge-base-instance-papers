# Gaskell et al. (2014), *Sleep Underpins the Plasticity of Language Production* — notes

Author: maria, 2026-10-25. Read in full: the **accepted manuscript with its supplement** (White Rose
eprint 79436). The typeset PDF is behind SAGE's bot wall. Data and the authors' lme4 scripts come from OSF
"Phonotactic Nap" (zqg9y), whose files sit in components fcgd6, c28d9, 7qn52, b7arh and 4gq6x. The parent
node holds none. The scripts were run in R 4.4.1 with lme4 1.1-35.5. They need one shim: R ≥ 4.0 no longer
reads strings as factors, so `contr.sum(levels(...))` fails. I wrapped `read.csv(..., stringsAsFactors=TRUE)`
and left the analysis code untouched.

## Why this paper

Item 4 of 8 in mark's blinded known-answer control. No prior knowledge and no search for third-party checks.

## What the paper claims

38 adults read second-order phonotactic sequences (/f/ and /s/ position depends on the vowel). After 48
sequences, 19 napped 90 min with polysomnography and 19 stayed awake. Then 96 more sequences, and 2AFC
recognition and generalisation tests.

1. Only the nap group's speech errors came to respect the new constraints. Three-way interaction
   β = 1.97, z = 3.31, p < .001.
2. Only the nap group generalised to new syllables: 69% vs 56%, p = .038.
3. The speech-error shift correlates with slow-wave sleep: β = .06, z = 3.10, p = .002; r = .47.

## What survived

- **The data reproduce the paper's point estimates exactly.**
  - Every fixed effect in the speech-error and generalisation models: 1.960 vs 1.97; matched subset 1.348 vs 1.35.
  - Every sleep-stage β in Table 3.
  - The participant-level r (SWS .466, REM −.494, N1 −.21, N2 −.06, period −.22).
  - Recognition (88% vs 87%), Table 2's means, and Table 1's means (pooled over errors).
- **The sleep effect on speech errors survives the test I expected to break it, but much weaker.** At
  training the wake group already showed the effect (+8.8 points; the paper calls it a Type I error) and
  the sleep group showed −2.0. That is a chance imbalance (p = .08), which by itself produces a crossover
  through regression to the mean. The training score barely predicts the test score (slope .05), so
  change scores mostly carry baseline noise. With an ANCOVA (test ~ group + training score), sleep still
  beats wake by **9.2 points, p = .039**. The change-score test the paper's interaction mirrors gives
  p = .009 (permutation .008), and the paper reports p < .001.
- **Generalisation, as an estimate.** The "both unfamiliar" items are above chance for sleep (z = 2.56, p = .011)
  and not for wake (p = .54), reproduced.

## What did not, or not as written

1. **The SWS result is an artefact of treating errors as participants.** The script fits
   `glm(SyllPos ~ Session:Restriction:N3Mins)`: 2,401 speech errors from 19 people, no participant term,
   and no lower-order terms. This reproduces the published z = 3.10 exactly. Adding the lower-order terms
   and clustering by participant gives **z = 1.90, p = .057**. At the participant level, r = .466 (p = .044, n = 19).
   - REM shows r = −.494 (p = .032), equally strong in the opposite direction.
   - Six sleep measures were tested without correction.
   - Delta power, offered as converging evidence (z = 2.64), is **r = .40, p = .09** at the participant level.
   The paper's caveat ("correlatory") is honest. Its p-values are not.
2. **Table 1's SD column is rotated.** In all eight columns, the SD printed for training belongs to test
   block 1, the one for test 1 belongs to test 2, and the one for test 2 belongs to training. Example:
   sleep / restricted error counts. Printed: 9.5 (4.7), 4.9 (3.8), 6.0 (5.4). True: 9.5 (5.4), 4.9 (4.7),
   6.0 (3.8). The means are right. They are pooled over errors, while the SDs are across participants,
   which the caption does not say.
3. **Table 2's "(SD)" are standard errors.** Recomputed SEs are 4.0 / 3.7 / 1.3 / 3.7 / 7.1 / 6.2, matching the
   print. The true SDs are 16–31%. With 3–4 items per participant, an SD of 7% is impossible, which is
   what made me check.
4. **The 69% vs 56% is an unweighted mean of three item-type means.** Raw accuracy is 64.8% vs 54.3%. The
   near-ceiling "target familiar" items (3–4 of ~19 trials) get a third of the weight. Defensible under
   effect coding, but unstated.
5. **Inference depends on software version.** Point estimates reproduce exactly, but standard errors from
   the maximal glmer models differ in current lme4. Several models fail to converge.
   - The published "Session" effect, p = .03, is now p = .08.
   - The post-hoc matched-subset follow-ups go from **p = .021 to .085** (sleep Session × Restriction) and
     from **.017 to .105** (sleep at test).
   - The sleep / test-block-1 effect prints β = 1.40, SE = .40, z = 2.48, which is internally inconsistent
     (1.40/.40 = 3.5). Now it is SE 1.16, p = .23.
   The headline three-way interaction survives (z = 3.27).
6. **The "matched subset" is a post-hoc selection on the variable in question.** 28 of 38 participants
   were chosen by "progressively excluding outliers ... based on their pre-interval phonotactic learning
   score". The ANCOVA above is the principled version of what it attempts, and it gives p = .039.
7. **"Sleep but not wake" contrasts are partly differences in significance.** For generalisation the Group
   effect is tested (p = .038; p = .020 in current lme4). The "only the sleep group" comparisons against chance
   are not a test of group difference. Sleepiness differed (Session × Group F = 15.3), and that is handled by
   correlations that read non-significance as absence, which the supplement admits.

## For the known-answer control (my prediction, written before unblinding)

Checked-type:
- Point estimates all reproduce.
- **Reported tables contain clear errors**: Table 1's SDs rotated, Table 2's SEs labelled SD, and one
  internally inconsistent z.
- Several reported p-values do not reproduce in current software (the matched-subset tests become
  non-significant). The code also needs a one-line shim to run at all.

Unchecked-type:
- The SWS p-value comes from pseudoreplication.
- Change scores overstate the sleep effect (p < .001 vs ANCOVA .039).

My call: **main sleep effect real but weaker than claimed; SWS claim not supported at the participant level;
reporting errors in two tables.** Strength of checked-type defects: moderate. This is the first of the four
where I would expect a reproduction audit to flag more than typos.
