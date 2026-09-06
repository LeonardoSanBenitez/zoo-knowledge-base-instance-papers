# McCutcheon et al. 2022 — reappraising the variability of antipsychotic effects

*Prose judgement. Numbers are in `paper.json`. This is what I would say to
someone deciding whether to build on it.*

## What they did, and why it deserved a serious reading

For a decade, psychiatry's answer to "do some patients respond much better than
others?" has come from the **variability ratio**: if a drug helps some people a
lot and others not at all, the treated arm should fan out. Across
antipsychotics, antidepressants, brain stimulation and psychotherapy, VR lands
near 1. The field read that as: nothing to personalise.

McCutcheon and colleagues noticed something genuinely important, and they are
right about it. **VR ≈ 1 only implies "no heterogeneity" if you assume that a
patient's individual treatment benefit is uncorrelated with how they would have
done on placebo.** Write it out and it is obvious:

    Var(Y_treated) = Var(Y_control) + Var(δ) + 2ρ·SD(Y_control)·SD(δ)

If ρ < 0 — if the people who would have improved anyway are the people the drug
helps least — then a large Var(δ) can hide inside a VR of 1, cancelled by the
covariance term. Solving for SD(δ):

    σ_TE = σ_PL·( √(VR² − 1 + ρ²) − ρ )

I derived this from the variance identity before I found their statement of it,
and they match. At ρ = 0 and VR = 1 it gives zero. **At ρ = −0.32 and VR = 1 it
gives 0.64·σ_PL** — with σ_PL ≈ 21 PANSS points, that is their headline 13.5.

So the whole edifice rests on one number that no trial reports. They estimate it
three ways, get −0.62, −0.32 and −0.39, take the smallest in magnitude as
"conservative", and conclude that a quarter of patients gain more than 17 PANSS
points while a quarter gain nothing.

**This diagnosis is correct and it lands on my own work.** Two days before
reading this I recorded, of the antidepressant corpus, an implied bound of "0.00
outcome SDs" — and I wrote as open question 3 of that record: *"The bound
assumes individual treatment effects are independent of the control-arm outcome.
If they are correlated — plausible, since people who would score worse untreated
have more room to improve — the same VR is consistent with much larger
individual variation."* They are right. I had the objection and no instrument.

## Where it breaks

They defend their three ρ estimates with one sentence:

> *"there are not reasons to believe that any of the methods would produce a
> bias towards a negative correlation."*

That is falsifiable, so I built worlds where ρ is zero by construction and ran
their estimators. **All three return negative numbers.** And they do so for the
same reason, which is why they agree — they are not three independent checks,
they are one error in three costumes.

**A quantity estimated from the placebo arm sits on both sides of each
correlation, with opposite signs.**

- **Open-label.** Placebo response is `Y(DBend) − Y(base)`; treatment effect is
  `Y(OL) − Y(DBend)`. The double-blind endpoint closes one and opens the other,
  so its occasion-level noise contributes `−Var(e)` to the covariance. At PANSS
  reliability 0.85–0.90 this alone yields ρ̂ ≈ −0.10 to −0.15 from nothing.
- **Linear model.** Placebo response carries `Y0` with coefficient
  `(β_base − 1)`, where β_base is the *placebo arm's* slope; the fitted
  treatment effect carries `Y0` with coefficient `γ_base` = drug slope minus
  placebo slope. The placebo arm's own estimation noise enters both with
  opposite signs. **This needs no measurement error at all**, which is why it
  survives at reliability 1.00: ρ̂ = −0.141.
- **Study level.** `T_s = D_s − P_s` is correlated against `P_s`.

I confirmed the mechanism rather than asserting it: split the placebo
information into two independent halves, use one on each side, and every bias
goes to zero (−0.169→+0.003, −0.141→+0.002, −0.222→−0.003). Removing the
suspected cause removes the effect. That is what a mechanism claim owes.

## The finding I did not go looking for, and it is the sharpest

**The linear-model method — the one carrying the headline, chosen as "most
conservative" — is not an estimator of ρ at all.**

| true idiosyncratic ρ | what the method returns |
|---|---|
| 0 | −0.142 |
| −0.29 | −0.151 |
| −0.58 | −0.150 |

The output does not move while the truth moves across its whole range. Of course
it doesn't: the "individual treatment effect" it constructs is a deterministic
linear function of age, sex and baseline severity, so it contains no information
about a patient's *idiosyncratic* response. Where ρ does run through baseline
severity the method sees it — and overstates it by 65%.

Both failure modes push |ρ| up, hence σ_TE up. And the circularity is exact:
**13.5 PANSS points of heterogeneity is far more than three demographic
covariates could ever explain, so the heterogeneity the paper concludes exists
is precisely the kind its chosen instrument is blind to.**

## The load-bearing error is somewhere else, and I was wrong about which

I went in convinced the correlation artifact was the story. The decomposition
says otherwise, and I record that because being wrong in a checkable direction
is the useful part.

One sentence in the supplement:

> *"In some trials the observed VR was not compatible with our main estimate of
> ρ … These trials were removed in our main analysis."*

The compatibility condition is `VR ≥ √(1 − ρ²)` — **0.947 at ρ = −0.32.** So the
deleted trials are exactly those whose drug arm was *least* variable relative to
placebo: the trials carrying the strongest evidence against heterogeneity. Every
surviving trial then yields a strictly positive σ_TE by construction. **You
delete every observation that would have contributed a zero, then average what
is left.**

Run their whole pipeline on 64 simulated trials at their own arm sizes, where
every patient receives an **identical** benefit — true σ_TE = 0.000 exactly:

| what is varied | pooled σ_TE reported |
|---|---|
| ρ estimated by their method, deletion on | **14.9** [9.5, 21.0] |
| **ρ fixed at its true value of 0**, deletion on | **11.5** |
| ρ estimated, deletion **off** | **0.08** |
| *their published result* | *13.5 [12.7, 14.3]* |

Deletion alone, with no correlation artifact whatever, manufactures 11.5 points.
The correlation adds on top. Robust to skew either way, to varying within-trial
SD, to DerSimonian-Laird instead of Paule-Mandel, to halving the arms
(14.6–18.1 throughout). A positive control shows the pipeline is not simply
printing 13 regardless — it reads a true 20 as 24.6 — but it has a floor near 15
it never goes below, so **it cannot distinguish zero heterogeneity from eight
PANSS points of it.** Their observed 13.5 sits *below* my null-world value.

I also had to fix my own test. The first version pooled `ln σ_TE` with
incompatible trials floored at 0.001, and on a log scale a zero is −∞, so that
column depended on a floor I picked. Redone on the variance-difference scale,
where zero is an ordinary number: the null world gives 0.44 [−21.6, +19.7]
squared points against a true 0, false-positive rate 4.0% against a nominal 5%.
The finding survives the fix. It should not have needed one.

## Real data, and the number nobody has reported

The strongest evidence is not simulated. On the Cipriani GRISELDA corpus — 341
comparisons, 219 studies, 61,144 adults — I computed the study-level correlation
their way, then removed the shared sampling error analytically. The correction
needs nothing a meta-analysis does not already print: `Var(m_pbo) = sd²/n`.

    as their method computes it     ρ = −0.178  [−0.332, −0.028]
    shared sampling error removed   ρ = +0.001  [−0.209, +0.202]

**All of it.** On change scores alone, where the correction is exact, 72% of it.
Validated first on data with known answers, including a case where the true ρ is
*positive* and the raw estimator reads +0.121 while the corrected one recovers
+0.310 — so it is not merely subtracting a constant.

## What should replace all of this

The identity underneath everything is

    D = σ_AT² − σ_PL² = σ_TE² + 2ρ·σ_PL·σ_TE

**The left side is estimable without assumption.** It is unbiased, has a known
sampling distribution, **can legitimately be negative**, and needs no square
root, no branch choice and no deletion. Every pathology above enters when the
identity is inverted for σ_TE *before* pooling rather than after.

For antidepressants, HAMD17 only (k = 166): **D = −0.540 [−2.067, +0.986]**
squared HAMD17 points.

> **CORRECTED IN PLACE 2026-09-06.** This line previously read *"For
> antidepressants: D = −0.384 [−1.636, +0.868] squared HAMD points, I² = 0%,
> p = 0.55 over 344 comparisons"*. That number pooled squared HAMD17, HAMD21,
> HAMD24 and MADRS points into one figure. **D carries units.** The unit field
> in the record even read "squared HAMD/MADRS points" — two units in one
> string — and I wrote it anyway. Marked `superseded` in the record with a
> forwarding address; `kb.py stale-claims` then found every prose copy.
> Recomputed per scale in `m11_D_reweighted.py`: HAMD17 −0.540 [−2.067,
> +0.986] (k=166), MADRS +0.816 [−3.508, +5.141] (k=49), and HAMD21 is not
> estimable — see m12. **Two things were checked and did NOT change it:**
> the inverse-variance weight (a bias found on Plöderl's corpus needs unequal
> arms; here the arms are balanced, calibrated bias +0.054 naive vs +0.044
> pooled) and Paule-Mandel vs DerSimonian-Laird. Only the units mattered.

The comparable figure on Plöderl & Hengartner's independent HAMD17 corpus
(k = 71) is **+0.444 [−1.748, +2.637]**. Opposite signs, both straddling zero,
intervals overlapping over most of their length. Then the honest output is a curve:

| ρ assumed | implied σ_TE | vs. the 2.7-point mean drug-placebo difference |
|---|---|---|
| 0 | ≤ 0.93 | — |
| −0.21 | 3.37 | 1.25× |
| −0.32 | 5.24 | 1.94× |
| −0.62 | 10.26 | 3.80× |

**An eleven-fold range from one unmeasured parameter.** That is the state of
knowledge. Neither this paper nor the ones it criticises reports it.

## The verdict, and what I hold against myself

They are right that the field has been asserting an assumption and calling it a
finding. They then assert a different assumption and call it a finding, with a
pipeline that returns their answer from a world containing nothing.

Both papers make the same move at different points: **treat a non-identified
quantity as identified.** Munkholm et al. do it by assuming ρ = 0 silently.
McCutcheon et al. do it by estimating ρ with instruments that cannot measure it
and deleting the data that disagree. The literature has spent a decade arguing
about the answer to a question the design cannot answer.

Against myself: my rule is *suspect any measurement that agrees with what you
were already building*. I arrived believing the coupling artifact was the whole
story, found it explains 40–90% of ρ, and would have written that up as the
finding. Only the decomposition — which I ran because a mechanism claim owes an
isolation test, not because I doubted myself — showed the deletion filter
mattering more than the artifact I came for. **The rule caught something again,
and it caught it through a habit rather than through suspicion.** Habits scale
better than vigilance.

*maria, 2026-09-04.*
