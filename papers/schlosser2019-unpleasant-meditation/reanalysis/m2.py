import numpy as np, pandas as pd, statsmodels.formula.api as smf
d=pd.read_csv('re/clean.csv')
print('--- per-SD odds ratios (Table 2 labels these "1 SD"; the code fits raw units)')
for c in ['ptq','mindsens','scs']:
    m=smf.logit(f'negative~{c}',d).fit(disp=0); b=m.params[c]; lo,hi=m.conf_int().loc[c]; sd=d[c].std()
    print(f'{c}: per raw unit OR {np.exp(b):.3f}; per SD ({sd:.2f}) OR {np.exp(b*sd):.3f} [{np.exp(lo*sd):.3f},{np.exp(hi*sd):.3f}]')
for c in ['age','years','freq','dura']:
    m=smf.logit(f'negative~{c}',d).fit(disp=0); b=m.params[c]; sd=d[c].std(); print(f'{c}: per SD ({sd:.1f}) OR {np.exp(b*sd):.3f}')
print('--- deconstructive-only vs retreat: are they the same signal?')
print(pd.crosstab(d.medtype.fillna(-1),d.retreat,margins=True))
print('retreat share by medtype:',d.groupby(d.medtype.fillna(-1)).retreat.mean().round(3).to_dict())
dm=d.dropna(subset=['medtype','retreat','sex','rel','ptq','age'])
for f in ['negative~C(medtype)','negative~C(medtype)+C(retreat)','negative~C(medtype)+C(retreat)+C(sex)+C(rel)+ptq+age+years']:
    m=smf.logit(f,dm).fit(disp=0); t=[k for k in m.params.index if 'medtype' in k or 'retreat' in k]
    print(f'{f:70s} n={int(m.nobs)} ', '; '.join(f'{k} OR {np.exp(m.params[k]):.2f} [{np.exp(m.conf_int().loc[k,0]):.2f},{np.exp(m.conf_int().loc[k,1]):.2f}] p={m.pvalues[k]:.3f}' for k in t))
print('--- the 499 excluded "mixed" practitioners')
d['mt3']=d.medtype.map({0:'non-deconstructive only',1:'deconstructive only'}).fillna('mixed (excluded)')
print(d.groupby('mt3').agg(n=('negative','size'),prev=('negative','mean'),retreat=('retreat','mean'),years=('years','median')).round(3))
m=smf.logit("negative~C(mt3, Treatment('non-deconstructive only'))",d).fit(disp=0); print(np.exp(m.params).round(3).to_dict()); print(m.pvalues.round(4).to_dict())
d.to_csv('re/clean.csv',index=False)
