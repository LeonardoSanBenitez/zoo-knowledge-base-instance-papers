"""v02: rebuild ue_tot and iue.number (the IME-30 unusual-experience count and adverse-effect count) from
the item-level columns, find which valence source and threshold the deposited columns used, and bound
the headline 58.35% by what imputation contributed.

IME-30 items: trans30 + psy30 + self30 from the authors' psychometrics script (osf.io/76ud3,
IUE_EFA_CFA_DFA.R lines 343-345). Intensity UES_xxx: 1 No, 2 So slight cannot decide, 3 Slight,
4 Moderate, 5 Strong, 6 Extreme. Valence UESV_xxx (as answered), UESV_xxx_MI and UESV_xxx_MI_Final
(random-forest multiple imputation): 1 Extremely, 2 Modestly, 3 Mildly unpleasant, 4 Neutral, 5-7 pleasant.
Valence was asked for at most 50 randomly selected items per person (manuscript p.10).
Usage: python -I -W ignore v02_reconstruct_ime.py <rds> <out_dir>
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_rds import load
import numpy as np

d = load(sys.argv[1]); out = sys.argv[2]
TRANS = ["UES_006", "UES_011", "UES_071", "UES_052", "UES_013", "UES_042", "UES_012", "UES_041", "UES_036", "UES_111"]
PSY = ["UES_029", "UES_083", "UES_028", "UES_104", "UES_050", "UES_080", "UES_105", "UES_055", "UES_056", "UES_048"]
SELF = ["UES_044", "UES_075", "UES_078", "UES_063", "UES_072", "UES_065", "UES_067", "UES_043", "UES_062", "UES_095"]
ITEMS = TRANS + PSY + SELF
n = len(d)
I = np.column_stack([d[c].astype(float).to_numpy() for c in ITEMS])            # intensity
V = {src: np.column_stack([d[c.replace('UES_', 'UESV_') + suf].astype(float).to_numpy() for c in ITEMS])
     for src, suf in (('raw', ''), ('MI', '_MI'), ('MI_Final', '_MI_Final'))}
res = {}

endorsed = I >= 3
ue_tot = endorsed.sum(1)
res['ue_tot_match'] = int((ue_tot == d['ue_tot'].to_numpy()).sum())
res['ue_any'] = int((ue_tot > 0).sum())
print(f'ue_tot rebuilt (intensity >= Slight over 30 items): equals deposit in {res["ue_tot_match"]}/{n}; '
      f'>=1 endorsed: {res["ue_any"]} (manuscript 856, deposit ue_tot>0 861)')
for thr in (3, 4):          # intensity thresholds tried for the 856
    print(f'   variant: intensity >= {thr}: any = {int(((I >= thr).sum(1) > 0).sum())}')

raw = V['raw']
print('valence asked (non-missing) for endorsed IME items:', int((~np.isnan(raw) & endorsed).sum()), 'of',
      int(endorsed.sum()), 'endorsed item-responses')
best = None
for src, M in V.items():
    for vthr in (2, 3):
        cnt = (endorsed & (M <= vthr)).sum(1)
        m = int((cnt == d['iue.number'].to_numpy()).sum())
        print(f'  iue.number from {src:8s} valence <= {vthr}: matches deposit in {m}/{n}; any = {int((cnt > 0).sum())}')
        if best is None or m > best[0]:
            best = (m, src, vthr)
res['iue_definition'] = {'valence_source': best[1], 'valence_max_code': best[2], 'rows_matching': best[0]}
src, vthr = best[1], best[2]

obs = ~np.isnan(raw)
lower = (endorsed & obs & (raw <= vthr)).sum(1) > 0                   # missing valence -> not unpleasant
upper = (endorsed & (np.isnan(raw) | (raw <= vthr))).sum(1) > 0        # missing valence -> unpleasant
imp = (endorsed & (V[src] <= vthr)).sum(1) > 0
res.update(ae_lower=int(lower.sum()), ae_imputed=int(imp.sum()), ae_upper=int(upper.sum()))
print(f'\nIME adverse effect (>= Slight and valence <= {vthr}):')
print(f'  observed valence only (missing = not unpleasant): {lower.sum()}/{n} = {100 * lower.mean():.1f}%')
print(f'  with the imputed valence used in the paper:       {imp.sum()}/{n} = {100 * imp.mean():.1f}%')
print(f'  missing valence counted as unpleasant:            {upper.sum()}/{n} = {100 * upper.mean():.1f}%')
miss_end = (endorsed & ~obs).sum(1)
print(f'  endorsed items with no valence asked, per person: mean {miss_end.mean():.2f}, '
      f'people with >= 1 such item {(miss_end > 0).sum()}')
# share of AE cases that rest only on imputed valences
only_imp = imp & ~lower
res['ae_cases_resting_only_on_imputation'] = int(only_imp.sum())
print(f'  AE cases that rest ONLY on imputed valences: {only_imp.sum()} of {imp.sum()} '
      f'({100 * only_imp.sum() / imp.sum():.1f}%)')
# the other threshold (Methods text says 'modestly unpleasant or greater' = code <= 2)
for t in (2, 3):
    k = int(((endorsed & (V[src] <= t)).sum(1) > 0).sum())
    res[f'ae_imputed_valence_le_{t}'] = k
    print(f'  imputed valence, threshold code <= {t} ({"modestly" if t == 2 else "mildly"} unpleasant or worse): '
          f'{k}/{n} = {100 * k / n:.1f}%')
json.dump(res, open(os.path.join(out, 'v02_out.json'), 'w'), indent=1)
