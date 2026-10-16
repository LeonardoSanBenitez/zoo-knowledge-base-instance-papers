"""Study 3a: does 'asymmetric scope sensitivity grows with population size' survive
subtracting each participant's OWN neutral-population answer at the SAME size?
Authors controlled for neutral only as a size-averaged covariate."""
import pandas as pd, numpy as np
from scipy import stats
import os; B=os.environ.get('CAVIOLA_OSF','work/osf/files/osfstorage/')
d=pd.read_csv(B+'Study 3a/PopEthics Study 3a.csv'); n0=len(d)
cn=np.where(d.condition=='happy',1,2)
d=d[(d.Progress==100)&(d.happy_intro==36)&(d.check_overpop==1)&(d.check_equal==1)&(d.attn_check==cn)].copy()
print('3a N',len(d),'excl',n0-len(d), d.condition.value_counts().to_dict())
S=[('1k_10k','neutral_1k_10k'),('1m_10m','neutral_1m_10m'),('1b_10b','neutral_1b_10')]
rows=[]
for cond in ['happy','unhappy']:
    g=d[d.condition==cond]
    for s,nc in S:
        raw=g[f'{cond}_{s}']; neu=g[nc]
        # welfare-attributable preference for the LARGER population (raw scale, 4=none)
        diff=raw-neu
        rows.append(dict(cond=cond,size=s,raw=raw.mean(),neutral=neu.mean(),diff=diff.mean(),sd=diff.std(),n=diff.notna().sum(),
                         t_raw_vs4=stats.ttest_1samp(raw,4).statistic, t_diff=stats.ttest_1samp(diff,0).statistic))
r=pd.DataFrame(rows); print(r.round(3).to_string())
# trend tests on differenced scores (paired, 1k vs 1b)
for cond in ['happy','unhappy']:
    g=d[d.condition==cond]
    dk=g[f'{cond}_1k_10k']-g.neutral_1k_10k; db=g[f'{cond}_1b_10b']-g.neutral_1b_10
    print(cond,'differenced 1k->1b change',round((db-dk).mean(),3), stats.ttest_rel(db,dk))
# authors' asymmetry-of-trend test (diff_kb by condition), raw vs differenced
d['both_1k']=d.happy_1k_10k.fillna(d.unhappy_1k_10k); d['both_1b']=d.happy_1b_10b.fillna(d.unhappy_1b_10b)
d['diff_kb']=d.both_1k-d.both_1b
print('authors diff_kb by condition (raw):', d.groupby('condition').diff_kb.mean().round(3).to_dict(), stats.ttest_ind(d[d.condition=='happy'].diff_kb,d[d.condition=='unhappy'].diff_kb))
d['diff_kb_adj']=(d.both_1k-d.neutral_1k_10k)-(d.both_1b-d.neutral_1b_10)
print('same, neutral-differenced:', d.groupby('condition').diff_kb_adj.mean().round(3).to_dict(), stats.ttest_ind(d[d.condition=='happy'].diff_kb_adj,d[d.condition=='unhappy'].diff_kb_adj))
# magnitude asymmetry per size after differencing: |unhappy diff| vs happy diff
d.to_csv('work/s3a_clean.csv',index=False)
