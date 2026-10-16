"""HLMI: rebuild the paper's aggregate (gamma CDF per respondent, mean of CDFs) and decompose the 2047 headline."""
import os, glob, numpy as np, pandas as pd
from scipy import stats, optimize
import sys
T=sys.argv[1] if len(sys.argv)>1 else 'hlmi'
YRS=['10','20','40'] if T=='hlmi' else ['10','20','50']
D=os.environ.get('ESPAI_DATA','osf/files/osfstorage/')
d=pd.read_csv(glob.glob(D+'*.csv')[0],low_memory=False)
num=lambda c: pd.to_numeric(d[c],errors='coerce')
P=np.array([.1,.5,.9]); fp=pd.DataFrame({k:num(f'{T}_{k}percent_clean') for k in ['10','50','90']}).dropna()
fy=pd.DataFrame({k:num(f'{T}_{k}years_clean') for k in YRS}).dropna()
print('complete fixed-probabilities',len(fp),' fixed-years',len(fy),' total',len(fp)+len(fy),'(paper n=1,714)')
def fit_nm(x,p):
    """least-squares gamma CDF through (x,p); x in years from survey, p in (0,1)"""
    x=np.asarray(x,float); p=np.clip(np.asarray(p,float),1e-4,1-1e-4)
    def loss(th):
        k,s=np.exp(th); return ((stats.gamma.cdf(x,k,scale=s)-p)**2).sum()
    best=None
    for k0 in (0.5,1,2,4):
        for s0 in (5,20,60):
            r=optimize.minimize(loss,np.log([k0,s0]),method='Nelder-Mead',options={'xatol':1e-6,'fatol':1e-10,'maxiter':4000})
            if best is None or r.fun<best.fun: best=r
    return np.exp(best.x), best.fun
def fit(x,p):
    """least-squares gamma CDF through (x,p) via trust-region LS on log-params; 4 starts"""
    x=np.asarray(x,float); p=np.clip(np.asarray(p,float),1e-4,1-1e-4)
    res=lambda th: stats.gamma.cdf(x,np.exp(th[0]),scale=np.exp(th[1]))-p
    best=None
    for k0,s0 in ((1,20),(3,10),(0.5,60),(2,np.median(x))):
        try:
            r=optimize.least_squares(res,np.log([k0,max(s0,0.5)]),bounds=([-6,-6],[6,14]))
        except Exception: continue
        if best is None or r.cost<best.cost: best=r
    return np.exp(best.x), best.cost
fits=[]
for _,r in fp.iterrows():
    if (r.values<=0).any() or not (r['10']<=r['50']<=r['90']): fits.append((None,'fp')); continue
    fits.append((fit(r.values,P)[0],'fp'))
for _,r in fy.iterrows():
    pr=r.values/100
    if not (pr[0]<=pr[1]<=pr[2]): fits.append((None,'fy')); continue
    fits.append((fit([int(y) for y in YRS],pr)[0],'fy'))
ok=[(th,f) for th,f in fits if th is not None]
print('fitted',len(ok),'of',len(fits),'(non-monotone or zero-year answers dropped)')
grid=np.concatenate([np.linspace(0.01,400,40000),np.geomspace(400.01,1e6,6000)])
def pooled(sel):
    return np.mean([stats.gamma.cdf(grid,th[0],scale=th[1]) for th,f in ok if sel(f)],axis=0)
for lab,sel in [('ALL (paper headline)',lambda f:True),('fixed-probabilities',lambda f:f=='fp'),('fixed-years',lambda f:f=='fy')]:
    c=pooled(sel); q=lambda a: grid[min(np.searchsorted(c,a),len(grid)-1)]
    med_i=np.median([stats.gamma.ppf(.5,th[0],scale=th[1]) for th,f in ok if sel(f)])
    print(f'{lab:24s} pooled-CDF 10%: {2023+q(.1):.0f}  50%: {2023+q(.5):.0f}  90%: {2023+q(.9):.0f} | median respondent 50% year: {2023+med_i:.0f}')
# extrapolation: fixed-years respondents whose 50% year lies beyond the longest horizon they were asked about (40y)
pr40=fy[YRS[-1]]/100; print('fixed-years: P(%s within %sy) < 50%%: %d of %d (%.1f%%) -> their 50%% year is a gamma EXTRAPOLATION beyond any year they answered'%(T.upper(),YRS[-1],(pr40<.5).sum(),len(fy),100*(pr40<.5).mean()))
print('fixed-years: P(within 10y) >= 50%%: %.1f%%'%(100*(fy['10']>=50).mean()))
# raw medians straight from answers, no fitting
print('NO-FIT checks: fixed-probabilities median of the 50%% answer = %.0f years; fixed-years median P(within %sy)=%.0f%%, P(within %sy)=%.0f%%'%(fp['50'].median(),YRS[1],fy[YRS[1]].median(),YRS[-1],fy[YRS[-1]].median()))
