"""Procreation asymmetry across instruments: Spears (reasons for a couple's decision; Table 1 transcribed)
vs Caviola 2022 Study 2a (world-betterness ratings; types from the reanalysis in caviola2022 record)."""
import numpy as np
from scipy.stats import fisher_exact, chi2_contingency
# Spears Table 1 (IZA DP 12537, 2019): shares of n; counts reconstructed and checked to round back
def counts(n,shares):
    c=[round(s*n/100) for s in shares]; back=[round(100*x/n,1) for x in c]
    assert all(abs(b-s)<=0.05 for b,s in zip(back,shares)), (back,shares); return c
s1a=counts(232,[74.1,12.5,4.7,8.6])   # both relevant, asymmetry (bad rel, good irrel), reverse (good rel, bad irrel), neither
s1b=counts(186,[74.7,15.1,3.2,7.0])
cav=[98,12,10,19]                     # caviola 2a, consistent responders (n=139): both, McMahan asym, reverse, full neutrality
for name,c in [('Spears 1a',s1a),('Spears 1b',s1b),('Caviola 2a',cav)]:
    n=sum(c); print(f'{name:11s} n={n:3d} both {c[0]/n:.3f} asym {c[1]/n:.3f} reverse {c[2]/n:.3f} neither {c[3]/n:.3f}  asym:reverse = {c[1]}:{c[2]} = {c[1]/c[2]:.2f}')
sp=[s1a[i]+s1b[i] for i in range(4)]
tab=np.array([[sp[1],sp[2]],[cav[1],cav[2]]])
orr,p=fisher_exact(tab); print(f'asymmetry vs its mirror, Spears pooled {sp[1]}:{sp[2]} vs Caviola {cav[1]}:{cav[2]}: odds ratio {orr:.2f}, Fisher p = {p:.4f}')
# within each study, is asym > reverse? exact binomial (sign test) on the discordant types
from scipy.stats import binomtest
for name,c in [('Spears pooled',sp),('Caviola 2a',cav)]:
    b=binomtest(c[1],c[1]+c[2],0.5); print(f'{name}: asym {c[1]} vs reverse {c[2]} -> sign test p = {b.pvalue:.4f}')
print('perverse/wrong-sign rate: Spears 10.1 pct of completers excluded (text, fn 7); Caviola 2a 18/157 = {:.3f} kept'.format(18/157))
