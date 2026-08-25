# Laurinavichyute, Yadav & Vasishth 2022 — *Share the code, not just the data*

Read 2026-08-25 by maria, from the PsyArXiv preprint (the published version is
Elsevier and paywalled). Methods and results read in full; the artifact audit is
mine and is the part of this record that is not in the paper.

---

## 1. Why this paper matters more than its citation count suggests

My area file has, for three weeks, converged on one sentence from two independent
directions — Trisovic's re-execution of 9,078 R files and Hardwicke's coding of
1,324 reported values in *Cognition*:

> **In both halves the materials are preserved and the executable specification
> is not.**

This paper is that sentence tested directly, prospectively, on a third field, by
a fourth team, with a fifth method. It compares 59 papers before and 59 after the
*Journal of Memory and Language* introduced an open data **and code** policy, and
then tries to reproduce every reported analysis in the post-policy set by hand.

The design has something none of the others has: **the contrast is within one
policy regime.** Everyone in the post-policy group was required to share; the
comparison is between those who also shared code and those who did not. That
removes most of what makes cross-corpus comparison in this area hopeless.

## 2. The numbers, with every rung printed

| | data, no code (19) | data + code (32) | all 59 surveyed |
|---|---|---|---|
| strict — everything reproduces exactly | **1 (5%)** | **19 (59%)** | 20 (**34%**) |
| ≤5 discrepancies over 10% | 3 | 22 | |
| ≤10 | 4 | 23 | |
| ≤20 (most lenient) | **7 (37%)** | **26 (81%)** | 33 (**56%**) |

Two things to take from the table rather than from the abstract.

**The criterion moves the headline by a factor of 1.6** — 34% to 56% — on
*exactly the same set of attempts*. My own synthesis showed the *denominator*
moving these numbers by about 2×. Here is a second, independent knob, and neither
is visible in a citation. A "reproducibility rate" is a triple: numerator,
denominator, and the threshold at which a difference counts.

**The code effect is enormous and stable across the knob.** Bayesian logistic
regression, 51 papers, regularising priors:

- data only, no code, no readme, no preregistration → **7%** [1, 22]
- availability of code → **+38 points** [19, 60]  (log-odds 2.49, SE 0.76, OR 12.1)
- readme → 0.72 [−0.47, 1.93], **indistinguishable from zero**
- preregistration → 0.98 [−0.96, 3.01], **indistinguishable from zero**

Under the most lenient criterion the intercept rises from 7% to 39% and the code
effect is **unchanged at +39 points** [14, 60]. An effect that survives moving the
outcome definition that far is not an artifact of where the line was drawn.

**Why the readme and preregistration nulls matter more than they look.** The
obvious objection to c3 is the one that bit me tonight on a different corpus:
people who share code are more careful, and you are measuring care. The authors
modelled two other care markers and both came out null. That is not
identification, but it is the right control, and almost nobody in this literature
runs it. Set against my own finding earlier today — that a Makefile and a
CITATION.cff predict whether declared dependencies install, while the environment
files do not — the honest position is that care is real and code is doing
something beyond it.

**And it reorders the field's advice.** Against +38 points [19, 60] for sharing
the code at all:
- *pin your dependency versions* — null once dependency count is controlled
  (`samuel2024#c6`, contrast +0.10, p = 0.18, bounded);
- *ship a container* — no reliable association with anything measured, and its
  own persistence is 43% at two years (`malka2026`);
- *write a readme* — null here.

**The field has been optimising the environment while the specification was
missing.**

## 3. The audit: this paper has lost its own code

The Data Availability statement names two OSF nodes. I checked both, and the
result is the paper's own finding instantiated on the paper.

**`osf.io/3bzu8` — "the code and anonymized data for regenerating this paper".**
Public. Last modified 2022-04-18. Wiki present. **Zero files in OSF storage.
Zero child components.** Its provider list includes a `github` add-on whose
configured target is `annlaurin/reproducibility:` — and
`github.com/annlaurin/reproducibility` returns **404**. So does
`github.com/annlaurin/images`, which hosts the river plot the node's own wiki
embeds. The account is alive with six unrelated public repositories and a
user-scoped GitHub search for "reproducibility" returns nothing, so this is not a
rename a reader could follow.

**`osf.io/3x2y6` — the 59 per-paper reproduction attempts.** Intact. Three files
in OSF storage and **59 child components**, one per surveyed paper, exactly as
described.

`reanalysis/audit_osf_artifacts.py` re-runs the whole thing in one command.

### Why this is evidence *for* them, not against them

It would be cheap to score a point here and it would also be wrong. Look at what
survived and what did not:

- the **data** — deposited into OSF — is fine after four years;
- the **code** — *linked* from OSF to a mutable repository — is gone.

That is precisely the mechanism the paper identifies, operating on the paper. And
it adds a distinction the authors do not draw and which I now think is the
practical core of the whole area:

> **Sharing is not depositing.** An archive add-on is a *pointer*, and a pointer
> inherits the lifetime of whatever it points at. The archive will keep serving
> the node, at HTTP 200, with a title and a wiki, long after the thing it points
> at is gone.

Same failure, different technology, from `malka2026`: **57% of Docker images
pushed to a registry were gone in under two years.** In both cases the artifact
that was *archived* survived and the artifact that was *referenced* did not. The
axis that matters is not built-vs-declared. It is **deposited vs pointed-at.**

### And it is a check my own tooling would have failed

`kb.py links`, which I wrote this morning, asks whether a URL answers.
`https://osf.io/3bzu8/` answers 200. It would have scored this artifact as alive.
Recorded as an open question against that command, because a checker that can
only be fooled in ways I have already catalogued is not finished.

That makes **five** distinct ways HTTP lied about an artifact today: publisher
anti-bot 403; a GitHub page answering while its LFS objects do not; a bucket
prefix 404ing because it is not a file; an `osf.io` soft-404 returning 200 with a
4 KB error page — the same 4,207 bytes I met again fetching this very preprint
from the wrong URL — and now an archive node that answers, has a title, and holds
nothing.

## 4. One number I did not verify and am keeping anyway

The discussion reports that **Artner et al. (2021) spent 280 workdays reproducing
232 reported values**, reaching 70% only by trying analyses that conflicted with
the reported procedure. That is **1.2 workdays per reported value.**

Second-hand, so recorded `unverified`. I am keeping it because the *cost* side of
verification is almost absent from my area file, and at that rate checking one
ordinary paper's forty numbers is two person-months — which decides, on its own,
whether any third-party verification scheme can scale. If it survives checking it
is one of the most consequential numbers in the field.

## 5. What I did not do

- Did not read the published Elsevier version; it is paywalled and may name other
  artifact locations. Everything in §3 is against the preprint's statement.
- Did not re-run their analysis. The code that would be re-run is the thing that
  is missing, which is the finding.
- Did not open the 59 components of `osf.io/3x2y6`. Their existence and count are
  verified; their contents are not.
- Did not contact the authors. Whether to tell them their code node is empty is
  not a decision I take alone; it is the same question mark has been designing a
  process for, and this is a good first case for it — small, exact, and entirely
  in their interest.
