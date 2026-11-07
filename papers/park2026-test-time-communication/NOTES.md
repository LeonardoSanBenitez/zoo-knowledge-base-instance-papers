# park2026-test-time-communication -- notes (maria, 2026-11-07)

I read this one on purpose because it is the strongest case FOR multi-agent work in the chain, and an area that only
collects debunkings is a biased area. It holds up. Equal per-agent compute, best@k computed exactly from a pool of
64, token curves, a single agent given 5x the budget, a low-budget ablation where the team loses, and a reported
null on Terminal-Bench: this is the design the Sakana papers lack.

The result is concentrated: 4 of 25 games carry the solve-rate gain. Where it appears it is enormous (LP85: 0/64
alone, 13/20 as a team of five), and the furthest-level gain is broad (18/25 games, p = 0.043).

What it adds to the area is a dividing line. Communication and self-improvement pay when progress can be VERIFIED
(levels, scorers, gold answers). With only an LLM judge, or feedback that cannot rank partial solutions, the gains
vanish or become unmeasurable. MASS and RHI sit on the wrong side of that line by design ("open-ended research",
LLM-judged), and that is the regime where they most need, and least have, an outside check.
