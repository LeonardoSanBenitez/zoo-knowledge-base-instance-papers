"""c03 -- PLAN_c03_code_k.md executed: expected positives under honest multiplicity with each trial's OWN abstract k.
Usage: python c03_estimate_with_coded_k.py <s003.docx>    (reads c03_codes.jsonl next to this script) -> out/c03.json
"""
import json, os, re, sys, zipfile
import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
x = zipfile.ZipFile(sys.argv[1]).read("word/document.xml").decode("utf8")
S3 = {}
for tr in re.findall(r"<w:tr[ >].*?</w:tr>", x, re.S)[1:]:
    c = [re.sub(r"<[^>]+>", "", "".join(re.findall(r"<w:t[^>]*>[^<]*</w:t>", tc))) for tc in re.findall(r"<w:tc>.*?</w:tc>", tr, re.S)]
    m = re.match(r"\s*(\d+)\s*/\s*(\d+)", c[5])
    S3[c[0]] = {"pos": c[1].strip().lower().startswith("pos"), "n1": int(m.group(1)), "n2": int(m.group(2)), "power": float(c[6]) / 100}
codes = [json.loads(l) for l in open(os.path.join(HERE, "c03_codes.jsonl"), encoding="utf-8") if l.strip()]
rows = []
for cd in codes:
    s = S3[cd["label"]]
    rows.append({**cd, **s})
k_bg = np.array([r["k_bg"] for r in rows]); s_bg = np.array([r["s_bg"] for r in rows])
unclear = np.array([r["unclear"] for r in rows]); within = np.array([r["within_only"] for r in rows])
pos = np.array([r["pos"] for r in rows]); n1 = np.array([r["n1"] for r in rows]); n2 = np.array([r["n2"] for r in rows])
pw = np.array([r["power"] for r in rows])
k_use = np.where((k_bg == 0) | (unclear == 1), 1, k_bg)
res = {"n_coded": len(rows), "n_unclear": int(unclear.sum()), "n_within_only": int(within.sum()),
       "k_bg_dist": {int(v): int((k_bg == v).sum()) for v in sorted(set(k_bg))},
       "k_bg_mean_clear": round(float(k_bg[(unclear == 0) & (k_bg > 0)].mean()), 2),
       "k_bg_median_clear": float(np.median(k_bg[(unclear == 0) & (k_bg > 0)])),
       "share_k_ge3_clear": round(float(np.mean(k_bg[(unclear == 0) & (k_bg > 0)] >= 3)), 3),
       "observed_positive_subsample": int(pos.sum()),
       "paper_single_test_expected_subsample_d055": round(float(pw.sum()), 1),
       "reported_outcomes_significant_share": round(float(s_bg.sum() / max(k_bg.sum(), 1)), 3),
       "trials_all_reported_significant": int(((k_bg > 0) & (s_bg == k_bg)).sum()),
       "trials_with_k_bg_gt0": int((k_bg > 0).sum())}
# positivity by my own coding (>= 1 significant between-groups) vs the paper's
res["my_bg_positive"] = int((s_bg > 0).sum())
res["paper_positive_but_no_bg_sig_in_my_coding"] = int((pos & (s_bg == 0)).sum())
rng = np.random.default_rng(7)


def p_any(d, a, b, k, rho, reps=20000):
    ncp = d * np.sqrt(a * b / (a + b))
    z = ncp + np.sqrt(rho) * rng.normal(size=(reps, 1)) + np.sqrt(1 - rho) * rng.normal(size=(reps, k))
    return float(np.mean(z.max(1) > 1.96))


grid = {}
for d in (0.0, 0.30, 0.44, 0.55):
    for rho in (0.3, 0.5, 0.7):
        e = sum(p_any(d, a, b, int(k), rho) for a, b, k in zip(n1, n2, k_use))
        grid[f"d{d}_rho{rho}"] = round(e, 1)
res["expected_honest_own_k"] = grid
obs = pos.sum()
e = grid["d0.44_rho0.5"]
res["decision_rule_d044_rho05"] = {"expected": e, "observed": int(obs), "shortfall_share": round(float((obs - e) / obs), 3),
                                   "verdict": "accounting artifact" if (obs - e) / obs <= 0.15 else ("excess survives" if (obs - e) / obs > 0.30 else "in between")}
# also with the abstract's k as LOWER bound -- what k multiplier would close the gap at d = .44, rho = .5?
for mult in (1.5, 2.0, 3.0):
    kk = np.maximum(1, np.round(k_use * mult)).astype(int)
    res[f"expected_d044_rho05_k_times_{mult}"] = round(sum(p_any(0.44, a, b, int(k), 0.5) for a, b, k in zip(n1, n2, kk)), 1)
print(json.dumps(res, indent=1))
os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
json.dump(res, open(os.path.join(HERE, "out", "c03.json"), "w"), indent=1)
