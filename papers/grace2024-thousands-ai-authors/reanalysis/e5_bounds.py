"""Partial identification of the pooled forecast's upper quantiles. Each respondent's fitted gamma CDF is used only up to
their information horizon h_i (fixed-years: the longest horizon asked; fixed-probabilities: the year they gave for 90%);
beyond h_i their CDF is only known to lie in [F_i(h_i), 1]. Pooling the lower and upper envelopes bounds the pooled CDF,
and therefore the pooled 50% and 90% years, without trusting any extrapolated tail."""
import os, sys, glob, numpy as np, pandas as pd
from scipy import stats, optimize
T = sys.argv[1] if len(sys.argv) > 1 else 'hlmi'
YRS = ['10', '20', '40'] if T == 'hlmi' else ['10', '20', '50']
D = os.environ.get('ESPAI_DATA', 'work/osf/files/osfstorage/')
d = pd.read_csv(glob.glob(D + '*.csv')[0], low_memory=False)
num = lambda c: pd.to_numeric(d[c], errors='coerce')
P = np.array([.1, .5, .9])
fp = pd.DataFrame({k: num(f'{T}_{k}percent_clean') for k in ['10', '50', '90']}).dropna()
fy = pd.DataFrame({k: num(f'{T}_{k}years_clean') for k in YRS}).dropna()
def fit(x, p):
    x = np.asarray(x, float); p = np.clip(np.asarray(p, float), 1e-4, 1 - 1e-4)
    res = lambda th: stats.gamma.cdf(x, np.exp(th[0]), scale=np.exp(th[1])) - p
    best = None
    for k0, s0 in ((1, 20), (3, 10), (0.5, 60), (2, np.median(x))):
        try: r = optimize.least_squares(res, np.log([k0, max(s0, 0.5)]), bounds=([-6, -6], [6, 14]))
        except Exception: continue
        if best is None or r.cost < best.cost: best = r
    return np.exp(best.x)
ok = []
for _, r in fp.iterrows():
    if (r.values <= 0).any() or not (r['10'] <= r['50'] <= r['90']): continue
    ok.append((fit(r.values, P), float(r['90']), 'fp'))
for _, r in fy.iterrows():
    pr = r.values / 100
    if not (pr[0] <= pr[1] <= pr[2]): continue
    ok.append((fit([int(y) for y in YRS], pr), float(YRS[-1]), 'fy'))
grid = np.concatenate([np.linspace(0.01, 400, 8000), np.geomspace(400.01, 1e6, 2000)])
def env(sel):
    lo = np.zeros_like(grid); hi = np.zeros_like(grid); pt = np.zeros_like(grid); n = 0
    for th, h, f in ok:
        if not sel(f): continue
        F = stats.gamma.cdf(grid, th[0], scale=th[1]); Fh = stats.gamma.cdf(h, th[0], scale=th[1])
        beyond = grid > h
        lo += np.where(beyond, Fh, F); hi += np.where(beyond, 1.0, F); pt += F; n += 1
    return lo / n, hi / n, pt / n, n
def q(c, a):
    i = np.searchsorted(c, a); return None if i >= len(grid) else 2023 + grid[i]
for lab, sel in [('ALL', lambda f: True), ('fixed-probabilities', lambda f: f == 'fp'), ('fixed-years', lambda f: f == 'fy')]:
    lo, hi, pt, n = env(sel)
    fmt = lambda v: 'never (unidentified)' if v is None else f'{v:.0f}'
    print(f'{T.upper()} {lab:20s} n={n:4d} | 50%: point {fmt(q(pt,.5))}, identified interval [{fmt(q(hi,.5))}, {fmt(q(lo,.5))}] | 90%: point {fmt(q(pt,.9))}, interval [{fmt(q(hi,.9))}, {fmt(q(lo,.9))}] | max identified pooled prob {lo[-1]:.3f}')
