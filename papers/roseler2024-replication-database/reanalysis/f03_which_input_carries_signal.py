"""Which of the forecast's inputs carries information about replication success in FReD?

The Pawel-Held forecast is a function of two things: |t_o| (evidence in the original) and c = n_r/n_o (how much
bigger the replication is). The model says both raise P(success). Here each input is scored alone (AUC, and success
rate by quintile), then jointly in a logistic regression, with original-clustered bootstrap CIs.
Usage: python f03_which_input_carries_signal.py <FReD_blinded.csv>   Writes out/f03.json
"""
import json, os, runpy, sys
import numpy as np, pandas as pd
import statsmodels.api as sm
from sklearn.metrics import roc_auc_score
HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv = [os.path.join(HERE, "f01_forecast_out_of_sample.py"), sys.argv[1]]
_o = sys.stdout; sys.stdout = open(os.devnull, "w"); G = runpy.run_path(sys.argv[0]); sys.stdout = _o
d, y = G["d"], G["y"]
d = d.assign(y=y, log_to=np.log(d.to_abs.clip(lower=0.05)), log_c=np.log(d.n_r / d.n_o), log_nr=np.log(d.n_r), log_no=np.log(d.n_o))
cl = d.doi_o.fillna(d.ref_o).astype(str).values
res = {}
for v in ("to_abs", "log_c", "log_nr", "log_no"):
    res[f"AUC_{v}_alone"] = round(float(roc_auc_score(d.y, d[v])), 3)
    q = pd.qcut(d[v], 5, labels=False, duplicates="drop")
    res[f"success_by_quintile_{v}"] = [round(float(d.y[q == i].mean()), 3) for i in range(int(q.max()) + 1)]
X = sm.add_constant(d[["log_to", "log_c"]]); m = sm.Logit(d.y, X).fit(disp=0, cov_type="cluster", cov_kwds={"groups": pd.factorize(cl)[0]})
res["logit_log_to_log_c"] = {k: [round(float(m.params[k]), 3), round(float(m.bse[k]), 3), round(float(m.pvalues[k]), 4)] for k in m.params.index}
X2 = sm.add_constant(d[["log_to", "log_no", "log_nr"]]); m2 = sm.Logit(d.y, X2).fit(disp=0, cov_type="cluster", cov_kwds={"groups": pd.factorize(cl)[0]})
res["logit_log_to_log_no_log_nr"] = {k: [round(float(m2.params[k]), 3), round(float(m2.bse[k]), 3), round(float(m2.pvalues[k]), 4)] for k in m2.params.index}
res["model_says"] = "both log_to and log_c coefficients positive and large (P(success) -> 1 as c grows for any t_o > 1.96)"
print(json.dumps(res, indent=1))
json.dump(res, open(os.path.join(HERE, "out", "f03.json"), "w"), indent=1)
