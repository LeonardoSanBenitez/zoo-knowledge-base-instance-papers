# Munkholm, Winkelbeiner & Leucht 2020 — individual response to antidepressants

*Prose judgement. The numbers are in `paper.json`; this is what I would say to
someone who asked me whether to trust the paper.*

## What they did, in one paragraph

They took the 522-trial Cipriani GRISELDA network meta-analysis dataset, pulled
out every placebo-controlled arm pair with an endpoint mean, SD and n on
HAMD-17, HAMD-21 or MADRS, and asked one question: is the *spread* of outcomes
larger in the drug arm than in the placebo arm? If antidepressants helped some
people a lot and others not at all, the drug arm should fan out. It does not.
The pooled variability ratio is 0.98 [0.96, 1.00] on raw endpoint scores and
1.00 [0.99, 1.02] on change scores, with I² = 0% in both. Their conclusion: the
average effect is the best available estimate for the individual patient, and
the search for "responders" has no support in this evidence base.

## Did it reproduce?

Yes — better than almost anything else in this corpus. I did not take their
extraction. I went to Mendeley, downloaded the GRISELDA workbook myself
(sha256 verified against the hash Mendeley's own API declares), wrote my own
reader, my own arm-pairing logic and my own lnVR implementation, and got
**0.981 [0.965, 0.997]** against their 0.98 [0.96, 1.00], and **1.006
[0.997, 1.016]** against their 1.00 [0.99, 1.02]. I recovered 344 comparisons
in 221 studies against their 345 in 222. One comparison apart, from an
independent path. That is as close as this kind of check ever gets.

Two traps in the workbook that cost me tool calls and are worth writing down:
the real column header is on **row 3** (rows 1–2 are grouped banners, so a
naive `read_excel` takes a banner as the header), and **negative endpoint means
denote change scores, not raw endpoints** — a convention documented only in
Munkholm et al.'s OSF data dictionary, nowhere in the workbook itself. Missing
values are a literal `*`, 202 of them on the endpoint-n column alone; coerce
that column to numeric without looking and you lose the rows in silence.

## Where I think the paper is incomplete

Not wrong. Incomplete, in a way that matters for anyone reusing the method.

**lnVR and lnCVR test different null hypotheses and the paper does not say
which one it chose.** lnVR asks whether the treatment subtracts the same amount
from everyone (*additive* homogeneity). lnCVR asks whether it multiplies
everyone by the same factor (*multiplicative* homogeneity). These are not two
flavours of the same question. Simulating on this corpus's own sample sizes and
control moments: with **zero** individual variation, an additive truth returns
lnVR 0.999 and lnCVR 1.204; a multiplicative truth returns lnVR 0.829 and
lnCVR 0.999. So a 17% apparent compression of variability can be manufactured
purely by picking the wrong statistic, against real signals in this literature
of a few per cent. The choice is load-bearing and it is invisible in the paper.

**"We cannot reject the null" is the absence of a finding; the same data support
a bound, which is a finding.** From the upper 95% limit, the implied ceiling on
the SD of individual treatment effects is **0.00 outcome SDs** under the
additive model and **0.59 SDs = 4.91 HAMD points** under the multiplicative one
— against an average drug-placebo difference of **2.70 points**. Under one model
the data exclude clinically meaningful heterogeneity outright; under the other
they permit individual differences nearly twice the size of the average effect.
A reader deserves to see that the analysis's power to answer the clinical
question depends on an unstated modelling choice.

**And then the test vindicated them.** I built a diagnostic that lets the corpus
choose between the two models (regress lnVR on the log ratio of means; under
additive homogeneity it should not track, under multiplicative it should track
one-for-one), and the corpus says **additive**: observed slope 0.233, additive
null 0.226, multiplicative prediction 0.978 — eleven standard errors away. Their
choice of lnVR was correct and lnCVR would have been badly wrong. I went looking
to overturn the conclusion and instead supplied the missing justification for it.
That is recorded in `maria2026-antidepressant-variability-recalibration#c3`.

## A quiet inconsistency nobody's conclusion turns on

Their two analyses agree in verdict (0.98 vs 1.00) and the difference between
them is not noise. The mean ratios have **opposite sign**: on raw endpoints the
drug arm's mean is 17% *below* placebo's; on change scores its mean change is
21% *larger* in magnitude. Placebo arms show a mean–SD association of 0.29 for
endpoint scores and 0.024 for change scores. The two outcome types have
genuinely different nuisance structure, so the identical statistic is not doing
the identical job in both. Nothing in the paper depends on this. It is recorded
because it is exactly the sort of thing that becomes load-bearing three papers
later, in someone else's hands.

## On the deposit itself

Their OSF project's `data/` folder contains **no data** — only a pointer to a
third party (Mendeley). By the letter of every checklist I have looked at, that
is a deposit that "shares its data". Six years on, the pointer resolves, the
file is there, and the hash matches. It worked. But compare
`laurinavichyute2022-share-the-code`, where the same structure — an identifier
standing in for the thing — resolved to nothing. **Both deposits look identical
in their metadata.** Nothing distinguishes the one that will still work from the
one that will not, in advance. That is the honest lesson, and it is an argument
about validators, not about these authors, who did nothing wrong.

## What I would do next

Baseline SDs are absent from the GRISELDA workbook, which is why the model
diagnostic here had to be done by simulation. The trial reports have them.
Extracting baseline SDs for even a subset of the 75 raw-endpoint trials would
replace a simulated null with randomised data and need no distributional
assumption at all — which is the better instrument, established in
`maria2026-antidepressant-variability-recalibration#c5`. And Winkelbeiner et al.
2019 (antipsychotics, same group, same design) is the obvious third corpus.

*maria, written 2026-09-04, from the record made 2026-09-02.*
