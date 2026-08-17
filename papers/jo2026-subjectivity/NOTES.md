# Notes — Jo, Garg & Raghavan (2026), The Subjectivity of Monoculture

Author: maria. Session 2026-08-07. Structured record: `paper.json`.

## Judgement

The most important paper I read this session, and the one I would keep if I had to
discard everything else. It converts a measurement dispute into an identifiability
result. Theorem 1 is a de Finetti-style representation: for any joint distribution of
binary outcomes across m models, a latent variable exists that makes them conditionally
independent with the observed marginals. So "these models are too correlated" is not a
fact about the models. It is a discrepancy from a baseline somebody chose.

That could have been a purely destructive point. The null-ladder construction is what
makes it constructive: nulls are nested, minimal excess is monotone in expressiveness
(Prop 2), residual covariance vanishes as K grows (Thm 3). So the question is not
"is there monoculture" but "at what level of the ladder does the correlation survive,
and is that level a defensible description of the world". That is answerable.

## Reading-method mistake worth keeping

I first fetched this through a summarising tool. What came back was fluent and largely
generic — "evaluator consensus artifacts", "coordinated subjective judgments" — which is
not what the paper says and reads like a small model filling gaps. It missed Theorem 1
entirely, i.e. the actual content. The PDF was already on disk from the same call.
Reading it directly gave the theorems, the K-sweep, the IRT-0.5 vs IRT-1 contrast and
the contributor-clustering result.

**Rule that came out of this, now in CONTRIBUTING.md:** a summariser decides whether to
download, never what the paper says.

## The gap they leave open, which is where my own work went

Section 3.2.2 and footnote 4: they work on binary correctness Y in {0,1}. They say
explicitly that Kim et al. and Goel et al. use answer-choice information, that this
"indeed provides additional information about cross-model agreement", and that their own
per-choice fit is "naive". So their null carries item *difficulty* and model *ability*
but nothing about **which** wrong answer is chosen.

That is exactly where the ability-graded concentration effect lives, and it is invisible
to them by construction. My reanalysis occupies that gap rather than duplicating them,
and lands in the same place by a different route — worth more than agreeing by the same
route would be.

## Figure 3 is under-discussed by its own authors

On HuggingFace, after fitting a 2-D IRT null, the residual model clusters track
**contributor** — DreadPoor, MaziyarPanahi, T145, bunnycore, dnhkng, lemon07r,
newsbang, qingy2024, sometimesanonion — i.e. who fine-tuned or merged the model. The
competing hypothesis (clusters = task specialisation) is killed by a PCA on
accuracy-stratified-by-question-type in which PC1 explains essentially everything.

Translated into the question mark asked me: what survives a good null is shared
**pipeline** — not shared substrate, not shared skill profile. That is a real data point
on the twins-vs-co-trained-raters question and nobody frames it that way. HELM by
contrast collapses to ~1 dimension ≈ accuracy, because it is closed models with no
shared merge lineage.

## Artifacts

None. No code, no data-availability statement in v1 — recorded as `status: absent`.
Worth stating plainly: the paper's thesis is that the null-model choice must be
inspectable and defended, and the null-fitting code, the one artifact that would let a
reader inspect *their* choice, is not published. The inputs are public (HELM, HF
leaderboard, ACSIncome); the IRT fitting would have to be reimplemented.
