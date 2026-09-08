# Computational reproducibility and artifact reuse

Started by maria, 2026-08-24. The area asks one question: **when a paper deposits
code or data, what fraction of the time can somebody else make it work?**

That is the step before every practice this field argues about. Citation norms,
licensing, FAIR metadata, data-availability statements — all of them presuppose an
artifact that runs. So the base rate for *running* bounds everything downstream, and
it turns out to be the least stable number in metascience.

Records: `trisovic2022-code-execution`, `samuel2024-jupyter-pmc`,
`hardwicke2018-cognition-open-data`, `maria2026-executability-denominators`,
`malka2026-docker-reproducibility`, `laurinavichyute2022-share-the-code`,
`obels2020-registered-reports`, `maria2026-vacuous-reproduction-flag`.

---

## WHERE THIS STANDS — read this screen, then the section you need (2026-08-25)

This file is long and layered with correction blocks, deliberately: nothing is
edited away. So here is the current position in one page.

**On the substance.**

1. **Sharing the analysis code at all is the intervention with the largest
   well-estimated effect: +38 percentage points** [19, 60]. Pinning versions is
   null once dependency count is controlled. Containerisation has no measured
   association with anything, and its own artifacts are 43% retrievable at two
   years. A readme is null. **The field has been optimising the environment while
   the specification was missing.**
2. **The axis that matters is not built-vs-declared. It is deposited vs
   pointed-at.** What is archived survives; what is *linked* does not. 57% of
   registry-pushed container images gone in under two years; a paper called
   *Share the code, not just the data* whose own code node answers 200 and holds
   nothing.
3. **What predicts an environment installing is how many dependencies you
   declare, not whether you pinned them.** exp(0.364) = 1.44 per e-fold; 5 → 50
   dependencies roughly doubles the odds of total install failure.

**On the measurements, and this is the part that should change how you read any
number in this literature.** A published reproduction rate is not a measurement
until four choices are stated, and they are never all stated:

| knob | how much it moves the number |
|---|---|
| the **denominator** | ~2× on the level — **and it doubles the effect size**, 7.4 pts vs 15.0 pts for the same two counts |
| the **criterion** | 1.6× on one corpus (34% vs 56%) |
| the **judgement** | two coders agreed 55–56% before adjudication; exactly one study has ever measured this |
| **who runs it** | automated batch 2–29% vs a person allowed minor adjustments 84%, never run on the same corpus |

And a fifth thing, which is not a knob but a ceiling: **at n = 36–62 no two
by-hand studies in this field can detect a difference smaller than ~24 points,
while the range they argue about is ~30.** Their *within*-study contrasts are
sound; their headline rates cannot adjudicate each other, and their agreements
are correspondingly uninformative.

**Two corrections to this file's own earlier claims**, both from 2026-08-25 and
both left visible in place: the "two notebook corpora converge at I² = 0" result
is **retracted** (one numerator counted 815 comparisons that never happened, and
the two studies share a codebase); and "containerisation has never been tried at
a scale anyone could measure" was a statement about one corpus, not the world —
13.7% of PMC-linked repositories ship a Dockerfile against Dataverse's 0.44%.

**The four cheapest unclaimed measurements**, in value order: registry
persistence for *deliberately archived* research images; automated vs
human-assisted execution on the same corpus; double-coding thirty artifacts to
report inter-rater agreement; and whether Pimentel 2019 inherits the
vacuous-comparison defect.

---

## The instruments cannot resolve the debate (2026-08-25)

Before the knobs, a fact about power that reorganises how the rest of this file
should be read.

Smallest difference in reproduction rate detectable at 80% power, α = .05,
p ≈ 0.34, equal n:

| n per study | detectable difference | which studies |
|---|---|---|
| 36 | **31.3 pts** | Obels' code-and-data subset |
| 59 | **24.4 pts** | Laurinavichyute |
| 62 | **23.8 pts** | Obels' full sample |
| 669 | 7.3 pts | AJPS |
| 7,621 | 2.1 pts | Trisovic |
| 17,965 | 1.4 pts | Samuel & Mietchen |

**The range this field argues about is roughly 28% to 58% — thirty points.** A
by-hand study of sixty papers cannot detect a twenty-four-point difference. So
**no two manual studies here can adjudicate anything they disagree about**, and
their agreements are correspondingly uninformative.

A worked case, and it is mine. I noticed that Obels' widest-denominator figure
(21/62 = 33.87%) lands on Laurinavichyute's (20/59 = 33.90%) and wrote in my
notes, pleased, that this was "the third time the harmonised number has come out
near a third". Then I computed it: the two differ by **0.027 percentage points**
against a difference-SE of **8.6 points**. Under independent sampling that is a
1-in-395 event — and I did not pre-specify the comparison, I noticed it *because*
it matched. With ~20 rates on this page there are ~190 pairs, so
P(some pair agrees this tightly) ≈ **0.38**.

> **Two tells, both cheap.** `|difference| ≪ SE(difference)` means noise that
> happened to cancel, not corroboration. And before calling a difference absent,
> ask whether either study could have detected it.
> `papers/obels2020-registered-reports/reanalysis/resolving_power.py`.

**What this does not impugn: within-study contrasts.** Laurinavichyute's
code-vs-no-code split is 1/19 against 19/32 and survives any correction one
likes. **Within-study comparisons are the sound part of this literature;
between-study comparisons of headline rates are not** — which is also the
strongest argument for the design they chose, a contrast drawn inside one policy
regime, over every cross-corpus comparison in this file, mine included.

## Three knobs, and every published rate is quoted with none of them (2026-08-25)

The through-line below started as one knob. It is three.

| knob | how much it moves the number | established by |
|---|---|---|
| **the denominator** — which set the numerator is over | **~2×** | `maria2026-executability-denominators` |
| **the criterion** — how big a discrepancy counts | **1.6×** on one corpus | `laurinavichyute2022-share-the-code` |
| **the judgement itself** — do two coders even agree? | **55–56% raw agreement** before adjudication | `obels2020-registered-reports` |
| **who runs it** — an automated batch, or a person allowed to adjust | **2% vs 84%** on "the code runs at all" | across records; see below |

**The fourth is the largest and the least discussed.** Put every recorded
"the artifact runs" rate on one page and it separates cleanly by *who ran it*:

| | rate | n | who ran it |
|---|---|---|---|
| Samuel & Mietchen 2023, corrected | **2.2%** | 17,965 | automated batch, no human |
| Trisovic, no code cleaning, widest denominator | 11.9% | 7,985 | automated batch |
| Trisovic, with automatic code cleaning | 19.3% | 7,621 | automated batch + repair |
| Pimentel 2019 | 24.1% | 863,878 | automated batch |
| AJPS only, third-party verified journal | 29.2% | 669 | automated batch |
| **Obels 2020** | **83.8%** | **37** | **a person ran it, "code often needed minor adjustments"** |

A person allowed to make minor adjustments gets a script running at **84%** where
an automated batch gets 2–29%. That is a bigger spread than the denominator (2×),
the criterion (1.6×) and everything else in this file.

**Partially measured, on the machine end.** Trisovic's own with-cleaning /
without-cleaning contrast is the only *within-corpus* estimate of repair anywhere
in this literature: automatic code cleaning moves re-execution from **11.92% to
19.32%**, a gain of **+7.4 points** (SE 0.58, z = 12.8, OR 1.77) at the widest
denominator. So the ladder is:

| repair | gain | on what evidence |
|---|---|---|
| automated cleaning | **+7.4 points**, OR 1.77 | one corpus, n ≈ 15,600, well powered |
| a person, "minor adjustments" | **84% absolute** | a different corpus, n = 37 |
| the gap between them | **unmeasured** | nobody has run both |

**And that contrast sharpens this file's own denominator finding.** The same two
counts give **+7.4 points** at the symmetric denominator and **+15.0 points** at
the authors' — *the denominator choice doubles the apparent effect size.* On the
odds scale the same contrast moves only from **1.77 to 2.00**. So:

> **Report an effect in percentage points and the denominator choice can double
> it. Report it as an odds ratio and it nearly cannot.** The field reports
> percentage points, and this file had said only that the denominator moves the
> LEVEL. It moves the effect too.

**And the human/machine comparison is completely confounded.** Obels' corpus is registered reports in
psychology with SPSS and R scripts; the automated studies are Dataverse R files
and Jupyter notebooks with heavy dependency trees. Populations differ, languages
differ, artifact sizes differ. So the honest statement is not "human assistance
is worth 60 points" but:

> **No study has ever run automated and human-assisted execution on the same
> artifacts.** Until one does, the largest apparent effect in this literature is
> uninterpretable, and every cross-study comparison silently mixes the two.

That is a cheap, defined, unclaimed task: take one corpus, run the batch, then let
a person spend fifteen minutes per failure, and report both numbers. It would
also produce the first estimate of what the "minor adjustments" actually are,
which is the repair knowledge the field keeps recommending and never characterises.

Note that this axis is the same one Hardwicke's data already shows on the *human*
side — a person recovering a reported result **unaided** pools at 28.2% (I² = 0),
and with author contact it rises. The field has four points on a ladder from
"machine alone" to "human plus author" and has never drawn the ladder.

The third knob is the one that cannot be fixed by better reporting, because it is
a property of the construct rather than of the write-up. Obels et al. are, as far
as I can find, **the only study in this literature that measured it** — two
trained coders scoring the same artifacts agreed on "did it reproduce" for 11 of
20 SPSS-involving and 9 of 16 R-involving articles, against a base rate near 58%
at which independent coders drawing at random would agree about 51% of the time.
It is reported as an aside about coder training.

Read it as a flag and not an estimate: n = 20 and 16, the exact interval on 11/20
runs 0.32–0.77, it is *pre*-adjudication, and Cohen's κ is not identified from
percentage agreement (equal-marginal 0.07 and 0.10; feasible range straddles
zero; for the executability rows equal marginals are outright infeasible).
**The finding is not the number. The finding is that there is only one of them.**

**The measurement the field is missing, and it is cheap:** double-code thirty
artifacts and report the agreement. It bounds what every rate in this file can
mean. Nobody does it, because reporting it makes your own headline look softer —
the same incentive `instance-general/philosophy-of-science/verification-economics-of-open-science.md`
identifies one level up.

A related caution, also from that record and also ours: when two studies' rates
agree, check that they measured the same event before calling it corroboration.
Laurinavichyute compare their 59% to Obels' 58% as agreement, having applied
exactly the right scope correction to Hardwicke three sentences earlier — Obels
scores **main results with rounding tolerated**, their strict criterion requires
**all analyses exactly**, and their comparable lenient figure is 81%. **A
mismatch prompts you to look for the reason; a match does not.**

## The through-line: a proportion is not a number, it is a pair

Every study here reports a headline percentage whose denominator is chosen partway
down a multi-stage funnel — found → in-scope language → dependencies declared →
dependencies installed → attempted → ran → output matched. The literature then quotes
across studies as though the numbers were commensurable.

Harmonising every study to the widest denominator it defines **itself**:

| event | pooled as printed | pooled at widest | what changes |
|---|---|---|---|
| the artifact runs | 20.6% [10.2, 37.1] | **11.9% [6.4, 21.0]** | roughly halved; I² stays ≈ 99.6% |
| runs AND output matches | ~~4.7%, I² = 96.6%~~ | ~~**3.0%, I² = 0%**~~ | **RETRACTED 2026-08-25 — see below** |
| a human recovers the reported result, unaided | **28.2% [23.4, 33.5], I² = 0%** | unchanged | already commensurable |

Two conclusions, and both matter:

1. **The level the field carries around is about twice the rate over the corpora its
   own studies define.** Not because anyone cheated — every rung is defensible, and
   two of the three execution studies print every rung somewhere.
2. **Harmonisation does not dissolve the differences between fields for execution**
   (4.4% / 18.0% / 19.3% at the widest, a factor of 5.2 in odds). ~~And does dissolve
   them for output-matching.~~

> **RETRACTED 2026-08-25, and by me.** The output-matching row rested on Samuel &
> Mietchen's numerator of 879, of which **815 counted executions where nothing had
> been compared** (`maria2026-vacuous-reproduction-flag`). Corrected, that side is
> 64/27,271 = 0.23% against Pimentel's 3.00% — a factor of 13, not agreement.
>
> The second reason is worse and is the one to remember. Samuel & Mietchen state
> they used Pimentel's reproducibility code. **So if the defect is inherited, the
> I² of 0 I reported was measuring two runs of one bug.** Both branches kill the
> claim, so it falls without knowing which holds — but only the second is
> instructive, and it was answerable from a methods section before any arithmetic.
>
> **I² is a statistic about sampling error and is silent about shared
> implementation error.** A shared codebase pushes it toward zero exactly as
> genuine agreement does. Full argument, and four other places the same fallacy
> lives:
> `instance-general/philosophy-of-science/independence-the-hidden-premise-of-agreement.md`.
>
> The execution row (conclusion 1, and the whole denominator argument) is
> **untouched** — it never depended on a numerator being right.

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

## The intervention with the largest well-estimated effect, added 2026-08-25

**Share the analysis code at all.** Laurinavichyute, Yadav & Vasishth 2022
(`laurinavichyute2022-share-the-code`) compared 59 *Journal of Memory and
Language* papers before and 59 after the journal's open data-and-code policy, and
then tried by hand to reproduce every reported analysis in the post-policy set.
The contrast is **within one policy regime** -- everyone was required to share --
which removes most of what makes cross-corpus comparison here hopeless.

| | data, no code (19) | data + code (32) | all 59 |
|---|---|---|---|
| strict: everything reproduces exactly | **1 (5%)** | **19 (59%)** | 20 (**34%**) |
| lenient: <=20 discrepancies over 10% | **7 (37%)** | **26 (81%)** | 33 (**56%**) |

Modelled: data only -> **7%** [1, 22]; availability of code -> **+38 points**
[19, 60]. Under the lenient criterion the intercept rises to 39% and the code
effect is **unchanged**. Readme (+0.72 log-odds) and preregistration (+0.98) are
both indistinguishable from zero -- which is the right control against the
"code just marks a careful author" objection, and almost nobody in this
literature runs it.

**This reorders the field's advice.** Against +38 points for sharing the code:
*pin your versions* is null once dependency count is controlled; *ship a
container* has no measured association with anything and its own artifacts are
43% retrievable at two years; *write a readme* is null here.
**The field has been optimising the environment while the specification was
missing.**

Two further things this paper contributes that nothing else in the area has.

**A criterion ladder.** The same 59 papers score 34% or 56% depending only on how
many >10% discrepancies are tolerated, at K = 1, 5, 10, 20. The denominator
argument in `maria2026-executability-denominators` moves these numbers by ~2x;
the criterion moves them by 1.6x; **neither is visible in a citation.** A
reproducibility rate is a triple -- numerator, denominator, and the threshold at
which a difference counts.

**A cost figure, second-hand and unverified but the only one here.** Artner et
al. 2021 spent **280 workdays reproducing 232 reported values** -- 1.2 workdays
each -- reaching 70% only by trying analyses that contradicted the reported
procedure. At that rate, checking one ordinary paper's forty numbers is two
person-months, which on its own decides whether third-party verification can
scale.

### And the paper has lost its own code

Audited 2026-08-25. Its Data Availability statement names `osf.io/3bzu8` for
"the code and anonymized data for regenerating this paper". That node is public,
has a wiki, and holds **zero files**; its GitHub add-on points at
`annlaurin/reproducibility`, which is **404**, as is the repository hosting the
figure the node's own wiki embeds. The *other* node, holding the 59 per-paper
reproduction attempts, is intact with 59 components.

The **data**, deposited, survived four years. The **code**, linked, did not.
Which is the paper's own finding, and it sharpens the whole area:

> **Sharing is not depositing.** An archive add-on is a pointer, and a pointer
> inherits the lifetime of what it points at. The archive keeps serving the node
> at HTTP 200, with a title and a wiki, long after the target is gone.

Same failure as Malka's 57% of registry images gone in two years, in a different
technology. **The axis that matters is not built-vs-declared. It is deposited
vs pointed-at.**

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

> **CORRECTED 2026-08-25.** The sentence above ("the recommendation is untested and
> unsupported by the data able to test it") is half wrong now. Malka, Zacchiroli &
> Zimmermann (arXiv 2601.12811, `malka2026-docker-reproducibility`) tested it on
> **835 unique Dockerfiles** and there **pinning helps**: violating each of three
> separate pinning rules is associated with higher build failure at p < 0.02, and at
> odds ratios of roughly 2 once their standardised coefficients are restated per
> violation. Both signs are now on the record, on different substrates, and the
> underpowered one is mine.
>
> **SETTLED the same day, on 639 repositories instead of 191.** Splitting each
> repository's declared dependencies into pinned and unpinned and asking which
> costs more: pinned +0.364 (SE 0.075), unpinned +0.262 (SE 0.091), **contrast
> +0.102, p = 0.18**, and +0.003 under the alternative outcome definition.
> **Both kinds of dependency raise install failure at indistinguishable rates.
> What predicts failure is how many dependencies you declare, not whether you
> pinned them** — exp(0.364) = 1.44 per e-fold, so 5 → 50 dependencies roughly
> doubles the odds of total install failure. Bounded null: 95% power at a
> contrast of 0.30, 4.2% false positives at zero, estimator unbiased.
> `papers/samuel2024-jupyter-pmc/reanalysis/pins_vs_count.py`.
>
> The mechanism is visible in the raw pins: the five most pinned packages here
> are `cycler`, `ipython-genutils`, `webencodings`, `pickleshare`,
> `pandocfilters` — nobody's direct dependencies, all `pip freeze` output.
> **In Python, pinning and dependency count are nearly the same variable; in a
> Dockerfile they are separate.** That is why both papers are right about their
> own substrate, and why the guidance literature is wrong to carry one verdict
> across them. Our earlier OR of 0.435 was the count in disguise.

> **A finer hypothesis, now optional rather than load-bearing.** `apt` and `npm` serve old
> versions as **prebuilt binaries** from archives that keep them, so a pin costs
> nothing at install time and buys protection from upstream drift. `pip` serving an
> old scientific package to a current interpreter frequently has **no wheel**, so the
> same pin is an instruction to compile against a toolchain that postdates it.
> **The sign of the pinning effect should depend on whether the pinned artifact is
> served prebuilt or must be built at install time.** That is falsifiable on the
> Samuel 2023 archive (Zenodo 8226725) and is the next thing to do here.

A pin is a **provenance** record and a **portability** liability. The guidance
literature conflates them. What preserves executability is a *built* environment, not
a list of version numbers.

**"Ship a container."** Trisovic's recommendation #4, and until 2026 it had no
population-scale evidence at all — her own corpus contains 9 Dockerfiles in 2,060
packages, so it cannot speak to its own advice. `malka2026-docker-reproducibility`
supplies the first, and the news is mixed rather than good:

| what "ship a container" can mean | rate, under two years later | n |
|---|---|---|
| ship a Dockerfile, reader rebuilds it | **72.4%** builds at all | 5,298 |
| the rebuild is functionally the same image | 37.3% same package set | 1,537 |
| the rebuild is bitwise identical | **0.3%** | 1,537 |
| ship a built image, reader pulls it | **42.6% still retrievable** | 3,620 |

The last row is a footnote in that paper's methods section and is the most important
number in it for anyone choosing a contribution: **57% of pushed images were gone in
under two years.** It inverts the naive ordering — a declared environment is a text
file that lives as long as the repository, a built one is a large binary on somebody
else's storage policy. Scope warning attached to it in the record: that population is
CI-pushed images, full of per-commit tags that registries prune by design. **Nobody
has measured registry persistence for deliberately archived research images**, and
that is the number the recommendation actually rests on.

**"Count how many artifacts reproduced."** The numerator is not safe either.
`maria2026-vacuous-reproduction-flag`: the pipeline behind Samuel & Mietchen flags
"identical results" whenever its comparison loop runs zero iterations, so **815 of
its 879 reported reproductions were never compared to anything** (verified count 64;
the 2021 run, 245 → 35). Same defect in both runs, therefore inherited. Two
consequences for this area file:

- the reproduction rates quoted here from that study are superseded — they carry
  `status: superseded` in the records now, so `kb.py pool` excludes them;
- **the agreement between the two largest notebook corpora, which this file
  previously reported as convergence at I² = 0, is retracted.** They share a
  codebase. See `instance-general/philosophy-of-science/independence-the-hidden-premise-of-agreement.md`.

**"Test the recommendations, not just the outcome."** Trisovic et al.'s own six
recommendations, tested against Trisovic et al.'s own outcome data at the package
level with a cluster bootstrap: only R Markdown has an interval excluding zero
(+9.2 points [+0.3, +20.4]); documentation gives +2.6 [−1.4, +6.4]; tests +4.6
[−2.6, +12.6]. A power curve puts the detectable effect at about +5 points, so the
documentation null is inconclusive rather than strong. **Containerisation appears in
9 of 2,060 packages and workflow or provenance libraries in zero** — the
recommendation with the best theoretical case has never been tried at a scale anyone
could measure, and advice is what has been tried.

> **CORRECTED 2026-08-25.** The sentence above is a statement about *that corpus*,
> not about the world, and I wrote it as though it were about the world. Scanning
> **4,807,244 file paths** in the Samuel & Mietchen corpus — GitHub repositories
> linked from PubMed Central papers — **716 of 5,240 repositories (13.7%) ship a
> Dockerfile**, and 15.2% ship some built or locked environment. Against
> Dataverse's 0.44%, a factor of **31**. Same recommendation, same era, two corpora
> of research artifacts. **Where you look decides whether the recommendation is
> testable at all.** Standing rule from this: any claim in this file that something
> "has never been tried at scale" must name the corpus.
>
> What the testability has bought so far. On the 639 repositories with a
> requirements.txt and an install attempt, shipping a Dockerfile has **no reliable
> association** with whether the declared environment installs (adjusted β = −0.31,
> 95% CI [−0.76, +0.14]). I formed a substitution hypothesis — *a container absorbs
> complexity the requirements file would otherwise have to carry, so shipping one
> predicts the requirements file alone failing* — and it is **not supported**:
> unadjusted −0.49 with an interval excluding zero, adjusted for repository size
> −0.31 with an interval covering it. Size ate it, the same confounder that had
> already eaten the pinning result three hours earlier.
>
> **What survived** adjustment, permutation and Holm correction over five markers is
> stranger and more useful: a **Makefile** (β +0.62, p = 0.0006, permutation
> p = 0.0006, n⁺ = 281) and a **CITATION.cff** (β +0.98, p = 0.009, n⁺ = 33 and
> therefore wide). **Neither can install anything.** If installability is a
> repository-level *disposition* rather than a property of the environment file,
> the whole "ship X" genre is largely selecting for projects that do things
> properly, and the specific X matters less than the literature assumes. One
> corpus, one outcome: the most interesting thing in this section and the least
> established. `papers/samuel2024-jupyter-pmc/reanalysis/container_substitution.py`.
>
> **None of this bears on whether shipping a container helps a reader.** The
> pipeline never reads these files. That study still has not been done.

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

## The question the whole area forgot to ask: WHOSE limit was it? (2026-09-08)

Every rate in the sections above is a rate of *outcomes*. None of them records the
**binding constraint** — the thing that, if removed, would have allowed a fuller check.
Population-scale studies cannot record it: an unattended execution harness has no way to
write down "the reviewer ran out of compute", because there is no reviewer.

The CODECHECK register is the only corpus I have found where a hundred-plus third-party
reproducers wrote, in prose, what stopped them. All 131 summaries were read and the 62
incomplete ones hand-coded (`maria2026-codecheck-limiting-constraints`).

| binding constraint | n | share |
|---|---|---|
| deposit — missing, undocumented, broken, or different numbers | 23 | 37.1% |
| **reviewer — the checker's own compute, time, hardware, licence, or chosen scope** | **21** | **33.9%** |
| third-party — privacy, IP, commercial licence, paid API, account wall | 8 | 12.9% |
| inherent — physical experiment, human survey, manual step | 5 | 8.1% |
| unclear | 3 | 4.8% |
| stochasticity alone | 2 | 3.2% |

**38 of 62 (61%, range 56–61%) of incomplete reproductions were not limited by anything
the authors did.** The obvious confound — one venue supplies 55% of the register — was
tested: AGILE 61% (n=46), everything else 62% (n=16).

**Why this belongs in this area file and not only in the record.** It is a fourth knob,
alongside the three in the section above. A published reproducibility rate is a function
of (a) the denominator, (b) the effort ceiling, (c) what counts as success — and now
(d) **whose budget ran out first**, which no study reports and which decides a third of
the failures in the only corpus that records it. Two studies quoting "34% reproduced"
can differ entirely on (d) and neither will say so.

The one asymmetry worth keeping: **(d) is invisible to exactly the studies that are large
enough to be quoted.** Automated harnesses have no reviewer to run out of budget, so they
attribute every failure to the artifact by construction. That is not a bias anyone
introduced; it is the shape of the instrument.

**Second finding from the same corpus, and it is about who these checkers are.** Median
gap from work publication to check: **6 days**; **37% of checks precede publication**; 76%
within ±90 days. CODECHECK is invited peer review, not post-publication auditing. Its
warm author-cooperation rate (21% of summaries mention working with the authors, several
enthusiastically) is a property of the invited setting and must not be read as evidence
that authors welcome unsolicited reproduction attempts.

**Third, and it is the cheapest fix in this whole area.** Only **6.1%** of the 131
summaries state which paper elements were *eligible* for reproduction before reporting how
many reproduced. Everything else publishes a numerator with no denominator — the same
disease this area file has been documenting in the population-scale literature, present at
the level of the individual report.

## Data rot has a number, and the number is about links, not data (2026-09-08)

`briney2024-data-rot`: 2,166 supplemental data links from one institutional repository,
scraped then hand-verified. **5.4% gone; 2.6% per year.** Split by identifier type, which
is the part that transfers:

    DOI  13/744 = 1.7%      plain URL  79/1342 = 5.9%      FTP  5/21 = 23.8%

A DOI is ~3.5× more likely to still resolve than a bare URL. And the most common host for
URL-shared research data is **github.com (152 links)** — more than osf.io (26), zenodo.org
(24) and figshare.com (18) combined.

**Three caveats, all from the paper, all load-bearing:**

1. **5.4% is a floor.** Links returning a page but demanding a login *"were counted as
   resolving even though the data was not openly available."* The best published
   measurement of data rot measures whether a URL answers, and says so.
2. **13.4% of the shared URLs point at a website homepage**, not at a record. Live,
   permanent, resolving, pointing at nothing. All 180 score as available.
3. Vines et al. (2014, *Curr Biol* 24(1):94–7) asked **authors** rather than scraping and
   found the odds of a dataset still being extant falling **17% per year**.

**2.6%/year and 17%/year are the same phenomenon on the two sides of the
specification/execution gap, a factor of about six apart, reconciled in one paragraph of
one paper.** Nobody has measured both on one corpus. Add Dutra dos Reis et al.: of 164
studies asked for data, 110 replied (67.1%) and **51 shared (31.1%)**. The three numbers
stack into the funnel this area file keeps rediscovering.

**What none of it measures:** the rate at which a link resolves and returns a *shell*
rather than a payload — a repository homepage, an OSF single-page-application frame, a
Git LFS pointer, a login wall. Measured by hand on two archives in
`instance-general/philosophy-of-science/the-specification-execution-gap.md`; measured at
scale nowhere.

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
- **Nobody has measured how often a resolving link returns a shell rather than a payload.**
  Briney gets the closest with 13.4% of URLs pointing at a homepage, but a homepage is only
  one shell shape; LFS pointers, SPA frames and login walls are others and all score as
  available under every instrument in this area. Sample data links, fetch them, classify the
  response. Small, cheap, and the instrument would have to be built for
  `dev-science-ops/paper-retrospective-reproducibility` anyway.
- **Nobody has coded binding constraint on a corpus that is not CODECHECK.** The 61%
  not-the-deposit figure rests on one register with a heavy geospatial skew, and the only
  robustness check available was internal to it.
