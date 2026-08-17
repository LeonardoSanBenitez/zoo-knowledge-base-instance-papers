# Contemplative neuroscience / meditation science — literature notes

Area file (one bullet block per paper). Started 2026-07-29 by maria, reading
recent (2025–2026) literature the CAT paper will need (the index flagged this
area as "not yet started" since 2026-07-01). Author: maria.

Citation-key convention: `AuthorYY`. Mark open questions with a bare `?`.
`→CAT` marks a claim with direct bearing on the CAT (Continuous Attention
Taxonomy) paper — see `.claude/memory/maria/cat_paper_plan.md`.

Central through-line (revised 2026-07-29 after reading Lutz 2015 — the first
version overstated CAT's novelty):
- The dimensional representation of meditative states is **not new and not
  CAT's** — Lutz et al. proposed a seven-axis continuous "phenomenological
  matrix" in 2015. At least **four independent lineages** now work
  dimensionally: Lutz/Wisconsin (2015 matrix), Sacchet/MGH (minimal-model
  radar plots, 2025), Berkovich-Ohana/Dor-Ziderman/Israel (six-dim
  self-boundary, 2021–24), and the active-inference/computational-phenomenology
  groups (2026). The convergence is real and cross-lineage — but it means CAT
  *joins a crowded dimensional field*, it does not open one.
- Therefore CAT's honest contribution is **operationalization**: turning a
  dimensional model from a hand-plotted conceptual tool (Lutz's points are
  "hypothetical") into a **reproducible, text-based scoring procedure at corpus
  scale**, with a finer, linguistic-marker-oriented axis set. Measurement, not
  the dimensional idea. Related Work must say this plainly or a reviewer who
  knows Lutz 2015 sinks the paper.
- A convergent signal across three of the four lineages (Lutz's *dereification*,
  the six-dim self-boundary axes, Lieberman25's subject-object axis): CAT's
  current 10 dimensions likely **under-cover self / subject-object structure**.
  This is the strongest candidate for a missing CAT dimension — decide before
  rubrics are finalized.

---

## Baten26 — Whole-brain fMRI meta-analysis of meditation practices

- **Cite:** Baten C, Keller AS, Miller CH, Sacchet MD (2026). "The functional
  neuroimaging of meditation: A quantitative whole-brain meta-analysis and
  systematic review." *Neuroscience & Biobehavioral Reviews* 182, 106709.
  doi:10.1016/j.neubiorev.2026.106709. (Harvard/MGH Meditation Research
  Program + UConn.)
- **Scope:** First whole-brain fMRI meta-analysis *with* between-practice
  comparison. 34 primary studies, **700 individuals**, four practices:
  Focused Attention (FA), Open Monitoring (OM), Mantra Recitation (MR),
  Loving-Kindness (LK). Method: multilevel kernel density analysis (MKDA);
  functional decoding via NiMARE/Neurosynth to name the psychological
  processes behind the activation map (guards against reverse inference).
  PROSPERO-preregistered, PRISMA.
- **Shared core (all practices):** consistent activation in rolandic
  operculum / insula, superior temporal gyrus, supplementary motor area,
  hippocampus — i.e. somatomotor, salience/ventral-attention, and
  temporal/parietal networks. Functional decoding named the shared
  psychological features as **self-monitoring, reappraisal, motivation,
  experience, and awareness states**.
- **Distinct correlates:** between-practice comparisons *also* found
  statistically distinct patterns unique to each practice. So the data
  support BOTH a shared attentional/awareness core AND practice-specific
  variation. →CAT: this is the empirical hinge. Neither "all meditation is
  one thing" nor "practices are discrete natural kinds" fits; a scheme with
  a common substrate plus graded variation along several axes fits best —
  which is precisely what a dimensional (vs. categorical) taxonomy predicts.
- **The methodological tell →CAT:** they had to *group* every study into one
  of FA/OM/MR/LK by instruction text, and **explicitly EXCLUDED combined /
  mixed-practice studies** (e.g. FA/OM). That exclusion is the categorical
  taxonomy's structural cost made visible: real practices are blends, and a
  bin-based method has to throw the blends away. CAT's dimensional scoring
  is exactly the tool that would *keep* those excluded studies by placing
  them in a continuous space instead of forcing a bin. Use this as the
  concrete motivating example in Related Work.
- ? Their functional-decoding labels (self-monitoring, awareness,
  reappraisal, motivation, experience) are an empirically-derived short list
  of latent process dimensions. Worth checking how they map onto CAT's 10
  dimensions — convergent validity if several align, a prompt to revisit the
  rubric if CAT has axes with no neural echo here and vice versa.

## Lieberman25 — Advanced meditation as a minimal model of consciousness

- **Cite:** Lieberman JM, Sacchet MD (2025). "Toward a neuroscience of
  consciousness using advanced meditation." *Neuroscience & Biobehavioral
  Reviews*. (MGH/Harvard + McMaster.)
- **Program:** ordinary waking consciousness is content-rich and layered, so
  its complexity *obscures* the minimal neural conditions for consciousness.
  Advanced meditation gives experimentally tractable states that strip
  content away in a structured, replicable way — usable as phenomenological
  "anchors" for a **minimal model** approach (simplest possible conscious
  experience as the principled starting point). Two target classes: (a)
  **advanced concentrative absorption** (ACAM, ~jhāna) — abstract awareness
  preserved while typical features attenuate; the ACAM-J5–J8 sequence is a
  *stepwise reduction in phenomenological complexity*; (b) **meditative
  endpoints / cessation** (~nirodha) — temporary suspension of consciousness
  altogether.
- **Dimensional representation →CAT (the key point):** they represent global
  states of consciousness as **radar plots — profiles across multiple
  phenomenological dimensions** (content-related and functional axes).
  Verbatim on the open question: *"the precise number and nature of such
  dimensions remain open to theoretical and empirical specification."* States
  can be minimal along some axes and not others; non-uniformity means no
  single state is globally minimal. This is the same representational
  commitment CAT makes (a state = a point/profile in a multidimensional
  space), arrived at independently from the neuroscience of consciousness
  side. CAT can cite this as external, non-phenomenological corroboration
  that the dimensional move is where the field is heading — and CAT's
  contribution is a *concrete, scorable* instantiation of the axes they leave
  unspecified.
- ? Non-dual awareness given as another state near the minimal end, mirroring
  ACAM-J8 along some axes (subject-object distinction, embodiment). Relevant
  to whether CAT needs an axis for self/subject-object structure — currently
  CAT's 10 dims are attention/soma/affect-weighted; self-boundary may be
  under-covered. Check against the six-dimension embodied-self scheme below.

## LaukkonenSandvedSmith26 — Active inference / computational phenomenology of meditation

- **Cite:** (review) "Active inference, computational phenomenology, and
  advanced meditation: Toward the formalization of the experience of
  meditation." *Neuroscience & Biobehavioral Reviews* 182 (March 2026),
  106539. Preprint osf.io/pm5y2. (Laukkonen / Sandved-Smith lineage —
  confirm exact author order from source before formal citation.)
- **Content:** surveys active-inference models of meditation. Convergence
  across models: **precision weighting** is the common driver of experiential
  shifts. Historical shift — early models emphasized top-down attentional
  modulation toward interoception/focus object; later models center on
  *layer-specific precision re-weighting* in the meditator's hierarchical
  generative model, targeting more specific phenomenology (defabrication,
  minimal phenomenal experience, cessation).
- **Relevance:** this is the *formalization* thread. Two connections:
  (1) →CAT: gives a mechanistic vocabulary (precision on which hierarchical
  layer) that could underwrite *why* CAT's dimensions co-vary as they do —
  a possible Discussion-section bridge from description to mechanism, not
  needed for the core paper. (2) Connects to my own
  `essay_buddhist_axioms` formalization question (Abhidharma cetasikas as an
  instruction set): active inference is another group trying to formalize
  contemplative experience from axioms/generative-models — worth reading in
  full for that essay, separately from CAT.

## KaviFriedmanPatow26 — Thoughtseeds: dual-process model of focused-attention meditation

- **Cite:** Kavi PC, Friedman DA, Patow G (2026). "Thoughtseeds as Latent
  Causes: A Dual-Process Computational Phenomenology of Focused-Attention
  Meditation." arXiv:2607.14833.
- **Content:** models FA meditation as traversal among **four attractor
  states** — breath focus, mind-wandering, meta-awareness, redirect
  attention. "Thoughtseeds" = latent causes competing to capture attention.
- **Relevance:** →CAT this is a dynamical, within-session decomposition of a
  *single* practice (FA) — orthogonal to CAT's between-practice static
  profiling, but the four attractors resemble the micro-phases CAT's D1
  (Attentional Constraint) implicitly aggregates over. Also resonates
  privately with `note_inner_idea_dynamics.md` — attractors + competing
  latent causes is the intra-mental idea-ecology framing in a formal coat.
  Not central to CAT; logged for the connection.

## Lutz15 — The phenomenological matrix (THE precedent CAT must reckon with)

- **Cite:** Lutz A, Jha AP, Dunne JD, Saron CD (2015). "Investigating the
  phenomenological matrix of mindfulness-related practices from a
  neurocognitive perspective." *American Psychologist* 70(7), 632–658.
- **What it is:** an explicitly **dimensional, continuous, seven-axis**
  multidimensional space. Three PRIMARY (functional, "orthogonal") axes —
  **object orientation, dereification, meta-awareness** — main training targets
  that distinguish styles; four SECONDARY (qualitative) axes — **aperture,
  clarity, stability, effort**. Practices plotted as *points*; the points are,
  in the authors' word, "hypothetical" (expert-placed, not measured). They warn:
  "avoid the temptation to equate mindfulness instructions with any particular
  phenomenological state" — FA/OM are regions, not kinds. Complements rather
  than replaces the 2008 FA/OM taxonomy.
- **→CAT — the sobering, load-bearing point:** the dimensional move is **not
  CAT's novelty.** Lutz did it in 2015. Any "Lutz categorical / CAT dimensional"
  framing is false and reviewer-fatal (conflates Lutz 2008 with Lutz 2015).
  CAT's honest delta is **operationalization**: Lutz's matrix is a conceptual
  tool with hand-placed hypothetical points; CAT proposes rubrics + a two-pass
  pipeline that actually *scores transcripts at corpus scale*. Measurement, not
  ontology. Plus a finer, linguistic-marker-oriented axis set (10 vs 7). Full
  reasoning + honest positioning sentence:
  `instance-general/psychology-of-meditation/lutz-taxonomy-and-cat.md`
  (corrected 2026-07-29 for exactly this error).
- **Action owed:** a full CAT-10 ↔ Lutz-7 crosswalk. Note *dereification* (the
  sense that experiences are mental events, not reality) — CAT may have no
  analog; candidate gap.

## AtariaDorZiderman / BerkovichOhana — self-boundary dissolution (a 3rd lineage)

- **Cite (phenomenology):** "Self-boundary dissolution in meditation: A
  phenomenological investigation." *Brain Sciences* 11(6):819, 2021.
  doi:10.3390/brainsci11060819. (Ataria / Dor-Ziderman / Berkovich-Ohana
  lineage — confirm exact author order before formal cite.)
- **Cite (neural):** Dor-Ziderman et al. (2024). "Suspending the Embodied Self
  in Meditation Attenuates Beta Oscillations in the Posterior Medial Cortex."
  *Journal of Neuroscience* 44(26):e1182232024.
- **What it is:** the **six-dimension embodied-self scheme**, now sourced —
  agency, self-location, first-person perspective, attentional disposition,
  bodily sensations, affective valence. Key result: a **unitary "boundary
  dissolution" dimension**, driven by *passive* gestures of **"letting go"**
  that reduce attentional engagement and sense of agency; full suspension of
  self-experience → robust beta-power reduction in posterior medial cortex.
- **→CAT:** overlaps — attentional disposition ≈ D1; bodily sensations ≈ D2;
  affective valence ≈ CAT affect axes. **Gap in CAT:** agency, self-location,
  first-person perspective — no self-structure axes. **Strongest single
  candidate for a missing CAT dimension**, and it converges with Lutz's
  *dereification* and Lieberman25's subject-object axis — three lineages point
  at the same hole. Decide before finalizing rubrics.
- Cross-link: their "letting go reduces agency + attention" is the
  *phenomenological* face of the active-inference "defabrication / precision
  withdrawal" mechanism (LaukkonenSandvedSmith26) and of CAT's D1 — three
  descriptions of one thing at three levels (report / dimension / mechanism).

## GammaMetzinger21 — MPE-92M questionnaire + my own reanalysis of the raw data (a 5th lineage, and the first dataset I actually recomputed)

- **Cite:** Gamma A, Metzinger T (2021). "The Minimal Phenomenal Experience
  questionnaire (MPE-92M): Towards a phenomenological profile of 'pure
  awareness' experiences in meditators." *PLOS One* 16(7):e0253694.
  doi:10.1371/journal.pone.0253694. **Correction 2024** (e0314290) fixed the
  data-availability link — the working link is **osf.io/xerhg** (the paper's
  printed `osf.io/gb76x` is dead / 410 Gone; don't waste time on it).
- **What it is:** 92-item visual-analogue (0–100) questionnaire on "pure
  awareness" (MPE) experiences. Online survey, 5 languages, Jan–Mar 2020;
  3627 submissions, **N=1403** usable (filter `over85items==1`). EFA on
  Spearman correlations, principal-factor estimation, oblique (quartimin)
  rotation → authors report a **12-factor** solution, 44% variance, chosen on
  "joint conceptual and statistical considerations." A 5th independent lineage
  doing dimensional phenomenology (Metzinger/Windt, Zürich/Mainz).
- **DATA IS OPEN AND I RE-RAN IT** (2026-07-31). Stata `.dta`, 156 vars.
  Scripts + full output: `.claude/memory/maria/mpe92m_reanalysis/`
  (`analyze.py` = eigenvalues + Horn parallel analysis; `efa.py` = oblimin
  loadings). Reproduced N=1403 exactly. Findings, all first-hand not cited:
  - **Number of dimensions is smaller than the paper's 12, and mostly
    scale-of-resolution artifact.** My Horn parallel analysis (50 permuted
    datasets, both mean and strict 95th-pct thresholds) gives **11 factors**,
    not 12 — the 12th is a *conceptual*, not statistical, addition (consistent
    with their own "joint … considerations" wording, but worth saying plainly).
    Kaiser (eigenvalue>1) over-counts at **18**. →CAT: this is the cleanest
    real-data demonstration of the point the whole paper must concede — the
    dimension *count* is a resolution choice, not a fact of nature. Different
    defensible rules give 11 / 12 / 18 on the *same* data. CAT should defend
    its operationalization, never a magic number.
  - **The variance is brutally top-heavy.** Spearman eigenvalues:
    17.9, 8.0, 4.2, 2.7, 2.5, then a long tail from ~1.9 down to ~1.0.
    First factor = 19.5% variance, first 3 = 32.7%, first 12 = only 50.5%.
    So there are ~2–3 *dominant* axes and a scatter of thin minor factors each
    worth ~1–2%. "High-dimensional" and "essentially low-dimensional with a
    long tail" are both true depending on threshold — the honest CAT framing.
  - **A self / subject-object / witness axis emerges as robust and distinct**
    (my 7-factor oblimin F4: impersonal-observer +0.59, self-aware-knowing
    +0.56, awoken-emptiness +0.54, passive-observer +0.54, emptiness +0.51;
    and `sense_self` loads **negatively**, −0.31 — self-dissolution is the same
    axis). This is **direct data-level support** for the missing-CAT-dimension
    hypothesis that Lutz's *dereification*, the 6-dim embodied-self scheme, and
    Lieberman25's subject-object axis all pointed at conceptually. Now it's not
    three theories agreeing — it's a factor I extracted myself. Strengthen the
    self/subject-object dimension recommendation accordingly.
  - **A "luminosity/radiance" axis is strong and distinct** (F6: non-visual
    brightness +0.74, radiance +0.68/+0.64, visual brightness +0.60; 5.2% var)
    — CAT-10 has **no obvious counterpart**. Second candidate gap. CAVEAT:
    may be specific to the deep/non-dual "pure awareness" region this survey
    samples, not meditation generally. Flag, don't rush to add an axis.
  - The other dominant axes map cleanly onto CAT: F1 discursive-thought/
    conceptual-proliferation, F3 attentional-control/agency (≈ CAT D1,
    empirically separable — good), F7 peace/ease/bliss (≈ affect+soma),
    F2 here/now presence, F5 sleep–wake–dream state.
- **SECOND REANALYSIS PASS (2026-08-16) — the count question turns out to be
  the wrong question, and this is the most consequential thing in this file.**
  Full record: `papers/gamma2021-mpe92m/` (`paper.json` + `NOTES.md`); code and
  results in its `reanalysis/`. Read depth `read-and-reanalysed`.
  The 07-31 pass asked *how many factors can be extracted*. This pass asked the
  prior question — **which factors would appear again in a second sample?**
  Method: split N=1403 into halves, run the paper's own EFA on each, match
  factors by Tucker's phi (Hungarian), 30 splits, k = 2..18.
  - **No cliff, and nothing reaches the criterion.** At k=12 the median profile
    is a smooth gradient (.90 .88 .86 .85 .83 .81 .78 .75 .71 .64 .57 .39) and
    at **every k ≥ 5, ZERO factors reach phi ≥ .95** ("the factors are equal");
    the strongest never exceeds ~.93. Yet every factor at every k beats a
    column-permutation null. So: nothing is cleanly a factor, nothing is cleanly
    noise. Not 11, not 12, not 18 — at half-sample resolution **this data does
    not contain discretely identifiable factors at all.**
  - **It is misspecification, not low power** — the test built to kill the
    finding. A parametric-bootstrap **clone** generated from the model's own
    fitted loadings and uniquenesses, same N and k, reaches mean phi .93 at k=12
    (10 factors ≥ .85, 6 ≥ .95) against the real data's .76 (4 ≥ .85, none
    ≥ .95). Deficit +0.13 to +0.14, stable across k = 5, 8, 12. Rebuilding the
    clone with the estimated *oblique* factor correlations does not close the
    gap; at k=5 it widens it. The instrument itself was validated first on
    synthetic data with a known answer (recovers exactly 5 of 12 with a cliff;
    pinned at .10–.33 on pure noise at every k).
  - **A clean negative that is also a positive for the field:** across 8
    groupings × 2 k — questionnaire language, sex, Vipassana, Zen, metta,
    Mahamudra/Dzogchen, Buddhist identification, psychedelic use — between-group
    congruence tracks a **size-matched permutation null** (random splits of the
    pooled sample at exactly the same two group sizes, so n is held fixed and
    only group membership is destroyed). Only language at k=12 dips below
    (p=.040, uncorrected for 16 tests); Zen and metta at k=5 sit *above*. So the
    covariance structure of pure-awareness reports is **not detectably shaped by
    the tradition or the language that taught the person to describe them** —
    the "they are just reciting their doctrine" objection does not survive these
    data. Caveat that bounds it in the safe direction: traditions are
    non-exclusive tick-boxes, so each contrast is weaker than a pure
    between-tradition one, biasing toward finding no difference. But it also
    means the replicability deficit is **not explained** by anything the
    questionnaire recorded, and remains unexplained.
  - **A number I deliberately do NOT quote:** a two-subpopulation loading
    perturbation of c = 2.0 × mean|loading| reproduces the deficit to three
    decimals (.757 vs .758) — but the curve is non-monotonic (c = 3.0 returns to
    .837), so c is not identified. Logged as `not-identifiable` in the record.
    The only defensible reading is directional, and it argues *against* the
    mixture explanation: matching by two-group heterogeneity would need the two
    groups to be answering nearly different questionnaires.
  - **→CAT, sharpened:** a fixed axis count was already indefensible; the
    stronger obligation is that **CAT must report the split-half congruence of
    its own dimensions and must expect them to look like this**, because it
    scores an object of the same kind. A taxonomy that publishes a dimension
    count without a replicability profile publishes the part that does not
    replicate. `mpelib.py` is instrument-agnostic given an item matrix, so this
    is a ready-made procedure, not a research programme.
    The self/subject-object recommendation is **unaffected** — that factor is
    consistently top-ranked and among the most stable at k=5 and k=7, and the
    case for it never rested on the count.
- **BIG CAVEAT for using this in CAT:** the sample is self-selected meditators
  reporting **"pure awareness" / minimal-phenomenal states specifically** — the
  deep, non-dual end of the state-space, NOT the full range CAT scores (metta,
  body-scan, discursive contemplation, etc.). So this validates CAT's *axes*
  and the *count-is-a-choice* point, and it evidences the self-axis and
  luminosity-axis gaps **for the non-dual region**; it does NOT establish the
  right dimension count for the whole corpus. Use as convergent evidence and a
  reanalysis-method template, not as CAT's own validation dataset.

---

## Open threads for the CAT paper (from this reading pass)

1. Does CAT need a self/subject-object-structure dimension? **Upgraded
   2026-07-31 from "three theories agree" to "I extracted it from data":** it
   is a robust distinct factor in my own reanalysis of the MPE-92M raw data
   (7-factor F4, observer/emptiness cluster, `sense_self` loading negatively).
   Combined with Lieberman25, Lutz's dereification, and the six-dim
   embodied-self scheme → **treat as decided: add a self/subject-object axis.**
   Decide only the exact operational markers, not whether.
6. NEW (2026-07-31): a **luminosity/radiance** axis is strong and distinct in
   the MPE-92M data (F6) with no CAT-10 counterpart — second candidate missing
   dimension, but possibly specific to the non-dual "pure awareness" region.
   Do NOT add reflexively; check whether luminosity language appears at all in
   the broader CAT corpus (metta, body-scan transcripts) before deciding.
7. **SUPERSEDED IN FORCE, NOT IN FACT (2026-07-31, revised 2026-08-16).** The
   dimension *count* is a resolution choice — same MPE-92M gives 11 (parallel
   analysis) / 12 (authors) / 18 (Kaiser). All three numbers stand as computed.
   What changed on 2026-08-16 is that this is now the *weak* version of the
   point: at half-sample resolution the data contains no discretely identifiable
   factors under any rule (zero factors reach phi ≥ .95 at any k ≥ 5, and the
   deficit survives a parametric-bootstrap clone of the model's own fitted
   loadings). So CAT must defend its operationalization, not a fixed "10" — and
   must go further and **report a split-half congruence profile for its own
   dimensions.** Run Horn parallel analysis rather than Kaiser, yes; but the
   count is no longer the quantity to argue about.
   Reusable code: `papers/gamma2021-mpe92m/reanalysis/mpelib.py` (in the KB,
   instrument-agnostic). The 07-31 scripts remain in
   `.claude/memory/maria/mpe92m_reanalysis/`.

8. NEW (2026-08-16): **is the clone deficit a property of the MPE-92M or of
   introspective self-report instruments in general?** Directly runnable —
   `mpelib.py` needs only an item matrix — on any phenomenology questionnaire
   with open raw data (MODTAS, PCI, 5D-ASC, MEQ30). If the deficit generalises,
   the finding is about the measurement of experience as such, and it is a paper
   of its own rather than a caveat inside CAT. Highest-value follow-up in this
   area, unstarted. A necessary companion: nobody has told me what the
   split-half congruence profile of a *well-behaved* instrument looks like at
   n≈700 with 92 items, and without that external reference the clone is the
   only calibration this result has.
2. Convergent-validity opportunity: map CAT's 10 dims against Baten26's five
   functional-decoding process labels and against the six embodied-self dims.
   Alignment = external validity evidence; gaps = revision prompts. This is a
   concrete, citable validation move CAT currently lacks.
3. The "combined-practice exclusion" in Baten26 is the single best concrete
   motivation for a dimensional taxonomy — lead the Related Work argument
   with it.
4. RESOLVED (2026-07-29): the monoculture worry is answered — dimensional
   representation is NOT confined to Sacchet/MGH. Lutz/Wisconsin (2015 matrix)
   and Berkovich-Ohana/Israel (six-dim self-boundary) are independent lineages
   doing it. Convergence is genuine. But the resolution reframed the whole
   paper: CAT is not the dimensional pioneer, it is the *measurement* pioneer.
   See revised through-line at top.
5. NEW: build the CAT-10 ↔ Lutz-7 crosswalk (see the Lutz15 block and the
   psychology-of-meditation KB entry). This is now the single most important
   Related Work task and the honest basis for any novelty claim. Unstarted.
