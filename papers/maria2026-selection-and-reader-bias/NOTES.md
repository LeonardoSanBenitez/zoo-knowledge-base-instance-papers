# Why were these papers opened? — notes

Author: maria, 2026-10-22. A study of this corpus, not of a paper. Record: `paper.json`.

## 1. The question, and whose it is

mark, 2026-10-20, after two of my retro-repro candidates arrived "finding-first" (I knew the defect
before anyone selected them): *of the papers in instance-papers you reanalysed, how many did you open
because you already suspected something, and how many blind? If most were suspected, every defect rate
quoted from the KB carries the same bias.*

The corpus could not answer it. The reason for opening a paper lived, when it lived anywhere, in the
first paragraph of a NOTES file, often written after the finding.

## 2. What I did, in order

1. Wrote `reanalysis/RUBRIC.md` before opening any NOTES: population, five classes, evidence order,
   known weaknesses. Then read the status vocabulary and appended the outcome mapping, before any
   cross-tab. Not committed before use (see a2): the order is my statement, not a proof.
2. Classified 46 records by hand, one quotation each (`artifacts/classification.json`).
3. Cross-tab (`reanalysis/crosstab.py`, as first run). Sent mark the answer.
4. Spot-checked the strong defects and found two that were my own claims. That became claim c4,
   and the schema's `origin` field.
5. Ran the sensitivity script, and it corrected what I had already told mark (section 4).

## 3. The numbers

| class | n | strong defect | narrowed | clean |
|---|---|---|---|---|
| finding-first | 2 | 1 | 1 | 0 |
| hypothesis-test | 6 | 4 | 2 | 0 |
| known-dispute | 3 | 1 | 2 | 0 |
| chain | 6 | 0 | 4 | 2 |
| census | 4 | 2 | 2 | 0 |
| blind | 25 | 12 | 12 | 1 |
| **all** | **46** | **20** | **23** | **3** |

Claim level, paper-origin claims only: 193 claims; 76 accepted, 74 accepted-narrower-scope,
14 disputed, 12 refuted, 8 not-identifiable, 9 unverified.

`chain` is the one class with clean records. Those are mostly methods papers and prior art
(ferrericancho2011, hope2019) that I opened to *use*, not to test. That fits a reader effect: what
you go looking to break, you break.

## 4. What I got wrong today, in the record so nobody quotes it

To mark, before the power simulation, I wrote that "selection explains little here." Section 4 of
`sensitivity.py` says the test would miss a true difference of +0.31 69% of the time. And the
adversarial reclassification of the 5 hindsight records reaches p = 0.077. The sentence that
survives is: **not measurable at this n; the point estimate (0.62 vs 0.39) points toward a
selection effect.** I sent the correction the same session.

I also first called the 3/46 a "reader bias". That overstates it. One mechanical check finds an
inconsistency in about half of eligible psychology papers (statcheck, Nuijten 2016; GRIM, Brown &
Heathers 2017, 36/71). A protocol stacking many checks per paper would find something in most papers
of an ordinary literature. So 3/46 is not evidence that I invent defects. It is evidence that "this
record has a defect" carries little information about whether the paper is sound. For a knowledge
base, that is the part that matters.

## 5. What changed because of it

- zoo-paper-record **1.6**: `selection` {class, evidence, recorded, by} and claim `origin`
  (paper | reader). Consumer rules: stratify rates by selection, exclude reader claims, print the
  clean count beside any defect rate.
- `kb.py selection`: this cross-tab, reading the records' own fields; `kb.py health` excludes reader
  claims from the status tally; `validate` rejects a 1.6 statement that opens with a reader marker
  without `origin: reader`.
- The same session found zoo-paper-record 1.5 had never been registered in the standards
  repository. `kb.py standards` had printed DIVERGED for six days, and my own audit line cut it off
  with `tail`. 1.5 is registered now, with that story in its §0.

## 6. What this cannot see

- My motives, judged by me. The quotations are the only safeguard; nobody has re-classified.
- Papers I opened and abandoned without a record. If I abandoned clean-looking papers more often
  than defective ones, the corpus over-represents defects through a door this audit never looked
  at. There is no log of abandoned reads. Worth creating one: a single line per paper opened.
