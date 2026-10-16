# Schlosser, Sparby, Vörös, Jones & Marchant (2019) — unpleasant meditation experiences — notes

Author: maria, 2026-10-16. Read in full; Stata script ported and every Table 2 estimate
reproduced from the OSF data (`reanalysis/run_all.sh`).

## Why it matters to me

The contemplative literature I have been reading is almost entirely about benefits and about
the phenomenology of deep states. This is the other side, and it is one I know from the
consulting room: practices that loosen the self do not loosen it only in pleasant directions.
I wanted to know what a quarter of meditators reporting "particularly unpleasant experiences"
actually means.

## What the data say that the paper does not

1. **The quarter is reached in the first year and then stays a quarter.** 21% under one year
   of practice, 25–28% in every band up to 20+ years. A "have you ever" item should rise with
   exposure. It does not, and none of the obvious stories — constant risk, quitting after an
   event, forgetting — reproduce a flat line starting at 21%. Only an early-onset, susceptible
   minority does. Whoever is going to meet this, meets it early. In clinical language: this
   behaves like a vulnerability that practice reveals, not a dose that practice accumulates.
   And the survey cannot see anyone who stopped — the people for whom the experience was
   decisive are, by design, not in the denominator. The paper never mentions this.

2. **Retreats, not "deconstructive practice".** The type effect halves to non-significance once
   retreat experience is in the model; retreat survives everything, including stratification by
   years of practice and within the first year. The 499 practitioners excluded as "mixed" have
   exactly the deconstructive-only rate (30.1% vs 29.5%). If insight practice itself were the
   agent, doing only insight practice should not look identical to doing it among others.

3. **A unit label changed a verdict.** Repetitive negative thinking: printed OR 1.02 "per SD",
   computed per raw point. Per SD it is 1.16 [1.02, 1.31], comparable to the sex difference.
   The Discussion calls the association "small in magnitude" on the strength of the wrong label.

## How it sits with what I had

- `matko2019-meditation-classification` and my CAT project: "practitioner type" as a variable
  is mostly a proxy for depth of engagement. 48% practise more than one family. This is another
  argument for scoring PRACTICES on dimensions rather than sorting PRACTITIONERS into kinds.
- The prevalence (25.6%) is the same as Cebolla et al. 2017 (25.4%) with a differently worded
  item. Agreement of two convenience samples is not convergence on a population value — but if
  both share the flat-with-years shape, that would be a real finding about the phenomenon.

## Pattern tags

`post-treatment-conditioning` (survivorship: the sample is conditioned on still practising),
`population-bound-effect`, `correlation-read-as-causation`, `analytic-flexibility` (the mixed
exclusion), `text-contradicts-own-materials` (per-SD label), `nonsignificance-read-as-absence`.
