# Notes — xiang2026-dojo

Author: maria, 2026-09-30. Read in full.

It is a position paper: a platform proposal with three evaluation planes, a human calibration protocol,
and a planned comparative study. There is no software yet (`dojo-health` is not on PyPI; the GitHub repo is
a website). The empirical work of the group lives in separate papers: the referee in
`cajas2026-agents-catching-agents` and modality reliance in `cajas2026-modalens`.

Two things worth keeping:

- **"Who evaluates the evaluators?"** The decoy-calibration protocol is the catch-trial logic of
  psychophysics and crowdsourcing, applied to clinical evaluators. It is correct in principle. The open
  practical question is sample size: at a 5-10% decoy rate an evaluator must do many evaluations before
  their calibration score means anything.
- **The paper cites its own group's BODHI result inaccurately** (1,800 observations for 2,000, and d values
  that measure seed reproducibility; see `arslan2026-bodhi-engineering`). This is a small instance of the
  paper's own thesis: evaluation claims need an outside check, including the ones about the evaluation
  framework.

Naming: the zoo's `dojo/` workspace is a contribution workflow that borrows the name. It is not this
platform.
