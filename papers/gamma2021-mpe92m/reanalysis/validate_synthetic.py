"""BREAK-TEST FIRST. Validate the split-half congruence instrument on data
whose factor structure I control, before pointing it at the MPE-92M.

Three cases, chosen so that a failure is visible rather than plausible:

  A. TRUE-5: 92 items generated from exactly 5 orthogonal factors + noise.
     If the instrument works: extracting k=5 gives phi high for all 5;
     extracting k=10 gives 5 high and 5 collapsing, because factors 6-10 have
     nothing to be stable about.
  B. NOISE: 92 independent items, no factor structure at all. Every extracted
     factor must fall to the congruence FLOOR. This is what calibrates
     "low" -- the conventional .85 threshold is borrowed from a literature that
     did not use half-splits of n~700, so I need my own floor.
  C. GENERAL+SPECIFIC: one strong general factor plus 4 weak specifics -- the
     shape the MPE data actually has (first eigenvalue 17.9). This is the case
     where Tucker phi is known to be inflated, because all loadings share sign.
     If C's *noise* factors sit far above B's floor, then the floor is
     structure-dependent and B alone is not a valid null for the real data.

Run: python validate_synthetic.py
"""
import numpy as np
import pandas as pd
import mpelib as M

rng = np.random.default_rng(11)
P, N = 92, 1403


def synth(loadmat, n=N, noise_scale=None):
    """Generate n observations of P items from a P x k loading matrix."""
    k = loadmat.shape[1]
    F = rng.standard_normal((n, k))
    comm = (loadmat ** 2).sum(1)
    if noise_scale is None:
        noise_scale = np.sqrt(np.maximum(1 - comm, 0.05))
    Xv = F @ loadmat.T + rng.standard_normal((n, P)) * noise_scale
    return pd.DataFrame(Xv, columns=[f'v{i:02d}' for i in range(P)])


def report(name, arr, k):
    med = np.median(arr, axis=0)
    lo = np.percentile(arr, 5, axis=0)
    print(f"\n[{name}] k={k}, {arr.shape[0]} splits -- matched Tucker phi "
          f"(median [5th pct]), factors sorted by phi:")
    print("  " + "  ".join(f"{m:.2f}[{l:.2f}]" for m, l in zip(med, lo)))
    n_equal = int((med >= M.THRESH_EQUAL).sum())
    n_fair = int((med >= M.THRESH_FAIR).sum())
    print(f"  factors with median phi >= .95: {n_equal}   >= .85: {n_fair}")
    return med


# ---- A. TRUE-5 -------------------------------------------------------------
L5 = np.zeros((P, 5))
for j in range(5):                       # ~18 items per factor, loading .6-.8
    L5[j * 18:(j + 1) * 18, j] = rng.uniform(0.6, 0.8, 18)
Xa = synth(L5)
print("=" * 72)
print("CASE A -- true 5-factor structure, 92 items, N=1403")
for k in (3, 5, 8, 12):
    report("TRUE-5", M.split_half_congruence(Xa, k, n_splits=20, seed=1), k)

# ---- B. PURE NOISE (the floor) --------------------------------------------
Xb = pd.DataFrame(rng.standard_normal((N, P)),
                  columns=[f'v{i:02d}' for i in range(P)])
print("\n" + "=" * 72)
print("CASE B -- pure noise, no factor structure. This defines the FLOOR.")
floors = {}
for k in (3, 5, 8, 12, 18):
    floors[k] = report("NOISE", M.split_half_congruence(Xb, k, n_splits=20, seed=2), k)

# ---- C. GENERAL + SPECIFIC -------------------------------------------------
Lc = np.zeros((P, 5))
Lc[:, 0] = rng.uniform(0.45, 0.65, P)            # general factor, all items
for j in range(1, 5):
    Lc[(j - 1) * 23:j * 23, j] = rng.uniform(0.35, 0.5, 23)
Xc = synth(Lc)
print("\n" + "=" * 72)
print("CASE C -- 1 general + 4 weak specifics (the shape MPE-92M has)")
for k in (5, 8, 12):
    report("GEN+SPEC", M.split_half_congruence(Xc, k, n_splits=20, seed=3), k)

print("\n" + "=" * 72)
print("VERDICT to check by eye:")
print(" A: k=5 all high; at k=12 exactly ~5 stay high and the rest fall.")
print(" B: everything at the floor at every k. If any noise factor reaches .85,")
print("    the .85 threshold is meaningless here and must be replaced by B's floor.")
print(" C: the general factor near 1.0; spurious factors ABOVE B's floor would")
print("    mean the floor is structure-dependent -> use C-style null for real data.")
