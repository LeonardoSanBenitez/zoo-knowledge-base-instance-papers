# periti2024-multi-period-dwsi — notes (maria, 2026-11-03)

A map, not a result. Useful vocabulary for SemEval-2027 Task 3 design choices: (1) clustering over consecutive
intervals (re-cluster t_i with t_{i-1} and again with t_{i+1}; breaks faithfulness), (2) per-period clustering +
alignment, (3) one-time clustering over all periods, (4) incremental clustering, (5) form-based monitoring to choose
where to cluster. And three assessment settings: consecutive, pairwise, cumulative.

The Task 3 scorer fixes the answer for a participant: ONE label space over all periods (BCubed over a word's usages)
and JSD between consecutive periods of that labelling. Option (3) is the only one that produces that without an
alignment step; (4) would have to be flattened into a global labelling afterwards. The authors' preference for
incremental clustering is argued, not measured, so it is a hypothesis to test on the synthetic 10-period set
(saponara2026), not a recommendation to follow.
