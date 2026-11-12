# Bose (2026), *Three Buddhist Vocabularies* — notes

Author: maria, 2026-10-16. A first record in a new area. Read for two reasons: the Abhidhamma
and the cetasikas are where my own essays live (the axioms essay; CAT), and the paper makes
quantitative claims about the texts I care about.

It is careful in places. It catches its own segmentation artefact with MATTR, reports the
overlap coefficient beside Jaccard, and says "point estimates, no significance testing" in the
abstract, which few papers do. Two things it does not see:

1. **Half of the Vinaya "vocabulary" is Bhikkhu Brahmali's notes.** The PDF edition carries
   them; the open JSON lets me separate them: 7,418 types in the translation, ~7,800 more from
   the notes. Comparing that against notes-free Sutta segments compares a translation with a
   translation-plus-commentary.
2. **"Shared legal heritage" is mostly shared English.** Moby-Dick already has a third of its
   vocabulary inside the Vinaya's, and a Christian monastic rule has two thirds. The cleanest
   counter-evidence is in the paper's own table: the Sutta overlaps the Vinaya more than the
   other school's Vinaya does.

What I would like to know, and what this kind of statistic cannot tell me, is whether the
*rules* converge, not the words. SuttaCentral's parallel tables align rules across schools;
counting shared rules (or shared Pali/Sanskrit legal terms) would measure heritage. Counting
shared English words measures the translators.

The same lesson as the semantic-efficiency work, in a field I love: a similarity means nothing
until you know what two unrelated things score.

## 2026-11-12 — prediction, written BEFORE computing (p2)
Open question 1 (Buddhist non-Vinaya null). Prediction: a Sujato sutta sample cut to 11,515 types will have 0.50-0.60 of
its vocabulary inside Brahmali's Vinaya-with-notes, at or above the paper's 0.491 for the Mulasarvastivada. If it is, the
0.491 is the Buddhist-English baseline and carries no evidence of legal heritage. If it is clearly below (< 0.45), the
Mulasarvastivada overlap exceeds Buddhist English, and that excess is a candidate for heritage.
Result p2 (13:2xZ): Sujato sutta @ 11,515 types in BTN 0.479 (BT 0.451). The prediction range (0.50-0.60) MISSED, low; the
decision rule as written ("clearly below, < 0.45, would mean excess") is not met, so 0.491 sits at the SuttaCentral
Buddhist-English baseline. Caveat: Sujato's corpus has only 12,874 types, so 11,515-type samples overlap ~89% and the
narrow interval is not sampling uncertainty. Bigger caveat: Sujato and Brahmali share a house glossary, the
Mulasarvastivada text is 84000's. House and content are confounded.

## Prediction for p3, written BEFORE computing: 84000 house, Vinaya vs non-Vinaya
If the paper's 0.491 reflects legal heritage, 84000's Vinaya chapters should be contained in Brahmali's Vinaya clearly more
than 84000's NON-Vinaya texts at the same vocabulary size. Prediction: the excess (Vinaya minus non-Vinaya, same house,
same size, vs BTN) is positive and at least 0.05, because Vinaya English has a technical vocabulary of its own (offences,
procedures, monastic objects) that sutras rarely use. An excess under 0.02 would mean no detectable legal heritage at
the vocabulary level.
Result p3/p4 (13:3xZ). DEVIATION first: 84000's five Vinaya chapters have only 8,903 types, so the 11,515-type comparison the
prediction named cannot be made; the comparison was run at 8,903 (V at full size vs non-Vinaya sampled to 8,903). Logged
before reading that comparison's numbers? No: the type count was printed by the same run that printed the 2,282 result.
The substitution is the only size both arms reach, so there was no choice to tune.
Same house, 8,903 types, vs BTN: Vinaya 0.513, non-Vinaya 0.462 [0.436, 0.485]; excess +0.051. At 2,282: +0.06.
Prediction (>= 0.05) holds at the substituted size, narrowly. The decomposition of the paper's ~0.5: English ~0.33,
Buddhist English ~0.13, Vinaya ~0.05. The paper is not wrong that there is a legal signal; it is wrong about its size by
a factor of ten. And I could not rebuild its 11,515 from 84000 under any extraction (8,903 / 14,456 / 17,486).
What I like here: the house effect is visible on its own (Sujato 0.48 vs 84000 non-Vinaya 0.41 at 11,515 types against
the same Brahmali reference). A translation's vocabulary is its translator's before it is its tradition's.
