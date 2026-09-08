# gamma2024-mpe92m-correction

A four-kilobyte PLOS correction notice, and the reason it has a record of its own.

## What it says

Verbatim, from the JATS manuscript retrieved 2026-09-08:

> The Data Availability statement for this paper is incorrect. The correct statement is: The data,
> documentation and all language versions of the MPE-92M questionnaire are publicly available as a
> ZIP-file on the Open Science Framework website. URL: https://osf.io/xerhg/download

That is the whole notice. No result, table, figure or number in the 2021 article is amended.

## Why a record exists for a correction notice

Because this house did not know it existed, and the cost of not knowing was concrete.

`gamma2021-mpe92m` was read in depth in July 2026, re-analysed through August, and its artifact `a3`
-- the dead `osf.io/gb76x` printed in the 2021 Data Availability statement -- was re-checked on
2026-08-25 and recorded as a live problem, with a paragraph explaining why it is a soft-404 worth
recording. It **is** dead. The authors published the fix on 2024-11-18. Had anything from that
record been sent to them, it would have told two authors about a problem they had already corrected
in the literature.

The check that finds this costs **one HTTP request**:

```sh
curl -s "https://api.crossref.org/works?filter=updates:10.1371/journal.pone.0253694"
```

It returns exactly one item. The reciprocal query on the correction's own DOI returns zero, which is
the expected asymmetry and was run so that a zero could not be mistaken for a failed request.

## The second-order point, which is the useful one

The original deep read reached the **right** artifact (`xerhg`) by another route and never knew it
was the officially corrected pointer. Getting the right answer by the wrong method is not a smaller
error than getting the wrong answer, because it does not announce itself: had `xerhg` also been
moved, nothing in the method would have caught it.

## The corpus audit this prompted, and its uncomfortable half

The obvious next question -- *how many other records describe corrected papers?* -- was run the same
session, over all **29** of the 42 records that carry a DOI. Raw output:
`corpus_corrections_audit.json`.

| | |
|---|---|
| records queried | 29 |
| with at least one formal update | **2** (6.9%) |
| `breznau2022-hidden-universe` | Correction `10.1073/pnas.2410677121`, 2024-06-20 -- Fig. 1 corrected |
| `gamma2021-mpe92m` | Correction `10.1371/journal.pone.0314290`, 2024-11-18 -- Data Availability corrected |

**And the Breznau one was already known.** It was found on 2026-08-12 and recorded accurately as
artifact `a6`: *"Corrects Fig. 1 only; the corrected legend is what states the inverse-team-size
weighting. No numerical claim in the body changed."*

So the honest finding is not *the method never checks*. It is worse and more useful: **the method
checks when the reader happens to notice, which on this evidence is one time in two, and nothing
distinguishes the two cases except that PNAS puts the correction on the article page and PLOS does
not.** A practice that depends on a publisher's page layout is not a practice.

**Second, structural:** the one correction that *was* recorded went into `artifacts[]` with
`role: supplement`, because that was the only slot available. A correction is not a supplement.
The consequence is that `python tools/kb.py ...` cannot answer *"which papers in this corpus have
been corrected?"* -- the fact exists in the corpus and is unreachable by any query. See
`open_questions` for the schema proposal.

**Third, a gap nobody has touched:** 13 of the 42 records carry no DOI. Nine are our own reanalyses;
four are arXiv- or OpenReview-only, where withdrawal and status changes are entirely different
mechanisms with different endpoints. Those four have never been checked by anything.

## Provenance

Found on 2026-09-08 while retrofitting `gamma2021-mpe92m` into
`dev-science-ops/paper-retrospective-reproducibility/`, whose S0 stage performs a corrections check
that this knowledge base's own reading method did not. The retrofit's evidence is at
`retrofit/papers/gamma2021-mpe92m/probe/crossref_updates_query.json` and
`probe/correction_0314290.xml`; the full account is in `retrofit/FINDINGS.md`.
