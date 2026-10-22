"""v05: H1b ('generic AE rate not different from Goldberg et al.'s 32.3%, 140/434') re-run per framing arm,
with the authors' own test (R prop.test with continuity correction = 2x2 chi-square with Yates).
Also: the Table 3 entry 'experience (hrs) 0.171** (0.171)' -- the z and p implied by its own beta and SE.
Usage: python -I -W ignore v05_h1b_by_arm.py <rds> <out_dir>
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_rds import load
from scipy import stats
import numpy as np

d = load(sys.argv[1]); out = sys.argv[2]
g = (d['AE_Def3_YN'] == 1)
res = {}


def prop_test(x1, n1, x2, n2):
    chi2, p, _, _ = stats.chi2_contingency([[x1, n1 - x1], [x2, n2 - x2]], correction=True)
    return chi2, p


x, n = int(g.sum()), len(d)
chi2, p = prop_test(x, n, 140, 434)
print(f'pooled (as published): {x}/{n} = {100 * x / n:.2f}% vs 32.26%: chi2 {chi2:.2f}, p {p:.3f}  (paper: 0.07, 0.795)')
res['pooled'] = [x, n, chi2, p]
for arm in ('AEUE', 'UEAE'):
    m = d['framing'].astype(str) == arm
    x, n = int(g[m].sum()), int(m.sum())
    chi2, p = prop_test(x, n, 140, 434)
    print(f'framing {arm} ({"AE block first" if arm == "AEUE" else "UE block first"}): {x}/{n} = {100 * x / n:.2f}% '
          f'vs 32.26%: chi2 {chi2:.2f}, p {p:.4f}')
    res[arm] = [x, n, chi2, p]
b, se = 0.171, 0.171
z = b / se
print(f'Table 3 experience (hrs) on #UEs: beta {b} SE {se} -> z {z:.2f}, two-sided p {2 * stats.norm.sf(z):.2f}; printed "**" (p < .01)')
res['table3_experience'] = [b, se, z, 2 * stats.norm.sf(z)]
json.dump(res, open(os.path.join(out, 'v05_out.json'), 'w'), indent=1)
