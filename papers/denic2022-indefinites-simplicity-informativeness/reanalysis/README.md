# Reanalysis: Denic, Steinert-Threlkeld & Szymanik (2022)

Author: maria, 2026-10-16. Python 3 + numpy + scipy. R is not needed: the R pipeline's
measures are re-implemented in `core.py` (cost, pragmatic cost, complexity lookup) and
`mdl.py` (exact shortest-formula complexity by DP closure).

    git clone https://github.com/milicaden/indefinite-pronouns-simplicity-informativeness repo
    git -C repo checkout 1e5c5cc78e2eb5bbc7c28ff828dca4abc260c663
    export DENIC_REPO=$PWD/repo            # or clone into reanalysis/repo

| script | what it does | result |
|---|---|---|
| r1_reproduce.py | cost/complexity/RSA cost for all 519 Exp-1 languages vs authors' CSV; matching diagnostics | max abs diff 0 / 5e-15 / 5e-15; matched artificial have 1.82 items vs natural 3.27 |
| r2_distances.py | refit frontier a/(b+cost), distances, Welch t | t(82.8) = -16.0, M 0.48 vs 1.55 (paper: same) |
| mdl.py (inline check) | DP minimal description vs authors' 63-item tables (2-op and 3-op) | 0 mismatches each |
| r3_exact_frontier.py | Pareto frontier by enumeration (all <=4-item languages, all 876 partial partitions, partitions + 1 item) | cost 1.00 at complexity 11; GA frontier 1.21 |
| r4_nulls.py | natural vs matched artificial vs overlap-free random languages, GA and exact frontiers | exact-frontier distance: natural 0.72, overlap-free 0.83, random-items 1.88 |
| r5_permute.py | 720 flavour relabelings of the 40 natural languages | 5/720 better on distance; 8/720 on complexity; 160/720 on cost |
| r6_exp2.py, r7_exp2_matched.py | Exp 2 decomposition; flavour-count-matched swap control | advantage survives: complexity t=-44.7, cost t=-13.8, RSA cost t=-5.9 |
| r8_family.py | family-weighted permutation (14 families, IE 22/40) | 9/720 |
| r9_known_answer.py | paper's Exp-1 test applied to random overlap-free languages | rejects at p<.001 in 100% of 1000 draws |
| r10_four_settings.py | all of the above across the paper's 4 settings | natural vs overlap-free p = .33/.21/.60/.46 |
