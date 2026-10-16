# Zaslavsky, Kemp, Regier & Tishby (2018) — colour naming as efficient compression — notes

Author: maria, 2026-10-16. Read in full (author's PDF; SI not retrievable). Released model and
WCS data re-analysed (`reanalysis/run_all.sh`).

**Reproduces:** eps 0.184 bits, beta 1.035, 94% of languages beat all their hue rotations.

**What "near-optimal" is near to.** A ladder of nulls, same number of terms, same scoring:
random assignment of chips 1.93 bits; random convex cells in CIELAB 0.29; real mode maps 0.19;
the bound 0. Convexity, with no language in it, closes ~85% of the way. Languages close ~5
points more and beat most random convex partitions — a real effect, and much smaller than the
phrase suggests. The paper's rotation control cannot see this because rotations are convex.

**The thing I will carry to other efficiency papers:** before reading "languages are near the
optimum", ask what a structurally minimal system scores. `coupe2019` had the same shape (a
compression partly guaranteed by how the quantity is built). Both papers' residual effects
survive; both headlines describe mostly the null.

**Not done, and it matters:** the LI prior is estimated from the same naming data; a
uniform-source curve would test whether the 5-point residual is partly the prior's. And the
convexity point is probably not new in the literature — I have not checked; I must before
saying it anywhere outside this record.

Link rot noted: the paper's WCS URL and the code's hard-coded data URLs (ICSI) time out; the
archive lives at linguistics.berkeley.edu. The model exists only on a personal Dropbox link.
