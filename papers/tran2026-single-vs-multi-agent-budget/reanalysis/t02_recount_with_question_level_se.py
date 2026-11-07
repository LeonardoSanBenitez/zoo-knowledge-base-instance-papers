"""t02 -- Recount Table 1 of Tran & Kiela 2026 with question-level binomial SEs.

For each of 8 (dataset, model) rows x 6 budgets: best single-agent (max of SAS, SAS-L) vs best multi-agent
(max of Seq, Sub, Roles, Deb, Ens). z = diff / sqrt(p1q1/n + p2q2/n), n = 824 (FRAMES) or 405 (MuSiQue
4-hop dev; the paper does not state n, so 405 is our assumption). Unpaired SE is conservative (the same
questions are used, so the paired SE is smaller), and taking the max over 5 MAS variants favours MAS
(selection), so 'MAS significantly better' counts are upper bounds. Values transcribed from Table 1 (p.7).
Run: python t02_recount_with_question_level_se.py
"""
import json, math, os

B = ["100", "500", "1k", "2k", "5k", "10k"]
# rows: (dataset, model): {budget: [SAS, SAS-L, Seq, Sub, Roles, Deb, Ens]}
T = {
 ("FRAMES", "Qwen3-30B"): [[.191,.195,.198,.155,.207,.204,.146],[.240,.220,.223,.187,.223,.206,.193],[.252,.235,.225,.220,.240,.228,.210],[.250,.246,.252,.232,.256,.232,.230],[.260,.246,.252,.237,.265,.238,.254],[.263,.246,.258,.244,.271,.240,.263]],
 ("MuSiQue", "Qwen3-30B"): [[.200,.210,.220,.174,.202,.225,.149],[.250,.213,.226,.187,.204,.229,.183],[.260,.231,.229,.207,.220,.224,.197],[.271,.239,.229,.234,.226,.234,.224],[.271,.248,.231,.249,.246,.249,.226],[.271,.248,.231,.254,.242,.244,.245]],
 ("FRAMES", "DeepSeek-R1-70B"): [[.365,.374,.387,.385,.427,.400,.365],[.427,.432,.396,.402,.407,.392,.400],[.448,.448,.391,.420,.425,.397,.419],[.454,.451,.393,.434,.433,.425,.431],[.455,.444,.394,.436,.448,.439,.450],[.456,.445,.397,.434,.450,.444,.458]],
 ("MuSiQue", "DeepSeek-R1-70B"): [[.294,.316,.328,.309,.316,.308,.316],[.383,.375,.332,.303,.329,.320,.319],[.407,.402,.320,.317,.334,.315,.323],[.418,.411,.327,.317,.335,.352,.346],[.419,.412,.323,.317,.345,.357,.334],[.417,.412,.327,.319,.354,.360,.330]],
 ("FRAMES", "G2.5-Flash"): [[.333,.427,.462,.365,.441,.445,.284],[.487,.459,.494,.442,.451,.470,.384],[.551,.484,.507,.482,.495,.527,.458],[.532,.517,.526,.509,.536,.527,.498],[.545,.542,.524,.532,.545,.552,.539],[.547,.546,.516,.541,.556,.564,.559]],
 ("MuSiQue", "G2.5-Flash"): [[.263,.352,.272,.264,.300,.318,.243],[.340,.352,.287,.291,.311,.329,.274],[.331,.354,.287,.313,.306,.328,.299],[.334,.369,.283,.323,.330,.349,.320],[.344,.364,.289,.332,.340,.355,.338],[.338,.369,.285,.335,.349,.354,.343]],
 ("FRAMES", "G2.5-Pro"): [[.368,.451,.654,.530,.609,.649,.407],[.600,.450,.660,.562,.598,.660,.400],[.680,.610,.670,.596,.600,.638,.430],[.700,.680,.690,.637,.658,.660,.558],[.700,.690,.680,.652,.700,.700,.710],[.692,.692,.691,.655,.718,.697,.719]],
 ("MuSiQue", "G2.5-Pro"): [[.308,.373,.393,.364,.400,.412,.302],[.391,.423,.391,.363,.397,.435,.330],[.413,.414,.400,.397,.430,.444,.325],[.412,.449,.414,.381,.409,.448,.372],[.419,.455,.392,.417,.447,.470,.434],[.428,.436,.392,.410,.447,.458,.445]],
}
N = {"FRAMES": 824, "MuSiQue": 405}
rows, tally = [], {"SA_sig_better": 0, "MA_sig_better": 0, "neither": 0}
tally_ex100 = dict(tally)
for (ds, model), grid in T.items():
    n = N[ds]
    for b, v in zip(B, grid):
        sa, ma = max(v[:2]), max(v[2:])
        se = math.sqrt(sa * (1 - sa) / n + ma * (1 - ma) / n)
        z = (sa - ma) / se
        k = "SA_sig_better" if z > 1.96 else "MA_sig_better" if z < -1.96 else "neither"
        tally[k] += 1
        if b != "100": tally_ex100[k] += 1
        rows.append({"dataset": ds, "model": model, "budget": b, "best_SA": sa, "best_MA": ma, "z": round(z, 2), "verdict": k})
out = {"tally_all_48": tally, "tally_excluding_100": tally_ex100,
       "SA_sig_cells": [r for r in rows if r["verdict"] == "SA_sig_better"],
       "MA_sig_cells": [r for r in rows if r["verdict"] == "MA_sig_better"]}
here = os.path.dirname(os.path.abspath(__file__))
json.dump({**out, "rows": rows}, open(os.path.join(here, "t02_out.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
