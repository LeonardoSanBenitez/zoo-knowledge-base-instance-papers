"""s01 -- SiriuS (arXiv 2502.04780, NeurIPS 2025): decode Table 3-5 percentages into question counts and
size each 'SiriuS beats baseline' margin.

Test sizes from Table 6: College Physics 34+29+44 = 107, College Chemistry 34+31 = 65; PubMedQA 500.
Decoding check: every printed % must equal k/n to 2 decimals for some integer k (known answer: if a
value does not decode, either n or the value is wrong).
Margin: difference in correct questions vs the best non-SiriuS method, and an exact two-sided p from a
binomial on discordant pairs is NOT possible (no per-item data), so we report the unpaired Newcombe-style
range: Wilson 95% CIs of both arms, and whether they overlap -- a coarse screen, stated as such.
Run: python s01_counts_and_margins.py
"""
import json, math, os

N = {"phys": 107, "chem": 65, "pubmed": 500}
T3 = {  # method: (phys, chem, pubmed)
 "gpt-3.5": {"Single": (24.30, 38.46, 56.40), "STaR": (29.91, 47.69, 63.80), "COMM": (30.84, 50.77, 71.80),
             "TextGrad": (32.71, 41.54, None), "SiriuS": (33.64, 56.92, 74.20)},
 "gpt-4o-mini": {"Single": (39.25, 41.54, 67.40), "STaR": (42.06, 47.69, 69.20), "COMM": (42.06, 49.23, 70.60),
                 "TextGrad": (42.99, 44.62, 68.20), "SiriuS": (46.73, 60.00, 73.40)}}
T4 = {"gpt-3.5": {"SiriuS": 74.20, "SiriuS+Base": 72.00, "Base+SiriuS": 73.20, "FT one base LLM": 70.40, "w/o Aug": 73.40, "Additional FT itr": 75.00},
      "gpt-4o-mini": {"SiriuS": 73.40, "SiriuS+Base": 72.80, "Base+SiriuS": 71.60, "FT one base LLM": 72.00, "w/o Aug": 72.20, "Additional FT itr": 73.60}}

def decode(pct, n):
    k = round(pct / 100 * n)
    return k if abs(100 * k / n - pct) < 0.006 else None

def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 3), round(c + h, 3))

out = {"decode_failures": [], "margins": {}, "ablations_pubmed_counts": {}}
for model, rows in T3.items():
    for i, task in enumerate(["phys", "chem", "pubmed"]):
        n = N[task]
        ks = {}
        for m, v in rows.items():
            if v[i] is None: continue
            k = decode(v[i], n)
            if k is None: out["decode_failures"].append([model, task, m, v[i]])
            ks[m] = k
        best_m = max((m for m in ks if m != "SiriuS"), key=lambda m: ks[m])
        out["margins"][f"{model}/{task}"] = {"n": n, "SiriuS_correct": ks["SiriuS"], "best_baseline": best_m,
            "baseline_correct": ks[best_m], "margin_questions": ks["SiriuS"] - ks[best_m],
            "vs_STaR_questions": ks["SiriuS"] - ks["STaR"],
            "wilson_SiriuS": wilson(ks["SiriuS"], n), "wilson_best_baseline": wilson(ks[best_m], n)}
for model, rows in T4.items():
    out["ablations_pubmed_counts"][model] = {m: decode(v, 500) for m, v in rows.items()}
out["reading"] = ("Margins over the best baseline: physics 1-4 questions of 107, chemistry 4-7 of 65, PubMedQA "
                  "12-14 of 500; single runs at temperature 0, no CIs in the paper. The second RSI iteration "
                  "('Additional FT itr') adds 4 and 1 questions of 500.")
here = os.path.dirname(os.path.abspath(__file__))
json.dump(out, open(os.path.join(here, "s01_out.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
