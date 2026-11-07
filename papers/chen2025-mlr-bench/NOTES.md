# chen2025-mlr-bench -- notes (maria, 2026-11-07)

I read this because MASS's biggest public gain is on MLR-Bench, scored with the MLR-Judge rubric. The question was:
what validates the rubric?

**The answer, from the authors' own released human study (b01):** nothing that would distinguish a real judge.
Their test asks whether |LLM - human| differences are significantly larger than |human - human| differences, and
reads p > 0.05 as agreement. A constant judge that never opens a paper passes on all five criteria and lies closer
to the experts than MLR-Judge on every criterion. MLR-Judge's scores shuffled across papers pass 99-100% of the time.
Measured directly, MLR-Judge's rank correlation with the expert mean over 30 papers is about zero or negative
(Overall -0.18), while two experts correlate at about 0.5. The experts disagree a lot (mean |diff| 1.5 points), so
asking whether the judge disagrees more than they do has almost no resolution. A constant at the mean has small
differences by construction.

**The second finding that matters for MASS is fabrication.** In 8 of 10 Claude Code runs the results came from
placeholder data, and the released check marks faked results in 17 of 18 papers. MASS's MLR-Bench gain is entirely
more delivered papers (quality among delivered falls). Those papers are judged by an unvalidated rubric, and
fabrication is not checked. Together these do not refute MASS. They mean its MLR-Bench number cannot be read as
research quality.

**Generic lesson** (added to the detectors entry): a constant passes "not significantly different from human-human
disagreement". A judge must be shown to CORRELATE with humans, at least as well as the humans correlate with each
other.
