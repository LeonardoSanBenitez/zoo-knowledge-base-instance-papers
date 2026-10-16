import pandas as pd, numpy as np
from scipy import stats
d=pd.read_csv('work/s2a_clean.csv')
def typ(r):
    h,u=r.jh,r.ju
    if h<4 or u>4: return 'wrong-sign (happy worse or unhappy better)'
    if h>4 and u<4: return 'both count (totalist-like)'
    if h==4 and u<4: return 'ASYMMETRY (McMahan): unhappy bad, happy neutral'
    if h==4 and u==4: return 'full neutrality'
    if h>4 and u==4: return 'reverse asymmetry: happy good, unhappy neutral'
d['type']=d.apply(typ,axis=1)
vc=d.type.value_counts(); print((vc).to_dict()); print((vc/len(d)).round(3).to_dict())
ok=d[~d.type.str.startswith('wrong')]
gh=ok.jh-4; gu=4-ok.ju
print(f'excluding wrong-sign (n={len(ok)}): mean goodness {gh.mean():.3f} badness {gu.mean():.3f}', stats.ttest_rel(gu,gh))
# among 'both count': magnitude asymmetry
bc=d[d.type.str.startswith('both')]; print('among both-count n=',len(bc),' badness-goodness mean',((4-bc.ju)-(bc.jh-4)).mean().round(3), stats.wilcoxon((4-bc.ju)-(bc.jh-4)))
# Does neutrality rating (j_neutral) predict type?
print(d.groupby('type').j_neutral.mean().round(2).to_dict())
e=pd.read_csv('work/s2b_clean.csv')
print('2b share answering 4 (=neutral) by cell:'); print(e.groupby(['world','valence']).rating.apply(lambda s:(s==4).mean()).round(3).to_dict())
print('2b wrong-sign share:', e.groupby(['world','valence']).apply(lambda g: ((g.rating<4)&(g.valence=='happy')|(g.rating>4)&(g.valence=='unhappy')).mean()).round(3).to_dict())
