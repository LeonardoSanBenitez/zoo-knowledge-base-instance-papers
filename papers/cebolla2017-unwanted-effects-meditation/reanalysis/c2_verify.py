"""c2 -- verify the two discrepancies found by c1 before believing them.
(a) Direction of the body-awareness effect: UE rate by each BA frequency category (code 1 = daily ... 6 = never), and
    Spearman of frequency code with UE. (b) Table 4: are the printed means the raw SPSS codes (1..11) rather than the
    labelled scores (0..10)? Compare printed means with raw-code means, item by item. Author: maria 2026-10-17."""
import sys, pyreadstat, numpy as np, pandas as pd
from scipy import stats
df, meta = pyreadstat.read_sav(sys.argv[1] if len(sys.argv) > 1 else 'ue.sav')
ue = (df.q0016 == 1).astype(int); c = 'q0011_0004_0002'
t = pd.crosstab(df[c], ue, margins=True); t['UE rate'] = t[1] / t['All']
t.index = [meta.variable_value_labels[c].get(i, i) for i in t.index]
print("(a) BODY AWARENESS: UE rate by frequency\n", t.round(3))
rho, p = stats.spearmanr(df[c], ue); print(f"Spearman(frequency code, UE) = {rho:.3f}, p = {p:.4f}  (negative = more frequent practice goes with MORE UE)")
print("    label check: does code 1 really mean daily?", meta.variable_value_labels[c][1.0])
printed = [3.3, 3.7, 2.7, 2.5, 2, 3.1, 2, 2.4, 2, 2.7, 2.1, 2.6, 2.4, 3, 2.2, 2.4, 2.1, 2.5, 1.8, 2.8, 3.3, 2.8]
printed_sd = [3, 3.2, 2.8, 2.7, 2.3, 3.1, 2.3, 2.6, 2.2, 2.7, 2.1, 2.4, 2.4, 2.8, 2.2, 2.5, 2.2, 2.6, 1.7, 2.9, 2.9, 2.8]
items = [c for c in df.columns if c.startswith(('q0031', 'q0033', 'q0035', 'q0037', 'q0039', 'q0041', 'q0043', 'q0045'))]
raw = np.array([df[i].mean() for i in items]); lab = raw - 1
sd = np.array([df[i].std() for i in items])
print("\n(b) TABLE 4: printed mean vs labelled-score mean (code-1) vs raw-code mean")
exact_raw = sum(abs(round(r, 1) - p) < 0.051 for r, p in zip(raw, printed)); exact_lab = sum(abs(round(l, 1) - p) < 0.051 for l, p in zip(lab, printed))
for i, (it, p, l, r, s, ps) in enumerate(zip(items, printed, lab, raw, sd, printed_sd)):
    print(f"  {i+1:2d} printed {p:3.1f} | score {l:4.2f} | raw code {r:4.2f} | SD data {s:4.2f} printed {ps}")
print(f"  printed mean matches raw-code mean (to 0.05) in {exact_raw}/22 items; matches labelled score in {exact_lab}/22")

# (b2) the paper says the checklist 'was completed by 276 participants'. Try complete cases.
cc = df[items].dropna()
rawc = cc.mean().values; sdc = cc.std().values
m = sum(abs(round(r, 1) - p) < 0.051 for r, p in zip(rawc, printed)); ms = sum(abs(round(s, 1) - p) < 0.051 for s, p in zip(sdc, printed_sd))
print(f"\n(b2) complete cases n = {len(cc)}: printed mean = raw-code mean in {m}/22; printed SD = data SD in {ms}/22")
print("     largest |printed - raw| (complete cases):", round(max(abs(np.round(rawc, 1) - printed)), 2))
d_raw = np.round(raw, 2) - np.array(printed); d_lab = np.round(lab, 2) - np.array(printed)
print(f"(b3) available-case: |printed - raw code| max {abs(d_raw).max():.2f}, mean {abs(d_raw).mean():.3f}; |printed - score| min {abs(d_lab).min():.2f}, mean {abs(d_lab).mean():.3f}")
