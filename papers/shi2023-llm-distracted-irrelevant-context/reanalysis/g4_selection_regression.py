"""g4 -- How much of GSM-IC's headline drop can selection-on-success produce with ZERO distraction?

Printed numbers (code-davinci-002, COT, 1 exemplar w/o irrelevant context):
  GSM8K dev (all 1,000; Table 5)          60.3   -- the population the bases were drawn from
  base set (100 'solvable' bases; Table 2) 95.0
  GSM-IC-4K micro (Table 3)               72.4   -- with one irrelevant sentence
  Table 4 micro by topic: in-topic 63.1, off-topic 80.7
NULL WORLD: problem b has a latent success probability p_b ~ Beta(mu k, (1-mu) k), mu = 0.603. Any change to
the prompt (an irrelevant sentence, or a neutral one) is a fresh draw at the same p_b -- prompt sensitivity,
no distraction. Bases are selected for having been solved. Then the expected 'with-sentence' accuracy on the
bases is E[p | selected]. Two selection rules bracket the paper's ('solved by at least one technique'):
  R1  solved by COT itself:         E[p | sel] = E[p^2]/E[p] = (mu k + 1)/(k + 1)
  R4  solved by >= 1 of 4 attempts sharing p_b (COT, LTM, PROGRAM, 0-COT):  E[p(1-(1-p)^4)] / E[1-(1-p)^4]
Under R1 the base accuracy is 100% by construction (paper: 95), under R4 it is mu / P(sel).
Output: the zero-distraction micro accuracy as a function of k, and the k at which it equals 72.4.
Author: maria 2026-10-17."""
import numpy as np
from scipy import integrate, stats
mu = 0.603
def r1(k): return (mu * k + 1) / (k + 1)
def r4(k, r=4):
    a, b = mu * k, (1 - mu) * k; f = lambda p: stats.beta.pdf(p, a, b)
    sel = integrate.quad(lambda p: (1 - (1 - p) ** r) * f(p), 0, 1, limit=200)[0]
    num = integrate.quad(lambda p: p * (1 - (1 - p) ** r) * f(p), 0, 1, limit=200)[0]
    return num / sel, mu / sel
print(f"{'k':>6} {'R1 micro':>9} {'R4 micro':>9} {'R4 base acc':>12}")
for k in (0.5, 1, 2, 2.28, 3, 4, 6, 10, 30):
    m4, b4 = r4(k); print(f"{k:6.2f} {r1(k):9.3f} {m4:9.3f} {b4:12.3f}")
from scipy.optimize import brentq
k1 = brentq(lambda k: r1(k) - 0.724, 0.01, 100)
print(f"\nR1: zero-distraction micro = 72.4 at k = {k1:.2f}  (g1 fitted k = 3.86 for the same row from micro/macro)")
print(f"R1 at k = 3.86 (g1): {r1(3.86):.3f}; R4 at k = 3.86: {r4(3.86)[0]:.3f}")
print("""
READ. In the null world, with heterogeneity of the size g1 recovered independently from the macro numbers (k ~ 2-4),
selection on COT success (R1) alone puts the with-sentence accuracy at 68-74% -- the printed 72.4 is inside it. R4
cannot be the operative rule: it predicts a base accuracy of 66-74%, not the printed 95, so selection was close to
'solved by COT' for this row and R1 is the relevant bracket. Hence the HEADLINE drop (95 -> 72.4) is not identified as
distraction by the printed numbers: a neutral-sentence control on the same bases is the missing condition. What IS
identified is the CONTRAST between sentence types on the same bases (in-topic 63.1 vs off-topic 80.7, 17.6 points):
selection cannot produce a difference between two kinds of sentence. Note off-topic 80.7 is ABOVE the R1 null at
k = 2-4: off-topic sentences may cost nothing at all.""")
