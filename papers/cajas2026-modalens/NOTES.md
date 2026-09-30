# Notes — cajas2026-modalens

Author: maria, 2026-09-30. Main text read in full (45 pp PDF, appendices not read). The advertised
repository is 404, with a control, so nothing was run.

## design / what it identifies

- **Design:** each case rendered twice, own image vs. another study's image, with question and report fixed.
  Report availability is the manipulated factor, and the outcome is whether the answer (or the logit
  margin) changes.
- **Identifies:** **sensitivity to the image intervention**, i.e. whether the image is *used*. It does not
  identify **visual correctness**, because every label is derived from a report. The authors say this in
  their own abstract, which is the main reason to trust the rest.

## Why this paper is the methodological template for the Dojo VLM work

Anyone about to benchmark a general VLM (the CosmosReason2 ticket) on medical images inherits the
question this paper answers carefully: *does the model use the image at all, or answer from the text and
its priors?* A plain accuracy number cannot tell those apart. A paired swap can, and it costs one extra
forward pass per item. Three details generalise:

1. **Readout choice changes the number but not the direction.** Lowercase first token vs token families
   vs generated answer moves the report-absent rate from 10.3% to 17.4% on one design. Report a
   readout-validation table or do not report a flip rate.
2. **Prompt order changes the magnitude.** Putting the text block first shrinks the report effect from 12.4
   to 7.8 points on identical trials. A flip rate is a property of (model, prompt), and never of the model
   alone.
3. **Pooled rates hide ceilings.** Five of 14 findings sit at a near-100% "yes" without the report, so they
   cannot flip. The pooled number averages "cannot move" with "moves a lot".

Point 3 is what connects this paper to `cajas2026-agents-catching-agents#c4`. See that record.

## Kept honest

The warning prompt ("the report may be wrong") does nothing (+0.28 points, CI spans zero). The steering
and probe-transfer results are negative and are reported as such. The layer claim is a bound, not a
locus. I have no quarrel with the paper's own reading. My only addition is that the magnitude should
always be quoted with the order caveat.
