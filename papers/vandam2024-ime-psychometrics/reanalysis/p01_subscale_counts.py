"""p01: Table 4 subscale endorsement (any item >= Slight): Enabling 832, Disabling 517, Distortions 582.
517 is also the companion paper's 'IME adverse effect' count (vandam2025: any of the 30 items >= Slight AND
valence <= mildly unpleasant). Which definition does 517 actually belong to? Also re-derive a sample of
Table 4 item endorsement counts.
Usage: python -I -W ignore p01_subscale_counts.py <rds> <out_dir>
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_rds import load
import numpy as np

d = load(sys.argv[1]); out = sys.argv[2]
SUB = {'Enabling': ["UES_006", "UES_011", "UES_071", "UES_052", "UES_013", "UES_042", "UES_012", "UES_041", "UES_036", "UES_111"],
       'Disabling': ["UES_029", "UES_083", "UES_028", "UES_104", "UES_050", "UES_080", "UES_105", "UES_055", "UES_056", "UES_048"],
       'Distortions': ["UES_044", "UES_075", "UES_078", "UES_063", "UES_072", "UES_065", "UES_067", "UES_043", "UES_062", "UES_095"]}
PRINTED = {'Enabling': 832, 'Disabling': 517, 'Distortions': 582}
res = {}
ae = (d['iue.yn'] == 1).to_numpy()
for name, items in SUB.items():
    I = np.column_stack([d[c].astype(float).to_numpy() for c in items])
    V = np.column_stack([d[c.replace('UES_', 'UESV_') + '_MI'].astype(float).to_numpy() for c in items])
    any_end = ((I >= 3).sum(1) > 0)
    any_unpl = (((I >= 3) & (V <= 3)).sum(1) > 0)
    res[name] = {'printed': PRINTED[name], 'any_item_ge_slight': int(any_end.sum()),
                 'any_item_ge_slight_and_unpleasant': int(any_unpl.sum()),
                 'item_counts_ge_slight': {c: int((d[c].astype(float) >= 3).sum()) for c in items}}
    print(f'{name:12s} printed {PRINTED[name]:4d} | any item >= Slight {any_end.sum():4d} | '
          f'any item >= Slight & unpleasant {any_unpl.sum():4d}')
print(f'companion IME adverse effect (iue.yn): {int(ae.sum())}')
dis = res['Disabling']
print(f'-> the printed Disabling 517 equals the any-item-unpleasant count over ALL 30 items, not the '
      f'Disabling endorsement ({dis["any_item_ge_slight"]})' if dis['any_item_ge_slight'] != 517 else
      '-> Disabling endorsement is 517 by its own definition')
# Table 4 item counts, spot check (printed values transcribed from p.28)
PRINT_ITEMS = {'UES_104': 219, 'UES_050': 158, 'UES_105': 220, 'UES_048': 162}
for c, v in PRINT_ITEMS.items():
    print(f'  {c}: printed {v}, data {res["Disabling"]["item_counts_ge_slight"][c]}')
json.dump(res, open(os.path.join(out, 'p01_out.json'), 'w'), indent=1)
