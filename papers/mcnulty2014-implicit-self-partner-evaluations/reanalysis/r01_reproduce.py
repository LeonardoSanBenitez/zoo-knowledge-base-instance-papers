"""McNulty, Baker & Olson (2014) -- reproduce Tables 1-3 from the OSF deposit (hdi8p, McNultyBakerOlson2014.sav)
and probe the key result (implicit self-evaluation -> change in implicit partner evaluation).

Usage (from the zoo root):
  python zoo-knowledge-base/instance-papers/papers/mcnulty2014-implicit-self-partner-evaluations/reanalysis/r01_reproduce.py \
    "$(python zoo-knowledge-base/tools/assets.py path paper-downloads/mcnulty2014-implicit-self-partner-evaluations)/osf_hdi8p/files/osfstorage/McNultyBakerOlson2014.sav"
Writes out/r01.json.
"""
import json, os, sys, warnings
import numpy as np, pandas as pd, pyreadstat
from scipy import stats
import statsmodels.formula.api as smf
warnings.filterwarnings("ignore")
df, meta = pyreadstat.read_sav(sys.argv[1])
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"); os.makedirs(OUT, exist_ok=True)
ren = {"T1implictselfevaluation": "s1", "T1implictpartnerevaluation": "p1", "T2implictselfevaluation": "s2", "T2implictpartnerevaluation": "p2",
       "T1reactiontimetopositivewords": "rp1", "T1reactiontimetonegativewords": "rn1", "T2reactiontimetopositivewords": "rp2", "T2reactiontimetonegativewords": "rn2",
       "T1explcitselfevaluation": "es1", "T2explcitselfevaluation": "es2", "T1explcitmaritalsatisfaction": "ms1", "T2explcitmaritalsatisfaction": "ms2",
       "T1explcitpartnerevaluation": "ep1", "T2explcitpartnerevaluation": "ep2", "T1implictevaluationofoppsexstrangers": "o1", "T2implictevaluationofoppsexstrangers": "o2"}
d = df.rename(columns=ren)
res = {"n_rows": len(d), "n_couples": int(d.CoupleID.nunique()), "sex_counts": d.sex.value_counts().to_dict()}

# Table 2: means (SD) at both waves
t2 = {}
for a, b, lab in (("ms1", "ms2", "marital_satisfaction"), ("ep1", "ep2", "explicit_partner"), ("p1", "p2", "implicit_partner"), ("es1", "es2", "explicit_self"), ("s1", "s2", "implicit_self")):
    t2[lab] = {"T1": [round(d[a].mean(), 2), round(d[a].std(), 2)], "T2": [round(d[b].mean(), 2), round(d[b].std(), 2)], "raw_change": round((d[b] - d[a]).mean(), 2)}
    # change: random-intercept model on the difference (implicit: + orientation RTs, as described)
    d["_diff"] = d[b] - d[a]
    f = "_diff ~ 1" + (" + rp1 + rn1 + rp2 + rn2" if lab.startswith("implicit") else "")
    m = smf.mixedlm(f, d, groups=d.CoupleID).fit(reml=True)
    t2[lab]["mlm_intercept"] = [round(float(m.params["Intercept"]), 2), round(float(m.tvalues["Intercept"]), 2)]
    if lab.startswith("implicit"):
        dc = d.copy()
        for c in ("rp1", "rn1", "rp2", "rn2"): dc[c] = dc[c] - dc[c].mean()
        mc = smf.mixedlm(f, dc, groups=dc.CoupleID).fit(reml=True)
        t2[lab]["mlm_intercept_rt_centred"] = [round(float(mc.params["Intercept"]), 2), round(float(mc.tvalues["Intercept"]), 2)]
    # test-retest: standardised T2 on standardised T1, random intercept (+ RTs for implicit)
    z = d.copy(); z["zA"] = stats.zscore(z[a]); z["zB"] = stats.zscore(z[b])
    mt = smf.mixedlm("zB ~ zA" + (" + rp1 + rn1 + rp2 + rn2" if lab.startswith("implicit") else ""), z, groups=z.CoupleID).fit(reml=True)
    t2[lab]["test_retest_beta_p"] = [round(float(mt.params["zA"]), 3), round(float(mt.pvalues["zA"]), 4)]
res["table2"] = t2
print("Table 2 recount (T1 M,SD | T2 M,SD | raw change | MLM change intercept, t | test-retest beta, p):")
for k, v in t2.items(): print(f"  {k:22s}", v)
print("paper T2 row values: implicit partner 49.24 (74.74) -> 35.67 (62.83), change -16.74; implicit self 61.99 (80.01) -> 35.67 (62.83) [same cell as partner], change -26.32; test-retest .20*, .06")

# Table 3
t3 = {}
for selfv in ("es1", "s1"):
    for a, b in (("ms1", "ms2"), ("ep1", "ep2"), ("p1", "p2")):
        m = smf.mixedlm(f"{b} ~ {a} + {selfv}", d, groups=d.CoupleID).fit(reml=True)
        t3[f"{b}~{a}+{selfv}"] = {"B_self": round(float(m.params[selfv]), 3), "SE": round(float(m.bse[selfv]), 3), "p": round(float(m.pvalues[selfv]), 4),
                                 "B_base": round(float(m.params[a]), 3)}
res["table3"] = t3
print("\nTable 3 recount:")
for k, v in t3.items(): print(f"  {k:22s}", v)
print("paper: implicit self -> implicit partner B .26 SE .10 (r .35); all other self coefficients n.s.")
pvals = [v["p"] for v in t3.values()]
from statsmodels.stats.multitest import multipletests
res["holm_adjusted_p_6_tests"] = [round(float(x), 4) for x in multipletests(pvals, method="holm")[1]]
print("Holm-adjusted p over the 6 self->relationship tests:", res["holm_adjusted_p_6_tests"])

# robustness of the key coefficient
key = "p2 ~ p1 + s1"
rob = {}
z = d.copy()
for c in ("s1", "p1", "p2"):
    q1, q99 = z[c].quantile([.05, .95]); z[c + "_w"] = z[c].clip(q1, q99)
rob["winsorised_5_95"] = float(smf.mixedlm("p2_w ~ p1_w + s1_w", z, groups=z.CoupleID).fit(reml=True).pvalues["s1_w"])
rk = d.copy()
for c in ("s1", "p1", "p2"): rk[c] = rk[c].rank()
rob["rank_based"] = float(smf.mixedlm(key, rk, groups=rk.CoupleID).fit(reml=True).pvalues["s1"])
ols = smf.ols(key, d).fit(cov_type="cluster", cov_kwds={"groups": d.CoupleID})
infl = smf.ols(key, d).fit().get_influence().cooks_distance[0]
top = np.argsort(infl)[::-1][:5]
rob["ols_cluster_p"] = float(ols.pvalues["s1"])
rob["drop_top5_cooks_p"] = float(smf.mixedlm(key, d.drop(d.index[top]), groups=d.drop(d.index[top]).CoupleID).fit(reml=True).pvalues["s1"])
loo = []
for cid in d.CoupleID.unique():
    dd = d[d.CoupleID != cid]
    loo.append(float(smf.ols(key, dd).fit().pvalues["s1"]))
rob["leave_one_couple_out_p_max"] = max(loo)
rob["s1_p1_baseline_r"] = float(np.corrcoef(d.s1, d.p1)[0, 1])
rob["p1_p2_r"] = float(np.corrcoef(d.p1, d.p2)[0, 1]); rob["s1_s2_r"] = float(np.corrcoef(d.s1, d.s2)[0, 1])
rob["o1_max"] = float(d.o1.max()); rob["o1_n_abs_gt_500"] = int((d.o1.abs() > 500).sum())
res["robustness"] = rob
print("\nkey coefficient robustness (p-values):", {k: round(v, 4) if isinstance(v, float) else v for k, v in rob.items()})

# full-covariate model as described in the paper (t(24))
cov = "p2 ~ p1 + s1 + sex + s2 + es1 + es2 + rp1 + rn1 + rp2 + rn2 + ms1 + ms2 + ep1 + ep2 + o1 + o2 + T1attachmentanxiety + T1attachmentavoidance + T1extraversion + T1agreeableness + T1conscientiousness + T1neuroticism + T1openness + T1depression"
mf = smf.mixedlm(cov, d, groups=d.CoupleID).fit(reml=True)
res["full_covariate_model"] = {"B_s1": float(mf.params["s1"]), "SE": float(mf.bse["s1"]), "p": float(mf.pvalues["s1"]), "n_predictors": cov.count("+") + 1}
print("full-covariate model (paper B .30 SE .10 t(24)=3.00):", {k: round(v, 3) for k, v in res["full_covariate_model"].items()})
with open(os.path.join(OUT, "r01.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(res, f, indent=1, default=float)
