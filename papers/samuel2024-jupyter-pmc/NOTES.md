# Samuel & Mietchen (2024) — *Computational reproducibility of Jupyter notebooks from biomedical publications*

GigaScience 13:giad113. arXiv 2308.07333. Read and reanalysed by maria, 2026-08-24,
from the PDF, the shipped analysis notebooks, and the full SQLite database of the
2021 run. Every number below marked "recomputed" came out of that database.

---

## What the paper is, and why it is the best-built study in this area

Mine PubMed Central full texts for GitHub links → clone → find Jupyter notebooks →
install their declared dependencies in a conda environment → execute → diff the
outputs against what the notebook already contains. Then do the whole thing twice,
in 2021 and again in 2023, and report both.

The 2023 funnel, as the paper states it:

| stage | n |
|---|---|
| notebooks found | 27,271 (2,660 repos, 3,467 publications) |
| written in Python | 22,578 |
| dependencies declared in a standard requirements file → attempted | 15,817 |
| all declared dependencies installed → executed | 10,388 |
| ran with no exception | 1,203 |
| …and produced results **identical** to the recorded outputs | **879** |
| …and produced **different** results | 324 |

Three things make this study better than its neighbours and they should be said
first, because most of what follows is criticism.

1. **The entire funnel is printed.** Trisovic et al. print one ratio. Pimentel et al.
   print one ratio. Samuel & Mietchen print every stage, so a reader can pick the
   denominator instead of inheriting one.
2. **The output diff is the actual reproducibility measure**, not a proxy. A notebook
   ships its own previous outputs; re-running and diffing is a genuine test of
   "same code, same data, same result". Nobody else in this set does that at scale.
3. **`analyses/variables.dat`** is a 911-line machine-readable key–value dump of every
   derived number in the paper. This is the single best artifact practice I have seen
   in this literature and I intend to copy it: a paper's numbers as a file, not only
   as prose. It is what makes a claim like "5.56%" checkable without re-deriving it.

Which is exactly why criticism is possible here at all.

---

## 1. Which number is "the" reproducibility rate? Six defensible answers

879 identical results, and the study itself supplies at least six denominators:

| denominator | n | rate | who would quote it |
|---|---|---|---|
| notebooks that installed and were executed | 10,388 | 8.5% | the abstract's narrative |
| notebooks whose deps were declared (attempted) | 15,817 | **5.56%** | the paper's own printed figure |
| Python notebooks | 22,578 | 3.9% | someone asking about Python notebooks |
| all notebooks found | 27,271 | 3.2% | someone asking about notebooks in papers |
| repositories with a notebook | 2,660 | — | someone asking about *papers* |
| publications | 3,467 | — | the question everyone actually means |

And "ran without error" gives 11.6% / 7.61% / 5.3% / 4.4% over the same ladder.

This is the same phenomenon I recorded in `trisovic2022-code-execution`, with one
crucial difference: **there the denominator was chosen silently inside a notebook and
half the corpus was labelled "TLE" when it was not; here every rung is printed.** The
failure mode is not shared. What is shared is that the *quoted* number depends on a
choice, and downstream citation loses the choice.

Evidence that it does: Pimentel et al. write that their 24.11% "is close to the
reproducibility rate of 24.9% that Collberg et al. achieved". I read the Collberg TR.
It reports **32.3% / 48.3% / 54.0%** of 402 code-backed papers, for "obtained and built
in under 30 minutes" / "built with extra effort" / "built, or the author says it
would". 24.9% is from the superseded 2014 version that Pimentel cites. And the two
quantities are not the same event on the same population in any case: Collberg
measures *a C/C++ project building*, Pimentel measures *a notebook running to
completion*. The apparent convergence of this literature around "about a quarter" is
partly an artifact of quoting across incommensurable funnels.

## 2. Notebooks are not independent, and the intra-class correlation is 0.435

Every notebook in a repository shares one conda environment, one set of data paths and
one author. Recomputed on the 2021 database (`reanalysis/cluster_and_age.py`):

- 4,169 attempted executions across **685 repositories**, mean cluster size 6.06
- **ICC = 0.435** for "executes without exception"; design effect 3.20; **effective n
  = 1,302, not 4,169**
- ICC = 0.335 for "executes and matches"; design effect 2.70
- of the 364 repositories contributing ≥3 executions, **281 (77.2%) had a completely
  homogeneous outcome** — every notebook succeeded or every notebook failed

A repository in this design is close to one Bernoulli trial. Every notebook-level
percentage in this literature — per field, per journal, per year, per article type —
is computed on an n that is roughly three times its effective size, and the finer the
slice, the more likely it is a statement about one repository.

**Concentration, measured:** the 396 successes of the 2021 run come from **130
repositories**. The top 20 account for 56.6%; the top 50 for 78.5%; Gini 0.541.

## 3. The "decay rate" analysis, which the paper does not report and which changes sign

`analyses/PMC4.DecayRate.ipynb` is titled *"Decay Rate: Replication Success over
Repository Age"*. "dependency decay" is a keyword of the paper. The paper's entire
statement about it is one clause: *"with notebooks from newer repositories not
generally performing better than older ones."*

**2023 run** (`reanalysis/age_trend.py`, from the notebook's own printed table):

| repo age (yr) | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| success rate | 11.8% | 8.8% | 6.3% | 17.2% | 16.2% | 11.3% | 12.1% | 25.5% | 8.5% | **48.9%** |

Cochran–Armitage trend **z = +11.7**, odds ratio **1.166 per year of age**. Older is
*better*, strongly. And the notebook filters to cohorts with >10 successes, which
deletes 2010–2012 — whose counts I recovered by subtraction (14 successes in 60
executions, 23.3%, roughly twice the corpus rate). **The filter removes evidence in
favour of the association the figure shows**, and undoing it strengthens the trend.
The trend survives a clustering correction all the way to ICC = 1 (z = 5.93), and a
synthetic clustered null (in which the naive test fires 21% of the time instead of 5%)
puts the 95th percentile of |z| at 2.96 against an observed 11.7.

**2021 run** (`reanalysis/cluster_and_age.py`, from the database):

Cochran–Armitage **z = −4.40** at notebook level, **z = −1.87** at repository level.
Odds ratio 0.882 per year. Older is *worse*.

**The same pipeline, run by the same people two years apart on overlapping cohorts,
gives opposite signs.** Cohort by cohort, the rate ratio between runs:

| repo year | 2021 run | 2023 run | ratio |
|---|---|---|---|
| 2013 | 6/129 = 4.7% | 69/141 = 48.9% | **×10.5** |
| 2016 | 22/643 = 3.4% | 51/420 = 12.1% | ×3.5 |
| 2017 | 37/674 = 5.5% | 75/666 = 11.3% | ×2.1 |
| 2019 | 146/840 = 17.4% | 267/1549 = 17.2% | ×1.0 |
| 2020 | 55/565 = 9.7% | 231/3670 = 6.3% | ×0.6 |

A 2013 cohort of near-identical size moved from 4.7% to 48.9%. Whatever that measures,
it is not a property of code written in 2013.

**My reading.** This design cannot measure dependency decay, and the reason is
structural, not a mistake anyone made. The pipeline conditions on *the declared
dependencies installing successfully* before a notebook is ever executed. Decay's
primary mechanism is that an old pin no longer installs — so decay removes its own
victims from the denominator upstream of the outcome. What is left in the old cohorts
is the survivors, and survivors are, by construction, code that only ever depended on
things that stayed stable. **Age effects in a survivor-conditioned design carry the
sign of the survival filter, not of the decay.** That is why the sign is unstable, and
it is a general warning for anyone designing the follow-up study everyone wants.

## 4. Does pinning your dependency versions actually help? Nobody had checked

"Capture your library versions" is recommendation #1 of Trisovic et al., a conclusion
of this paper, and a fixture of every "ten simple rules" article. I could not find it
tested against a re-execution outcome. This archive makes it testable, because it ships
the verbatim **content** of every requirement file alongside the outcome.

`reanalysis/does_pinning_help.py`, unit = repository (because of the ICC above),
restricted to the 191 repositories that declared requirements — repositories with no
requirements file are *not* a control group, they receive a large default conda
environment, which is a different treatment:

| pinning of the requirements file | env installed | ≥1 notebook ran |
|---|---|---|
| no version constraints at all (n=47) | 40.4% | **14.9%** |
| <50% exact pins (n=86) | 43.0% | 12.8% |
| 50–90% exact pins (n=7) | 14.3% | 14.3% |
| ≥90% exact pins (n=47) | 23.4% | **6.4%** |
| Pipfile.lock, fully locked (n=5) | 40.0% | **0.0%** |

- headline 2×2: 3/48 vs 19/143, **OR = 0.435, Fisher exact p = 0.29**
- adjusted for dependency count, licence and stars: β = −0.392 (SE 0.644, z = −0.61)
- every one of six pre-specified strata (by licence / releases / stars) points the same
  way, z between −0.99 and −2.08
- the environment-install stage is where it happens: ≥90% pinned installs 23.4% of the
  time against 40.4% unconstrained, z = −1.77

**What this does and does not establish.** 191 repositories, 22 events. It cannot
establish that pinning hurts and I will not say it does. What it does establish is
that **the field's most repeated recommendation has never been tested, and the one
dataset that can test it does not support it** — the point estimate is on the wrong
side, consistently, across every stratum, and the mechanism is not mysterious:
`numpy==1.16.4` is an instruction to build a 2019 wheel on a 2023 toolchain, and it
fails where a bare `numpy` succeeds.

A pin is a *provenance* record and a *portability* liability, and the literature
conflates them. What preserves executability is a **built environment** (a container
image, a lockfile *plus* the index that resolves it), not a list of version numbers.
Trisovic's recommendation #4 — use Docker — is the one that survives this; #1 does not,
on this evidence.

## 5. Reproduction of my own reproduction

The funnel recomputed from the database matches the paper's printed 2021 values
exactly: 4,169 attempted, 396 finished, 245 identical, 151 different,
different/(different+identical) = 0.381 vs the paper's 0.38. That is the check that
licenses everything else in this file.

## 6. How this stands to what I already had

- **`trisovic2022-code-execution`.** Same estimand, different language, different
  repository, and the two studies make opposite *methodological* choices about the same
  problem. Trisovic hides the funnel and picks a permissive denominator; Samuel &
  Mietchen print the funnel and pick a middle one. Cross-checking their raw rates
  against a common denominator is the point of
  `maria2026-executability-denominators`.
- **`maria2026-analytic-variability-reanalysis` / `breznau2022-hidden-universe`.** Two
  runs of *one* pipeline by *one* team, two years apart, giving opposite signs is a
  many-analysts result with n = 1 analyst. It says the dispersion Breznau attributes to
  analysts is available without any analysts at all, when the estimand is conditioned on
  an unstable upstream filter.
- **`jo2026-subjectivity`.** Same edge as for Trisovic: the reference class is a choice,
  and here the choice is printed, which is the fix.
- **My own KB stewardship rule** (*a measurement that silently drops the inputs it
  cannot handle reports on the tool while looking like a report on the world*) has now
  appeared in three published studies in one session. The version here is subtler than
  Trisovic's: nothing is dropped silently, the drop is printed — and the *downstream*
  analysis (decay) is still invalid, because it conditions on the survivor filter. **A
  printed funnel protects the headline number and does not protect the sub-analyses.**
  That is a new lesson and it applies directly to my own `kb.py health` reporting.

## 7. What I did not do

- I did not run the pipeline. I re-ran nothing biomedical; I re-analysed their records.
- The database I queried is the **2021** run (1,419 articles / 2,177 repos / 9,625
  notebooks). The paper's headline numbers are the **2023** run. The clustering and
  pinning results are therefore measured on the 2021 corpus and assumed to transfer as
  structural properties. That assumption is stated, not tested.
- I did not download the 2023 database (I did not locate a Zenodo record for it) and
  did not use the FAIR Jupyter knowledge graph (arXiv 2404.12935), which is the same
  data as RDF with a SPARQL endpoint and would be the cheaper way to redo section 4 on
  the newer corpus.
- The 371 MB SQLite file is **deleted**; `reanalysis/cluster_and_age.py` carries the
  two commands that regenerate it.

## 8. Open

- Redo section 4 (pinning) on the 2023 corpus, where n is ~3× larger and the event
  count might reach the point of being informative. 22 events is not.
- The 2013 anomaly (×10.5 between runs) is one or two repositories. Naming them would
  settle whether the whole "old code reproduces better" pattern is a single artifact.
- Nobody has measured executability with the *environment* preserved rather than
  declared — i.e. the rate for artifacts that ship a container image. If Trisovic's
  recommendation #4 is right, that rate should be far above 12%, and it is the only
  version of this measurement that would change what anyone does.
- The paper reports exception rates by journal with some above 50% and some below 20%.
  Given ICC 0.435 and 130 repositories producing all successes, most of those journal
  differences are one-repository differences. Recomputing them at repository level is a
  small job and would probably delete a table.
