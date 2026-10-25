"""Break test for the key result (baseline implicit self-evaluation predicts change in implicit partner
evaluation, controlling baseline partner evaluation).

Residualised change with an unreliable baseline is a known artefact generator: if the predictor correlates
with the TRUE baseline and the observed baseline is measured with error, the predictor 'predicts change'
even when nothing changes. Here the baseline partner measure has a 3-year retest of ~.2 and the predictor
comes from the same priming session.

(1) Cross-lagged symmetry: under 'both constructs stable, no influence', r(s1, p2) = r(p1, s2).
(2) Known answer: simulate stable latent S and P (no effect of S on change in P) with session-specific
    shared method factors, choose parameters that reproduce the observed correlation matrix of
    (s1, p1, s2, p2), and fit the paper's model p2 ~ p1 + s1 at n = 104. How often is s1 'significant',
    and what standardised coefficient does the null produce?
Usage: same .sav argument as r01. Writes out/r02.json."""
import json, os, sys, itertools, warnings
import numpy as np, pandas as pd, pyreadstat
import statsmodels.api as sm
warnings.filterwarnings("ignore")
df, _ = pyreadstat.read_sav(sys.argv[1])
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
x = df.rename(columns={"T1implictselfevaluation": "s1", "T1implictpartnerevaluation": "p1", "T2implictselfevaluation": "s2", "T2implictpartnerevaluation": "p2"})[["s1", "p1", "s2", "p2"]]
R = x.corr().values
res = {"observed_corr": x.corr().round(3).to_dict()}
print("observed correlations:\n", x.corr().round(3))
print(f"cross-lagged: r(s1,p2) = {R[0,3]:.3f} vs r(p1,s2) = {R[1,2]:.3f}")
res["cross_lagged"] = {"r_s1_p2": float(R[0, 3]), "r_p1_s2": float(R[1, 2])}
# observed standardised coefficient of s1
z = (x - x.mean()) / x.std()
ob = sm.OLS(z.p2, sm.add_constant(z[["p1", "s1"]])).fit()
res["observed_std_beta_s1"] = float(ob.params["s1"]); print(f"observed standardised beta(s1) = {ob.params['s1']:.3f} (p = {ob.pvalues['s1']:.4f}, OLS)")

# null model: s_t = a*S + m*M_t + e, p_t = b*P + m*M_t + e', corr(S,P)=rho, M_t independent across t
def implied(a, b, m, rho):
    vs = a*a + m*m + max(0, 1 - a*a - m*m); vp = vs  # standardised: residual variance fills to 1
    C = np.eye(4)
    C[0, 1] = C[1, 0] = a*b*rho + m*m      # s1,p1 same session
    C[2, 3] = C[3, 2] = a*b*rho + m*m      # s2,p2
    C[0, 2] = C[2, 0] = a*a                # s1,s2 stable S
    C[1, 3] = C[3, 1] = b*b                # p1,p2 stable P
    C[0, 3] = C[3, 0] = a*b*rho            # s1,p2
    C[1, 2] = C[2, 1] = a*b*rho            # p1,s2
    return C
best = None
for a, b, m, rho in itertools.product(np.linspace(.2, .9, 36), np.linspace(.2, .9, 36), np.linspace(0, .7, 36), np.linspace(0, 1, 21)):
    if a*a + m*m > 1 or b*b + m*m > 1: continue
    C = implied(a, b, m, rho)
    err = ((C - R)[np.triu_indices(4, 1)] ** 2).sum()
    if best is None or err < best[0]: best = (err, a, b, m, rho)
err, a, b, m, rho = best
res["null_fit"] = {"sse": float(err), "a": a, "b": b, "m": m, "rho": rho, "implied": implied(a, b, m, rho).round(3).tolist()}
print(f"best null fit: a={a:.2f} b={b:.2f} m={m:.2f} rho={rho:.2f} SSE={err:.4f}\n implied:\n", implied(a, b, m, rho).round(3))
rng = np.random.default_rng(9); hits = 0; betas = []; S_ = 4000; n = len(x)
for _ in range(S_):
    S = rng.standard_normal(n); P = rho * S + np.sqrt(1 - rho**2) * rng.standard_normal(n)
    M1, M2 = rng.standard_normal(n), rng.standard_normal(n)
    es = np.sqrt(max(1e-9, 1 - a*a - m*m)); ep = np.sqrt(max(1e-9, 1 - b*b - m*m))
    s1 = a*S + m*M1 + es*rng.standard_normal(n); p1 = b*P + m*M1 + ep*rng.standard_normal(n)
    p2 = b*P + m*M2 + ep*rng.standard_normal(n)
    X = sm.add_constant(np.c_[p1, s1]); f = sm.OLS(p2, X).fit()
    betas.append(f.params[2]); hits += f.pvalues[2] < .05 and f.params[2] > 0
res["null_sim"] = {"sims": S_, "share_positive_significant": hits / S_, "median_std_beta": float(np.median(betas)), "p95_std_beta": float(np.quantile(betas, .95))}
print(f"KNOWN ANSWER (no effect of S on change in P): s1 positive & p<.05 in {hits/S_:.3f}; median beta {np.median(betas):.3f}, 95th pct {np.quantile(betas,.95):.3f} vs observed {ob.params['s1']:.3f}")
# cross-lagged asymmetry: couple-cluster bootstrap of r(s1,p2) - r(p1,s2)
cid = df.CoupleID.values; cu = np.unique(cid); diffs = []
for _ in range(5000):
    pick = rng.choice(cu, len(cu), replace=True)
    idx = np.concatenate([np.where(cid == c)[0] for c in pick])
    xb = x.iloc[idx]
    diffs.append(np.corrcoef(xb.s1, xb.p2)[0, 1] - np.corrcoef(xb.p1, xb.s2)[0, 1])
diffs = np.array(diffs)
res["cross_lagged_diff_bootstrap"] = {"diff": float(R[0, 3] - R[1, 2]), "ci95": [float(np.quantile(diffs, .025)), float(np.quantile(diffs, .975))],
                                      "share_le_0": float((diffs <= 0).mean())}
print(f"cross-lagged difference {R[0,3]-R[1,2]:.3f}, couple-bootstrap 95% CI [{np.quantile(diffs,.025):.3f}, {np.quantile(diffs,.975):.3f}], share <= 0: {(diffs<=0).mean():.3f}")
with open(os.path.join(OUT, "r02.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(res, f, indent=1, default=float)
