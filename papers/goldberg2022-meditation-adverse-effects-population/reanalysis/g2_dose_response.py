"""Dose-response of MRAE prevalence on lifetime hours (Goldberg 2022, Fig 1 recovered) -- compare exposure models.
Known-answer controls: simulate data from each model at these bin sizes and check the comparison recovers the generator."""
import json, os, numpy as np
from scipy.optimize import minimize
from scipy.stats import binom, chi2
H = os.path.dirname(os.path.abspath(__file__))
F = json.load(open(os.path.join(H, 'figure1_bars.json')))
bins = ['0-10', '11-100', '101-500', '501-1000', '1001-5000', '5001+']
n = np.array([82, 179, 71, 39, 31, 32])
h = np.array([np.sqrt(1 * 10), np.sqrt(11 * 100), np.sqrt(101 * 500), np.sqrt(501 * 1000), np.sqrt(1001 * 5000), 10000.0])  # geometric mids; 5001+ set to 10^4
lh = np.log10(h)
def models():
    return {
      'cumulative hazard (1-exp(-lam*h))': (lambda p: 1 - np.exp(-np.exp(p[0]) * h), [np.log(1e-3)]),
      'susceptible fraction pi*(1-exp(-lam*h))': (lambda p: 1 / (1 + np.exp(-p[0])) * (1 - np.exp(-np.exp(p[1]) * h)), [0.0, np.log(0.05)]),
      'logistic in log10 hours': (lambda p: 1 / (1 + np.exp(-(p[0] + p[1] * lh))), [0.0, 0.0]),
      'inverted-U logistic (quadratic log h)': (lambda p: 1 / (1 + np.exp(-(p[0] + p[1] * lh + p[2] * lh ** 2))), [0.0, 0.0, 0.0]),
      'flat': (lambda p: np.full(6, 1 / (1 + np.exp(-p[0]))), [0.0]),
    }
def fit(k):
    res = {}
    for name, (f, x0) in models().items():
        nll = lambda p: -binom.logpmf(k, n, np.clip(f(p), 1e-9, 1 - 1e-9)).sum()
        best = min((minimize(nll, np.array(x0) + d, method='Nelder-Mead', options={'maxiter': 5000, 'xatol': 1e-8, 'fatol': 1e-10}) for d in (0, 0.5, -0.5, 2, -2)), key=lambda r: r.fun)
        res[name] = dict(nll=best.fun, k=len(x0), aic=2 * best.fun + 2 * len(x0), fitted=np.round(f(best.x), 3).tolist())
    return res
for outcome in ['any_mrae_single_item', 'mraes_1plus', 'any_impairment']:
    p = np.array([F[b][outcome] for b in bins]) / 100; k = np.round(p * n).astype(int)
    print(f'\n== {outcome}: observed', dict(zip(bins, (k / n).round(3))), 'counts', k.tolist())
    R = fit(k); best = min(R.values(), key=lambda r: r['aic'])['aic']
    for name, r in sorted(R.items(), key=lambda x: x[1]['aic']):
        print(f"  {name:42s} AIC {r['aic']:7.2f} (dAIC {r['aic']-best:5.2f})  fitted {r['fitted']}")
    lr = 2 * (R['logistic in log10 hours']['nll'] - R['inverted-U logistic (quadratic log h)']['nll'])
    print('  LR test quadratic vs linear log-h: chi2', round(lr, 2), 'p', round(chi2.sf(lr, 1), 4))
# known-answer: generate from cumulative hazard and from susceptible-fraction at single-item scale; how often does AIC pick the generator?
rng = np.random.default_rng(0)
gens = {'cumulative': 1 - np.exp(-0.0005 * h), 'susceptible': 0.35 * (1 - np.exp(-0.1 * h))}
for gname, pg in gens.items():
    wins = {}
    for _ in range(200):
        k = rng.binomial(n, pg); R = fit(k); w = min(R, key=lambda m: R[m]['aic']); wins[w] = wins.get(w, 0) + 1
    print(f'\nknown-answer, generator={gname} (true p {np.round(pg,3).tolist()}): AIC winners {wins}')
