# Selection audit of instance-papers — rubric (written BEFORE reading any NOTES)

Written 2026-10-22, in answer to mark's question (2026-10-20): "of the papers in instance-papers you
reanalysed, how many did you open because you already suspected something, and how many blind? If most
were suspected, every defect rate quoted from the KB carries the same bias."

## Population
Every record in `zoo-knowledge-base/instance-papers/papers/` whose read_depth is read-and-reanalysed or
read-and-ran-artifacts and whose id does NOT start with `maria2026-` (those are my own studies, not papers
selected for reading). Records at lower depths are listed but not classified for the rate.

## Selection classes (one per record, decided from the earliest written evidence of WHY it was opened)
- **F finding-first**: before opening, I (or a peer who pointed me to it) had a specific suspicion of a defect
  in THIS paper (an error, a mis-measurement, a non-reproducing number, an over-claim), or it was chosen
  as a test case for a defect hypothesis already held.
- **K known-dispute**: chosen because the literature already disputes its result (published comment,
  adversarial collaboration, correction notice), but no specific defect suspicion of my own.
- **C chain**: opened because another record pointed to it (a reference, a comparator, the paper a
  correction corrects), with no defect suspicion recorded at the moment of opening.
- **B blind**: chosen for topic, for shipping data/code, or as a canonical example of a phenomenon,
  with no recorded defect suspicion. Includes papers picked from a search for "ships data".
- **U unknown**: no written evidence of why it was opened. Not to be imputed.

Evidence order: (1) the record's NOTES.md opening section, (2) the session file of its creation date in
`.claude/memory/maria/`, (3) the commit message that created it. Quote the evidence line per record.

## Outcome (decided mechanically, from paper.json, after classification)
defect = at least one claim whose our_assessment.status is in {refuted, disputed, measures-something-else,
not-reproduced, corrected, partially-reproduced} OR any quantity with status in {superseded, retracted,
measures-something-else}. Exact status vocabulary to be read off the corpus first; the mapping is fixed
before the cross-tab is computed.

## Known weaknesses, stated in advance
- Classifier = the selector = the reanalyst. No blinding is possible: I remember some of these. The quote
  per record is the only safeguard; anyone can re-classify from the quotes.
- Retrospective notes may rationalise: a NOTES file written after a finding can describe the opening
  motive with hindsight. Where the NOTES opening was clearly written after the finding, mark it.
- n is ~45. Rates per class will have wide intervals; report counts, not only rates.

## Addendum, written after reading the status vocabulary and BEFORE the cross-tab
Corpus vocabulary (2026-10-22): claim status {accepted 153, accepted-narrower-scope 135, unverified 21,
disputed 20, refuted 17, not-identifiable 12}; quantity status {current, measures-something-else 16,
superseded 9, disputed 4, retracted 1}.
- **defect (strong)** = record has >=1 claim refuted | disputed | not-identifiable, or >=1 quantity
  measures-something-else | disputed.
- **narrowed (weak)** = no strong defect, >=1 claim accepted-narrower-scope.
- **clean** = neither.
- quantity superseded/retracted EXCLUDED: in this corpus those mark MY withdrawn numbers, not the paper's.
- Known contamination: the schema has no field saying whether a claim is the paper's or one I added; a
  refuted claim of my own would count as a paper defect. To be spot-checked on the strong-defect records.
- F is reported with subtypes, as the rubric's own wording already contains both: F1 = suspicion about THIS
  paper; F2 = paper chosen to test a general defect hypothesis I already held.
