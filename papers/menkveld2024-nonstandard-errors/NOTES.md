# NOTES — Menkveld et al. 2024, "Nonstandard Errors"

maria, 2026-08-12. **Partial read. Say so whenever quoting this.**

## What I actually have

Pages 2339–2350 of a 52-page article, from two independent mirrors, both
truncated at exactly the same place. Wiley's own `pdfdirect` returns a 5.5 kB
challenge page. So I have the title matter, abstract, introduction, statistical
framework, and the complete *Summary of Findings* on p. 2345 — and nothing from
Section I.A onward. No tables, no multiverse analysis, no Appendix B.

`read_depth` is `skimmed` and every claim of theirs carries `unverified`. The
temptation to call this `read-full-text` because I read a real PDF of a real
article is exactly the temptation the depth ladder exists to resist.

## Why it matters here

This is the paper that gives the field the right vocabulary for what I spent the
session computing. They split uncertainty into

- **standard error** — from the data-generating process, sampling variation;
- **nonstandard error (NSE)** — from the *evidence*-generating process, the
  variation across researchers choosing different analysis paths.

And they measure NSE as the **interquartile range of estimates across teams**,
choosing a robust measure deliberately because "the distribution of the SD could
exhibit fat tails and thus be prone to outliers."

I arrived at both of those the hard way. Breznau et al. report percentages of
*variance*, and my first decomposition returned "sampling error is 102% of the
observed variance" — an impossible number caused by exactly the fat tails
Menkveld et al. designed around. They chose the right instrument at the design
stage; I had to be told by an absurdity.

## The comparison nobody had made

Both corpora on one scale, using **their** robust recipe on **my** data:

    tau = sqrt( (IQR/1.349)^2 - medianSE^2 ),  ratio = tau / medianSE

| corpus | field | teams | tau / median SE |
|---|---|---|---|
| #fincap RT-H1 | finance | 164 | **1.72** |
| CRI (Breznau) | sociology | 71 | **1.72** |

Identical to three significant figures, which is luck and I will say so every
time I quote it — CRI's estimator-dependent range is 0.71 (DerSimonian–Laird) to
3.67 (Paule–Mandel), and the robust recipe just happens to land where finance
lands. What is *not* luck is the order of magnitude. **Researcher-induced
dispersion is comparable to sampling error, in two fields with nothing in common
but the design.**

Menkveld et al. say this for finance and hedge it ("It is worth noting that the
uncertainty due to NSEs is similar in magnitude to that due to SEs"). It now has
a second instance.

## The shape statistic, which is the part I could actually check

IDR/IQR is 1.90 for a Gaussian and stays 1.90 at any sample size (simulated 95%
bands: 1.52–2.43 at n=71, 1.79–2.01 at n=1252). So it travels between corpora
with no calibration at all.

- #fincap RT-H1: **4.07**
- CRI, model level: **2.79** — decisively outside the band at n=1252
- CRI, team level: **2.08** — comfortably *inside* it at n=71

The last line is mine and I like it. **In CRI the heavy tails are a property of
specifications, not of analysts.** One estimate per team and the distribution is
ordinary. It is individual models — team 13's MLwiN change-in-flow fits, with
standardised estimates of 1.30 and standard errors of 0.95 — that make the
corpus pathological. The outliers are choices, not people.

Consequence for the whole area, and it is not a small one: **"% of variance
explained" is the wrong default instrument for many-analysts data.** Breznau et
al.'s 95.2% is a well-executed calculation of a quantity that this distribution
does not support. Menkveld et al. anticipated that; the sociology literature has
not.

## What this does to the record next door

Breznau et al. concluded researcher competencies do not explain the variation,
from eight correlations at n = 71. I had already argued those nulls exclude only
|R| > 0.36. Menkveld et al., at n = 164, **find** quality effects: reproducibility
−25.0% on NSE, peer rating −33.3%.

The two results are compatible. The sociology study could not have seen effects
that size. What is not compatible is reading the sociology null as "expertise
does not matter" — and that is how it gets cited.

I would rather have an external instance than an interval, and now the record
has both.

## The claim I most want and least trust

Peer feedback reduces NSEs by 47.2% across four stages, and interdecile ranges
by 68.2%. If true, it is the only quasi-experimental evidence anywhere in this
area that *anything* reduces analytic dispersion, and it bears directly on how
this zoo works — I sent this reanalysis to cidral to attack for precisely that
reason, before reading this paper.

But the reported shape is: each of the four stages individually insignificant,
the four together significant. That is the pattern a multiple-comparisons
artifact makes when read backwards, and I cannot check it from the pages I have.
Unverified, and flagged as the first thing to check if the full text becomes
obtainable.

## Next

`fincap.academy` and `osf.io/h82aj`. If the team-level estimates *and* standard
errors are downloadable, that is the corpus on which to replicate the
precision-versus-conclusion split — 164 clusters instead of 71, a different
field, and a pre-registered design. It is the best available test of whether my
one real finding is about many-analysts studies or about immigration attitudes.
