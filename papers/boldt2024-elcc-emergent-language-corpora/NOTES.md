# Boldt & Mortensen (2024), ELCC — notes

Author: maria, 2026-10-16. Skimmed as a resource for my neuralese interest. The resource is good:
73 emergent-language corpora from 7 systems, pinned on Hugging Face, with code, so anyone can
study emergent "languages" without training agents.

The one analytic claim I wanted to check -- that XferBench, a "humanlikeness" score, tracks
unigram entropy -- I could not: the scores are not released and the figures are raster. If it
is true, it deserves the same suspicion as the colour-naming case. A token stream with the right
entropy and no structure might look "human-like" to the metric. The shuffled-token control is
the obvious first experiment, and it needs a GPU I do not have free today.
