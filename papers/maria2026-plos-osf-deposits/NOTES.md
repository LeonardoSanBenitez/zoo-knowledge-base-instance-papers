# maria2026-plos-osf-deposits — what an OSF link in a PLOS Data Availability statement delivers

Author: maria. Measured 2026-10-14. Own study, not someone else's paper. Sibling of
`maria2026-shell-or-payload` (which asked the question for *every* data link in 160 PLOS ONE
articles, 2016–2025, and found 37.7% resolving without delivering). This one asks it for one host,
OSF, in 2026 papers, and goes one step further: **not only "is there a file?" but "is it the file
the paper had?"**

The numbers are in `paper.json` (claims c1–c5) and regenerate from
`python reanalysis/analyse.py artifacts/plos_osf.jsonl --verify-dates`.

## Why it was measured

The retro-repro project (`dev-science-ops/paper-retrospective-reproducibility/`) gained OSF and
figshare backends on 2026-10-14 and needed a calibration paper whose deposit is on OSF. The scout
that looked for one is the instrument here. The candidate list it produced is in that project's
`papers/_scouting/README.md`; this record keeps only what is durable about the population.

## Population and sample

- PLOS search API (`api.plos.org/search`), query recorded verbatim in every row:
  `everything:"osf.io" AND everything:"code" AND publication_date:[2026-01-01 TO NOW] AND
  doc_type:full AND article_type:"Research Article"` -> **647 articles** on 2026-10-14.
- Seeded random sample of **60** (`random.Random(20261014).sample`).
- **The population is filtered by keyword.** It is "2026 PLOS research articles whose full text
  mentions osf.io and code", not PLOS. The share whose DAS names OSF describes that filtered set
  only. The complement was not sampled.

## The instrument

Per paper: the JATS from journals.plos.org, the `data-availability` custom-meta, every OSF GUID
in it (with any `view_only` key from the same URL), and per GUID: `/v2/guids/` type and status,
a full walk of providers, folders and pages (the same walker `tools/acquire.py` uses for S1),
child components, licence, and per file `[path, size, date_modified, current_version]`. **Nothing
was downloaded.** For every file whose `date_modified` is after the paper's publication date, the
versions endpoint was read and the file classed as `replaced` (a new version after publication),
`late` (first version after publication) or `metadata` (neither).

**Known-answer controls, run at the start of every pass, which aborts if either fails:**
`osf.io/cbhdv` must list 1 file of 1,301,939 B; `osf.io/3bzu8` must list 0 files with its GitHub
add-on answering 404. Both held on all three passes.

**Second method for "private".** A 401 from the v2 API was re-checked against WaterButler
(`files.osf.io/v1/resources/<g>/providers/osfstorage/`): 200 public, 403 private, 404 invented;
controls cbhdv 200/200 and invented zzzz9 404/404. The legacy `osf.io/api/v1/project/<g>/`
answers **200 for private nodes too**, so it is a shell and was not used.

## Failures, recorded with the same care as findings

1. **Pass 1 dropped `view_only` keys, and produced 6 false "private" verdicts.** The GUID regex kept
   the five characters and threw away `?view_only=<key>`. Of 10 papers whose DAS GUID answered 401,
   7 printed a key in the same URL, and all 7 opened with it. The output of that pass is kept as
   `dev-science-ops/paper-retrospective-reproducibility/papers/_scouting/plos_osf.v1-dropped-view_only.jsonl`
   so the error can be seen. **I had already solved this on 2026-09-08**, in
   `maria2026-shell-or-payload/reanalysis/authoritative.py`, which retries with the token, and I did
   not query the knowledge base before writing the new scout. The same defect was then found and
   fixed in the project's `gate.py` and `acquire.py`, which had never had it either.
2. A pass-2 run was stopped at 53/60 in order to add per-file dates (pass 3). Its partial output
   was used only to count the view_only effect, which pass 3 reproduces.
3. The first interim count read "8 of 29 papers with an OSF GUID have zero files". It was wrong for
   the reason in 1, and it was the number this project would most have liked to be true.

## What this does not show

- Nothing about what is *inside* archives (`.zip`): code inside one is invisible to a listing.
  "Visible code" is a lower bound.
- Nothing about whether the files reproduce anything.
- `date_modified` is not used as evidence on its own. Only version dates are.
- A `view_only` link in a published DAS is reachable *today*. It is an anonymous-review token the
  owner can revoke at any time, and nothing about the printed URL would change if they did. That
  makes it fragile, not wrong; PLOS's policy does not forbid it.
