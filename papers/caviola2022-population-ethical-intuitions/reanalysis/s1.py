import pandas as pd, numpy as np
from scipy import stats
import os; B=os.environ.get('CAVIOLA_OSF','work/osf/files/osfstorage/')
# --- 1a: port of authors' R exclusions
d=pd.read_csv(B+'Study 1a/PopEthics Sudy 1a.csv')
n0=len(d)
d=d[(d.Progress==100)&(d.participant_id.astype(str).str.len()>5)&(d.attn_check==1)].copy()
d['happy']=d.inter_1.fillna(d.intra_1); d['unh']=d.inter_2.fillna(d.intra_2)
print('1a N',len(d),'excl',n0-len(d))
for c,g in d.groupby('condition'): print(c, round(g.happy.mean(),2), round(g.happy.std(),2), len(g))
print('t vs 50', stats.ttest_1samp(d.happy,50))
print('sum!=100:', ((d.happy+d.unh)!=100).sum())
h=d.happy
def dist(h,label):
    h=h.dropna()
    print(f'--- {label} n={len(h)} mean={h.mean():.2f} median={h.median()} mode={h.mode().tolist()}')
    for lo,hi,name in [(0,49.99,'<50 (happiness weighs MORE)'),(50,51,'50-51 symmetric'),(51.01,99.99,'51<x<100 weighted asym'),(100,100,'100 (no happiness suffices / strict NU-like)')]:
        k=((h>=lo)&(h<=hi)).sum(); print(f'   {name:45s} {k:4d} {k/len(h):.3f}')
    # implied exchange rate r = h/(100-h) (happy needed per unhappy)
    r=h[h<100]/(100-h[h<100])
    print(f'   ratio-of-means implied rate {h.mean()/(100-h.mean()):.2f}; median individual rate {np.median(r):.2f}; geometric mean rate (h<100) {np.exp(np.log(r[r>0]).mean()):.2f}; mean individual rate {r.mean():.2f}')
    vc=h.value_counts().head(10); print('   top values', dict(vc))
dist(d.happy,'1a pooled')
d.to_csv('work/s1a_clean.csv',index=False)
# --- 1b
e=pd.read_csv(B+'Study 1b/PopEthics Study 1b.csv')
print(e[['happiness','unhappiness']].drop_duplicates().head(), len(e))
