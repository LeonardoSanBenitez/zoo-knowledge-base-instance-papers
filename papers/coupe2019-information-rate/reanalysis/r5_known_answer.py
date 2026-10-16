"""Known-answer check for the compensation slope. Worlds: true language-level slope b in {0 (full compensation),
0.35, 1 (none)}; text-specific translation noise in NS that is NOT compensated (slope 1, as the within-language
control shows 0.98). Noise SD and language SD are taken from the data. Which estimator recovers b?"""
import os, numpy as np, pandas as pd, statsmodels.formula.api as smf
rng=np.random.default_rng(11)
R=os.environ.get('INFORATE_REPO','repo/')
d=pd.read_csv(R+'InfoRateData.csv',sep='\t')
c=d.groupby(['Language','Text']).agg(NS=('NS','first'),dur=('Duration','mean')).reset_index(); c['lNS']=np.log(c.NS); c['ldur']=np.log(c.dur)
res=smf.ols('lNS ~ C(Language)+C(Text)',c).fit(); s_tr=np.sqrt(res.mse_resid)
lang_sd=c.groupby('Language').lNS.mean().std(); dur_res=smf.ols('ldur ~ lNS + C(Text)+C(Language)',c).fit(); s_dur=np.sqrt(dur_res.mse_resid)
print('from data: language SD of log NS %.3f, translation-noise SD %.3f, residual duration SD %.3f'%(lang_sd,s_tr,s_dur))
L,T=17,15
for b in (0.0,0.35,1.0):
    est_fe=[];est_lang=[]
    for _ in range(400):
        lang=rng.normal(0,lang_sd,L); txt=rng.normal(0,0.3,T)
        rows=[]
        for i in range(L):
            for j in range(T):
                e=rng.normal(0,s_tr); lNS=lang[i]+txt[j]+e
                ldur=b*lang[i]+txt[j]+1.0*e+rng.normal(0,s_dur)+rng.normal(0,0.0)
                rows.append((i,j,lNS,ldur))
        s=pd.DataFrame(rows,columns=['Language','Text','lNS','ldur'])
        est_fe.append(smf.ols('ldur ~ lNS + C(Text)',s).fit().params['lNS'])
        g=s.groupby('Language')[['lNS','ldur']].mean(); est_lang.append(np.polyfit(g.lNS,g.ldur,1)[0])
    print('true b=%.2f: text-FE estimator mean %.3f [%.3f,%.3f] | language-level estimator mean %.3f [%.3f,%.3f]'%(b,np.mean(est_fe),*np.percentile(est_fe,[2.5,97.5]),np.mean(est_lang),*np.percentile(est_lang,[2.5,97.5])))
