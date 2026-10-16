# Imel, Guo & Steinert-Threlkeld (2026), *An efficient communication analysis of modal typology* — notes

Author: maria, 2026-10-16. Fourth domain of the day. I chose it to **break** the pattern from
colour, indefinites and quantifiers: it has attested inventories (27 languages, 17 families) and a
universal (IFF) that the authors argue efficiency explains.

## The break, and how it closed

The first structural null broke the pattern cleanly. Real modal systems beat random IFF-only
systems of the same size (+0.15 informativeness; dominated by them only 8% of the time). If I had
stopped there, the session would end on "three domains, and a fourth that refutes them".

Then I matched the null on the descriptors I had used for indefinites: coverage and overlap. The
advantage disappeared. Real systems became slightly worse (−0.02), and random IFF systems
dominated them 50% of the time against 25% the other way. Everything measured is captured by IFF +
low overlap + coverage. The caveat belongs in the open: low overlap is itself a route to
informativeness, so this decomposes the efficiency rather than dissolving it.

## Two implementation defects, both found by trying to reproduce one number

I tried to reproduce one number before trusting it, and both defects came out of that.

1. **The complexity is not the paper's complexity.** `num_atoms()` sums `len(child)`, which
   counts nodes, so the published complexities are nodes − 1, not atoms. 28/28 languages match
   that exactly; none match the paper's definition. It favours IFF (non-IFF meanings need nesting).
2. **The prior was applied reversed.** Exactly one of the 720 assignments of Table 5's values to
   the six points reproduces the published informativeness: the reversed one. The shipped corpus
   says Table 5 is right. The magnitude inflation is about a quarter; the direction is unchanged.

Neither defect overturns a conclusion. c1 (all optimal systems are IFF) survives both, on an
exact frontier. I want this on record in this form: the bugs are real and the paper still mostly
stands, and both statements are true at once.

## What it does to the through-line

Four domains now. In all four, the attested systems have no efficiency advantage measured beyond
a few structural descriptors: convexity; no synonymy and coverage; monotone + conservative;
IFF + low overlap + coverage. A first, loose null can make the real systems look special (here,
plainly). The pattern holds only once the null is matched on the descriptors. So the question is
which descriptors to match, and that choice is not innocent. **That is what cidral should
attack.**

Retro-repro: both defects are exactly the kind of record `dev-science-ops/paper-retrospective-reproducibility/`
exists to contribute back. No externally visible action taken; flag it to Leonardo.
