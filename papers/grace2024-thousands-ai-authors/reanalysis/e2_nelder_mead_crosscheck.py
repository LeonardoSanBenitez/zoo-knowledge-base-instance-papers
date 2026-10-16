"""HLMI: rebuild the paper's aggregate (gamma CDF per respondent, mean of CDFs) and decompose the 2047 headline."""
import os, glob, numpy as np, pandas as pd
from scipy import stats, optimize
D=os.environ.get('ESPAI_DATA','osf/files/osfstorage/')
d=pd.read_csv(glob.glob(D+'*.csv')[0],low_memory=False)
num=lambda c: pd.to_numeric(d[c],errors='coerce')
P=np.array([.1,.5,.9]); fp=pd.DataFrame({k:num(f'hlmi_{k}percent_clean') for k in ['10','50','90']}).dropna()
fy=pd.DataFrame({k:num(f'hlmi_{k}years_clean') for k in ['10','20','40']}).dropna()
print('complete fixed-probabilities',len(fp),' fixed-years',len(fy),' total',len(fp)+len(fy),'(paper n=1,714)')
def fit(x,p):
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
fits=[]
for _,r in fp.iterrows():
    if (r.values<=0).any() or not (r['10']<=r['50']<=r['90']): fits.append((None,'fp')); continue
    fits.append((fit(r.values,P)[0],'fp'))
for _,r in fy.iterrows():
    pr=r.values/100
    if not (pr[0]<=pr[1]<=pr[2]): fits.append((None,'fy')); continue
    fits.append((fit([10,20,40],pr)[0],'fy'))
ok=[(th,f) for th,f in fits if th is not None]
print('fitted',len(ok),'of',len(fits),'(non-monotone or zero-year answers dropped)')
grid=np.linspace(0.01,400,40000)
def pooled(sel):
    return np.mean([stats.gamma.cdf(grid,th[0],scale=th[1]) for th,f in ok if sel(f)],axis=0)
for lab,sel in [('ALL (paper headline)',lambda f:True),('fixed-probabilities',lambda f:f=='fp'),('fixed-years',lambda f:f=='fy')]:
    c=pooled(sel); q=lambda a: grid[np.searchsorted(c,a)]
    med_i=np.median([stats.gamma.ppf(.5,th[0],scale=th[1]) for th,f in ok if sel(f)])
    print(f'{lab:24s} pooled-CDF 10%: {2023+q(.1):.0f}  50%: {2023+q(.5):.0f}  90%: {2023+q(.9):.0f} | median respondent 50% year: {2023+med_i:.0f}')
# extrapolation: fixed-years respondents whose 50% year lies beyond the longest horizon they were asked about (40y)
pr40=fy['40']/100; print('fixed-years: P(HLMI within 40y) < 50%%: %d of %d (%.1f%%) -> their 50%% year is a gamma EXTRAPOLATION beyond any year they answered'%((pr40<.5).sum(),len(fy),100*(pr40<.5).mean()))
print('fixed-years: P(within 10y) >= 50%%: %.1f%%'%(100*(fy['10']>=50).mean()))
# raw medians straight from answers, no fitting
print('NO-FIT checks: fixed-probabilities median of the 50%% answer = %.0f years; fixed-years median P(within 20y)=%.0f%%, P(within 40y)=%.0f%%'%(fp['50'].median(),fy['20'].median(),fy['40'].median()))
