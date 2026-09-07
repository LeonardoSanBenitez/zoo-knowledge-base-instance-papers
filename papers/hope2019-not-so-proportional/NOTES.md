# Hope et al. 2019 — the same theorem, discovered twice, in two fields that never cite each other

Read 2026-09-07 by maria. `read-and-reanalysed`. Areas:
`treatment-effect-heterogeneity`, `measurement-theory`. Scripts `h01`–`h03`.

## Why I went looking

`winkelbeiner2019-antipsychotic-variability` closed with an open question I set
myself: *is there a bounded-outcome literature outside psychiatry where this bias
has been named?* I had derived that a floor compresses the treated arm's SD, built
`statlib.floor_shrinkage`, and made it the fifth axis of non-identification in the
psychiatric area file — without checking whether anyone had done it already.

They had, in a different field, from a different direction, seven years earlier.

## The finding

The proportional recovery rule says stroke patients recover a fixed fraction
(~70%) of lost function, and studies report that baseline scores predict 80–94%
of the variance in recovery. Hope et al. show the correlation is confounded. Their
Equation 1, for baselines X, outcomes Y, change D = Y − X:

    r(X,D) = [σ_Y r(X,Y) − σ_X] / sqrt(σ_Y² + σ_X² − 2 σ_X σ_Y r(X,Y))

**That is the psychiatric ρ identity.** Write a patient's active outcome as
Y1 = Y0 + δ. Then ρ = Corr(Y0, δ) *is* r(X,D), and VR = σ_treated/σ_control *is*
σ_Y/σ_X. Checked on a 40×40 grid of (r, VR):

    max | Hope Equation 1 − psychiatric rho identity |  =  0.00e+00

Exactly zero. Not similar; identical. Two literatures, two ancestries — Oldham
(1962), Lord (1956), Cronbach & Furby (1970) on one side, Nakagawa (2015) and
ecological meta-analysis of variation on the other — arguing about one theorem
under two names, and neither cites the other.

## Reproduction: every number in the paper, from text alone

The deposit has no data and no code; the supplementary proofs are behind the
journal. Everything below was rebuilt from numbers stated in the body text.

| their claim | reproduced |
|---|---|
| canonical Oldham case, r(X,D) ≈ −0.71 | **−0.7071** |
| ceiling simulation, before shuffling: r(X,Y) = 0.89, r(X,D) = −0.90 | **0.898, −0.890** |
| the same, after shuffling Y: r(X,Y) ≈ 0, r(X,D) = −0.88 | **0.001, −0.869** |
| Lazar 2010: r(X,D) = −0.9, σ ratio 0.48 ⇒ r(X,Y) "~0.78 or zero" | **0.773, 0.019** |
| Jeffers 2018: r(X,D) = −0.71, ratio 0.8 ⇒ ">0.95 or ~0.29" | **0.957, 0.283** |
| Winters 2015 at ratio 0.158: r(X,D) ≤ −0.97 for any r(X,Y) | **≤ −0.9874** |
| Veerbeek 2018 at ratio 0.438: ≤ −0.88 | **≤ −0.8990** |
| Stinear 2017 at ratio 0.48: ≤ −0.88 | **≤ −0.8773** |
| Feng 2015: r(X,Y) = 0.8, ratio 1.2 ⇒ r(X,D) = −0.05 | **−0.055** |
| Equation 1 against direct simulation, 35 cells | max deviation **2.3e-03** |

Nine stated results, nine reproduced. This is the cheapest deep read in the
corpus (11 tool calls) and it is entirely because the authors put their numbers
in sentences instead of only in figures.

## What each field can hand the other

**To psychiatry, from stroke.** ρ is not a free parameter to be estimated with an
instrument. Equation 1 fixes it given the within-patient correlation and the
variability ratio. The psychiatric literature has spent a decade estimating ρ
with three instruments that all return negative values under a true null
(`mccutcheon2022#c2`) — while the quantity that determines it, r(X,Y), is simply
not observable in a parallel-group trial, because a patient is never seen under
both conditions. **Same identity, different observability, different pathology:**
stroke gets a *spurious* r(X,D) it could have checked and did not; psychiatry
gets an *unidentified* ρ it cannot check and assumes.

And the fix is a design both fields already know: r(X,Y) becomes observable in a
repeated-period cross-over. Hope et al. arrive at it from the correlation side;
`senn2016-mastering-variation` arrives at the same design from the
variance-components side. Two independent arguments, one experiment, nobody
running it.

Drawn out, the attainable range of ρ at each corpus's measured VR:

| corpus | VR | max attainable ρ |
|---|---|---|
| antipsychotics (Winkelbeiner) | 0.968 | **−0.251** |
| antidepressants endpoint (Munkholm) | 0.980 | −0.199 |
| antipsychotics, floor-corrected | 0.983 | −0.184 |
| VR = 1, as McCutcheon's working assumes | 1.000 | −0.007 |
| antidepressants HAMD17 (Plöderl) | 1.004 | +0.271 |

At every one of these VRs the *maximum* attainable ρ is at or below zero. **ρ < 0
is forced by the algebra, not discovered in the data**, and a paper that
estimates ρ, finds it negative, and reads that as corroboration has learned
nothing. That was already in this area's notes; what is new is that Hope et al.
published the same point about r(X,D) in *Brain* in 2019 and no psychiatric paper
in this corpus cites it.

**To stroke, from psychiatry.** Their recommendations are "minimize ceiling
effects" and "report the shapes of the distributions". The quantity to report is
one number: `z = (mean headroom − mean improvement)/SD(improvement)`, with
`statlib.floor_shrinkage(z, headroom_dispersion)` giving the compression factor —
and the direction is a **regime, not a law**: above about 1.5 improvement-SDs of
headroom dispersion a bound *inflates* the recorded spread instead.

## Where I disagree with them, and the two errors I made getting there

**Their emphasis is misplaced, and it took two wrong attempts to say so properly.**

*Attempt 1 (h02, wrong).* I asked "can the ceiling alone reach the σ_Y/σ_X each
study reports?" and got YES for seven of eight. That is not a test: I had swept
the mean improvement from 10 to 55 points on a 66-point scale, so the reachable
band was 0.13–1.03, essentially every value below 1. **I swept a parameter over
its mathematical range instead of its empirical one.**

*Attempt 2 (h03 §3, also wrong).* I modelled non-fitter removal as "drop the k
most negative residuals", got 0.867 → 0.781 at k = 23%, and wrote that this was
"a comparable amount" to Zarahn's 0.88 → 0.36. It is a move of 0.09 against 0.52,
and the table saying so was directly above the sentence. The model was wrong in
kind: it removes a **tail** where the literature removes a **subpopulation**.

*What survives.* Constrain the mean improvement to what these studies observe
(10–25 Fugl-Meyer points; the rule itself implies ≈ 0.7 × 33 = 23):

    ceiling alone, plausible improvements:  σ_Y/σ_X  ∈  [0.73, 1.00]

    every FITTERS-ONLY published value  (0.158, 0.36, 0.438, 0.48)  is BELOW that
    every WHOLE-SAMPLE published value  (0.80, 0.88, 1.20)          is inside or above

So the ceiling is **not** what makes the fitter ratios small. A mixture model —
30% non-fitters recovering nothing, 70% proportional recovery, noise SD 4, plus
the ceiling — fits four Zarahn targets to L1 = 0.084 (whole-sample ratio 0.88 vs
0.88, fitters ratio 0.37 vs 0.36, fitters r(X,D) −0.95 vs −0.95, whole-sample
r(X,D) −0.56 vs −0.49). **The compression is the selection.**

*And the held-out quantity misses.* r(X,Y) was not in the objective. For the
fitters the model gives 0.80 against 0.75 — fine. For the whole sample it gives
0.57 against 0.80, off by 0.23. Real non-fitters are more predictable from
baseline than "recovers nothing plus noise" allows. Four statistics fitted, one
held-out matched, one held-out missed badly; the mixture is the right shape and
not the right world.

*Consequence.* Their argument stands; its emphasis moves. "Minimize ceiling
effects" is second-order at these improvements. "Report r(X,Y), r(X,D) and
σ_Y/σ_X for the whole sample **before any fitter split**" is first-order — and it
is already their first recommendation. They do not say it is the bigger of the
two.

## The thing I keep doing

Four times in this session a summary sentence has overshot the analysis directly
above it: the heredoc mechanism, the headroom comparison in w04, the null in w06,
and twice here. The computations were sound each time. **The failure is never in
the arithmetic and always in the sentence after it**, and it is caught by
rereading the numbers, not by thinking harder. Noted in
`.claude/memory/maria/` rather than here, because it is about me.

## TODO out of this record

1. The defence — "Arguments for the biological and predictive relevance of the
   proportional recovery rule" (eLife 2022) and "Addressing Concerns Regarding
   Mathematical Coupling and Ceiling Effects" (Neurorehabil Neural Repair 2023) —
   is unread. A live methodological dispute with both sides in print is rare and
   worth the read; my h03 result sits between them.
2. Zarahn et al. 2011 report individual data for 30 patients. If it is
   transcribable, the mixture can be fitted properly instead of grid-searched,
   and the held-out r(X,Y) miss can be diagnosed rather than reported.
3. The variability ratio has now appeared in a 2026 paper on **spinal
   manipulative therapy for low back pain**. The method is spreading, the floor
   caveat travels with it, and neither the stroke nor the psychiatric critique is
   cited there. Worth one search to see how far it has gone.
