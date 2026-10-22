# Pre-registered plan — is the repetition of the Pali suttas a trace of oral composition?

Written 2026-10-23 by maria BEFORE downloading any text. Committed before data.

## Question

allon2022 (Journal of Indian Philosophy) reports that about 30% of DN 25 is verbatim repetition and reads
the repetitiveness of the early Buddhist texts as a feature of oral composition and transmission. That
record's open question: compare within-text repetition of the canonical prose with the commentaries at
matched length. If repetition is the signature of orality, layers of decreasing orality should repeat less:
**mula** (canon) > **atthakatha** (commentaries, compiled in Pali in the 5th c. from older Sinhala
commentaries) > **tika** (sub-commentaries, later, composed in writing).

## Data

VipassanaTech/tipitaka-xml, commit 05d5d3c7cede (2026-09-16), `romn/` (roman script, Chattha Sangayana).
Six books x three layers: DN s0101-s0103 and MN s0201-s0203, files `m.mul`, `a.att`, `t.tik`. 18 files.

## Measure

Text = XML with tags removed and `<note>` content dropped; lower-case; tokens = maximal runs of letters
(Pali diacritics included). The edition abbreviates repetitions with `pe` (peyyala); those tokens are
removed and COUNTED per 1,000 tokens per layer. Elided repetition is invisible to the measure, so canon
repetition is a LOWER bound -- the elision works against prediction P1, not for it.

R_n(segment) = share of tokens in the segment covered by at least one word n-gram that occurs two or more
times within that segment. Segments: consecutive non-overlapping windows of 20,000 tokens, per layer and
nikaya (tail shorter than 20,000 dropped). Primary n = 8; sensitivity n = 4 and n = 12.

## Known-answer checks (run on real segments before any comparison is read)

- shuffled tokens (within segment): R_8 should be near 0;
- a 10,000-token passage followed by itself: R_8 should be 1.

## Predictions

- **P1** In both DN and MN: mean R_8 mula > atthakatha > tika; mula vs atthakatha Mann-Whitney p < .01 on
  segments.
- **P2** The mula > atthakatha ordering holds at n = 4 and n = 12.
- **P3** (the risk I can see) Commentaries are formulaic too ("ti attho", "vuttam hoti", glosses repeated
  for each occurrence of a lemma). If R_8(atthakatha) >= R_8(mula) in either nikaya, the comparative
  support for reading canonical repetition as oral residue fails in that nikaya, and the record says so.

## Deviations

(none yet)
