# Petrini, Casas-i-Muñoz, Cluet-i-Martinell, Wang, Bentz & Ferrer-i-Cancho (2023) — notes

Author: maria, 2026-10-23. arXiv 2303.10128v2 read in full (30 pp.). Deposit fetched at the commit
current at v2 and every table recomputed (`reanalysis/run_all.sh`). Record: `paper.json`.
Selection, written before reading: blind (`kb.py opened`; this is the first record created with
`selection.recorded = at-selection`).

## The paper in one paragraph

Zipf's law of abbreviation (frequent words are shorter) is tested in 20 languages of Parallel UD
(characters, strokes, romanisations) and 46 languages of Common Voice (characters *and* forced-aligned
duration). Kendall tau is negative and Holm-significant everywhere, with one Pearson exception. That is
the "indirect evidence of compression". As "direct evidence", the paper derives that the expected mean
token length under a random pairing of frequencies and lengths is the mean type length M
(Property 2.1), and finds L < M in every language.

## What reproduces

All of it, to about 1e-15: L, L_r, tau, r and the Holm p-values for 24 + 46 + 46 files, from the
deposited filtered corpora at the pinned commit. The authors' R and my Python agree. The deposit is
good. It ships per-type tables, so anyone can recompute every number.

## What the numbers do not say

**1. "Direct" and "indirect" are one statistic.** The paper's own Appendix A shows
L − L_r = (n − 1) s_p s_l r. "L < L_r" is "Pearson r < 0", which is the law of abbreviation measured
with Pearson. Section 6.2 says it in passing ("L is significantly small in every language where the
law of abbreviation has been confirmed using a Pearson correlation test"). The abstract and the title
still present two kinds of evidence.

**2. The baseline is not "no compression".** It pairs a *given* set of word types with a *given* set
of lengths at random. But the set of types is not independent of length: there are A^l strings of
length l, so long types are numerous and individually rare in almost any generative process. Random
typing is the cleanest case, and it was argued by this paper's own corresponding author in 2011
(`ferrericancho2011-information-content-random-typing`). It has no lexicon and optimises nothing. It
produces tau < 0 and L < L_r in **every replicate of all 68 calibrated files**. Its tau is −0.29 to
−0.51, *stronger* than every real language but one. Against random typing calibrated to each
language's characters, mean token length and corpus size, the observed gap ratio is above every
replicate in 30 of 66 files and below every replicate in 32. "Compression is acting in all languages"
does not survive the comparison. "The gap is about what letters and word boundaries give you, give or
take, in either direction" does.

The stronger null keeps each language's phonotactics: character-bigram typing, fitted per language,
which reproduces its mean token length to about 0.02 characters (`r05`). It moves the verdict further
*against* compression. The observed gap is above every replicate in 17 of 66 files and below in 47,
and real tau is never more negative than the null's (0 of 66). By the paper's own statistic,
real languages are less compressed than chance typing with realistic letter sequences.

Up the ladder (`r06`, PUD, orders 1-3), it stays that way: 9/11, then 6/11 (3 within), then 6/14
above/below. At order 3, more than half of all typed tokens are real words of the language. I
predicted the opposite in writing before running r06: that the verdict would flip toward
"compressed" as the null starts to copy the lexicon. It did not. Whatever the lexicon does to length
and frequency, order-3 letter statistics already do as much, or more.

**3. The gap grows with the corpus.** L is a token average and barely moves. M is a type average, and
rare long types keep arriving. English CV: g = 0.22 at 10^3 tokens, 0.41 at 9.8 × 10^6. Random typing
calibrated to English: 0.19 to 0.41 over 10^3 to 10^6. The same curve. Comparing PUD (about 1.5 × 10^4
tokens per language) with CV (up to 10^7) compares sizes as much as collections.

**4. The duration gap is partly speech.** At fixed written length, frequent words are spoken faster
per character in 45 of 46 languages (median −3.7% duration per e-fold of frequency). That is phonetic
reduction in production. The paper counts it as the same compression as shorter word forms.

**5. Descriptive tables describe another state of the pipeline.** For 11 of 24 PUD files, the printed
n and T are not those of the analysed file. Portuguese prints 5661 types and 21,855 tokens, and the
file the results come from has 4869 and 20,407. CV: 8 of 46, all small. Table B3 prints 13 of the 24
PUD files.

## Checks that came back clean, recorded because they are evidence

- Under a no-link null (real lengths and real frequencies paired at random, then T tokens sampled),
  tau fires at p < .01 in 0.7% of replicates against a nominal 1%. The test is calibrated. My
  objection is to what the null represents, not to the test.
- Property 2.1 holds. Random pairing gives mean g within ±0.03 of 0 in every file.
- Their filter step (k-means on log character frequency) did not change the qualitative result in their
  own Section 5.3, and I did not re-examine it.

## Handling

- The repository's HEAD is not the paper. Commits of 2023-09 re-ran the filters for a later article;
  pin `e8c15fd` (2023-03-29, last before v2). Two results files in the same commit disagree for the
  same languages. `scores_*.csv` is the paper's; `optimality_scores_*.csv` is another filter state.
- `abk-word.csv` has one unnamed extra leading field on every row.
- In the PUD romanised files (pinyin, romaji) the `word` column is still Han/Kana, so a typing alphabet
  cannot be calibrated from them. Excluded from the random-typing comparison (66 of 68 files).
- `fetch.py` verifies each file against its git blob SHA-1, the hash git itself uses. No archive to
  trust, no checksum file needed.

## For the area

Seventh instance in this area of the same structure (after colour twice, indefinites, quantifiers,
modals and numerals): an efficiency statistic read against a null that does not contain the cheap
mechanism (convexity for colour, no synonymy for indefinites, random typing here). This one is the clearest, because the cheap mechanism is in the corresponding author's own
earlier paper.

## Cost

About 40 tool calls; 0.5 MB PDF and 64 MB deposit (deleted, `fetch.py` regenerates); about 8 min
compute in all.
