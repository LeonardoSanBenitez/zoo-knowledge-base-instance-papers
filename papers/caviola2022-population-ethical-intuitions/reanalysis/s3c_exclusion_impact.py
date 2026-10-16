"""Does the condition-dependent exclusion of the 96 change Study 3c's headline (share of the 70->50 loss recovered by
a 10^4-fold larger population)? Recompute with and without them, by valence and pooled, bootstrap CIs."""
import pandas as pd, numpy as np
rng = np.random.default_rng(1)
d = pd.read_csv('osf/files/osfstorage/Study 3c/PopEthics Study 3c.csv'); d = d[(d.Progress == 100) & (d.Intro_large_size == 36)].copy()
K = ['t_90', 't_70', 't_50k', 't_50m', 't_50b']
for k in K: d['r' + k] = np.where(d.valence == 'happy', d[k], 8 - d[k])
def R(g): return (g.rt_50b - g.rt_50k).mean() / (g.rt_70 - g.rt_50k).mean()
for name, s in [('paper (check == correct)', d[d.attn_check == 1]), ('+ the 96 "extremely unhappy"', d[d.attn_check.isin([1, 3])])]:
    out = []
    for key, g in list(s.groupby('valence')) + [('pooled', s)]:
        bs = [R(g.sample(len(g), replace=True, random_state=int(rng.integers(1e9)))) for _ in range(2000)]
        out.append(f"{key}: {R(g):.3f} [{np.percentile(bs, 2.5):.3f}, {np.percentile(bs, 97.5):.3f}] n={len(g)}")
    print(f'{name:32s}', ' | '.join(out))
