"""Maglio & Polman (2014, Psych Sci 25(7):1345) -- reproduce every inferential number from the OSF deposit (6m2it)
and probe each against distributional choices.

Usage (from the zoo root):
  python -I zoo-knowledge-base/instance-papers/papers/maglio2014-spatial-orientation-psychological-distance/reanalysis/r01_reproduce.py \
    "$(python zoo-knowledge-base/tools/assets.py path paper-downloads/maglio2014-spatial-orientation-psychological-distance)/osf_6m2it/files/osfstorage"
Writes out/r01.json and prints a published-vs-recomputed table.
"""
import json, os, sys, warnings
import numpy as np, pandas as pd, openpyxl
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm
warnings.filterwarnings("ignore")
D = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"); os.makedirs(OUT, exist_ok=True)


def load(name):
    ws = openpyxl.load_workbook(os.path.join(D, name), data_only=True).worksheets[0]
    rows = [r for r in ws.iter_rows(values_only=True) if any(v is not None for v in r)]
    return pd.DataFrame(rows[1:], columns=rows[0])


def eta_p(F, df1, df2):
    return F * df1 / (F * df1 + df2)


def oneway(df, y, g):
    groups = [v[y].astype(float).values for _, v in df.groupby(g)]
    F, p = stats.f_oneway(*groups)
    return float(F), float(p)


res = {}
rows = []  # (study, quantity, published, recomputed)

# ---------------- Study 1 ----------------
s1 = load("S1_Subway.xlsx")
s1.columns = ["dir", "y", "stn", "name"]
s1["dir"] = s1.dir.str.strip().str.upper()
s1["y"] = s1.y.astype(float)
res["s1_n"] = {"total": len(s1), "by_dir": s1.dir.value_counts().to_dict(), "cells": s1.groupby(["name", "dir"]).size().to_dict()}
m = smf.ols("y ~ C(dir, Sum) * C(name, Sum)", s1).fit()
a = anova_lm(m, typ=3)
F_dir, F_stn, F_int = a.loc["C(dir, Sum)", "F"], a.loc["C(name, Sum)", "F"], a.loc["C(dir, Sum):C(name, Sum)", "F"]
dfr = int(m.df_resid)
rows += [("S1", "F station (3,194)", 24.10, round(F_stn, 2)), ("S1", "F interaction (3,194)", 16.28, round(F_int, 2)),
         ("S1", "F orientation (<1)", "<1", round(F_dir, 2)), ("S1", "df_resid", 194, dfr),
         ("S1", "eta_p2 station", .27, round(eta_p(F_stn, 3, dfr), 3)), ("S1", "eta_p2 interaction", .20, round(eta_p(F_int, 3, dfr), 3))]
# simple effects: paper does not say whether error term is pooled; compute both
pub_simple = {"STG": (.001, .28), "SPA": (.001, .20), "B-Y": (.053, .08), "SHE": (.001, .24)}
mse = m.mse_resid
simple = {}
for nm, sub in s1.groupby("name"):
    Fo, po = oneway(sub, "y", "dir")
    gm = sub.groupby("dir").y.agg(["mean", "count", "std"])
    # pooled-error contrast
    diff = gm.loc["EAST", "mean"] - gm.loc["WEST", "mean"]
    se = np.sqrt(mse * (1 / gm.loc["EAST", "count"] + 1 / gm.loc["WEST", "count"]))
    Fp = (diff / se) ** 2
    pp = float(stats.f.sf(Fp, 1, dfr))
    simple[nm] = {"means": gm.round(3).to_dict(), "sep_F": round(Fo, 3), "sep_p": round(po, 4), "sep_eta": round(eta_p(Fo, 1, len(sub) - 2), 3),
                  "pooled_F": round(Fp, 3), "pooled_p": round(pp, 4), "pooled_eta": round(Fp / (Fp + dfr), 3)}
res["s1_simple"] = simple
for nm, (pp, ee) in pub_simple.items():
    key = [k for k in simple if k.upper().startswith(nm[:2])][0]
    rows.append(("S1", f"simple {key} p (sep / pooled)", pp, f"{simple[key]['sep_p']} / {simple[key]['pooled_p']}"))
    rows.append(("S1", f"simple {key} eta (sep / pooled)", ee, f"{simple[key]['sep_eta']} / {simple[key]['pooled_eta']}"))
# The theoretically relevant contrast: toward vs away (station on the side you travel to)
west_st = {"SPA", "STG"}
s1["side"] = np.where(s1.name.str.upper().str[:3].isin(west_st), "WEST", "EAST")
s1["toward"] = (s1.side == s1.dir).astype(int)
s1["near"] = s1.name.str.upper().str[:3].isin({"STG", "B-Y"}).astype(int)
mt = smf.ols("y ~ toward * near + C(side)", s1).fit()
res["s1_toward_model"] = {k: [round(float(mt.params[k]), 3), round(float(mt.pvalues[k]), 5)] for k in mt.params.index}
res["s1_toward_means"] = s1.groupby(["near", "toward"]).y.mean().round(3).to_dict()
res["s1_toward_MW"] = float(stats.mannwhitneyu(s1[s1.toward == 1].y, s1[s1.toward == 0].y).pvalue)

# ---------------- Study 2 ----------------
s2 = load("S2_Facing.xlsx"); s2.columns = ["dir", "face", "y"]
s2["dir"] = s2.dir.str.strip().str.lower(); s2["face"] = s2.face.str.strip().str.lower(); s2["y"] = s2.y.astype(float)
m2 = smf.ols("y ~ C(dir, Sum) * C(face, Sum)", s2).fit(); a2 = anova_lm(m2, typ=3)
F2 = a2.loc["C(dir, Sum)", "F"]
g2 = s2.groupby("dir").y.agg(["mean", "std", "count"])
res["s2"] = {"cells": s2.groupby(["dir", "face"]).size().to_dict(), "anova": a2.round(4).to_dict(), "means": g2.round(3).to_dict(),
             "MW_p": float(stats.mannwhitneyu(s2[s2.dir == "east"].y, s2[s2.dir == "west"].y).pvalue),
             "t_welch_p": float(stats.ttest_ind(s2[s2.dir == "east"].y, s2[s2.dir == "west"].y, equal_var=False).pvalue)}
rows += [("S2", "F orientation (1,76)", 4.79, round(F2, 2)), ("S2", "p", .032, round(float(a2.loc['C(dir, Sum)', 'PR(>F)']), 4)),
         ("S2", "M east (toward)", 3.63, round(g2.loc['east', 'mean'], 2)), ("S2", "SD east", 1.00, round(g2.loc['east', 'std'], 2)),
         ("S2", "M west (away)", 4.15, round(g2.loc['west', 'mean'], 2)), ("S2", "SD west", 1.12, round(g2.loc['west', 'std'], 2)),
         ("S2", "F face, F int (<1)", "<1,<1", f"{a2.loc['C(face, Sum)', 'F']:.2f},{a2.loc['C(dir, Sum):C(face, Sum)', 'F']:.2f}")]

# ---------------- Study 3a ----------------
s3 = load("S3a_Shoppers.xlsx"); s3.columns = ["dir", "y"]; s3["dir"] = s3.dir.str.strip().str.lower(); s3["y"] = s3.y.astype(float)
F3, p3 = oneway(s3, "y", "dir"); g3 = s3.groupby("dir").y.agg(["mean", "std", "count"])
res["s3a"] = {"means": g3.round(3).to_dict(), "F": F3, "p": p3, "MW_p": float(stats.mannwhitneyu(s3[s3.dir == "toward"].y, s3[s3.dir == "away"].y).pvalue),
              "log1p_F_p": oneway(s3.assign(y=np.log1p(s3.y)), "y", "dir"), "max_by": s3.groupby("dir").y.max().to_dict(),
              "skew_by": s3.groupby("dir").y.apply(lambda v: float(stats.skew(v))).to_dict()}
rows += [("S3a", "n toward/away", "52/48", f"{int(g3.loc['toward','count'])}/{int(g3.loc['away','count'])}"),
         ("S3a", "M toward", 7.65, round(g3.loc['toward', 'mean'], 2)), ("S3a", "SD toward", 9.98, round(g3.loc['toward', 'std'], 2)),
         ("S3a", "M away", 14.83, round(g3.loc['away', 'mean'], 2)), ("S3a", "SD away", 17.19, round(g3.loc['away', 'std'], 2)),
         ("S3a", "F(1,98)", 6.65, round(F3, 2)), ("S3a", "p", .011, round(p3, 4))]

# ---------------- Study 3b ----------------
s3b = load("S3b_Starbucks.xlsx"); s3b.columns = ["dir", "tgt", "y"]
s3b["dir"] = s3b.dir.str.strip().str.lower(); s3b["tgt"] = s3b.tgt.str.strip(); s3b["y"] = s3b.y.astype(float)
m3b = smf.ols("y ~ C(dir, Sum) * C(tgt, Sum)", s3b).fit(); a3b = anova_lm(m3b, typ=3)
g3b = s3b.groupby("dir").y.agg(["mean", "std", "count"])
res["s3b"] = {"cells": s3b.groupby(["dir", "tgt"]).size().to_dict(), "anova": a3b.round(4).to_dict(), "means": g3b.round(3).to_dict(),
              "MW_p": float(stats.mannwhitneyu(s3b[s3b.dir == "toward"].y, s3b[s3b.dir == "away"].y).pvalue),
              "log1p_anova_p_dir": float(anova_lm(smf.ols("np.log1p(y) ~ C(dir, Sum) * C(tgt, Sum)", s3b).fit(), typ=3).loc["C(dir, Sum)", "PR(>F)"]),
              "cell_means": s3b.groupby(["dir", "tgt"]).y.mean().round(2).to_dict(), "max_by": s3b.groupby("dir").y.max().to_dict()}
rows += [("S3b", "n Jervis/Thurlow", "44/42", "/".join(str(v) for v in s3b.tgt.value_counts().reindex(["Jervis", "Thurlow"]).values)),
         ("S3b", "F orientation (1,82)", 6.86, round(a3b.loc['C(dir, Sum)', 'F'], 2)), ("S3b", "p", .011, round(float(a3b.loc['C(dir, Sum)', 'PR(>F)']), 4)),
         ("S3b", "M toward", 14.36, round(g3b.loc['toward', 'mean'], 2)), ("S3b", "SD toward", 11.99, round(g3b.loc['toward', 'std'], 2)),
         ("S3b", "M away", 25.43, round(g3b.loc['away', 'mean'], 2)), ("S3b", "SD away", 25.78, round(g3b.loc['away', 'std'], 2)),
         ("S3b", "interaction p (>.18)", ">.18", round(float(a3b.loc['C(dir, Sum):C(tgt, Sum)', 'PR(>F)']), 4)),
         ("S3b", "F target (<1)", "<1", round(a3b.loc['C(tgt, Sum)', 'F'], 2))]

# ---------------- Study 4 ----------------
s4 = load("S4_probability.xlsx"); s4.columns = ["cond", "y", "fam"]; s4["cond"] = s4.cond.str.strip().str.lower()
s4["y"] = s4.y.astype(float); s4["fam"] = s4.fam.astype(float); s4["tw"] = (s4.cond == "southbound").astype(int)
F4, p4 = oneway(s4, "y", "cond"); g4 = s4.groupby("cond").y.agg(["mean", "std", "count"])
r4 = stats.pearsonr(s4.fam, s4.y)
fam_p = float(stats.ttest_ind(s4[s4.tw == 1].fam, s4[s4.tw == 0].fam).pvalue)
anc = smf.ols("y ~ tw + fam", s4).fit()
res["s4"] = {"means": g4.round(3).to_dict(), "F": F4, "p": p4, "r_fam": [float(r4[0]), float(r4[1])], "fam_by_cond_p": fam_p,
             "ancova_p": float(anc.pvalues["tw"]), "MW_p": float(stats.mannwhitneyu(s4[s4.tw == 1].y, s4[s4.tw == 0].y).pvalue),
             "value_counts": {c: s4[s4.cond == c].y.value_counts().sort_index().to_dict() for c in ("southbound", "northbound")}}
rows += [("S4", "M toward", 4.00, round(g4.loc['southbound', 'mean'], 2)), ("S4", "SD toward", 1.73, round(g4.loc['southbound', 'std'], 2)),
         ("S4", "M away", 2.80, round(g4.loc['northbound', 'mean'], 2)), ("S4", "SD away", 1.71, round(g4.loc['northbound', 'std'], 2)),
         ("S4", "F(1,48)", 6.09, round(F4, 2)), ("S4", "p", .017, round(p4, 4)), ("S4", "r familiarity", -.343, round(r4[0], 3)),
         ("S4", "p r", .02, round(float(r4[1]), 4)), ("S4", "ANCOVA p", .009, round(float(anc.pvalues['tw']), 4)), ("S4", "fam x cond p (>.80)", ">.80", round(fam_p, 3))]

# ---------------- Study 5 ----------------
s5 = load("S5_LA_Chicago.xlsx"); s5.columns = ["cond", "y"]; s5["cond"] = s5.cond.str.strip().str.lower(); s5["y"] = s5.y.astype(float)
F5, p5 = oneway(s5, "y", "cond"); g5 = s5.groupby("cond").y.agg(["mean", "std", "count"])
res["s5"] = {"means": g5.round(3).to_dict(), "F": F5, "p": p5, "MW_p": float(stats.mannwhitneyu(s5[s5.cond == "departing"].y, s5[s5.cond == "arriving"].y).pvalue),
             "welch_p": float(stats.ttest_ind(s5[s5.cond == "departing"].y, s5[s5.cond == "arriving"].y, equal_var=False).pvalue),
             "value_counts": {c: s5[s5.cond == c].y.value_counts().sort_index().to_dict() for c in ("departing", "arriving")}}
rows += [("S5", "n dep/arr", "22/23", f"{int(g5.loc['departing','count'])}/{int(g5.loc['arriving','count'])}"),
         ("S5", "M toward (departing)", 2.41, round(g5.loc['departing', 'mean'], 2)), ("S5", "SD toward", 1.59, round(g5.loc['departing', 'std'], 2)),
         ("S5", "M away (arriving)", 1.61, round(g5.loc['arriving', 'mean'], 2)), ("S5", "SD away", 1.03, round(g5.loc['arriving', 'std'], 2)),
         ("S5", "F(1,43)", 4.03, round(F5, 2)), ("S5", "p", .051, round(p5, 4))]

res["table"] = rows
print(f"{'study':5s} {'quantity':34s} {'published':>10s}  recomputed")
for r in rows:
    print(f"{r[0]:5s} {r[1]:34s} {str(r[2]):>10s}  {r[3]}")
print("\nS1 simple effects:", json.dumps(simple, indent=0, default=str)[:1500])
print("\nS1 toward model:", res["s1_toward_model"], "\nmeans (near,toward):", res["s1_toward_means"], "MW p", res["s1_toward_MW"])
for k in ("s2", "s3a", "s3b", "s4", "s5"):
    print(k, {kk: vv for kk, vv in res[k].items() if kk not in ("anova", "means")})
def _k(o):
    if isinstance(o, dict): return {("|".join(map(str, k)) if isinstance(k, tuple) else str(k)): _k(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [_k(v) for v in o]
    return o
# S3b target effect by sum-of-squares type (paper: F < 1)
res["s3b_target_F_by_type"] = {t: round(float(anova_lm(m3b, typ=t).loc["C(tgt, Sum)", "F"]), 3) for t in (1, 2, 3)}
res["s3b_target_oneway"] = oneway(s3b, "y", "tgt")
print("S3b target F by SS type:", res["s3b_target_F_by_type"], "one-way", res["s3b_target_oneway"])
json.dump(_k(res), open(os.path.join(OUT, "r01.json"), "w"), indent=1, default=str)
