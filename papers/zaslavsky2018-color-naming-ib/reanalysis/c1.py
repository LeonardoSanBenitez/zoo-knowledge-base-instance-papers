"""Reproduce Zaslavsky et al. 2018: efficiency loss eps_l of each WCS language under the released IB model
(LI source), and the hue-rotation control (93% of languages beat all 39 rotations)."""
import os, sys, pickle, numpy as np, pandas as pd
ROOT=os.environ.get('IBC','.')
PRECISION=1e-16
def xlogx(v):
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.where(v > PRECISION, v * np.log2(v), 0)
def H(p): return -xlogx(p).sum()
def MI(pXY): return H(pXY.sum(axis=0)) + H(pXY.sum(axis=1)) - H(pXY)
m=pickle.load(open(ROOT+'/repo/models/IB_color_naming_model/IB_color_naming.pkl','rb'))
pM=m['pM'].reshape(-1,1); pU_M=m['pU_M']; betas=m['betas']; curve=m['IB_curve']; F=curve[0]-betas*curve[1]
print('model: pM',pM.shape,'pU_M',pU_M.shape,'betas',len(betas),'range',betas.min(),betas.max(),'I(M;U)=%.3f'%MI(pU_M*pM))
def comp(q): return MI(q*pM)
def acc(q):
    pMW=q*pM; return MI(pMW.T@pU_M)
def fit(q):
    Fl=comp(q)-betas*acc(q); d=Fl-F; i=d.argmin(); return d[i]/betas[i], betas[i], i
# WCS naming data -> encoders
chips=pd.read_csv(ROOT+'/wcs/chip.txt',sep='\t',header=None,names=['cnum','row','col','code'])
term=pd.read_csv(ROOT+'/wcs/term.txt',sep='\t',header=None,names=['lang','spk','cnum','term'])
term=term[term.term.astype(str).str.strip()!='*']
enc={}; nresp={}
for l,g in term.groupby('lang'):
    t=g.groupby(['cnum','term']).size().unstack(fill_value=0)
    t=t.reindex(range(1,331),fill_value=0)
    cnt=t.sum(axis=1).values; nresp[l]=cnt.min()
    q=(t.values+0.0); q=q/np.maximum(q.sum(axis=1,keepdims=True),1)
    enc[l]=q
langs=sorted(enc); keep=[l for l in langs if nresp[l]>=5]
print('WCS languages',len(langs),'; with >=5 responses on every chip:',len(keep),'(paper: 110 - 15 = 95)')
rows=[]
for l in keep:
    e,b,i=fit(enc[l]); rows.append((l,e,b,comp(enc[l]),acc(enc[l]),enc[l].shape[1]))
R=pd.DataFrame(rows,columns=['lang','eps','beta','complexity','accuracy','n_terms'])
print('eps mean %.3f sd %.3f | beta mean %.3f sd %.3f (paper LI/IB: eps 0.18+-0.07, beta 1.03+-0.01; cross-validated)'%(R.eps.mean(),R.eps.std(),R.beta.mean(),R.beta.std()))
R.to_csv(ROOT+'/re/eps_wcs.csv',index=False)
np.save(ROOT+'/re/keep.npy',np.array(keep))
pickle.dump({'enc':enc,'keep':keep},open(ROOT+'/re/enc.pkl','wb'))
