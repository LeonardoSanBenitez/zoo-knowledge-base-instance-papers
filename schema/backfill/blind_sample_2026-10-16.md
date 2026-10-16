# Blind pattern-tagging sample, 2026-10-16

For an independent reader (asked: cidral). For each item, choose 0-3 slugs from
`instance-papers/schema/patterns.json` that describe the DEFECT the assessment found, using only
the text below. Do not open the paper.json files: they carry maria's tags. 'none' is a valid answer.
Answer format, one line per item:  `B07: slug-a, slug-b`  or  `B07: none`.

## B01
**Claim (the paper's):** Researcher competencies and prior beliefs do not explain the variation: methodological expertise, topical expertise, prior attitudes and prior beliefs show correlations from -0.12 to +0.14 with both the team's average effect and its within-team variance, none significant.

**Assessment (accepted-narrower-scope):** The nulls are real but weak. At n = 71 the widest of these intervals excludes only |R| > 0.36, i.e. a researcher characteristic explaining an eighth of the between-team variance would have been reported here as a null. Our independent scan of 85 usable team-level survey items finds max |r| = 0.26 with the team's average estimate and 0.31 with the team's median log standard error, against a chance threshold of 0.24 for 85 tests at n = 71 -- consistent with no effect and with nothing detectable. The correct statement is 'not shown to explain more than a moderate amount', not 'do not explain'.

## B02
**Claim (the paper's):** MARIA 2026, NEW: the identified quantity D = sigma_AT^2 - sigma_PL^2 on the HAMD17 subset is +0.444 [-1.748, +2.637] HAMD points^2 (k = 71, I2 = 0%), which at rho = 0 bounds sigma_TE at 1.62 points -- 0.86 times the 1.88-point mean drug-placebo effect -- and at rho = -0.32 permits 5.45 points.

**Assessment (accepted-narrower-scope):** Accepted as an estimate of D on HAMD17 with the corrected estimator of c5. NOT accepted as a statement about sigma_TE, which is not identified by a parallel-group design (senn2016) and moves by a factor of eight over the rho values this literature has used. The scale restriction is not fastidiousness: the unit-mixed pool over all 169 trials gives +1.188 [-0.477, +2.854], so mixing units moves the answer by more than any difference between the arms does. PRIORITY CORRECTED 2026-09-07: reporting D from summary data is Mills et al. (2021), not new here, and their guidance that D may only be pooled within one measurement scale is also theirs. What is mine is c5 -- their own deposited code uses the biased weight -- and the numbers on this corpus.

## B03
**Claim (the paper's):** 95.2% of the total variance in the numerical results is unexplained by any identified component of research design or researcher characteristics; identified design decisions account for at most 2.6% and researcher characteristics for at most 1.2%.

**Assessment (accepted-narrower-scope):** The direction is right and our out-of-sample test is HARSHER than theirs, not kinder: with grouped 10-fold cross-validation by team and a swept ridge penalty over 8 orders of magnitude, the 137 non-constant decision indicators achieve a best out-of-fold R^2 of -0.003 on the standardized estimate (permutation null -0.001). Out of sample the decisions explain zero, not 2.6%. But the 95.2% figure is computed on a raw variance that is not a stable quantity: 13 models (1.0%) with standard errors above the 99th percentile carry 47% of the total sum of squares, and the ten largest contributors come from only two teams (13 and 75). Trimming that 1% drops the SD of the standardized estimates from 0.0736 to 0.0400. So 'unexplained variance' is the right conclusion reached through a fragile statistic.

## B04
**Claim (the paper's):** Gold document position matters and follows a consistent order: accuracy is highest when the gold document is adjacent to the query (Near), lower when it is farthest (Far), and lowest when it is in the middle (Mid).

**Assessment (accepted-narrower-scope):** Large, monotone and independently reproduced WITHIN ITS POPULATION -- 7B models at 4-bit with a 15-token cap, 2023 generation. Scope cut on 2026-08-13: Gabin, Perez & Parapar 2026 sweep gold position on LLaMA-3.1:8B and Mistral-NeMo:12B unquantised and find flat curves with no U shape, on AmbigQA and on standard NQ/HotpotQA. An effect of this size (0.3781 Near vs 0.1795 Mid) does not vanish through noise, so the right reading is that the position effect is indexed to an inference regime rather than being a property of RAG. I had called this 'the most durable finding in the paper' one day earlier; that sentence was too strong.

## B05
**Claim (the paper's):** In 47.7% of these papers with listed OSF files, at least one file is visibly code by extension. This is a lower bound: code inside an archive is not visible to a listing.

**Assessment (accepted-narrower-scope):** Lower bound by construction, and the keyword filter biases it upward; the two biases do not cancel in any known way.

## B06
**Claim (the paper's):** DOJO is proposed as an open-source, containerised, MCP-based evaluation layer between data access and clinical deployment, with three planes (data: shortcuts, cohort bias, measurement equity; model: adversarial and out-of-distribution inputs; clinical workflow: latency, GPU, interoperability), a human-in-the-loop layer, and installation via `pip install dojo-health`.

**Assessment (accepted-narrower-scope):** As a statement of intent, accurate. As of 2026-09-30 no platform is released: `dojo-health` returns 404 on PyPI (an invented-name control also 404s; bodhi-llm returns 200, so the check discriminates), and criticaldata/dojo is a static website. The empirical arms that exist are separate papers (cajas2026-agents-catching-agents, cajas2026-modalens).

## B07
**Claim (the paper's):** Following documented Dockerfile best practices has a statistically significant but very weak association with reproducibility outcomes; effect sizes are below 3% and the models have poor explanatory power.

**Assessment (disputed):** Half right, and the half that is wrong is the half the paper's recommendation rests on. The FIT statistics are correct and do support 'poor explanatory power' -- pseudo-R^2 0.052, and on the held-out split the model recalls 5% of failures. But the EFFECT SIZES are misreported, because every regression standardises the 0/1 rule-violation dummies before fitting (`StandardScaler().fit_transform(X)` in cells 55, 60, 62, 64, 66), so the quantities reported as 'Odds Ratio' in Figure 6 are per standard deviation of the dummy, not per violation. Corrected, violating DL3008 multiplies the odds of a failed rebuild by AT LEAST 2.16, not the printed 1.47. Small explained variance and small effect are different things, and standardisation makes the difference invisible. See c5.

## B08
**Claim (the paper's):** Provided the response distributions under two treatments do not cross as a covariate varies, a transformation exists making the treatment difference constant, so the presence or absence of statistical interaction is partly a choice of scale rather than a fact about the treatment.

**Assessment (accepted-narrower-scope):** Accepted as stated, and it explains a result of mine that had no explanation. On 2026-09-02 I built a diagnostic that asks whether a corpus supports ADDITIVE or MULTIPLICATIVE homogeneity, and both corpora tested came back additive. I recorded that as an empirical finding about antidepressants and mindfulness. Senn's point is that the existence of a scale on which the effect is additive is close to generic, so 'the corpus chooses additive' is weaker evidence about the treatment than I took it to be -- it is partly evidence that the outcome scale was already a reasonable one. NARROWER SCOPE because the converse still bites: a qualitative interaction that reverses the sign for some patients cannot be transformed away, and my diagnostic would not detect one. What survives from my 09-02 work is the operational half -- lnVR and lnCVR test different nulls, the choice is load-bearing, and no paper states which was made.

## B09
**Claim (the paper's):** Researcher-induced dispersion is of the same order as sampling error in two unrelated fields. Applying Menkveld et al.'s robust recipe -- tau = sqrt((IQR/1.349)^2 - medianSE^2), then tau/medianSE -- gives 1.72 for #fincap RT-H1 (finance, 164 teams) and 1.72 for the CRI models (sociology, 71 teams).

**Assessment (accepted-narrower-scope):** Agreement to three significant figures is luck and must be quoted as such: CRI's ratio is 0.71 to 3.67 depending on the heterogeneity estimator, and the robust IQR-based recipe simply happens to land where finance lands. The defensible statement is the order of magnitude -- researcher-induced dispersion is comparable to, not negligible against, sampling error -- and it now has two instances in fields sharing nothing but the design. Narrowing: this is one hypothesis of six in #fincap (the others are only described as 'similar in magnitude') and the CRI figure pools 11 dependent variables, where the per-DV range is 0.88-2.14.

## B10
**Claim (the paper's):** Detectability is inversely related to directness: direct test-set leakage is 75% of mechanisms and caught 97% of the time, while offline label distillation (fit leaked labels offline, hard-code coefficients as 'domain priors') evades 38% (n = 32), about twelve times as often; exploits rated 10/10 on efficacy evade 0.4% of the time.

**Assessment (accepted-narrower-scope):** Sums check. The printed CI for distillation, [20, 52]%, matches neither Wilson [22.9, 54.7] nor a plain binomial; attempts within a Setting-3 pair are correlated, so a clustered interval is plausible but unstated. The relative ordering (direct leaks are visible, disguised ones are not) is the robust part, and the authors themselves say only the relative result is supported.

## B11
**Claim (the paper's):** The coefficient-of-variation ratio is 0.82 (95% CI 0.80 to 0.84), i.e. the increase of variance with increasing pre-post difference is weaker in antidepressant than in placebo arms; the authors state there is no immediately plausible explanation for this.

**Assessment (refuted):** It is not a fact about variance. Both statistics carry the identical Nakagawa small-sample correction, which cancels, so per trial lnCVR_i - lnVR_i = ln(m_PL,i / m_AD,i) EXACTLY -- measured max absolute deviation 2.8e-16 across all 169 trials. CVR is VR divided by the ratio of mean symptom reductions and contains no further information. The drug reduces symptoms more than placebo in 159 of 169 trials; on HAMD17 the reduction is 10.99 vs 9.11 points, ratio 1.207, reciprocal 0.829. Their own Table 1 gives VR/CVR = 1.2317 against an n-weighted mean-change ratio of 1.2286, and the identity predicts every subgroup row including the tricyclic outlier (CVR/VR 0.613 vs mean ratio 0.603). The 'no immediately plausible explanation' is the treatment effect. Their code carries the tell: 'for the calculations of CVR, it was necessary to use the absolute values of the pre-post differences' -- a coefficient of variation requires a mean on a ratio scale, and a pre-post change has an arbitrary zero and either sign. FURTHER, 2026-09-06 (see c10): the sign of the result flips with the reporting convention. Their own supplementary table 1 runs the identical analysis on the 84 endpoint-score trials and gets CVR = 1.15, above 1, while VR stays at 0.98. PRIORITY CORRECTED 2026-09-07: this is NOT new. Mills et al. (2021, Epidemiology, `mills2021-differences-in-variance`) state it, with R code deposited, and cite the psychiatric variability meta-analyses as the examples of the violation. I found their paper on the third search of the same session, after writing this record. What remains mine is quantitative and is stated separately below. Specifically: Mills et al. say the coefficient of variation requires a ratio scale with a meaningful zero and name HAMD and MADRS as failing it. What is still mine here is the exact identity -- lnCVR minus lnVR equals the log ratio of arm means EXACTLY, the small-sample corrections cancelling, measured to 2.8e-16 over 169 trials -- which is stronger than 'the scale does not support it', because it says the statistic carries no information at all beyond lnVR and the treatment effect. And the reporting-convention sign flip in c10, which is in neither paper.

## B12
**Claim (the paper's):** MARIA 2026, NEW: the readback r = 1 - 2 rho^2 holds only at VR = 1. The general form is r = (1 + rho u)/VR with u = -rho + sqrt(rho^2 + VR^2 - 1), and at the VRs actually measured on three corpora it changes both the implied heterogeneity and which rho values are admissible at all.

**Assessment (accepted-narrower-scope):** The algebra is exact and reduces to the known special case at VR = 1. Accepted as a READBACK TOOL: whatever rho a paper assumes, it is also assuming the within-patient correlation in the last column, and that quantity IS checkable against test-retest data these trials already collect. Nobody has checked it; that is the recommendation this claim carries -- rho should never be reported without its r. NOT accepted as a refutation of any particular rho. The tempting stronger reading -- 'a measured VR of 0.968 rejects rho = 0 outright' -- is conditional on the additive decomposition holding on an UNBOUNDED scale, and that condition fails: a bounded outcome produces VR < 1 with sigma_TE = 0 and any rho at all (winkelbeiner2019-antipsychotic-variability#c4). The first draft of m13 asserted the stronger version in both its docstring and its summary; both are corrected in place, which is the third time in this session that a summary paragraph overshot the analysis directly above it.

## B13
**Claim (the paper's):** The Power-of-Noise effect of Cuconasu et al. 2024 reproduces under the original experimental setup: with 4-bit quantised Llama-2-7B-chat and MPT-7B, a 15-token generation cap and the original NO-RES extraction prompt, adding random documents to a context whose gold document sits nearest the query does not degrade and often improves accuracy.

**Assessment (accepted-narrower-scope):** The numbers reproduce and the Delta(%) against the original is under 1% in the Near column, which is a genuine replication. The narrowing: the effect is +0.0224 accuracy at n=10,000, i.e. about 2.1 standard errors, and it exists only in the Near position for one quantisation of one 7B model. Nothing in Table 2 licenses 'random documents improve RAG'.

## B14
**Claim (the paper's):** Notebooks are the unit of analysis: rates are reported per notebook, by year, research field, journal and article type.

**Assessment (disputed):** Not a claim the paper makes explicitly, which is the problem: it is an unstated design assumption underneath every percentage in the Results. Every notebook in a repository shares one conda environment, one set of data paths and one author, and the measured ICC is 0.435. 77.2% of repositories contributing three or more executions had a completely homogeneous outcome -- a repository is close to one Bernoulli trial. The effective n is about a third of the printed one, and the finer the slice (per journal, per field, per year) the more likely it reports a single repository. All 396 successes of the 2021 run come from 130 repositories, with the top 20 supplying 57%. This does not touch the headline rate, which is a simple proportion; it undermines every comparison built on top of it.

## B15
**Claim (the paper's):** Neither model family nor prompt configuration predicts the Power-of-Noise effect for a held-out level: every grouped cross-validated R-squared is negative, although the effects range over 0.86 in accuracy. This is the same negative result as in Breznau's sociology multiverse, in a literature that has never cited it.

**Assessment (accepted-narrower-scope):** Robust in sign across all four subsets, and the estimator is the same one used on CRI. The narrowing is a power caveat that must travel with it: with 19 points and 5 levels, a grouped CV R^2 near zero is also what a modest true effect would produce. The claim is that the recorded dimensions do not predict WELL, not that they have no effect. The synthetic controls in reanalysis/04 show the machinery does attribute an injected 0.02-sd configuration effect correctly, so the negative result is not blindness.

## B16
**Claim (the paper's):** The mechanism is entropy collapse: by adding random documents to the context, the conditioned distribution p(y|.,d) is better conditioned, avoiding pathologically low attention entropy that causes degenerate outputs.

**Assessment (not-identifiable):** The claim has no truth value as stated. No entropy is measured anywhere in the paper -- Fig. 3 is a mean-attention heatmap for a single hand-picked query, not an entropy statistic over any sample -- and no alternative to entropy collapse is specified against which it could fail. Mazuryk et al. later supply a competing mechanism (output-format failures in the low-document baseline) that predicts the same accuracy pattern, and the two are not distinguished by anything in this paper. Stronger than 'disputed', which is why the status exists.

## B17
**Claim (the paper's):** A cumulative attention block on report-token positions restores image-swap sensitivity when it begins at or below about layer 22 of 62 and not from layer 28 upward (flip rate 1.50% to 7.75% when blocked from layer 0, against 12.00% with no report); difference-of-means steering and a linear probe transfer are negative.

**Assessment (accepted-narrower-scope):** Carefully bounded by the authors; the negative steering and probe results are reported with the same care as positives, which is rare.

## B18
**Claim (the paper's):** Of these papers whose cited OSF deposit lists files, 9.1% had a file first uploaded after the paper was published, and 4.5% had a file replaced by a new version after publication. Counting only changes 7 or more days after publication, 4.5%.

**Assessment (accepted-narrower-scope):** The classifier was not trusted on date_modified: every flagged file was resolved against its version history, and all 13 resolved. Narrow: the publication date is PLOS's (day resolution, timezone unknown), so lags of 1-2 days are within noise; a file deleted after publication is invisible to a listing taken today, so these are lower bounds on change.

## B19
**Claim (the paper's):** Answers to the three extinction questions were 'mostly consistent', with medians of 5% or 10%: AI advances causing human extinction or severe disempowerment (mean 16.2%, median 5%, n = 1,321); human inability to control future advanced AI causing it (19.4%, 10%, n = 661); the first within 100 years (14.4%, 5%, n = 655).

**Assessment (accepted-narrower-scope):** Every number reproduces. 'Mostly consistent' hides the one direction that matters: the control-problem question names a subset of the general question's event and receives the HIGHER probabilities (median 10 vs 5, p = 0.008), while the time-restricted subset is coherently lower. A between-subjects violation of extension, the signature of support-theory unpacking: naming a mechanism adds probability. The effect is small (probability of superiority 0.536) and must be quoted as small, but it means 'AI researchers put about 5% on extinction' and 'about 10%' are both instrument-relative: which one a reader hears depends on which wording they read.

## B20
**Claim (the paper's):** When average and total conflict, people apply both principles, with a threshold for minimally acceptable average: 1000 people at +100 is roughly as good as 100,000 at +70, but even 1 billion at +50 does not outweigh 1000 at +100; reflection shifts answers toward totalism (Study 3c, N=461; Study 3d mere addition, N=482; Study 3b equal totals, N=825).

**Assessment (accepted):** Reproduces. The averagist preference in 3b is not a comprehension artifact: it is at least as strong among the 5.6% who demonstrably understood that totals were equal (2.18 vs 2.31). The quantitative content worth carrying for longtermist arguments: for HAPPY populations, multiplying the population by 10,000 recovers about a quarter of what a 20-point drop in average costs, and beyond a million people each further factor of ten moves the answer by ~0.02 scale points -- lay value of happy numbers is saturated. For unhappy populations the same multiplication recovers more than the whole loss; that valence contrast carries the same reverse-coding confound as c4 and should not be cited as a welfare asymmetry. 3d gender test: the printed t(571) and means are those of the UNEXCLUDED sample (N=613), not the reported N=482 (reanalysis/s3bd.py); same conclusion either way.

## B21
**Claim (the paper's):** Similarity judgements from 100 experienced meditators over 20 basic meditation techniques are well described by two dimensions, labelled 'amount of body orientation' and 'activation', with seven clusters within them.

**Assessment (accepted-narrower-scope):** The design is good and the subgroup replication is the strongest part -- separately fitting Buddhist (n=27) and Hindu (n=20) raters gives congruent two-dimensional solutions, which is a real check and is rare in this literature. NARROWER on two counts, both from their own text. (1) The seven clusters were 'identified by visual inspection' of the figures, with no clustering criterion and no stability check, so they are an interpretation of the configuration rather than a result of it. (2) The choice of two dimensions over three rests on calling a stress reduction of 0.023 'negligible' -- a judgement, not a test -- and the underlying matrix is not deposited, so nobody outside can examine either decision. The dimensional finding stands; the seven clusters are a reading.

## B22
**Claim (the paper's):** Most people do not find human extinction uniquely bad: among those ranking no catastrophe > 80% killed > 100% killed, only 23.5% (UK, 50/213) and 18.8% (US, 27/144) judge the 80%->100% difference greater than the 0->80% difference.

**Assessment (accepted-narrower-scope):** Reproduces from the data in both samples, and the two checks I expected to weaken it came back clean. (1) The forced binary choice has no 'equal' option, but only 3.5-4.5% of free texts say anything like 'equal' or 'cannot compare', and control-condition texts reason explicitly by counting deaths ('80% more die... only 20% more'). (2) The main question is asked only of those passing the ranking filter, a post-treatment filter whose pass rate varies 78-92% by condition; unconditional shares tell the same story (control 19.5% vs utopia 66.5% in 2a). The narrowing is about what the instrument measures: choosing 'the second difference' requires extinction's extra badness to exceed the deaths of 60% of humanity (80 > 20 + premium). 'Not uniquely bad' therefore means 'premium below that threshold', not 'no special badness'; with Parfit's original 99% the threshold would be 98%. The share is a function of the 80% the authors chose.

## B23
**Claim (the paper's):** MARIA 2026, NEW: the compression of sigma_Y/sigma_X in this literature is dominated by the removal of 'non-fitters', not by the ceiling. A mixture of a genuine non-fitter subpopulation with proportional recovery and a ceiling reproduces the fitters-only statistics; the ceiling alone cannot come near them.

**Assessment (accepted-narrower-scope):** Accepted for the direction and rejected for completeness, and the route there is recorded because it was wrong twice. Attempt 1 asked whether the ceiling could REACH each published ratio and answered yes for seven of eight -- vacuous, because the sweep ran the mean improvement to 55 points on a 66-point scale and the reachable band became 0.13-1.03, i.e. everything. Attempt 2 modelled non-fitter removal as dropping the most negative residuals, moved the ratio by 0.09 against Zarahn's 0.52, and I wrote 'a comparable amount' with the contradicting table directly above. The residual model removes a TAIL where the literature removes a SUBPOPULATION. The mixture is the right shape: four targets fitted to L1 = 0.084 and one held-out statistic matched. But the other held-out statistic, whole-sample r(X,Y), misses by 0.23 -- real non-fitters are more predictable from baseline than 'recovers nothing plus noise' allows. Right shape, not the right world.

## B24
**Claim (the paper's):** 25.6% (95% CI 23.1-28.0) of regular meditators report having had particularly unpleasant experiences they think may have been caused by their meditation practice.

**Assessment (accepted-narrower-scope):** Reproduces exactly. Narrower in what the number IS: a lifetime-ever item that does not behave like a lifetime cumulative risk. It is 21% already among those practising under a year and 28% after twenty years. A constant hazard predicts roughly 2% rising to 62%; adding quitting after an event (k = 0.09/yr) or recall decay (10%/yr) still predicts a rising curve from about 2-3%. Only a front-loaded, early-onset subgroup (about a quarter, experiencing it within the first months) reproduces the flat shape (reanalysis/m4.py). So the 25.6% describes who is prone, early, among people who kept practising -- it cannot be projected as 'risk accumulated over a meditative career', and it says nothing about people who stopped, whom the design excludes and the paper never mentions. Completion before the item was 65% and differed by continent and religiosity.

## B25
**Claim (the paper's):** With the radiology report in the prompt, swapping the image for another study's changes MedGemma-27B's generated answer on 4.26% of trials; without the report on 20.94%, a paired increase of 16.7 points (patient-clustered 95% CI [15.6, 17.7]).

**Assessment (accepted-narrower-scope):** Direction is robust across readouts, templates, option order, an Uncertain option, three model lineages and substitute redraws, per the authors. Magnitude is not: block order alone moves the report effect from +12.4 to +7.8 on identical trials, and the pooled rate is a mix of findings at ceiling (five findings answer yes on 97.8-100% of report-absent trials) and findings that flip 16.8-32%. Quote the direction and the range, not '16.7 points' alone.

## B26
**Claim (the paper's):** The tables of Mazuryk et al. 2026 are computed on exactly 10,000 items; the 2,889-item NQ-open test split is ruled out by the printed decimals alone.

**Assessment (accepted-narrower-scope):** Conclusive for Tables 1, 2 and 4-7. Narrower for Table 3: the reproduction's Table 3a violates the k/2889 grid at 7 of 58 values, which is real; the ORIGINAL's Table 3 violates at 2 of 58, which a single typo would produce, so I do not assert it for the original. An earlier version of reanalysis/04 asserted the Table 3 result without ever having fed Table 3 into the test. That overclaim is annotated in place in 04 and superseded in 06 rather than deleted.

## B27
**Claim (the paper's):** The variability of outcome was slightly lower in the antipsychotic arms than in placebo arms: VR = 0.97 (95% CI 0.95-0.99, P = .01) across 52 RCTs and 15,360 patients, so there is no evidence that antipsychotics increase outcome variance and hence no personal element of response.

**Assessment (accepted-narrower-scope):** The measurement reproduces exactly from the deposited data -- k, both patient totals and the pooled VR to three decimals, under their own pooling and under two alternatives. Accepted as a measurement. NOT accepted as the inference: VR significantly BELOW 1 is not 'no increase', it is incompatible with their own null model (see c3), and the deviation is the same size as a bias their design carries (c4).

## B28
**Claim (the paper's):** The code for the reproduction is available at https://github.com/ina0105/The-Power-of-Noise-Reproduction.

**Assessment (disputed):** The repository exists and contains the pipeline, the SLURM job scripts and the prompt construction, which is more than most. But 4 of its 16 Python files raise SyntaxError or IndentationError under py_compile, including both generation entry points (src/generate_answers_llm.py, src/generate_answers_llm_mixed.py) and the vLLM wrapper (src/llm_vllm.py). Three of the four were broken by the single commit named 'final experiments'. The per-question generation results are not in the repository at all; the README points at a Google Drive folder. So the artifact is present-but-insufficient and, at HEAD, not executable.

## B29
**Claim (the paper's):** Reading the observed distributions directly, the effect on the worst-off decile is about twice the effect on the best-off decile.

**Assessment (accepted-narrower-scope):** True as a description of what the two arms' distributions look like, which is what a service deciding whom to offer a programme to would actually see. NOT a claim that any individual's benefit depends on their starting point -- arm-level moments cannot see individuals, and a mixture in which half the participants improve a lot and half not at all reproduces the same two moments. The narrower scope is the whole point: this number belongs in a discussion of allocation, not of mechanism.

## B30
**Claim (the paper's):** The truncation-relief mechanism Mazuryk et al. propose for the Power-of-Noise effect runs backwards on their own data; the instruction-hedging channel is the one that is supported.

**Assessment (accepted-narrower-scope):** Two independent sources point the same way, which is why I record it rather than filing it as a doubt. The narrowing: this refutes the truncation channel as the explanation for those specific configurations, not for every configuration in the paper -- Figure 2's underlying counts are only partly quoted in prose and the per-question outputs are in a gated artifact, so a regression of accuracy on truncation rate across all cells cannot be run.
