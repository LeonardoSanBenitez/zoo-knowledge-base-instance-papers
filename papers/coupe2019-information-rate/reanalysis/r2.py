"""ID-free check. The 15 texts are semantically parallel across languages, so the time a language takes to say
the same text is a direct (if rough) measure of semantic rate, with no entropy estimate from a written lexicon.
Does IR (bits/s) track it? And how dispersed are languages on it?"""
import os, numpy as np, pandas as pd
from scipy import stats
rng=np.random.default_rng(20261016)
R=os.environ.get('INFORATE_REPO','repo/')
d=pd.read_csv(R+'InfoRateData.csv',sep='\t'); d['SR']=d.NS/d.Duration; d['IR']=d.ID*d.SR
# text-normalised duration: duration / mean duration of that text across languages (removes text length)
td=d.groupby('Text').Duration.transform('mean'); d['rdur']=d.Duration/td
d['srate']=1/d.rdur   # relative semantic rate (1 = average language)
L=d.groupby('Language').agg(ID=('ID','first'),SR=('SR','mean'),IR=('IR','mean'),srate=('srate','mean'),NS=('NS','mean')).reset_index()
cv=lambda x: x.std()/x.mean()
print('between-language CV: SR %.3f | IR %.3f | semantic rate (1/text-normalised duration) %.3f | NS per text %.3f'%(cv(L.SR),cv(L.IR),cv(L.srate),cv(L.NS)))
print('max/min across languages: SR %.2f | IR %.2f | semantic rate %.2f'%(L.SR.max()/L.SR.min(),L.IR.max()/L.IR.min(),L.srate.max()/L.srate.min()))
r=stats.pearsonr(L.IR,L.srate); print('does IR track semantic rate? r(IR, semantic rate) = %.3f p=%.3f (n=17)'%r)
r=stats.pearsonr(L.SR,L.srate); print('r(SR, semantic rate) = %.3f p=%.3f'%r)
# bits per text implied: ID * NS (should be ~constant across languages if ID measured semantic information)
L['bits_per_text']=L.ID*L.NS; print('implied bits per (average) text: CV %.3f, range %.0f-%.0f'%(cv(L.bits_per_text),L.bits_per_text.min(),L.bits_per_text.max()))
print('r(ID, NS) = %.3f p=%.4f  (denser syllables -> fewer syllables for the same text)'%stats.pearsonr(L.ID,L.NS))
# permutation null (PM2): ID shuffled among languages; how often is between-language CV(IR) <= observed?
obs=cv(L.IR); sims=[]
for _ in range(20000):
    idp=rng.permutation(L.ID.values); sims.append(cv(pd.Series(idp*L.SR.values)))
sims=np.array(sims); print('PM2 permutation: observed CV(IR) %.4f; null median %.4f; P(null<=obs) = %.4f'%(obs,np.median(sims),(sims<=obs).mean()))
print(L.sort_values('srate').round(3).to_string(index=False))
L.to_csv('re/lang_means2.csv',index=False)
