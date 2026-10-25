# Walasek & Brown (2015), *Income Inequality and Status Seeking* — notes (ABSTRACT-ONLY, provisional)

Author: maria, 2026-10-25. **I could not reach the full text.**
- It is not open access.
- WRAP Warwick has the record without the file.
- SAGE returns a Cloudflare wall.
- The Wayback copies of the SAGE pages are paywall wrappers.
- No author copy was found on the lab pages.
What I read: the PubMed abstract, and the authors' own two-page reproduction instructions on OSF
(`LW&GDAB_Methods.pdf`, component tkfxd). The deposit was examined in full. Until a full text is read,
every assessment below stays `unverified` (the schema's honesty rule), and I told mark (2026-10-25).

## Why this paper

Item 5 of 8 in mark's blinded known-answer control. No prior knowledge and no search for third-party checks.

## What the abstract claims

The design:
1. Regress state Gini on income and three controls.
2. Enter the residuals into Google Correlate.
3. Have MTurk raters classify the 40 most positively and the 40 most negatively correlated search terms.
Result: more than 70% of the positive terms are status goods, against 0% of the negative terms. Residual-based
analysis is offered as a method "avoiding confounds and high risks of spurious correlations".

## What the deposit lets me check

- **The residuals reproduce exactly** from the deposited census controls: max |diff| 0.000005. Population
  enters raw, not logged; with log population the residuals change (r = .93).
- **"> 70% vs 0%" reproduces** under a majority rule, p(yes) > .5 out of yes + no with 60 raters per term:
  29/40 = 72.5% against 0/40. The share falls with stricter thresholds (55% at .70, 45% at .80). The
  negative side stays at 0, because no negative term exceeds .40.
- **The 40 positive terms are not 40 observations.** Of the 29 status-classified terms, 6 are Ralph Lauren
  queries, 8 are David Yurman queries and 3 are loafer queries. Twelve stand outside these families. The
  negative list has its own duplicates (pinatubo ×2, viking sewing ×2, moist chicken / super moist).
- **The residual is regional.** The four Census regions explain 40% of residual inequality (p < .0001).
  The top states are CT, LA, NY, MA, MS, AL, TN and RI: Northeast and Deep South. The status terms are
  largely a preppy regional idiom: Ralph Lauren, Vineyard Vines, seersucker, Bass and penny loafers,
  Johnston & Murphy, St Thomas Ritz, Little Dix Bay. The negative terms are gaming, PC hardware and home
  cooking (Diablo, Blizzard, Radeon 7950, lemon bars). The controls cover income, population, urban share and
  foreign-born share, not region or culture. So the design cannot separate "inequality motivates status
  seeking" from "the regions that happen to be unequal share a consumer culture".
- **The term discovery cannot be re-run.** Google shut Google Correlate down in 2019. The authors' own
  instructions warn that results "may differ ... due to the constantly updated Google Correlate database",
  even before the shutdown.

## What I could not check without the paper

Whether raters were blind to the list a term came from. How the paper reports the comparison (a test?
a threshold?). Whether region was considered. Any robustness analysis.

## For the known-answer control (provisional, abstract-only)

Checked-type: the deposited residuals and the abstract's headline proportions **reproduce**. The pipeline
step between them is irreproducible by construction, because the service is defunct. Unchecked-type: the
abstract's "avoiding confounds" over-claims. Regional culture is an uncontrolled alternative explaining
much of the residual, and the counts are inflated by query families. Strength of checked-type defects,
on what I could see: none. Not a full read.
