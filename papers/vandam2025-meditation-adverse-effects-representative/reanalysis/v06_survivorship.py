"""v06: is the fall of LIFETIME adverse-effect incidence with practice (v04 B) a survivorship signature?
A lifetime incidence cannot fall with exposure within a fixed population. It can fall across people if
those who were harmed practise less afterwards (stop, or never accumulate hours), or if long-ago events
are forgotten. The survey asks the not-in-the-past-12-months group why they stopped
(MED.Stop: [1] 'I had a bad experience during or as a result of meditation').
Tests: (1) how many stopped because of a bad experience; (2) AE rates, current vs lapsed;
(3) the hours/years gradient among CURRENT meditators only; (4) the gradient with distress held fixed.
Usage: python -I -W ignore v06_survivorship.py <rds> <out_dir>
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_rds import load
import numpy as np
import statsmodels.formula.api as smf

d = load(sys.argv[1]); out = sys.argv[2]
d = d.assign(any_ime=(d['iue.yn'] == 1).astype(int), generic=(d['AE_Def3_YN'] == 1).astype(int),
             any_mraes=(d['AE_Def2_YN'] == 1).astype(int), lh=np.log10(d['med.hrs'].astype(float)),
             yrs=d['med.years'].astype(float), k10=d['K10_TOTAL'].astype(float),
             psy=d['Psychoticism'].astype(float), current=(d['MED.Screener'].astype(float) == 1).astype(int))
res = {}
lapsed = d[d['current'] == 0]
print(f'current (meditated in past 12 months): {int(d.current.sum())}; lapsed: {len(lapsed)}')
stop = lapsed['MED.Stop'].astype(float).value_counts(dropna=False).sort_index().to_dict()
print('  reason for stopping (1 = bad experience, 2 = no time/space/energy, 3 = not helping, 4 = other, 5 = could not practise properly):', stop)
res['n_current'] = int(d.current.sum()); res['n_lapsed'] = len(lapsed); res['stop_reasons'] = {str(k): int(v) for k, v in stop.items()}
for y in ('any_ime', 'generic', 'any_mraes'):
    r = d.groupby('current')[y].mean().round(3).to_dict()
    res[f'{y}_by_current'] = r
    print(f'  {y:10s} lapsed {r.get(0)}  current {r.get(1)}')
cur = d[d.current == 1]
print('\nAmong current meditators only:')
for y in ('any_ime', 'generic', 'any_mraes'):
    m1 = smf.logit(f'{y} ~ lh', cur).fit(disp=0)
    m2 = smf.logit(f'{y} ~ yrs', cur).fit(disp=0)
    m3 = smf.logit(f'{y} ~ lh + yrs + k10 + psy', cur).fit(disp=0)
    print(f'  {y:10s} log10 hours {m1.params["lh"]:+.3f} (p {m1.pvalues["lh"]:.3g}); years {m2.params["yrs"]:+.4f} '
          f'(p {m2.pvalues["yrs"]:.3g}); with K10 + psychoticism: hours {m3.params["lh"]:+.3f} (p {m3.pvalues["lh"]:.3g}), '
          f'years {m3.params["yrs"]:+.4f} (p {m3.pvalues["yrs"]:.3g})')
    res[f'{y}_current_gradient'] = {'lh': [float(m1.params['lh']), float(m1.pvalues['lh'])],
                                    'yrs': [float(m2.params['yrs']), float(m2.pvalues['yrs'])],
                                    'adjusted_lh': [float(m3.params['lh']), float(m3.pvalues['lh'])],
                                    'adjusted_yrs': [float(m3.params['yrs']), float(m3.pvalues['yrs'])]}
# distress is higher in less experienced? (an alternative to survivorship: the novices are the distressed)
for v in ('k10', 'psy'):
    rho = d[[v, 'lh']].corr(method='spearman').iloc[0, 1]
    print(f'  Spearman({v}, log hours) = {rho:+.3f}')
    res[f'rho_{v}_loghours'] = float(rho)
json.dump(res, open(os.path.join(out, 'v06_out.json'), 'w'), indent=1)
