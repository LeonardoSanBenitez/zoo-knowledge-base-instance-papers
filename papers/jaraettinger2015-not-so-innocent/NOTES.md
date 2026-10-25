# Jara-Ettinger, Tenenbaum & Schulz (2015), *Not So Innocent* — notes

Author: maria, 2026-10-25. Read in full: the published PDF, the author copy from the Yale lab page. Data
and the authors' R script are from OSF z9ikh, and the materials (scripts, puppet videos) from frwun and
4qfvj. Every count and statistic in Methods/Results was recounted from the deposited CSV, and the
authors' `AnalyzeData.R` was run unmodified in R 4.4.1 (`reanalysis/out/authors_AnalyzeData_R_run.txt`).

## Why this paper

Item 1 of 8 in mark's **blinded known-answer control of my reading protocol** (2026-10-23). I received
identifiers only. Some of the eight have been independently established as sound and some not, and I do
not know which. I agreed not to search for third-party checks of these papers until unblinding. So
everything below comes from the paper, its deposit and my own computation. Prior suspicion: none. I had
never heard of the paper.

## What the paper claims

- Toddlers prefer an agent who achieves a goal at lower cost (Exp 1, 15/16).
- When both agents refuse to help, children still prefer to play with the competent one (Exp 2, 11/16;
  Exp 3 play, 13/16).
- But they judge the incompetent one "nicer" (Exp 3 nicer, 11/16 incompetent), and that judgement
  differs from a baseline with no refusal (5/16 incompetent).
- The abstract's sentence: "children retain a preference for the more competent agent but infer that the
  less competent agent is nicer."

## What survived

- **The deposit is exemplary for 2015.** Every exclusion has its reason, age is given in days, and
  counterbalancing is coded. Every N, exclusion count, mean age, SD and range in the paper recounts
  exactly (`out/r01_out.txt`). The R script reproduces the reported bootstrap intervals.
- **Exp 1 is solid**: 15/16, binomial p = 0.0005.
- **"Retain a preference for the competent agent when both refuse"** holds when the two refusal-plus-play
  cells are pooled: 24/32, p = 0.007. Exp 2 alone is 11/16, p = 0.21, which the paper describes as "a
  bias". It is not distinguishable from chance on its own.

## What did not, or not as written

1. **The decisive test is misreported.** Nicer vs nicer-baseline is the comparison that isolates the
   effect of refusal on the "nicer" judgement, because the question is the same. Fisher's exact test,
   two-sided, on [[5,11],[11,5]] gives **p = 0.0756**. The paper prints "p < .075". The threshold is
   unusual and the inequality is false. The authors' own script runs this exact `fisher.test` and prints the value.
2. **But Fisher is the conservative choice here, and the effect sits on the line.** At n = 16 per group,
   Fisher rejects 1.6–1.8% of the time under a true null (simulation, `r02`). The unconditional exact tests
   give **Boschloo p = 0.0501 and Barnard p = 0.0502**. The authors' non-stratified basic bootstrap CI excludes
   zero ([6.17, 71.03]), and my known-answer simulation shows that tool is only mildly liberal (5.7–6.9%
   under the null). Honest reading: weak evidence, at the threshold under every reasonable test. It is
   neither a finding nor nothing.
3. **The abstract states as a fact a judgement that is not distinguishable from chance.** In the nicer
   condition, 11/16 chose the incompetent agent, p = 0.21 against 0.5. The "nicer" claim rests on
   comparisons. Against play (p = 0.011) it confounds the question asked with the inference drawn: children
   can prefer to play with the competent agent and still split on "nicer". Against baseline the p is 0.05–0.076.
   The Results section words it carefully ("tended to choose"). The abstract does not.
4. **Exp 3's play CI is mistyped**: the text says [68.75%, 100%]. The authors' script comment, their figure
   code and my recomputation all say 62.50%. Exp 1's basic bootstrap upper bound is 106.25% and was printed as
   100%. Truncating a basic interval at the parameter boundary is a sign the interval type is wrong at a
   15/16 proportion. The fix is cosmetic, but the paper does not say it truncated.
5. **Power.** "We predicted strong effect sizes ... and set our sample size at 16." For the effect the study
   reports (11/16 vs 5/16), Fisher's exact power at 16 per group is **0.435** (exact enumeration). A study
   with this design detects its own reported effect less often than a coin flip.
6. **Fragility to non-responders.** Of the children who reached the question, 5/21 in the nicer condition
   made no choice in 30 s, against 2/18 in play and 3/19 in baseline. Assigning the 8 nicer/baseline
   non-responders at the bounds moves the decisive p from 0.004 to 0.545. Non-response is not obviously
   ignorable when the question is "which one is nicer?" of two agents who both just refused to help.
7. **Forking, disclosed.** Exp 2 contradicted the prediction. Exp 3 then changed the procedure: the
   experimenter added "Neither of our friends *wants* to help". The baseline condition came from a reviewer.
   All of this is honest, and all of it means Exp 3 was designed after seeing Exp 2.
8. **One exact duplicate row** in the deposit (Exp 3 control, F, 768 days, Competent, same three
   counterbalancing codes). It could be twins. Removing it leaves the decisive p unchanged (0.0756 either
   way), so it does not matter here. It is still the kind of thing a deposit check should flag.

## What I would tell a reader

The cost-sensitivity premise (Exp 1) is well supported. The moral inference the title and abstract lead
with is the weakest result in the paper: one cell of 16 children, p = 0.05–0.076 against its proper control,
reported with a false inequality. The data are honest and complete enough to let anyone see that, which
is to the authors' credit.

## For the known-answer control (my prediction, written before unblinding)

Checked-type defects: there are **reporting errors** (p < .075 false, a CI bound mistyped, a truncated
interval), but **no numbers fail to reproduce from the data**. A reproduction audit would find these
values reproducible except the play CI typo and the "p < .075" inequality. Unchecked-type: the abstract
over-claims the "nicer" inference, and the study is underpowered for its own effect. My call: **sound
data, reproducible analysis, over-stated central claim.** Strength of the checked-type defects: minor.
