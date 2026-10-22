"""Score the pre-registered predictions P1-P5 (reanalysis/PLAN.md) on dlm.py's per-sentence output.
Usage: python -I analyse.py <dlm_rows.csv> <out_json>
"""
import csv, json, math, site, sys
sys.path.append(site.getusersitepackages())
import numpy as np
import statsmodels.api as sm
from scipy import stats

rows = list(csv.DictReader(open(sys.argv[1], encoding='utf-8')))
out = {}
TB = sorted({r['treebank'] for r in rows})
HEAD_FINAL = ['UD_Japanese-GSD', 'UD_Korean-GSD', 'UD_Turkish-IMST', 'UD_Telugu-MTG']
HEAD_INITIAL = ['UD_Italian-ISDT', 'UD_Indonesian-GSD', 'UD_Irish-IDT']


def arr(tb, scheme, col, lo=1, hi=99):
    return np.array([float(r[col]) for r in rows if r['treebank'] == tb and r['scheme'] == scheme
                     and lo <= int(r['length']) <= hi])


def slope_test(tb, scheme, base):
    L = arr(tb, scheme, 'length', 2); d = arr(tb, scheme, 'obs', 2) - arr(tb, scheme, base, 2)
    X = sm.add_constant(L ** 2)
    m = sm.OLS(d, X).fit(cov_type='HC3')
    b, se = m.params[1], m.bse[1]
    return float(b), float(se), float(stats.norm.cdf(b / se)), len(d)   # one-sided p for slope < 0


print('P1 / P2: slope of (observed - baseline) on length^2, HC3, one-sided p(slope < 0)')
res = {}
for tb in TB:
    for scheme in ('content', 'function'):
        for base in ('free_mean', 'fixed_mean'):
            res[(tb, scheme, base)] = slope_test(tb, scheme, base)
    f, x = res[(tb, 'content', 'free_mean')], res[(tb, 'content', 'fixed_mean')]
    print(f'  {tb:26s} n={f[3]:6d}  FREE slope {f[0]:+.4f} p={f[2]:.1e} | FIXED slope {x[0]:+.4f} p={x[2]:.1e}')
p1 = sum(res[(tb, 'content', 'free_mean')][2] < 1e-3 and res[(tb, 'content', 'free_mean')][0] < 0 for tb in TB)
p2 = sum(res[(tb, 'content', 'fixed_mean')][2] < 1e-2 and res[(tb, 'content', 'fixed_mean')][0] < 0 for tb in TB)
print(f'P1 (FREE, p < .001, 12/12 predicted): {p1}/{len(TB)}')
print(f'P2 (FIXED, p < .01, >= 11/12 predicted): {p2}/{len(TB)}')
out['P1'] = p1; out['P2'] = p2
out['slopes'] = {f'{k[0]}|{k[1]}|{k[2]}': v for k, v in res.items()}

print('\nP3: short sentences, mean (observed - FREE) and two-sided t-test, content-head')
p3_nonneg, p3_sigpos = 0, []
out['short'] = {}
for tb in TB:
    line, nonneg = [], False
    for n in (3, 4, 5):
        d = arr(tb, 'content', 'obs', n, n) - arr(tb, 'content', 'free_mean', n, n)
        if len(d) < 5:
            line.append(f'{n}: n<5'); continue
        t = stats.ttest_1samp(d, 0.0)
        line.append(f'{n}: {d.mean():+.3f} (n={len(d)}, p={t.pvalue:.2g})')
        out['short'][f'{tb}|{n}'] = [float(d.mean()), len(d), float(t.pvalue)]
        if d.mean() >= 0:
            nonneg = True
        if n in (3, 4) and d.mean() > 0 and t.pvalue < 0.05:
            p3_sigpos.append(f'{tb}@{n}')
    p3_nonneg += nonneg
    print(f'  {tb:26s} ' + '   '.join(line))
print(f'P3: treebanks with mean d >= 0 at some length 3-5: {p3_nonneg}/{len(TB)} (predicted >= half); '
      f'significant positive at 3 or 4: {p3_sigpos or "none"} (predicted >= 1)')
out['P3_nonneg'] = p3_nonneg; out['P3_sigpos'] = p3_sigpos

print('\nP4: obs/FREE ratio at length 18-22, content vs function head')
p4_sign = p4_size = 0
out['ratio20'] = {}
for tb in TB:
    r = {}
    for scheme in ('content', 'function'):
        o = arr(tb, scheme, 'obs', 18, 22); fr = arr(tb, scheme, 'free_mean', 18, 22)
        r[scheme] = float(o.mean() / fr.mean()) if len(o) else float('nan')
    sc, sf = res[(tb, 'content', 'free_mean')][0], res[(tb, 'function', 'free_mean')][0]
    p4_sign += (sc < 0) == (sf < 0)
    big = abs(r['content'] - r['function']) > 0.05
    p4_size += big
    out['ratio20'][tb] = r
    print(f'  {tb:26s} content {r["content"]:.3f}  function {r["function"]:.3f}  diff {r["function"] - r["content"]:+.3f}'
          f'{"  <-- > 0.05" if big else ""}')
print(f'P4: same slope sign {p4_sign}/{len(TB)} (predicted 12/12); |ratio diff| > 0.05 in {p4_size} (predicted >= 4)')
out['P4_sign'] = p4_sign; out['P4_size'] = p4_size

print('\nP5: obs/FREE ratio at length 15-25, content-head')
rat = {}
for tb in TB:
    o = arr(tb, 'content', 'obs', 15, 25); fr = arr(tb, 'content', 'free_mean', 15, 25)
    rat[tb] = float(o.mean() / fr.mean()) if len(o) else float('nan')
for tb in sorted(rat, key=rat.get):
    tag = 'head-final' if tb in HEAD_FINAL else 'head-initial' if tb in HEAD_INITIAL else ''
    print(f'  {tb:26s} {rat[tb]:.3f} {tag}')
hf = [rat[t] for t in HEAD_FINAL if not math.isnan(rat[t])]; hi = [rat[t] for t in HEAD_INITIAL]
p5 = min(hf) > max(hi)
print(f'P5 (all head-final above all head-initial): {p5}; head-final min {min(hf):.3f}, head-initial max {max(hi):.3f}')
out['P5'] = bool(p5); out['ratio15_25'] = rat
json.dump(out, open(sys.argv[2], 'w'), indent=1)
