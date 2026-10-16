import pandas as pd, numpy as np
from scipy import stats
from common import dist
import os; B=os.environ.get('CAVIOLA_OSF','work/osf/files/osfstorage/')
c=pd.read_csv(B+'Study 1c/PopEthics Study 1c.csv'); n0=len(c)
c['accept_assum']=c.accept_assum.fillna(c['accept_assum.1'])
c=c[(c.Progress==100)&(c.participantID.astype(str).str.len()>5)&(c.accept_assum==1)].copy()
c['rating']=c.inter_1.fillna(pd.to_numeric(c.intra_1,errors='coerce'))
print('1c N',len(c),'excl',n0-len(c))
print(c.groupby('condition').rating.agg(['mean','std','median','count']).round(2))
print('share 50/51', round(((c.rating>49)&(c.rating<52)).mean(),4))
print(c.attn_check.value_counts())
dist(c.rating,'1c pooled')
dist(c[c.attn_check==2].rating,'1c assumed-equal-intensity only')
c.to_csv('work/s1c_clean.csv',index=False)
b=pd.read_csv('work/s1b_clean.csv')
for (h,u),g in b.groupby(['happiness','unhappiness']): dist(g.numbers_1,f'1b {h}-happy/{u}-unhappy')
