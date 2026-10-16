"""3c: how much of the loss from a 20-point drop in average (100k@70 -> 100k@50) is recovered by
multiplying the population 10,000-fold (100k@50 -> 1B@50)? Model-light, bootstrap over people."""
import pandas as pd, numpy as np
from scipy import stats
rng=np.random.default_rng(20261016)
import os; B=os.environ.get('CAVIOLA_OSF','work/osf/files/osfstorage/')
d=pd.read_csv(B+'Study 3c/PopEthics Study 3c.csv'); n0=len(d)
d=d[(d.Progress==100)&(d.Intro_large_size==36)&(d.attn_check==1)].copy()
print('3c N',len(d),'excl',n0-len(d))
K=['t_90','t_70','t_50k','t_50m','t_50b']
for k in K: d['r'+k]=np.where(d.valence=='happy',d[k],8-d[k])
print(d.groupby(['valence','thinking'])[['r'+k for k in K]].mean().round(2))
def R(g):
    loss=(g.rt_70-g.rt_50k).mean(); gain=(g.rt_50b-g.rt_50k).mean(); return gain/loss, loss, gain
rows=[]
for key,g in list(d.groupby(['valence','thinking']))+[(('pooled','pooled'),d)]:
    r,loss,gain=R(g); bs=[R(g.sample(len(g),replace=True,random_state=int(rng.integers(1e9))))[0] for _ in range(2000)]
    # step concavity: d3->d4 (1 order) vs d4->d5 (3 orders)
    s1=(g.rt_50m-g.rt_50k).mean(); s2=(g.rt_50b-g.rt_50m).mean()
    rows.append(dict(cell=key,n=len(g),loss_70to50=round(loss,3),gain_x10000=round(gain,3),recovered=round(r,3),ci=(round(np.percentile(bs,2.5),3),round(np.percentile(bs,97.5),3)),step_1order=round(s1,3),step_next3orders=round(s2,3)))
print(pd.DataFrame(rows).to_string())
# individuals: share for whom 10^4 more people recovers NOTHING (gain<=0) though the 70->50 drop cost something (loss>0)
g=d; m=(g.rt_70-g.rt_50k)>0
print('share with loss>0:',round(m.mean(),3),' of those, gain<=0:',round(((g.rt_50b-g.rt_50k)[m]<=0).mean(),3), ' gain>=loss (full recovery):', round(((g.rt_50b-g.rt_50k)[m]>=(g.rt_70-g.rt_50k)[m]).mean(),3))
d.to_csv('work/s3c_clean.csv',index=False)
