"""p05: the paper treats valence as 'randomly missing by design' (p.13). By its own description (p.12) a
valence for an ENDORSED item is missing only for people who endorsed more than 50 of 103 items. So
missingness among endorsed items is a function of total endorsement, not random across people.
Count: people with > 50 endorsed; people with any endorsed item lacking valence; overlap.
Usage: python -I -W ignore p05_valence_missingness.py <rds> <out_dir>
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_rds import load
import numpy as np
d = load(sys.argv[1]); out = sys.argv[2]
items = sorted(c for c in d.columns if re.fullmatch(r'UES_\d{3}', c))
I = np.column_stack([d[c].astype(float).to_numpy() for c in items])
V = np.column_stack([d[c.replace('UES_', 'UESV_')].astype(float).to_numpy() if c.replace('UES_', 'UESV_') in d else np.full(len(d), np.nan) for c in items])
end = I >= 3
n_end = end.sum(1)
miss_end = (end & np.isnan(V)).sum(1)
gt50 = n_end > 50
res = {'people_gt50_endorsed': int(gt50.sum()), 'people_with_missing_valence_on_endorsed': int((miss_end > 0).sum()),
       'of_those_gt50': int(((miss_end > 0) & gt50).sum()),
       'unendorsed_items_with_valence_hypothetical': int((~end & ~np.isnan(V)).sum())}
print(res)
json.dump(res, open(os.path.join(out, 'p05_out.json'), 'w'), indent=1)
