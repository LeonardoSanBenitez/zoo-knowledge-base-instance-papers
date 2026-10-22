<!--kb
id: area:computational-buddhist-studies
labels: kind:paper-notes, area:computational-buddhist-studies
triggers: computational analysis of the Pali Canon; stylometry of Buddhist texts; vocabulary overlap between Buddhist schools; lexical diversity of suttas; quantitative study of Buddhist canonical texts; Abhidhamma enumeration statistics
verified: 2026-10-16
-->

# Computational Buddhist studies

Author: maria. Started 2026-10-16. Records: `bose2026-pali-canon-stylometry`, `allon2022-early-buddhist-texts-repetition`.

**Scope.** Quantitative claims about Buddhist canonical and commentarial texts: stylometry,
vocabulary, formula and repetition structure, cross-school parallels. Read with two questions:
what layer is being measured (Pali, translation, translator's apparatus), and what an unrelated
text scores on the same statistic.

## The lead (one record)

- **Similarity needs a baseline.** English texts with no Buddhist connection already have 31-34%
  of their vocabulary inside the Theravada Vinaya's, at the size where the paper reads 49% as
  "shared legal heritage". The Theravada Sutta overlaps the Vinaya more than the
  Mulasarvastivada Vinaya does. `bose2026#c1`.
- **Know the layer.** In the PDF edition, about half of the Vinaya's vocabulary is the
  translator's notes. `bose2026#c2`.
- **How repetitive is a sutta, and whose number is it?** Allon's famous 87% (DN 25, hand count)
  depends on the definition: verbatim 8-word repeats cover 54% of DN 25 and 4-word repeats 65%
  (his verbatim + minor-modification total), but no contiguous measure reaches 87%. DN 25 is
  typical: median of the 186 DN+MN suttas. `allon2022#c1`.

## Open threads

1. Heritage measured on rules, not words: SuttaCentral's parallel tables align Vinaya rules across
   schools; the share of rules with parallels is the quantity a heritage claim needs.
2. Pali-original analyses (Zigmond's `tipitaka` R package) remove the translator layer entirely.
3. Oral-formulaic repetition as redundancy: a channel-coding reading of sutta repetition (error
   protection for oral transmission) is testable with compression ratios on the Pali text vs
   matched prose. Not yet found in the literature.

## Repetition as a trace of transmission (added 2026-10-23, maria)

Record: `maria2026-pali-repetition-oral-written` (pre-registered; answers `allon2022`'s open question). Within-text
verbatim repetition (share of tokens in a recurring word 8-gram, 20,000-token windows, Chattha Sangayana edition):
suttas 0.59, their commentaries 0.02, sub-commentaries 0.003; canonical Abhidhamma 0.67; the written Visuddhimagga
0.06. Paired at matched length, sutta > own commentary in 44/44. The genre objection ("discourses repeat, exegesis
does not") fails on the Abhidhamma, which is not discourse and repeats most. The edition's '...pe...' elisions make
every canonical figure a floor. One text per category for the genre control; mnemonic vs combinatorial readings of
the Abhidhamma's repetition are not separable by counts.
Addendum 2: three more Abhidhamma books 0.56-0.89; the late books the Burmese canon took in (Milindapanha 0.26,
Nettippakarana 0.21, Petakopadesa 0.03) sit in between -- a gradient by mode and milieu of composition, not a
switch by canonical status. The pre-registered 'all < 0.10' failed.

