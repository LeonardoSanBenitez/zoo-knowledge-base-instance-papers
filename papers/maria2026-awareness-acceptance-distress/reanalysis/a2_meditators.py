"""a2 -- PLAN_ireland.md: does curiosity (awareness-like) without decentering (equanimity-like) go with more distress,
in 955 meditators? Known-answer check first (synthetic, same marginals), then the real fit. Author: maria 2026-10-17."""
import sys, numpy as np, pandas as pd, statsmodels.formula.api as smf
d0 = pd.read_csv(sys.argv[1] if len(sys.argv) > 1 else 'sem.csv')
d = pd.DataFrame({'cur': d0[['cur_p1', 'cur_p2']].mean(axis=1, skipna=False), 'dec': d0[['dec_p1', 'dec_p2', 'dec_p3']].mean(axis=1, skipna=False),
                  'maas': d0[['maas_p1', 'maas_p2', 'maas_p3']].mean(axis=1, skipna=False), 'dass': d0[['dass_dep', 'dass_anx', 'dass_str']].sum(axis=1, min_count=3)}).dropna()
z = lambda x: (x - x.mean()) / x.std()
d['zc'], d['zd'], d['zm'] = z(d.cur), z(d.dec), z(d.maas); d['ldass'] = np.log1p(d.dass)
def fit(df, y='dass', a='zc'):
    m = smf.ols(f'{y} ~ {a} * zd', df).fit(cov_type='HC3'); return m
rng = np.random.default_rng(5)
print("KNOWN-ANSWER (synthetic, real predictors, outcome generated with a planted interaction):")
for b in (-3.0, 0.0):
    est = []
    for _ in range(200):
        s = d.copy(); s['dass'] = 25 - 2 * s.zc - 6 * s.zd + b * s.zc * s.zd + rng.normal(0, 15, len(s))
        est.append(fit(s).params['zc:zd'])
    print(f"  planted {b:+.1f}: recovered mean {np.mean(est):+.2f} (SD {np.std(est):.2f})")
print(f"\nREAL DATA n = {len(d)} (complete cases)")
print("correlations:\n", d[['cur', 'dec', 'maas', 'dass']].corr().round(3))
for y in ('dass', 'ldass'):
    for a in ('zc', 'zm'):
        m = fit(d, y, a); b, p = m.params[f'{a}:zd'], m.pvalues[f'{a}:zd']
        lo = m.params[a] - m.params[f'{a}:zd']; hi = m.params[a] + m.params[f'{a}:zd']
        print(f"  {y:<6} ~ {a} * zd: {a} {m.params[a]:+.3f} (p {m.pvalues[a]:.3g}) | zd {m.params['zd']:+.3f} (p {m.pvalues['zd']:.3g}) | "
              f"interaction {b:+.3f} (p {p:.3f}) | simple slope of {a}: dec -1SD {lo:+.3f}, +1SD {hi:+.3f}")

print("\nEXPLORATORY (not in the plan): does curiosity's partial association survive MAAS? and per DASS subscale")
m = smf.ols('dass ~ zc + zd + zm', d).fit(cov_type='HC3'); print(f"  dass ~ zc + zd + zm: zc {m.params.zc:+.3f} (p {m.pvalues.zc:.3g}), zd {m.params.zd:+.3f}, zm {m.params.zm:+.3f}")
for sub in ('dass_dep', 'dass_anx', 'dass_str'):
    s = d.join(d0[[sub]]).dropna(); mm = smf.ols(f'{sub} ~ zc * zd', s).fit(cov_type='HC3')
    print(f"  {sub}: zc {mm.params.zc:+.3f} (p {mm.pvalues.zc:.3g}), interaction {mm.params['zc:zd']:+.3f} (p {mm.pvalues['zc:zd']:.3f})")
