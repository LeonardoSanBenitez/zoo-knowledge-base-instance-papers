"""b01 -- MLR-Bench (arXiv 2505.19955): does the MLR-Judge validation test distinguish a judge that reads
the paper from one that does not?

Paper's test (human_eval/compute_agreement_score.ipynb, reproduced exactly): per criterion, pool
|human_i - human_j| over reviewer pairs on the same paper, and |human - LLM| over (reviewer, paper);
Mann-Whitney U two-sided; p > 0.05 is read as 'LLM and human judgments are well-aligned'.

Known-answer judges fed to the SAME test:
  K1 constant judge: every paper gets the rounded mean human score for that criterion (reads nothing).
  K2 shuffled LLM: the real LLM scores permuted across papers (right marginal, no link to the paper);
     1000 permutations -> share of permutations that 'pass' (p > 0.05).
Direct agreement measures the test never computes: Spearman r(LLM, mean human) over papers, and
Spearman r(human A, human B) over doubly-reviewed papers.
Input: merge_data.csv from github.com/chchenhui/mlrbench @ f728d57 (human_eval/); path is argv[1].
Run: python b01_judge_validation_known_answer.py <merge_data.csv>
"""
import json, os, sys
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, spearmanr

df = pd.read_csv(sys.argv[1])
crit = ["Novelty", "Clarity", "Soundness", "Significance", "Overall"]

def vectors(d, llm_cols):
    hh = {c: [] for c in crit}; hl = {c: [] for c in crit}
    for (w, m), g in d.groupby(["workshop_name", "model_name"]):
        revs = g["reviewer_id"].unique()
        if len(revs) >= 2:
            rs = [g[g["reviewer_id"] == r] for r in revs]
            for i in range(len(rs)):
                for j in range(i + 1, len(rs)):
                    for c in crit:
                        v1, v2 = rs[i][f"{c}_human"].values, rs[j][f"{c}_human"].values
                        if len(v1) == len(v2): hh[c].extend(np.abs(v1 - v2))
        for _, row in g.iterrows():
            for c in crit:
                hl[c].append(abs(row[f"{c}_human"] - row[llm_cols[c]]))
    return hh, hl

def test(d, llm_cols):
    hh, hl = vectors(d, llm_cols)
    return {c: float(mannwhitneyu(hh[c], hl[c]).pvalue) for c in crit}, \
           {c: (round(float(np.mean(hh[c])), 2), round(float(np.mean(hl[c])), 2), len(hh[c]), len(hl[c])) for c in crit}

out = {"rows": len(df), "papers": int(df.groupby(["workshop_name", "model_name"]).ngroups)}
p_real, means = test(df, {c: f"{c}_llm" for c in crit})
out["reproduced_p"] = {c: round(v, 3) for c, v in p_real.items()}
out["paper_reported_p"] = {"Novelty": 0.673, "Clarity": 0.055, "Soundness": 0.481, "Significance": 0.513, "Overall": 0.981}
out["mean_abs_diff_hh_hl_n"] = means

# K1 constant judge
d1 = df.copy()
for c in crit:
    d1[f"{c}_const"] = round(df[f"{c}_human"].mean())
p_const, m_const = test(d1, {c: f"{c}_const" for c in crit})
out["K1_constant_judge_p"] = {c: round(v, 3) for c, v in p_const.items()}
out["K1_constant_judge_mean_abs_diff"] = {c: m_const[c][1] for c in crit}

# K2 shuffled LLM scores across papers
rng = np.random.default_rng(19955)
papers = df[["workshop_name", "model_name"] + [f"{c}_llm" for c in crit]].drop_duplicates(["workshop_name", "model_name"]).reset_index(drop=True)
passes = {c: 0 for c in crit}; R = 1000
for _ in range(R):
    perm = papers.copy()
    idx = rng.permutation(len(perm))
    for c in crit:
        perm[f"{c}_llm"] = papers[f"{c}_llm"].values[idx]
    d2 = df.drop(columns=[f"{c}_llm" for c in crit]).merge(perm, on=["workshop_name", "model_name"])
    p2, _ = test(d2, {c: f"{c}_llm" for c in crit})
    for c in crit: passes[c] += p2[c] > 0.05
out["K2_shuffled_llm_share_passing"] = {c: round(passes[c] / R, 3) for c in crit}

# direct agreement
agg = df.groupby(["workshop_name", "model_name"]).agg({**{f"{c}_human": "mean" for c in crit}, **{f"{c}_llm": "first" for c in crit}})
out["spearman_llm_vs_mean_human"] = {c: round(float(spearmanr(agg[f"{c}_llm"], agg[f"{c}_human"]).statistic), 3) for c in crit}
hh_r = {}
for c in crit:
    a, b = [], []
    for _, g in df.groupby(["workshop_name", "model_name"]):
        if g["reviewer_id"].nunique() >= 2:
            v = g.sort_values("reviewer_id")[f"{c}_human"].values
            a.append(v[0]); b.append(v[1])
    hh_r[c] = (round(float(spearmanr(a, b).statistic), 3), len(a))
out["spearman_human_A_vs_B (r, papers)"] = hh_r

here = os.path.dirname(os.path.abspath(__file__))
json.dump(out, open(os.path.join(here, "b01_out.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
