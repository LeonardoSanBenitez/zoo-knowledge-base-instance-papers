import pandas as pd, numpy as np
from scipy import stats
import os; B=os.environ.get('CAVIOLA_OSF','work/osf/files/osfstorage/')
d=pd.read_csv(B+'Study 2a/PopEthics Study 2a.csv'); n0=len(d)
d=d[(d.Progress==100)&(d.assumpt1==1)&(d.assumpt2==1)].copy()
d['jh']=np.where(d.valence=='happy',d.j_main,d.j_t2); d['ju']=np.where(d.valence=='happy',d.j_t2,d.j_main)
print('2a N',len(d),'excl',n0-len(d)); print('happy',d.jh.mean().round(2),d.jh.std().round(2),'unhappy',d.ju.mean().round(2),d.ju.std().round(2),'neutral',d.j_neutral.mean().round(2))
gh=d.jh-4; gu=4-d.ju   # magnitude of goodness / badness
print('paired t (|bad| - good):',stats.ttest_rel(gu,gh))
asym=gu-gh
print('individual asymmetry (badness - goodness) distribution:'); print(asym.value_counts().sort_index().to_dict())
print(f'  share symmetric {(asym==0).mean():.3f}; suffering-heavier {(asym>0).mean():.3f}; happiness-heavier {(asym<0).mean():.3f}')
print('happy rating dist',d.jh.value_counts().sort_index().to_dict()); print('unhappy rating dist',d.ju.value_counts().sort_index().to_dict())
print('ceiling: happy=7',(d.jh==7).mean().round(3),' unhappy=1',(d.ju==1).mean().round(3))
# wrong-direction answers: happy person makes world worse / unhappy person better
print('happy<4',(d.jh<4).sum(),' unhappy>4',(d.ju>4).sum(), ' both-wrong-sign', ((d.jh<4)&(d.ju>4)).sum())
print('neutral dist',d.j_neutral.value_counts().sort_index().to_dict())
# order effect on asymmetry
print(d.groupby('order').apply(lambda g: ((4-g.ju)-(g.jh-4)).mean()))
d.to_csv('work/s2a_clean.csv',index=False)
# 2b
e=pd.read_csv(B+'Study 2b/PopEthics Study 2b.csv'); n0=len(e)
e=e[(e.Progress==100)&(e.assumpt1==1)&(e.assumpt2==1)&(e.attn_check==1)]
e=e[(e.rating<8)&(e.neutral<8)].copy(); print('2b N',len(e),'excl',n0-len(e))
print(e.groupby(['world','valence']).rating.agg(['mean','std','count']).round(2))
for (w,v),g in e.groupby(['world','valence']): print(w,v,g.rating.value_counts().sort_index().to_dict())
e.to_csv('work/s2b_clean.csv',index=False)
