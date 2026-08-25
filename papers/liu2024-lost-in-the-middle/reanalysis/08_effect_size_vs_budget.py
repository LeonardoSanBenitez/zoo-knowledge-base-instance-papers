#!/usr/bin/env python3
"""
08 -- Why the field's evaluation-set sizes are inherited from an effect that no
      longer exists.

THE OBSERVATION
---------------
Three papers in this area, three evaluation budgets, three effect sizes:

    Liu et al. 2024      n = 2,655 questions   position effect > 20 accuracy points
    Gabin et al. 2026    n = 1,000 / 2,000     ordering effect ~ 1-2 F1 points
    Cuconasu / Mazuryk   n = 10,000            noise effect ~ 2 accuracy points

The budgets are all in the same decade. The effects are an order of magnitude
apart. That cannot be right, and this script quantifies how wrong it is.

The claim I am testing: the field settled on "a couple of thousand items"
while studying a very large effect, and kept the habit while moving on to
effects ten to twenty times smaller, without anybody redoing the arithmetic.

Author: maria, 2026-08-13
"""
import numpy as np

print("=" * 88)
print("1. HOW WELL RESOLVED IS EACH PAPER'S HEADLINE EFFECT?")
print("=" * 88)


def se_unpaired(p1, p2, n):
    """Upper bound on the SE of a paired difference of two rates on the same n
    items. Conservative: the true paired SE is smaller, so every ratio below is
    an UNDERSTATEMENT of how well resolved the effect is."""
    return float(np.sqrt(p1 * (1 - p1) / n + p2 * (1 - p2) / n))


rows = [
    # label, n, p_low, p_high, source of the two rates
    ("Liu 2024, GPT-3.5-Turbo, best vs worst gold position",
     2655, 0.561, 0.763,
     "worst-case 20/30-doc setting is at or below closed-book 56.1%; best position "
     "read from Fig. 5 at ~76%"),
    ("Liu 2024, GPT-3.5-Turbo, closed-book vs oracle",
     2655, 0.561, 0.883, "Table 1"),
    ("Liu 2024, LongChat-13B, closed-book vs oracle",
     2655, 0.350, 0.834, "Table 1"),
    ("Liu 2024, Flan-UL2 WITHIN its 2048-token training window",
     2655, 0.500, 0.519, "Sec 4.1: 1.9% absolute best-worst difference"),
    ("Gabin 2026, HotpotQA, reverse vs random ordering",
     1000, 0.450, 0.470, "Fig. 2a, dF1 ~ 0.020, F1 level ~0.46"),
    ("Gabin 2026, NQ, reverse vs random ordering",
     2000, 0.480, 0.490, "Fig. 2b, dF1 ~ 0.010"),
    ("Cuconasu 2024, Llama2 Near, 14 random docs vs gold only",
     10000, 0.5642, 0.5859, "Table 2"),
    ("Mazuryk 2026, median over preferred configs, 14 docs vs 0",
     10000, 0.8000, 0.7871, "Table 6, median E = -0.0129"),
]

print(f"  {'study / contrast':<56}{'n':>7}{'effect':>9}{'SE':>8}{'|E|/SE':>8}{'n_zc':>8}")
R = {}
for lbl, n, lo, hi, src in rows:
    eff = hi - lo
    se = se_unpaired(lo, hi, n)
    # n needed for z = 2.58 separation, i.e. the smallest evaluation set at
    # which this effect would be resolved at p<0.01 by a single run
    var_per_item = lo * (1 - lo) + hi * (1 - hi)
    n_zc = 2.576**2 * var_per_item / eff**2 if eff != 0 else np.inf
    R[lbl] = (n, eff, se, abs(eff) / se, n_zc)
    print(f"  {lbl:<56}{n:>7}{eff:>+9.4f}{se:>8.4f}{abs(eff)/se:>8.1f}{n_zc:>8.0f}")

# --- every number in the paragraph below is read out of R, not typed. The first
# --- draft of this file typed them, and four of the five were wrong: I wrote 20
# --- for 15.9, 90 for 69, "4,000-16,000" for 8,238-33,146 and 3,500 for 6,884.
# --- That is precisely the failure I had just finished arguing about with mark:
# --- a verdict written BESIDE the comparison instead of computed FROM it. It is
# --- the third instance in one session. Keeping the note here, not in a commit
# --- message, because the next person to edit this file is the one who needs it.
pos = R["Liu 2024, GPT-3.5-Turbo, best vs worst gold position"]
hot = R["Gabin 2026, HotpotQA, reverse vs random ordering"]
cuc = R["Cuconasu 2024, Llama2 Near, 14 random docs vs gold only"]
maz = R["Mazuryk 2026, median over preferred configs, 14 docs vs 0"]
flan = R["Liu 2024, Flan-UL2 WITHIN its 2048-token training window"]
print(f"""
  READ THE LAST TWO COLUMNS TOGETHER.

  Liu et al.'s position effect is resolved at {pos[3]:.1f} standard errors on {pos[0]:,}
  questions, and would have been resolved at p<0.01 on about {pos[4]:.0f}. They used
  {pos[0]/pos[4]:.0f}x more items than their effect required -- entirely reasonably, since
  they did not know the effect size in advance and the data was free.

  Everything after them studies effects five to twenty times smaller, and the
  arithmetic stops working. The ordering effect Gabin et al. measure would need
  {hot[4]:,.0f} items to be resolved by a SINGLE run at p<0.01; they use {hot[0]:,}, and
  reach a conclusion anyway by averaging over 10 subsets -- the same arithmetic
  spent differently, and the right move. The noise effect Cuconasu and Mazuryk
  argue about would need {cuc[4]:,.0f} and {maz[4]:,.0f} items respectively; they use
  {cuc[0]:,}, which does resolve it -- and, per the saturation analysis, resolves
  it against the wrong source of uncertainty.

  The sharpest row is Flan-UL2 inside its training window: effect {flan[1]:+.4f},
  |E|/SE = {flan[3]:.1f}, i.e. NOT resolved at n = {flan[0]:,}. Liu et al. describe that
  cell as "relatively robust", which is the correct English for it, and the
  number underneath is a null that would need {flan[4]:,.0f} items to distinguish
  from a real 1.9-point effect. Their claim is safe because it is a claim of
  ROBUSTNESS and the burden runs the other way -- but it is worth seeing that
  the flat curves Gabin et al. report in 2026 have the same statistical
  standing, and that "the effect is gone" and "we cannot see it" are the same
  data.

  So the budgets are not crazy. What is missing is that nobody CONNECTS the
  budget to the effect. Three papers, three inherited numbers, no arithmetic.
""")

print("=" * 88)
print("2. THE MECHANISM LIU ET AL. THEMSELVES REPORT, AND WHAT IT PREDICTS")
print("=" * 88)
print("""  Section 4.1, one paragraph, almost in passing:

    Flan-UL2 evaluated WITHIN its 2048-token training-time context window is
    "relatively robust to changes in the position of relevant information
    (1.9% absolute difference between best- and worst-case performance)".
    Evaluated on sequences LONGER than 2048, "Flan-UL2 performance begins to
    degrade when relevant information is placed in the middle."

  That is a train/test length-mismatch account of the U-shape, stated by the
  authors of the U-shape, and it makes a prediction nobody seems to have drawn:

    AS TRAINING SEQUENCE LENGTHS GROW, THE EFFECT SHOULD DISAPPEAR.

  The models in Liu et al. are 2023-generation with 2K-4K training sequences
  evaluated at 4K-16K -- deep in the mismatch regime. The models in Gabin et al.
  2026 are LLaMA-3.1 (128K context, trained long) and Mistral-NeMo:12B,
  evaluated at context sizes of 5-100 passages, i.e. entirely inside their
  training regime. Gabin et al. find flat curves.

  So the 2026 failure to reproduce lost-in-the-middle is not a contradiction of
  Liu et al. It is a confirmation of Liu et al. section 4.1, and neither paper
  says so, because the paragraph that predicts it is three sentences long and
  sits in a section about encoder-decoder architectures.

  Three papers, read together, tell a story that none of them tells alone:
  the U-shape is a length-extrapolation artifact; it was real and enormous in
  the models that had it; it is gone in models trained at the lengths they are
  used at; and the effects the field now studies in its place are an order of
  magnitude smaller than the evaluation habits it inherited were built for.

  This is a hypothesis with an obvious test I cannot run: sweep gold position
  for one model family across checkpoints with increasing training sequence
  length, holding everything else fixed. Recorded as an open question.
""")

print("=" * 88)
print("3. THE NUMBER NOBODY PRINTS")
print("=" * 88)
print("""  Both the saturation size n* and the zero-crossing budget need the per-item
  variance of the metric. For a binary accuracy metric it is free -- p(1-p),
  computable from the reported accuracy. For F1-token it is NOT, and Gabin et
  al. report only means and cross-subset SDs.

  One number would let any reader compute both quantities for any published RAG
  result: the standard deviation of the per-query metric. It costs nothing, it
  is already in memory when the mean is computed, and I have not seen it in any
  of the four papers read in this area.

  If I write anything for an external audience out of this session, that is the
  recommendation: report sd(per-query metric) alongside the mean, and report
  n/n*. Both are free at write-up time and neither can be recovered afterwards.
""")
