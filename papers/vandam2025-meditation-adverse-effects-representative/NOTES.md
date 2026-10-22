# vandam2025 — notes (maria)

2026-10-17: abstract-only placeholder (OSF 503). 2026-10-23: deposit fetched, the authors' manuscript of
14 May 2024 read in full, every incidence figure recomputed (`reanalysis/v01`–`v06`). The published 2025
version was not reachable; where it may differ, the record says so.

## What reproduces

Every adverse-effect count, exactly: 517 IME (58.35%), 694 MRAES (78.33%), 278 generic (31.38%), 81
impaired (9.14%), 34 lasting (3.84%). I rebuilt the IME counts from the item-level intensities and
valences, and they match the deposited columns row by row (886/886). The pooled H1b test reproduces
(chi2 = 0.07, p = .795). A clean, well-documented deposit with a full data dictionary.

## The one count that does not

"96.61% (856) experienced at least one unusual experience." By the stated definition (≥ Slight on any
of the 30 IME items) the data give 861 (97.18%). 856 is hard-coded in the authors' script. It is
also exactly the number of respondents who meditated in the past 12 months. Probably a typed-in count
from the wrong column. It changes nothing of substance.

## What the numbers belong to

The survey randomised two features of its own construction, 2 × 2 between subjects. The analysis script
models both. The manuscript reports neither:

| | fixed item order | random item order |
|---|---|---|
| IME adverse effect (the 58.4%) | **63.4%** (293/462) | **52.8%** (224/424) |

| | AE block first | UE block first |
|---|---|---|
| generic "challenging, difficult or distressing" | **24.9%** (107/429) | **37.4%** (171/457) |

Each is worth more than ten points (p = .0014 and p = 6 × 10⁻⁵). The second carries a consequence:
H1b ("consistent with Goldberg's 32.3%") holds only for the pooled mix. The AE-first arm is
significantly LOWER than Goldberg (p = .021). An incidence of meditation harm is, in part, an incidence
of a questionnaire. I knew this from karger2023 for probabilities. Here it is for symptoms, measured
by a randomised experiment its authors ran and did not report.

The threshold matters as much: the Measures paragraph defines an IME adverse effect at "modestly
unpleasant or greater", which gives 42.2%. The analysis used "mildly", which gives 58.4%. That
deviation is listed elsewhere, but the defining sentence was not updated.

## What I expected, and what the data said

Before reading, I wrote that schlosser2019 and goldberg2022 point to an early-onset susceptible
subgroup. Here the lifetime IME rate FALLS with practice: 68.5% in the first year, 42.4% after twenty.
A lifetime rate cannot fall with exposure within one population, so this is selection, forgetting or
cohort, not protection. The fall is carried by distress. Novices are more distressed (ρ = −0.22 with
hours). With K10 and psychoticism held fixed the gradient vanishes, and for the generic item it
reverses: more hours, more adverse effects. Only 30 lapsed meditators are in the sample, one of whom
stopped because of a bad experience, so attrition itself cannot be seen. And the lapsed
who are here report the generic item LESS often (23% vs 32%), as in goldberg2022, which argues
against attrition of the harmed. What is left is composition: the less experienced are the more
distressed, for whatever reason. The safe sentence is negative. In a cross-sectional survey of practitioners, "experienced meditators report fewer adverse
effects" is not evidence that practice protects.

The retreat association answers the 2026-10-17 question. It survives adjustment for hours, years,
distress and psychoticism: impairment OR 2.13 (p = .01), generic OR 1.48 (p = .02).

## A false alarm, kept because it is the most useful thing in this file

On the first run, the "imputation" appeared to overwrite 69% of observed valence ratings, which
would have been a serious defect. It was my reader. The Python `rdata` package returns R's
`NA_integer_` as −2147483648, so every missing cell compared as "extremely unpleasant". After masking,
the imputation changes 0 of 27,548 observed cells. The headline is bounded between 57.7% and 59.7%
whatever the missing valences were. I nearly wrote the defect into the record. What stopped me was
reading the most frequent change pairs before writing anything: all of them came from one impossible
value.

## Handling

- `.rds` without R: `pyreadr` fails ("unsupported features"). `rdata` works with a custom data.frame
  constructor (`reanalysis/load_rds.py`). It needs dict iteration, flattening of (n, 1) matrix columns,
  and the NA mask above.
- Data are not committed: they include Prolific IDs. `reanalysis/fetch.py` regenerates them, checking
  OSF's sha256.

## Cost

About 45 tool calls; about 5 MB downloaded; every script runs in seconds.
