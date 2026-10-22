# Futrell, Mahowald & Gibson (2015) — dependency length minimisation in 37 languages — notes

Author: maria, 2026-10-23. Read in full (PMC HTML; Europe PMC's XML endpoint answered 500 for this
non-OA item), with both published corrections. Table S1 (supplement PDF) not retrievable: the PMC link
returns an HTML page. Replication on Universal Dependencies 2.14 with a plan committed before any
treebank was downloaded (`reanalysis/PLAN.md`, commit 70018f4).

## Why this paper, and what that means for reading it

Selection, written at the time: *blind, expecting it to be sound*. My last seven records in this area
broke a "near-optimal" claim against a structural null the authors had not used. This one already
uses structural nulls: random projective linearisations of the same trees, then consistent orders per
relation type, then consistent head direction, then fixed head position. The selection audit found 3 of
46 records clean and no known-answer control for my protocol. A paper picked because it looks sound is
the cheapest substitute a single reader has, so the plan said in advance what "clean" would be.

## The corrections

Both benign. One fixes Figs. 2 and 3, which were mislabelled and out of order. The other restores five
omitted references, including Liu (2008), prior corpus evidence from 20 languages, with a sentence that
narrows the paper's novelty to "word orders ... given the dependency tree structures".

## What I did

No code or data was deposited with the paper, and one of its corpora is LDC-licensed. So this is a
replication, not a reproduction: twelve UD 2.14 treebanks overlapping the paper's languages, the
paper's measure and its two main baselines (FREE random projective; FIXED random order per relation
type), both head schemes, and five predictions written and committed first.

## Outcome

| prediction | result |
|---|---|
| P1 FREE, slope < 0 at p < .001 in 12/12 | **held**, 12/12 (weakest: Telugu, p = 1e-5) |
| P2 FIXED, at p < .01 in >= 11/12 | **held**, 11/12; Telugu fails, as in the paper |
| P3 reversal in short sentences | **held**: 8 cells at length 3-4 significantly LONGER than random |
| P4 head scheme: same sign 12/12; size shift > .05 in >= 4 | **held** exactly (4); function-head always lowers the ratio |
| P5 all head-final above all head-initial | **failed**: Japanese-GSD 0.676 < Irish 0.686 |

The central result replicates on newer annotation: dependency length is minimised in every treebank,
against both baselines, except the one exception the paper itself reports. That is the result the
title and abstract claim, and it stands.

The secondary claim does not travel. Head-final languages are said to minimise much less.
Korean, Turkish and Telugu do minimise weakly (0.79-0.87). But Japanese-GSD is among the most
minimised (0.676 content-head, 0.582 under the paper's own normalisation). And German, Ancient Greek
and Chinese, none of them head-final, are as weakly minimised as Korean and Turkish. Head finality is
not the dividing line in this sample. The Japanese difference is probably the corpus: spoken dialogue
in the paper, written Wikipedia text with its own segmentation in UD-GSD.

## What this record says about the reading protocol

I picked this paper because it looked sound, and wrote down in advance what "clean" would mean. It is
not clean by that definition: one pre-registered prediction failed, on a claim the authors themselves
called "apparent" and "unexpected". In the selection audit's terms, the record will count as having a
disputed claim, and that should be read with its weight. The headline replicated in 12/12, the
exception replicated, and the failure is in a discussion-section observation on a different corpus.
A defect *label* again flattens a good paper into the same column as a bad one. That is the 3-of-46
problem from the other side. The fix is not to soften this record. Rates over records should weight
which claim failed, not merely whether one did. A crude version: count only failures of claims that
appear in the title or abstract. Noted as a 1.7 candidate.

## Handling

- Europe PMC XML: HTTP 500 for this non-OA item and both corrections; PMC HTML works (archive-api-traps).
- Table S1 link returns an HTML page; not read.
- Punctuation removal can orphan dependents of punctuation (rare); re-attached to the punctuation's head.
- `function_head` promotes the closest `case`/`mark` dependent. "Stanford-style" conjunction handling was
  not replicated (stated in the plan).
- FIXED baseline: siblings with the same relation type tie; broken at random (deviation 1 in the plan).

## Cost

About 30 tool calls; 185 MB of treebanks (deleted, fetch_ud.py regenerates); about 4 minutes of
compute on 12 processes.
