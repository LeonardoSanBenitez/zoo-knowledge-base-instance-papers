# cassotti2025-hypothesis-driven-lsc — notes (maria, 2026-11-03)

Read because SemEval-2027 Task 3 Subtask 2 ("Hypothesis-Driven Change Detection": given one sense definition, mark
which usages express it) is named after this paper, and its authors are among the task's organisers.

What it gives a participant: the organisers' mental model of Subtask 2 is *definition -> synthetic usages ->
prototype embedding -> similarity ranking*. The paper never thresholds the ranking, so a participant still has to
choose how to turn similarity into 0/1 — and the paper's own numbers (top-1 similarities 0.88-0.98, including an OCR
artefact at 0.88) suggest raw XL-LEXEME cosines are compressed near 1 for same-lemma usages, i.e. a global threshold
will be fragile. Per-word calibration (e.g. relative to the word's own similarity distribution) is the obvious
alternative to test.

Janus is English-only (OED). For the other five task languages the analogous generator would be a multilingual LLM
prompted with the definition, or real dictionary examples.

Nothing to reproduce: no artifact, no evaluation numbers.
