"""Joel, Teper & MacDonald (2014) -- reproduce Studies 1 and 2 from the OSF deposit (osf.io/873fp).

Usage (from the zoo root):
  python zoo-knowledge-base/instance-papers/papers/joel2014-overestimate-rejecting-partners/reanalysis/r01_reproduce.py \
     "$(python zoo-knowledge-base/tools/assets.py path paper-downloads/joel2014-overestimate-rejecting-partners)/osf_873fp/files/osfstorage"
Writes out/r01.json.
"""
import json, os, sys, warnings
import numpy as np, pandas as pd, pyreadstat
from scipy import stats
import statsmodels.api as sm
warnings.filterwarnings("ignore")
D = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"); os.makedirs(OUT, exist_ok=True)
res = {}

def chi2(tab):
    c, p, _, _ = stats.chi2_contingency(tab, correction=False); return float(c), float(p)

def mediation(df, cond, meds, dv_reject, B=5000, seed=1):
    """PROCESS-style: a paths OLS, b and c' from one logistic model, indirect = a*b, bootstrap (percentile & BCa)."""
    rng = np.random.default_rng(seed)
    def est(d):
        a = [sm.OLS(d[m], sm.add_constant(d[[cond]])).fit().params[cond] for m in meds]
        lg = sm.Logit(d[dv_reject], sm.add_constant(d[[cond] + meds])).fit(disp=0)
        b = [lg.params[m] for m in meds]
        return np.array([ai * bi for ai, bi in zip(a, b)] + [sum(ai * bi for ai, bi in zip(a, b))]), a, b, lg.params[cond]
    th, a, b, cp = est(df)
    c = sm.Logit(df[dv_reject], sm.add_constant(df[[cond]])).fit(disp=0).params[cond]
    boots = []
    n = len(df)
    for _ in range(B):
        try:
            boots.append(est(df.iloc[rng.integers(0, n, n)])[0])
        except Exception:
            pass
    boots = np.array(boots)
    # BCa
    from statistics import NormalDist
    N = NormalDist()
    jack = np.array([est(df.drop(df.index[i]))[0] for i in range(n)])
    out = {}
    for j in range(len(th)):
        z0 = N.inv_cdf(min(max((boots[:, j] < th[j]).mean(), 1e-6), 1 - 1e-6))
        jm = jack[:, j].mean(); acc = ((jm - jack[:, j]) ** 3).sum() / (6 * (((jm - jack[:, j]) ** 2).sum()) ** 1.5)
        lo = N.cdf(z0 + (z0 + N.inv_cdf(.025)) / (1 - acc * (z0 + N.inv_cdf(.025))))
        hi = N.cdf(z0 + (z0 + N.inv_cdf(.975)) / (1 - acc * (z0 + N.inv_cdf(.975))))
        out[(meds + ["total"])[j]] = {"indirect": float(th[j]), "boot_se": float(boots[:, j].std(ddof=1)),
                                      "bca": [float(np.quantile(boots[:, j], lo)), float(np.quantile(boots[:, j], hi))],
                                      "pct": [float(np.quantile(boots[:, j], .025)), float(np.quantile(boots[:, j], .975))]}
    return {"a": [float(v) for v in a], "b": [float(v) for v in b], "c": float(c), "c_prime": float(cp), "indirect": out, "B": len(boots)}

# ================================ Study 1 ===========================================================
s1, m1 = pyreadstat.read_sav(os.path.join(D, "Empathy Gap Study 1 data.sav"))
r = {"n_rows": len(s1), "gender": s1.gender.value_counts(dropna=False).to_dict(),
     "age_mean_sd_min_max": [float(s1.age.mean()), float(s1.age.std()), float(s1.age.min()), float(s1.age.max())]}
s1["reject"] = (s1.exchangeinfo == 2).astype(int)
tab = pd.crosstab(s1.condition, s1.exchangeinfo)
r["exchange_by_condition(rows 0=hyp,1=real; cols 1=yes,2=no)"] = tab.values.tolist()
r["chi2_p"] = chi2(tab.values)
pa = s1[["selfattractive", "otherattractive"]].dropna()
t = stats.ttest_rel(pa.otherattractive, pa.selfattractive)
r["attractiveness_paired"] = {"n_pairs": len(pa), "M_other": float(pa.otherattractive.mean()), "M_self": float(pa.selfattractive.mean()), "t": float(t.statistic), "df": len(pa) - 1}
# composites: rebuild from items to check the deposit's composite
oth_items = [f"{p}{i}" for i in (2, 4, 6, 8) for p in ("reasontrue", "motives")]
self_items = [f"{p}{i}" for i in (1, 3, 5, 7) for p in ("reasontrue", "motives")]
r["out_of_range_item_values(1-5 scale)"] = {c: s1.loc[(s1[c] > 5) | (s1[c] < 1), c].tolist() for c in oth_items + self_items if ((s1[c] > 5) | (s1[c] < 1)).any()}
r["composite_rebuild_max_abs_diff"] = {"other": float((s1[oth_items].mean(1) - s1.otherfocused_motives).abs().max()),
                                       "self": float((s1[self_items].mean(1) - s1.selffocused_motives).abs().max())}
for v in ("otherfocused_motives", "selffocused_motives"):
    g = [s1.loc[s1.condition == k, v] for k in (0, 1)]
    F = stats.f_oneway(*g)
    r[v] = {"hyp_M_SD": [float(g[0].mean()), float(g[0].std())], "real_M_SD": [float(g[1].mean()), float(g[1].std())], "F": float(F.statistic), "p": float(F.pvalue)}
# Wilks MANOVA (2 DVs, 2 groups) == Hotelling T2
from statsmodels.multivariate.manova import MANOVA
mv = MANOVA.from_formula("otherfocused_motives + selffocused_motives ~ C(condition)", s1).mv_test()
r["manova_wilks_F_p"] = [float(mv.results["C(condition)"]["stat"].loc["Wilks' lambda", "F Value"]), float(mv.results["C(condition)"]["stat"].loc["Wilks' lambda", "Pr > F"])]
r["mediation"] = mediation(s1.dropna(subset=["condition", "reject", "otherfocused_motives", "selffocused_motives"]).reset_index(drop=True),
                           "condition", ["otherfocused_motives", "selffocused_motives"], "reject")
res["study1"] = r
print("STUDY 1", json.dumps({k: v for k, v in r.items() if k != "mediation"}, default=float))
print("  mediation:", json.dumps(r["mediation"], default=float))
print("  paper: 10/61 vs 26/71, chi2 6.77 p .009; t(103)=6.77 (4.48 vs 6.08); MANOVA F(2,129)=4.85 p .009; other 2.62/1.00 vs 3.12/1.05 F 7.82;"
      " self 2.21/.71 vs 2.50/.79 F 4.77; indirect other -.2928 [-.7994,-.0111], self -.5076 [-1.2404,.0140], total -.8005 [-1.6751,-.1533]")

# ================================ Study 2 ===========================================================
s2, m2 = pyreadstat.read_sav(os.path.join(D, "Empathy_Gap_Study_2_data.sav"))
r = {"n_rows": len(s2), "condition_value_labels_in_file": {str(k): v for k, v in m2.variable_value_labels.get("condition", {}).items()},
     "condition_values_present": s2.condition.value_counts(dropna=False).to_dict()}
d2 = s2.dropna(subset=["exchange.contact", "condition"]).copy()
d2["reject"] = (d2["exchange.contact"] == 2).astype(int)
tab = pd.crosstab(d2.condition, d2["exchange.contact"])
r["n_analysed"] = len(d2)
r["exchange_by_condition"] = tab.values.tolist()
r["chi2_p"] = chi2(tab.values)
r["gender_analysed"] = d2.gender.value_counts().to_dict()
r["age_mean_sd"] = [float(d2.age.mean()), float(d2.age.std())]
r["motive_item_scale_max"] = float(s2[[c for c in s2.columns if c.startswith(("reasontrue", "motives"))]].max().max())
for v in ("otherfocused_motives", "selffocused_motives"):
    g = [d2.loc[d2.condition == k, v] for k in (0, 1)]
    F = stats.f_oneway(*g)
    r[v] = {"cond0_M_SD": [float(g[0].mean()), float(g[0].std())], "cond1_M_SD": [float(g[1].mean()), float(g[1].std())], "F": float(F.statistic), "p": float(F.pvalue)}
mv = MANOVA.from_formula("otherfocused_motives + selffocused_motives ~ C(condition)", d2).mv_test()
r["manova_wilks_F_p"] = [float(mv.results["C(condition)"]["stat"].loc["Wilks' lambda", "F Value"]), float(mv.results["C(condition)"]["stat"].loc["Wilks' lambda", "Pr > F"])]
r["mediation"] = mediation(d2.reset_index(drop=True), "condition", ["otherfocused_motives"], "reject")
res["study2"] = r
print("STUDY 2", json.dumps({k: v for k, v in r.items() if k != "mediation"}, default=float))
print("  mediation:", json.dumps(r["mediation"], default=float))
print("  paper: N=99 (31 M, 68 F), 24/52 hyp vs 35/47 real, chi2 8.22 p .004; MANOVA F(2,96)=3.71; other 3.70/1.42 vs 4.49/1.45 F 7.39;"
      " self 3.81/1.41 vs 4.03/1.14 F .70; indirect -.20 (SE .15) BCa [-.57,.04]; a .79 b -.25 c -1.22 c' -1.06")
with open(os.path.join(OUT, "r01.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(res, f, indent=1, default=float)
