"""Is the 'weak general preference to add a NEUTRAL person' (2a d=0.35; 2b) carried by wrong-sign responders,
and does it exist in a full world at all?"""
import pandas as pd, numpy as np
from scipy import stats
d=pd.read_csv('work/s2a_clean.csv')
ws=(d.jh<4)|(d.ju>4)
for lab,s in [('2a all',d),('2a wrong-sign',d[ws]),('2a consistent',d[~ws])]:
    t=stats.ttest_1samp(s.j_neutral,4); print(lab,len(s),round(s.j_neutral.mean(),3),'d=%.3f'%((s.j_neutral.mean()-4)/s.j_neutral.std()),round(t.statistic,2),round(t.pvalue,4))
ex=(d.j_neutral-4); print('share of excess from wrong-sign group', round(ex[ws].sum()/ex.sum(),3), ' group share of N', round(ws.mean(),3))
e=pd.read_csv('work/s2b_clean.csv')
ws2=((e.valence=='happy')&(e.rating<4))|((e.valence=='unhappy')&(e.rating>4))
for w,g in e.groupby('world'):
    c=g[~(((g.valence=='happy')&(g.rating<4))|((g.valence=='unhappy')&(g.rating>4)))]
    print('2b',w,'all',round(g.neutral.mean(),3),'consistent',round(c.neutral.mean(),3),'p=%.4f'%stats.ttest_1samp(c.neutral,4).pvalue, len(c))
