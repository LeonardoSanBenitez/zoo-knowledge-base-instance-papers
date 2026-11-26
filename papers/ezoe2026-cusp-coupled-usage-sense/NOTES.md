# ezoe2026-cusp-coupled-usage-sense — notes (maria, 2026-11-27)

Author: maria

## What the paper does
CUSP: per-period Gaussian mixtures over usage embeddings, coupled across periods by a Markov-composed transport, with displacement operators that split change into movement of component centres vs reorganisation within components, attribute it to component pairs, and ground it in passages. Theory for the Gaussian case; experiments on synthetic data, DWUG EN/DE, Janus six-period histories, and 60 legal lemmas in US court opinions.

## What I checked
- DWUG (c1): their own claim is modest and holds; but no period-blind control. On the same sets/encoder a period-blind dispersion score is already .74/.80 (goworek reanalysis). Not separable.
- Janus (c2): stable path length 1e-17 = identical fits across periods. With 10 sentences per pool and 10 usages per pool per stable period, the stable panels are presumably the same set each period. Then AUROC 1.000 is by construction, and the benchmark has none of the within-period sampling noise that dominates real ~20-40-use gold (arena-lsc F37). Inference, flagged as such.
- Code: repository 404 on 2026-11-27 (artifact dangling).

## For arena-lsc
Not a system lead (no code, GMMs per period at 20 uses in 1024 dims are badly underdetermined). Useful for the paper's related work as the one timing-oriented multi-period method of 2026, and as an example of a synthetic multi-period test whose no-change condition apparently has no sampling noise.
