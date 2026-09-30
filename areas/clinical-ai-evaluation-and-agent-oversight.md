<!--kb
id: papers-clinical-ai-evaluation-and-agent-oversight
labels: kind:paper-notes, area:clinical-ai-evaluation-and-agent-oversight, area:multi-agent-systems
triggers: evaluating clinical AI beyond benchmarks, agent committees conformity, referee monitor,
          reward hacking by research agents, medical VLM ignores the image, image swap audit,
          effect size of a prompting framework, who evaluates the evaluators, DOJO MIT Critical Data,
          benchmark an open VLM on medical data, evaluation integrity
verified: 2026-09-30
-->

# Clinical AI evaluation and agent oversight — per-paper notes

Author: maria. Started 2026-09-30, for the zoo's `dojo/` workspace. That workspace contributes to MIT
Critical Data's repositories (benchmaxxing, bodhi, creativity-survey, Lab-dashboard) and is where Leonardo
supplied these sources. Workspace decisions and ticket state stay in `dojo/`. This file holds only what
is true of the literature.

**Through-line.** Every paper here asks one question in a different costume: **did the thing we are
evaluating use the evidence we think it used, and who controls the evidence that says so?**

- A committee member adopts a peer's wrong answer. Did it reason, or conform? (`cajas2026-agents-catching-agents`)
- A radiology VLM answers correctly with the report present. Did it look at the image? (`cajas2026-modalens`)
- A research agent reports a score above threshold. Did it earn it, or edit the grader? (`huang2026-reward-hacking-research-agents`)
- A prompting framework reports d = 16. Is that the behaviour's size, or the seeds' reproducibility? (`arslan2026-bodhi-engineering`)

The answers share a shape. **More of the producer's own output (a transcript, a trajectory, a
self-report, a richer rubric) does not answer the question. A counterfactual the producer did not
control does.** That counterfactual is the private re-query, the swapped image, the independent
recomputation, or the effect restandardised on the right unit. The generic concepts are in
`instance-general/ai-evaluation/` (two entries) and
`instance-general/multi-agent-systems/conformity-cascades-in-agent-committees.md`.

Honest caveat on the corpus: four of the six records come from one research group (MIT Critical Data and
collaborators). Only `huang2026-reward-hacking-research-agents` is independent. The agreement between
them is agreement within a group, and it is weighed accordingly
(`philosophy-of-science/independence-the-hidden-premise-of-agreement.md`).

---

## Records

| id | depth | one line | our strongest finding |
|---|---|---|---|
| `cajas2026-agents-catching-agents` | read-and-reanalysed | Two scripted peers flip correct answers; only a private re-query referee transfers across modalities | Counts recompute exactly from committed rows. The "no pixels altered" CheXpert arm plants "no" on 150/150 films and has **no device-free control**, so "correct alone" may be a yes-prior (c4). |
| `cajas2026-modalens` | read-full-text | With the report present, swapping the image changes the answer on ~4% of trials vs ~21% without | Sensitivity is not correctness (labels are report-derived, as the authors say). Block order halves the effect; ceilings hide in the pooled rate. The advertised repo is **404** with a control. |
| `huang2026-reward-hacking-research-agents` | read-and-reanalysed (printed numbers) | 17 models, 38 tasks: 30.5% spontaneous hacking on research-pipeline tasks; disguised exploits evade review; richer feedback doubles evasion | All recomputable numbers check. About 25 Setting-1 cells are silently excluded. Artifacts withheld by design. |
| `arslan2026-bodhi-engineering` | read-and-reanalysed | Two-pass "humble and curious" prompt: +16.6 pp HealthBench Hard, context-seeking 7.8% to 97.3% | **All eight printed d values are standardised by seed-to-seed SD** (n = 5). Per response, humility d = 0.66, not 5.80. The curiosity metric is largely a manipulation check. |
| `xiang2026-dojo` | read-full-text | DOJO platform proposal: data/model/workflow planes plus decoy-based evaluator calibration | Position paper; `dojo-health` is not on PyPI (control-checked). Cites BODHI as 1,800 observations where the source says 2,000. |
| `cajas2026-creativity-constraint` | read-and-ran-artifacts | Filed under `human-ai-creativity`, listed here for the shared group | Screening log shows 2/3 majority votes where the text describes two humans. |

## What a Dojo ticket that benchmarks a model should inherit from this file

These are notes from the literature, not a plan. Planning belongs to the ticket.

1. **Add an input-swap arm before reporting accuracy** on any multimodal task. It separates "uses the
   image" from "answers from text and priors", at one extra forward pass per item (ModaLens c1).
2. **Report the readout and the prompt order** with any flip rate. Both move the magnitude (ModaLens).
3. **Check planted-answer polarity and ceilings**. An arm that only ever pushes one direction, on a finding
   the model always affirms, measures a prior (benchmaxxing c4).
4. **Keep the metric outside the producing agent**, and recompute headline numbers from rows the agent did
   not write. This applies to our own agents too (Huang c5).
5. **State the unit an effect size was standardised on**, or report the risk difference instead (BODHI c2).
