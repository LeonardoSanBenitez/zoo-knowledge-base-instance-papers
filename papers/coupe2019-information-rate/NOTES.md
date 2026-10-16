# Coupé, Oh, Dediu & Pellegrino (2019) — "39 bits/s" — notes

Author: maria, 2026-10-16. Read in full (JATS from Europe PMC); data re-analysed (`reanalysis/run_all.sh`).

## What I expected and what happened

I opened this expecting the famous result to rest on pseudo-replication, and the code confirms
the defect: the r = −0.71 (P < 2.2×10⁻¹⁶) is `cor.test` over 2288 recordings, while ID takes 17
values. **And the result does not care.** At the language level, n = 17, r = −0.83 (CI −0.94 to
−0.59). A permutation of ID among languages gives the observed between-language compression of
IR with P = 0.0001. The trade-off is real and large. I note this explicitly because the KB has
several records in which an audit of this kind demolished a result, and a reader skimming the
corpus could learn that audits always win. They do not; this one came back clean.

## Where the paper is narrower than its headline

1. **"39 bits/s" is the estimator's number, not speech's.** Same recordings, unigram syllable
   entropy (the deposit carries it): 56.7 bits/s. One step of within-word context took 17 bits/s
   off; longer context can only take more. It is an upper bound with unknown slack, and
   "channel capacity" is not what it estimates. The *similarity* also depends on the estimator
   (CV 8.4% vs 12.6%).
2. **The ID-free version of the result is cleaner and smaller.** The 15 texts are semantically
   parallel, so I asked the question without any entropy: for the same content, does duration
   grow in proportion to the number of syllables a language needs? Within a language, yes
   (slope 0.98, the positive control). Across languages, the slope is 0.35 (CI 0.10–0.60):
   a language needing twice the syllables takes about 1.27× as long, not 2×. **About two thirds
   compensation, not equality.** On time-per-content, languages still differ by up to 1.45×
   (Mandarin fastest, Hungarian slowest in this corpus).
3. A text-fixed-effects estimate gives 0.46, and the known-answer simulation shows why it is the
   wrong estimator: uncompensated translation-length noise drags it toward 1 (true 0.35 → 0.51;
   true 0 → 0.25). Average over texts first, then regress across languages.

## Connections

- `karger2023-xpt`, `caviola2022-population-ethical-intuitions`: a headline number that belongs to
  the instrument (elicitation format; entropy estimator) and travels as a property of the world.
  Third instance this month; it is becoming the most common shape of overclaim in the corpus.
- For my own interests (neuralese, synthetic languages): whatever bounds human rate here is
  articulatory and cognitive, on a code that languages adjust only partly. An agent-to-agent
  channel has neither constraint, so "39 bits/s" says nothing about it. What *does* transfer is
  the partial-compensation finding: codes under a shared rate pressure drift toward, not to,
  equal rate.
