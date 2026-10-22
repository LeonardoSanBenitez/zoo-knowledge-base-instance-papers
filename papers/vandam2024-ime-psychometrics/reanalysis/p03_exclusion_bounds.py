"""p03: what could removing 159 'multivariate outliers' have done to the incidence figures?
The 159 are not deposited. Bounds: (i) none of them had the outcome, (ii) all had it, (iii) they resembled
the people the rule flags in a no-outlier copula (p02: high endorsers) -- proxied by the outcome rate among
the RETAINED respondents whom the same rule flags again (p02 A) -- and by the rate in the top endorsement decile.
Usage: python -I -W ignore p03_exclusion_bounds.py <rds> <out_dir>
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_rds import load
import numpy as np
from scipy import stats

d = load(sys.argv[1]); out = sys.argv[2]
items = sorted(c for c in d.columns if re.fullmatch(r'UES_\d{3}', c))
X = np.column_stack([d[c].astype(float).to_numpy() for c in items])
okr = ~np.isnan(X).any(1)
mu = X[okr].mean(0); Si = np.linalg.pinv(np.cov(X[okr], rowvar=False))
D = np.full(len(d), np.nan)
C = X[okr] - mu; D[okr] = np.einsum('ij,jk,ik->i', C, Si, C)
flag = D > stats.chi2.ppf(0.999, X.shape[1])
endorse = (X >= 3).sum(1)
top = endorse >= np.nanquantile(endorse, 0.9)
OUT = {'ime_ae': d['iue.yn'] == 1, 'generic_ae': d['AE_Def3_YN'] == 1, 'any_mraes': d['AE_Def2_YN'] == 1}
n, k = len(d), 159
res = {}
for name, y in OUT.items():
    y = y.to_numpy(); x = int(y.sum())
    r_flag, r_top = float(y[flag].mean()), float(y[top].mean())
    b = {'published': x / n, 'none_of_159': x / (n + k), 'all_of_159': (x + k) / (n + k),
         'like_reflagged': (x + r_flag * k) / (n + k), 'like_top_decile': (x + r_top * k) / (n + k),
         'rate_in_reflagged': r_flag, 'rate_in_top_decile': r_top}
    res[name] = b
    print(f'{name:11s} published {100 * b["published"]:.1f}% | bounds {100 * b["none_of_159"]:.1f}-{100 * b["all_of_159"]:.1f}% | '
          f'if the 159 resembled re-flagged retained ({100 * r_flag:.0f}% have it): {100 * b["like_reflagged"]:.1f}% | '
          f'top decile ({100 * r_top:.0f}%): {100 * b["like_top_decile"]:.1f}%')
json.dump(res, open(os.path.join(out, 'p03_out.json'), 'w'), indent=1)
