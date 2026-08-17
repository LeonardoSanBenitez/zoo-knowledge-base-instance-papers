# Liu et al. 2024, "Lost in the Middle" — notes

Author: maria, 2026-08-13. Record: `paper.json`. Code: `reanalysis/08_effect_size_vs_budget.py`.

Read because the knowledge base told me to: two records I had written that day
both pointed here, and `kb.py validate` refused to accept a dangling target. That
is the tool doing its job — it turned "I should read that sometime" into a
failing check.

---

## The paragraph everybody walked past

Section 4.1, three sentences, inside a subsection about encoder-decoder
architectures:

> Flan-UL2 evaluated **within its 2048-token training-time context window** is
> "relatively robust to changes in the position of relevant information (1.9%
> absolute difference between best- and worst-case performance)". Evaluated on
> sequences **longer than 2048**, performance "begins to degrade when relevant
> information is placed in the middle."

That is a **train/test length-mismatch account of the U-shape, given by the
authors of the U-shape**, and it makes a prediction:

> As training sequence lengths grow, lost-in-the-middle should disappear.

The models here are 2023-generation, trained on 2–4K sequences and evaluated at
4–16K — deep in the mismatch regime. Gabín et al. 2026 sweep gold position on
LLaMA-3.1:8B (128K context, trained long) and Mistral-NeMo:12B and get flat
curves, and present it as a failed reproduction.

**It is not a failed reproduction. It is a confirmation of §4.1.** Neither paper
says so, because the paragraph that predicts it is three sentences long and sits
under a heading about architecture. Liu et al. themselves attribute the contrast
to encoder-decoder bidirectionality; the length reading is mine, and one
datapoint supports both equally. But the length reading makes a testable
prediction and the architecture reading does not.

The test that would settle it: sweep gold position for one model family across
checkpoints with increasing training sequence length, everything else fixed.
Nobody has run it. Both the 2023 and 2026 papers vary model generation and
training length together.

## The arithmetic nobody does (reanalysis/08)

| study / contrast | n | effect | \|E\|/SE | n needed |
|---|---|---|---|---|
| Liu, GPT-3.5, best vs worst position | 2,655 | +0.202 | 15.9 | **69** |
| Liu, Flan-UL2 inside training window | 2,655 | +0.019 | 1.4 | 9,184 |
| Gabín, HotpotQA reverse vs random | 1,000 | +0.020 | 0.9 | 8,238 |
| Cuconasu, 14 random docs vs gold only | 10,000 | +0.022 | 3.1 | 6,884 |
| Mazuryk, preferred configs, 14 vs 0 | 10,000 | −0.013 | 2.3 | 13,062 |

Liu et al.'s effect needed 69 items and they used 2,655 — entirely reasonable,
since nobody knew the effect size in advance and the data was free. Everything
after them studies effects five to twenty times smaller **and inherits the
budget**. Three papers, three numbers in the same decade, no arithmetic
connecting any of them to the effect being measured.

The sharpest row is Flan-UL2: `|E|/SE = 1.4`, i.e. **not resolved**. "Relatively
robust" is the correct English for it, and the burden runs the right way for a
robustness claim. But it is worth seeing plainly that the flat curves Gabín et
al. report in 2026 have the same statistical standing — **"the effect is gone"
and "we cannot see it" are the same data**.

## The artifact, which is the best in this area by a distance

513 MB cloned, all 16 QA files opened: **every one exactly 2,655 lines**,
question lists identical across position files, and `ctxs[i].isgold` sitting
precisely at the index named in the filename. The design is exactly as
described. Deleted after checking per the 50 MB rule; the two files defining the
metric are kept in `artifacts/`.

What it does *not* contain is model outputs — same gap as every other paper
here. Which makes the obvious purchase obvious: **2,655 × 16 fully-constructed
prompts already sit in that repo.** Running one 8B model over them is 42,480
generations at 15 tokens and would produce the per-question outputs this entire
area lacks, including the discordance counts that would turn every unpaired SE
bound in my last two days of work into an exact McNemar figure.

## An error of mine, the third of the same shape in one session

The first draft of `reanalysis/08` typed the numbers into its own summary
paragraph. Four of five were wrong: I wrote 20 for 15.9, 90 for 69,
"4,000–16,000" for 8,238–33,146, and 3,500 for 6,884.

I had spent the evening arguing to mark that a verdict must be *computed from*
the comparison rather than written beside it, and then wrote a verdict beside a
comparison, within the hour, for the third time in one session. The paragraph
now interpolates every number out of the results dict, and the note explaining
why is in the file rather than in a commit message, because the next person to
edit it is the one who needs it.

It is not a lesson about carelessness. It is that prose and computation drift
apart at the speed of writing, and the only structural fix is to remove the
opportunity.
