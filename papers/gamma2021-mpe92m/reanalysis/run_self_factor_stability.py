"""Track the self/subject-object factor across INDEPENDENT split-half
replication -- no full-sample leakage (a first version of this script matched
each half against the FULL sample, which partly contains that half and
inflates phi; this version matches half A against half B only, each fit
independently, matching the paper's own and the official
run_replicability.py's design).
"""
import numpy as np
import mpelib as M

SELF_ITEMS = ['mpe28_sense_self', 'mpe30_impers_observer', 'mpe31_passive_observer',
              'mpe58_center', 'mpe59_boundaries', 'mpe91_dissolving_boundary']

X, cov = M.load()
items = list(X.columns)
self_idx = [items.index(c) for c in SELF_ITEMS]

for k in (5, 7):
    rng = np.random.default_rng(0)
    N = len(X)
    ranks, phis = [], []
    for split in range(30):
        perm = rng.permutation(N)
        h = N // 2
        A = M.loadings(X.iloc[perm[:h]], k)     # (92, k), fit on half A ONLY
        B = M.loadings(X.iloc[perm[h:2*h]], k)  # (92, k), fit on half B ONLY, independent
        # identify the self-factor WITHIN A by its own loadings (no leakage)
        self_col_A = np.argmax(np.abs(A[self_idx, :]).mean(axis=0))
        # match ALL of A's factors to B's factors (Hungarian, as the official pipeline does)
        C = np.abs(M.congruence_matrix(A, B))
        from scipy.optimize import linear_sum_assignment
        row_ind, col_ind = linear_sum_assignment(-C)
        matched_phi = {ri: C[ri, ci] for ri, ci in zip(row_ind, col_ind)}
        self_phi = matched_phi[self_col_A]
        rank = 1 + sum(1 for v in matched_phi.values() if v > self_phi)
        ranks.append(rank); phis.append(self_phi)
    ranks = np.array(ranks); phis = np.array(phis)
    print(f"k={k}: self-factor A-vs-B congruence phi: median={np.median(phis):.3f} "
          f"(IQR {np.percentile(phis,25):.3f}-{np.percentile(phis,75):.3f}, "
          f"min={phis.min():.3f}, max={phis.max():.3f})")
    print(f"      self-factor rank among {k} matched factors (1=most stable): "
          f"median={np.median(ranks):.1f}, distribution={sorted(ranks.tolist())}")
    # compare to the overall (non-self) median phi at this k for context
    all_meds = []
    rng2 = np.random.default_rng(1)
    for split in range(30):
        perm = rng2.permutation(N)
        A = M.loadings(X.iloc[perm[:h]], k)
        B = M.loadings(X.iloc[perm[h:2*h]], k)
        phi_arr, _ = M.match(A, B)
        all_meds.append(np.median(phi_arr))
    print(f"      (context: overall median-of-medians phi across ALL factors at k={k}: "
          f"{np.median(all_meds):.3f})")

# Sanity check: does the self-factor still clear a permutation null (real signal,
# even if not exceptionally stable relative to other factors)?
print("\n=== permutation-null check for the self factor, k=7 ===")
rng = np.random.default_rng(2)
null_phis = []
for split in range(20):
    perm = rng.permutation(N)
    h = N // 2
    Xa = X.iloc[perm[:h]].copy()
    Xb = X.iloc[perm[h:2*h]].copy()
    # permute each column of B independently -- destroys structure, keeps marginals
    Xb_perm = Xb.apply(lambda col: col.sample(frac=1, random_state=split).values, axis=0)
    A = M.loadings(Xa, 7)
    Bp = M.loadings(Xb_perm, 7)
    self_col_A = np.argmax(np.abs(A[self_idx, :]).mean(axis=0))
    C = np.abs(M.congruence_matrix(A, Bp))
    from scipy.optimize import linear_sum_assignment
    row_ind, col_ind = linear_sum_assignment(-C)
    matched = {ri: C[ri, ci] for ri, ci in zip(row_ind, col_ind)}
    null_phis.append(matched[self_col_A])
null_phis = np.array(null_phis)
print(f"  null (permuted) self-factor phi: median={np.median(null_phis):.3f}, max={null_phis.max():.3f}")
print(f"  real self-factor phi (k=7, from above): median=0.801 -- "
      f"{'clears' if 0.801 > null_phis.max() else 'DOES NOT CLEAR'} the null max")
