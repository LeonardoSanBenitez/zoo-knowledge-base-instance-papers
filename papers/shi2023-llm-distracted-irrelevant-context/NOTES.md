# shi2023 GSM-IC -- notes (maria, 2026-10-17)

Why this paper: my word-salad experiment (2026-10-16/17) found that plausible unrelated passages hurt a reader
and word salad did not. GSM-IC is the canonical "irrelevant context distracts LLMs" result, so I read it to see
whether it supports that reading -- and whether its headline would survive a content-free control.

## What I checked, in order
1. **Macro accuracy is instrument-relative (g1, g2).** Class sizes 192-640 (median 640) in the released data;
   GSM-IC-4K has ~40 variants per base. Beta model pinned to micro + macro: LTM 18% -> ~35% at m = 10, ~4% on
   the full set. Known-answer test passes under exchangeability; under template heterogeneity it under-predicts
   at small m.
2. **Selection on success (g4).** Bases = "solvable by at least one technique". Same COT prompt: 60.3% on the
   1,000-problem pool, 95% on the bases, 72.4% with distractors. A null world with ZERO distraction and k = 2-4
   predicts 68-74%. The headline drop is not identified; the in-topic vs off-topic contrast (17.6 pts) is.
3. **Question edits (g5).** 31.4% of variants also rewrite the question (pronoun -> name, a grammar fix). That
   is a confound bundled into the treatment.
4. **Local test (g3, pre-registered in reanalysis/PLAN.md, committed before any call).** Running.

## How it connects
- maria2026-word-salad-noise-test: the same lesson from the other side -- relatedness, not mere presence, distracts.
- The selection argument is the benchmark analogue of survivorship conditioning: the base set was conditioned on
  the outcome, then perturbed. Any "robustness drop" benchmark built from items a model already solves inherits it.
