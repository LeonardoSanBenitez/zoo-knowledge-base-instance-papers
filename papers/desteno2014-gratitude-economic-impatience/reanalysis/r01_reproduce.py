"""DeSteno, Li, Dickens & Lerner (2014) -- reproduce every reported statistic from the Dataverse deposit
(doi:10.7910/DVN/24885 v1.0), then refit the discount factors from the raw choices.

Usage (from the zoo root):
  python zoo-knowledge-base/instance-papers/papers/desteno2014-gratitude-economic-impatience/reanalysis/r01_reproduce.py \
     "$(python zoo-knowledge-base/tools/assets.py path paper-downloads/desteno2014-gratitude-economic-impatience)/dataverse_24885/files"
Writes out/r01.json and out/participants_refit.csv.
"""
import json, os, sys, warnings
import numpy as np, pandas as pd
from scipy import stats, optimize
import statsmodels.formula.api as smf
warnings.filterwarnings("ignore")

D = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)
res = {}

x = pd.read_excel(os.path.join(D, "Gratitude_Discounting_PsycSci.xlsx"))
try:
    import pyreadstat
    s, meta = pyreadstat.read_sav(os.path.join(D, "Gratitude_Discounting_PsycSci.tab"))
    s.columns = [c.lower() for c in s.columns]
    xl = x.copy(); xl.columns = [c.lower() for c in xl.columns]
    common = [c for c in xl.columns if c in s.columns]
    diff = {c: int((~np.isclose(pd.to_numeric(xl[c], errors="coerce").fillna(-999).values,
                                 pd.to_numeric(s[c], errors="coerce").fillna(-999).values, atol=1e-6)).sum())
            for c in common}
    res["xlsx_vs_sav_cells_differing"] = {k: v for k, v in diff.items() if v}
    print("xlsx vs SPSS (.tab is an SPSS file): columns compared", len(common), "differing:", res["xlsx_vs_sav_cells_differing"])
except Exception as e:
    print("sav read failed:", e)

cond = x["Condition"].map({1: "Neutral", 2: "Gratitude", 3: "Happiness"})
x["cond"] = cond
res["n_by_condition"] = cond.value_counts().to_dict()
res["gender_counts(1=men,2=women)"] = x["gender"].value_counts().to_dict()
res["age"] = {"mean": float(x["age"].mean()), "min": float(x["age"].min()), "max": float(x["age"].max())}
print("N", len(x), res["n_by_condition"], "gender", res["gender_counts(1=men,2=women)"], "age", res["age"])

# indices
gi = x[["grateful", "appreciative", "thankful"]].mean(1); hi = x[["happy", "content", "pleasan"]].mean(1)
res["GratIndex_matches_deposit_max_abs_diff"] = float((gi - x["GratIndex"]).abs().max())
res["HapIndex_matches_deposit_max_abs_diff"] = float((hi - x["HapIndex"]).abs().max())
def alpha(df):
    k = df.shape[1]; return k / (k - 1) * (1 - df.var(ddof=1).sum() / df.sum(1).var(ddof=1))
res["alpha_gratitude"] = alpha(x[["grateful", "appreciative", "thankful"]])
res["alpha_happiness"] = alpha(x[["happy", "content", "pleasan"]])
res["r_grat_hap"] = float(np.corrcoef(x["GratIndex"], x["HapIndex"])[0, 1])
print(f"alpha grat {res['alpha_gratitude']:.3f} (paper .92)  alpha hap {res['alpha_happiness']:.3f} (paper .74)  r {res['r_grat_hap']:.3f} (paper .57)")

# manipulation check: target-emotion means
tgt = np.where(x.cond == "Gratitude", x.GratIndex, np.where(x.cond == "Happiness", x.HapIndex, np.nan))
for c, col in (("Gratitude", "GratIndex"), ("Happiness", "HapIndex")):
    v = x.loc[x.cond == c, col]; res[f"manip_{c}_{col}_mean_sd"] = [float(v.mean()), float(v.std(ddof=1))]
neu = x.loc[x.cond == "Neutral"]
res["manip_neutral_mean_of_both_indices_mean_sd"] = [float(((neu.GratIndex + neu.HapIndex) / 2).mean()), float(((neu.GratIndex + neu.HapIndex) / 2).std(ddof=1))]
res["manip_neutral_GratIndex_mean_sd"] = [float(neu.GratIndex.mean()), float(neu.GratIndex.std(ddof=1))]
res["manip_neutral_HapIndex_mean_sd"] = [float(neu.HapIndex.mean()), float(neu.HapIndex.std(ddof=1))]
print("manip:", {k: [round(a, 2) for a in v] for k, v in res.items() if k.startswith("manip")}, "(paper: grat 4.47/.38, hap 4.11/.72, neutral 3.17/.84)")

# 3x2 mixed ANOVA interaction (condition between, emotion within): equivalent to one-way ANOVA on the difference
dlt = x.GratIndex - x.HapIndex
F, p = stats.f_oneway(*[dlt[x.cond == c] for c in ("Neutral", "Gratitude", "Happiness")])
res["manip_interaction_F(2,72)"] = [float(F), float(p)]
# focused ANCOVAs
gh = x[x.cond.isin(["Gratitude", "Happiness"])].copy(); gh["g"] = (gh.cond == "Gratitude").astype(int)
m1 = smf.ols("GratIndex ~ g + HapIndex", gh).fit(); m2 = smf.ols("HapIndex ~ g + GratIndex", gh).fit()
res["ancova_grat_F(1,df)"] = [float(m1.tvalues["g"] ** 2), int(m1.df_resid)]
res["ancova_hap_F(1,df)"] = [float(m2.tvalues["g"] ** 2), int(m2.df_resid)]
print(f"interaction F={F:.2f} (paper 22.48); ANCOVA grat F={m1.tvalues['g']**2:.2f} df={int(m1.df_resid)} (paper 34.08, 47); "
      f"ANCOVA hap F={m2.tvalues['g']**2:.2f} (paper 10.81)")

# --- main outcome --------------------------------------------------------------------------------
y = x["ExpDiscountRate"]
means = {c: float(y[x.cond == c].mean()) for c in ("Neutral", "Gratitude", "Happiness")}
ses = {c: float(y[x.cond == c].std(ddof=1) / np.sqrt((x.cond == c).sum())) for c in means}
res["delta_mean_by_cond"] = means; res["delta_se_by_cond"] = ses
def contrast(v, w={"Neutral": -1, "Happiness": -1, "Gratitude": 2}):
    g = {c: v[x.cond == c] for c in w}
    mse = sum(((a - a.mean()) ** 2).sum() for a in g.values()) / (len(v) - 3)
    L = sum(w[c] * g[c].mean() for c in w)
    se = np.sqrt(mse * sum(w[c] ** 2 / len(g[c]) for c in w))
    t = L / se; df = len(v) - 3
    return float(t), int(df), float(2 * stats.t.sf(abs(t), df))
t, df, p = contrast(y)
res["planned_contrast_t_df_p"] = [t, df, p]
# Cohen's d for gratitude vs the other two pooled
a = y[x.cond == "Gratitude"]; b = y[x.cond != "Gratitude"]
sp = np.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1)) / (len(a) + len(b) - 2))
res["d_grat_vs_others_pooled"] = float((a.mean() - b.mean()) / sp)
res["d_from_t_2t_over_sqrt_df"] = 2 * t / np.sqrt(df)
pw = {}
for c in ("Neutral", "Happiness"):
    pw[f"grat_vs_{c}_welch_p"] = float(stats.ttest_ind(a, y[x.cond == c], equal_var=False).pvalue)
    pw[f"grat_vs_{c}_student_p"] = float(stats.ttest_ind(a, y[x.cond == c]).pvalue)
    # LSD with pooled MSE
    g = {k: y[x.cond == k] for k in ("Neutral", "Gratitude", "Happiness")}
    mse = sum(((v - v.mean()) ** 2).sum() for v in g.values()) / (len(y) - 3)
    tt = (a.mean() - g[c].mean()) / np.sqrt(mse * (1 / len(a) + 1 / len(g[c])))
    pw[f"grat_vs_{c}_pooledMSE_p"] = float(2 * stats.t.sf(abs(tt), len(y) - 3))
pw["neutral_vs_happiness_student_p"] = float(stats.ttest_ind(y[x.cond == "Neutral"], y[x.cond == "Happiness"]).pvalue)
res["pairwise"] = pw
tr, dfr, pr = contrast(y.rank())
res["rank_contrast_t_df_p"] = [tr, dfr, pr]
m = smf.ols("ExpDiscountRate ~ GratIndex + HapIndex", x).fit()
z = x[["ExpDiscountRate", "GratIndex", "HapIndex"]].apply(stats.zscore)
mz = smf.ols("ExpDiscountRate ~ GratIndex + HapIndex", z).fit()
res["regression"] = {"beta_grat_std": float(mz.params["GratIndex"]), "t_grat": float(m.tvalues["GratIndex"]),
                     "p_grat": float(m.pvalues["GratIndex"]), "t_hap": float(m.tvalues["HapIndex"]), "R2": float(m.rsquared)}
print("means", {k: round(v, 3) for k, v in means.items()}, "SEs", {k: round(v, 3) for k, v in ses.items()})
print(f"planned contrast t({df})={t:.2f} p={p:.4f}  (paper t(72)=2.18 p=.03)   d pooled={res['d_grat_vs_others_pooled']:.2f}, 2t/sqrt(df)={res['d_from_t_2t_over_sqrt_df']:.2f} (paper d=0.62)")
print("pairwise", {k: round(v, 4) for k, v in pw.items()}, "(paper: vs neutral .05, vs happy .08)")
print(f"rank contrast t={tr:.2f} p={pr:.4f} (paper 1.93, p<.06)")
print("regression", {k: round(v, 3) for k, v in res["regression"].items()}, "(paper beta .32 t 2.29 p<.03 R2 .07; hap t<1.13)")

# money translation: delta^(3/12) * 85
for c in means:
    res[f"money_equiv_85_in_3mo_{c}"] = 85 * means[c] ** 0.25
print("money:", {c: round(85 * means[c] ** .25, 1) for c in means}, "(paper $63 grateful, $55 neutral/happy)")

# --- refit discount factors from the raw choices (port of expdiscountMLE.m) -----------------------
items = [c for c in x.columns if c.startswith("n") and "or" in c and "in" in c]
def parse(c):
    a, rest = c[1:].split("or"); b, d = rest.split("in"); return float(a), float(b), float(d)
P = np.array([parse(c) for c in items])               # SS amount, LL amount, delay days
months = P[:, 2] / (365 / 12)
choices = x[items].values                              # 1 / 2 coding
res["choice_coding_values"] = sorted(map(int, np.unique(choices[~np.isnan(choices)])))
def nll(params, ll):
    d, prec = params
    ull = P[:, 1] * d ** (months / 12); uss = P[:, 0]
    pr = 1 / (1 + np.exp(np.clip(prec * (uss - ull), -700, 700)))
    pr = np.clip(pr, 1e-8, 1 - 1e-8)
    return -(ll * np.log(pr) + (1 - ll) * np.log(1 - pr)).sum()
rows = []
for i in range(len(x)):
    ll = (choices[i] == 2).astype(float)                # 2 = later-larger (checked below against deposit)
    best = None
    for start in ([.1, .4], [.5, .4], [.9, .4], [.3, 2.0], [.05, 0.1]):
        r = optimize.minimize(nll, start, args=(ll,), bounds=[(0, 1), (0, 10000)], method="L-BFGS-B")
        if best is None or r.fun < best.fun: best = r
    r0 = optimize.minimize(nll, [.1, .4], args=(ll,), bounds=[(0, 1), (0, 10000)], method="L-BFGS-B")
    rows.append({"subject": int(x.Subject[i]), "cond": x.cond[i], "prop_LL": ll.mean(),
                 "delta_deposit": float(x.ExpDiscountRate[i]), "delta_refit_bestof5": float(best.x[0]),
                 "delta_refit_start_paper": float(r0.x[0]), "prec_refit": float(best.x[1]),
                 "nll_best": float(best.fun), "nll_paper_start": float(r0.fun)})
R = pd.DataFrame(rows)
R.to_csv(os.path.join(OUT, "participants_refit.csv"), index=False, lineterminator="\n")
res["refit_corr_with_deposit"] = float(np.corrcoef(R.delta_deposit, R.delta_refit_bestof5)[0, 1])
res["refit_abs_diff_gt_0.05"] = int((abs(R.delta_deposit - R.delta_refit_bestof5) > .05).sum())
res["participants_all_SS_or_all_LL"] = int(((R.prop_LL == 0) | (R.prop_LL == 1)).sum())
res["delta_deposit_lt_0.01"] = int((R.delta_deposit < .01).sum())
res["delta_deposit_quantiles"] = R.delta_deposit.quantile([0, .1, .25, .5, .75, .9, 1]).round(4).tolist()
print(f"refit vs deposit r={res['refit_corr_with_deposit']:.4f}; |diff|>.05: {res['refit_abs_diff_gt_0.05']}; "
      f"all-SS/all-LL participants: {res['participants_all_SS_or_all_LL']}; deposit delta<.01: {res['delta_deposit_lt_0.01']}")
print("delta quantiles", res["delta_deposit_quantiles"])
# model-free outcome: proportion of later-larger choices
tp, dfp, pp = contrast(R.set_index(x.index).prop_LL)
res["model_free_propLL_contrast_t_df_p"] = [tp, dfp, pp]
res["propLL_mean_by_cond"] = R.groupby("cond").prop_LL.mean().to_dict()
print(f"MODEL-FREE: proportion of later-larger choices by condition {res['propLL_mean_by_cond']}; contrast t={tp:.2f} p={pp:.4f}")
with open(os.path.join(OUT, "r01.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(res, f, indent=1, default=float)
