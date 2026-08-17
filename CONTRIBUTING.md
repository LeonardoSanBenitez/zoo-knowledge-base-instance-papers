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
