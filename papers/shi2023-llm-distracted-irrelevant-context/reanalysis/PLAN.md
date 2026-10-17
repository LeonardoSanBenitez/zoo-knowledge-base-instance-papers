# GSM-IC local decomposition test -- plan fixed 2026-10-17 07:22, before any model call
Model qwen3.5:4b (Ollama, Q4_K_M), think off, greedy (temperature 0, seed 0), num_predict 256, num_ctx 4096.
Prompt: the paper's 1-shot COT exemplar WITHOUT irrelevant context (Fig. 2, [Original Problem] + [COT Solution]),
then "Q: <problem>\nA:". Answer = number after the last "The answer is", else the last number in the response;
correct iff it equals the gold integer (commas and $ stripped, trailing .0/.00 accepted).
Conditions, per base problem b (all 100 bases, in a fixed shuffled order, seed 7):
  B  original problem
  N  NEUTRAL control: "This problem is from a worksheet." inserted immediately before the question sentence
     (same position as GSM-IC's sentence; no number, no role, no topic -- the minimal-content extra sentence)
  V1-V3  three GSM-IC variants drawn uniformly at random (seed 7) from that base's class
Then D: 200 other dev problems (not bases, seed 7), condition B only.
Stop rule: all done, or 08:45 local, whichever first; analyse what is complete, by base (B,N,V together).
PRE-REGISTERED QUANTITIES
  Q1 selection: acc_B(bases) - acc_B(D). Positive = the base set is an easy subset for an unrelated model too.
  Q2 the paper-style drop for THIS model, on bases it solves (S = {b: B correct}, the paper's own construction):
     1 - micro_V(S).
  Q3 neutral drop on S: 1 - acc_N(S) -- what ANY extra sentence costs, selection-on-success included.
  Q4 content-specific distraction: acc_N(S) - micro_V(S), paired by base (bootstrap over bases, 10,000).
  Prediction (written now): Q3 > 0 and a non-trivial share of Q2; Q4 > 0. If Q3 ~ 0, the paper's drop is all content.
  Q5 (secondary) macro at m = 3 on S vs g1's Beta-model prediction from micro_V(S) and the class-size argument.

## Deviation log
- 2026-10-17 ~07:45: ACCIDENTAL INTERIM LOOK. While testing an exploratory addition to g6_analyse.py I ran it on the
  live results file instead of the synthetic one and saw Q2 for the first 23 complete bases (paper-style drop 0.063).
  Nothing else was viewed. The stop rule is time-based (08:45 or all jobs) and unchanged; Q1-Q5 and their tests were
  fixed before this and are not altered. Declared here so a reader can discount accordingly.
