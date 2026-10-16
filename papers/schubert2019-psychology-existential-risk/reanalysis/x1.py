"""Recompute every printed chi-square in Schubert, Caviola & Faber 2019 from the counts printed beside it."""
import numpy as np
from scipy.stats import chi2_contingency
S={'2a':{'control':(50,213,257),'animals':(98,221,246),'sterilization':(97,208,252),'salience':(97,193,248),'utopia':(165,215,248)},
   '2b':{'control':(27,144,164),'animals':(55,159,172),'sterilization':(44,153,167),'salience':(58,147,177),'utopia':(105,157,175)}}
printed={('2a','animals','control'):8.82,('2a','sterilization','control'):23.83,('2a','salience','control'):29.90,('2a','utopia','control'):30.30,('2a','utopia','salience'):29.90,
         ('2b','animals','control'):8.82,('2b','salience','control'):14.10,('2b','utopia','control'):68.72,('2b','utopia','salience'):21.868,('2b','sterilization','control'):3.55}
for (st,a,b),pv in printed.items():
    ka,na,_=S[st][a]; kb,nb,_=S[st][b]; t=np.array([[ka,na-ka],[kb,nb-kb]])
    c0=chi2_contingency(t,correction=False)[0]; c1=chi2_contingency(t,correction=True)[0]
    flag='' if min(abs(c0-pv),abs(c1-pv))<0.06 else '   <-- MATCHES NEITHER'
    print(f'{st} {a:13s} vs {b:8s}: printed {pv:7.3f} | recomputed {c0:6.2f} (no Yates) {c1:6.2f} (Yates){flag}')
print('\nunconditional share (uniquely bad AND expected ranking) / everyone in the condition, and ranking-filter pass rate:')
for st in S:
    for c,(k,n,N) in S[st].items(): print(f'  {st} {c:13s} conditional {k/n:.3f}  unconditional {k/N:.3f}  pass-rate {n/N:.3f}')
