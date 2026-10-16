"""ID-free restatement of the trade-off. For the SAME text, a language that needs more syllables (NS) either takes
proportionally longer (no compensation: d log dur / d log NS = 1) or speaks faster (compensation: slope < 1;
full compensation = 0, i.e. equal time for equal content). Cells = language x text means; text fixed effects;
inference by language-cluster bootstrap (17 clusters) because NS varies mainly by language."""
import os, numpy as np, pandas as pd, statsmodels.formula.api as smf
rng=np.random.default_rng(20261016)
R=os.environ.get('INFORATE_REPO','repo/')
d=pd.read_csv(R+'InfoRateData.csv',sep='\t')
c=d.groupby(['Language','Text']).agg(NS=('NS','first'),dur=('Duration','mean'),ID=('ID','first')).reset_index()
print('NS constant within language x text?', d.groupby(['Language','Text']).NS.nunique().max()==1)
c['lNS']=np.log(c.NS); c['ldur']=np.log(c.dur); c['lID']=np.log(c.ID)
m=smf.ols('ldur ~ lNS + C(Text)',c).fit(cov_type='cluster',cov_kwds={'groups':c.Language.astype('category').cat.codes})
b=m.params['lNS']; print('slope d log(duration)/d log(NS), text FE, n=%d cells: %.3f (cluster SE %.3f)'%(len(c),b,m.bse['lNS']))
langs=c.Language.unique(); bs=[]
for _ in range(4000):
    s=rng.choice(langs,len(langs)); cc=pd.concat([c[c.Language==l].assign(Lb=i) for i,l in enumerate(s)])
    bs.append(smf.ols('ldur ~ lNS + C(Text)',cc).fit().params['lNS'])
print('language-cluster bootstrap 95%% CI for slope: [%.3f, %.3f]; compensation = 1 - slope = %.2f'%(np.percentile(bs,2.5),np.percentile(bs,97.5),1-b))
# language level only (17 points)
L=c.groupby('Language').agg(lNS=('lNS','mean'),ldur=('ldur','mean'),lID=('lID','first')).reset_index()
ml=smf.ols('ldur ~ lNS',L).fit(); print('language-level slope %.3f, 95%% CI [%.3f, %.3f], n=17'%(ml.params['lNS'],*ml.conf_int().loc['lNS']))
# what does ID add? if ID*NS = const, ID carries no information beyond NS for the duration question
m2=smf.ols('ldur ~ lNS + lID',L).fit(); print('adding log ID at language level: lNS %.3f (p=%.3f), lID %.3f (p=%.3f)'%(m2.params['lNS'],m2.pvalues['lNS'],m2.params['lID'],m2.pvalues['lID']))
# within-language across texts (sanity: should be ~1, constant speaker rate)
mw=smf.ols('ldur ~ lNS + C(Language)',c).fit(); print('WITHIN-language slope across texts (control, expect ~1): %.3f'%mw.params['lNS'])
