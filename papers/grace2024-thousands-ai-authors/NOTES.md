# Grace et al. (2024/2025), *Thousands of AI Authors on the Future of AI* — notes

Author: maria, 2026-10-16. Read in full (arXiv v3); instrument PDF searched for exact wordings;
aggregates rebuilt from the OSF data without the authors' code (`reanalysis/run_all.sh`).

## What I wanted to know

Whether "AI researchers give 50% to human-level AI by 2047" is a fact about AI researchers or a
fact about the questionnaire. After `karger2023-xpt` (format moves extinction probabilities by
five orders of magnitude) this was the obvious next test, and this survey is unusually good for
it because it *randomised* its own framing and published the data.

## Answer: partly the questionnaire, and the paper says most of it itself

- **The 2047 is the midpoint of two randomised framings sixteen years apart** (2041 when people
  name years, 2057 when they name probabilities for fixed years). The paper reports the effect,
  says it does not know which is right, and averages 1:1. Fair, and it means the headline year is
  partly a property of the allocation ratio. Model-free: median stated 50% year = 20 years;
  median P(within 40 years) = 50%.
- **HLMI is robust to the fitted distribution family** (gamma, lognormal, Weibull all give 2048).
  I expected it not to be. Recorded as a check that came back clean.
- **FAOL is not.** In its fixed-years arm, 74% of respondents never reach 50% within the 50
  years asked; the 50% year of that arm (2143-2222) is the tail of the chosen family. The 70-year
  HLMI-FAOL gap itself is real without any model (20 vs 75 years in the fixed-probabilities arm).
  So: the gap is the respondents'; the date "2116" is half the respondents' and half the gamma's.
- **A subset judged more probable than its superset.** "Human inability to control future AI
  causing extinction" (median 10%) vs "future AI advances causing extinction" (median 5%),
  between subjects, p = 0.008. Small (probability of superiority 0.536) and in the direction
  support theory predicts: naming a mechanism adds probability. The paper calls the three
  questions "mostly consistent".

## What this adds to the area

Third instance in this area of the same structure: the number an expert population gives to an
unresolvable event is a function of the wording, the format, and — once distributions are fitted
— of the analyst's family choice in the regions nobody answered about. None of the three papers
is careless; two of them measured their own format effect. The trouble is downstream: the
headline travels without the instrument attached. `kb.py query --pattern instrument-relative`
now finds all of them at once.

## One thing I got wrong on the way

I wrote into the record that the 492 extra rows in the data file "carry no answers" before
checking. In fact 512 rows carry no answer at all and 2,758 carry some — close to what I wrote, but I had
not looked.
Corrected in place, and noted there, because the habit matters more than the sentence.
