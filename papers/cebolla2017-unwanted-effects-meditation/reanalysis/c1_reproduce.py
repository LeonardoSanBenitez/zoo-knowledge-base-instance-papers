"""c1 -- Cebolla et al. 2017 (PLOS ONE 12:e0183137) against their own Zenodo deposit 838669 (ue.sav, md5 cf6d1f6b...).
Reproduce Table 2 (frequency of each practice type), the Kruskal-Wallis tests of UE x frequency, Table 4 (checklist),
and test the abstract's practice-type claims with denominators. Author: maria 2026-10-17."""
import sys, pyreadstat, numpy as np, pandas as pd
from scipy import stats
df, meta = pyreadstat.read_sav(sys.argv[1] if len(sys.argv) > 1 else 'ue.sav')
ue = (df.q0016 == 1).astype(int)
print(f"UE yes {ue.sum()}/{len(df)} = {ue.mean():.3%}")
types = {'FA': 'q0011_0001_0002', 'OM': 'q0011_0002_0002', 'I': 'q0011_0003_0002', 'BA': 'q0011_0004_0002', 'C': 'q0011_0005_0002', 'IP': 'q0011_0006_0002'}
print("value labels:", meta.variable_value_labels['q0011_0001_0002'])
print("\nTABLE 2 reproduction (counts per frequency code) and KW of frequency by UE")
pk = []
for k, c in types.items():
    vc = df[c].value_counts().sort_index().to_dict()
    g1, g0 = df.loc[ue == 1, c], df.loc[ue == 0, c]
    h, p = stats.kruskal(g1, g0)
    # practitioners: any frequency other than 'never' -- find the 'never' code from labels
    lab = meta.variable_value_labels[c]; never = [v for v, l in lab.items() if l.lower().startswith('nunca')]
    prac = ~df[c].isin(never)
    r1, r0 = ue[prac].mean(), ue[~prac].mean()
    pk.append(p)
    print(f"  {k:<3} counts {vc} | KW H = {h:.3f} p = {p:.4f} | mean code UE {g1.mean():.2f} vs no-UE {g0.mean():.2f} | UE rate practitioners {r1:.3f} (n={prac.sum()}) vs never {r0:.3f} (n={(~prac).sum()})")
print(f"  Holm over 6 KW tests: smallest p {min(pk):.4f} vs Holm threshold {0.05/6:.4f}")
items = [c for c in df.columns if c.startswith(('q0031', 'q0033', 'q0035', 'q0037', 'q0039', 'q0041', 'q0043', 'q0045'))]
print("\nTABLE 4 reproduction (codes 1..11 = scores 0..10): mean (SD), % max, % min")
for c in items:
    x = df[c].dropna() - 1
    print(f"  {meta.column_names_to_labels[c][:55]:<55} {x.mean():.1f} ({x.std():.1f})  max {np.mean(x == 10):.1%}  min {np.mean(x == 0):.1%}  n={len(x)}")
