# fedorova2024-axolotl24-overview — notes (maria, 2026-11-03)

Why it matters for SemEval-2027 Task 3: it is the closest precedent for sense-level evaluation, and its lesson is a
metric lesson. When the score rewards assigning usages to known glosses, a WSD system wins even if it never detects
change (Deep-change: no novel senses, first place). Task 3 avoids that for Subtask 1 (no inventory given, BCubed over
induced clusters) but Subtask 2 is exactly a one-gloss WSD decision, so gloss-matching models (GlossReader) are the
natural tool there.

Its data are useful but uneven: Finnish is clean (manual target positions) and large; Russian splices two dictionaries
(Dal for old, CoDWoE for new) and lacks target offsets, so 'change' there partly reflects dictionary granularity.
