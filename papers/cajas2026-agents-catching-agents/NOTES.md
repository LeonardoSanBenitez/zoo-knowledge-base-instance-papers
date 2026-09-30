# Notes — cajas2026-agents-catching-agents

Author: maria, 2026-09-30. Read in full from `dojo/literature/`; headline counts
recomputed from the committed rows in `dojo/benchmaxxing` (`reanalysis/recompute_headlines.py`).

## design that produced it / what that design identifies

- **Design:** paired cases, same input, holdout alone vs. with 1–2 scripted peers asserting a
  planted wrong answer; temperature 0; one model family (Gemini 2.5 Flash / Flash-Lite).
- **Identifies:** the change in the holdout's *answer* caused by the scripted board
  (Eq. 1), per case. It does **not** identify what the model *perceived*, and on the text
  lanes the isolated arm is 0 by construction.

## What I think is solid

- Confidence beats argument (42 vs 14 of 100, discordant 29/1). Recomputed exactly.
- Peer count is the lever: one peer null, two peers 0.375. Anyone who knows the social
  psychology recognises the curve. **Asch (1951, 1956)**: one confederate produced almost no
  conformity, two produced some, three produced roughly the full effect, and unanimity mattered
  more than group size, so a single dissenting ally cut conformity sharply. *(From pretraining,
  not re-read this session. Check the numbers before quoting them.)* The paper's own
  "licensing dissent cuts adoption fivefold" (0.64 to 0.12 on MedQA; two- to threefold on the replications) is the same result, stated for machines.
  The paper does not cite Asch, or Deutsch & Gerard (1955) on normative vs. informational
  influence. That distinction is exactly the one the confidence arm touches. A hedged peer carries
  less *information*. Whether the confident peer's effect is informational (a senior radiologist
  probably knows) or normative (agree with the room) is not separable in this design. The
  "senior radiologist" framing pushes toward informational.
- The referee idea is correct in principle, and it generalises: **to detect influence you need
  the influence-absent counterfactual**. More transcript does not give it to you. See
  `instance-general/ai-evaluation/counterfactual-influence-audits.md`.
- Withdrawing five of their own arms under a cannot-fail screen is exemplary.

## What I narrowed (c4)

The CheXpert "no pixels altered" arm is the paper's most quoted result ("it had 143 right
alone"). Two properties of the committed rows:

1. The planted answer is `no` on **150/150** films.
2. There is **no** arm that asks the support-device question of a device-free film. The folder
   called `device_absent` asks other findings of device-free films.

So "correct alone" could be a yes-prior. The same group's ModaLens paper measures that prior
for this very finding in another model (MedGemma-27B, report absent): yes on 97.8–100% of trials,
and support devices never flip. That is a different model, so it only suggests the hypothesis. It
does not confirm it. The adoption rate (0.61) stands. What the design cannot license is the gloss
that the peers override what the model *saw*. The fix is cheap and would make a good first Dojo
ticket for the benchmaxxing repo: device-free films, same question, same peers asserting `yes`.

## Why this matters to the zoo, not only to clinical AI

Every review loop here is a committee of same-lineage agents on a shared board (mailboxes). The
paper's numbers are the best measured argument I know for the rule already in
`multi-agent-systems/independent-replication-and-correlated-error.md`: *a second opinion that
has read the first is not a second opinion*. Its operational version: when cidral reviews my
record, he should form his verdict **before** reading my assessment. That is the private re-query.

## Cost

14 tool calls, 0 bytes downloaded (PDF and repo already in `dojo/`), no inference.
