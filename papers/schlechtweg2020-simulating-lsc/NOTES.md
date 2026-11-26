# schlechtweg2020-simulating-lsc — notes (maria, 2026-11-27)

Author: maria

## What it is
The paper that defines graded LSC as the JS distance between sense frequency distributions (and binary LSC by a 0.1 threshold), and builds a 148-lemma synthetic testset by splitting SemCor: target lemmas (freq 100-1000) get their senses pushed to one half, everything else is split at random. Reports SGNS/SVD/RI models against polysemy and frequency baselines.

## Breaking it
`reanalysis/null_check.py`: gold recomputed exactly; baselines .349/.120 reproduced exactly. The baseline it lacks: the no-change expectation of the plug-in distance (K and the two sizes only) gets .422, more than the polysemy baseline and close to the best of many configurations (.451). 62/148 lemmas are indistinguishable from a random re-split, and among them gold follows the null ranking at .79. Randomly split lemmas are pure sampling noise by construction, and they still carry a graded change of ~0.15 on average.

## For arena-lsc
The definition behind 1b came with an explicit warning about polysemy and frequency confounds; the sample-size confound was not named in 2020 and is not named in the task. Paper section 4 can cite this as the origin and add the no-change baseline as the missing third.
