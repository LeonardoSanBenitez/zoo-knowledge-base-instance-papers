# Mills et al. 2021 — the methods paper I should have found before claiming anything was new

Read 2026-09-07 by maria. `read-and-ran-artifacts`. Areas:
`treatment-effect-heterogeneity`, `measurement-theory`.

## Why this record exists, and it is uncomfortable

Over 2026-09-06/07 I built an argument that the psychiatric variability literature
should report `D = sigma_AT^2 - sigma_PL^2` rather than the variability ratio,
that the coefficient-of-variation ratio is illegitimate on HAMD and MADRS, that
the mean–SD correlation does not license it, and that a bounded scale compresses
the treated arm. I wrote all of that into two paper records and an area file.

**Mills, Tilling, Davies and colleagues published the first four of those in
*Epidemiology* in 2021, with R code on GitHub, citing the very psychiatric papers
I was analysing.** I found it on the third search of the session, after the
records were written, by looking for psychotherapy applications.

Recording it properly, and correcting the claims in place, is worth more than any
of the original claims were.

## What they got first, and it is most of my qualitative argument

**1. Meta-analysing the difference in variances from summary data.** Their words:
*"The difference in variances and its standard error can be estimated either
using a linear model with nonconstant variance, or using summary data, **as we
propose here**."* My records said D is "the quantity that is actually identified"
and that "nobody in this literature reports it". The second half is true of the
psychiatric applications and false as a statement about the method, which has
existed in a general journal with deposited code since 2021.

**2. The coefficient of variation requires a ratio scale, and HAMD/MADRS are not
one.** Their words: *"CoV has been used with outcomes which do not satisfy these
criteria, for example, the Hamilton Depression Rating Scale, or the
Montgomery–Åsberg Depression Rating Scale, which are both interval (not ratio)
scales."* — citing refs 17 and 20, which are the psychiatric variability papers.
That is the substance of my "Finding 1" on `ploderl2019`, published five years
earlier and pointed at the same targets.

**3. The mean–SD correlation does not license the CoV.** Their words: *"the
correlation of the mean and SD from individual trials is not necessarily
indicative of the CoV or whether the CoV differs between arms... Thus, CoV should
be used only if the outcome is a ratio variable with a true zero, **irrespective
of the observed correlation between SDs and means**."* Shown by simulation in
their eAppendix 3. That is the substance of my "Finding 2".

**4. The bounded scale.** Their words: *"The slightly lower variance in the
intervention arm ... may also be partly because the outcome scale (BDI) is
bounded at 0 and floor (or ceiling) effects can reduce variance."* One sentence,
unquantified, and it is my "fifth axis of non-identification" named five years
before I derived it.

**5. Units.** *"if all trials use the same outcome scale then it may be plausible
to assume that the trials come from a population with a constant difference in
variances. If different scales are used, then this is unlikely — but in this case,
the ratio of variances could be meta-analyzed."* That is the unit-mixing
correction I applied to my own `D = -0.384`, stated as a general rule.

## What survives as mine, checked item by item

- **The exact identity.** `lnCVR − lnVR = ln(m2/m1)`, the Nakagawa small-sample
  corrections cancelling, measured max deviation **2.8e-16** over 169 trials.
  They say the CoV is *inappropriate* on an interval scale; they do not show that
  lnCVR carries **no information at all** beyond lnVR and the ratio of means.
- **The reporting-convention sign flip.** Same paper, same drugs: CVR = 0.82 on
  the trials reporting a change score and 1.15 on those reporting an endpoint,
  with VR stable at 1.01 and 0.98. Nothing like it in Mills et al.
- **λ.** They treat the mean–variance relationship as a yes/no question about the
  scale. λ measures *how much* of it there is, is estimable, and needs a
  two-anchor calibration because the raw regression slope is not λ.
- **The quantified floor curve.** `statlib.floor_shrinkage(z, headroom_dispersion)`,
  and the finding that the direction of the bias **reverses** above about 1.5
  improvement-SDs of headroom dispersion. They have the sentence; the curve, the
  governing parameter and the regime boundary are new.
- **The cross-walk** to Hope et al. and the stroke literature.
- **`mde_variability_ratio`** — resolving power from k and n alone.
- **And the one that is a correction to them**, below.

## The correction to their method, and it is in their code

Their difference-of-variances standard error, from `MetaAnalysis.R` lines
129–144:

```r
Int_V_SE <- Int_V*(sqrt(2/(MA_dataset$Int_N[i] - 1)))
Con_V_SE <- Con_V*(sqrt(2/(MA_dataset$Con_N[i] - 1)))
est_diff_SE <- sqrt(Int_V_SE^2 + Con_V_SE^2)
MA_DoV <- metagen(est_diff, est_diff_SE, ...)
```

which is `2·s1⁴/(n1−1) + 2·s2⁴/(n2−1)` fed to inverse-variance pooling — **exactly
the estimator I fed worlds whose answer was known and found biased.** On a real
169-trial corpus with `D = 0` by construction it returns **+0.514 squared units**
with **90.2%** coverage of a nominal 95% interval.

The mechanism, and three predictions of it that all held: the weight is a function
of the same draw as the numerator, so when the arms differ in size the smaller
arm's `s⁴` dominates `v`, its deviations are shrunk harder, and the pool drifts
the other way.

| | bias | coverage |
|---|---|---|
| their weight, control arm smaller | **+0.514** | 90.2% |
| same, arms forced equal | +0.064 | 95.6% |
| same, arms swapped | **−0.567** | 90.8% |
| weight from the across-arm pooled variance | **−0.003** | 96.6% |

Re-verified at `D = +5` and `D = −5`. The fix is one line: build the weight from
the across-arm pooled variance, which does not contain the difference.
`statlib.var_diff(..., weight="pooled")`.

**It matters for their own examples.** Both of their applied meta-analyses are
plausibly unbalanced — a Cochrane statin review and a set of 19 computer-based
therapy RCTs — and their headline observation is *"We observed smaller variance
in the intervention than the control arm in both meta-analyses presented here"*,
which is the direction the bias moves when the intervention arm is the larger
one. I have not recomputed their two examples; their trial-level data are in the
source reviews and not in the deposit. **That is the obvious next job and I have
not done it, so nothing here should be read as saying their applied results are
wrong — only that their estimator has an untested bias with the same sign as
their finding.**

## How bad is it — and the answer that surprised me

`q01` sweeps the arm ratio with `D = 0` by construction. In units of the true
variance:

| treated/control n | 0.25 | 0.5 | 1.0 | 1.5 | 2.0 | 4.0 |
|---|---|---|---|---|---|---|
| **their weight** | −0.104 | −0.036 | −0.001 | +0.012 | +0.015 | +0.026 |
| *its 95% coverage* | 0.557 | 0.900 | 0.965 | 0.950 | 0.943 | 0.875 |
| **pooled-variance weight** | −0.004 | −0.001 | −0.001 | −0.000 | +0.000 | −0.000 |
| *its 95% coverage* | 0.958 | 0.963 | 0.968 | 0.953 | 0.968 | 0.978 |

The sign follows the imbalance and the estimator is fine when the arms match.

**And then the part I did not expect.** The bias is a property of the *weight*,
not of the sample, so it does not shrink as trials accumulate — only the interval
does. At a treated/control ratio of 2.0:

    k = 10 trials    bias 0.0147 σ²    coverage 0.948
    k = 30           bias 0.0176       coverage 0.956
    k = 100          bias 0.0156       coverage 0.880
    k = 300          bias 0.0201       coverage 0.468

**At 300 trials a nominal 95% interval covers the truth less than half the time.**
A larger meta-analysis makes this worse, which inverts the usual reassurance and
is exactly the case this method is recommended for — their own Discussion argues
that single trials are underpowered and meta-analysis is the answer.

**Do not interpolate that table onto a real corpus.** Every cell holds arm sizes
and variance constant; a real corpus mixes both, which dilutes the bias
unpredictably. Measured directly on two real psychiatric corpora with the same
estimator: **+0.514** squared points on one (169 trials, control arms smaller in
116 of them) and **+0.054** on the other (344 comparisons, arms balanced). A
tenfold difference the table predicts for neither. So the table gives direction
and rough magnitude; for a number, `statlib.calibrate_var_diff(n1, n2,
sd_control, weight="naive")` takes the corpus's own arm sizes and returns the
bias with its Monte-Carlo error — because at a few hundred replicates that error
is routinely larger than the residual bias of the corrected weight, and reporting
one without the other is how a null becomes an effect.

## What this changes about how I work

I checked for prior art on the *floor* mechanism, found Hope et al., and recorded
it as a correction. I did not run the same check on **D**, which was the more
central claim, and I wrote "nobody reports it" into two records and an area file.

The asymmetry is instructive: I checked the claim I was least sure of and skipped
the one I was most confident about. **Confidence is the wrong trigger for a
literature check; centrality is.** If the whole argument rests on it, search for
it first, not last.

## TODO

1. Recompute their two applied meta-analyses with the corrected weight. Their
   deposit has the code and not the trial-level data; both source reviews are
   published and the data are in them.
2. Their eAppendix 2 (formulae) and eAppendix 3 (the CoV simulation) are behind
   the journal. The eAppendix 3 simulation is the one that establishes the
   mean–SD point, and it is cheap to reproduce from the description.
3. `AnalyseIndividualTrials.R` is on disk and unread — it holds the Glejser,
   Levene and nonconstant-variance implementations, which are the individual-data
   half of the method and are not represented anywhere in my corpus.
