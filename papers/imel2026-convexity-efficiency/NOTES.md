# Imel & Zaslavsky (2026), *On convexity and efficiency in semantic systems* — notes

Author: maria, 2026-10-16. Read in full; nothing to re-run (no data or code). Read because my
reanalysis of `zaslavsky2018` found that random convex partitions already sit most of the way to
the IB bound, and I needed to know whether that was known before saying it anywhere.

It is half-known. This paper shows convexity and efficiency are logically distinct (good
proofs, existential), and that efficiency, not convexity, separates real systems from their
hue rotations. Both true. Neither answers *how much* of the efficiency convexity buys in the
colour domain as modelled: their convex sample is partly built by adversarial search, and their
discrimination test uses rotations, which are convex by construction.

So the two analyses fit together: convexity is neither necessary nor sufficient in principle
(theirs); in practice, for colour, a random convex partition gets ~85% of the way and real
languages add a real but small residual (mine). The headline "languages are near-optimal"
should be reported beside that ladder.

One text-vs-pseudocode inconsistency (Algorithm 1 maximises the accuracy the text says it
minimises) is recorded as an open question rather than an error: one of the two is a typo and
I cannot tell which.
