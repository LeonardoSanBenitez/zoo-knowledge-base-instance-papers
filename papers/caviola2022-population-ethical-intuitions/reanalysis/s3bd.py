import pandas as pd, numpy as np
from scipy import stats
import os; B=os.environ.get('CAVIOLA_OSF','work/osf/files/osfstorage/')
d=pd.read_csv(B+'Study 3d/PopEthics Study 3d.csv'); n0=len(d)
d['gender']=np.where(d.gender=='female','female','male')
full=d[d.Progress==100].copy()
d=d[(d.Progress==100)&(d.attn1==1)&(d.attn2==1)&(d.attn_check==2)].copy()
print('3d N',len(d),'excl',n0-len(d),' full(progress=100) N',len(full))
for k in ['q_10','q_50','q_90']:
    d[k]=np.where(d.valence=='unhappy',8-d[k],d[k]); full[k]=np.where(full.valence=='unhappy',8-full[k],full[k])
d['cs']=d[['q_10','q_50','q_90']].mean(axis=1); full['cs']=full[['q_10','q_50','q_90']].mean(axis=1)
print(d.groupby(['valence','thinking']).cs.agg(['mean','std','count']).round(2))
for lab,s in [('excluded sample',d),('full sample',full)]:
    f=s[s.gender=='female'].cs; m=s[s.gender=='male'].cs
    t=stats.ttest_ind(f,m,equal_var=False); print(lab,'gender: F',round(f.mean(),2),round(f.std(),2),'M',round(m.mean(),2),round(m.std(),2),'Welch t',round(t.statistic,2),'df~',len(f)+len(m)-2)
print('strict averagist(1)/totalist(7) shares:',{k:(round((d[k]==1).mean(),2),round((d[k]==7).mean(),2)) for k in ['q_10','q_50','q_90']})
# 3b
b=pd.read_csv(B+'Study 3b/PopEthics Study 3b.csv'); print(b.columns.tolist()[14:40])
