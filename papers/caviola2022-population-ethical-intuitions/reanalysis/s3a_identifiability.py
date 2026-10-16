"""Known-answer worlds for Study 3a. Two worlds that differ in what the paper claims to measure
(valence asymmetry of scope sensitivity) and are built to give the same six cell means.
World S: welfare effect SYMMETRIC (w_h = w_u) at each size + a size aversion a(s) common to valences.
World A: welfare effect ASYMMETRIC, no size aversion.
Run the authors' test (raw 1k-minus-1b trend, happy vs unhappy arm) on both."""
import numpy as np
from scipy import stats
rng=np.random.default_rng(7)
obs_h=np.array([5.117,4.326,3.714]); obs_u=np.array([3.041,2.558,2.323])   # raw means, 1k,1m,1b (higher=prefer larger)
# World S: h = 4 + w(s) - a(s); u = 4 - w(s) - a(s)  => w=(h-u)/2, a=4-(h+u)/2
w=(obs_h-obs_u)/2; a=4-(obs_h+obs_u)/2
print('World S implied symmetric welfare w(s):',w.round(3),' common size aversion a(s):',a.round(3))
# World A: a=0, w_h=h-4, w_u=4-u
print('World A implied w_h:',(obs_h-4).round(3),' w_u:',(4-obs_u).round(3))
def simulate(mh,mu,n=400,sd=1.8,reps=300):
    rej=0; ests=[]
    for _ in range(reps):
        H=np.clip(np.round(rng.normal(mh,sd,(n,3))),1,7); U=np.clip(np.round(rng.normal(mu,sd,(n,3))),1,7)
        dh=H[:,0]-H[:,2]; du=U[:,0]-U[:,2]; t=stats.ttest_ind(dh,du); rej+= t.pvalue<.05; ests.append(dh.mean()-du.mean())
    return rej/reps, np.mean(ests)
# both worlds have identical expected cell means by construction -> identical test behaviour
mS_h=4+w-a; mS_u=4-w-a; mA_h=4+(obs_h-4); mA_u=4-(4-obs_u)
print('World S cell means',mS_h.round(3),mS_u.round(3)); print('World A cell means',mA_h.round(3),mA_u.round(3))
print('authors trend-asymmetry test, World S (symmetric welfare): rejection rate, mean diff =',simulate(mS_h,mS_u))
print('authors trend-asymmetry test, World A (asymmetric welfare): rejection rate, mean diff =',simulate(mA_h,mA_u))
print('=> the six means do not distinguish the worlds; a non-post-treatment neutral arm would (World S predicts neutral = 4 - a(s) =',(4-a).round(2),'; World A predicts 4,4,4).')
