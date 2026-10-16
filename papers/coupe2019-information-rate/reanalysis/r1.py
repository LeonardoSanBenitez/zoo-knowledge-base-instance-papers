import os, numpy as np, pandas as pd
from scipy import stats
R=os.environ.get('INFORATE_REPO','repo/')
d=pd.read_csv(R+'InfoRateData.csv',sep='\t')
d['SR']=d.NS/d.Duration; d['IR']=d.ID*d.SR
print('rows',len(d),'languages',d.Language.nunique(),'speakers',d.Speaker.nunique(),'texts',d.Text.nunique())
for v in ['SR','IR']: print(v,'mean %.2f sd %.2f CV %.3f'%(d[v].mean(),d[v].std(),d[v].std()/d[v].mean()))
r=stats.pearsonr(d.SR,d.ID); print('ROW-LEVEL (paper) r=%.3f p=%.2e n=%d'%(r[0],r[1],len(d)))
L=d.groupby('Language').agg(ID=('ID','first'),SR=('SR','mean'),IR=('IR','mean'),dur=('Duration','mean'),NS=('NS','mean')).reset_index()
rl=stats.pearsonr(L.SR,L.ID); sl=stats.spearmanr(L.SR,L.ID)
z=np.arctanh(rl[0]); se=1/np.sqrt(len(L)-3); ci=np.tanh([z-1.96*se,z+1.96*se])
print('LANGUAGE-LEVEL n=%d: Pearson r=%.3f p=%.4f 95%%CI [%.2f,%.2f]; Spearman rho=%.3f p=%.4f'%(len(L),rl[0],rl[1],ci[0],ci[1],sl[0],sl[1]))
S=d.groupby(['Language','Speaker']).agg(ID=('ID','first'),SR=('SR','mean')).reset_index()
rs=stats.pearsonr(S.SR,S.ID); print('speaker-level n=%d r=%.3f p=%.2e (still pseudo-replicated: ID varies by language only)'%(len(S),rs[0],rs[1]))
# between vs within language CVs
for v in ['SR','IR']:
    m=L[v]; print(v,'between-language CV of language means: %.3f'%(m.std()/m.mean()))
w=d.groupby('Language').apply(lambda g: pd.Series({'cvSR':g.SR.std()/g.SR.mean(),'cvIR':g.IR.std()/g.IR.mean()}))
print('within-language CV identical for SR and IR by construction? max abs diff = %.2e'%(w.cvSR-w.cvIR).abs().max())
# log-variance decomposition at language level
lsr=np.log(L.SR); lid=np.log(L.ID); lir=np.log(L.IR)
print('var log SR %.4f, var log ID %.4f, 2cov %.4f, var log IR %.4f'%(lsr.var(),lid.var(),2*np.cov(lsr,lid)[0,1],lir.var()))
print(L.sort_values('ID').round(2).to_string(index=False))
L.to_csv('re/lang_means.csv',index=False)
