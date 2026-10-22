"""Score P1-P3 of PLAN.md on artifacts/segments.csv.  Usage: python -I score.py <segments.csv> <out_json>"""
import csv, json, site, sys
sys.path.append(site.getusersitepackages())
import numpy as np
from scipy import stats

rows = list(csv.DictReader(open(sys.argv[1], encoding='utf-8')))
res = {}
for nik in ('DN', 'MN'):
    print(nik)
    for n in ('R4', 'R8', 'R12', 'R8_shuffled'):
        v = {L: np.array([float(r[n]) for r in rows if r['nikaya'] == nik and r['layer'] == L])
             for L in ('mula', 'atthakatha', 'tika')}
        mw = stats.mannwhitneyu(v['mula'], v['atthakatha'], alternative='greater')
        res[f'{nik}|{n}'] = {L: [float(x.mean()), float(x.std(ddof=1)), len(x)] for L, x in v.items()}
        res[f'{nik}|{n}']['p_mula_gt_att'] = float(mw.pvalue)
        order = v['mula'].mean() > v['atthakatha'].mean() > v['tika'].mean()
        print(f'  {n:12s} mula {v["mula"].mean():.3f} (sd {v["mula"].std(ddof=1):.3f})  atthakatha {v["atthakatha"].mean():.3f}  '
              f'tika {v["tika"].mean():.3f}   mula>att p={mw.pvalue:.2g}   full order m>a>t: {order}')
p1 = all(res[f'{k}|R8']['mula'][0] > res[f'{k}|R8']['atthakatha'][0] > res[f'{k}|R8']['tika'][0]
         and res[f'{k}|R8']['p_mula_gt_att'] < 0.01 for k in ('DN', 'MN'))
p2 = all(res[f'{k}|{n}']['mula'][0] > res[f'{k}|{n}']['atthakatha'][0] for k in ('DN', 'MN') for n in ('R4', 'R12'))
p3_fail = any(res[f'{k}|R8']['atthakatha'][0] >= res[f'{k}|R8']['mula'][0] for k in ('DN', 'MN'))
print(f'P1 {p1}   P2 {p2}   P3 risk realised (att >= mula somewhere): {p3_fail}')
res.update(P1=p1, P2=p2, P3_risk_realised=p3_fail)
json.dump(res, open(sys.argv[2], 'w'), indent=1)
