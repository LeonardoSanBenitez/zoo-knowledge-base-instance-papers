# coronadomontoya2016-mindfulness-positive-results — reading notes

Author: maria, 2026-11-05.

## Paper
124 RCTs of MBSR/MBCT-type therapy vs inactive control. 108 (87%) "positive" in the abstract; 65.7 expected at
d = .55 (individual psychotherapy for depression, chosen as a deliberately generous reference). Excess concentrated
in small trials. Registry side: 13/21 unpublished at 30 months; 0/21 adequately registered primary outcomes; 0/36
reviews flag reporting bias. They explicitly decline to run Ioannidis-Trikalinos (no primary outcome identifiable,
no unbiased d, heterogeneity) and present the ratio "for comparison".

## Reproduced (c01)
S3 Appendix is a docx table (no data file); parsed it from document.xml. Power column recomputed to 0.0005;
Table 1 bins exact; d needed for 108 = 1.029 (paper 1.03).

## The break
"Positive" = at least one significant outcome among those in the abstract. "Expected" = single-test power. So the
paper's own reasons for not running the formal test (no single primary outcome) are exactly why its comparison is
not like-for-like. Known-answer: with NO reporting bias, k equicorrelated outcomes (rho .5):

| d | k=1 | k=3 | k=4 | k=6 |
|---|---|---|---|---|
| 0 | 3.1 | 7.8 | 9.6 | 12.9 |
| .30 | 28.9 | 51.5 | 57.8 | 66.6 |
| .44 | 50.7 | 76.5 | 82.3 | 89.9 |
| .55 | 67.3 | 91.4 | 96.4 | 102.3 |

At their d = .55 most of the gap closes. At plausible d (AHRQ .22-.44) a real excess remains, 1.2-2x. So: the
conclusion's direction survives, its magnitude does not. "d = 1.03 would be needed" should never be quoted.

## A note from the clinician in me
The 14 positives that rest on within-group pre-post change are the old problem of the waiting-list control dressed
as a result: everyone improves a little after eight weeks of attention. The paper counts them positive because the
abstracts present them so -- which is the paper's real finding, and a better one than the ratio: of 16 negative
trials, 11 still headlined within-group improvement and 5 a caveat; only 3 said plainly that it did not work.

## Connections
- maglio2014: same logic per paper (TIVA). pawel2020: same shape of trap (the definition of 'expected' moves the gap).
- contemplative-neuroscience area: evidence quality of the intervention literature that CAT's validation would lean on.
