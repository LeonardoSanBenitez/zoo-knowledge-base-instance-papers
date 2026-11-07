# zhao2025-sirius -- notes (maria, 2026-11-07)

SiriuS is the ancestor of MASS's outer loop: run a multi-agent system, keep the trajectories that reached the
right answer (and repair some that did not), then fine-tune each agent on its own part. Unlike MASS it has a
VERIFIER: QA with gold answers. Unlike MASS it fine-tunes one model PER ROLE.

What the numbers support (s01; every percentage decodes to an integer count):
- Against the same multi-agent prompt without training (CoMM), SFT adds 12-14 of 500 PubMedQA questions. That
  is the honest "self-improvement" effect. On physics (107) and chemistry (65) the margins are 1-7 questions,
  from single runs.
- Against single-agent STaR the gap is large (+52/500), but compute is not matched: three calls against one.
- A second iteration adds 1-4/500, which is flat.
- Per-role models beat one shared model (19/500 for gpt-3.5; actor-critic 35/500). This is in tension with MASS's
  shared-weights design, though the regimes differ.

Lesson for the area: when there IS a verifier, SFT on your own successful multi-agent traces gives a small,
real gain over the untrained multi-agent prompt. Without one (MASS, RHI), the filter is a self-judge, and in MASS
that judge can discard only 3 of 18 runs.
