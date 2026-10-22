# vandam2024 — IME psychometrics — notes

Author: maria, 2026-10-23. Authors' manuscript (10 May 2024) read in full from osf.io/76ud3. The data are
the vandam2025 deposit, already verified that night. Opened as a chain from vandam2025. The prior I
wrote down came from gamma2021-mpe92m: factor counts of meditative-experience inventories may be
resolution choices.

## The prior failed, and that is the first finding

The three factors are real in the sense that matters. They replicate across random halves of the
sample. The weakest factor's Tucker φ is .955 on all 103 items, the level the Big Five reach in the
same pipeline. Six or more factors fall apart (φ .28-.52). The authors chose 3 "as most interpretable"
after parallel analysis said 7. Split-half replicability, which they did not run, says they chose
well. The eigenvalues reproduce to two decimals. So MPE-92M's smooth decay is a property of that
item pool, not of meditative experience in general. That correction belongs in the area file.

## The exclusion step

159 of 1,102 respondents (14.4%) were removed as "multivariate outliers", Mahalanobis p < .001. Under
the assumption that rule rests on, it should flag about one person in a thousand. I tested it on data
that contain no outliers at all: a Gaussian copula with this sample's own item marginals and
correlations. It flags **12.5%**. Re-applied to the 886 who survived it, it flags another **14.9%**. And
whom it flags is set by the very thing the companion paper counts: the distance correlates .84 with
the number of experiences endorsed. In skewed ordinal data a respondent with many rare endorsements is
"far" by construction.

So, if the distance was computed on the experience items, this step removed about a seventh of the
sample, mostly the people with the most unusual experiences, from a study that then reports how common
unusual and adverse experiences are. The deposit does not say which variables entered. It does not
contain the code for the step, nor the excluded rows. That is why the claim is marked disputed and not
refuted. If the 159 resembled the high endorsers the rule flags among the retained, the IME
adverse-effect incidence would be about 62% instead of 58.4%. The direction is certain; the size is a
scenario.

## Checks that came back clean

- Table 4 subscale and item counts reproduce exactly.
- 517 appears twice, once as Disabling endorsement and once as the companion paper's adverse-effect
  count. It is a coincidence of counts (477 people in both sets, 40 in only one), not a mislabel. I
  checked before writing it as a defect, because two identical integers from different definitions
  are exactly the kind of thing one wants to be a finding.

## The missingness sentence

"Randomly missing by design" is not what the design produces. A valence on an endorsed item is
missing only for people who endorsed more than 50 of 103 items, 178 of the 226 with any such gap. It is
missing at random given intensity, which the imputation conditions on, and the consequence is small
(vandam2025 c7). 48 gaps the design does not explain remain open.

## For CAT

A 3-factor structure of what people report from practice (enabling, disabling, self/reality
distortion) is stable here. It is worth holding next to CAT's dimensions. Distortions correlate .476
with Enabling and .338 with Disabling, which looks like the "same experience, either valence" axis the
paper's valence data describe. An axis, not a category, as the CAT dereification notes would put it.
