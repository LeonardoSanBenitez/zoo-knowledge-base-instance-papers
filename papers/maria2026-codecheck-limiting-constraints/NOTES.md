# Who is the binding constraint when a reproduction is incomplete?

Read 2026-09-08. Source: the CODECHECK register, 132 certificates, 131 with a written
summary by the person who did the check. CC-BY-4.0, concept DOI `10.5281/zenodo.4059767`.

I read all 131 summaries. That is the whole method, and it took longer than the analysis.

---

## Why I went looking

I had just finished retrofitting two papers into
`dev-science-ops/paper-retrospective-reproducibility`, a project whose central worry is
stated in its own `CONTRIBUTING.md`:

> **A false fail is worse than a false pass.** A false pass leaves things as they were; a
> false fail makes someone change work that was correct, or tells an author their artifact
> is broken when it is not. Every documented harm in this project's evidence base is a
> false fail.

That project writes reports about other people's work. So the question is not *how often do
reproductions fail* — everyone measures that — but **when a reproduction stops short, whose
constraint was it?** If most of the time it is the checker's own budget, then a report that
says "partially reproduced" without saying whose limit it was is systematically unfair, at
scale, by construction.

Nobody publishes that number. The CODECHECK register is the only place I know where a
hundred-plus third-party reproducers wrote down, in prose, what stopped them.

## The answer

**62 of 131 certificates (47%) report a less-than-complete reproduction.** Hand-coding each
one by binding constraint:

| binding constraint | n | share |
|---|---|---|
| **deposit** — something the authors released was missing, undocumented, broken, or gave different numbers | 23 | 37.1% |
| **reviewer** — the checker's compute, time, hardware, licence, or chosen scope | 21 | 33.9% |
| **third-party** — privacy, IP, commercial licence, paid API, account wall | 8 | 12.9% |
| **inherent** — a physical experiment, a human survey, a manual step | 5 | 8.1% |
| unclear | 3 | 4.8% |
| stochasticity alone | 2 | 3.2% |

> **38 of 62 incomplete reproductions — 61% — were not limited by anything the authors did
> or failed to do.** Range 56–61% under the worst-case recoding of the three `unclear` rows.

The sentences behind that number are not ambiguous:

- *"due to the lack of available computational resources **on the side of the reviewer**"* (2024-013)
- *"the time constraints of this review ... allowed only a partial reproduction ... **with more time, a successful reproduction of the entire workflow is highly likely**"* (2022-005)
- *"I initially attempted a full reproduction, but had to abandon this due to time constraints"* (2025-010)
- *"the author recommends the use of an HPC cluster, which is **beyond the scope of this CODECHECK**"* (2025-006)
- *"data generation relied on paid APIs (OpenAI, DeepSeek, Google Gemini) that were not accessible for re-running"* (2026-016)

## The robustness check that mattered, and it passed

One venue — AGILE GIScience Series — supplies **55%** of the register and runs a structured
reproducibility-review programme. That was the obvious way for the finding to be an artifact:
a single programme's conventions producing a single pattern of limits.

| subset | n coded | not limited by the deposit |
|---|---|---|
| AGILE GIScience | 46 | 28 (**61%**) |
| everything else | 16 | 10 (**62%**) |

One percentage point apart. Small n outside AGILE, so this rules out the artifact rather than
establishing the rate independently — but it rules it out in the direction that was worrying.

## Two structural things I did not go looking for

**CODECHECK is peer review, not auditing.** Median gap from work publication to check:
**6 days.** **37% of checks happen before the work is published.** 76% within ±90 days.

This matters and it is easy to misuse. 21% of summaries mention working with the authors, and
several are warm about it — *"the authors accompanied me throughout this process, providing new
versions of the code files to correct the errors I encountered"* (2024-010); *"17 emails over
~10 days"* (2025-013). **That cooperation rate is a property of the invited setting.** Anyone
planning unsolicited post-publication contact with strangers and taking these numbers as an
expectation is reading a figure generated under a different social contract.

**Almost nobody states a denominator.** Only **6.1%** of summaries say which elements of the
paper were *eligible* for reproduction before saying how many reproduced. The ones that do are
conspicuously easier to read:

> *"Out of the 17 Figures in the paper, 10 are eligible for reproduction. Out of the 10
> eligible Figures, 8 Figures where successfully reproduced, one Figure was partially
> reproduced and one Figure was not reproducible."* (2022-011)

Without that first sentence, "8 reproduced" and "8 of 17" and "8 of 10" are the same string.

**And the register is concentrated in venue but not in people:** 55% from one venue, but 72%
of the 80 named codecheckers did exactly one check. Top checker 14.6%, top five 35.4%.

## The instrument I threw away, kept in the folder

My first pass was a regex classifier. It is still in `reanalysis/classify_codecheck.py`,
marked `present-but-insufficient` rather than deleted, because a superseded instrument that
has been deleted cannot warn anyone. It failed both ways:

- **False positive.** *"This reproduction required several hours of compute time, **but the
  reproduction itself was straightforward**"* (2020-011) and *"**Due to** long computation
  times, **only a subset** of the results could be checked"* (2021-001) share their vocabulary
  entirely. They differ in the consequence clause.
- **False negative, and the worse one.** *"A **full reproduction** requires substantial
  computational resources"* (2026-012) was classified as a full reproduction, because the
  phrase appeared after the word "Partial" and my tie-break took the last match. It means the
  opposite.

**The general form: where a code depends on which clause a phrase sits in, a lexical
classifier measures the vocabulary and reports it as the finding.** Same family as the
error in `the-null-is-a-modelling-choice.md` — an instrument agreeing with the analyst
because it cannot see the thing that would disagree.

The hand-coding that replaced it carries a quoted fragment per row, and
`handcode_limits.py` **verifies every fragment against the source before reporting anything**.
That check earned its keep immediately: it refused to run over a misquotation of 2024-008,
where the register's own text contains a doubled "that" and my quote had silently tidied it.
A quote I had tidied is a quote I had partly written.

## What this is for

Three concrete consequences for anyone writing a report about someone else's work:

1. **Never report an incomplete outcome without naming whose limit it was.** On this
   evidence, the majority are yours. `not-attempted` and `blocked` are not the same verdict
   and the difference belongs in the sentence, not the appendix.
2. **State the eligible denominator before the numerator.** 94% of these summaries do not,
   and their outcome counts are unreadable as a result.
3. **Do not import CODECHECK's author-cooperation rate into an unsolicited setting.** Six
   days median, 37% pre-publication. It is a different activity wearing the same name.

## What I did not do

Coded the summaries, not the linked reports. Every certificate has a full report with far more
detail; the summary is what a reader of the register sees, and the gap between the two is
unmeasured and is the first thing I would do next. I also left a 133-vs-132 discrepancy between
`register.csv` and `docs/register-full.json` unchased, and recorded it rather than quietly
picking one.

And nothing here says an incomplete reproduction is *bad*. A check that stops at a sample
dataset and says so may be worth more than one that grinds through a national-scale workflow
and reports a tick. The register gives no way to tell a well-scoped partial from an abandoned
one, and I do not know what would.
