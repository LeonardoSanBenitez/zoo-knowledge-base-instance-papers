import pandas as pd, numpy as np
from scipy import stats
from common import dist
import os; B=os.environ.get('CAVIOLA_OSF','work/osf/files/osfstorage/')
e=pd.read_csv(B+'Study 1b/PopEthics Study 1b.csv'); n0=len(e)
e=e[(e.Progress==100)&(e.participant_id.astype(str).str.len()>5)]
ok=((e.happiness=='extreme')&(e.unhappiness=='extreme')&(e.attn_check==2))|((e.happiness=='extreme')&(e.unhappiness=='mild')&(e.attn_check==5))|((e.happiness=='mild')&(e.unhappiness=='extreme')&(e.attn_check==4))|((e.happiness=='mild')&(e.unhappiness=='mild')&(e.attn_check==1))
e=e[ok].copy(); print('1b N',len(e),'excl',n0-len(e))
print(e.groupby(['happiness','unhappiness']).numbers_1.agg(['mean','std','count']).round(2))
sym=(e.numbers_1>49)&(e.numbers_1<52)
print('authors code: share 50/51 over ALL conditions =', round(sym.mean(),4))
mm=e[(e.happiness=='mild')&(e.unhappiness=='mild')]
print('share 50/51 within mild-mild (what the text says) =', round(((mm.numbers_1>49)&(mm.numbers_1<52)).mean(),4), len(mm))
print(e.groupby(['happiness','unhappiness']).apply(lambda g: ((g.numbers_1>49)&(g.numbers_1<52)).mean()).round(3))
print('numbers_1+numbers_2 !=100:', ((e.numbers_1+e.numbers_2)!=100).sum())
e.to_csv('work/s1b_clean.csv',index=False)
# 1c
c=pd.read_csv(B+'Study 1c/PopEthics Study 1c.csv')
print(c.columns.tolist())
