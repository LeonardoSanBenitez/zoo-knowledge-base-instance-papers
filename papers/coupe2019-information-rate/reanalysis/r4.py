"""How much of '39 bits/s' is the estimator? The deposit carries two per-language entropies: ShE (unigram Shannon
entropy of syllables) and ID (syllable conditional entropy given the previous syllable within the word)."""
import os, numpy as np, pandas as pd
from scipy import stats
R=os.environ.get('INFORATE_REPO','repo/')
d=pd.read_csv(R+'InfoRateData.csv',sep='\t'); d['SR']=d.NS/d.Duration
d['IR']=d.ID*d.SR; d['ShIR']=d.ShE*d.SR
for v in ['IR','ShIR']: print('%s mean %.2f sd %.2f CV %.3f'%(v,d[v].mean(),d[v].std(),d[v].std()/d[v].mean()))
L=d.groupby('Language').agg(ID=('ID','first'),ShE=('ShE','first'),SR=('SR','mean'),IR=('IR','mean'),ShIR=('ShIR','mean'))
print('between-language CV: IR %.3f ShIR %.3f'%(L.IR.std()/L.IR.mean(),L.ShIR.std()/L.ShIR.mean()))
print('ratio ID/ShE per language: mean %.3f range %.3f-%.3f'%((L.ID/L.ShE).mean(),(L.ID/L.ShE).min(),(L.ID/L.ShE).max()))
print('r(SR, ShE) language level = %.3f p=%.4f'%stats.pearsonr(L.SR,L.ShE))
print(L[['ShE','ID']].round(2).T.to_string())
