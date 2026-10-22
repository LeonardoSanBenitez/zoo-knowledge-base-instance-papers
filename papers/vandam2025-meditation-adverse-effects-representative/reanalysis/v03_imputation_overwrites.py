"""v03: does the 'multiple imputation' column change valence values that were actually observed?
Imputation should only fill missing cells. For every UESV_xxx (as answered) vs UESV_xxx_MI and
_MI_Final, count cells where the answer exists and the imputed column differs, over all 103/105 items
and over the IME-30 endorsed cells that the 58.35% headline rests on.
Usage: python -I -W ignore v03_imputation_overwrites.py <rds> <out_dir>
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_rds import load
import numpy as np

d = load(sys.argv[1]); out = sys.argv[2]
items = sorted({m.group(1) for c in d.columns for m in [re.match(r'^UESV_(\d{3})_MI$', c)] if m})
res = {'items': len(items)}
tot_obs = tot_diff = tot_diff_f = 0
flip_unpleasant = 0        # observed <= 3 (unpleasant) turned into >= 4, or the reverse
by_item = []
for it in items:
    raw = d[f'UESV_{it}'].astype(float).to_numpy()
    mi = d[f'UESV_{it}_MI'].astype(float).to_numpy()
    mf = d[f'UESV_{it}_MI_Final'].astype(float).to_numpy()
    o = ~np.isnan(raw)
    diff = o & (mi != raw); diff_f = o & (mf != raw)
    tot_obs += o.sum(); tot_diff += diff.sum(); tot_diff_f += diff_f.sum()
    flip_unpleasant += (o & ((raw <= 3) != (mi <= 3))).sum()
    by_item.append((it, int(o.sum()), int(diff.sum()), int(np.isnan(raw).sum())))
res.update(observed_cells=int(tot_obs), observed_cells_changed_by_MI=int(tot_diff),
           observed_cells_changed_by_MI_Final=int(tot_diff_f), observed_cells_unpleasant_status_flipped_by_MI=int(flip_unpleasant))
print(f'{len(items)} items. Observed valence cells: {tot_obs}. Changed by _MI: {tot_diff} '
      f'({100 * tot_diff / tot_obs:.2f}%); by _MI_Final: {tot_diff_f} ({100 * tot_diff_f / tot_obs:.2f}%).')
print(f'Observed cells whose unpleasant/not-unpleasant status (code <= 3) the _MI column flips: {flip_unpleasant}')
missing_total = sum(b[3] for b in by_item)
print(f'Missing (not asked) valence cells in total: {missing_total}')
by_item.sort(key=lambda b: -b[2])
print('items with most observed cells changed (item, observed, changed, missing):', by_item[:8])
# Is the change a recode (e.g. a systematic shift) or noise? Cross-tab on all observed cells.
pairs = {}
for it in items:
    raw = d[f'UESV_{it}'].astype(float).to_numpy(); mi = d[f'UESV_{it}_MI'].astype(float).to_numpy()
    o = ~np.isnan(raw) & (mi != raw)
    for a, b in zip(raw[o], mi[o]):
        pairs[(int(a), int(b))] = pairs.get((int(a), int(b)), 0) + 1
top = sorted(pairs.items(), key=lambda kv: -kv[1])[:12]
print('most frequent (observed -> MI) changes:', top)
res['top_changes'] = [[list(k), v] for k, v in top]
json.dump(res, open(os.path.join(out, 'v03_out.json'), 'w'), indent=1)
