# lee2026-rhi -- notes (maria, 2026-11-07)

Read as the inner loop of MASS (`lee2026-mass-self-supervision`). Body and QnA appendix read in full, prompts skimmed.
`reanalysis/r01_win_counts_execution_noise.py` covers bar transcription, the execution-noise SD, the H0 decomposition
and a trend null.

**What it is.** A textual multi-agent "harness" (roles, instructions, output contracts, hops) is appended to the task
prompt of a Claude coding agent. Each iteration runs the task once, an LLM judge compares the output with the
previous iteration's output, and an LLM optimiser rewrites the harness from the accumulated verdicts. It is evaluated
on 30 LLM-written ML research tasks against the same model at higher reasoning effort.

**What holds.** For sonnet-4.6 the win count against `max` rises 14 -> 16 -> 20 -> 20 -> 22 of 30. Even after
adding the execution noise the paper omits, that ordering is rare under a no-improvement null (p about 0.001-0.004).
Cost is lower than `max` or `ultracode` at equal or better judged quality.

**What to discount.**
1. Error bars are judge reseeding of one execution. Execution noise (SD about 2-2.7 wins per bar) is absent, and
   the follow-up paper's own appendix shows it is large.
2. About half of the opus-4.8 gain is the unoptimised starting harness H[0]. "RHI iterations" and "having a harness
   at all" are reported as one effect.
3. The optimiser is told to make "stronger contracts" and "more hops". The finding that contracts and hops carry
   the change is therefore partly an echo of that instruction, and the paper half-admits it.
4. The in-loop judge is never named. If it is a reporting judge, the gain is measured with the instrument that
   trained it.
5. The rubric's first criterion is deliverable coverage. Together with MASS's finding that gains are delivery
   rate, this suggests the lineage optimises "finish everything the prompt lists". That is useful, but it is not
   the same thing as better research.

**Lineage note.** RHI (July) -> MASS (October) is one group. MASS fixed RHI's main design problem by separating
the in-loop judge from the reporting judges, and inherited the rest: single executions, judge-only evidence, and an
optimiser prompt that predetermines the "information flow" finding.
