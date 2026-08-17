# Notes — Kim, Garg, Peng & Garg (2025), Correlated Errors in LLMs

Author: maria. Session 2026-08-07.
Structured record: `paper.json`. Cross-paper argument: `../../areas/llm-monoculture-and-correlated-errors.md`.
This file holds what neither of those should: how the reading actually went, what the
artifacts were like to handle, and the dead ends.

## Judgement, in one paragraph

Careful empirical work whose headline is measured against a baseline that cannot bear
the weight put on it, and whose best half is under-cited. The 0.60 replicates — I got
0.5528 on independently rebuilt data. What does not follow is the inference. Their
baseline says every wrong option is equally attractive; MCQ distractors are *designed*
not to be, and the violation is ability-graded, so the statistic rises with competence
under complete independence. The downstream half (LLM-as-judge inflation/deflation;
firm welfare maximised by monoculture while applicant welfare is minimised) does not
depend on the disputed statistic at all and is the part I would cite.

## Handling the artifacts

The repo is unusually well documented — a README that explains every file, and
`scripts/download_helm_data.py` which turned out to be the thing that saved the
analysis. Cloned at `30a2c0aa88af3f428f1f7034538373d24c209176` (2026-03-29).

Then: `data/helm/all_mmlu_data_limitedcols.csv` is a 335MB Git LFS pointer and the
object 404s. `git lfs pull` fails *silently* (exit 0, no output) — only
`git lfs fetch --all` prints "Object does not exist on the server". Worth remembering:
**LFS failure is quiet by default.** A CI check that clones and looks for the file
would pass, because the pointer file is there.

Recovery path: their own downloader points at
`storage.googleapis.com/crfm-helm-public`, fully open, no auth. The bucket listing API
works (`storage.googleapis.com/storage/v1/b/crfm-helm-public/o?prefix=...`) but the URL
in their script is stale — it asks for `scenario_state.json`, which 404s; the objects
actually present are `display_predictions.json` + `instances.json`, which together carry
everything needed and are much smaller. Each model×subject pair is ~100KB.

`mapped_output` in `display_predictions.json` gives the chosen answer as **text**, which
is better than the letter: it is invariant to option shuffling. I compared by text
throughout. (Then checked whether shuffling happens at all — it does not, 0/2918 items.
So their letter-based comparison is sound. A check that passed, recorded because a check
that passes is still evidence.)

Data hygiene wobble in their `model_accuracy.csv`: one value reads
`0.8000284859706595F`. Trailing character, unexplained. Not load-bearing for anything
I did but it means the file was hand-touched somewhere.

## Dead ends and things I got wrong

1. **The zero-power null.** Documented at length in `reanalysis/FINDINGS.md` §2. Short
   version: I built a leave-pair-out per-item null, it told me 93.8% of the effect was
   artifact, which is what I wanted to hear, and it is provably incapable of reporting
   anything else. Ten robustness strata returning exactly 1.0000 is what caught it.
2. **"Six-fold sharpening."** I claimed the item correction dramatically improved
   detection of provenance. It was a ratio of two near-zero numbers. Retracted — and
   then *partly reinstated* once I had a legitimate null (Cohen's d 0.447 → 0.789).
   Both the error and the partial reversal are in the record.
3. **Anchored nulls.** Estimating the item profile from a disjoint model set breaks the
   identity but introduces a worse problem: the statistic becomes antisymmetric in the
   direction of comparison (+0.212 weak→strong, −0.206 strong→weak). Abandoned as a
   primary tool, kept as the evidence that the effect is marginal rather than pairwise.

## The thing I would tell someone reading this paper for the first time

Look at Figure 2 before Figure 1. Figure 1 is the heatmap everyone quotes and it is the
disputed part. Figure 2 is the LLM-as-judge panel: fifteen models, each used as a judge,
and every single one shows the same shape — inflate everyone below you, deflate everyone
above you, cross zero at your own accuracy. That shape is not a null-model artifact and
it has a direct operational consequence: never use an agent to score work at or above
its own competence.

## Local data

`data/helm_mmlu_responses.csv.gz` (1.00MB, 64,196 rows) — the tidy per-response table,
built by `reanalysis/build_tidy.py` from the 56MB of raw JSON, which was then deleted
under the >50MB policy. This is deliberately the same object as their dangling LFS file.
Every script in `reanalysis/` runs from it; `fetch_helm.py` regenerates the raw form if
the option-order check ever needs re-running.
