# wang2026-rethinking-harness-evolution -- notes (maria, 2026-11-07)

This is the independent counterweight to the Sakana pair (MASS, RHI). Its question is the one those papers skip:
**against a baseline that spends the same budget on plain retries, does evolving the harness win?** On
Terminal-Bench 2.1 the answer is no: parallel sampling with self-selection beats it without tests, and with
tests both parallel sampling and sequential refinement beat it. The evolved harness also gains nothing on 34
held-out tasks.

**Two corrections to the paper's own reading (w01).**
- Its tables contain a free replicate. Direct sampling is the same procedure in Tables 1 and 2, and the two runs
  differ by 0.0, +0.6 and -2.5 pp. Per-model differences of about 2 pp are therefore noise.
- "Overfitting to the search set" requires an in-sample gain that disappears out of sample. The in-sample pass@1
  gains are -0.8 and +2.1 pp, and held-out is 0.0. There is nothing to overfit. Read it as "no harness gain at
  pass@1 anywhere".

**Where harness evolution does work here:** long-horizon games with rich, verifiable feedback, starting from an
already strong harness, where the agent writes its own tools (ARC-AGI-3: 43 -> 78 RHAE). The setting is the
opposite of MASS and RHI, which use LLM judges, no verifier and open-ended deliverables.

**For the area.** RHI compares its harness only against the same model at higher reasoning effort, never
against best-of-k at equal cost. This paper makes that missing baseline the standard.
