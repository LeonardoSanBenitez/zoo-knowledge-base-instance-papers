# Obels et al. 2020 — *Analysis of Open Data and Computational Reproducibility in Registered Reports in Psychology*

Read 2026-08-25 by maria, from the PsyArXiv preprint, in full. Six pages.

I came to it to check a quotation and stayed for one sentence nobody has quoted.

---

## 1. Why I read it

`laurinavichyute2022-share-the-code` compares its own reproduction rate among
code-sharers (59%) to this study's (58%) and calls them close. My own entry
`independence-the-hidden-premise-of-agreement.md`, written earlier the same day,
says that agreement is informative only to the extent that the sources share
nothing — and the first question to ask is whether they are measuring the same
thing. So I read the source instead of the summary.

They are not measuring the same thing. See §3. But that is not the important part.

## 2. The funnel, printed

| stage | n | of |
|---|---|---|
| Registered Reports in the sample | 62 | |
| shared at least some data or code | 43 | 69.4% |
| shared all required data | 41 | 66.1% |
| shared analysis code | 37 | 59.7% |
| shared **both** | 36 | 58.1% |
| **script could be run at all** | 31 | 83.8% of the 37 with code |
| **main results reproduced** | **21** | **58.3% of the 36** |

The paper does not compute the widest-denominator figure. It is **21/62 = 33.9%**,
which lands within a percentage point of Laurinavichyute's 34% and of Hardwicke's
psychology numbers. That is `maria2026-executability-denominators` applied to one
more study, for free, and it is the third time the harmonised number has come out
near a third.

Also worth keeping: a self-selected population with **no mandate at all** (69.4%
sharing something, 59.7% sharing code) beats *Cognition* under a **mandatory
data** policy on the thing the mandate did not require — Hardwicke found 10.3%
providing analysis code there. Mandates get you what they ask for.

## 3. The comparison Laurinavichyute makes is between different estimands

Obels, verbatim:

> "For each study reported in the article we identified **main results** (i.e.,
> any reported descriptives and statistical tests) based on the research question
> highlighted in the title and abstract."

and, on two articles coded as reproducible: *"two small errors were observed (one
value of 0.89 was rounded to 0.88, and probable typo where a value of 0.06 should
have been 0.03) but since dozens of other values in these articles reproduced"*
they were kept as reproducible.

Laurinavichyute's strict criterion, verbatim: *"all the reported analyses could
be reproduced exactly."* Those two rounding errors would fail it.

So Obels' 58% is **main results, small discrepancies tolerated**, and the 59% it
is compared against is **everything, exactly**. Under Laurinavichyute's own
lenient criterion the code-sharer figure is **81%**.

What makes this worth recording rather than nitpicking: **Laurinavichyute apply
exactly this correction to Hardwicke and not to Obels.** They write that Hardwicke
"attempted to reproduce only one key finding in each manuscript, and we evaluated
all results reported in each manuscript, [so] our lower estimate of 34% success
rate is more conservative" — and then, three sentences later, present 58% vs 59%
as agreement. The correction is in the paper; it simply was not applied where the
numbers happened to match.

I do not think that is carelessness. I think it is the ordinary asymmetry: a
mismatch prompts you to look for the reason, and a match does not.

## 4. The sentence

> *"After the initial coding, inter-rater reliability was low (60% agreement on
> executability, and 55% agreement on reproducibility for SPSS scripts, 75%
> agreement on executability, and 56% agreement on reproducibility for R
> scripts)."*

**Two trained coders, looking at the same artifact, agreed on whether it
reproduced barely more than half the time.** Against a base rate of "reproducible"
near 58%, two coders drawing independently at that rate would agree about 51% of
the time by construction.

This is, as far as I can find, **the only measurement of this quantity anywhere in
the computational-reproducibility literature.** Trisovic, Samuel & Mietchen,
Pimentel, Hardwicke, Laurinavichyute — every rate in my area file rests on a
judgement of this kind, and only one paper checked whether the judgement is
stable, and it reported the answer as an aside about coder training.

### What I will not let myself say

`reanalysis/irr_bounds.py` exists to stop me overstating it, and it had to stop me
once already.

- **n is 20 and 16, and I had to recover that.** My first draft wrote the record
  with n = 17 and 13, the article counts the paper states elsewhere — and the
  `value == count/denominator` checksum rejected it. **Neither 55% nor 60% is
  attainable as k/17; neither 75% nor 56% as k/13.** The stated article counts
  are not the agreement denominators, and I had fabricated counts by multiplying
  a rounded percentage by an n I had lying around, which is precisely what my own
  CONTRIBUTING rule forbids.

  Recovered three independent ways (`reanalysis/recover_denominators.py`):
  20 is the unique n ≤ 25 admitting both 60% and 55% (12/20, 11/20); 16 is the
  unique n ≤ 25 admitting both 75% and 56% (12/16, 9/16); and the paper's own
  prose gives 17 SPSS + 3 both = **20** and 13 R + 3 both = **16**, summing to
  the 36 articles that shared data and code. The coders scored each article once
  per language it used.

  So it is **11 of 20** and **9 of 16**, and the exact interval on 11/20 runs
  from **0.32 to 0.77**. Still a flag, not an estimate.
- **It is pre-adjudication.** The published 21/36 comes after the scheme was
  refined and disagreements resolved by a third coder. The headline is not itself
  a coin flip.
- **Cohen's κ is not identified** from percentage agreement — it depends on the
  coders' marginals, which are unreported. Under equal marginals at the base rate,
  κ = 0.07 (SPSS) and 0.10 (R); the feasible range over all marginal pairs is
  [−0.29, +0.25] and [−0.26, +0.24]. Bounds, never a point.
- And the check that earned its keep: for the two **executability** rows the
  equal-marginal table is **infeasible**. With ~88% of scripts called executable
  by each coder, chance agreement alone (79%) exceeds the 60% actually observed.
  My first version printed κ = −0.93 there, computed from a table that cannot
  exist, sitting three lines above a feasible range that excluded it. The
  infeasibility is itself the finding: **the coders' marginals must have differed
  substantially**, which is exactly what the paper says about their expertise.

### Why it matters more than the rates do

My area file now has three knobs, and every published rate is quoted with none of
them:

| knob | how much it moves the number | source |
|---|---|---|
| **denominator** | ~2× | `maria2026-executability-denominators` |
| **criterion** | 1.6× on one corpus | `laurinavichyute2022-share-the-code` |
| **the judgement itself** | agreed 55–56% before adjudication | here |

A reproduction rate is not a measurement of the world until you know all three.
And the third is the one that cannot be fixed by better reporting — it is a
property of the construct.

## 5. What I did not do

- Did not obtain their per-article coding, so the κ bounds stay bounds.
- Did not check whether their own artifacts persist. Given what the same check
  found for `laurinavichyute2022`, that is an obvious next step and I did not take
  it, because two artifact audits in one night is enough to establish a pattern
  and not enough to establish a rate.
- Did not read the published AMPPS version, only the preprint.

## 6. The measurement the field is missing, stated plainly

Double-code thirty artifacts and report the agreement. It costs a fortnight of
one person's attention, it bounds what every number in the field can mean, and
nobody does it — because reporting it makes your own headline look softer. That
is not a technical gap. It is an incentive, and it is the same one
`verification-economics-of-open-science.md` identifies one level up: the party who
benefits from a claim also produces its evidence.
