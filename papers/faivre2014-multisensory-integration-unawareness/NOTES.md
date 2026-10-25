# Faivre, Mudrik, Schwartz & Koch (2014), *Multisensory Integration in Complete Unawareness* — notes

Author: maria, 2026-10-25. Read in full: the published OnlineFirst PDF (EPFL Infoscience, also on OSF). The
supplement is on OSF and was not read in full. Data: OSF usfa5 `files.zip` holds one `.dat` file per
participant for 8 experiments, plus the stimuli. No analysis code is deposited, so I rebuilt everything
in Python.

## Why this paper

Item 7 of 8 in mark's blinded known-answer control. No prior knowledge and no search for third-party checks.

## What the paper claims

Masked audiovisual digit primes, then audiovisual letter targets; the task is to judge identical vs
different. Unconscious congruency priming appears when only the visual prime is masked (Exp 1), only the
auditory prime (Exp 2), and **both** (Exp 3). It disappears without prior conscious training (Exp 4).
The claim: "the first demonstration of multisensory integration in complete unawareness."

## What survived

- **Participant counts, target accuracies and the semantic-relation effects** reproduce for Exps 1, 3 and 4
  (89 / 95 / 79 ms vs 88.8 / 91.7 / 78.6 per participant).
- **The prime-awareness numbers reproduce on all unconscious trials**: 53.3% (t = 2.05) vs the published
  53.3% (t(16) = 2.06); 47.4% vs 47.2%; 50.3% vs 50.0%.
- **The Exp 1 and Exp 3 interactions are robust across my multiverse.** The target × congruency
  interaction reaches p < .05 in 69% (Exp 1) and 100% (Exp 3) of 48 specifications.

## What did not

1. **"Complete unawareness" is contradicted by the deposited data.** Participants partly copy their target
   answer into the prime question: prime answer = target answer on 58–60% of trials in Exps 1 and 3. So raw
   prime accuracy mixes sensitivity with carryover. In Exp 3, prime "accuracy" is 56.7% on congruent and
   37.6% on incongruent trials. Measured within each target-response level:
   - **Exp 1: sensitivity .075, p = .024.** Above chance, even after the 9 most aware participants were
     removed.
   - **Exp 3: −.041, p = .032.** Significantly *reversed*. The paper reads its below-chance 47.2% as
     "evidence for an absence of awareness". Systematic below-chance performance means the prime
     information is available and mapped the wrong way. It is not absence.
2. **Unawareness partly by exclusion, and the excluded are not deposited.** 9 of 26 (Exp 1) and 6 of 28
   (Exp 2) participants were removed for prime accuracy above 65%. The cutoff was set "based on ...
   Experiments 1 and 2". Selecting on a noisy awareness measure leaves a sample that looks unaware partly by
   regression to the mean. The deposit has only the 17 and 22 retained participants, so the selection
   cannot be checked.
3. **Table 4 does not reproduce.** I tried 12 aggregation variants: per-participant vs group exp of mean log
   RT, dropping the first 5 trials of the experiment / of each block / none, and the RT window. None
   reproduces Exp 3 (best attempt: identical 51 vs published 59) or Exp 4. **Exp 4's identical-target
   priming is negative under every variant (−9 to −27 ms) against +25 published.** Exp 2's published
   different-target priming (37 ms, p = .035) and interaction (p = .02) reach p < .05 in **0 of 48**
   specifications; under the paper's stated pipeline the interaction is p = .17 and the semantic effect
   61 → 50 ms (p = .003 → .06).
4. **The priming evidence is fragile even where it reproduces.** No main effect of congruency in any
   experiment. The cell carrying each claim sits at p = .035–.04 in print and p = .05–.11 in my
   reproduction. Its direction flips: identical targets in Exps 1 and 3, different targets in Exp 2.
   Under a within-participant permutation null, the paper's criterion (interaction or any cell p < .05) fires
   10–14% of the time per experiment.
5. **Sample sizes were reduced after looking**: "After analyzing the results of these experiments, we
   estimated the effect sizes and accordingly redefined the sample sizes for Experiments 3 and 4 to include
   20 to 25."
6. **The deposit's readme mislabels its own key column.** Column 5 ('rel'/'unrel') is described as prime-
   target congruency. In the data it marks identical targets, on every row. A reuser following the readme
   would code congruency wrongly; I did at first.

## For the known-answer control (my prediction, written before unblinding)

Checked-type, the strongest of the set:
- Table 4's priming values do not reproduce from the deposit (Exp 4 with the opposite sign).
- Exp 2's significant priming appears in no reasonable specification.
- The readme mislabels a key variable.
- Excluded participants are not deposited.
Unchecked-type:
- The central "complete unawareness" claim is contradicted by the authors' own trial data once response
  copying is controlled.
- The below-chance result is misread.
My call: **not reproducible as reported; central claim not supported.** Strength of checked-type
defects: **strong**.
