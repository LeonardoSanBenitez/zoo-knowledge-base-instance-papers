# tran2026-single-vs-multi-agent-budget -- notes (maria, 2026-11-07)

This is the cleanest test of MASS's premise ("multi-agent topologies excel at complex reasoning"): fix the
thinking-token budget, then compare one agent against five multi-agent designs on multi-hop QA. The result is a
draw. The title says "outperform", but with question-level standard errors, 38 of 40 cells cannot tell the two
apart (t02). There is one cell each way, and the multi-agent cell contradicts the paper's own blanket sentence.

The appendix confidence intervals are about 2-4x too narrow and are not centred on their point estimates (t01). On
FRAMES the implied n is about 4 x 824. The likely cause is repeated runs pooled as if they were independent
questions, which is a pseudo-replication signature. Correct intervals would make even more cells "indistinguishable",
so the "single agent matches" reading gets stronger and "outperforms" gets weaker. My own bootstrap at n = 824
reproduces n and centring, which is the control.

The DPI argument is right and honestly limited. It covers an ideal reader with perfect context. Long-horizon agents
are not ideal readers, and that is exactly the regime where the paper predicts multi-agent can win. So this
paper does not refute MASS. It says MASS's evidence for "multi-agent is better" must come from regimes with
degraded context, and must be compared at equal compute. MASS compares at unequal compute: its multi-agent
teachers generate 2.4x the tokens.
