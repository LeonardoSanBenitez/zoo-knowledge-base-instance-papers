"""Open question: is the clone deficit (real split-half congruence < clone congruence by .13-.14) a visual-analogue RESPONSE-
STYLE artifact (extreme vs midpoint users of the 0-100 scales) rather than phenomenology? Rerun the clone test after
removing person-level response style: (a) row-centering (each respondent's mean over the 92 items removed),
(b) row z-scoring (mean AND spread removed). The clone is fitted to the TRANSFORMED data, so real and clone are compared
like-for-like (ipsatization creates its own negative dependencies; they are then present in both).
If the deficit shrinks to ~0 under (b), response style explains it. If it persists, it does not."""
import os, json, warnings, numpy as np, pandas as pd
warnings.filterwarnings('ignore')
import mpelib as M
DTA = os.environ.get('MPE_DTA', M.DTA)
X0, cov = M.load(DTA)
N, P = X0.shape
variants = {'raw': X0,
            'row-centered': X0.sub(X0.mean(1), axis=0),
            'row-z': X0.sub(X0.mean(1), axis=0).div(X0.std(1).replace(0, np.nan), axis=0).fillna(0)}
rng = np.random.default_rng(31); out = {}
for name, X in variants.items():
    for k in (5, 8, 12):
        L = M.loadings(X, k); comm = np.clip((L ** 2).sum(1), 0, 0.99); uniq = np.sqrt(1 - comm)
        Xc = pd.DataFrame(rng.standard_normal((N, k)) @ L.T + rng.standard_normal((N, P)) * uniq, columns=X.columns)
        real = np.median(M.split_half_congruence(X, k, n_splits=15, seed=500 + k), 0)
        clone = np.median(M.split_half_congruence(Xc, k, n_splits=15, seed=600 + k), 0)
        out[f'{name}_k{k}'] = {'real_mean': round(float(real.mean()), 3), 'clone_mean': round(float(clone.mean()), 3),
                               'deficit': round(float(clone.mean() - real.mean()), 3), 'real_ge95': int((real >= .95).sum())}
        print(name, k, out[f'{name}_k{k}'], flush=True)
json.dump(out, open('results_clone_response_style.json', 'w'), indent=1)
