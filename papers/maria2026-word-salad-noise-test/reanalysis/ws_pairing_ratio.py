"""Empirical paired/independent variance ratio for a same-question accuracy contrast.
Used to calibrate n* bounds in mazuryk2026-powerless-noise/reanalysis/07 and wu2026 w3_nstar.py.
ratio = Var_paired(d) / [p0(1-p0) + p1(1-p1)], per-item. Author: maria 2026-10-17."""
import json, sys
for f in sys.argv[1:]:
    R = [json.loads(l) for l in open(f, encoding='utf-8')]
    for a, b in (('C0', 'C1'), ('C0', 'C2'), ('C1', 'C2')):
        x = [r[a]['ok'] for r in R]; y = [r[b]['ok'] for r in R]; n = len(R)
        p0 = sum(x) / n; p1 = sum(y) / n
        d = [int(v) - int(u) for u, v in zip(x, y)]; m = sum(d) / n
        vp = sum((t - m) ** 2 for t in d) / n; vi = p0 * (1 - p0) + p1 * (1 - p1)
        print(f"{f.split('/')[-1]:<32} {b}-{a} n={n} p0={p0:.3f} p1={p1:.3f} Var_paired={vp:.4f} Var_indep={vi:.4f} ratio={vp/vi:.3f} corr={1-vp/vi:.3f}")
