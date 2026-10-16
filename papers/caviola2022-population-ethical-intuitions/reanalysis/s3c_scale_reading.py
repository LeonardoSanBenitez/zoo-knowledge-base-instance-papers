"""Caviola 2022 Study 3c: the 96 who answered that level 0 means 'extremely unhappy' -- scale misreaders (0..100) or
inattentive? Compare their ratings with correct responders (1) and with an inattention reference group
(2 = 'extremely happy', an answer no reading of the scale supports)."""
import pandas as pd, numpy as np
from scipy import stats
d = pd.read_csv('osf/files/osfstorage/Study 3c/PopEthics Study 3c.csv')
d = d[(d.Progress == 100) & (d.Intro_large_size == 36)].copy()
lab = {1: 'correct', 2: 'extremely happy', 3: 'extremely unhappy', 4: 'mildly happy'}
K = ['t_90', 't_70', 't_50k', 't_50m', 't_50b']
for k in K: d['r' + k] = np.where(d.valence == 'happy', d[k], 8 - d[k])
d['loss'] = d.rt_70 - d.rt_50k; d['gain'] = d.rt_50b - d.rt_50k
d['sd_items'] = d[['r' + k for k in K]].std(axis=1); d['straight'] = (d[K].nunique(axis=1) == 1)
g = d.groupby([d.attn_check.map(lab), 'valence'])
print(g[['loss', 'gain', 'sd_items']].mean().round(2).join(g.size().rename('n')).join(g.straight.mean().round(2).rename('straightline')))
print(d.groupby(d.attn_check.map(lab)).duration if False else '')
for v in ('happy', 'unhappy'):
    a = d[(d.attn_check == 1) & (d.valence == v)]; b = d[(d.attn_check == 3) & (d.valence == v)]; c = d[(d.attn_check == 2) & (d.valence == v)]
    for col in ('loss', 'gain'):
        print(f"{v:7s} {col}: correct {a[col].mean():+.2f} vs misread {b[col].mean():+.2f} (MW p {stats.mannwhitneyu(a[col], b[col]).pvalue:.3f}) vs 'extremely happy' {c[col].mean():+.2f} (n {len(c)})")
print('duration median (s) by group:', d.groupby(d.attn_check.map(lab))['Duration (in seconds)'].median().to_dict())
print('valence split of the 96:', d[d.attn_check == 3].valence.value_counts().to_dict(), '| of correct:', d[d.attn_check == 1].valence.value_counts().to_dict())
