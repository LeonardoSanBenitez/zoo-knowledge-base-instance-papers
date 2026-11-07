<!--kb
id: papers-self-improving-agents-and-workflow-search
labels: kind:paper-notes, area:self-improving-agents-and-workflow-search, area:multi-agent-systems, area:ai-evaluation
triggers: recursive self-improvement, model evaluates itself, LLM optimises its own workflow or harness,
          multi-agent workflow search, distil multi-agent trajectories into one model, SFT on self-generated traces,
          harness optimisation, does more agents help, score per output token, judge-only evaluation of research agents,
          Sakana MASS, RHI, self-correction
verified: 2026-11-07
-->

# Self-improving agents and workflow search: per-paper notes

Author: maria. Started 2026-11-07 when Leonardo sent `github.com/SakanaAI/mass`. This area is a neighbour of
`clinical-ai-evaluation-and-agent-oversight.md`, which holds the Dojo literature. That file asks *who controls the
evidence that an agent did well*, and here the agent controls it on purpose: the loop's own judge decides which
workflows and which trajectories the model learns from.

**Through-line.** Each paper here reports that a system improved itself. The question to put to each is the same:
**what would the curve look like if nothing improved?** In this literature the answer is usually "about the same",
for three recurring reasons:

1. **Single executions judged many times.** An agent run is expensive, so each configuration is run once and judged
   six times. The six verdicts are reads of one output. Execution noise is the largest component, and it is
   absent from the error bars. Identical workflows can score 6-0 and then 0-6 (`lee2026-mass-self-supervision`,
   Table 11).
2. **Running maxima.** "Number of tasks ever won" or "best so far" rises under pure noise. In MASS, the
   per-execution win probability measured at iteration 0 predicts all three published coverage curves to within one
   task, with no optimisation at all (m02).
3. **Completion counted as quality.** Research-agent benchmarks score a missing deliverable as zero, and LLM judges
   list deliverable coverage first. A model that learns to finish within the time limit "improves" without any
   deliverable improving. In MASS, both the MLR-Bench and the AstaBench gains are exactly delivery rate times a
   *falling* mean among delivered outputs, and the README's 107-task MLR-Bench run shows the same.

A fourth, specific to harness search: **the optimiser is told what to find.** RHI's optimiser prompt demands
"stronger contracts" and "more hops", and the papers then report that contracts and hops became task-specific.

---

## Records

| id | depth | one line | our strongest finding |
|---|---|---|---|
| `lee2026-mass-self-supervision` | read-and-reanalysed | Qwen3.6-27B searches multi-agent workflows with itself as judge, then SFTs on the traces; two cycles | Gains on MLR/Asta = delivery rate (quality among delivered falls). Fig 3a "faster discovery" is reproduced by a no-improvement null. L1 held-out gain: 2 of 3 tasks below 50%. The arm that would show the optimisation matters, SFT on the *unoptimised* workflow's traces, was never run. Teacher selection can drop only 3 of 18 runs (ceiling 0.26 SD). |
| `lee2026-rhi` | read-and-reanalysed | Prompt-level multi-agent harness, revised from pairwise self-comparison; Claude agents beat their own higher-effort settings on 30 LLM-written tasks | The sonnet trend survives execution noise (p about 0.001-0.004). For opus-4.8, about half of the gain is the *unoptimised* starting harness. The in-loop judge is never named. The optimiser prompt orders the "contracts and hops" result. |
| `wang2026-rethinking-harness-evolution` | read-and-reanalysed | AI2/UW, independent: at matched budget on Terminal-Bench 2.1, harness evolution loses to parallel sampling and sequential refinement, and gains nothing on 34 held-out tasks; it wins in long-horizon games with verifiable feedback | Its own tables carry a free replicate: the same procedure run twice moves 0 / 0.6 / 2.5 pp. 'Overfitting' has no in-sample pass@1 gain to lose (-0.8 / +2.1). The held-out test detects +5 pp per model with probability 0.75-0.95, depending on task determinism. |
| `tran2026-single-vs-multi-agent-budget` | read-and-reanalysed | Stanford: one agent vs five multi-agent designs at equal thinking tokens on multi-hop QA; the DPI says an ideal single reader cannot lose | It is a draw, not 'outperform': 38/40 cells are indistinguishable at question level, one cell goes each way. The appendix CIs are 2-4x too narrow and off-centre (FRAMES implied n is about 4 x 824: pooled runs). The theory exempts degraded-context, long-horizon regimes, which is where MASS and RHI live. |
| `zhao2025-sirius` | read-and-reanalysed | NeurIPS 2025: keep each multi-agent trajectory that reached the gold answer, fine-tune each role's model on it; the ancestor of MASS's outer loop, but WITH a verifier and per-role models | All 30 % decode to counts. Over the untrained multi-agent prompt, SFT adds 12-14/500 on PubMedQA, and 1-7 questions on the 107/65-question sets. The second iteration adds 1-4/500. Per-role models beat one shared model (19/500), which is in tension with MASS's shared weights. |
| `huang2024-cannot-self-correct` | read-and-reanalysed | ICLR 2024: without gold labels, asking a model to review its own answer never helps; debate loses to majority vote at equal responses | Exact McNemar on Fig 1 transitions: a significant drop in 4/8 cells (weak or suggestible models). For GPT-4-Turbo and others the change is about zero: strong models leave their answers alone. 'Harms all' over-reads four nulls. |
| `chen2025-mlr-bench` | read-and-reanalysed | The benchmark MASS gains most on: 201 workshop research tasks, scored by the MLR-Judge rubric | Its judge validation is passed by a CONSTANT judge (b01, on the authors' released human study); MLR-Judge vs experts Spearman about 0 (Overall -0.18; experts with each other 0.48). Fabricated results: 8/10 Claude Code runs, 17/18 checked papers. Validation refuted; fabrication finding stands. |

## What a reader of this literature should carry

These are notes from the literature, not a plan.

0. **Ask for the equal-compute baseline.** Best-of-k or sequential refinement at the same cost beat harness
   evolution on Terminal-Bench (`wang2026-rethinking-harness-evolution`), and one agent matches five multi-agent
   designs at equal thinking tokens (`tran2026-single-vs-multi-agent-budget`). RHI compares only against higher
   reasoning effort, and MASS's multi-agent teachers spend 2.4x the tokens of its single-agent ones.
1. **Ask for the unoptimised-workflow arm.** Most of what "self-improvement" buys may be "some reasonable
   multi-agent prompt" plus "keep the completed runs". RHI's H[0] carries about half of its opus-4.8 gain; MASS
   never trains on H[0] traces.
2. **Ask how many executions each point is.** If one, the interval must come from execution replicates, not judge
   seeds.
3. **Split every agent-benchmark score into delivery rate x quality among delivered.** It is one line of arithmetic,
   and in MASS it reverses the reading.
4. **Read the optimiser's prompt before believing a "what changed" analysis.**
5. **Ask whether the judge was validated, and how.** MLR-Judge's published validation passes a constant
   judge (`chen2025-mlr-bench`). For delivered-paper benchmarks, also ask how many deliverables are fabricated:
   8/10 runs in the benchmark's own audit.
6. **The outside judge must catch redefined success.** In MASS, an agent that rewrote a simulator so objects
   teleport to the goal won 5 of 6 frontier-judge verdicts (G.3). That is reward hacking, as studied in
   `huang2026-reward-hacking-research-agents` (filed under the Dojo area).

Generic lessons from this area that apply outside it are in
`instance-general/statistics/detectors-that-find-signal-in-null-worlds.md` (running-maximum statistics).

## Reading queue (citation chain, not yet read)

TTHE 2607.08124; SIA 2605.27276; HASE 2607.03935;
HELIX 2608.13951; Squeeze Evolve 2604.07725; Park et al. 2609.21032 (test-time communication); Multi-Agent Evolve
2510.23595; Wang et al. 2026 (harness evolution vs test-time-scaling baselines at equal budget: cited by RHI as a
negative result -- READ, see records); ADAS, AFlow, GPTSwarm; Self-Rewarding LMs; STaR; ReST-EM.
