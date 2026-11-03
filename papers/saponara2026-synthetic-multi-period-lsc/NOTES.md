# saponara2026-synthetic-multi-period-lsc — notes (maria, 2026-11-03)

The organisers of SemEval-2027 Task 3 point participants here for development data. Two things matter to a participant.

**1. Their reference pipeline is XL-LEXEME + agglomerative clustering with a distance threshold, and the threshold is
the lever.** 0.32 vs 0.50 moves the cluster-JSD correlation from 0.27 to 0.41 in their Table 2; I reproduce the same
contrast (0.386 vs 0.249 on 261 lemmas). My public-data sweeps for the task's 1a (BCubed) and 1b (consecutive-period
JSD) put the 1a optimum near 0.40 and the 1b optimum near 0.26-0.38 (average linkage), so the 1a/1b tension is real
and the organisers' 0.32 sits on the 1b side.

**2. PRT did not reproduce.** 0.367 [0.267, 0.447] on my sample vs 0.473 printed. Not normalisation (raw vs
normalised vectors give identical PRT to 0.002; XL-LEXEME norms are almost constant, 30.6 +- 0.3). The three other
metrics land inside their intervals, so a gold-construction difference (which would move all four) is unlikely to be
the cause. Left open: their lemma set (all ~2,300 vs my 261), linkage, PRT code. The claim "PRT is the most robust
metric" therefore rests on a number I cannot reach; on my sample JSD@0.32 is at least as good.

What the synthetic data is and is not: sense time series are frequency curves of randomly drawn CCOHA words, masked to
OED dates. It is a calibration set with known answers (good: it is the only multi-period sense-labelled data in
public), not a picture of how senses really change. Sentences are Janus generations, so any system that keys on
generation artefacts would look better here than on real text.

Reproduction files: reanalysis/r01 (point estimates), r02 (bootstrap over lemmas), r03 (raw vs normalised PRT), with
.out files. Embeddings and converted data live in the arena-lsc assets (assets.py: arena-lsc-public).
