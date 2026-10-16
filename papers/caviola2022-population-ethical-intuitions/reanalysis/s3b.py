import pandas as pd, numpy as np
import os; B=os.environ.get('CAVIOLA_OSF','work/osf/files/osfstorage/'); b=pd.read_csv(B+'Study 3b/PopEthics Study 3b.csv'); n0=len(b)
b=b[(b.Progress==100)&(b.accept_assump==1)&(b.believe_assumpt==1)].copy()
for k in ['happy_k','happy_m','happy_b']: b[k]=np.where(b.condition=='happy',b[k],8-b[k])
b['ag']=b[['happy_k','happy_m','happy_b']].mean(axis=1)
print('3b N',len(b),'excl',n0-len(b)); print(b.groupby('condition').ag.agg(['mean','std','count']).round(2))
for c in ['total_a','total_b','avg_a','avg_b']: b[c]=pd.to_numeric(b[c],errors='coerce')
calc=(b.total_a.abs()==240000)&(b.total_b.abs()==240000)&(b.avg_a.abs()==60)&(b.avg_b.abs()==40)
pr=(b.principle_total==1)&(b.principle_avg==1)
for lab,s in [('all',b),('correct calc',b[calc]),('correct principle',b[pr]),('both',b[calc&pr]),('computed total=avg (60/40)',b[(b.total_a.abs()==60)&(b.total_b.abs()==40)])]:
    print(f'{lab:28s} n={len(s):4d} mean={s.ag.mean():.2f} sd={s.ag.std():.2f} share<4={(s.ag<4).mean():.2f} share==4={(s.ag==4).mean():.2f}')
    print('    by condition', s.groupby('condition').ag.mean().round(2).to_dict())
b.to_csv('work/s3b_clean.csv',index=False)
