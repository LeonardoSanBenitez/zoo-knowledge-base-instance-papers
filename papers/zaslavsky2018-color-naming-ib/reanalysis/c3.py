"""Scale of epsilon: random NON-convex partitions (chips assigned to K labels at random) vs random convex
(Voronoi) vs real mode maps vs the curve. How much of 'near-optimal' is convexity alone?"""
import pickle, numpy as np, pandas as pd
exec(open('re/c1.py').read().split('# WCS naming data')[0])
rng=np.random.default_rng(7)
R=pd.read_csv('re/controls.csv')
def hard(labels,K):
    q=np.zeros((330,K)); q[np.arange(330),labels]=1; return q
out=[]
for K in sorted(R.K.unique()):
    e=[fit(hard(rng.integers(0,K,330),K))[0] for _ in range(20)]
    out.append((K,np.median(e)))
E=dict(out); R['eps_random_nonconvex']=R.K.map(E)
med=R[['eps_random_nonconvex','eps_median_voronoi','eps_modemap']].median()
print(med.round(3).to_dict())
gap_conv=(R.eps_random_nonconvex-R.eps_median_voronoi)/R.eps_random_nonconvex
gap_lang=(R.eps_median_voronoi-R.eps_modemap)/R.eps_random_nonconvex
print('share of the distance from random partitions to the IB bound closed by CONVEXITY alone: median %.2f'%gap_conv.median())
print('additional share closed by the real language beyond a random convex partition: median %.2f'%gap_lang.median())
R.to_csv('re/controls.csv',index=False)
