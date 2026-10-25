"""Walasek & Brown (2015) -- what can be checked from the OSF deposit (fitgz components) without the paper.

(1) Rebuild the residual inequality measure from the deposited census controls (regress GINI on log mean
    income, population, % urban, % foreign born; 50 states, DC omitted per the authors' methods PDF) and
    compare with the deposited residuals that were entered into Google Correlate.
(2) Recompute the abstract's '>70% of the 40 positively correlated terms were classified as status goods,
    0% of the 40 negatively correlated' from the MTurk counts, under the methods PDF's rule (proportion
    'yes' out of yes+no, 'not sure' excluded) and a range of classification thresholds.
(3) Break test: is the residual measure geographically structured? If residual inequality is largely a
    Census-region effect, terms that track it can be regional brand culture (Northeast preppy brands)
    rather than status seeking -- the 'avoid confounds' claim covers only the 4 controls.
Usage (from the zoo root):
  python zoo-knowledge-base/instance-papers/papers/walasek2015-income-inequality-status-seeking/reanalysis/r01_deposit_checks.py \
    "$(python zoo-knowledge-base/tools/assets.py path paper-downloads/walasek2015-income-inequality-status-seeking)"
Writes out/r01.json.
"""
import json, os, sys, warnings
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
warnings.filterwarnings("ignore")
B = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"); os.makedirs(OUT, exist_ok=True)
res = {}
c = pd.read_excel(os.path.join(B, "osf_tqi83/files/osfstorage/Inequality_Control_Data.xlsx"))
r = pd.read_excel(os.path.join(B, "osf_437xf/files/osfstorage/open_access_residuals.xlsx"))
t = pd.read_excel(os.path.join(B, "osf_xfmbq/files/osfstorage/RatingData.xlsx"))
res["n_states_controls"] = len(c); res["n_states_residuals"] = len(r)
res["log_mean_inc_is_ln_of_mean_income_max_abs_diff"] = float((np.log(c.MeanIncome) - c.log_mean_inc).abs().max())

# (1) residuals
variants = {
    "pop_raw": "GINIindex ~ log_mean_inc + Population + percurban + PercentForeignBorn",
    "pop_log": "GINIindex ~ log_mean_inc + np.log(Population) + percurban + PercentForeignBorn",
}
m = c.merge(r, left_on="state", right_on="State", how="outer", indicator=True)
res["state_merge"] = m["_merge"].value_counts().to_dict()
best = None
for k, f in variants.items():
    fit = smf.ols(f, m).fit()
    d = (fit.resid - m.Residual_GINI).abs()
    res[f"residuals_{k}"] = {"max_abs_diff": float(d.max()), "corr": float(np.corrcoef(fit.resid, m.Residual_GINI)[0, 1]), "R2": float(fit.rsquared)}
    print(f"residuals, model {k}: max |diff| vs deposit = {d.max():.6f}, r = {np.corrcoef(fit.resid, m.Residual_GINI)[0, 1]:.6f}, R2 = {fit.rsquared:.3f}")
fit = smf.ols(variants["pop_raw"], m).fit()
res["control_model_coefs"] = {k: [float(v), float(fit.pvalues[k])] for k, v in fit.params.items()}

# (2) ratings
t.columns = ["direction", "term_id", "term", "yes", "no", "dk", "r"]
t["p_yes"] = t.yes / (t.yes + t.no)
# the deposit stores negative r as text with a typographic minus (U+2013 or U+2212); parse it
t["r"] = pd.to_numeric(t.r.astype(str).str.replace(chr(0x2013), "-", regex=False).str.replace(chr(0x2212), "-", regex=False), errors="coerce")
res["r_unparseable"] = int(t.r.isna().sum())
res["n_terms"] = t.direction.value_counts().to_dict()
res["raters_per_term"] = sorted(set((t.yes + t.no + t.dk).astype(int)))
res["r_range_by_direction"] = {d: [float(g.r.min()), float(g.r.max())] for d, g in t.groupby("direction")}
thr = {}
for th in (0.5, 0.6, 2 / 3, 0.7, 0.75, 0.8):
    thr[f"{th:.3f}"] = {d: float((g.p_yes > th).mean()) for d, g in t.groupby("direction")}
res["share_classified_status_by_threshold"] = thr
res["mean_p_yes_by_direction"] = t.groupby("direction").p_yes.mean().to_dict()
res["mannwhitney_p_yes_pos_vs_neg"] = float(stats.mannwhitneyu(t[t.direction == "pos"].p_yes, t[t.direction == "neg"].p_yes).pvalue)
print("raters per term:", res["raters_per_term"], "| terms:", res["n_terms"])
print("share of terms with p(yes) > threshold:", {k: {a: round(b, 3) for a, b in v.items()} for k, v in thr.items()})
print("abstract: >70% of 40 positive terms status goods, 0% of 40 negative")
print("negative-list terms with the highest p(yes):", t[t.direction == "neg"].sort_values("p_yes", ascending=False).head(5)[["term", "p_yes"]].values.tolist())
print("positive-list terms with p(yes) <= .5:", t[(t.direction == "pos") & (t.p_yes <= .5)][["term", "p_yes"]].values.tolist())
res["positive_terms_p_yes_le_half"] = t[(t.direction == "pos") & (t.p_yes <= .5)][["term", "p_yes"]].values.tolist()

# (2b) the 40 terms are not 40 independent observations: near-duplicate query families
status = t[(t.direction == "pos") & (t.p_yes > .5)].copy()
fam = {"ralph lauren": status.term.str.contains("ralph lauren"), "yurman": status.term.str.contains("yurman"),
       "loafer": status.term.str.contains("loafer")}
res["status_terms_majority_rule"] = int(len(status))
res["status_terms_in_families"] = {k: int(v.sum()) for k, v in fam.items()}
res["status_terms_outside_families"] = int(len(status) - sum(v.sum() for v in fam.values()))
print("status-classified positive terms:", len(status), "| in near-duplicate families:", res["status_terms_in_families"],
      "| outside:", res["status_terms_outside_families"])

# (3) geography of the residual
region = {
 "Northeast": "Connecticut Maine Massachusetts New_Hampshire Rhode_Island Vermont New_Jersey New_York Pennsylvania",
 "Midwest": "Illinois Indiana Michigan Ohio Wisconsin Iowa Kansas Minnesota Missouri Nebraska North_Dakota South_Dakota",
 "South": "Delaware Florida Georgia Maryland North_Carolina South_Carolina Virginia West_Virginia Alabama Kentucky Mississippi Tennessee Arkansas Louisiana Oklahoma Texas",
 "West": "Arizona Colorado Idaho Montana Nevada New_Mexico Utah Wyoming Alaska California Hawaii Oregon Washington"}
reg = {s.replace("_", " "): k for k, v in region.items() for s in v.split()}
m["region"] = m.state.map(reg)
res["states_without_region"] = m[m.region.isna()].state.tolist()
fr = smf.ols("Residual_GINI ~ C(region)", m).fit()
res["residual_on_region_R2_p"] = [float(fr.rsquared), float(fr.f_pvalue)]
res["residual_mean_by_region"] = m.groupby("region").Residual_GINI.mean().round(4).to_dict()
top = m.sort_values("Residual_GINI", ascending=False)[["state", "Residual_GINI"]].head(8).values.tolist()
res["top8_residual_states"] = top
print(f"\nresidual inequality explained by 4 Census regions: R2 = {fr.rsquared:.3f}, p = {fr.f_pvalue:.4f}; means {res['residual_mean_by_region']}")
print("top-8 residual-inequality states:", top)
with open(os.path.join(OUT, "r01.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(res, f, indent=1, default=float)
