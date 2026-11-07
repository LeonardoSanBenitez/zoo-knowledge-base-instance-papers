"""t01 -- Tran & Kiela 2026 (arXiv 2604.02460v2): are the appendix 95% bootstrap CIs consistent with
their own point estimates?

The paper's 'statistically indistinguishable from the best' (Table 1 bolding) rests on CI overlap from
Appendix Tables 3-10. Two properties any percentile bootstrap CI of an accuracy should have:
  (1) it contains the point estimate, roughly centrally: position = (p - lo)/(hi - lo) near 0.5;
  (2) its width matches the binomial width for the number of questions: n_implied =
      p(1-p) * (2*1.96 / width)^2 should be the dataset size (FRAMES 824; MuSiQue-Ans dev 4-hop 405,
      unless a subset was used, which the paper does not state).
Known-answer control: run the same two checks on CIs we generate ourselves by percentile bootstrap of
simulated 0/1 outcomes at n = 824 -- they must give position ~0.5 and n_implied ~824.
Input: the PDF text (path given as argv[1]); parsing is by the 'Table k:' captions and '95% CI' rows.
Run: python t01_bootstrap_ci_consistency.py <paper.txt>
"""
import json, os, re, sys
import numpy as np

txt = open(sys.argv[1], encoding="utf-8", errors="replace").read().splitlines()
pair = re.compile(r"^\((\d?\.\d+),\s*(\d?\.\d+)\)$")
num = re.compile(r"^\d?\.\d+$")
SYSTEMS = {"SAS", "SAS-L", "Seq", "Sub", "Roles", "Deb", "Ens", "Sequential", "Subtask-parallel",
           "Parallel-roles", "Debate", "Ensemble"}

cells, table = [], None
i = 0
while i < len(txt):
    line = txt[i].strip()
    m = re.match(r"^Table (\d+): (.*)", line)
    if m:
        k = int(m.group(1))
        table = (k, m.group(2)) if 3 <= k <= 10 else None
    if table and line in SYSTEMS:
        vals, j = [], i + 1
        while j < len(txt) and num.match(txt[j].strip()) and len(vals) < 6:
            vals.append(float(txt[j].strip())); j += 1
        if j < len(txt) and txt[j].strip() == "95% CI":
            cis, j = [], j + 1
            while j < len(txt) and pair.match(txt[j].strip()) and len(cis) < 6:
                a, b = pair.match(txt[j].strip()).groups(); cis.append((float(a), float(b))); j += 1
            for b_idx, (p, (lo, hi)) in enumerate(zip(vals, cis)):
                cells.append({"table": table[0], "dataset": "FRAMES" if "FRAMES" in table[1] else "MuSiQue",
                              "system": line, "budget_idx": b_idx, "p": p, "lo": lo, "hi": hi})
            i = j; continue
    i += 1

def summarize(cs, label):
    pos, nimp, outside = [], [], 0
    for c in cs:
        w = c["hi"] - c["lo"]
        if w <= 0: continue
        pos.append((c["p"] - c["lo"]) / w)
        outside += not (c["lo"] - 1e-9 <= c["p"] <= c["hi"] + 1e-9)
        nimp.append(c["p"] * (1 - c["p"]) * (2 * 1.96 / w) ** 2)
    pos, nimp = np.array(pos), np.array(nimp)
    return {"label": label, "cells": len(pos), "point_outside_CI": int(outside),
            "position_median": round(float(np.median(pos)), 3),
            "position_frac_in_outer_10pct": round(float(np.mean((pos < 0.1) | (pos > 0.9))), 3),
            "n_implied_median": int(np.median(nimp)), "n_implied_p10_p90": [int(np.percentile(nimp, 10)), int(np.percentile(nimp, 90))]}

out = {"parsed_cells": len(cells),
       "FRAMES": summarize([c for c in cells if c["dataset"] == "FRAMES"], "FRAMES (n should be 824)"),
       "MuSiQue": summarize([c for c in cells if c["dataset"] == "MuSiQue"], "MuSiQue 4-hop (n 405 if full dev 4-hop)")}

# known-answer control
rng = np.random.default_rng(2460)
ctrl = []
for _ in range(200):
    p = rng.uniform(0.2, 0.7); n = 824
    y = rng.random(n) < p
    boots = [y[rng.integers(0, n, n)].mean() for _ in range(1000)]
    ctrl.append({"p": round(float(y.mean()), 3), "lo": round(float(np.percentile(boots, 2.5)), 3),
                 "hi": round(float(np.percentile(boots, 97.5)), 3)})
out["control_our_bootstrap_n824"] = summarize(ctrl, "our percentile bootstrap, n=824")
out["examples"] = [c for c in cells if c["table"] == 3][:6]

here = os.path.dirname(os.path.abspath(__file__))
json.dump(out, open(os.path.join(here, "t01_out.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "examples"}, indent=1))
