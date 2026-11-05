"""Robustness of f01 and the known-answer ceiling.

(1) CEILING: if the SH model were the true data-generating process, outcomes would be Bernoulli(p_SH). Simulate that
    500 times on the real forecast vector: the AUC and calibration you would see if the model were right. If the real
    AUC (0.58) is far below this ceiling, the discrimination failure is real, not a property of the forecast spread.
(2) Robustness of f01's headline (SH: expected 638.5 vs observed 388; AUC .579):
    a. exact-p originals only / parsed-statistic originals only
    b. one replication per original (first effect_id), and weights 1/k per original
    c. drop n_r > 5,000 (mega-replications) and n_r/n_o > 20
    d. outcome = replicators' own verdict (reported_success == 'successful')
    e. originals significant only (|t_o| > 1.96)
Usage: python f02_robustness_and_ceiling.py <FReD_blinded.csv>   (re-runs f01's preparation)   Writes out/f02.json
"""
import json, os, runpy, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv = [os.path.join(HERE, "f01_forecast_out_of_sample.py"), sys.argv[1]]
_stdout = sys.stdout; sys.stdout = open(os.devnull, "w")
G = runpy.run_path(sys.argv[0])  # recomputes d, y, FC exactly as f01
sys.stdout = _stdout
d, y, FC, scores = G["d"], G["y"], G["FC"], G["scores"]
p_sig_pawel, ZC = G["p_sig_pawel"], G["ZC"]
rng = np.random.default_rng(5)
res = {}
from sklearn.metrics import roc_auc_score
for k in ("N", "SH", "SH_tau.2", "SA08"):
    p = FC[k]; aucs = []
    for _ in range(500):
        ys = (rng.random(len(p)) < p).astype(int); aucs.append(roc_auc_score(ys, p))
    res[f"ceiling_AUC_if_{k}_true"] = [round(float(np.quantile(aucs, q)), 3) for q in (.025, .5, .975)]
    res[f"real_AUC_{k}"] = round(float(roc_auc_score(y, p)), 3)


def sub(mask, label, yy=None, wts=None):
    yy = y if yy is None else yy
    out = {}
    for k in ("N", "SH", "SH_tau.2", "SA08"):
        p = FC[k][mask]; t = yy[mask]
        if wts is None:
            s = scores(p, t)
        else:
            w = wts[mask]; s = {"n_eff_originals": round(float(w.sum()), 1), "observed_w": round(float((w * t).sum()), 1), "expected_w": round(float((w * p).sum()), 1),
                                "AUC_w": round(float(roc_auc_score(t, p, sample_weight=w)), 3)}
        out[k] = s
    res[label] = out
    print(label, {k: {kk: vv for kk, vv in v.items() if kk in ("n", "observed", "expected", "AUC", "BS", "n_eff_originals", "observed_w", "expected_w", "AUC_w")} for k, v in out.items()})


allm = np.ones(len(d), bool)
sub(d.p_o_source.values == "exact_p", "a_exact_p_only")
sub(d.p_o_source.values == "parsed_stat", "a_parsed_stat_only")
cl = d.doi_o.fillna(d.ref_o).astype(str).values
first = ~d.assign(_c=cl).duplicated("_c").values
sub(first, "b_first_replication_per_original")
k_per = d.assign(_c=cl).groupby("_c")["_c"].transform("size").values
sub(allm, "b_weight_1_over_k", wts=1.0 / k_per)
sub((d.n_r.values <= 5000) & ((d.n_r / d.n_o).values <= 20), "c_drop_mega_and_ratio>20")
sub(allm, "d_outcome_reported_successful", yy=(d.reported_success.values == "successful").astype(int))
sub(d.to_abs.values > ZC, "e_significant_originals_only")
res["share_pairs_from_originals_with_k>1"] = round(float(np.mean(k_per > 1)), 3)
res["max_k"] = int(k_per.max())
print({k: v for k, v in res.items() if k.startswith(("ceiling", "real", "share", "max"))})
json.dump(res, open(os.path.join(HERE, "out", "f02.json"), "w"), indent=1)
