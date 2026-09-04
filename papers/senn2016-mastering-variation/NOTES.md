# Senn 2016 — mastering variation

*Read after spending a session dismantling a 2022 paper, and it reorganised the
whole session. The lesson about my own method is at the end.*

## The paper in one table

| design | identifies | error term |
|---|---|---|
| parallel group | A | **B + C + D** |
| classical cross-over | A, B | **C + D** |
| repeated-period cross-over | A, B, **C** | D |

A = between treatments. B = between patients. C = **patient-by-treatment
interaction**. D = within patients, occasion to occasion.

C *is* σ_TE². C is what "some patients respond better than others" means. And in
a parallel-group trial C is confounded with B and D — not poorly estimated,
**not estimated at all**. "Identification of differential response to treatment
requires replication at the level at which differential response is claimed."

The entire psychiatric variability-ratio literature — antipsychotics,
antidepressants, brain stimulation, two psychotherapy corpora — consists of
attempts to read C off parallel-group trials. This was published in 2015.
McCutcheon et al. cite the adjacent Senn 2018 *Nature* piece and adopt none of
the argument.

## The counter-example that costs the VR statistic its meaning

Senn's own, and it is a fourth kind of non-identification I had not articulated:

> compare an oral with an intravenous formulation. Absorption may vary from
> patient to patient — that is interaction, real individual response. It may
> also vary from occasion to occasion *within* a patient — that is
> heteroscedastic noise, and there is no individual response at all.

Both raise the treated arm's variance. VR is identical. **A larger variance in
the treated arm is not evidence of individual differences; it is evidence of
something.** No statistical care removes this, because it is a design fact.

So the tally for the variability ratio now runs to four:

1. it bounds heterogeneity rather than measuring it (mixture equivalence);
2. lnVR and lnCVR test different nulls and nobody says which was chosen;
3. it needs ρ, the correlation between individual effect and control outcome,
   which no parallel-group trial observes;
4. **and even given all three, an inflated variance may be C or may be D.**

## The two worlds

Figures 2 and 3. A double cross-over, 1000 patients, each contributing *two*
independent estimates of their own treatment effect. Both worlds have the same
mean difference (0.5 L FEV1) and the same SD of that difference (0.2 L). They
differ only in how well a patient's effect in periods 1–2 predicts their effect
in periods 3–4: r = 0.90 versus r = 0.02.

    r = 0.90  ->  sigma_C = 0.19 L   individual response is real and repeatable
    r = 0.02  ->  sigma_C = 0.03 L   the apparent variation is occasion noise

**A parallel-group trial sees identical data in both. So does a classical
cross-over.** Only the replicate separates them.

I re-ran this from the parameters in his appendix — which are stated in words,
precisely enough to reproduce seven years later, with no data deposit anywhere.
Worth holding against the reflex that reproducibility requires a repository. A
paragraph did it.

**And I got it wrong the first time.** I read the figures as pairs of *(placebo,
active) outcomes* correlated r, implemented that, and wrote "REPRODUCES" into an
artifact record. They are pairs of *differences* across replicate period-pairs.
Rereading the body text with the appendix caught it. The correction made his
point stronger than my misreading had: in the correct version the *marginals*
match too, so a classical cross-over is fooled as well, not only a parallel-group
trial. Corrected in place in both records rather than quietly rewritten.

One honest number from the re-run: analytically the two worlds differ 6.7-fold
in σ_C; at his own n = 1000 the simulation recovers 4.4-fold. The gap is
sampling noise in the estimated replicate correlation. **Even a double
cross-over in a thousand patients pins σ_C down only loosely** — that is the
price of the only design that identifies it at all, and it should temper any
enthusiasm for "just run n-of-1 trials".

## What it does to my own earlier work

On 2026-09-02 I built a diagnostic that asks whether a corpus supports *additive*
or *multiplicative* homogeneity, ran it on antidepressants and on mindfulness,
and got "additive" both times. I recorded that as a finding about those
treatments.

Senn, following Berrington de Gonzalez and Cox: provided the response
distributions do not cross, **a transformation making the effect additive nearly
always exists.** So "the corpus chooses additive" is substantially weaker
evidence about the drug than I took it to be — it is partly evidence that the
outcome scale was already a sensible one. The operational half of that work
survives (lnVR and lnCVR test different nulls; the choice is load-bearing; no
paper states it). The interpretive half is narrowed, and I have marked it so.

The converse still bites, and Senn says so: a *qualitative* interaction — one
that reverses sign for some patients — cannot be transformed away, and my
diagnostic would not detect one.

## The lesson about method, which is the reason this record exists

I found the coupling artifact, the sensitivity failure, the deletion filter, the
null-world result and the analytic identity **before** reading the paper that
says the question was never identifiable. All of that work is still correct and
still worth having — an audit of a specific pipeline is not the same object as a
design argument, and the field will not be moved by the design argument alone,
since it has been available for a decade and has not moved it.

But the order was wrong. **I audited an estimator for three hours before asking
whether the estimand existed.** The cheap question — *what does this design
identify?* — comes first, costs almost nothing, and would have told me where to
point the expensive machinery.

Adding it to the method: before reanalysing a quantity, write down what design
produced it and what that design can identify. If the answer is "not this
quantity", the reanalysis is about the estimator's behaviour, not about the
world, and should say so in its first sentence.

*maria, 2026-09-04.*
