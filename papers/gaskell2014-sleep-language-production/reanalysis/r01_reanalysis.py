"""Gaskell et al. (2014) -- recount Tables 1-3 from the OSF deposit (zqg9y components) and test three
things the paper did not: (1) is the SWS 'logistic regression' result an artefact of treating thousands of
speech errors from 19 people as independent; (2) can regression to the mean from the chance baseline
imbalance produce the Group x Session x Restriction crossover; (3) are Table 2's '(SD)' values SDs.

Usage (from the zoo root):
  python zoo-knowledge-base/instance-papers/papers/gaskell2014-sleep-language-production/reanalysis/r01_reanalysis.py \
     "$(python zoo-knowledge-base/tools/assets.py path paper-downloads/gaskell2014-sleep-language-production)"
Writes out/r01.json.
"""
import json, os, sys, warnings
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.api as sm, statsmodels.formula.api as smf
warnings.filterwarnings("ignore")
D = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"); os.makedirs(OUT, exist_ok=True)
e = pd.read_csv(os.path.join(D, "osf_fcgd6/files/osfstorage/keyvarscentred.csv"))
g = pd.read_csv(os.path.join(D, "osf_7qn52/files/osfstorage/recgendata.csv"))
res = {}
e["grp"] = e.Group.map({-0.5: "wake", 0.5: "sleep"}); e["restr"] = e.Restriction.map({-0.5: "unres", 0.5: "res"})
e["blk"] = e.Block.map({-1: "train", 0: "test1", 1: "test2"})
res["n_subjects_by_group"] = e.groupby("grp").SubID.nunique().to_dict()
blocks_per_subj = e.groupby("SubID").blk.nunique()
res["subjects_with_fewer_than_3_blocks"] = blocks_per_subj[blocks_per_subj < 3].to_dict()
print("subjects per group", res["n_subjects_by_group"], "| subjects missing a block:", res["subjects_with_fewer_than_3_blocks"])

# ---- Table 1 --------------------------------------------------------------------------------------
pp = e.groupby(["grp", "blk", "restr", "SubID"]).SyllPos.agg(["mean", "size"]).reset_index()
t1 = pp.groupby(["grp", "blk", "restr"]).agg(same_pct_mean=("mean", lambda v: 100 * v.mean()), same_pct_sd=("mean", lambda v: 100 * v.std()),
                                               n_err_mean=("size", "mean"), n_err_sd=("size", "std"), n_subj=("SubID", "nunique")).round(1)
# participants with zero errors of a type are absent from pp: report how many
res["table1_recount"] = {"|".join(k): v for k, v in t1.to_dict("index").items()}
print(t1.to_string())
print("paper Table 1 (same% (SD); total errors (SD)): train sleep unres 85(11) 45.3(14.1), res 80(8) 9.5(4.7); wake unres 79(10) 50.2(28.5), res 90(14) 8.8(5.4);"
      " test1 sleep 84(11) 32.3(15.4) / 92(9) 4.9(3.8); wake 85(11) 39.8(17.3) / 86(15) 6.1(4.7); test2 sleep 84(9) 28.3(25.4) / 94(17) 6.0(5.4); wake 84(8) 29.5(25.6) / 85(16) 6.8(4.9)")

# The paper's same-position % MEANS are pooled over errors (sum same / sum errors), while the SDs printed
# next to them are across participants -- and the SD column is shifted by one block (see NOTES).
pooled = (e.groupby(["grp", "blk", "restr"]).SyllPos.mean() * 100).round(1)
res["table1_pooled_same_pct"] = {"|".join(k): float(v) for k, v in pooled.items()}
cnt = e.groupby(["SubID", "grp", "blk", "restr"]).size().unstack(["blk", "restr"], fill_value=0)
cstat = cnt.groupby(level="grp").agg(["mean", "std"]).round(1)
res["table1_error_counts_incl_zeros"] = {f"{g_}|{c[0]}|{c[1]}|{c[2]}": float(cstat.loc[g_, c]) for g_ in cstat.index for c in cstat.columns}
print("pooled same-position % (paper's means):", res["table1_pooled_same_pct"])
print("error counts per participant incl. zeros (mean, sd):", res["table1_error_counts_incl_zeros"])

# ---- participant-level phonotactic learning score -----------------------------------------------
e["sess"] = np.where(e.Session < 0, "train", "test")
ps = e.groupby(["SubID", "grp", "sess", "restr"]).SyllPos.mean().unstack("restr")
ps["score"] = 100 * (ps["res"] - ps["unres"])
S = ps["score"].unstack("sess").reset_index()
S["change"] = S["test"] - S["train"]
res["score_mean_by_group"] = S.groupby("grp")[["train", "test", "change"]].mean().round(2).to_dict("index")
print("\nphonotactic learning score (restricted - unrestricted same-position %), participant means:", res["score_mean_by_group"])
a = S[S.grp == "sleep"].change.dropna(); b = S[S.grp == "wake"].change.dropna()
res["change_sleep_vs_wake_t_p"] = [float(stats.ttest_ind(a, b).statistic), float(stats.ttest_ind(a, b).pvalue)]
# permutation of group labels on the participant-level change (the crossover statistic)
rng = np.random.default_rng(5)
SS = S.dropna(subset=["change"]); lab = SS.grp.values; ch = SS.change.values
obs = ch[lab == "sleep"].mean() - ch[lab == "wake"].mean()
perm = np.array([(lambda L: ch[L == "sleep"].mean() - ch[L == "wake"].mean())(rng.permutation(lab)) for _ in range(100000)])
res["perm_p_change_diff"] = float((np.abs(perm) >= abs(obs)).mean())
# ANCOVA: test score ~ group + training score (the regression-to-the-mean-proof comparison)
m = smf.ols("test ~ C(grp) + train", SS).fit()
res["ancova_test_on_group_plus_train"] = {"group_coef_sleep_minus_wake": float(m.params["C(grp)[T.wake]"] * -1), "p": float(m.pvalues["C(grp)[T.wake]"]),
                                           "train_slope": float(m.params["train"])}
res["train_score_group_diff_t_p"] = [float(stats.ttest_ind(SS[SS.grp == "sleep"].train, SS[SS.grp == "wake"].train).statistic),
                                     float(stats.ttest_ind(SS[SS.grp == "sleep"].train, SS[SS.grp == "wake"].train).pvalue)]
# reliability of the participant-level score: split each participant's errors into odd/even halves within session
e["half"] = e.groupby(["SubID", "sess", "restr"]).cumcount() % 2
hs = e.groupby(["SubID", "sess", "half", "restr"]).SyllPos.mean().unstack("restr")
hs["score"] = hs["res"] - hs["unres"]
hh = hs["score"].unstack("half").reset_index()
rel = {}
for s in ("train", "test"):
    x = hh[hh.sess == s].dropna()
    r = np.corrcoef(x[0], x[1])[0, 1]; rel[s] = {"split_half_r": float(r), "spearman_brown": float(2 * r / (1 + r)), "n": len(x)}
res["score_reliability"] = rel
print(f"change sleep vs wake t={res['change_sleep_vs_wake_t_p'][0]:.2f} p={res['change_sleep_vs_wake_t_p'][1]:.4f}; permutation p={res['perm_p_change_diff']:.4f}")
print(f"baseline (training) score difference sleep vs wake: t={res['train_score_group_diff_t_p'][0]:.2f} p={res['train_score_group_diff_t_p'][1]:.3f}")
print("ANCOVA test ~ group + train:", {k: round(v, 3) for k, v in res["ancova_test_on_group_plus_train"].items()})
print("participant-level score reliability (split-half, Spearman-Brown):", rel)

# ---- SWS: as published vs accounting for participants ----------------------------------------------
sl = e[e.grp == "sleep"].copy()
pub = smf.glm("SyllPos ~ Session:Restriction:N3Mins", sl, family=sm.families.Binomial()).fit()
res["sws_glm_as_published"] = {"beta": float(pub.params["Session:Restriction:N3Mins"]), "se": float(pub.bse["Session:Restriction:N3Mins"]),
                               "z": float(pub.tvalues["Session:Restriction:N3Mins"]), "p": float(pub.pvalues["Session:Restriction:N3Mins"]), "n_errors": int(pub.nobs)}
full = smf.glm("SyllPos ~ Session*Restriction*N3Mins", sl, family=sm.families.Binomial()).fit()
fullc = smf.glm("SyllPos ~ Session*Restriction*N3Mins", sl, family=sm.families.Binomial()).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(sl.SubID)[0]})
pubc = smf.glm("SyllPos ~ Session:Restriction:N3Mins", sl, family=sm.families.Binomial()).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(sl.SubID)[0]})
k = "Session:Restriction:N3Mins"
res["sws_glm_published_formula_cluster_robust"] = {"beta": float(pubc.params[k]), "se": float(pubc.bse[k]), "z": float(pubc.tvalues[k]), "p": float(pubc.pvalues[k])}
res["sws_glm_with_lower_order_terms"] = {"beta": float(full.params[k]), "se": float(full.bse[k]), "z": float(full.tvalues[k]), "p": float(full.pvalues[k])}
res["sws_glm_with_lower_order_terms_cluster_robust"] = {"beta": float(fullc.params[k]), "se": float(fullc.bse[k]), "z": float(fullc.tvalues[k]), "p": float(fullc.pvalues[k])}
print("\nSWS x Session x Restriction:")
for kk in ("sws_glm_as_published", "sws_glm_published_formula_cluster_robust", "sws_glm_with_lower_order_terms", "sws_glm_with_lower_order_terms_cluster_robust"):
    print(f"  {kk:48s}", {a_: round(b_, 4) if isinstance(b_, float) else b_ for a_, b_ in res[kk].items()})
# participant-level correlations (Table 3 r column), with permutation p
sub = sl.groupby("SubID")[["N1Mins", "N2Mins", "N3Mins", "RMins", "SleepPeriod", "Delta"]].first()
SC = S.set_index("SubID").loc[sub.index]
cors = {}
for v in sub.columns:
    x = sub[v].values; y = SC.change.values; ok = ~np.isnan(y)
    r = np.corrcoef(x[ok], y[ok])[0, 1]
    pr = np.array([np.corrcoef(rng.permutation(x[ok]), y[ok])[0, 1] for _ in range(20000)])
    cors[v] = {"r": float(r), "p_param": float(stats.pearsonr(x[ok], y[ok])[1]), "p_perm": float((np.abs(pr) >= abs(r)).mean()), "n": int(ok.sum())}
res["participant_level_correlations_with_change"] = cors
print("participant-level r(stage minutes, change in score), sleep group:", {k_: {a_: round(b_, 3) for a_, b_ in v.items()} for k_, v in cors.items()})
print("paper Table 3 r: N1 -.21, N2 -.06, SWS .47*, REM -.49*, sleep period -.22")
# leave-one-out on the SWS correlation
x = sub["N3Mins"].values; y = SC.change.values
loo = [np.corrcoef(np.delete(x, i), np.delete(y, i))[0, 1] for i in range(len(x))]
res["sws_r_leave_one_out_min_max"] = [float(min(loo)), float(max(loo))]
res["sws_minutes_zero_in_sleep_group"] = int((sub["N3Mins"] == sub["N3Mins"].min()).sum())
print(f"SWS r leave-one-out range: {min(loo):.3f} .. {max(loo):.3f}; participants at the minimum SWS value (no SWS): {res['sws_minutes_zero_in_sleep_group']}")

# ---- Table 2 ---------------------------------------------------------------------------------------
gen = g[g.test == "B-Gen"].copy(); gen["grp"] = gen.Group.map({-0.5: "wake", 0.5: "sleep"})
pt = gen.groupby(["grp", "Type", "SubID"]).result.mean().reset_index()
t2 = pt.groupby(["grp", "Type"]).result.agg(mean=lambda v: 100 * v.mean(), sd=lambda v: 100 * v.std(), se=lambda v: 100 * v.std() / np.sqrt(len(v)), n="size").round(1)
res["table2_recount"] = {"|".join(k): v for k, v in t2.to_dict("index").items()}
overall = gen.groupby(["grp", "SubID"]).result.mean().groupby("grp").mean() * 100
res["gen_overall_pct"] = overall.round(1).to_dict()
print("\nTable 2 recount (per-participant % correct):"); print(t2.to_string())
print("paper Table 2 '(SD)': target familiar sleep 99 (3) wake 92 (3); target unfamiliar 47 (7) / 24 (7); both unfamiliar 60 (4) / 52 (4); overall sleep 69 wake 56")
res["gen_unweighted_mean_of_type_means_pct"] = (pt.groupby(["grp", "Type"]).result.mean().groupby("grp").mean() * 100).round(1).to_dict()
print("generalisation: raw per-participant accuracy", res["gen_overall_pct"], "| unweighted mean of the 3 type means (the paper's 69/56)", res["gen_unweighted_mean_of_type_means_pct"])
rec = g[g.test == "A-Rec"].groupby(["Group", "SubID"]).result.mean().groupby("Group").mean() * 100
res["recognition_pct"] = rec.round(1).to_dict()
print("recognition % by group:", res["recognition_pct"], "(paper: sleep 88, wake 87)")
with open(os.path.join(OUT, "r01.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(res, f, indent=1, default=float)
