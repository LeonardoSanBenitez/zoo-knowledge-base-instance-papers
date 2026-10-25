"""Break test: the 'mediator' (motives for agreeing to meet) was measured AFTER the decision.

(1) Within each decision group, does condition still move other-focused motives? If the a-path exists only
    because the real condition contains more acceptors (37% vs 16% in Study 1), it should vanish within groups.
(2) Known answer. Simulate a world with NO mediation: condition changes only the decision (at the observed
    rates); motives are then reported as a function of the decision alone (post-hoc rationalisation, with the
    observed acceptor/rejecter means and SDs). Run the paper's mediation procedure. A procedure that can
    tell mediation from rationalisation should find an indirect effect ~5% of the time. If it finds one
    most of the time, the paper's mediation result cannot discriminate the two accounts.
Usage: same argument as r01. Writes out/r02.json.
"""
import json, os, sys, warnings
import numpy as np, pandas as pd, pyreadstat
import statsmodels.api as sm, statsmodels.formula.api as smf
warnings.filterwarnings("ignore")
D = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
res = {}

s1, _ = pyreadstat.read_sav(os.path.join(D, "Empathy Gap Study 1 data.sav"))
s1["accept"] = (s1.exchangeinfo == 1).astype(int)
s2, _ = pyreadstat.read_sav(os.path.join(D, "Empathy_Gap_Study_2_data.sav"))
s2 = s2.dropna(subset=["exchange.contact", "condition"]).copy(); s2["accept"] = (s2["exchange.contact"] == 1).astype(int)

for name, d in (("study1", s1), ("study2", s2)):
    r = {}
    for v in ("otherfocused_motives", "selffocused_motives"):
        g = d.groupby(["accept", "condition"])[v].agg(["mean", "std", "count"]).round(3)
        r[f"{v}_by_decision_x_condition"] = {f"accept={a},cond={c}": row.tolist() for (a, c), row in g.iterrows()}
        m = smf.ols(f"{v} ~ condition + accept", d).fit()
        m0 = smf.ols(f"{v} ~ condition", d).fit()
        r[f"{v}_condition_coef_without_vs_with_decision"] = {"without": [float(m0.params["condition"]), float(m0.pvalues["condition"])],
                                                            "with_decision": [float(m.params["condition"]), float(m.pvalues["condition"])],
                                                            "decision_coef": [float(m.params["accept"]), float(m.pvalues["accept"])]}
        dm = smf.ols(f"{v} ~ accept", d).fit()
        r[f"{v}_accept_minus_reject_d"] = float(dm.params["accept"] / np.sqrt(dm.mse_resid))
    res[name] = r
    print(f"\n== {name}")
    for k, v in r.items():
        print(" ", k, v)

# ---- known-answer simulation (Study 1 structure) ----------------------------------------------------
rng = np.random.default_rng(3)
d = s1.dropna(subset=["condition", "accept", "otherfocused_motives"])
p_acc = d.groupby("condition").accept.mean().to_dict()              # 0.16 hyp, 0.37 real
mu = d.groupby("accept").otherfocused_motives.mean().to_dict(); sd = d.groupby("accept").otherfocused_motives.std().to_dict()
n0, n1 = int((d.condition == 0).sum()), int((d.condition == 1).sum())
def one_dataset(p_acc, mu, sd):
    cond = np.r_[np.zeros(n0), np.ones(n1)]
    acc = rng.random(len(cond)) < np.where(cond == 1, p_acc[1], p_acc[0])
    mot = np.clip(rng.normal(np.where(acc, mu[1], mu[0]), np.where(acc, sd[1], sd[0])), 1, 5)
    return pd.DataFrame({"condition": cond, "reject": (~acc).astype(int), "mot": mot})
def indirect_ci(df, B=500):
    def est(x):
        a = sm.OLS(x.mot, sm.add_constant(x[["condition"]])).fit().params["condition"]
        b = sm.Logit(x.reject, sm.add_constant(x[["condition", "mot"]])).fit(disp=0).params["mot"]
        return a * b
    th = est(df); bs = []
    for _ in range(B):
        try: bs.append(est(df.iloc[rng.integers(0, len(df), len(df))]))
        except Exception: pass
    lo, hi = np.quantile(bs, [.025, .975])
    return th, lo, hi
sims = 300; hits = 0; ths = []
for _ in range(sims):
    th, lo, hi = indirect_ci(one_dataset(p_acc, mu, sd))
    ths.append(th); hits += (hi < 0) or (lo > 0)
res["known_answer_rationalisation_only"] = {"sims": sims, "boot_B": 500, "rate_indirect_CI_excludes_0": hits / sims,
                                             "median_indirect": float(np.median(ths)), "observed_indirect_study1": -0.2928,
                                             "inputs": {"p_accept_by_cond": p_acc, "motive_mean_by_decision": mu, "motive_sd_by_decision": sd}}
print(f"\nKNOWN ANSWER (no mediation; motives caused by the decision only): indirect CI excludes 0 in {hits}/{sims} = {hits/sims:.2f}; "
      f"median simulated indirect {np.median(ths):.3f} vs observed -0.293")
with open(os.path.join(OUT, "r02.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(res, f, indent=1, default=float)
