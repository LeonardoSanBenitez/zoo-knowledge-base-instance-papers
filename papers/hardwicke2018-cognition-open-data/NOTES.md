# Hardwicke et al. (2018) — *Data availability, reusability, and analytic reproducibility: evaluating the impact of a mandatory open data policy at the journal Cognition*

R Soc Open Sci 5:180448. Read and reanalysed by maria, 2026-08-24, from the full
text (EuropePMC JATS, the publisher PDF being blocked) and the released OSF data.
Every number below was recomputed from `artifacts/`, not read off the paper, unless
it says "paper".

---

## Why this one, and why it belongs next to the code-execution records

*Cognition* introduced a mandatory open-data policy on 1 March 2015. Hardwicke and
eleven co-authors coded all 591 empirical articles published March 2014 → March 2017
for data availability and in-principle reusability, then took 35 articles with
reusable data and **re-ran the reported analyses, checking 1,324 individual reported
values one at a time**.

This is the *data* version of the funnel my other records measure for *code*:
deposited → present → usable → the reported number comes back out. It is the only
study I have found that codes reproduction outcomes **per value and per value type**,
and it is preregistered.

## 1. Everything reproduces, to the article

`reanalysis/which_numbers_fail.py` rebuilds the funnel from `codingData.csv` and
recovers the paper's printed figures exactly:

| | pre-policy (417 articles) | post-policy (174) |
|---|---|---|
| data-availability statement | 104 (24.9%) | 136 (78.2%) |
| …files downloaded and opened | 103 (99.0% of statements) | 133 (97.8%) |
| **…ALL needed data present** | **30 (28.8%)** | **104 (76.5%)** |
| …and understandable = **reusable** | 23 (22.1%) | 85 (62.5%) |

and the reproducibility side: 35 articles, 1,324 values, 64 major numerical errors,
146 minor, 2 insufficient-information, 0 decision errors; 11 Success, 11 Success with
author assistance, 13 Failure despite author assistance.

**The two bold rows are not printed anywhere in the paper.** They matter, because they
say what the policy actually did.

## 2. The policy's real effect is on completeness, not availability

Of articles whose data downloaded and opened, the share with *all needed data present*
went from **30/103 = 29%** to **104/133 = 78%**. Availability itself was never the
binding constraint — 99% of statements led to a file that opened, before and after.
What a mandatory policy changed is whether the file contained the study.

That is the fact a repository or journal should act on: **a data-availability
statement was already reliable; a data-availability statement plus a completeness
check is the intervention.**

## 3. What the policy did *not* change: analysis scripts

Of articles whose data downloaded, the share also sharing an analysis script:

| pre-policy | post-policy |
|---|---|
| 9 of 103 (8.7%) | 8 of 133 (6.0%) |

**A mandatory open *data* policy tripled data completeness and moved script sharing not
at all** — slightly down, on tiny counts. And 34 of the 35 articles taken forward for
reproduction shared no script.

## 4. Which kind of published number fails to reproduce?

The released file carries `Total_<type>` and `Major_<type>` for eighteen types of
reported value. The rate by type is not in the paper and, as far as I can find,
nowhere else. It answers the question a reuser actually has.

| type of reported value | checked | major errors | rate | article-level bootstrap 95% CI |
|---|---|---|---|---|
| **p-value** | 185 | 17 | **9.2%** | [2.5%, 17.9%] |
| **standard deviation** | 169 | 15 | **8.9%** | [1.3%, 19.6%] |
| F statistic | 83 | 7 | 8.4% | [0.0%, 20.8%] |
| effect size | 108 | 6 | 5.6% | [0.8%, 12.2%] |
| t statistic | 58 | 3 | 5.2% | [0.0%, 12.9%] |
| standard error | 55 | 2 | 3.6% | [0.0%, 13.3%] |
| degrees of freedom | 209 | 4 | 1.9% | [0.0%, 5.6%] |
| confidence interval | 66 | 1 | 1.5% | [0.0%, 12.5%] |
| sample size | 67 | 1 | 1.5% | [0.0%, 14.3%] |
| **mean** | 274 | 4 | **1.5%** | [0.0%, 3.8%] |

Types with fewer than 20 values (r, chi-square, Bayes factor, median, regression
coefficient, z, inter-rater reliability) are printed in the log and never ranked.

**The pattern is that descriptive location survives and inference does not.** A mean —
the most-checked type, 274 values — fails at 1.5%; a p-value fails at 9.2%, six times
as often. That makes mechanical sense: a mean is a near-direct function of the shared
data, while a p-value is a function of the whole model specification, and the
specification is the thing that was not shared (see §3 and §6).

**Practical form, and the one sentence I would give a reuser:** *if you are going to
build on one number from a paper, build on a mean; the p-value attached to it is about
six times likelier not to come back out of the authors' own data.*

The confidence intervals overlap heavily and the ordering is not established at this n.
What is established is the two ends: mean [0.0, 3.8] against p-value [2.5, 17.9].

## 5. The errors are extremely concentrated

- **22 of 35 articles (63%) had no major numerical error at all.**
- The single worst article holds 13 of 64 major errors (20%); the top 10 hold 95%.

So "9.2% of p-values are wrong" must not be read as a per-paper hazard. Most papers are
clean and a few are badly wrong. This is the same clustering fact I measured for code
(ICC 0.435 for notebooks in repositories, 0.251 for files in packages) appearing on the
data side, and it has the same consequence: **a rate computed over values is not a rate
you can apply to a paper.**

## 6. What actually went wrong

Values whose cause was identified and resolved after contacting the authors:

| resolved as | values |
|---|---|
| **the analysis was under-specified in the paper** | **24** |
| a problem with the shared data | 8 |
| an error in the original analysis | 1 |
| a typo | 0 |

And nine articles had at least one error whose cause was **never identified**.

**The dominant reason a published number does not come back out of its own shared data
is that the paper did not say precisely enough what was done.** Not a wrong number, not
a corrupted file — an under-specified procedure.

This is the same finding as the code side, in different clothes. There: an artifact
fails because the *environment* was described rather than preserved. Here: an analysis
fails because the *procedure* was described rather than preserved. In both cases the
materials are fine and **the executable specification is missing**. Everything in the
open-science toolkit optimises the materials.

## 7. The 35 are a best-case stratum, and 37% of them still failed

The 35 were drawn from the reusable pool and then triaged further for "a substantive
finding based on a relatively straightforward analysis". Checked in the data: all 35
were coded as having all needed data *and* being understandable. So no sharing practice
can be tested on this sample — the variables have no variance.

What can be said is worse than a correlation. **This is the friendliest possible
sample, and 13 of 35 (37%) could not be reproduced even with the original authors
helping**; only 11 of 35 (31%) reproduced unaided.

## 8. The end-to-end number nobody states

P(article's data is reusable) × P(its numbers reproduce unaided | reusable):

| era | reusable | × unaided conditional | end to end |
|---|---|---|---|
| pre-policy | 23/417 = 5.5% | 11/35 = 31.4% | **≈ 1.7%** |
| post-policy | 85/174 = 48.9% | 11/35 = 31.4% | **≈ 15.4%** |

A mandatory open-data policy moved the share of published articles whose reported
numbers a stranger can recover from the shared data without contacting the author from
about 1.7% to about **15.4%** — a factor of nine, and still about **one article in
seven**.

Two load-bearing assumptions, both mine. The conditional 31.4% is measured on a
best-case stratum, so it is optimistic; and applying it to the pre-policy era assumes
the conditional did not change, which is unverifiable. The pre/post ratio is therefore
rough. **The post-policy 15% does not depend on the second assumption and is the number
I would defend.**

## 9. Where this stands against the rest of the area

- **`maria2026-executability-denominators`.** Hardwicke's unaided rate, 31.4%, is one
  of the three studies in the "a human recovers the reported result" stratum that pool
  at 28.2% with I² = 0 across economics, psychology and *Science*. Working through the
  raw data here has not moved that number and has told me what it is a rate *of*: a
  triaged best case.
- **`trisovic2022-code-execution` §10 and `samuel2024-jupyter-pmc` §4.** Both test a
  recommended practice against an outcome and fail to find support. This record adds the
  third and most direct instance: the policy that was mandated (share data) moved a
  different variable from the one that binds (specify the analysis), and script sharing
  — the closest thing to specifying it — did not move at all.
- **My own artifact-status vocabulary.** `paper.schema.json` distinguishes
  `present-but-insufficient` from `dangling` and the CONTRIBUTING file claims "both pass
  every artifact-badging scheme in existence". Here is the measurement: pre-policy,
  103 of 104 data statements led to a file that opened and only 30 of those contained
  all the data. **71% of pre-policy available datasets were `present-but-insufficient`,
  not `dangling`.** A badge would have shown green on all 103.

## 10. What I did not do

- Did not re-run any of the 1,324 value checks. I reanalysed their coding, not their
  analyses.
- Did not use the interrupted-time-series machinery; the pre/post split here is a plain
  date cut at 2015-03-01, which is what the funnel needs and is not what the paper's
  causal claim rests on.
- Did not touch Study 1's secondary questions (licence types, file formats, hosting).
- Did not obtain the individual reproducibility reports (osf.io/p7vkj), which contain
  the per-article narratives and would say *which* under-specification bit.

## 11. Open

- The per-type error table should be repeated on any other corpus with per-value
  coding. If "means reproduce, p-values do not" holds twice, it is a rule for reusers
  and it is currently nobody's finding.
- 9 articles had errors whose cause was never identified. That is 14% of major errors
  with no explanation, in the friendliest sample, with author cooperation. Nobody has
  asked what those are.
- The obvious intervention this points at — require the analysis script, not only the
  data — has been tested nowhere. Script sharing here is 6–9% and did not respond to a
  mandatory data policy, so there is no natural experiment in this corpus to exploit.
