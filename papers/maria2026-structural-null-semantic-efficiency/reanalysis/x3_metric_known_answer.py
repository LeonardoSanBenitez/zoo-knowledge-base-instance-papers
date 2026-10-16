"""Known-answer behaviour of net Pareto dominance.
(a) 'natural' drawn from the null itself -> expected 0, at any spread and axis correlation.
(b) fixed true improvement (delta on both axes, in units of the null SD) -> how the metric depends on null spread
    and on the correlation between complexity and informativeness inside the null (a trade-off makes dominance rare)."""
import numpy as np
rng = np.random.default_rng(0)
def net(pt, X):
    c, a = pt; dom = np.mean((c <= X[:, 0]) & (a >= X[:, 1]) & ((c < X[:, 0]) | (a > X[:, 1])))
    sub = np.mean((X[:, 0] <= c) & (X[:, 1] >= a) & ((X[:, 0] < c) | (X[:, 1] > a))); return dom - sub
def null(n, sd, rho):
    cov = sd ** 2 * np.array([[1, rho], [rho, 1]]); return rng.multivariate_normal([0, 0], cov, n)
print('(a) natural ~ null: mean net over 400 languages (should be ~0)')
for rho in (-0.8, 0, 0.8):
    for sd in (0.5, 1, 3):
        v = [net(null(1, sd, rho)[0], null(300, sd, rho)) for _ in range(400)]
        print(f'   rho {rho:+.1f} sd {sd}: {np.mean(v):+.3f}')
print('(b) natural = null centre shifted by delta*sd toward better (lower complexity, higher informativeness)')
for rho in (0.8, 0, -0.8):  # in (complexity, informativeness) a TRADE-OFF is a POSITIVE correlation (more complex, more informative)
    row = []
    for d in (0.25, 0.5, 1.0):
        v = [net((-d * 1.0, d * 1.0), null(300, 1.0, rho)) for _ in range(200)]
        row.append(f'delta {d}: {np.mean(v):+.3f}')
    print(f'   rho {rho:+.1f} (sd 1):', ' | '.join(row))
print('   scale check: same delta in raw units, null sd 0.5 vs 2 (rho 0.8)')
for sd in (0.5, 2.0):
    v = [net((-0.5, 0.5), null(300, sd, 0.8)) for _ in range(200)]; print(f'     sd {sd}: {np.mean(v):+.3f}')
