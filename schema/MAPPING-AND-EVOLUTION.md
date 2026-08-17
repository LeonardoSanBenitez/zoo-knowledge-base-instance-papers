# Mapping to standard vocabularies, and how to change this schema

Author: maria, 2026-08-07.

Two jobs. **Part 1** keeps the door open to publishing these records outside the zoo.
**Part 2** says how to replace this schema when it stops fitting — which it will.

---

# Part 1 — Mapping out

## Why bother

Standing goal, set by Leonardo 2026-08-07, deliberately with no deadline:

> These records could be useful beyond our own tooling. Cidral already ships a JSON
> catalogue of a paper's mathematical statements alongside his Lean formalisations in
> pull requests to public repos — something he invented, and which plausibly every
> paper should have. The same may become true of this. Design as if it will leave the
> house; do not act on it until there is a reason.

So the constraint on every schema decision from now on is: **could a field be given a
stable meaning outside this repo?** Not "is it RDF today" — Gruber's minimal
ontological commitment applies, and premature formalisation is the failure mode this
whole exercise is trying to avoid. But a field whose meaning is "whatever maria meant
that afternoon" cannot travel, and should be either defined or dropped.

Practical near-term consequence: `paper.json` is plain JSON with no `@context`, and
that is deliberate — a JSON file that anyone can read beats JSON-LD nobody opens. But
every field below has a target IRI, so emitting JSON-LD is a mechanical transformation,
not a redesign. Whoever needs it can write `kb.py export --jsonld` in an afternoon of
tool calls.

## Field → standard vocabulary

| our field | maps to | notes |
|---|---|---|
| `id` | `dcterms:identifier` (local), paired with `identifiers.doi` → `datacite:Identifier` | local key; the DOI/arXiv id is the globally resolvable one |
| `title`, `authors`, `year`, `venue` | `dcterms:title`, `dcterms:creator`, `fabio:hasPublicationYear`, `fabio:JournalArticle`/`fabio:ConferencePaper` | FaBiO (SPAR) types the *work*; we currently flatten venue to a string |
| `area` | `fabio:hasSubjectTerm` / `dcterms:subject` | uncontrolled today. **Weakest field for export.** Should eventually point at a real subject scheme |
| `read_depth` | *no standard equivalent found* | our own. Arguably the most transferable idea here: a public claim about how deeply the recorder actually engaged. Nothing in CiTO, PROV-O or DataCite expresses it |
| `claims[].statement` | nanopub **assertion** graph | one claim ≈ one nanopublication assertion |
| `claims[].our_assessment` | nanopub **provenance** + `cito:agreesWith`/`disagreesWith`/`corrects` | the assertion/provenance split is exactly why these are separate fields |
| `claims[].scope` | *no clean equivalent* | closest is OCRe-style study-design typing, unstudied. Scope loss is the commonest citation failure, so this field should survive any redesign |
| `claims[].quantities[]` | `qudt:Quantity` (value/unit); `n`, `baseline` have no standard home | **the `baseline` field is ours and matters**: for any agreement or correlation statistic the baseline *is* the claim (see `jo2026-subjectivity`). No standard vocabulary carries it |
| `methods[]` | `fabio` has no method vocabulary; **EXPO** does (218 concepts) | our slugs are a poor person's EXPO. If methods ever need structure, mine EXPO rather than growing the slug list |
| `artifacts[]` | RO-Crate data entities: `schema:Dataset` / `schema:SoftwareSourceCode` / `schema:CreativeWork` | one `paper.json` ≈ one RO-Crate root with aggregated entities |
| `artifacts[].role` | `schema:additionalType` | our enum; `in-paper-table` is unusual and worth keeping — small-n fields publish data as PDF tables and no standard treats that as data |
| `artifacts[].derived_from` | `prov:wasDerivedFrom` | direct, already aligned |
| `artifacts[].checked` | `prov:Activity` with `prov:used`, `prov:wasAssociatedWith`, `prov:endedAtTime` | direct. The `how` string is a degenerate `prov:Plan` |
| `artifacts[].status` | *no standard equivalent* | **the second genuinely new thing here.** `present-but-insufficient` and `dangling` have no home in DataCite, RO-Crate, or any artifact-badging scheme, and they are precisely the two states that make a paper unreanalysable. If anything from this schema deserves to be proposed upstream, it is this |
| `artifacts[].datasheet` | Datasheets for Datasets §§ motivation/composition/collection/preprocessing | compressed to 5 fields; `caveats` is our addition and earns the stub |
| `artifacts[].sha256`, `bytes` | `spdx:checksum`, `schema:contentSize` | |
| `relations[].type` | **CiTO** directly — the enum values *are* CiTO IRIs under `http://purl.org/spar/cito/` | already exportable with no translation |
| `relations[].target` | `cito` object, or our `record#claimid` → a nanopub URI | claim-level targets are the interesting case |
| `zoo:sharesUnstatedAssumptionWith` | *nothing* | two works that never cite each other and stand or fall together. Invisible to every citation graph. Candidate CiTO extension |
| `cost` | `prov:Activity` qualified with our own units | tool calls and bytes. No standard, and unlikely to want one |
| `curation` | `prov:Agent`, `dcterms:created`, `dcterms:modified` | `verified` (last date artifact statuses were *re-checked*) has no standard equivalent and rots fastest |
| `triggers` | *nothing* | retrieval phrases, lucas's idea. Purely instrumental, would not export |

## What we would be contributing, if it ever went out

Four things are not in the prior art, in descending order of confidence:

1. **`artifacts[].status`** — the distinction between an artifact being *present* and
   being *sufficient for reanalysis*. Every badging scheme checks the first. The first
   record in this folder is a well-documented ICML 2025 repo where code, derived tables,
   regressions and figures are all present and the raw matrix is a dangling LFS pointer.
2. **`quantities[].baseline`** — carrying the comparison alongside the number, because
   for a large class of statistics the number is meaningless without it.
3. **`read_depth`** — a public, honest statement of engagement depth, which makes a
   citation from a record checkable rather than assumed.
4. **`zoo:sharesUnstatedAssumptionWith`** — the edge citation graphs cannot see.

Plausible routes, unresearched, listed so a future session does not start from zero:
SPAR/CiTO issue tracker for the relation term; the RO-Crate community profiles
mechanism for an "analysed paper" profile; nanopub for claim-level publishing.

---

# Part 2 — How to change this schema

This was invented on 2026-08-07 in a single session, under criticism, by one agent, on
four papers. It is a first draft that happens to validate. **It is not settled and
should not be treated as settled.**

## Evolution rules

1. **Bump `schema_version` and write a CHANGELOG entry below.** Records carry their
   version; a validator can support several.
2. **Extend, do not fork** (OBO Foundry). A second parallel record format is the
   failure mode, not a new field.
3. **A field earns its place by being *used*, not by being reasonable.** Run
   `kb.py vocab` — it reports how many terms were used exactly once. Fields and enum
   values that stay at one occurrence after ~20 records are decoration. Cut them.
4. **Check the prior art before inventing.** The `supports:`/`rebuts:` mistake cost
   nothing to fix and would have cost a lot to live with. CiTO had 40 terms ready.
5. **Prefer dropping a field to filling it dishonestly.** A blank `datasheet.caveats` is
   information; an invented one is worse than nothing.

## Known weaknesses of v1.0, in the order I would attack them

- `area` is an uncontrolled string list, and it is the field most used for navigation.
  Needs either a real subject scheme or an explicit decision that it stays folksonomic.
- `methods` slugs have no definitions — just strings. Two agents will coin different
  slugs for the same method and the vocabulary will silently fragment. A one-line
  definition per slug, in a file, is the cheap fix; EXPO is the expensive one.
- `claims[].statement` is free text, so claims cannot be compared across papers
  mechanically. Deliberate (minimal ontological commitment) but it caps what
  `kb.py` can ever do. The nanopub people would say formalise; I say not yet, and the
  moment to revisit is when we have two papers making *the same* claim and want the
  tool to notice.
- No `superseded_by` at claim level, only at record level.
- No multi-agent curation: one `curation.author`. When cidral reviews a record — he was
  asked to attack one on 2026-08-07 — there is nowhere to record his verdict.
  **This is the most likely next change.**
- `cost` is not comparable across agents with different tooling.

## CHANGELOG

- **1.0 — 2026-08-07, maria.** Initial. Built from CiTO (relations), nanopublications
  (assertion/provenance split), RO-Crate (artifacts + provenance), Datasheets for
  Datasets (data stubs), OBO Foundry (identifier and orthogonality discipline), Gruber
  (minimal commitment). Replaces an inline two-term `stance:` markdown convention that
  survived about four hours.
