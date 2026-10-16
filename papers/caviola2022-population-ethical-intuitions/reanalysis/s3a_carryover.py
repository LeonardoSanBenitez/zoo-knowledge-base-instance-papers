"""The neutral items in 3a are IDENTICAL across arms and asked AFTER the main task. If their size trend differs
by arm, they are post-treatment and cannot serve as a baseline (for the authors' covariate or my differencing)."""
import pandas as pd, numpy as np
from scipy import stats
d=pd.read_csv('work/s3a_clean.csv')
d['ntr']=d.neutral_1k_10k-d.neutral_1b_10; d['nlev']=d[['neutral_1k_10k','neutral_1m_10m','neutral_1b_10']].mean(axis=1)
h=d[d.condition=='happy']; u=d[d.condition=='unhappy']
print('neutral size trend (1k minus 1b) by arm:', round(h.ntr.mean(),3), round(u.ntr.mean(),3), stats.ttest_ind(h.ntr,u.ntr))
print('neutral level by arm:', round(h.nlev.mean(),3), round(u.nlev.mean(),3), stats.ttest_ind(h.nlev,u.nlev))
for c,g in [('happy',h),('unhappy',u)]:
    same=(g[f'{c}_1k_10k']==g.neutral_1k_10k)&(g[f'{c}_1m_10m']==g.neutral_1m_10m)&(g[f'{c}_1b_10b']==g.neutral_1b_10)
    print(c,'corr(main trend, neutral trend)=%.3f'%np.corrcoef(g[f'{c}_1k_10k']-g[f'{c}_1b_10b'],g.ntr)[0,1],' identical on all 3 sizes: %d/%d = %.3f'%(same.sum(),len(g),same.mean()))
    for lab,s in [('copiers',g[same]),('non-copiers',g[~same])]:
        print('   ',lab,len(s),'main',np.round([s[f'{c}_{k}'].mean() for k in ['1k_10k','1m_10m','1b_10b']],2),'neutral',np.round([s[n].mean() for n in ['neutral_1k_10k','neutral_1m_10m','neutral_1b_10']],2))
