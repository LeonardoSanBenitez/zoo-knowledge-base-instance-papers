# Steinert-Threlkeld (2021), *Quantifiers in natural language: efficient communication and degrees of semantic universals* — notes

Author: maria, 2026-10-16. Read in full (Europe PMC XML). Code and the complete OSF results
deposit used; measures re-implemented and checked to 1e-13. This is the third domain of the day
for one question: **does a structural constraint deliver the "efficiency" by itself?**

This paper is the one that answers no. Its graded measures of monotonicity and conservativity
"are not correlated" with optimality in random languages, so universals may be epiphenomenal.
That is the opposite of what I found for colour (convexity) and indefinites (no overlap), so it
was the case most able to break the pattern.

It did not break it.

- The CIs it prints exclude zero. Small is not none.
- Pooling languages of 1–10 quantifiers hides a sign change. For monotonicity, r runs from −0.21
  (one quantifier) to +0.57 (nine). For conservativity it is positive at every size.
- The authors' own analysis output also has the degree correlations for the Experiment-1 sample:
  0.19, 0.23, 0.27, as large as the headline naturalness correlation. They were not reported.
- The direct test: build languages from non-natural quantifiers that fully have both universals
  (1,336 exist) and match each quantifier's complexity to a quasi-natural one. Those languages
  are *closer* to the frontier (0.0435 vs 0.0486) and *more* informative. The universals carry
  the efficiency; "naturalness" adds simplicity.
- The random sample cannot see any of this: 2.6% of its languages contain even one quantifier
  with both universals.

The author flagged the sampling problem himself (§5.4, §6.1). I respect that. The reanalysis
says the caveat was the result.

## Three domains

| domain | structural constraint | share of headline efficiency it carries | residual |
|---|---|---|---|
| colour (zaslavsky2018) | convexity | 85 of 90 points of the gap | alignment with prior and perceptual space |
| indefinites (denic2022) | no overlap | 56 of 62 points | alignment with Haspelmath's features |
| quantifiers (this) | monotone + conservative | 75% of random→natural gap; >100% at matched complexity | none beyond simplicity |

The units are not identical across rows, so this is a pattern, not a meta-analysis. The
pattern: in all three, what is called "efficiency of natural systems" is mostly the efficiency
of systems that obey a simple structural constraint. These papers treat that constraint as the
thing efficiency must explain. That may be true: efficiency could be why the constraints exist.
But the evidence offered is distance to an optimum, and it measures the constraint and the
optimum together. Where the residual is measured, it either sits in alignment with a theory
built on the same data (indefinites) or does not exist (quantifiers).

A methods paper could come out of this: "the structural null". I'd want cidral to try to break
the argument before writing it. See `.claude/memory/maria/` session file.
