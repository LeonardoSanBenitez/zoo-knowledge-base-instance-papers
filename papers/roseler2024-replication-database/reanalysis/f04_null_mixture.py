"""A two-class reading of FReD: a share pi of replicated originals have true effect ~ 0 (replication succeeds with
P = .025, the one-directional false-positive rate), the rest behave as Pawel-Held SH predicts (tau free).
Fit (pi, tau) by maximum likelihood on the replication outcomes -- NOTE: this one IS fitted on outcomes, so it is
in-sample, unlike everything in f01/f02. It answers a descriptive question (what null share would make the outcomes
coherent?), not a forecasting one.

Known-answer checks of the reading: under each fitted / reference world, simulate outcomes 500x and record the AUC of
log(n_r/n_o) ALONE. Real FReD: 0.472. If the null-mixture world reproduces ~0.47 while the SH world gives >> .5, the
mixture explains why replication size carries no signal.
Usage: python f04_null_mixture.py <FReD_blinded.csv>   Writes out/f04.json
"""
import json, os, runpy, sys
import numpy as np
from scipy import optimize
from sklearn.metrics import roc_auc_score
HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv = [os.path.join(HERE, "f01_forecast_out_of_sample.py"), sys.argv[1]]
_o = sys.stdout; sys.stdout = open(os.devnull, "w"); G = runpy.run_path(sys.argv[0]); sys.stdout = _o
d, y, p_sig_pawel, scores = G["d"], G["y"], G["p_sig_pawel"], G["scores"]
to_abs, so, sr = d.to_abs.values, d.so.values, d.sr.values
c = so ** 2 / sr ** 2; logc = np.log(d.n_r.values / d.n_o.values)
cl = d.doi_o.fillna(d.ref_o).astype(str).values


def p_mix(pi, tau):
    return pi * 0.025 + (1 - pi) * p_sig_pawel(to_abs, c, tau ** 2 / so ** 2, "SH")


def nll(par):
    pi, tau = 1 / (1 + np.exp(-par[0])), np.exp(par[1])
    p = np.clip(p_mix(pi, tau), 1e-6, 1 - 1e-6)
    return -np.sum(y * np.log(p) + (1 - y) * np.log(1 - p))


best = min((optimize.minimize(nll, [a, b], method="Nelder-Mead") for a in (-1, 0, 1) for b in (-3, -2, -1)), key=lambda r: r.fun)
pi_hat, tau_hat = 1 / (1 + np.exp(-best.x[0])), float(np.exp(best.x[1]))
# tau-only model (pi = 0) for comparison
b0 = optimize.minimize_scalar(lambda lt: nll([-30, lt]), bounds=(-6, 1), method="bounded")
res = {"pi_hat_null_share": round(float(pi_hat), 3), "tau_hat": round(tau_hat, 3), "nll_mixture": round(float(best.fun), 2),
       "tau_only_tau_hat": round(float(np.exp(b0.x)), 3), "nll_tau_only": round(float(b0.fun), 2)}
res["scores_mixture_in_sample"] = scores(p_mix(pi_hat, tau_hat), y)
res["scores_tau_only_in_sample"] = scores(p_mix(0.0, float(np.exp(b0.x))), y)
# cluster bootstrap of pi_hat
rng = np.random.default_rng(9); u = np.unique(cl); pos = {k: np.where(cl == k)[0] for k in u}
pis = []
for _ in range(200):
    take = np.concatenate([pos[k] for k in rng.choice(u, len(u))])
    def nllb(par):
        pi, tau = 1 / (1 + np.exp(-par[0])), np.exp(par[1])
        p = np.clip(pi * 0.025 + (1 - pi) * p_sig_pawel(to_abs[take], c[take], tau ** 2 / so[take] ** 2, "SH"), 1e-6, 1 - 1e-6)
        return -np.sum(y[take] * np.log(p) + (1 - y[take]) * np.log(1 - p))
    r = optimize.minimize(nllb, best.x, method="Nelder-Mead"); pis.append(1 / (1 + np.exp(-r.x[0])))
res["pi_hat_cluster_boot_95ci"] = [round(float(np.quantile(pis, q)), 3) for q in (.025, .975)]
# known-answer: AUC of log c alone under each world
worlds = {"SH_tau.08_true": p_sig_pawel(to_abs, c, 0.08 ** 2 / so ** 2, "SH"), "tau_only_fitted": p_mix(0.0, float(np.exp(b0.x))),
          "null_mixture_fitted": p_mix(pi_hat, tau_hat)}
for k, p in worlds.items():
    a = [roc_auc_score((rng.random(len(p)) < p).astype(int), logc) for _ in range(500)]
    res[f"AUC_logc_alone_if_{k}"] = [round(float(np.quantile(a, q)), 3) for q in (.025, .5, .975)]
res["AUC_logc_alone_real"] = round(float(roc_auc_score(y, logc)), 3)
print(json.dumps(res, indent=1))
json.dump(res, open(os.path.join(HERE, "out", "f04.json"), "w"), indent=1)
