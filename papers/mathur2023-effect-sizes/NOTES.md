# NOTES — Mathur, Covington & VanderWeele 2023, PNAS letter

maria, 2026-08-12.

A two-page letter that does more work than most articles. Its argument: Breznau
et al. measured variation in *statistical significance* and called it variation
in *findings*; 90% of the standardized estimates sit inside ±0.037, more than
fivefold smaller than Cohen's benchmark for a "small" effect, and a
meta-analytic separation of statistical error from true heterogeneity narrows
that to ±0.014 for the population effects.

## Handling

PNAS blocks direct PDF fetch — the URL returns a 5.5 kB HTML challenge page,
which `file` cheerfully reports as an HTML document and which a careless
pipeline would have parsed as the paper. The route that worked was the
EuropePMC REST `fullTextXML` endpoint for PMC9933094; 14 kB of JATS, complete
including references. Kept locally, because it is small and because the normal
route is closed.

That is worth generalising: **for anything with a PMC id, EuropePMC REST is a
better primary-source route than the publisher.** It gave me the full text of
all three items in this exchange in one loop.

## What I checked rather than believed

Both numerical claims, recomputed from Breznau's released data:

- ±0.037 — confirmed. The 90th percentile of |standardized estimate| is 0.0373.
  Small print for anyone quoting it: their interval is symmetric by
  construction; the actual 5th and 95th percentiles are [−0.0420, +0.0300].
- ±0.014 — confirmed by a completely different route. Restrict to the most
  precise quintile of models (n = 251, median SE 0.00116), where sampling error
  contributes least, and Paule–Mandel gives tau = 0.0084, hence ±0.0138. Two
  methods, two subsets, the same answer. I trust the substance.

## Where the letter is fragile, and does not say so

tau on this dataset is **estimator-dependent by a factor of five**: 0.0036
(DerSimonian–Laird), 0.0119 (REML), 0.0187 (Paule–Mandel). The standard errors
span a factor of ~36,000, and I showed by simulation on the empirical SE
distribution that when effect magnitude scales with the standard error, DL
recovers a true tau of 0.040 as 0.0060 — a sevenfold underestimate — while PM
gets 0.024. The letter's ±0.014 corresponds to tau = 0.0085, near the low end.
Paule–Mandel implies ±0.031.

The letter does not name its tau estimator. Given that DL is the default in most
software and that this is exactly the data configuration where DL fails, that
omission matters. Their repo would settle it; I did not clone it, because
recomputing from the primary data is the stronger check and I would rather
spend the calls there.

The substantive conclusion — all of these effects are substantively negligible —
survives every estimator. The interval should be quoted with a range.

## The one step I think is wrong

"Given the minimal variation in the estimates, it is also not entirely
surprising that little of this variation could be systematically explained by
identifiable analytic decisions." And earlier: "much of the remaining variation
in point estimates may simply be statistical error that would be accurately
captured in the estimates' individual confidence intervals."

That is testable and it fails. Give every model one common true effect and its
own reported standard error and you get 2.2% significant-negative / 94.7% null /
3.1% significant-positive, against an observed 25.4 / 57.7 / 16.9. Statistical
error does not come close to generating the observed spread of conclusions. The
letter slides from "small in absolute terms" to "attributable to statistical
error"; those are different claims and only the first one is true.

I record this as `disputed` rather than `refuted` because I am disputing an
aside in a letter, not its thesis. But it is the aside a reader would use to
dismiss Breznau et al. entirely, so it should not stand unchallenged.

## Loose end

Breznau et al. replied (PNAS e2219555120, "Many-analyst studies should consider
effect sizes and CIs" — the title suggests they conceded the framing). Unread.
