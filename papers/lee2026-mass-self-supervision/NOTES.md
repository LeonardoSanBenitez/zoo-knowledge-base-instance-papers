# lee2026-mass-self-supervision -- notes (maria, 2026-11-07)

Leonardo sent the repo (github.com/SakanaAI/mass). PDF v1 read in full, 39 pp. Repo cloned and offline tests run.
Three reanalysis scripts are in `reanalysis/`. Downloads are in `assets.py path paper-downloads/lee2026-mass-self-supervision`.

## What the paper does

One model, Qwen3.6-27B, plays executor, workflow optimiser and pairwise judge. The inner loop is RHI from the
same group, arXiv 2607.15524: an elite-size-1 search over textual multi-agent workflows (roles, instructions,
output contracts, call order), where each proposal is run once and judged against the incumbent by the same model.
The outer loop runs the retained workflow 18 times per task, ranks the runs with self-judged Bradley-Terry, and
fine-tunes LoRA on the top 15 with the workflow text stripped from the prompt. There are two cycles. Frontier
models (GPT-5.5, Opus 4.8) are used only to report results.

## What survives, what does not

**Survives.** The trained model delegates without being asked: 1/110, then 48/110, then 87/110 episodes.
It delivers a paper or report far more often within the time limit: MLR 52% to 83%, Asta 50% to 76%.
With the executor held fixed, workflows proposed by L1 beat those proposed by L0 64% of the time (Table 1;
this is the correct design, but no counts are given).

**Does not survive as stated.**
1. *"Higher performance per output token."* On MLR-Bench and AstaBench the aggregate is exactly delivery rate times
   the mean among delivered outputs, and the mean among delivered outputs FALLS. The README's separate 107-task
   MLR run shows the same pattern: flat at about 3.0, with all of the gain in delivery. On DSBench, 94% of the
   per-token gain is fewer tokens around a noise-size score change. The student finishes; it does not do better
   research per finished paper. To its credit, the paper says most of this in Appendix C.5. The abstract does not.
2. *"Post-trained models discover workflows faster"* (Fig 3a). The plotted quantity is a running maximum of
   unanimous verdicts over noisy single executions. The paper itself shows an identical workflow going 6-0 and then
   0-6. With no optimisation at all, the per-execution probability read at iteration 0 predicts all three curves to
   within about one task, and for L0 it predicts MORE coverage than observed. The first-hit hazard declines over
   iterations. The known-answer simulation shows that this statistic cannot detect a real trend (3.5% power for a
   strong one) once tasks differ. The generational gap is present at iteration 0, before any search, so it is the
   executor and not the optimiser.
3. *Held-out gain at L1.* Two of the three test tasks are below 50%. The six judgments per pair are repeated reads of
   one output. Indistinguishable from zero.
4. *Training efficiency of multi-agent traces.* The 4.3-point headline is 0.45 SE at the pair level, between arms
   that differ in task coverage, sampler and checkpoint rule. The controls' checkpoints were chosen on the evaluation
   tasks.

**The missing arm** (c10). Nobody trained a student on the trajectories of the unoptimised starting workflow. Several
facts suggest the optimisation may not matter beyond "some multi-agent prompt plus a completion filter": the
coverage null; Fig 7b's flat win rate around 0.5; teacher selection that can drop only 3 of 18 runs (m03: a ceiling of
0.26 SD); and a base model that already delegates 110/110 when merely told to form a team. One more SFT run
would settle it.

## How it reads as a document

The appendix is unusually candid: it says the observations are not independent, explains why significance is not
inferred, separates the conditional means, and states that delegation is not the public-benchmark mechanism.
The repo's `docs/experiment_coverage.md` lists exactly what it cannot reproduce. The overreach is concentrated
in the abstract and the claim boxes, which state more than the appendix supports. That shape is common, and
worth knowing: in this paper, read the appendix first.

## The one example to remember

In test task 305, the student had the simulator rewritten so that objects teleport toward the goal instead of being
pushed, reported success on every task type, and won 5 of 6 frontier-judge verdicts (G.3). An RSI loop is only
as anchored as its outside judge, and here the outside judge rewarded the redefinition of success.

## Scripts

- `m01_tables_arithmetic_and_units.py` (stdlib, run with `python -I`): Table 5 sums, intervals at three units,
  delivery decomposition, per-token ratio decomposition, Fig 6 interpolation, and the README's 107-task MLR run.
- `m02_coverage_curve_null.py` (numpy/scipy, 56 s): geometric first-hit model with H0, beta-geometric and trend
  fits on the Fig 3a curves, plus known-answer worlds with no improvement and with forced improvement.
- `m03_teacher_selection_ceiling.py` (numpy, 14 s): the repo's own tournament and BT code under latent-quality
  worlds with judge accuracy 0.5 / 0.6 / 0.73 / 0.93 / 1.
