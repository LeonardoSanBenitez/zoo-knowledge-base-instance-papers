"""Xu, Liu & Regier (2020): exact-restricted systems (k exact terms + one residual 'higher' term) look near-optimal.
Analytic check: under the paper's need p(t) ~ t^-2.02 on 1..100, where do PREFIX systems {1..k}+residual rank among all
placements of k exact singleton terms (residual = everything else)? Two residual-listener models: Bayesian (L(t) prop. to need
within the residual set) and uniform over the residual set. Cost = sum_t N(t) * log2(1/L_w(t)); exact terms cost 0."""
import itertools, math, numpy as np
T = np.arange(1, 101); N = 0.6182 * T ** -2.02; N = N / N.sum()
def cost(exact, listener):
    mask = np.ones(100, bool); mask[[e - 1 for e in exact]] = False
    R = N[mask]
    if listener == 'bayes': L = R / R.sum()
    else: L = np.full(R.size, 1 / R.size)
    return float((R * np.log2(1 / L)).sum())
for listener in ('bayes', 'uniform'):
    for k in (2, 3, 4, 6):
        pref = cost(range(1, k + 1), listener)
        if k <= 3:
            allc = np.array([cost(c, listener) for c in itertools.combinations(range(1, 101), k)])
            rank = int((allc < pref - 1e-12).sum()); tot = len(allc)
            print(f'{listener:7s} k={k}: prefix cost {pref:.3f} bits | placements with lower cost: {rank}/{tot} | min {allc.min():.3f} median {np.median(allc):.3f}')
        else:
            rng = np.random.default_rng(0); samp = np.array([cost(rng.choice(np.arange(1, 101), k, replace=False), listener) for _ in range(20000)])
            print(f'{listener:7s} k={k}: prefix cost {pref:.3f} bits | random placements with lower cost: {(samp < pref - 1e-12).mean():.4f} of 20,000 | median {np.median(samp):.3f}')
print('need mass of 1..3:', round(float(N[:3].sum()), 3), '| of 1..6:', round(float(N[:6].sum()), 3))
