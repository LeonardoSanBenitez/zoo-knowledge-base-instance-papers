# Pre-registered plan — futrell2015 replication on Universal Dependencies 2.14

Written 2026-10-23 by maria, after reading the paper (PMC4547262) and both corrections, BEFORE downloading
any treebank. Committed before data. Deviations will be listed at the end under "Deviations".

## Why

The selection audit (`maria2026-selection-and-reader-bias`) found 3 of 46 reanalysed records clean, and
no known-answer control for the reading protocol. This paper was chosen *expecting it to be sound*: it
already compares against structural random baselines. If the protocol is discriminating, this record
should come out clean or nearly so. **A clean outcome is a result, and will be recorded as one.**

## Data

UD 2.14 (tag `r2.14` of each `UniversalDependencies/UD_*` repository), all splits concatenated. Twelve
treebanks chosen for overlap with the paper's languages and for size, fixed now:
English-EWT, German-GSD, Italian-ISDT, Indonesian-GSD, Irish-IDT, Finnish-TDT, Japanese-GSD,
Korean-GSD, Turkish-IMST, Telugu-MTG, Ancient_Greek-Perseus, Chinese-GSD.
Sentences: single-rooted, punctuation (UPOS PUNCT) and its arcs removed as in the paper, multiword
tokens and empty nodes dropped, length 1-99 after removal.

## Measures (as in the paper)

Arc length = |position(head) - position(dependent)| over non-punctuation words; sentence DL = sum.
Baselines per sentence, 50 linearisations each (paper: 100):
- FREE: random projective linearisation (random order of head and dependent subtrees at each node).
- FIXED: one random weight in [-1, 1] per relation type (UD `deprel`, subtype stripped), head weight 0,
  dependents ordered by weight at every node; new weights per sentence.
Two trees per sentence: CONTENT-HEAD (UD as distributed) and FUNCTION-HEAD (the paper's normalisation:
`case` and `mark` dependents become heads of their former heads; the paper's conjunction handling,
"Stanford style", is approximated by leaving `cc`/`conj` as in UD -- stated, not hidden).

## Test

Per sentence, d_s = observed DL - mean baseline DL. OLS of d_s on l_s^2 across sentences (one point per
sentence, so no pseudo-replication), HC3 SE, one-sided test that the slope < 0. (The paper's mixed model
with 100 baseline rows per sentence is equivalent in sign.)

## Predictions (made now)

- **P1** FREE, content-head: slope < 0 at p < .001 in 12/12 treebanks.
- **P2** FIXED, content-head: slope < 0 at p < .01 in at least 11/12 (Telugu may fail, as in the paper).
- **P3** Short sentences (length 3-5): observed DL is NOT below FREE in at least half the treebanks
  (mean d_s >= 0 at some length in 3-5); I expect at least one language with d_s > 0 at p < .05 at length
  3 or 4 (the "anti-minimisation" reported by Ferrer-i-Cancho & Gomez-Rodriguez 2021 -- from memory, not
  re-read; this prediction does not rest on the citation).
- **P4** FUNCTION-HEAD vs CONTENT-HEAD: same sign of slope in 12/12; the ratio obs/FREE at length 20
  differs by more than 0.05 in at least 4 treebanks (i.e. the normalisation is not innocuous for the
  effect SIZE, though the paper says the "pattern of results and their significance was the same").
- **P5** Head-final (Japanese, Korean, Turkish, Telugu) have higher obs/FREE at length 15-25 than
  head-initial (Italian, Indonesian, Irish), as the paper reports (all four above all three).

## What would count as clean

P1, P2, P5 hold; P4 shows same sign everywhere. Then the paper's claims stand as stated, and the record
says so (claims `accepted`). P3 and P4-size are about scope, not about defects; if they come out as
predicted they narrow nothing the paper claimed, because the paper itself reports length-12 as the
first length significant in all languages and says the normalisation does not change significance.

## Deviations

Written 2026-10-23 after the run, before writing the record.
1. FIXED baseline: siblings with the SAME relation type have equal weights; the plan (like the paper) did not
   say how to order them. dlm.py breaks such ties at random. Stated, not a choice made after seeing results.
2. P4 is scored on 11 treebanks: Telugu-MTG has no sentence of length 18-22 after punctuation removal.
3. Nothing else. 50 linearisations per baseline, seed 20261023, all twelve treebanks as listed.

## Outcome against the predictions (artifacts/analyse_out.txt)

P1 12/12 held. P2 11/12 held (Telugu fails, as in the paper). P3 held (7/12 non-negative; 8 significant
positive cells at length 3-4). P4 held exactly (sign 12/12; size > 0.05 in 4). **P5 FAILED**: Japanese-GSD
(0.676) is below Irish (0.686). By the definition written above, the record is therefore NOT clean.
