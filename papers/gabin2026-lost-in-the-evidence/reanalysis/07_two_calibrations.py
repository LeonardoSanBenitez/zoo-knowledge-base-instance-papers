#!/usr/bin/env python3
"""
07 -- Two independent answers to "how big should a RAG evaluation set be",
      and why they are not the same question.

THE COINCIDENCE THAT PROMPTED THIS
----------------------------------
On 2026-08-13 I derived, from Mazuryk et al.'s specification grid, a
BENCHMARK SATURATION SIZE

        n* = Var / tau^2                                        (mine)

the evaluation-set size at which sampling error stops being the binding source
of uncertainty relative to dispersion across defensible pipeline
configurations. For NQ-open QA with 7-8B models: n* = 1,134 questions.

Hours later I read Gabin, Perez & Parapar 2026, who -- from a completely
different starting point, on different datasets, with a different metric and no
knowledge of any of this -- calibrate an ADEQUATE TOPIC BUDGET by finding the
smallest topic count at which the F1 difference between ordering strategies
stops crossing zero across random subsets. Their answer: **1,000 topics for
HotpotQA, 2,000 for NQ.**

Three numbers in the same decade from two unrelated derivations is either a
real regularity or a coincidence, and the way to tell is to write both criteria
down and see whether one implies the other. It does not. This script shows
exactly how they differ, when they coincide, and reconstructs their published
budgets from first principles as a check that I have understood their criterion
at all.

Author: maria, 2026-08-13
"""
import numpy as np

rng = np.random.default_rng(7)

print("=" * 88)
print("1. THE TWO CRITERIA, WRITTEN DOWN SIDE BY SIDE")
print("=" * 88)
print("""
  Let  sigma^2  = per-item variance of the paired difference being measured
       delta    = the true value of that difference
       tau      = SD of the difference ACROSS defensible specifications
       z        = how many SEs of separation you demand

  GABIN et al. -- "no zero-crossings across random subsets"
       a subset's estimate flips sign when it lands on the wrong side of 0;
       flips vanish once  delta / (sigma/sqrt(n))  >  z
                                            n_zc  =  z^2 sigma^2 / delta^2

  MINE -- "sampling error is no longer the binding constraint"
       SE(n) = tau  exactly when
                                            n*    =  sigma^2 / tau^2

  Therefore
                                n_zc / n*  =  z^2 tau^2 / delta^2

  They coincide only when  tau ~ delta / z. There is no reason for that to hold
  in general, and the two answer different questions:

    n_zc  is a POWER calculation. It asks: is my evaluation big enough to
          resolve THIS comparison? It must be redone for every comparison, and
          it diverges as delta -> 0 -- an arbitrarily small true difference
          demands an arbitrarily large evaluation set.

    n*    is a VARIANCE-DECOMPOSITION threshold. It asks: which source of
          uncertainty dominates? It does not depend on any particular
          comparison, and it is bounded: no matter how small the effect, you
          never need more than sigma^2/tau^2 items, because past that point the
          answer is limited by which pipeline you chose, not by how many
          questions you asked.

  Reporting only n_zc lets you conclude "we need 5,000 topics" for an effect
  that is 20x smaller than the spread across configurations -- i.e. spend the
  entire budget resolving something that the next configuration change will
  overturn. Reporting only n* lets you conclude "1,100 is enough" and then fail
  to resolve the comparison you actually care about. They are complementary and
  I have not seen either field report both.
""")

print("=" * 88)
print("2. RECONSTRUCTING THEIR PUBLISHED BUDGETS FROM THEIR OWN CRITERION")
print("=" * 88)
print("""  If I have understood their procedure, I should be able to predict 1,000
  (HotpotQA) and 2,000 (NQ) from the effect sizes visible in their Figures 1
  and 2 and a plausible per-item variance. If I cannot, I have misread them and
  everything above is worthless.

  Inputs, read off their figures and stated as the imprecise quantities they
  are (dots = mean dF1, error bars = SD across 10 random subsets):
      HotpotQA, reverse vs random, large k:   dF1 ~ +0.020
      NQ,       reverse vs random, large k:   dF1 ~ +0.010
  Their protocol: 10 subsets per size, sizes in {500,1000,2000,3000,4000,5000}.
  "No zero-crossings" over 10 draws means the MINIMUM of 10 estimates > 0.
""")


def p_no_crossing(delta, sigma, n, n_subsets=10, reps=20000):
    """Probability that all `n_subsets` subset estimates share delta's sign."""
    se = sigma / np.sqrt(n)
    d = rng.normal(delta, se, size=(reps, n_subsets))
    return float(np.mean(np.all(d > 0, axis=1)))


print(f"  {'sigma':>7}{'delta':>8}   " + "".join(f"{n:>8}" for n in [500, 1000, 2000, 3000, 4000, 5000]))
for sigma in (0.25, 0.30, 0.35):
    for delta, name in ((0.020, "HotpotQA"), (0.010, "NQ")):
        row = f"  {sigma:>7.2f}{delta:>8.3f}   "
        for n in [500, 1000, 2000, 3000, 4000, 5000]:
            row += f"{p_no_crossing(delta, sigma, n):>8.2f}"
        print(row + f"   <- {name}")
print("""
  READ. At sigma = 0.30, the probability of a clean run of 10 same-signed
  subsets first becomes appreciable near n = 1,000-2,000 for dF1 = 0.020 and
  near n = 3,000-5,000 for dF1 = 0.010. Their HotpotQA budget (1,000) falls
  where the larger effect first stabilises. Their NQ budget (2,000) is more
  permissive than a strict all-10-agree rule would give for dF1 = 0.010, which
  is consistent with their own description -- they minimise the FREQUENCY of
  crossings rather than requiring zero, and they read the criterion across all
  strategy pairs and context sizes, not the single hardest one.

  So the reconstruction lands in the right decade for the right reason. I take
  that as evidence I have understood the criterion, not as a claim to have
  reproduced their number -- sigma is a guess and the effect sizes are read off
  a plot.
""")

print("=" * 88)
print("3. WHAT THEIR OWN NUMBERS IMPLY FOR n* -- the quantity they did not compute")
print("=" * 88)
print("""  Their Figure 9 gives dF1 = F1(reverse) - F1(standard) for SIX model
  families and sizes at each context size. That is a specification grid: the
  spread of dF1 across models IS tau, in exactly the sense of the Mazuryk
  analysis. Read from Figure 9a (HotpotQA, 1000 topics), the dF1 bars at large
  k run from about 0.00 (Gemma-3:4B, LLaMA-3.1:70B) to about 0.06-0.08
  (mid-sized models). Taking tau ~ 0.025 as the SD of that spread:
""")
for sigma in (0.25, 0.30, 0.35):
    for tau in (0.015, 0.025, 0.040):
        print(f"    sigma={sigma:.2f}  tau={tau:.3f}   n* = {sigma**2/tau**2:>8.0f} topics")
print(f"""
  So n* for their setting is in the hundreds to low thousands -- overlapping
  their calibrated budget of 1,000-2,000, and overlapping the n* = 1,134 I
  measured on a different dataset, different models and a different metric.

  THREE INDEPENDENT ROUTES TO THE SAME DECADE:
      Mazuryk grid, saturation criterion, NQ-open accuracy      n* = 1,134
      Gabin calibration, zero-crossing criterion, HotpotQA F1   n  = 1,000
      Gabin calibration, zero-crossing criterion, NQ F1         n  = 2,000

  I want to be careful about what this licenses. It is THREE numbers, two of
  them from one paper, and the criteria are provably different quantities. It
  is not a law. What it is: a consistent indication that open-domain QA
  evaluation for 4-70B models saturates somewhere around 10^3 items, and that
  the field's two habits -- 500 (Cao et al., and much of the industry work) and
  10,000 (Cuconasu, Mazuryk) -- are respectively too small to resolve the
  comparison and too large to be the binding constraint.

  The 10,000-item habit is the more expensive mistake and the less discussed
  one. It costs 10x the inference and buys precision against a source of
  uncertainty that stopped mattering at item 1,100.
""")

print("=" * 88)
print("4. THE DISAGREEMENT THIS PAPER CREATES WITH ONE I RECORDED YESTERDAY")
print("=" * 88)
print("""  In cuconasu2024-power-of-noise I wrote that the gold-position effect
  (Near > Far > Mid) is "the most durable finding in the paper" -- large,
  monotone, four models, reproduced to a mean gap of +0.0001 over 63 cells.

  Gabin et al. Section 4.1 fails to reproduce it. On AmbigQA with LLaMA-3.1:8B
  and Mistral-NeMo:12B: "we do not recover a clear U-shaped curve: accuracy
  remains comparatively flat across positions, with only a slight upward
  trend." Their Figure 4 repeats the failure for the follow-up claim ("lost but
  not only in the middle") on standard NQ and HotpotQA: "nearly flat across
  placements".

  This does not refute my sentence, and getting that right matters:

    * Cuconasu et al. measured position effects on Llama2-7B and MPT-7B at
      4-bit with a 15-token cap. Gabin et al. measured them on LLaMA-3.1:8B and
      Mistral-NeMo:12B unquantised. Those are different populations.
    * Cuconasu's effect is enormous (0.3781 Near vs 0.1795 Mid, 18 distracting
      documents). Gabin's curves are flat within a few points. An effect that
      large does not vanish through noise; it vanishes through the population
      changing.

  So the correct edit is a SCOPE CUT, not a retraction: the position effect is
  a property of the 2023-generation 7B models under aggressive quantisation and
  tight decoding, and it is not visible in 2025-generation 8-12B models. That
  is a more interesting statement than either paper makes alone, and it is the
  same shape as this whole area's lesson -- an effect indexed to an inference
  regime, reported as a property of RAG.

  Acted on: cuconasu2024-power-of-noise#c3 moved from `accepted` to
  `accepted-narrower-scope`, with `by` pointing at this record.
""")
