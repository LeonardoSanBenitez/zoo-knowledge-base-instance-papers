# How to read a paper in depth, here

Author: maria, 2026-08-07. Written after a session in which I did this badly and
was told so. The failures are named below rather than hidden, because they are the
reason each rule exists.

This governs `instance-papers/`. Prose synthesis per research area stays in
`areas/`; every paper read in depth also gets a folder in `papers/<id>/`.

---

## 0. What counts as "in depth"

A bibliography entry is cheap. This is not, so it is reserved. The `read_depth`
field is the honest signal and it is enforced by nothing except your own report:

| depth | means |
|---|---|
| `abstract-only` | you read an abstract or a search result. **Never carry assessments.** |
| `skimmed` | you read the paper's structure. Claims may be recorded, all `unverified`. |
| `read-full-text` | you read the actual PDF, not a summariser's rendering of it. |
| `read-and-ran-artifacts` | you downloaded the code/data and executed something. |
| `read-and-reanalysed` | you produced a number the authors did not. |

**Prefer papers that ship artifacts.** Not because artifact-less work is worse, but
because the depth we can reach is bounded by what we can open, and a session spent on
a paper we can only paraphrase is a session that produces prose about prose.

## 1. Read the primary source, not a summary of it

A fetch-and-summarise tool gives you a paraphrase produced by a small model that did
not care about your question. Twice in one session it gave me generic text that was
partly invented; both times the PDF was already on disk and reading it directly gave
the actual theorems.

**Rule: if the PDF downloaded, read the PDF.** Use the summariser to decide whether to
download, never to decide what the paper says.

## 1b. Ask whether the paper has been corrected. One request. Do it first.

Added 2026-09-08, after this method read a paper in depth, re-analysed it across three
sessions, recorded a dead data link as a live problem — and never noticed that the
authors had formally corrected that exact link in 2024.

```sh
curl -s "https://api.crossref.org/works?filter=updates:<DOI>"
```

For `10.1371/journal.pone.0253694` this returns exactly one item: a **Correction**,
`10.1371/journal.pone.0314290`, PLOS ONE 19(11):e0314290, 2024-11-18, by the same two
authors, replacing the Data Availability statement and giving the working URL. The record
`gamma2021-mpe92m` had carried the dead URL as an open defect for twenty-two months after
the fix was published. Had anything from it been sent to those authors, it would have told
them about a problem they had already announced the answer to.

**Three things this rule requires, and each exists because skipping it is tempting:**

1. **Run the reciprocal query too** — `filter=updates:<the correction's own DOI>` — and
   expect zero. A single query returning nothing looks the same whether there is no
   correction or the request failed. Crossref returns HTTP 429 on back-to-back queries from
   a bare client; use a `mailto:` in the User-Agent and retry with backoff.
2. **Record the answer even when it is "none".** A record with no `updates` note is
   ambiguous between *checked and clean* and *never checked*. Put the query and its result
   in the artifact's `checked` block or in `open_questions`.
3. **Re-run it at `curation.verified` time**, not only at creation. A paper can be corrected
   after you read it, and the check costs one request.

**The base rate, measured the same day over this corpus.** The query was run against all
**29** of the 42 records carrying a DOI. **Two** have formal corrections — Breznau et al.
2022 (Fig. 1 corrected, 2024-06-20) and Gamma & Metzinger 2021 — a base rate of **6.9%**.
Raw output: `papers/gamma2024-mpe92m-correction/corpus_corrections_audit.json`.

**And the uncomfortable half.** The Breznau correction had *already* been found, on
2026-08-12, and recorded accurately. So this method does not never-check. It checks **when
the reader happens to notice, which on this evidence is one time in two**, and the only
visible difference between the two cases is that PNAS puts the correction on the article
page and PLOS does not. *A practice that depends on a publisher's page layout is not a
practice.* That is the argument for the rule, and it is a stronger argument than a simple
miss would have been.

**Where the recorded one went, and why that is a second problem.** The Breznau correction
is stored as `artifacts[]` with `role: supplement`, because that is the only slot the schema
offers. A correction is not a supplement. The consequence is that no `kb.py` query can
answer *"which papers here have been corrected?"* — the fact is in the corpus and is
reachable only by reading prose. A first-class `updates` field is proposed in that record's
`open_questions`; until it exists, put the answer in `open_questions` where at least
`kb.py query --text` will find it.

**Where this came from.** `dev-science-ops/paper-retrospective-reproducibility/` performs
this at its S0 stage. This method did not. The whole account, and eleven other things the
comparison exposed, is in that project's `retrofit/FINDINGS.md`.

**The second-order lesson, which is the one worth keeping.** The original read reached the
*right* artifact by another route and never knew it was the officially corrected pointer.
**Getting the right answer by the wrong method is not a smaller error than getting the wrong
answer, because it does not announce itself.**

## 2. Open the artifacts. All of them, separately.

A paper is not one link. It is typically several artifacts with different roles, different
health, and provenance edges between them: raw data, derived tables, code, human labels,
a benchmark it draws on, prompts, model weights. Record each one with its own `role`,
`status`, and — this is the field that does the work — a `checked` block containing the
**literal command you ran**. "I looked at the repo page" is not a check.

The two statuses nobody else records, and the two that matter most:

- **`present-but-insufficient`** — it is there, and it does not let you redo the
  analysis. Derived tables without the raw matrix. You can re-execute; you cannot
  re-decide.
- **`dangling`** — advertised and not retrievable. A Git LFS pointer whose object 404s.
  A dead OSF link. A repo that exists with an empty `data/`.

Both pass every artifact-badging scheme in existence. Both make reanalysis impossible.
The first paper recorded here has a dangling raw-data file and is otherwise complete —
`python tools/kb.py artifacts --status dangling` finds it in one command.

**Small-n fields keep their data in a PDF table.** That is a legitimate artifact
(`role: in-paper-table`), not a failure. Transcribe it into the paper folder, record
where it came from, and treat it as data. Psychology and clinical work do this
constantly and dismissing it is a computer-science provincialism.

## 2b. Ask what the design identifies BEFORE auditing the estimator

Added 2026-09-04, after doing it in the wrong order and noticing only at the end.

I spent a session dismantling a World Psychiatry paper's estimator of individual
treatment-effect variability: found a coupling artifact in all three of its
inputs, a headline estimator with no sensitivity to the quantity it names, a
deletion rule that manufactures the result from a null world, and finally an
algebraic identity showing the formula adds nothing to its own input. All of it
correct, all of it worth having.

Then I read Senn (2015), who shows in one table that **the quantity is not
identified by the design at all** — patient-by-treatment interaction is
confounded with between-patient and within-patient variation in every
parallel-group trial, and only replication within patients separates them.

The cheap question was available the whole time and I never asked it.

**Rule.** Before reanalysing a quantity, write down two lines:

    design that produced it:  ...
    what that design identifies: ...

If the target is not on the second line, the reanalysis is about **the
estimator's behaviour**, not about the world, and its first sentence must say so.
This costs one paragraph and it tells you where to point the expensive machinery
— and sometimes that the machinery is unnecessary.

**It does not make the audit worthless.** A design argument that has been in
print for a decade and has not moved a field will not move it on the eleventh
year either; showing that a specific published pipeline returns 14.9 units of an
effect from a world containing 0.0 of it is a different kind of object and it
travels further. Do both. Just do them in this order.

## 3. Try to break the result before you try to believe it

The order matters. The failure that cost me the most was believing an analysis
because it agreed with me:

> I built a null model, it reported that 93.8% of the effect was an artifact — which
> is what I already suspected — and I wrote it up. Then ten robustness strata all
> returned *exactly* 1.0000, and the estimator turned out to have algebraically zero
> power on any dataset. I had built an instrument that cannot detect what it measures.

Minimum before writing a number down:

- **Feed it a case where you know the answer.** Synthetic data with the effect forced
  in, and with the effect absent. If it cannot see 99% injected monoculture, it cannot
  see anything.
- **Check whether your "correction" is self-referential.** If the null is estimated
  from the same population you are testing, suspect an identity.
- **Suspicion trigger: agreement to four decimal places is not robustness, it is
  circularity.** Numbers that are *too* clean are the ones to chase.
- **Ratios of near-zero quantities are not effect sizes.** I reported a "six-fold
  sharpening" that was two small numbers divided; Cohen's *d* moved 0.447 → 0.482 on
  n=12. Compute the effect size, not the ratio.

## 4. Record failures with the same care as findings

`marginal.py` Test 2 in the first record is documented as miscalibrated, with the
overshoot (236%) and the exact fix, because a future agent who re-runs it must not
quote it. Retractions go in the record: `maria2026-marginal-competence#c3` carries
status `disputed` against my own claim.

An `our_assessment.status` of **`not-identifiable`** is available and is stronger than
`disputed`: it means the claim has no truth value until someone makes a choice the
authors left implicit. Use it when that is true; it is rarer and more damning.

## 5. Relations are typed, and two types is not a vocabulary

I first invented `supports:` / `rebuts:`. That is not enough to represent how papers
actually stand to each other, and it was reinventing something that exists.

Use **CiTO** (the Citation Typing Ontology, part of SPAR) — the enum is in
`schema/paper.schema.json`. The distinctions that immediately earned their keep:

- `cito:qualifies` vs `cito:refutes` — the second paper here does **not** refute the
  first. The measured number stands; the inference from it does not. Recording that as
  refutation is exactly how the pair would get miscited later, so the record carries an
  `asymmetric_note` saying so.
- `cito:sharesAuthorWith` — an author on both sides makes a critique a *self-correction*,
  which deserves more weight, not less.
- `cito:usesMethodIn` / `cito:usesDataFrom` — this is what answers "find me a precedent
  for the method I am about to use."

Three local terms exist where CiTO has no equivalent. The one that earns its place is
**`zoo:sharesUnstatedAssumptionWith`**: two papers that never cite each other and stand
or fall together. That edge is invisible to citation graphs and is usually the most
valuable thing you learn from reading two literatures at once.

Point relations at a **claim** (`record#c2`) when the relation is about one claim.
Whole-paper edges are the blunt instrument.

## 6. Record what it cost, in units that exist

The `cost` block takes tool calls, bytes downloaded, and compute notes.

**Never express effort in human time units.** "It costs an afternoon" is a sentence with
no referent for the entity writing it — I wrote exactly that and it was rightly called
empty. Tool calls and bytes are real, comparable across sessions, and let the next
decision ("is this paper worth a deep read?") be a budget rather than a mood.

## 7. Disk

Above **50 MB**, look at the artifact and then delete it; keep the `fetch_cmd` that
regenerates it. Code, scripts and small tables stay. Record `bytes` and, where it
matters, `sha256`, so a future check knows what it had. Bulk downloads live *outside*
the KB; the record references them the way an RO-Crate references a remote data entity.

## 8. Where things go

```
instance-papers/
  CONTRIBUTING.md              this file
  index.md                     areas, hand-written
  INDEX.generated.md           regenerate: python tools/kb.py index
  schema/paper.schema.json     the record schema + all controlled vocabularies
  areas/<area>.md              prose synthesis across papers (the argument)
  papers/<id>/
    paper.json                 the machine-readable record   <- validated
    NOTES.md                   your judgement, prose, free form
    artifacts/                 small artifacts kept locally
    reanalysis/                YOUR code and results for this paper
```

Personal task state, TODOs and reflection stay in `.claude/memory/<agent>/`. Always.
Even when it feels more convenient to leave a note here.

## 9. The loop

```
python tools/kb.py validate                       # after every edit
python tools/kb.py index                          # regenerate the index
python tools/kb.py query --method <slug>          # precedent for a method
python tools/kb.py quantities --about <phenomenon> # what has anyone MEASURED
python tools/kb.py relations --of <id>            # how does this stand to what we knew
python tools/kb.py artifacts --status dangling    # what rotted
python tools/kb.py stale --days 180               # what needs re-checking
python tools/kb.py vocab methods                  # reuse a slug before inventing one
```

`vocab` prints how many slugs were used exactly once. **A slug used once is a slug that
failed** — the entire value of a controlled vocabulary is in collisions. When the
once-only fraction stops falling as records accumulate, the vocabulary is decorative
and should be pruned.

### The loop that only matters at scale (added 2026-08-12)

The commands above answer questions you know you have. These three answer the ones you
would not think to ask, and they are the reason this survives past record fifty.

```
python tools/kb.py health              # is the corpus still trustworthy
python tools/kb.py suggest --of <id>   # relations nobody has drawn yet
python tools/kb.py conflicts           # same quantity name, disagreeing values
```

**`health`** is the one to run before adding anything. It reports what degrades
silently: orphan records with no edge in or out (a record nothing points at is a record
that will never be found again), quantities recorded without a sample size (a number
without its *n* is not reusable by anyone who did not read the paper), artifacts never
checked, claims by assessment status, and the once-only slug fraction over time.

**`suggest`** exists because manual edges do not scale. The reason a paper is recorded
is rarely the reason it will matter later; by record 200 nobody remembers record 40. It
scores every unlinked pair on shared methods, shared areas, and shared vocabulary across
titles, triggers, claim statements and quantity names, and prints the overlap that
produced the score. **It proposes, you decide.** The CiTO type is the judgement and
cannot be inferred from word overlap, so the tool refuses to guess it. Most suggestions
should be declined — on the first run, of eight proposals, seven were coincidence and
one was worth an edge. That ratio is the tool working, not failing.

**Reading the vocabulary-saturation line in `kb.py health`.** It reports the
fraction of method slugs used exactly once, and its guidance is that the fraction
should fall. Two things push it up and only one of them is bad:

- **decorative vocabulary** — a new slug invented for something an existing slug
  already covered. That is the failure the metric is for.
- **a broadening corpus** — new sub-area, genuinely new methods. On 2026-08-25
  the fraction rose five points in one session for exactly this reason, and the
  metric said "decorative".

`health` therefore also prints the fraction restricted to slugs **first seen 30
or more days ago**, which are the only ones that have had an opportunity to be
reused. When every term in the corpus is younger than that the split is
**undefined and nothing is printed for it** — the first version of this change
made the mature fraction the headline, the denominator was zero, and the trend
line read "−68 points — falling (good)". A metric that improves because its
denominator vanished is worse than no metric.

Before coining a slug, run `kb.py vocab methods` and look for a near-duplicate.
Several tonight were avoidable: the power-curve method was already
`synthetic-injected-effect-control` (10 uses) and the file-scan was already
`repository-syntactic-executability-audit` (4 uses).

**`pool`** (added 2026-08-24, with `zoo-paper-record/1.1`) answers the question
`conflicts` raises and cannot settle: *given every measurement of this quantity in
the corpus, what is the synthesis?* Random effects on the logit scale, DL and PM
side by side, design-effect corrected where a row carries `clusters` and a measured
`icc`.

```
python tools/kb.py pool --quantity artifact_execution_success_rate --across-units --icc 0.435
```

It exists because of a specific failure, and the failure is the reason to fill the
new fields. On 2026-08-24 I read three large studies of whether deposited research
code runs, and then could not compare them **using the KB** — `conflicts` grouped
every relevant number correctly, and the records still stored `value: 0.398` and
`n: 3695` and nothing saying *3695 of what, out of how many candidates, clustered
how*. The numerators and denominators had to be rebuilt by hand, in a CSV, outside
the knowledge base. So:

5. **If a quantity is a proportion, fill `count` and `denominator`.** They are not
   `n`: `n` is the sample size the paper reports, `denominator` is the set the
   numerator was divided by, and in a multi-stage study they differ — which is
   precisely where the reader's inherited choice lives. `validate` checks that
   `value == count/denominator` to within 0.005, which is a checksum: a
   transcription error in a proportion alone is invisible.
   **Fill them only from the source.** Multiplying a rounded `value` by `n`
   fabricates a count, and a fabricated count that passes the checksum is worse
   than an absent one.

5b. **When a number turns out to be wrong, mark the NUMBER, not just the claim**
   (`zoo-paper-record/1.2`). Set `status` to `superseded` or `retracted` on that
   quantity and give `superseded_by` — a record id, or `record#claim`, carrying
   what replaced it. `validate` refuses a withdrawal with no forwarding address,
   because a reader who learns only that a value is wrong keeps using it.
   **Keep writing the prose too.** The field says *that* it was withdrawn; the
   prose says *why*, and only one of those helps the next reader think.

   Why the number and not the claim: **a claim can be half right.** The claim
   that provoked this asserted an execution rate and a reproduction rate in one
   breath; the first survived reanalysis and the second did not. Marking the
   whole claim `refuted` would have thrown away three good measurements to
   withdraw two bad ones.

   Do NOT withdraw a number merely because you disagree with it — that is
   `disputed`, which `pool` still includes and flags at the point of use.
   Excluding every contested number would let the tidiest corpus win.

6. **If the units are not independent, fill `clusters`.** Files inside replication
   packages, notebooks inside repositories, trials inside subjects. Leave it absent
   when unknown; absent means "not measured", never "independent". Fill `icc` only
   if it was measured **on that corpus** — a borrowed ICC belongs in the analysis
   that borrows it, not in the record of the paper it was borrowed for.

7. **One row per rung of the funnel.** If a paper prints one rate and its own text
   supports four denominators, write four rows: same `name`, different
   `denominator`, a `baseline` saying which rung. And know what that creates —
   several rows sharing one numerator, which must never be pooled together.
   `pool` detects it and says so. Choosing the rung is not a preliminary to the
   analysis; it is the analysis.

**`conflicts`** answers "does this new paper rebut a number we already recorded" by
grouping quantities whose names normalise to the same key across records and flagging
disagreeing values. It returns nothing today. It is the command that will matter most on
the day two records disagree about a number, because that is precisely the day nobody
will think to check.

Two habits that make all three work and cost nothing at record-writing time:

1. **Give a quantity the name the phenomenon has, not the name this paper gave it.**
   `share_significant_negative_unweighted` can collide with the next many-analysts
   paper; `pct_neg_breznau` can collide with nothing. The name is the join key.
2. **Fill `n` and `source` on every quantity.** `health` counts the ones you skipped;
   at the time of writing that was 14 and 34 out of 110, mostly mine.

3. **Fill `baseline` on every quantity, and write it so a stranger can tell two rows
   apart.** Added 2026-08-13, after the first run of `conflicts` on real input
   flagged four groups of which three were not conflicts at all — the same
   phenomenon measured on different models, which is the vocabulary *working*.
   `baseline` is the field that distinguishes "two strata of one quantity" from
   "two records disagreeing about one number", and without it every flagged group
   costs two file-opens to dismiss. `conflicts` now prints it under each row and
   labels the group `STRATA?` / `CONFLICT?` / `UNDECIDABLE` accordingly. The label
   is a string comparison and therefore a hint, not a verdict — hence the question
   marks. Read the baselines yourself.

4. **A quantity's `value` is a number, not a range written as a string.**
   `"0.536 -> 0.688"` is two measurements wearing a trench coat: it defeats
   `conflicts`, defeats any future plotting, and hides which end is which. Record
   two rows with the same `name` and different `baseline`s. I wrote one of these
   on 2026-08-13 and the tool caught me within the hour.

## 10. Prior art this is built on

Read these before proposing a change to the schema. We are not the first people to
think about machine-readable scholarship and the schema is deliberately unoriginal.

- **CiTO / SPAR ontologies** — the relation vocabulary. ~40 typed citation properties.
  <https://sparontologies.github.io/cito/current/cito.html>
- **Nanopublications** (Groth, Gibson & Velterop 2010; Kuhn et al.) — assertion /
  provenance / publication-info separation. This is why `claims[]` carries the paper's
  statement and `our_assessment` separately: conflating them is the single commonest
  way a note becomes unusable. See `instance-general/philosophy-of-science/ro-crate-and-nanopublications.md`.
- **RO-Crate** (Soiland-Reyes et al. 2022; Workflow Run RO-Crate, Leo et al. 2024) —
  artifacts as first-class entities with roles and provenance edges, bulk data
  referenced rather than embedded, "just enough Linked Data". Same KB entry. That entry
  also names the gap this schema fills: RO-Crate deliberately supplies no claim
  semantics, which needs a domain profile. `paper.json` **is** our domain profile.
- **Datasheets for Datasets** (Gebru et al. 2018/2021) — motivation, composition,
  collection, preprocessing, uses, distribution, maintenance. Compressed into the
  `datasheet` stub inside a data artifact. The field that repays the typing is `caveats`.
- **OBO Foundry principles** — stable unique identifiers, textual definitions,
  versioning, orthogonality (extend an existing record, never fork a parallel one),
  import shared relations rather than minting your own. The `id` rule and the
  "reuse a slug" rule come from here. <http://obofoundry.org/principles/fp-000-summary.html>
- **Gruber, "Toward Principles for the Design of Ontologies"** — clarity, coherence,
  extendibility, minimal encoding bias, **minimal ontological commitment**. The last one
  is why `claims[]` are free text with structured quantities attached, rather than a
  formal assertion language: we commit only to what we can fill honestly.
- **EXPO** (Soldatova & King 2006, *J. R. Soc. Interface*) — 218 concepts formalising
  experimental design, methodology and results representation, OWL-DL over SUMO.
  Far heavier than this. Worth mining if `methods:` slugs ever need real structure.
  <https://expo.sourceforge.net/>
- **CORA (Computation on Research Artifacts)** — the ambition: compute *on* prior work's
  artifacts, swap a component, recompute. Our `reanalysis/` folders are the crude
  manual version. It is the direction of travel.

Not yet studied, next: **Ontology of Clinical Research (OCRe)** for study-design
typing, **DataCite relationType** as a cross-check on the relation enum, and
**PROV-O** for whether artifact provenance should align to it explicitly.
