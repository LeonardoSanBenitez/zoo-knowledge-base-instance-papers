# Word salad and the Power of Noise — notes

Author: maria, 2026-10-16. The RAG area's open question 2 called this "the cheapest decisive
test in the literature": if literal word salad improves a RAG reader, no information-theoretic
account of the noise effect can be right. I had a local GPU and an afternoon of pauses, so I ran
it, with the plan written down before I looked.

Nothing happened, which is itself a result. Word salad left accuracy where it was (−0.2 points;
the interval excludes the paper's +3). Real unrelated passages pulled it down slightly. One small
model, one setting: this does not refute the Power of Noise, but its most diagnostic form did not
appear where it should have been easiest to see.

What I was tempted to do and didn't: peek at 100 questions, see a trend, and stop. The plan file
is the only reason I can say the result was not chosen.

## 2026-10-17: gemma4 replication (pre-registered addendum, n = 200)

Gold only 70.5%, + word salad 65.5% (-5.0, p 0.16), + 5 unrelated Wikipedia 60.5% (-10.0, CI -15.5 to -4.5,
p 0.0012). The loss is abstention: NO-RES 13.5% -> 25.5% (26 vs 2 discordant; exploratory). Word salad
is ignored; plausible text competes. Two models now, neither shows the Power-of-Noise gain; the
real-document effect is negative in both and significant in the larger one. Recorded as c2.

## 2026-10-17 08:07 -- interpretations written BEFORE the qwen3.5:latest outcome is seen
- P2 rejects (abstention rises with real passages), P1 rejects or not: abstention-induction replicates outside gemma4,
  in a second family member of qwen at 2x the size of c1's model -> "plausible text makes readers decline" is not
  gemma-specific; still oracle-only, K = 5.
- P2 retains, P1 retains: gemma4's abstention effect does not replicate in qwen3.5:latest; the real-passage harm is
  model-specific (as qwen3.5:4b's -2.2 n.s. already hinted). Report as such; no reinterpretation.
- P1 rejects, P2 retains: real passages hurt by a route other than abstention (wrong extractions) -- inspect the
  C2-only errors descriptively, label it exploratory.
- Word salad (secondary): any sign; the c1/c2 conclusion (no Power-of-Noise gain) only changes if C1 - C0 >= +3 points
  with a CI excluding 0.
