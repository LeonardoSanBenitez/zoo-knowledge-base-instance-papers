"""Port of UnpleasantMeditation_code.do; reproduce prevalence, Table 1, Table 2."""
import os, numpy as np, pandas as pd, statsmodels.formula.api as smf
B=os.environ.get('SCHLOSSER_DATA','osf_d6mgj/files/osfstorage/')
x=pd.read_excel(B+'UnpleasantMeditation_Clean data.xlsx',sheet_name=None)
print(x['Codebook'].to_string())
d=x['MeditationRNTdata'].copy(); n0=len(d)
for c in d.columns:
    if c!='RespondentId_opinio': d[c]=pd.to_numeric(d[c],errors='coerce')
d=d.rename(columns={'years_regular_practice':'years','religious':'rel','education':'edu','residence':'resi','frequency_session':'freq','duration_session_average':'dura','retreat_experience':'retreat'})
d=d[~(d.years<0.16)]; d=d[d.negative.notna()]
print('N',len(d),'(file rows',n0,')'); p=d.negative.mean(); se=np.sqrt(p*(1-p)/len(d)); print('prevalence %.4f CI [%.4f, %.4f] count %d'%(p,p-1.96*se,p+1.96*se,d.negative.sum()))
for c in ['age','ptq','mindsens','scs','freq','dura','years']: print(c,'mean %.2f sd %.2f'%(d[c].mean(),d[c].std()))
d['medtype']=np.select([(d.attentional==0)&(d.constructive==0)&(d.deconstructive==1),((d.deconstructive==0)&((d.attentional==1)|(d.constructive==1)))],[1,0],np.nan)
print('medtype counts',d.medtype.value_counts(dropna=False).to_dict())
d['dur10']=d.dura/10
def lr(f,data=d):
    m=smf.logit(f,data).fit(disp=0); return m
rows=[]
for f,term in [('negative~age','age'),('negative~C(sex)','C(sex)[T.1]'),('negative~C(edu)','C(edu)[T.1]'),('negative~C(rel)','C(rel)[T.1]'),('negative~years','years'),('negative~C(medtype)','C(medtype)[T.1.0]'),('negative~C(retreat)','C(retreat)[T.1]'),('negative~freq','freq'),('negative~dur10','dur10'),('negative~ptq','ptq'),('negative~mindsens','mindsens'),('negative~scs','scs')]:
    m=lr(f); term=m.params.index[-1]; b=m.params[term]; ci=m.conf_int().loc[term]
    rows.append((f,round(np.exp(b),3),round(np.exp(ci[0]),3),round(np.exp(ci[1]),3),round(m.pvalues[term],4),int(m.nobs)))
print(pd.DataFrame(rows,columns=['model','OR','lo','hi','p','n']).to_string(index=False))
d.to_csv('re/clean.csv',index=False)
