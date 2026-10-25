"""Follow-ups to r01: what produces d = 0.62 and the manipulation-check means; is 'gratitude is
differentiable from happiness' actually tested; exact permutation p-values for the contrast on a bounded,
skewed outcome; and a known-answer check of the contrast under the null on THIS outcome distribution.
Usage: same argument as r01. Writes out/r02.json."""
import json, os, sys, itertools
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

D = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
x = pd.read_excel(os.path.join(D, "Gratitude_Discounting_PsycSci.xlsx"))
x["cond"] = x["Condition"].map({1: "Neutral", 2: "Gratitude", 3: "Happiness"})
R = pd.read_csv(os.path.join(OUT, "participants_refit.csv"))
assert (R.subject.values == x.Subject.values).all()
x["propLL"] = R.prop_LL.values
y = x.ExpDiscountRate
res = {}

# --- which d gives 0.62? ---------------------------------------------------------------------------
g = {c: y[x.cond == c] for c in ("Neutral", "Gratitude", "Happiness")}
def d(a, b, pooled=True):
    if pooled:
        s = np.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1)) / (len(a) + len(b) - 2))
    else:
        s = b.std(ddof=1)
    return float((a.mean() - b.mean()) / s)
mse = sum(((v - v.mean()) ** 2).sum() for v in g.values()) / (len(y) - 3)
others = pd.concat([g["Neutral"], g["Happiness"]])
cands = {
    "grat_vs_neutral_pooled": d(g["Gratitude"], g["Neutral"]),
    "grat_vs_happy_pooled": d(g["Gratitude"], g["Happiness"]),
    "grat_vs_others_pooled": d(g["Gratitude"], others),
    "grat_vs_others_sd_of_others": d(g["Gratitude"], others, pooled=False),
    "grat_vs_neutral_sd_of_neutral(Glass)": d(g["Gratitude"], g["Neutral"], pooled=False),
    "grat_vs_others_over_sqrtMSE": float((g["Gratitude"].mean() - others.mean()) / np.sqrt(mse)),
    "contrast_L_over_sqrtMSE (L=2g-n-h)": float((2 * g["Gratitude"].mean() - g["Neutral"].mean() - g["Happiness"].mean()) / np.sqrt(mse)),
    "2t/sqrt(df)": 2 * 2.1806 / np.sqrt(72),
    "t*sqrt(1/25+1/50)": 2.1806 * np.sqrt(1 / 25 + 1 / 50),
    "t*sqrt(6/25)/ ... (contrast d with sum|w|/2 standardizer)": float((2 * g["Gratitude"].mean() - g["Neutral"].mean() - g["Happiness"].mean()) / 2 / np.sqrt(mse)),
}
res["d_candidates"] = cands
print("d candidates (paper 0.62):", {k: round(v, 3) for k, v in cands.items()})

# --- manipulation check means ------------------------------------------------------------------------
both = (x.GratIndex + x.HapIndex) / 2
res["manip_mean_of_both_indices_by_cond"] = {c: [round(float(both[x.cond == c].mean()), 3), round(float(both[x.cond == c].std(ddof=1)), 3)] for c in g}
print("mean of both positive indices by condition [M, SD]:", res["manip_mean_of_both_indices_by_cond"], "(paper grat 4.47/.38, happy 4.11/.72, neutral 3.17/.84)")

# --- is 'differentiable from happiness' tested? ----------------------------------------------------
gh = x[x.cond.isin(["Gratitude", "Happiness"])]
res["grat_vs_happy_delta_t_test_p"] = float(stats.ttest_ind(g["Gratitude"], g["Happiness"]).pvalue)
res["grat_vs_happy_propLL_t_test_p"] = float(stats.ttest_ind(gh.propLL[gh.cond == "Gratitude"], gh.propLL[gh.cond == "Happiness"]).pvalue)
res["grat_vs_neutral_propLL_t_test_p"] = float(stats.ttest_ind(x.propLL[x.cond == "Gratitude"], x.propLL[x.cond == "Neutral"]).pvalue)
# difference between the two regression coefficients (beta_grat - beta_hap = 0)
m = smf.ols("ExpDiscountRate ~ GratIndex + HapIndex", x).fit()
tt = m.t_test("GratIndex - HapIndex = 0")
res["regression_coef_difference_t_p"] = [float(tt.tvalue.item()), float(tt.pvalue)]
print(f"grat vs happy (delta) p={res['grat_vs_happy_delta_t_test_p']:.3f}; (propLL) p={res['grat_vs_happy_propLL_t_test_p']:.3f}; "
      f"grat vs neutral (propLL) p={res['grat_vs_neutral_propLL_t_test_p']:.3f}")
print(f"regression: test beta_grat = beta_hap: t={res['regression_coef_difference_t_p'][0]:.2f} p={res['regression_coef_difference_t_p'][1]:.3f}")
# within-condition regression (does gratitude intensity predict delta inside the gratitude condition alone?)
for c in g:
    sub = x[x.cond == c]
    r_, p_ = stats.pearsonr(sub.GratIndex, sub.ExpDiscountRate)
    res[f"within_{c}_r_grat_delta"] = [float(r_), float(p_)]
print("within-condition r(GratIndex, delta):", {k: [round(v, 3) for v in vv] for k, vv in res.items() if k.startswith("within_")})
mc = smf.ols("ExpDiscountRate ~ C(cond) + GratIndex + HapIndex", x).fit()
res["regression_with_condition_dummies_t_grat_p"] = [float(mc.tvalues["GratIndex"]), float(mc.pvalues["GratIndex"])]
print(f"regression adding condition dummies: GratIndex t={mc.tvalues['GratIndex']:.2f} p={mc.pvalues['GratIndex']:.3f} "
      "(if the association is only the between-condition contrast, it should vanish)")

# --- exact-ish permutation p for the planned contrast -------------------------------------------------
rng = np.random.default_rng(11)
w = x.cond.map({"Neutral": -1, "Happiness": -1, "Gratitude": 2}).values
def L(v, lab):
    return 2 * v[lab == "Gratitude"].mean() - v[lab == "Neutral"].mean() - v[lab == "Happiness"].mean()
lab = x.cond.values
for name, v in (("delta", y.values), ("propLL", x.propLL.values), ("delta_rank", y.rank().values)):
    obs = L(v, lab)
    perm = np.array([L(v, rng.permutation(lab)) for _ in range(100000)])
    res[f"perm_p_two_sided_{name}"] = float((np.abs(perm) >= abs(obs) - 1e-12).mean())
    print(f"permutation p (two-sided, 100k) contrast on {name}: {res[f'perm_p_two_sided_{name}']:.4f}")

# --- known answer: is the parametric contrast calibrated on this skewed, bounded outcome? -------------
# Null: resample 75 outcomes from the pooled empirical distribution, assign conditions at random.
pool = y.values; hits = 0; S = 20000
for _ in range(S):
    v = rng.choice(pool, 75, replace=True)
    gg = [v[:25], v[25:50], v[50:]]
    msev = sum(((a - a.mean()) ** 2).sum() for a in gg) / 72
    Lv = 2 * gg[1].mean() - gg[0].mean() - gg[2].mean()
    t = Lv / np.sqrt(msev * (4 / 25 + 1 / 25 + 1 / 25))
    hits += 2 * stats.t.sf(abs(t), 72) < 0.05
res["null_typeI_parametric_contrast_on_empirical_delta"] = hits / S
print(f"known-answer null (pooled empirical delta, random labels): parametric contrast rejects {hits/S:.3f} at alpha .05")
with open(os.path.join(OUT, "r02.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(res, f, indent=1)
