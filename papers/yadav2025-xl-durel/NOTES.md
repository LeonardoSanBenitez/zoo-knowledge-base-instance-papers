# yadav2025-xl-durel — notes (maria, 2026-11-03)

A better graded usage-similarity model (alpha .67 vs .58 on ordinal WiC) gives only a small gain when its similarities
are turned into sense clusters (+0.01-0.05 BCubed F on clean sets, nothing on change ranking). Read with the arena-lsc
negative results: once the encoder is WiC-trained, the remaining errors on task-style data are senses that need
world knowledge to tell apart (Swedish fröken as title vs profession), and better graded similarity does not supply it.
Authors verified on the PDF title page (Sachin Yadav, Dominik Schlechtweg; Stuttgart).
