"""h01 -- Huang et al. 2024 (ICLR, arXiv 2310.01798): exact McNemar tests from Figure 1's answer transitions.

Figure 1 gives, after two rounds of intrinsic self-correction, the share of questions in
{No change, Incorrect->Incorrect, Incorrect->Correct, Correct->Incorrect}. The discordant pairs that
change accuracy are I->C (b) and C->I (c). Exact two-sided McNemar = binomial test of b vs c at 0.5.
n: GPT-3.5 used full sets (GSM8K test 1319, CommonSenseQA dev 1221 -- the paper says 'full evaluation
set'); GPT-4, GPT-4-Turbo, Llama-2 used 200 sampled questions.
Known-answer check: net change b - c must equal the accuracy change Standard -> round 2 in Tables 3-4.
Run: python -I h01_mcnemar_from_transitions.py
"""
import json, math, os

def binom_two_sided(k, n):
    if n == 0: return 1.0
    pk = [math.comb(n, i) / 2 ** n for i in range(n + 1)]
    obs = pk[k]
    return min(1.0, sum(p for p in pk if p <= obs + 1e-15))

# (model, task): (n, nochange, I->I, I->C, C->I, acc_std, acc_round2)
F = {
 ("GPT-3.5", "GSM8K"): (1319, 74.7, 8.9, 7.6, 8.8, 75.9, 74.7),
 ("GPT-3.5", "CommonSenseQA"): (1221, 42.8, 11.6, 5.8, 39.8, 75.8, 41.8),
 ("GPT-4", "GSM8K"): (200, 90.5, 0.0, 1.5, 8.0, 95.5, 89.0),
 ("GPT-4", "CommonSenseQA"): (200, 90.5, 1.5, 3.0, 5.0, 82.0, 80.0),
 ("GPT-4-Turbo", "GSM8K"): (200, 96.0, 0.5, 1.0, 2.5, 91.5, 90.0),
 ("GPT-4-Turbo", "CommonSenseQA"): (200, 88.0, 1.0, 5.0, 6.0, 84.0, 83.0),
 ("Llama-2-70b", "GSM8K"): (200, 40.0, 23.5, 5.5, 31.0, 62.0, 36.5),
 ("Llama-2-70b", "CommonSenseQA"): (200, 40.0, 16.5, 8.0, 35.5, 64.0, 36.5),
}
out = {}
for (m, t), (n, nc, ii, ic, ci, a0, a2) in F.items():
    b, c = round(ic / 100 * n), round(ci / 100 * n)
    out[f"{m}/{t}"] = {"n": n, "I->C": b, "C->I": c, "net_pp_from_fig": round(ic - ci, 1),
                       "net_pp_from_tables": round(a2 - a0, 1),
                       "consistent": abs((ic - ci) - (a2 - a0)) < 0.15,
                       "shares_sum": round(nc + ii + ic + ci, 1),
                       "mcnemar_exact_p": round(binom_two_sided(b, b + c), 4)}
# Table 7: debate (9 responses) vs self-consistency (9) on GSM8K full test (1319), unpaired screen
d, s = 0.830, 0.882
se = math.sqrt(d * (1 - d) / 1319 + s * (1 - s) / 1319)
out["debate9_vs_selfconsistency9"] = {"diff_pp": round(100 * (d - s), 1), "z_unpaired": round((d - s) / se, 2)}
here = os.path.dirname(os.path.abspath(__file__))
json.dump(out, open(os.path.join(here, "h01_out.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
