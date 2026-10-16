import numpy as np, pandas as pd, statsmodels.formula.api as smf
d=pd.read_csv('re/clean.csv')
d['yb']=pd.cut(d.years,[0.16,1,2,5,10,20,80],include_lowest=True).astype(str)
m=smf.logit('negative~C(retreat)+C(yb)',d).fit(disp=0); k='C(retreat)[T.1]'
print('retreat OR adjusted for years band: %.2f [%.2f, %.2f] p=%.4f'%(np.exp(m.params[k]),*np.exp(m.conf_int().loc[k]),m.pvalues[k]))
print(d.groupby(['yb','retreat']).negative.agg(['size','mean']).round(3).unstack())
# KNOWN-ANSWER: which data-generating stories can produce a FLAT cross-sectional curve among current practitioners?
rng=np.random.default_rng(3); yrs=d.years.values
def sim(story, n=200000):
    t=rng.choice(yrs,n)                     # observed exposure distribution
    if story=='constant hazard, no attrition':
        p=1-np.exp(-0.03*t)
    elif story=='constant hazard + quit after event (k=0.09/yr)':
        h,k=0.03,0.09; p=h/(h+k)*(1-np.exp(-(h+k)*t))   # share experienced-and-still-practising, approx.
    elif story=='susceptible 26% experience within first months':
        p=0.26*(1-np.exp(-t/0.25))
    elif story=='recall decay (events forgotten at 10%/yr)':
        h,f=0.06,0.10; p=h/(h+f)*(1-np.exp(-(h+f)*t))
    ev=rng.random(n)<p
    s=pd.DataFrame({'t':t,'ev':ev}); s['yb']=pd.cut(s.t,[0.16,1,2,5,10,20,80],include_lowest=True)
    return s.groupby('yb',observed=True).ev.mean().round(3).values
for st in ['constant hazard, no attrition','constant hazard + quit after event (k=0.09/yr)','susceptible 26% experience within first months','recall decay (events forgotten at 10%/yr)']:
    print(f'{st:52s}', sim(st))
print(f'{"OBSERVED":52s}', d.groupby(pd.cut(d.years,[0.16,1,2,5,10,20,80],include_lowest=True),observed=True).negative.mean().round(3).values)
