"""Port of Parfit2a.R / Parfit2b.R: exclusions, counts, Yates chi-squares, CRT logistic (B vs Exp(B))."""
import os, numpy as np, pandas as pd, statsmodels.formula.api as smf
from scipy.stats import chi2_contingency
R=os.environ.get('SCHUBERT_DATA','.')
def load(study):
    f={'2a':R+'/osf_erp2z/files/osfstorage/Parfit2a.csv','2b':R+'/osf_c4qy9/files/osfstorage/Parfit2b.csv'}[study]
    d=pd.read_csv(f,sep=';',low_memory=False); n0=len(d)
    for c in d.columns:
        if c not in ('condition','CRT_3') and not c.startswith('Free'): d[c]=pd.to_numeric(d[c],errors='coerce')
    d=d[(d.Progress==100)&(d.att_check==1)&(d.OUS_10==2)].copy()
    d['CRT']=(d.CRT_1==2).astype(int)+(d.CRT_2==8).astype(int)+(d.CRT_3.astype(str).str.strip().str.lower()=='emily').astype(int)
    pre={'control':'control_Parfit_prel','goodfuture':'good_Parfit_prel','zebras':'Zebra_Parfit_prel','salientfuture':'salience_Parfit_prel','sterilization':'Steril_Parfit_prelim'}
    mains={'control':'control_Parfit_main','goodfuture':'good_Parfit_main','zebras':'Zebra_Parfit_main','salientfuture':'salience_Parfit_main','sterilization':'Steril_Parfit_main'}
    d['p1']=np.nan; d['p4']=np.nan; d['main']=np.nan; d['free']=''
    for cnd,p in pre.items():
        m=d.condition==cnd
        d.loc[m,'p1']=d.loc[m,p+'_1']; d.loc[m,'p4']=d.loc[m,p+'_4']; d.loc[m,'main']=d.loc[m,mains[cnd]]
    fc=[c for c in d.columns if c.startswith('Free')]
    d['free']=d[fc].astype(str).replace('nan','').agg(' '.join,axis=1).str.strip()
    d['rank_ok']=(d.p1==1)&(d.p4==3)
    d['OUS_IB']=d[[f'OUS_{i}' for i in range(1,6)]].mean(axis=1); d['OUS_IH']=d[[f'OUS_{i}' for i in range(6,10)]].mean(axis=1)
    return d,n0
for st in ['2a','2b']:
    d,n0=load(st); print(f'== Study {st}: N={len(d)} (excluded {n0-len(d)})')
    print(' main coding:',d.main.value_counts(dropna=False).to_dict())
    t=d.groupby('condition').agg(N=('rank_ok','size'),ranked=('rank_ok','sum')).astype(int)
    ok=d[d.rank_ok]; t['second_greater']=ok.groupby('condition').main.apply(lambda s:(s==1).sum()); print(t)
    for a in ['zebras','sterilization','salientfuture','goodfuture']:
        x=ok[ok.condition.isin(['control',a])]; tb=pd.crosstab(x.main,x.condition); print(f'  control vs {a}: Yates chi2 = {chi2_contingency(tb)[0]:.2f}')
    x=ok[ok.condition.isin(['salientfuture','goodfuture'])]; print(f'  salient vs good: Yates chi2 = {chi2_contingency(pd.crosstab(x.main,x.condition))[0]:.2f}')
    m=smf.logit('main~CRT+OUS_IH+OUS_IB',ok.dropna(subset=['main'])).fit(disp=0)
    print(f'  CRT logistic: B = {m.params.CRT:.3f}, Exp(B) = {np.exp(m.params.CRT):.3f}, p = {m.pvalues.CRT:.4f}')
    d.to_csv(f'work/s{st}.csv',index=False)
