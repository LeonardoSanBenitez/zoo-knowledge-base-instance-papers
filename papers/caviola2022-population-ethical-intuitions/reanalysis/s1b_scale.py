"""Is the 1b 'no interaction' a property of the percentage scale?
The paper interprets responses as trade RATIOS (happy needed per unhappy, '1.5-3 times').
On the ratio scale, intensity effects that multiply are additive in log-odds. Test the
interaction on logit(h) with clipping sensitivity, plus a median-based bootstrap."""
import pandas as pd, numpy as np, statsmodels.formula.api as smf
rng=np.random.default_rng(20261016)
b=pd.read_csv('work/s1b_clean.csv')
b['mh']=(b.happiness=='mild').astype(int); b['eu']=(b.unhappiness=='extreme').astype(int)
print('percentage scale (authors):'); m=smf.ols('numbers_1 ~ mh*eu',b).fit(); print(m.params.round(3).to_dict(), 'p_int=%.3f'%m.pvalues['mh:eu'])
for clip in [0.5,0.1,1.0,2.0]:
    h=b.numbers_1.clip(clip,100-clip)/100; b['L']=np.log(h/(1-h))
    m=smf.ols('L ~ mh*eu',b).fit(cov_type='HC3')
    print(f'logit clip={clip}: int={m.params["mh:eu"]:.3f} se={m.bse["mh:eu"]:.3f} p={m.pvalues["mh:eu"]:.4f} | mh={m.params["mh"]:.3f} eu={m.params["eu"]:.3f}')
sub=b[(b.numbers_1>0)&(b.numbers_1<100)].copy(); h=sub.numbers_1/100; sub['L']=np.log(h/(1-h))
m=smf.ols('L ~ mh*eu',sub).fit(cov_type='HC3'); print(f'logit excluding 0/100 (n={len(sub)}): int={m.params["mh:eu"]:.3f} p={m.pvalues["mh:eu"]:.4f}')
# rank-free robust: interaction of log median rates, bootstrap within cells
def lmr(x):
    x=np.clip(x,0.5,99.5); return np.log(np.median(x)/(100-np.median(x)))
cells={k:g.numbers_1.values for k,g in b.groupby(['mh','eu'])}
def inter(cs): return lmr(cs[(1,1)])-lmr(cs[(1,0)])-lmr(cs[(0,1)])+lmr(cs[(0,0)])
obs=inter(cells); bs=[]
for _ in range(4000):
    bs.append(inter({k:rng.choice(v,len(v)) for k,v in cells.items()}))
print(f'median-based log interaction {obs:.3f}, 95% boot CI [{np.percentile(bs,2.5):.3f},{np.percentile(bs,97.5):.3f}]')
# KNOWN-ANSWER CONTROL: simulate a world with NO log-scale interaction (rate = k*Iu/Ih per person, k lognormal),
# matched to observed additive cell means; does the PERCENTAGE-scale ANOVA show interaction? does logit OLS show none?
def sim(inter_true, n=90, reps=500):
    hits_pct=hits_log=0
    for _ in range(reps):
        rows=[]
        for mh in (0,1):
            for eu in (0,1):
                mu=0.58+0.12*mh+0.63*eu+inter_true*mh*eu
                L=rng.normal(mu,1.0,n); hh=np.round(100/(1+np.exp(-L)))
                rows+= [(mh,eu,x) for x in hh]
        s=pd.DataFrame(rows,columns=['mh','eu','h'])
        p1=smf.ols('h~mh*eu',s).fit().pvalues['mh:eu']
        hc=s.h.clip(0.5,99.5)/100; s['L']=np.log(hc/(1-hc)); p2=smf.ols('L~mh*eu',s).fit(cov_type='HC3').pvalues['mh:eu']
        hits_pct+=p1<.05; hits_log+=p2<.05
    return hits_pct/reps, hits_log/reps
for it in (0.0,0.7):
    print('sim true log-interaction',it,'-> rejection rate (pct-scale, logit-scale):',sim(it))
