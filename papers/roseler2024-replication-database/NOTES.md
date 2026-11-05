# roseler2024-replication-database — reading notes

Author: maria, 2026-11-05.

## What it is
FReD: a crowdsourced, living database of original-replication pairs, mostly psychology. The JOPD data paper describes
the 16 Oct 2023 snapshot (1,239 entries, 336 originals); the GitHub export of 2026-02-01 has 2,164 rows with renamed
columns. Liberal inclusion; Many Labs entered per lab; effect sizes converted to r where possible; outcome coded
from replicators' statements or computed. "Success" = both significant or both non-significant, same direction.

## Reproduced (f05, frozen version)
Outcome counts 641/447/133/15/3, relative ES k = 1,050, M .52, SD .98, Md .387, min/max -- all exact. Two
bookkeeping numbers do not match (335 vs 336 originals; 188 vs 201 rows without ES).

## Blinding (f00)
mark's known-answer control (8 Psych Sci 2014 papers) is still blinded. f00 drops, before anything is printed, every
row whose original DOI is one of the 8 or whose original ref/author/title contains any of their first-author surnames,
and prints nothing about dropped rows. f05 runs on the unfiltered frozen file but prints corpus aggregates only.

## What I did with it (f01-f04; the forecasting claims live in pawel2020 #c7)
- 1,082 usable pairs (747 exact original p, 335 parsed 1-df statistics), 475 originals, success 35.9%.
- Original |t| predicts modestly (AUC .625; 27% -> 51% by quintile). Replication n predicts nothing (AUC .47,
  coefficient ~0). Under the standard model it should (AUC .66). Robust to every subset I tried.
- A "share of nulls" mixture fitted by ML degenerates (tau -> infinity): the model family is wrong, not just tau.
- With the database's own verdict as outcome, the forecast is anti-informative (AUC .476). Unexplained. Before anyone
  uses `reported_success` as ground truth for a detector, find out why.

## Traps (for whoever uses it next)
- osf.io/qtkzy downloads as FReD.xlsx but is CSV text. pandas.read_excel fails; read_csv works.
- es_value_o mixes numbers and test-statistic strings ("F(1, 188) = ..."). Parse, do not coerce.
- Rows are not independent: 72.8% of usable pairs come from originals with > 1 row (max 35). Weight 1/k or cluster.
- `power` is computed at the original effect size: median .98, useless as an outcome predictor.
- jyx.jyu.fi bitstream for the PDF returned 0 bytes; JOPD /articles/101/files/<hash>.pdf works with a browser UA.
