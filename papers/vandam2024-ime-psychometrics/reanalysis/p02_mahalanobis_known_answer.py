"""p02: what does 'multivariate outlier, Mahalanobis p < .001' remove from skewed ordinal item data?
The paper excluded 159 of 1,102 (14.4%) on this rule. The variables used are not stated, and the code
that did it is not in the deposit; the 159 rows are not deposited. So two checks that need neither:

(A) Apply the rule to the RETAINED 886 on the 103 intensity items: how many would be flagged again?
(B) Known answer: a sample with NO outliers by construction -- a Gaussian copula with the retained data's
    own item marginals and item correlation structure (latent normal, thresholded to the observed
    category frequencies), n = 1,102. Share flagged at chi2(103) p < .001, and who is flagged: correlation
    of D^2 with the number of items endorsed >= Slight. 20 replicates.
If (B) flags many respondents, the 14.4% need not be outliers at all; and if flagged ones are high endorsers,
the exclusion removed precisely the people with many unusual experiences.
Usage: python -I -W ignore p02_mahalanobis_known_answer.py <rds> <out_dir>
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_rds import load
import numpy as np
from scipy import stats

d = load(sys.argv[1]); out = sys.argv[2]
items = sorted(c for c in d.columns if re.fullmatch(r'UES_\d{3}', c))
X = np.column_stack([d[c].astype(float).to_numpy() for c in items])
ok = ~np.isnan(X).any(1)
X = X[ok]
n, p = X.shape
crit = stats.chi2.ppf(0.999, p)
res = {'items': p, 'n_retained_complete': int(n), 'chi2_crit': float(crit)}


def d2(Z):
    mu = Z.mean(0); S = np.cov(Z, rowvar=False)
    Si = np.linalg.pinv(S)
    C = Z - mu
    return np.einsum('ij,jk,ik->i', C, Si, C)


D = d2(X)
flag = D > crit
res['A_flagged_in_retained'] = int(flag.sum())
endorse = (X >= 3).sum(1)
res['A_spearman_D2_endorsement'] = float(stats.spearmanr(D, endorse).statistic)
print(f'(A) retained n={n}, {p} items: flagged again at p<.001: {flag.sum()} ({100 * flag.mean():.1f}%); '
      f'Spearman(D^2, #items >= Slight) = {res["A_spearman_D2_endorsement"]:+.3f}')

# (B) Gaussian copula with observed marginals
rng = np.random.default_rng(20261023)
U = (stats.rankdata(X, axis=0) - 0.5) / n
Zs = stats.norm.ppf(U)
R = np.corrcoef(Zs, rowvar=False)
w, V = np.linalg.eigh(R); w = np.clip(w, 1e-6, None); L = V * np.sqrt(w)
cats = [np.sort(np.unique(X[:, j])) for j in range(p)]
cum = [np.array([np.mean(X[:, j] <= c) for c in cats[j]]) for j in range(p)]
shares, rhos, top_dec = [], [], []
for _ in range(20):
    G = rng.standard_normal((1102, p)) @ L.T
    Uu = stats.norm.cdf(G)
    Y = np.column_stack([cats[j][np.minimum(np.searchsorted(cum[j], Uu[:, j]), len(cats[j]) - 1)] for j in range(p)])
    Dy = d2(Y); fy = Dy > crit
    e = (Y >= 3).sum(1)
    shares.append(fy.mean()); rhos.append(stats.spearmanr(Dy, e).statistic)
    q = np.quantile(e, 0.9); top_dec.append(fy[e >= q].mean() / max(fy.mean(), 1e-9))
res.update(B_flag_share_mean=float(np.mean(shares)), B_flag_share_range=[float(min(shares)), float(max(shares))],
           B_spearman_D2_endorsement_mean=float(np.mean(rhos)), B_enrichment_top_decile=float(np.mean(top_dec)))
print(f'(B) no-outlier copula, n=1102, 20 reps: flagged {100 * np.mean(shares):.1f}% '
      f'(range {100 * min(shares):.1f}-{100 * max(shares):.1f}%; paper removed 14.4%); '
      f'Spearman(D^2, endorsement) {np.mean(rhos):+.3f}; flag rate in top endorsement decile = '
      f'{np.mean(top_dec):.1f}x the overall rate')
json.dump(res, open(os.path.join(out, 'p02_out.json'), 'w'), indent=1)
