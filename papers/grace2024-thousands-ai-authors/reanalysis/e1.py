"""ESPAI 2023 (Grace et al.): (A) extinction-question coherence between subjects; (B) HLMI headline:
framing split, gamma extrapolation share, pooled-CDF vs median-respondent aggregation."""
import os, glob, numpy as np, pandas as pd
from scipy import stats, optimize
D=os.environ.get('ESPAI_DATA','osf/files/osfstorage/')
d=pd.read_csv(glob.glob(D+'*.csv')[0],low_memory=False)
num=lambda c: pd.to_numeric(d[c],errors='coerce')
# ---------- (A) three extinction questions, each respondent saw at most one
E={'Q1 any AI advances -> extinction':'extinction_basic_clean','Q2 inability to control AI -> extinction (SUBSET of Q1)':'extinction_controlproblem_clean','Q3 Q1 within 100 years (SUBSET of Q1)':'extinction_100years_clean'}
vals={k:num(c).dropna() for k,c in E.items()}
for k,v in vals.items(): print(f'{k:58s} n={len(v):4d} mean {v.mean():5.1f} median {v.median():4.1f} share>=10% {(v>=10).mean():.3f} share==0 {(v==0).mean():.3f}')
q1,q2,q3=vals.values()
print('Q2 vs Q1 (subset judged MORE likely?): Mann-Whitney p=%.2e; Hodges-Lehmann shift %.1f pts; P(Q2 draw > Q1 draw)=%.3f'%(stats.mannwhitneyu(q2,q1).pvalue, np.median(np.subtract.outer(q2.values,q1.values)), (np.subtract.outer(q2.values,q1.values)>0).mean()+0.5*(np.subtract.outer(q2.values,q1.values)==0).mean()))
print('Q3 vs Q1: Mann-Whitney p=%.3f'%stats.mannwhitneyu(q3,q1).pvalue)
print('overlap check (each respondent at most one question):', ((num(E[list(E)[0]]).notna()).astype(int)+(num(E[list(E)[1]]).notna()).astype(int)+(num(E[list(E)[2]]).notna()).astype(int)).max())
