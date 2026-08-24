# Trisovic, Lau, Pasquier & Crosas (2022) — *A large-scale study on research code quality and execution*

Sci Data 9:60. DOI 10.1038/s41597-022-01143-6. arXiv 2103.12793.
Read and reanalysed by maria, 2026-08-24, from the published PDF and the released
run logs. Everything below that carries a number was recomputed from
`artifacts/data/`, not read off the paper, unless it says "paper".

---

## What the paper is

2,109 replication packages from Harvard Dataverse (2010 → July 2020), 9,078 R
files. Every file re-executed in a clean Debian container under three R
interpreters (3.2, 3.6, 4.0), twice: once as deposited, once after an automatic
"code cleaning" pass that rewrites `setwd()`, wraps paths in `basename()`,
converts to ASCII, and turns `library(x)` into
`if (!require("x")) install.packages("x")`. Ten research questions. The headline:

> "74% of R files failed to complete without error in the initial execution,
> while 56% failed when code cleaning was applied."

This is the largest execution-level study of deposited research code that ships
its raw logs, and it is the closest thing the literature has to a base rate for
**whether a deposited artifact runs at all** — the step that has to succeed
before any of the reuse practices we normally argue about can even be attempted.

It is also, and this is the reason it repaid a deep read rather than a citation,
a paper whose own analytic pipeline is a small, legible instance of the thing my
`analytic-variability-and-many-analysts` and `rag-and-knowledge-management`
records are about: **one traversal of a chain of researcher degrees of freedom,
reported as if the chain were fixed.**

---

## 1. Both headline numbers reproduce exactly

`reanalysis/denominator.py` reimplements the authors' own combining rule from
`analysis/02-get-combined-success-rates.ipynb` and recovers, to the file:

| condition | successes | denominator | rate | paper |
|---|---|---|---|---|
| no code cleaning | 952 | 3,830 | 24.9% | 25% |
| with code cleaning | 1,472 | 3,695 | 39.8% | 40% |

So this is not a reproduction failure. The artifacts are excellent — raw
per-file, per-version, per-condition logs, the notebooks that made every figure,
the manual journal-policy survey, all under MIT/CC0. **Very few metascience
papers can be checked this hard, and the only reason I can say what follows is
that these authors published enough to be checked.** That should be said plainly
before the criticism, because the criticism is only possible because of the
openness the paper is arguing for.

## 2. The denominator is a third of the corpus, and the bucket that was removed is mislabelled

The authors' rule, verbatim from their notebook (cell 14):

```python
def get_combined_result(r):
    if 'success' in [r.r32, r.r36, r.r40]:            return 'success'
    if pd.isnull(r.r36) or pd.isnull(r.r32) or pd.isnull(r.r40):
        return np.nan                                  # <-- ANY missing version drops the row
    if "time limit exceeded" in [r.r32, r.r36, r.r40]: return np.nan
    ...
```

and then the figure is drawn on `df[df.result.notnull()]`.

**The rule is asymmetric.** A file is a success if *any one* of three versions
succeeded. A file is a failure only if *all three* versions reported. A file that
one version never got to — because a sibling file in the same package ate the
5-hour per-dataset budget — is deleted, not counted.

The paper presents the deleted rows as time-limit-exceeded. That is checkable in
the logs and it is mostly false:

| condition | rows dropped | of which contain a literal `time limit exceeded` | of which are a **recorded error** with ≥1 version missing |
|---|---|---|---|
| no cleaning | 4,054 | 56 (1.4%) | 3,835 (94.6%) |
| with cleaning | 3,866 | 922 (23.8%) | 2,880 (74.5%) |

In the no-cleaning condition, **98.6% of the "TLE" bucket is not TLE.** It is
overwhelmingly files that were observed to fail.

A second rule points the same way (cell 21):
`df.drop(df[df.doi.isin(bad_dois) & (df['result'] != 'success')].index)` —
remove rows from download-failing DOIs *unless they succeeded*. Small (60 and 101
rows) and in the same direction.

## 3. What the rate is, under every denominator that can be defended

| estimator | no cleaning | with cleaning |
|---|---|---|
| **paper** | **24.9%** | **39.8%** |
| symmetric rule (success if any version succeeded; failure if any version errored and none succeeded), over all files seen in ≥1 log | 11.9% | 19.3% |
| Manski lower bound (every unobserved cell would have failed) | 11.9% | 19.3% |
| calibrated imputation, MAR given coverage pattern (optimistic — see below) | 12.6% | 23.6% |
| Manski upper bound (every unobserved cell would have succeeded) | 62.6% | 69.0% |

The bounds are 50 points wide, so **the rate is not point-identified by this
design** and any single number, including mine, is an imputation. What *is*
identified is the ordering: the paper's rule sits about twice the calibrated
estimate in both conditions.

The calibration is worth stating because it is estimated from the paper's own
data rather than assumed. Among fully-observed files, if version A errored, the
probability that any remaining version succeeded is between 0.003 and 0.053. So
missing cells recover almost nothing, and the honest point estimate sits just
above the lower bound.

**Is the missingness ignorable?** No, and the test uses only observed cells so it
never touches the missing one. Per-cell success rate among fully-observed files
vs. partially-observed files: 13.8% vs 9.4% (no cleaning, two-proportion
z = 9.16) and 23.6% vs 14.3% (with cleaning, z = 14.80). Files that a version
never reached are worse files.

**Synthetic check** (`denominator.py::synthetic_check`, the rule-3 discipline —
feed the estimator a case whose answer is known). Simulate the study's structure
with a true rate of 65.4% and failure-dependent missingness: the authors' rule
returns 90.8%; the symmetric rule returns 60.9%. And under a **null** where
missingness is completely at random, the authors' rule *still* returns 81.4%
against a truth of 66.5%. That decomposition matters: **the asymmetry, not the
informativeness of the missingness, is the primary bias.** Even a perfectly
random loss of log lines would inflate this estimator.

The symmetric rule slightly *under*-states in the synthetic (60.9 vs 65.4),
which is why I report it as the lower bound rather than the answer.

## 4. The rule's benefit is 0.8 points and its cost is 20

The asymmetry is justified in the paper by Table 1: "we have identified a version
of R able to re-execute a given R file." That premise is measurable on the
fully-observed files, where no imputation is needed:

| | fully observed | succeed in 1 of 3 | 2 of 3 | 3 of 3 | best single version | any of three | **gain from versions 2 and 3** |
|---|---|---|---|---|---|---|---|
| no cleaning | 3,490 | 13 (0.4%) | 39 (1.1%) | 453 (13.0%) | 14.1% (R 4.0) | 14.5% | **+0.4 pts** |
| with cleaning | 3,169 | 30 (0.9%) | 121 (3.8%) | 655 (20.7%) | 24.6% (R 3.6) | 25.4% | **+0.8 pts** |

Per-version single rates are 13.5 / 14.0 / 14.1 and 21.4 / 24.6 / 24.6. Outcomes
are nearly all-or-nothing at the file level: whether an R script re-executes is a
property of the script, not of the interpreter version.

So the three-version design — which is what motivates the "success in any"
half of the asymmetry — rescues under one file in a hundred, while the asymmetry
it licenses moves the headline by roughly twenty points. **That is the core
methodological finding of this reanalysis, and it is a ratio, not an opinion.**

RQ8, four figure panels on how re-execution varies with R version and release
year, is analysing a factor worth ≤0.8 points at the file level. The paper's own
RQ8 conclusion is null, which is consistent; the framing is not.

## 5. "No cases of code cleaning breaking previously successful code" — false, and instructively so

RQ5, verbatim: *"There were no cases of code cleaning 'breaking' the previously
successful code."* A universal negative over ~8,000 files, and directly testable.

Restricting to (doi, file, version) cells where **both** runs exist and the raw
run succeeded: n = 1,729 comparable cells, of which **25 (1.4%) did not succeed
after cleaning** (4 under R 3.2, 5 under R 3.6, 16 under R 4.0). At file level
under the symmetric rule, 23 files broke against 618 fixed.

The failures are not random. The modal breakage message is
`Error in file(file, 'rt') : cannot open the connection` — which is exactly what
the cleaning's `basename()` rewrite does to a script whose data genuinely lives
in a subdirectory. The cleaner flattens every path on the assumption that all
files were downloaded into one directory; when the package has real structure,
the assumption is wrong and previously-working code stops working.

Under the authors' own combining rule the count of breakages is **0** — because
the rows that would show it are the rows the rule drops. The universal negative
is an artifact of the same asymmetry as the headline.

**This does not overturn the recommendation.** 618 fixed against 23 broken is a
26:1 ratio and automatic cleaning is clearly worth doing. What is wrong is the
word "no", and it matters because "no cases" is what licenses running a rewriter
over someone else's deposited code without review.

## 6. RQ7, the policy claim — the direction survives; the inference is n = 11

The most-cited sentence in the paper is *"the strictness of the data sharing
policy is positively correlated to the re-execution rate."* The paper gives a bar
chart and no statistic. Computing it on the eleven journals above the paper's own
>30-datasets threshold, with strictness 1–5 from their own manual survey:

| journal | level | datasets | paper's rule | symmetric rule (n files) |
|---|---|---|---|---|
| American Journal of Political Science | 5 (verification) | 138 | 61.7% | **29.1%** (669) |
| Political Science Research and Methods | 5 (verification) | 96 | 41.0% | 18.8% (314) |
| Political Analysis | 4 (reviewed) | 77 | 50.2% | 22.3% (489) |
| American Political Science Review | 3 | 83 | 38.8% | 17.8% (427) |
| British Journal of Political Science | 3 | 87 | 35.1% | 20.2% (416) |
| International Studies Quarterly | 3 | 70 | 38.1% | 17.9% (224) |
| Political Behavior | 3 | 60 | 51.0% | 24.0% (304) |
| Research & Politics | 3 | 51 | 29.0% | 14.4% (125) |
| J. Experimental Political Science | 3 | 31 | 25.0% | 11.4% (79) |
| International Interactions | 2 (encouraged) | 50 | 22.6% | 11.0% (127) |
| The Journal of Politics | 1 (no policy) | 190 | 35.1% | 17.7% (750) |

- Spearman ρ = **+0.716**, p = 0.014 under the paper's rule;
  ρ = **+0.666**, p = 0.026 under the symmetric rule. The direction is robust to
  the denominator choice, which is the one thing I most expected to break it.
- Leave-one-out: dropping AJPS takes ρ to +0.567; dropping International
  Interactions to +0.583. Two journals, one at each end, carry most of it.
- n = 11 with **six journals tied at level 3**, which collapses the permutation
  space; p = 0.026 is not far from its floor. One observation with a consistent
  direction, not a rate.
- **A covariate the paper never tests beats the policy variable.** Mean R files
  per dataset, available in the same released metadata, correlates with the
  re-execution rate at ρ = **+0.736** — higher than policy strictness does. It is
  itself correlated with policy level (ρ = +0.363), and the partial correlation
  of level with rate given it is +0.633, so it does not explain the effect away.
  But at n = 11 nothing can be separated from anything, and the paper's policy
  recommendation is offered without either number.
- Median publication year is 2018 for ten of eleven journals; not a confound here.

**The number I would actually quote from this table is not the correlation.**
It is that **AJPS — which since 2016 has run a mandatory pre-publication
verification in which a third party re-runs the code — still has only 29.1% of
its R files re-execute in a clean container** (n = 669 files, 138 datasets).
Under the paper's own rule it is 61.7%. Either way, the journal with the
strictest code policy in the social sciences is nowhere near the ceiling. That is
a far more useful fact for policy than "strictness correlates with rate", and it
points at the real gap: verification is performed in the verifier's environment,
and environment is exactly what does not travel.

## 7. Where this sits against what I already believed

- **`maria2026-rag-specification-dispersion` / `mazuryk2026-powerless-noise`.**
  I audited a released reproduction repo and found 4 of 16 Python files did not
  parse, three broken by the commit named "final experiments". n = 16 — an
  anecdote, and I recorded it as one. Trisovic gives the population version of
  the same phenomenon at n ≈ 8,000, and the base rate is far worse than my
  anecdote suggested: not "a quarter of files are broken", but *at most a quarter
  of files run, and more likely one in eight*. My anecdote was the optimistic
  end. Same family, different rung: syntactic parse ⊂ execution ⊂ reproduction of
  the reported number, and each rung loses most of the survivors of the previous
  one.
- **`breznau2022-hidden-universe` / `menkveld2024-nonstandard-errors` /
  `maria2026-analytic-variability-reanalysis`.** My through-line there was that
  analytic decisions predict how *precisely* an analysis answers a question and
  say nothing about *what* the answer is (out-of-team R² = 0.19 for log SE,
  ≈ 0 for the estimate). This paper is a counter-example worth holding onto: here
  a single analytic decision moves the *estimate* from 12% to 40%. The
  reconciliation is not that Breznau was wrong — it is that Breznau's teams were
  all estimating a regression coefficient whose sampling distribution dominated,
  whereas here the quantity is a **proportion whose denominator is itself a
  researcher choice**. When the degree of freedom is *what counts as a case*, it
  moves the point estimate, not the standard error. That distinction is not in
  either literature and I think it is the real generalisation.
- **`jo2026-subjectivity` (the null-ladder theorem).** Jo et al. showed that a
  monoculture statistic is a discrepancy from a null the analyst chooses, and a
  rich enough null absorbs all of it. The analogue here is exact and I had not
  seen it: a *re-execution rate* is a discrepancy from a denominator the analyst
  chooses, and a permissive enough exclusion rule absorbs all of the failure.
  These two papers have nothing to do with each other and share the assumption
  that the reference class is given. That is a
  `zoo:sharesUnstatedAssumptionWith` edge.
- **My own stewardship rule**, written 2026-08-18 after the third instance in two
  days: *a measurement that silently drops the inputs it cannot handle will
  report on my tool while looking like a report on the world.* This paper is the
  same bug class at publication scale, in a Nature-family journal, in a paper
  whose subject is other people's code quality. I found the rule by breaking my
  own tools three times; it generalises further than I had assumed.

## 8. What I did not do

- I did not re-run any of the 9,078 R scripts. Everything here is computed from
  the released logs. The claim "the rate is ~12–24%" is a claim about *their*
  execution environment, not an independent execution.
- I did not check RQ1–RQ3 (file sizes, comment ratios, library counts). They are
  descriptive, the derived tables are present, and nothing hangs on them.
- I did not attempt the RQ10 reproducibility spot-check (3 datasets, hand-run).
  n = 3 and the paper is appropriately hedged about it.
- The `readability_metrics.csv` artifact belongs to a different paper
  (Bahaidarah et al. 2021) and I did not open it.

## 9. Open

- The dataset-level rate (45%) is computed on datasets with ≥1 successful file
  and inherits the same asymmetry, more severely, since one success rescues a
  whole package. I have not recomputed it and it is the number a repository
  operator would actually act on.
- Is the "files per dataset" association real or mechanical? A dataset with many
  files has more chances at one success and more chances to exhaust the budget.
  Separating those needs the per-dataset timing data, which is not released.
- Nobody has repeated this on Dataverse *after* 2020 — i.e. after `renv`,
  `targets` and Rocker had time to diffuse. The paper found `renv` in 2 packages
  out of 2,091. That is the single most valuable follow-up and it is now four
  years overdue.

## 10. Do the paper's own recommendations work? (added 2026-08-24)

The paper closes with six recommendations for researchers. None is tested against
the outcome the same paper measured, although the released data supports the test:
`dataset_level.csv` codes, per replication package, whether it ships documentation,
R Markdown, a Dockerfile, tests, a project file, code in another language, spaces in
filenames. `reanalysis/do_recommendations_work.py` joins that to the run logs.

**First, the unit of analysis, because it changed the answer.** My first pass used
"the package has at least one file that ran" and documentation looked overwhelming:
35.8% against 22.2%, z = 6.66. That is an artifact of my own outcome definition — a
package with twenty files has twenty chances, and package size is by far the largest
association in the table (z = +16.8). Switching to the file-level rate within each
group removes it. And a z on 9 or 22 clusters is arithmetic rather than evidence, so
the inference below is a bootstrap over **packages**, 4,000 resamples.

**A second, independent ICC.** The per-file outcome within a replication package has
**ICC = 0.251** (7,557 files in 2,103 packages, mean cluster size 3.59, design effect
1.65). The Samuel & Mietchen corpus — a different language, a different repository, a
different research community — gives 0.435 for the same kind of cluster. Two estimates,
same direction, both large. Every file-level percentage in this literature needs the
correction and none applies it.

| practice | packages | file rate with | without | difference [95% CI, cluster bootstrap] |
|---|---|---|---|---|
| documentation / README present | 1,190 | 20.0% | 17.4% | +2.6 [−1.4, +6.4] |
| uses R Markdown | 65 | 28.0% | 18.8% | **+9.2 [+0.3, +20.4]** |
| contains a test file | 108 | 23.4% | 18.8% | +4.6 [−2.6, +12.6] |
| ships an .Rproj file | 22 | 38.2% | 18.9% | +19.4 [−6.1, +43.1] |
| filename contains a space (discouraged) | 658 | 20.2% | 18.8% | +1.4 [−2.4, +5.2] |
| contains other-language code (discouraged) | 661 | 21.5% | 18.2% | +3.3 [−0.9, +7.5] |
| ships a Dockerfile | **9** | 6.7% | 19.3% | −12.7 [−17.0, −8.1] |
| Sweave / Rnw | **5** | 4.3% | 19.3% | −14.9 [−20.6, −12.6] |

**Only R Markdown has an interval excluding zero, and its lower bound is +0.3.** The
Dockerfile and Sweave rows have intervals excluding zero on the wrong side, and they
are 9 and 5 packages: the interval is narrow because those few packages consistently
failed, which is a statement about nine packages and not about containerisation.

**How big an effect could this corpus have shown?** A power curve over 20 random
assignments of a fake practice to 1,190 packages: planting a rescue of 0 / 3 / 6 / 12 /
20% of failing files gives recovered +0.2 / +2.6 / +5.1 / +9.9 / +16.3 points at
power 5% / 35% / 75% / 100% / 100%. The 5% false-positive rate at a planted zero says
the bootstrap is calibrated. So the documentation null is **inconclusive at +2.6, not
strong** — 35% power — while a real benefit of +5 points would have shown three times
in four.

**The number I would actually put in front of a repository operator is a denominator.**
Containerisation, the recommendation with the best theoretical case and the one my
synthesis names as the only untested intervention that could matter, appears in **9 of
2,060 packages (0.44%)**. Workflow libraries (drake, targets, workflowr): **zero**.
Provenance libraries: **zero**. It is not that these were tried and failed. After a
decade of advice they have never been tried at a scale anyone could measure — and no
amount of further advice changes that, because advice is what has been tried.

This pairs with `samuel2024-jupyter-pmc` section 4, which tests the *other* universal
recommendation (pin your dependency versions) on the *other* corpus, in the other
language, and also fails to find support. Two corpora, two languages, two
recommendations, no evidence.
