"""Controls for 'near-optimal': (1) the paper's hue rotations; (2) random CONVEX partitions of CIELAB
(Voronoi cells around K random chips), K matched to each language's number of modal terms, compared
hard-vs-hard with the language's own mode map."""
import os, pickle, numpy as np, pandas as pd
exec(open('re/c1.py').read().split('# WCS naming data')[0])
rng=np.random.default_rng(20261016)
D=pickle.load(open('re/enc.pkl','rb')); enc,keep=D['enc'],D['keep']
chips=pd.read_csv('wcs/chip.txt',sep='\t',header=None,names=['cnum','row','col','code']).sort_values('cnum')
lab=pd.read_csv('wcs/cnum-vhcm-lab-new.txt',sep='\t').sort_values('#cnum')[['L*','a*','b*']].values
pos={r.cnum:(r.row,int(r.col)) for r in chips.itertuples()}; inv={v:k for k,v in pos.items()}
def rotate(q,k):
    out=q.copy()
    for c,(r,col) in pos.items():
        if col==0: continue
        src=inv[(r,(col-1-k)%40+1)]
        out[c-1]=q[src-1]
    return out
def hard(labels,K):
    q=np.zeros((330,K)); q[np.arange(330),labels]=1; return q
res=[]
for l in keep:
    q=enc[l]; e0=fit(q)[0]
    er=[fit(rotate(q,k))[0] for k in range(1,40)]
    modal=q.argmax(axis=1); used=np.unique(modal); K=len(used)
    qh=hard(np.searchsorted(used,modal),K); eh=fit(qh)[0]
    ev=[]
    for _ in range(40):
        cen=lab[rng.choice(330,K,replace=False)]
        lbl=((lab[:,None,:]-cen[None,:,:])**2).sum(-1).argmin(1)
        ev.append(fit(hard(lbl,K))[0])
    res.append((l,K,e0,min(er),np.median(er),eh,np.median(ev),np.mean(np.array(ev)<=eh)))
R=pd.DataFrame(res,columns=['lang','K','eps_soft','eps_best_rotation','eps_median_rotation','eps_modemap','eps_median_voronoi','share_voronoi_le_modemap'])
print('languages',len(R))
print('soft encoder beats ALL 39 rotations: %d/%d = %.3f (paper 93%%)'%((R.eps_soft<R.eps_best_rotation).sum(),len(R),(R.eps_soft<R.eps_best_rotation).mean()))
print('median eps: soft %.3f | median rotation %.3f | mode map (hard) %.3f | random Voronoi (hard, same K) %.3f'%(R.eps_soft.median(),R.eps_median_rotation.median(),R.eps_modemap.median(),R.eps_median_voronoi.median()))
print('mode map beats the median random convex partition in %d/%d languages; mean share of Voronoi partitions at least as efficient as the mode map: %.3f'%((R.eps_modemap<R.eps_median_voronoi).sum(),len(R),R.share_voronoi_le_modemap.mean()))
R.to_csv('re/controls.csv',index=False)
