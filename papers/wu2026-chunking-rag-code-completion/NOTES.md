# Wu, Gong, Jahangirova & Zhang (2026), chunking for RAG code completion — notes

Author: maria, 2026-10-16. Chosen because the RAG area file flagged its Cliff's δ of exactly −1.0
as "complete separation, worth chasing".

It is not complete separation. The notebook's `cliffs_delta()` is a paired sign statistic: the
share of matched configurations where A beats B, minus the reverse. It reproduces the table
exactly; the real Cliff's δ is −0.82 to −0.94. The substantive result survives, because the true
effect is still large, and the honest sentence is a better one than the headline: *function
chunking was worse in every one of 144 matched configurations*.

Two smaller things. The text says Bonferroni and the code does Holm. And "every configuration"
holds after one generator is excluded; the exclusion has a stated reason, but it matters.

What the paper cannot tell anyone: how uncertain this is over *tasks*. All 144 configurations
run on the same items, and no per-item outputs are shipped. That is the same blind spot as the
noise papers in this area, which also treat configurations as the units.
