"""v04: (A) the randomised questionnaire order (ORD vs RAND item order) x framing (UE block first vs AE
block first) factors -- analysed in the authors' script (lines 611-631), not reported in the 14 MAY 2024
manuscript. Does the incidence depend on how the questionnaire was put together?
(B) incidence by lifetime meditation hours and years: is there an early rise and a plateau, as in
schlosser2019 (flat across years) and goldberg2022 (step between 0-10 and 11-100 h)?
(C) the retreat association, raw and adjusted for dose and distress.
Usage: python -I -W ignore v04_framing_and_dose.py <rds> <out_dir>
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_rds import load
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

d = load(sys.argv[1]); out = sys.argv[2]
d = d.assign(any_ime=(d['iue.yn'] == 1).astype(int), any_mraes=(d['AE_Def2_YN'] == 1).astype(int),
             generic=(d['AE_Def3_YN'] == 1).astype(int), impair=(d['Impairment'] == 1).astype(int),
             ue_n=d['ue_tot'].astype(float), ae_n=d['iue.number'].astype(float),
             hrs=d['med.hrs'].astype(float), yrs=d['med.years'].astype(float),
             retreat=d['RETREAT_YN'].astype(float), k10=d['K10_TOTAL'].astype(float),
             psy=d['Psychoticism'].astype(float), order=d['order'].astype(str), framing=d['framing'].astype(str))
res = {}
print('(A) order x framing (randomised between participants)')
tab = d.groupby(['order', 'framing'])[['any_ime', 'any_mraes', 'generic', 'ue_n', 'ae_n']].mean()
tab['n'] = d.groupby(['order', 'framing']).size()
print(tab.round(3).to_string())
for y in ('any_ime', 'any_mraes', 'generic'):
    full = smf.logit(f'{y} ~ C(order) * C(framing)', d).fit(disp=0)
    main = smf.logit(f'{y} ~ C(order) + C(framing)', d).fit(disp=0)
    no_fr = smf.logit(f'{y} ~ C(order)', d).fit(disp=0)
    no_or = smf.logit(f'{y} ~ C(framing)', d).fit(disp=0)
    lr_int = 2 * (full.llf - main.llf); lr_fr = 2 * (main.llf - no_fr.llf); lr_or = 2 * (main.llf - no_or.llf)
    r = {k: float(stats.chi2.sf(v, 1)) for k, v in (('p_interaction', lr_int), ('p_framing', lr_fr), ('p_order', lr_or))}
    fr = d.groupby('framing')[y].mean(); orr = d.groupby('order')[y].mean()
    r.update(framing_rates=fr.round(4).to_dict(), order_rates=orr.round(4).to_dict())
    res[y] = r
    print(f'  {y:10s} framing {fr.round(3).to_dict()} p={r["p_framing"]:.3g} | order {orr.round(3).to_dict()} '
          f'p={r["p_order"]:.3g} | interaction p={r["p_interaction"]:.3g}')
for y in ('ue_n', 'ae_n'):
    m = smf.ols(f'{y} ~ C(order) * C(framing)', d).fit()
    print(f'  {y:10s} OLS: ' + ', '.join(f'{k} {v:+.2f} (p {m.pvalues[k]:.3g})' for k, v in m.params.items() if k != 'Intercept'))
    res[y] = {k: [float(v), float(m.pvalues[k])] for k, v in m.params.items()}

print('\n(B) incidence by lifetime hours (bins of goldberg2022 + the paper\'s)')
bins = [0, 10, 100, 250, 500, 1000, np.inf]
lab = ['0-10', '11-100', '101-250', '251-500', '501-1000', '>1000']
d['hbin'] = pd.cut(d['hrs'], bins=bins, labels=lab, right=True)
g = d.groupby('hbin', observed=False)[['any_ime', 'any_mraes', 'generic', 'retreat']].mean()
g['n'] = d.groupby('hbin', observed=False).size()
print(g.round(3).to_string())
res['by_hours'] = {k: {c: (None if pd.isna(v) else float(v)) for c, v in row.items()} for k, row in g.iterrows()}
d['ybin'] = pd.cut(d['yrs'], bins=[0, 1, 2, 5, 10, 20, np.inf], labels=['<=1', '1-2', '2-5', '5-10', '10-20', '>20'])
gy = d.groupby('ybin', observed=False)[['any_ime', 'any_mraes', 'generic']].mean(); gy['n'] = d.groupby('ybin', observed=False).size()
print(gy.round(3).to_string())
res['by_years'] = {k: {c: float(v) for c, v in row.items()} for k, row in gy.iterrows()}
d['lh'] = np.log10(d['hrs'])
for y in ('any_ime', 'any_mraes', 'generic'):
    lin = smf.logit(f'{y} ~ lh', d).fit(disp=0)
    quad = smf.logit(f'{y} ~ lh + I(lh**2)', d).fit(disp=0)
    print(f'  {y:10s} logit on log10(hours): slope {lin.params["lh"]:+.3f} (p {lin.pvalues["lh"]:.3g}); '
          f'quadratic term {quad.params["I(lh ** 2)"]:+.3f} (p {quad.pvalues["I(lh ** 2)"]:.3g})')
    res[f'{y}_loghours'] = [float(lin.params['lh']), float(lin.pvalues['lh']), float(quad.params['I(lh ** 2)']),
                            float(quad.pvalues['I(lh ** 2)'])]

print('\n(C) retreat association')
for y in ('any_ime', 'any_mraes', 'generic', 'impair'):
    dd = d if y != 'impair' else d[d['Impairment'].notna()]
    raw = smf.logit(f'{y} ~ retreat', dd).fit(disp=0)
    adj = smf.logit(f'{y} ~ retreat + lh + yrs + k10 + psy', dd).fit(disp=0)
    print(f'  {y:10s} n={len(dd)}  OR raw {np.exp(raw.params["retreat"]):.2f} (p {raw.pvalues["retreat"]:.3g})   '
          f'adjusted for log hours, years, K10, psychoticism {np.exp(adj.params["retreat"]):.2f} (p {adj.pvalues["retreat"]:.3g})')
    res[f'retreat_{y}'] = [float(np.exp(raw.params['retreat'])), float(raw.pvalues['retreat']),
                           float(np.exp(adj.params['retreat'])), float(adj.pvalues['retreat'])]
json.dump(res, open(os.path.join(out, 'v04_out.json'), 'w'), indent=1, default=str)
