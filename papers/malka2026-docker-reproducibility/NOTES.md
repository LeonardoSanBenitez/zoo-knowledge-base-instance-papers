# Malka, Zacchiroli & Zimmermann 2026 — *Docker Does Not Guarantee Reproducibility*

Read 2026-08-25 by maria, from the arXiv PDF and from the replication package's
`Results.ipynb` read cell by cell **including its stored outputs**, which is where
everything below comes from. No Docker was run and no image was rebuilt.

---

## 0. Why I picked this up

My standing open question, carried across three sessions: *every population-scale
study of artifact re-executability measures artifacts whose environment is
**declared** (a requirements file, a DESCRIPTION, a setup.py). Containerisation is
the field's most-repeated recommendation and its evidence base is nearly empty.*
Trisovic's Dataverse corpus contains **9 Dockerfiles in 2,060 packages**, so it
structurally cannot answer.

This paper is the closest thing in existence, and it answers a *neighbouring*
question. Keeping the two apart is the whole discipline of reading it.

---

## 1. What it actually measures, and what it does not

| what people mean by "ship a container" | measured here? |
|---|---|
| ship a **Dockerfile**; a reader rebuilds it | **yes** — 72% still build after <2 years |
| ship a **built image**; a reader pulls it | **no** — but see §3, they measure whether it is still *there* |
| the rebuilt image is the **same** as the original | yes — and it essentially never is |
| the artifact's **analysis** re-executes | **no.** Nobody has measured this. |

The paper's estimand is *reproducibility of the image build*, not *re-execution of
a research artifact*. A study that rebuilds an image and diffs it never runs the
science inside. This is the gap that remains open after reading it, and it is the
one I care about.

## 2. The ladder, printed with every denominator (Figure 4b)

Of 1,537 images whose historical counterpart could still be downloaded:

| level | n | % |
|---|---|---|
| downloadable | 1537 | 100.0 |
| rebuildable | 1116 | 72.6 |
| auditable (Trivy could read it) | 1096 | 71.3 |
| same package set (versions ignored) | 573 | 37.3 |
| same major versions | 406 | 26.4 |
| same major + minor | 271 | 17.6 |
| same exact versions | 70 | 4.6 |
| same files (bitwise) | 4 | 0.3 |

This is the reporting practice I have been arguing for in three records: a funnel
with every stage's denominator printed. It costs one figure and it makes the paper
re-analysable by a stranger. Overall rebuildability on the full corpus, 3,836/5,298
= **72.4%**, agrees with 1,116/1,537 = 72.6% on the downloadable subset — a
consistency check the authors do not point out but which the printed funnel makes
free.

Caveat the authors state and which must travel with the bitwise number: **no
workflow in the corpus set `SOURCE_DATE_EPOCH`.** So 0.3% is a fact about
practice, not about Docker's ceiling.

## 3. The biggest number in the paper is in a methods footnote

> "Among these 3620 images, we successfully retrieved 1541; the remaining 2079
> were no longer accessible at the time of our analysis. This number is not
> unexpected, as images are routinely deleted from registries."

**57% of pushed images were gone in under two years.** That is an availability
failure roughly twice the size of the rebuild failure the paper foregrounds, and
it is reported as a data-collection loss rather than as a result.

For the question I actually care about it is decisive in shape and useless in
value, and both halves matter:

- **decisive in shape** — it inverts the naive ordering. A declared environment is
  a text file that lives in the repository as long as the repository lives. A built
  environment is a large binary that lives somewhere else, on someone else's
  storage policy. The intervention that "preserves" the environment is the one that
  introduces a new single point of failure.
- **useless in value** — this population is CI-pushed images, and a large share of
  those are per-commit tags that registries prune by design or that maintainers
  delete deliberately. **43% must never be quoted as the persistence rate for
  research images.** Recorded as `accepted-narrower-scope` for exactly this reason.

Open question written into the record: nobody has measured registry persistence for
*deliberately archived* research images. That number is enumerable from Zenodo and
Software Heritage and would settle the intervention.

## 4. The reanalysis: Figure 6's odds ratios are per standard deviation

This is the part that required the replication package, and it is why "open the
artifacts" is a rule and not a preference.

`Results.ipynb` cell 55, verbatim in structure:

```python
X = df_model[feature_cols]          # 0/1 rule-violation dummies
y = df_model['is_failure']          # 1 = build failed
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, ...)
X_train_scaled = StandardScaler().fit_transform(X_train)
result = sm.Logit(y_train, sm.add_constant(X_train_scaled)).fit()
```

and cell 56 reports `np.exp(result.params)` under the column header **"Odds
Ratio"**, which Figure 6 then plots against feature names like `rule_DL3008` and
the caption interprets as rules being violated or not.

Because the dummies were standardised, `exp(beta)` is the odds ratio **per standard
deviation of the dummy**, not per violation. For a 0/1 variable with prevalence *p*,
sd = √(p(1−p)) ≤ 0.5, hence

    beta_per_violation = beta_std / sd      and      |beta_pv| ≥ 2|beta_std|

which gives the distribution-free bound **OR_pv ≥ OR_std²** (for OR > 1), needing no
knowledge of *p* at all. Two prevalences happen to be printed in the notebook's own
stored output, so two rows can be computed exactly rather than bounded.

| rule | printed OR | per violation | how |
|---|---|---|---|
| CR02 — not built from an official base | 1.290 | **2.011** | exact, prevalence 0.1575 |
| DL3008 — pin versions in `apt-get install` | 1.471 | **≥ 2.163** | bound |
| DL3007 — do not use `latest` | 1.247 | **≥ 1.556** | bound |
| CR01 — not a staged build | 0.783 | **0.610** | exact, prevalence 0.4288 |
| DL3016 — pin versions in `npm install` | 1.207 | **≥ 1.456** | bound |
| DL3015 — `--no-install-recommends` | 0.786 | **≤ 0.618** | bound |

The bound is verified against both rows where the exact value is computable
(CR02: 2.011 ≥ 1.663 ✓; CR01: 0.610 ≤ 0.613 ✓).

**Nothing qualitative changes.** Standardisation is a monotone rescaling of each
coefficient; z and p are invariant. I did not argue that, I proved it by
construction — `verify_standardisation.py` fits both parameterisations on synthetic
data with planted coefficients and checks that β_std = β_raw·sd exactly, that z and
p are identical to 1e−6, and that the standardised OR is strictly closer to 1. Plus
a negative control with true coefficients zero.

**What does change is the paper's own summary of its findings.** The discussion says
the rules have "very weak effects, explaining only a few percentage points of the
variability" and effect sizes "below 3%", and concludes that best practices "help,
but are not a silver bullet". Two different things are welded together there:

- **explanatory power** — pseudo-R² 0.052, and on the held-out split the model
  recalls 5% of failures at a 0.5 threshold. Genuinely poor, *unaffected* by
  standardisation, and the "not a silver bullet" half stands entirely.
- **effect size** — understated by a factor of at least two on the log-odds scale.
  A rule violation that **doubles the odds of a failed rebuild** is not a weak
  effect. It merely fails to explain much variance, because violations are common
  and the outcome is noisy.

Small R² and large effect coexist comfortably. Standardising the predictors is
exactly what makes them indistinguishable in the output, because it converts every
coefficient into the same "per 1 SD" currency and 1 SD of a rare binary is a tiny
step. The four OLS models standardise too, so "below 3%" is also per SD; correcting
those needs per-rule prevalences the notebook does not print.

## 5. A hypothesis I formed and then killed

On the first read of the extracted text I believed Figure 6's caption contradicted
its own legend, and I was ready to write it up: the `-layout` extraction interleaves
the OR and p annotations into glyph soup (`pO=R:01.0.4073`), and the legend entries
`Protective (OR < 1)` / `Risk Factor (OR > 1)` land in an order that suggests
red = OR>1. Under that mapping the caption is backwards and the paper contradicts
itself about whether pinning helps.

The plotting cell settles it in one line:

```python
colors = ['red' if or_val < 1 else 'blue' for or_val in plot_data['Odds Ratio']]
```

Red is OR < 1. Caption, legend, code and discussion all agree, and my reading was
the error. Recorded here rather than quietly dropped, because the near-miss is the
lesson: **the sign convention of a figure is not inferable from a text extraction
of that figure, and a paper accused of self-contradiction on the strength of one is
being accused by an artefact of `pdftotext`.**

Two operational consequences worth keeping:
- `pdftotext -layout` is wrong for figure annotations. `-raw -f N -l N` separates them.
- Anyone quoting Figure 6 from a `-layout` extraction is quoting noise.

## 6. How this stands to what I already had, including where it corrects me

- **`samuel2024-jupyter-pmc` — it disagrees with my own reanalysis, and it is
  better powered than I was.** Last session I found pinning associated with *lower*
  environment-install and execution success (OR 0.435, Fisher p = 0.29, 191
  repositories, **22 events**) and wrote that "the field's most repeated
  recommendation has never been tested, and the one dataset that can test it does
  not support it". The first clause is now false. It has been tested here, on 835
  unique Dockerfiles, and three separate pinning rules each come out on the
  *helping* side at p < 0.02 — and, once corrected, at odds ratios around 2. **That
  sentence in the samuel2024 record needs amending in place, and this record is the
  `by` pointer.**

- **The reconciling hypothesis, which is mine and is in neither paper.** The two
  results need not conflict, because "pinning" means different things:
  - `apt` and `npm` serve old versions as **prebuilt binaries** from archives that
    keep them. Pinning costs nothing at install time and buys protection against
    upstream drift. It helps.
  - `pip` serving an old scientific package to a current interpreter frequently has
    **no wheel**, so `numpy==1.16.4` is an instruction to compile a 2019 source
    distribution against a 2023 toolchain. It fails where a bare `numpy` succeeds.

  **The sign of the pinning effect should depend on whether the pinned artifact is
  served prebuilt or must be built at install time.** That is testable on the
  Samuel 2023 corpus, which ships the verbatim content of every requirements file
  alongside the install outcome: classify each pin by whether a wheel exists for
  that exact version on the interpreter used, and compare. It is the next thing.

- **`trisovic2022-code-execution`.** Recommendation #4 there is "use Docker",
  offered on a corpus with 9 Dockerfiles in 2,060 packages — i.e. on no evidence
  from the study making it. This paper supplies evidence for one half and the news
  is mixed: 72% rebuild, 43% still downloadable. Neither is the near-certainty the
  recommendation implies.

- **My own stewardship rule** — *a measurement that silently drops the inputs it
  cannot handle reports on the tool while looking like a report on the world* —
  appears again in a new form. Here nothing is dropped; instead a **rescaling**
  reports on the parameterisation while looking like a report on the world. Same
  family, and harder to see, because a dropped input leaves a gap in a denominator
  and a rescaled coefficient leaves nothing at all.

## 7. What I did not do

- I did not rebuild any image, did not run Docker, and did not verify the 72%
  independently. That would be thousands of builds.
- The intermediate data (`intermediate-data/`, `historical-images/`, `results/`) is
  **not** in the replication package — only the code that produces it and the
  notebook's stored outputs. So c1–c3 are `accepted` on the strength of internal
  consistency and printed funnels, not on re-execution. Everything in c5 rests only
  on numbers the notebook printed and on arithmetic I can verify.
- I did not correct the four OLS models' effect sizes. The bound applies there too
  (coefficients are at least doubled) but per-rule prevalences are not printed for
  those corpora.

## 8. Worth sending to the authors

The Figure 6 correction is small, correct, machine-checkable, and improves a
published result without touching its conclusions — which is exactly the
contribution shape mark is designing for in `repro-contrib`. It needs one CSV from
them (rule prevalences in each fitted sample) to become complete for the OLS models
too. Noted to him separately; the decision to contact anyone is not mine to take
alone.
