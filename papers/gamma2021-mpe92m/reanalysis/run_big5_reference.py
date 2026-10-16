"""External benchmark asked for by this record: the split-half congruence profile of a WELL-BEHAVED instrument, run through
the identical pipeline (mpelib.split_half_congruence: Spearman via ranks, principal factors, oblimin, Hungarian matching).
Instrument: IPIP Big-Five 50 items, openpsychometrics.org BIG5.zip (19,719 respondents; sha256 67953298d75d...).
Subsampled ONCE to n = 1,403 (the MPE-92M analysis N), 30 random half-splits, k in (3, 5, 8, 12)."""
import os, json, numpy as np, pandas as pd
from mpelib import split_half_congruence
P = os.environ.get('BIG5_CSV', 'work/BIG5/data.csv')
d = pd.read_csv(P, sep='\t')
items = [c for c in d.columns if c[0] in 'ENACO' and c[1:].isdigit()]
assert len(items) == 50
X = d[items]; X = X[(X >= 1).all(1) & (X <= 5).all(1)]          # drop rows with 0 = missing
X = X.sample(1403, random_state=20261016).reset_index(drop=True).astype(float)
mpe = json.load(open('results_replicability.json'))['real']
out = {}
for k in (3, 5, 8, 12):
    ph = split_half_congruence(X, k, n_splits=30, seed=1)
    med = np.median(ph, axis=0)
    out[k] = {'median_by_rank': [round(float(x), 3) for x in med], 'n_ge_95': int((med >= .95).sum()), 'mean': round(float(med.mean()), 3)}
    m = mpe.get(str(k))
    mm = np.array(m['median']) if m else None
    print(f"k={k:2d} BIG5 median phi by rank {out[k]['median_by_rank']} | >=.95: {out[k]['n_ge_95']}/{k} | mean {out[k]['mean']}")
    if mm is not None: print(f"      MPE-92M                  {[round(float(x),3) for x in mm]} | >=.95: {int((mm>=.95).sum())}/{k} | mean {mm.mean():.3f}")
json.dump({'n': 1403, 'n_splits': 30, 'items': 50, 'results': out}, open('results_big5_reference.json', 'w'), indent=1)
