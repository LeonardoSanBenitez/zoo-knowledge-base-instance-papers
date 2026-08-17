<!--kb
id: papers-llm-monoculture
labels: kind:paper-notes, area:llm-monoculture, area:multi-agent-systems
triggers: correlated errors, algorithmic monoculture, outcome homogenization,
          model diversity, ensemble independence, LLM-as-judge inflation,
          excess agreement, null model, item response theory, distractor
verified: 2026-08-07
-->

# LLM monoculture and correlated errors — per-paper notes

Author: maria. Started 2026-08-07.

**Through-line.** The field asks "do different models fail in the same way?" and
answers with an *agreement statistic measured against a null*. Between mid-2025 and
early 2026 the argument moved from the statistic to the null, and the null turns out
to be the whole ballgame: agreement is not an absolute property of a model population,
it is a discrepancy from a baseline the analyst chooses. Read Kim25 and Jo26 together
or neither.

Format per paper: the `<!--kb-->` block is the machine-readable record (see
`instance-papers/index.md` for the field contract); prose below it is the judgement.

---

<!--kb
id: paper:kim2025-correlated-errors
labels: kind:paper, venue:ICML2025, area:llm-monoculture
cite: Kim, Garg, Peng & Garg (2025). Correlated Errors in Large Language Models. ICML 2025 (PMLR 267). arXiv:2506.07962
triggers: agreement when both wrong, 60% agreement, systemic exclusion, LLM-as-judge
          accuracy inflation, same provider same architecture, resume screening
methods: pairwise-agreement-conditional-on-both-wrong, ols-on-pair-features,
         stable-matching-simulation, llm-as-judge-audit
quantities: |
  agreement_when_both_wrong_HELM = 0.60 (baseline 1/3; 71 models x 14,042 MMLU items)
  agreement_when_both_wrong_HF   = 0.423 (baseline 0.127; 349 models x 12,032 items)
  pairs_above_baseline = 100% (HF), 97.5% (HELM)
  regression_R2 = 0.340 (HF) / 0.613 (HELM) / 0.415 (Resumes)
  same_company_coef = +0.066 (HF), +0.022 (HELM), +0.021 n.s. (Resumes)
  same_architecture_coef = +0.076 (HF)
  systemic_exclusion: 0.75 same-LLM, 0.49 same-company, 0.43 random-LLM, 0.24 uniformly-random
  systemic_exclusion_20_distinct_LLMs = ~0.20 (vs ->0 under random preferences)
  outlier_pair = google/text-unicorn@001 vs writer/palmyra-x-v3, 0.9987
stance: extends:bommasani2022-homogenization; extends:kleinberg2021-monoculture;
        rebutted-by:jo2026-subjectivity; reanalysed-by:maria2026-marginal-competence
artifact: github.com/nikhgarg/llm_correlated_errors_public — BROKEN. data/helm/all_mmlu_data_limitedcols.csv
          is a git-LFS pointer whose object 404s ("Object does not exist on the server"),
          verified 2026-08-07 by maria. Code, derived pair-level tables, regressions and
          figures all present: re-executable, NOT reanalysable. Raw data recoverable
          independently from storage.googleapis.com/crfm-helm-public.
verified: 2026-08-07
-->

**Kim, Garg, Peng & Garg (2025) — Correlated Errors in Large Language Models.**
Three datasets (HELM MMLU, HF Open LLM Leaderboard 2, a hand-built 1,800-pair
resume/job-description set with 450 human labels). The metric is agreement rate
*conditional on both models being wrong*, chosen deliberately to avoid the confound
that two accurate models trivially agree on correct answers.

Downstream half is the stronger half and is under-cited relative to the headline:
in LLM-as-judge, a judge **inflates** the measured accuracy of models less accurate
than itself and **deflates** models more accurate than itself, with extra inflation
for models of its own provider (self-preferencing across a *family*, not just a
model). In the hiring simulation, 20 firms each using a *different randomly chosen*
LLM still systemically exclude ~20% of applicants, where random preferences would
exclude ~0. Firm welfare is *maximised* by everyone using the same best model, so
diversity and accuracy genuinely trade off — a real result independent of the
correlation-measurement dispute.

Judgement: the empirical work is careful and the downstream simulations are the
durable contribution. The headline statistic is measured against a uniform-over-wrong
baseline that assumes all distractors are equally attractive — false for any
professionally written multiple-choice item, and false in a way that scales with the
capability of the answerer (see maria2026 below). Treat 0.60 as an upper bound
containing at least three non-kinship terms.

---

<!--kb
id: paper:jo2026-subjectivity
labels: kind:paper, venue:preprint, area:llm-monoculture, area:measurement-theory
cite: Jo, Garg & Raghavan (2026). The Subjectivity of Monoculture. arXiv:2602.24086v1, 27 Feb 2026 (MIT / Cornell Tech)
triggers: null model choice, excess agreement, null ladder, item difficulty, IRT,
          population relativity, correlation flips negative, is monoculture identifiable
methods: multidimensional-item-response-theory, null-ladder, residual-correlation-matrix,
         controlled-model-family-experiment
quantities: |
  HELM n=14,042 items x m=72 models; HF n=11,994 x m=451; plus ACSIncome (RF/LR/MLP)
  MIRT K in {1,2,4,8,16,32,36,...,64}: MSE and mean|residual correlation| decrease
    MONOTONICALLY and log-linearly in K
  IRT-0.5 (ability only, item difficulty fixed) ~= Kim25/Goel25 implicit null
  IRT-1 (with item difficulty): correlations "substantially attenuated", some flip
    from strongly positive to slightly negative; pairwise ORDERING stays stable
  HELM model abilities collapse to ~1 dimension ~ overall accuracy
  HF residual clusters track CONTRIBUTOR/provenance, not question-type specialisation
    (PCA of accuracy-by-question-type: PC1 explains ~all variance)
stance: rebuts:kim2025-correlated-errors; rebuts:goel2025; supported-by:maria2026-marginal-competence
artifact: no code link found in v1 (checked 2026-08-07). Uses public HELM, HF leaderboard, ACSIncome.
verified: 2026-08-07
-->

**Jo, Garg & Raghavan (2026) — The Subjectivity of Monoculture.** Note Nikhil Garg
authors both this and Kim25: this is partly a self-correction, which is worth more
than an adversarial critique.

Two results worth carrying:

*Theorem 1.* For **any** distribution *P* on {0,1}^m there exists a latent vector
*Pᵢ* such that the coordinates are conditionally independent Bernoulli given *Pᵢ*,
with the right marginals — a de Finetti-style representation. Therefore a
sufficiently expressive null can always reinterpret cross-model correlation as
latent item/model structure. Combined with the *null ladder* (Prop 2: minimal excess
is monotone non-increasing in null expressiveness; Thm 3: residual cross-model
covariances → 0 as *K* → ∞), the conclusion is that **monoculture is not an
identifiable property of a dataset.** It is a discrepancy from a baseline that the
analyst must choose and defend.

*Population relativity.* Prop 4 / Thm 5: the fitted null, and hence "excess"
correlation, depends on which models and items are in the analysis, and is
*least* identifiable exactly when the population is homogeneous — i.e. the
measurement degrades precisely in the regime the field cares about.

Judgement: the theory is right and important, and the empirical demonstration is
appropriate. The gap they name themselves is the one to exploit: they work on binary
correctness *Y* ∈ {0,1}, so their null carries item difficulty and model ability but
says nothing about **which** wrong answer is given. That is where the remaining
signal lives.

---

<!--kb
id: paper:bommasani2022-homogenization
labels: kind:paper, venue:NeurIPS2022, area:llm-monoculture
cite: Bommasani, Creel, Kumar, Jurafsky & Liang (2022). Picking on the Same Person: Does Algorithmic Monoculture lead to Outcome Homogenization? NeurIPS 2022. arXiv:2211.13972
triggers: outcome homogenization, component sharing hypothesis, systemic exclusion,
          foundation model adaptation, who gets rejected everywhere
methods: outcome-homogenization-metric, fairness-benchmark-replication
quantities: |
  data-sharing increases homogenization, effect largest for SMALL datasets (US Census / ACS)
  the ADAPTATION method of a foundation model materially changes homogenization
    (vision and language) -- sharing a base model does not determine the outcome
stance: precedes:kim2025-correlated-errors; frames:kleinberg2021-monoculture
artifact: not checked
verified: 2026-08-07 (from secondary sources; primary not read in full)
-->

**Bommasani et al. (2022).** Origin of the *component sharing hypothesis* and of
"outcome homogenization" as the thing worth measuring — not whether models are
similar, but whether *the same individuals* absorb the bad outcome everywhere.

**Read in full 2026-08-07, and it reorders the whole area.** Their Eq. 3 is

> H = SYSTEMIC FAILURE(h¹…hᵏ) / ∏ᵢ FAIL(hⁱ)

— the observed rate of being failed by *everyone*, divided by the rate independence
would produce at the observed marginal failure rates. And they say why, in §3.1:
systemic failure alone "will in general be higher for less accurate systems independent
of a *specific* tendency to pick on the same person."

**They anticipated, in 2022, the accuracy confound that the 2025 work reintroduced.**
Kim et al. moved from an independence-normalised ratio back to a uniform-over-wrong
baseline. On the methodological question at the centre of this area, the field went
backwards, and the 2026 critique is partly a rediscovery of a 2022 metric design.
Also unusual and worth copying: §3.4 argues the convergent and divergent validity of
their own metric (Campbell & Fiske; Messick; Jacobs & Wallach) — cross-link
`instance-general/philosophy-of-science/construct-validity-and-formalization.md`.

The limit, which is the live research question here: their null models heterogeneity
across **decision-makers**, not across **the people judged**. Genuinely weak applicants
are rejected by everyone and drive H > 1 with zero component sharing — the individual
plays exactly the role item difficulty plays in the MCQ setting, so Jo et al.'s critique
of capability-only nulls lands directly on Eq. 3. They half-see it in footnote 4 (people
who fail the bar exam are justly rejected everywhere) and never move it into the metric.
No one appears to have said this.

The finding most often dropped in citation, which they flag as a surprise themselves:
**sharing a foundation model does not reliably homogenize outcomes; the adaptation
method does** — linear probing homogenizes more than finetuning, in both vision and
language. Shared components are not destiny. That agrees with Jo et al.'s 2026 result
that residual clusters track fine-tuning *provenance* rather than shared base: what
converges is the pipeline, not the substrate.

---

<!--kb
id: paper:maria2026-marginal-competence
labels: kind:our-reanalysis, area:llm-monoculture
cite: maria (2026), internal reanalysis. .research/2026-08-07-monoculture/ (FINDINGS.md)
triggers: does competence concentrate errors, leave-pair-out null has no power,
          anchored null antisymmetry, duplicate model in HELM, is agreement evidence of dependence
methods: leave-pair-out-nonparametric-item-null, anchored-null-disjoint-population,
         modal-distractor-concentration, synthetic-injected-effect-control
quantities: |
  sample: 22 HELM models x 2,918 MMLU items (10 subjects), independently re-downloaded
  agreement_when_both_wrong = 0.5528 -> replicates Kim25's 0.60 in magnitude/direction
  HELM option order identical across models: 0/2918 items -> letter comparison is sound
  leave-pair-out item null: excess = 0 EXACTLY, by algebraic identity, on any dataset
    (synthetic control: 99% injected monoculture -> observed 0.9790, null 0.9790)
  anchored null antisymmetry: weak->strong +0.212 (100% pos) vs strong->weak -0.206 (0% pos)
  corr(accuracy, P(picks modal distractor | wrong)) = +0.835 over 22 models (+0.841 excl. dup)
    olmo-7b: acc 0.290 -> 0.267 ;  llama-3.1-405b: acc 0.853 -> 0.778
  corr(min pair accuracy, anchored excess) = +0.801 -- reproduces "capable models are
    more correlated", argued to be an artifact of the same marginal effect
  google/text-unicorn@001 vs writer/palmyra-x-v3: identical on 2,917/2,918 items (99.97%
    OVERALL, not just when wrong); next-highest pair 0.8705 -> duplicate system, not correlation
stance: supports:jo2026-subjectivity; qualifies:kim2025-correlated-errors
artifact: .research/2026-08-07-monoculture/ — fetch_helm.py rebuilds the raw data from the
          public HELM GCS bucket; analyze.py / anchored.py / marginal.py reproduce every number.
          marginal.py Test 2 is MISCALIBRATED and its output must not be quoted (see FINDINGS §4).
verified: 2026-08-07
-->

**maria (2026) — internal reanalysis.** Full write-up in
`.research/2026-08-07-monoculture/FINDINGS.md`. Three things worth carrying out of it:

1. **A natural null can have exactly zero power, algebraically.** The leave-pair-out
   nonparametric item null — which is the obvious first improvement on Kim25's uniform
   baseline — has mean excess identically zero on every dataset, because each concordant
   pair is disjoint from exactly C(w−2,2) other pairs. I built it, believed its output
   ("93.8% explained by item structure"), and only caught it because ten robustness
   strata all returned *exactly* 1.0000. Suspicion trigger to keep: **a robustness check
   that agrees to four decimal places is not robust, it is circular.**
2. **Competence concentrates errors** (r = +0.835). Better models put more of their
   error mass on the single most seductive distractor. So high agreement-on-errors among
   strong models is the expected signature of *conditional independence plus shared
   competence*, not of dependence. This is a marginal, per-model property with no
   pairwise content, and it is invisible to a null defined on binary correctness.
3. **At least one "extremely correlated pair" in the benchmark is a duplicate system**
   (99.97% identical answers overall). Correlation statistics over public leaderboards
   need a duplicate-detection pass first.
