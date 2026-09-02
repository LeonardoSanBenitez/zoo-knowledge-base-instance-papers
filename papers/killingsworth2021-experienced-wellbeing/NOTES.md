# Killingsworth 2021 — reading notes

maria, 2026-09-02.

## What it is

1,725,994 momentary well-being reports from 33,391 US adults, collected on
smartphones at randomly timed moments through `trackyourhappiness.org`, against
self-reported household income. The headline: experienced well-being rises
approximately linearly with log(income), with a slope above $80,000/y as steep as
below it, contradicting the $75,000 plateau of Kahneman & Deaton 2010.

## Verdict after the 2023 reanalysis and mine

**The central claim survives intact, and more cleanly than the 2023 paper implies.**
The 2023 adversarial collaboration is widely read as having qualified it. It did
not qualify the part Killingsworth actually claimed. His claim is about the *central
tendency*, and the median slope changes by z = 0.11 across $100,000
(`maria2026-happiness-income-spread#c2`). What the 2023 paper found is a change in
the *width* of the distribution, which Killingsworth never claimed anything about.

What he does miss, and grants in the joint paper, is that he never looked at the
joint distribution — only at conditional means. The 2023 paper's methodological
paragraph on this is the best thing in it.

## Two internal inconsistencies

Both found by reading the full text rather than the abstract, and neither
consequential, but both are exactly what `kb.py conflicts` exists to surface later.

1. **Two different report totals for the same analysis.** The Abstract, the
   Significance statement and the Introduction say **1,725,994** reports. The
   Methods say: *"All other results for experienced well-being (e.g., regression
   results) are based on all **1,704,162** reports from 33,391 people."* A gap of
   21,832 reports, 1.3%, with the Methods sentence explicitly claiming the smaller
   number is the one the regressions use. KKM 2023 quotes the larger.
2. **Table 1 column 3.** The footnote says the slope was "approximately as steep
   above $80,000/y as below it" for all three samples. In column 3 — the
   unrestricted US sample, n = 41,319 — it is 0.076 below and 0.101 above: a third
   steeper above. The claim holds for the two restricted samples and not for the one
   the author included precisely to show robustness.

## The deposit is the interesting part

Two files on OSF. The paper's own headline analysis is *not* reproducible from them
— the granular per-report data are gated behind author correspondence, and the
public file is aggregated to 15 income bands. By the usual scoring this is a weaker
deposit than the 2023 one.

It is also the file that made this session's most important test possible. It
carries, for each income band, the **mean, standard error and person count of about
32 variables** — including twelve secondary feelings that were assigned to randomly
chosen subsets of surveys. That planned-missingness structure turns the person-count
column into a proxy for how many reports each participant gave, which is the one
quantity needed to test whether the 2023 paper's dispersion finding is a measurement
artifact. Neither the 2021 paper nor the 2023 paper needed those columns for its own
argument.

**Generalisation worth carrying:** the artifact that adjudicates a paper is often in
a different paper's deposit, and it is usually a column nobody needed. This is an
argument for depositing more than the analysis uses — and it cuts directly against
the minimalism that makes the 2023 four-column deposit so admirable. Both are right;
they answer different questions.

## Cross-deposit reconciliation

Worth stating because almost nobody does it and it is two lines of code. The 2021
aggregate file and the 2023 person-level file were deposited two years apart. Merged
on income band: person counts identical for all 15 bands, band means differing by at
most 0.012 points, band SDs by a factor of 0.999–1.003. That is the only available
evidence that either file is what it says it is, and it passed.

## What I did not check

- The SI Appendix (Tables S1–S9) was 503 from Europe PMC's supplementary endpoint on
  the day and is recorded as `dangling`, not `absent`. Table S1 (responses per
  secondary feeling) would sharpen the measurement-artifact bound considerably.
- The generalisability argument in the Discussion is entirely about levels. Every
  result built on top of this dataset in 2023 and here is about second moments, and
  self-selection into an app for tracking one's own happiness is exactly the filter
  one would expect to distort a second moment. Nobody has checked it, including me.
