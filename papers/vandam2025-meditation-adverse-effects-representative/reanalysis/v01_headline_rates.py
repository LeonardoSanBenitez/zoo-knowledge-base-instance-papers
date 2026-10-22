"""v01: recompute the headline incidence rates from the deposited derived columns, and compare with the
counts hard-coded into the authors' proportion tests (Predictors_and_Incidence_8Apr2024.R lines 25-110)
and with the manuscript (14 MAY 2024, pp. 12-14).
Usage: python -I -W ignore v01_headline_rates.py <rds>
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_rds import load
import numpy as np

d = load(sys.argv[1])
n = len(d)
print('n =', n)


def rate(name, mask, script_count, printed):
    k = int(np.nansum(mask))
    print(f'  {name:46s} {k:4d}/{n} = {100 * k / n:6.2f}%   script x = {script_count}   manuscript {printed}')


rate('>=1 unusual experience (ue_tot > 0)', d['ue_tot'] > 0, 856, '96.61%')
rate('>=1 unusual experience (UE_TOTAL > 0)', d['UE_TOTAL'] > 0, 856, '96.61%')
rate('IME adverse effect (iue.yn)', d['iue.yn'] == 1, 517, '58.35% (mild)')
rate('IME adverse effect (AE_Def1_YN)', d['AE_Def1_YN'] == 1, 517, '58.35%')
rate('any MRAES item (mraes.number > 0)', d['mraes.number'] > 0, 694, '78.33%')
rate('any MRAES item (AE_Def2_YN)', d['AE_Def2_YN'] == 1, 694, '78.33%')
rate('generic AE item (AE_Def3_YN)', d['AE_Def3_YN'] == 1, 278, '31.38%')
rate('functional impairment (Impairment == 1)', d['Impairment'] == 1, 81, '9.14%')
rate('impairment > 1 day', d['ImpairDurGtOneDay'] == 1, 34, '3.84%')
print('  Impairment asked of', int(d['Impairment'].notna().sum()), 'participants (missing', int(d['Impairment'].isna().sum()), ')')
for c in ('Group', 'order', 'framing', 'Val_Instr', 'ValUnselected'):
    print(' ', c, d[c].value_counts(dropna=False).to_dict() if d[c].nunique() < 8 else d[c].nunique())
