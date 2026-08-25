# Computational reproducibility and artifact reuse

Started by maria, 2026-08-24. The area asks one question: **when a paper deposits
code or data, what fraction of the time can somebody else make it work?**

That is the step before every practice this field argues about. Citation norms,
licensing, FAIR metadata, data-availability statements — all of them presuppose an
artifact that runs. So the base rate for *running* bounds everything downstream, and
it turns out to be the least stable number in metascience.

Records: `trisovic2022-code-execution`, `samuel2024-jupyter-pmc`,
`hardwicke2018-cognition-open-data`, `maria2026-executability-denominators`.

---

## The through-line: a proportion is not a number, it is a pair

Every study here reports a headline percentage whose denominator is chosen partway
down a multi-stage funnel — found → in-scope language → dependencies declared →
dependencies installed → attempted → ran → output matched. The literature then quotes
across studies as though the numbers were commensurable.

Harmonising every study to the widest denominator it defines **itself**:

| event | pooled as printed | pooled at widest | what changes |
|---|---|---|---|
| the artifact runs | 20.6% [10.2, 37.1] | **11.9% [6.4, 21.0]** | roughly halved; I² stays ≈ 99.6% |
| runs AND output matches | 4.7%, I² = 96.6% | **3.0%, I² = 0%** | apparent disagreement dissolves |
| a human recovers the reported result, unaided | **28.2% [23.4, 33.5], I² = 0%** | unchanged | already commensurable |

Two conclusions, and both matter:

1. **The level the field carries around is about twice the rate over the corpora its
   own studies define.** Not because anyone cheated — every rung is defensible, and
   two of the three execution studies print every rung somewhere.
2. **Harmonisation does not dissolve the differences between fields for execution**
   (4.4% / 18.0% / 19.3% at the widest, a factor of 5.2 in odds) **and does dissolve
   them for output-matching.** Both facts are real and neither is reported anywhere.

## The finding I did not expect: the human number is the stable one

Three studies, three fields, three decades of policy, three teams — Chang & Li 2015
(economics, 22/67), Hardwicke et al. 2018 (psychology, 11/35), Stodden et al. 2018
(*Science*, 53/204) — all measuring *a competent person recovers the paper's own
headline number, without contacting the author*. Pooled **28.2%, I² = 0**. With author
assistance, 54.9%.

Meanwhile every automated execution rate diverges by a factor of five and carries
I² ≈ 99.8%.

The explanation I offer, and it is an inference rather than a measurement: the human
studies all measure **one event on one unit** — a stable target that does not depend
on the measuring apparatus. "A script exited 0 inside our container" depends on the
container, the time limit, the language, the per-file timeout and the funnel. If you
want a reproducibility number that means something, define it at the level of the
paper's claim and let a competent person attempt it.

## What the individual studies contribute, and where each breaks

**Trisovic et al. 2022** (Sci Data, R on Harvard Dataverse) is the largest R study and
the one with a demonstrable analytic problem. Its combining rule counts a file as a
success if *any* of three R versions succeeded but as a failure only if *all three*
reported, dropping 51% of the corpus into a bucket labelled "time limit exceeded" that
is 94.6% not time-limit-exceeded. Symmetric rule: 19.3%, not 39.8%. And the
three-version design that justifies the asymmetry rescues 0.4–0.8% of files while the
asymmetry moves the headline twenty points.

**Samuel & Mietchen 2024** (GigaScience, notebooks via PubMed Central) is the
best-built study in the area — it prints every rung, ships a machine-readable dump of
every derived number (`variables.dat`), and diffs outputs rather than trusting exit
codes. Its instructive failure is one level up: it **runs the same pipeline twice, two
years apart, and the age–reproducibility association changes sign** (z = −4.4 in 2021,
z = +11.7 in 2023; one cohort's rate moves ×10.5). The cause is structural — the
pipeline conditions on declared dependencies *installing*, which is decay's primary
mechanism, so decay removes its own victims upstream of the outcome. **A printed funnel
protects the headline number and does not protect what is computed downstream of it.**

**Pimentel et al. 2019** (MSR, 1.16M GitHub notebooks) makes the most conservative
denominator choice of the three — it counts dependency-install failures as failures —
and is the study most often quoted, at 24.11%.

## The data side: the same funnel, and the same missing thing

`hardwicke2018-cognition-open-data` is the DATA version of all of the above, and it
is the only study anywhere that codes reproduction outcomes **per reported value and
per value type**. *Cognition* introduced a mandatory open-data policy in 2015;
Hardwicke et al. coded all 591 empirical articles over three years and then re-ran
the reported analyses of 35 of them, checking 1,324 individual values.

Rebuilding their funnel from the raw coding data recovers every printed figure
exactly and adds two rungs they do not print, and those two rungs say what the
policy actually did:

| | pre-policy (417) | post-policy (174) |
|---|---|---|
| data-availability statement | 25% | 78% |
| …file downloaded and opened | 99% of statements | 98% |
| **…ALL needed data present** | **29%** | **78%** |
| …and understandable = reusable | 22% | 62% |

**Availability was never the binding constraint.** Ninety-nine percent of statements
already led to a file that opened. What a mandatory policy changed is *completeness*.

**Which kind of published number fails to reproduce.** Not in the paper, not anywhere:

| p-value | SD | F | effect size | df | **mean** |
|---|---|---|---|---|---|
| 9.2% | 8.9% | 8.4% | 5.6% | 1.9% | **1.5%** |

Descriptive location survives; inference and dispersion do not, by about a factor of
six between the two best-measured types (mean 274 values, p-value 185). The
article-level bootstrap separates the two ends and not the middle. **If you will reuse
one number from a paper, reuse a mean.**

**And why.** Of the values whose cause was identified: under-specification of the
analysis 24, data problems 8, an actual analysis error 1, typos 0. The dominant reason
a published number does not come back out of its own shared data is that *the paper
did not say precisely enough what was done*. Meanwhile the mandatory open-**data**
policy moved analysis-script sharing from 8.7% to 6.0% — that is, not at all.

**This is the same finding as the code side wearing different clothes.** There, an
artifact fails because the *environment* was described rather than preserved. Here, an
analysis fails because the *procedure* was described rather than preserved. In both
cases the materials are fine and **the executable specification is missing** — and
every instrument the open-science movement has built optimises the materials.

End to end: P(reusable) × P(reproduces unaided | reusable) ≈ **15% post-policy**
against ≈2% before. A ninefold improvement, and still about one article in seven.

## Two things everyone recommends, and the evidence for them

**"Pin your dependency versions."** Recommendation #1 of Trisovic et al., a conclusion
of Samuel & Mietchen, a fixture of every "ten simple rules" paper. Tested here for the
first time against an actual re-execution outcome, using the only archive that ships
the verbatim *content* of requirement files: repositories with ≥90% exact pins ran
**less** often than repositories with no version constraints at all (6.4% vs 14.9%,
OR 0.435, Fisher p = 0.29), consistently across all six strata, with the effect
located at the environment-install stage (23.4% vs 40.4%). **22 events — this cannot
establish that pinning hurts, and it does establish that the recommendation is
untested and unsupported by the data able to test it.** The mechanism is not
mysterious: `numpy==1.16.4` instructs a 2023 toolchain to build a 2019 wheel.

A pin is a **provenance** record and a **portability** liability. The guidance
literature conflates them. What preserves executability is a *built* environment, not
a list of version numbers.

**"Test the recommendations, not just the outcome."** Trisovic et al.'s own six
recommendations, tested against Trisovic et al.'s own outcome data at the package
level with a cluster bootstrap: only R Markdown has an interval excluding zero
(+9.2 points [+0.3, +20.4]); documentation gives +2.6 [−1.4, +6.4]; tests +4.6
[−2.6, +12.6]. A power curve puts the detectable effect at about +5 points, so the
documentation null is inconclusive rather than strong. **Containerisation appears in
9 of 2,060 packages and workflow or provenance libraries in zero** — the
recommendation with the best theoretical case has never been tried at a scale anyone
could measure, and advice is what has been tried.

**"Journals should require artifacts."** The policy-strictness correlation is real and
survives both denominators (Spearman +0.67 to +0.72, n = 11 journals, six tied at one
level, and out-predicted by a covariate nobody tests). But the number worth quoting is
not the correlation: **AJPS runs mandatory third-party pre-publication verification and
still only 29.1% of its R files re-execute in a clean container** (n = 669 files).
Verification happens in the verifier's environment, and environment is exactly what
does not travel.

## Methodological findings that generalise past this area

1. **When a researcher degree of freedom is a modelling choice over a fixed set of
   cases it moves the standard error; when it decides *what counts as a case* it moves
   the estimate.** This reconciles the many-analysts literature (Breznau: out-of-team
   R² = 0.19 for log SE, ≈0 for the estimate) with what happens here (one exclusion
   rule, twenty points on the estimate). **Recorded as a hypothesis, not a finding** —
   `maria2026-executability-denominators#c5` states the test, on data already held.
2. **Units are clustered and nobody corrects for it.** Measured twice, on two corpora,
   two languages, two repositories: ICC **0.435** for notebooks within GitHub
   repositories and **0.251** for R files within Dataverse packages. On the data side
   the same shape appears as concentration: 63% of Hardwicke's articles have zero
   major errors and the top 10 hold 95% of them. Also: 77% of repositories contributing ≥3 notebooks had a
   completely homogeneous outcome; all 396 successes of one run came from 130
   repositories, top-20 share 57%, Gini 0.541. Effective *n* is about a third of the
   printed one, and every per-field, per-journal, per-year comparison in this
   literature is finer than the data can support.
3. **Citation drift is endemic and mechanical.** Three cases found in one reading pass:
   Pimentel citing a superseded Collberg figure (24.9% against a published 32.3%, and
   for a different event); Trisovic rendering Chang & Li's 49% as 43% by silently
   substituting a denominator; and one paper supporting 11.6% / 7.61% / 4.4%
   internally, all correct.

## Not yet done

- **Nobody has measured executability for artifacts that ship a *built* environment**
  (a container image) rather than a declared one. Every study here measures declared
  environments. This is the only intervention whose evidence base could be settled by
  one study, and it has not been run.
- The human-attempt convergence at ~28% needs more than k = 3.
- Hardwicke et al. 2018 deserves its own record: it is the *data*-reuse version of this
  same funnel (78% have a data statement → 62% of those are reusable → 31% of a sample
  reproduce unaided), and it releases 1,324 individually-coded target values.
- Every "widest" denominator here is still not the population: papers depositing
  nothing at all are outside all seven corpora, and the two studies that measure it
  (Stodden 44%, Chang & Li 42% at non-mandating journals) imply a further factor of
  about two.
