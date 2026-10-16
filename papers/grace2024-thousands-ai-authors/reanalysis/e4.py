"""How much of the HLMI / FAOL headline is the distribution family? Refit every respondent with gamma, lognormal,
Weibull (same least-squares criterion on the CDF), pool, and report the 50% year by framing."""
import os, glob, sys, numpy as np, pandas as pd
from scipy import stats, optimize
D=os.environ.get('ESPAI_DATA','osf/files/osfstorage/')
d=pd.read_csv(glob.glob(D+'*.csv')[0],low_memory=False)
num=lambda c: pd.to_numeric(d[c],errors='coerce')
FAM={'gamma':lambda x,a,b: stats.gamma.cdf(x,a,scale=b),'lognormal':lambda x,a,b: stats.lognorm.cdf(x,a,scale=b),'weibull':lambda x,a,b: stats.weibull_min.cdf(x,a,scale=b)}
def fit(F,x,p):
    x=np.asarray(x,float); p=np.clip(np.asarray(p,float),1e-4,1-1e-4)
    res=lambda th: F(x,np.exp(th[0]),np.exp(th[1]))-p; best=None
    for a0,b0 in ((1,20),(3,10),(0.5,60),(2,float(np.median(x)))):
        try: r=optimize.least_squares(res,np.log([a0,max(b0,.5)]),bounds=([-6,-6],[6,14]))
        except Exception: continue
        if best is None or r.cost<best.cost: best=r
    return np.exp(best.x)
grid=np.concatenate([np.linspace(0.01,400,20000),np.geomspace(400.01,1e7,4000)])
out=[]
for T,YRS in (('hlmi',[10,20,40]),('faol',[10,20,50])):
    fp=pd.DataFrame({k:num(f'{T}_{k}percent_clean') for k in ['10','50','90']}).dropna()
    fp=fp[(fp>0).all(axis=1)&(fp['10']<=fp['50'])&(fp['50']<=fp['90'])]
    fy=pd.DataFrame({k:num(f'{T}_{k}years_clean') for k in map(str,YRS)}).dropna()/100
    fy=fy[(fy.iloc[:,0]<=fy.iloc[:,1])&(fy.iloc[:,1]<=fy.iloc[:,2])]
    for fam,F in FAM.items():
        cdf={'fp':[],'fy':[]}
        for v in fp.values: a,b=fit(F,v,[.1,.5,.9]); cdf['fp'].append(F(grid,a,b))
        for v in fy.values: a,b=fit(F,YRS,v); cdf['fy'].append(F(grid,a,b))
        def q50(c):
            i=np.searchsorted(c,.5); return 2023+grid[min(i,len(grid)-1)]
        allc=np.mean(cdf['fp']+cdf['fy'],axis=0)
        out.append((T,fam,round(q50(np.mean(cdf['fp'],axis=0))),round(q50(np.mean(cdf['fy'],axis=0))),round(q50(allc))))
        print(out[-1],flush=True)
print(pd.DataFrame(out,columns=['milestone','family','50% fixed-probs','50% fixed-years','50% pooled (headline)']).to_string(index=False))
