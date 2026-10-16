"""Robustness of the convex null: Voronoi centres drawn in proportion to the source prior pM (where
communication happens) instead of uniformly over chips."""
import numpy as np, pandas as pd
exec(open('re/c1.py').read().split('# WCS naming data')[0])
rng=np.random.default_rng(11)
lab=pd.read_csv('wcs/cnum-vhcm-lab-new.txt',sep='\t').sort_values('#cnum')[['L*','a*','b*']].values
R=pd.read_csv('re/controls.csv'); w=pM.ravel()/pM.sum()
def hard(labels,K):
    q=np.zeros((330,K)); q[np.arange(330),labels]=1; return q
med={}
for K in sorted(R.K.unique()):
    e=[]
    for _ in range(40):
        cen=lab[rng.choice(330,K,replace=False,p=w)]
        e.append(fit(hard(((lab[:,None,:]-cen[None])**2).sum(-1).argmin(1),K))[0])
    med[K]=np.median(e)
R['eps_median_voronoi_pM']=R.K.map(med)
print('median eps: Voronoi uniform centres %.3f | Voronoi pM-weighted centres %.3f | mode maps %.3f'%(R.eps_median_voronoi.median(),R.eps_median_voronoi_pM.median(),R.eps_modemap.median()))
print('mode map beats median pM-weighted Voronoi in %d/%d languages'%((R.eps_modemap<R.eps_median_voronoi_pM).sum(),len(R)))
print('by K:'); print(R.groupby('K')[['eps_modemap','eps_median_voronoi','eps_median_voronoi_pM','eps_random_nonconvex']].median().round(3).assign(n=R.groupby('K').size()))
R.to_csv('re/controls.csv',index=False)
