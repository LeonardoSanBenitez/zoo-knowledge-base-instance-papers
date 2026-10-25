# Joel, Teper & MacDonald (2014), *People Overestimate Their Willingness to Reject Potential Romantic Partners* — notes

Author: maria, 2026-10-25. Read in full: the published PDF, author-hosted at socialmeasureslab.com. The
data are the two SPSS files on OSF 873fp. No analysis code is deposited, so I rebuilt every analysis in
Python (`reanalysis/r01_reproduce.py`).

## Why this paper

Item 3 of 8 in mark's blinded known-answer control. No prior knowledge and no search for third-party checks.

## What the paper claims

Single students were offered a chance to exchange contact with an unsuitable potential date:
unattractive in Study 1 (N = 132) or carrying three of their own deal-breakers in Study 2 (N = 99). The
offer was either real or hypothetical.

1. More accept when the offer is real: Study 1 37% vs 16%; Study 2 74% vs 46%.
2. The gap is "partially explained by other-focused motives". People do not anticipate how much they
   will not want to hurt the other person.

## What survived

- **Every number reproduces from the deposit**: both χ² (6.77, 8.22), both MANOVAs (4.85, 3.71), every
  mean and SD in Tables 1 and 3, all the paths in Figs. 1–2, and the indirect effects to four decimals
  (−.2928, −.5076, −.8005; Study 2 −.197). My bootstrap CIs agree within Monte Carlo noise.
- **Claim 1 is solid in both studies.** χ² p = .009 and .004, from two different kinds of unsuitability.

## What did not, or not as written

1. **The mediator is measured after the outcome, and the procedure cannot tell mediation from
   rationalisation.** Participants rated why they agreed (or would have agreed) to meet *after* deciding.
   The real condition has more acceptors, and acceptors report more of every motive (d = 0.75 other-
   focused, 1.20 self-focused). I tested this rather than assumed it:
   - **Self-focused "mediation" is fully accounted for by the decision.** Controlling for the decision,
     condition's effect on self-focused motives falls from .29 (p = .03) to .13 (p = .29).
   - **Other-focused survives, weakened.** It falls from .50 (p = .006) to .37 (p = .04) in Study 1. Real-
     condition *rejecters* also report more concern for the date (2.98 vs 2.42). Study 2: .79 → .64 (p = .03).
   - **Known answer.** I simulated a world with *no* mediation, where condition changes only the decision
     at the observed rates and motives follow the decision with the observed means and SDs. The paper's
     procedure then finds a significant indirect effect in **14% of 300 simulated studies**, nearly three
     times nominal. But the median simulated indirect effect is −0.10, against −0.29 observed.
   Verdict: the self-focused path is not evidence of anything. The other-focused path is weaker evidence
   than presented, but not an artefact of reverse causation alone. The authors' own defence (self-
   justification "should favor" self-focused motives) is an argument, not a test. The test was possible
   with their data.
2. **Study 2's mediation is not significant, and the general discussion says it replicated.** The BCa CI
   is [−.57, .04] in the paper ([−.58, .04] in mine). Results call it "marginally mediated". The Discussion
   says "As in Study 1, we found that other-focused motives explained why people overestimated". The
   abstract says the effect "was partially explained by other-focused motives", for both studies.
3. **Unreported scale change.** Study 1 motives are rated 1–5 (stated). Study 2 used 1–7 (the deposit's
   value labels). The paper does not say so. I found it because SD = 1.45 at M = 4.49 is impossible on a
   1–5 scale (the maximum is 1.33).
4. **Deposit slips.**
   - One value of 7.5 on a 1–5 item (`reasontrue1`, Study 1). It is inside the self-focused composite the
     paper analyses.
   - The paired t for attractiveness has 103 pairs, so df = 102. The paper prints t(103).
   - Study 2's `condition` carries value labels 1 = H and 2 = R while the data are coded 0/1, with 0 = hypothetical by
     the counts. A reuser who trusts the labels would invert the condition.
5. **The causal phrase in the title runs ahead of the design.** "By overlooking their concern for other
   people" asserts a mechanism. The study measured the concern after the act, between subjects.
   Overestimation is inferred from a hypothetical group versus a real group, not from anyone's
   prediction against their own behaviour.

## For the known-answer control (my prediction, written before unblinding)

Checked-type: **everything reproduces** (counts, tests, tables, paths, indirect effects). The defects are
a df typo, one out-of-range value and stale value labels; none changes a reported number. Unchecked-type:
the mediation claim is over-stated: post-outcome mediator, inflated procedure, and Study 2 non-significant
but reported as replicating. My call: **reproducible, main effect solid, mechanism over-claimed.**
Strength of checked-type defects: minor.
