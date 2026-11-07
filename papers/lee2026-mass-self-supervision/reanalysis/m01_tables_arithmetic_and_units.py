"""m01 -- MASS (arXiv 2610.12176): arithmetic checks and re-aggregation of the PDF tables.

All inputs are transcribed from the PDF (v1, 8 Oct 2026); the repo ships no result ledger
(docs/experiment_coverage.md says so). Page numbers refer to the PDF.

Checks:
  A. Table 5 pooled sums and win shares (p.19).
  B. Test-task win share 53.9%: interval at three units (judgment, pair, task).
  C. MLR-Bench and AstaBench aggregate = delivery rate x mean among delivered (p.21) -- is the gain
     entirely completion?
  D. ScienceAgentBench trial counts (p.20): L0 vs L2 at the pooled-run level.
  E. Fig 6 interpolation gaps (8.3, 6.3 pp) and the 1.4x token claim (p.8, p.22-23).
  F. Fig 2 score-per-token ratios: implied change in output tokens = ratio / score ratio.
  G. M+ vs S++ (68.3 vs 64.0) and M vs S: what n supports the difference.
Run: python -I m01_tables_arithmetic_and_units.py  (stdlib only)
"""
import math, json, os

out = {}

def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return round(c - h, 3), round(c + h, 3)

# ---------- A. Table 5 ----------
t5 = {  # task: (split, wins, losses)  10 pairs x 6 judgments each
    51: ("train", 53, 7), 53: ("train", 52, 8), 56: ("train", 38, 22), 202: ("train", 44, 16),
    205: ("train", 12, 48), 302: ("train", 45, 15), 307: ("train", 33, 27), 324: ("train", 38, 22),
    60: ("test", 29, 31), 207: ("test", 27, 33), 305: ("test", 41, 19)}
A = {}
for split, rep_w, rep_l in [("train", 315, 165), ("test", 97, 83)]:
    w = sum(v[1] for v in t5.values() if v[0] == split)
    l = sum(v[2] for v in t5.values() if v[0] == split)
    A[split] = {"wins": w, "losses": l, "reported": [rep_w, rep_l], "match": (w, l) == (rep_w, rep_l),
                "share": round(w / (w + l), 4)}
    for t, v in t5.items():
        assert v[1] + v[2] == 60, t
out["A_table5_sums"] = A

# ---------- B. test win share at three units ----------
test = [t5[t] for t in (60, 207, 305)]
shares = [v[1] / 60 for v in test]
m = sum(shares) / 3
sd = math.sqrt(sum((s - m) ** 2 for s in shares) / 2)
tcrit2 = 4.303  # t_{0.975, df=2}
B = {
    "per_task_share": [round(s, 3) for s in shares],
    "judgment_unit_n180_wilson95": wilson(97, 180),
    # 30 pairs; if the 6 judgments of a pair were perfectly correlated the effective n is 30.
    "pair_unit_n30_wilson95_upper_bound_on_width": wilson(round(0.539 * 30), 30),
    "task_unit_n3_mean": round(m, 3), "task_unit_t95": [round(m - tcrit2 * sd / math.sqrt(3), 3),
                                                       round(m + tcrit2 * sd / math.sqrt(3), 3)],
    "train_tasks_below_50pct": [t for t, v in t5.items() if v[0] == "train" and v[1] < v[2]],
    "test_tasks_below_50pct": [t for t, v in t5.items() if v[0] == "test" and v[1] < v[2]],
}
out["B_test_unit"] = B

# ---------- C. delivery decomposition ----------
C = {}
for name, deliv, n, cond, agg in [
        ("MLR-Bench (12x5)", [31, 36, 50], 60, [3.07, 3.00, 2.88], [1.58, 1.80, 2.40]),
        ("AstaBench E2E-Hard (40x3)", [60, 69, 91], 120, [0.105, 0.095, 0.088], [0.053, 0.055, 0.067])]:
    rows = []
    for g in range(3):
        pred = deliv[g] / n * cond[g]
        rows.append({"gen": g, "delivery": round(deliv[g] / n, 3), "cond_mean": cond[g],
                     "delivery_x_cond": round(pred, 4), "reported_aggregate": agg[g],
                     "rel_err": round(abs(pred - agg[g]) / agg[g], 3)})
    gain = agg[2] / agg[0]
    C[name] = {"rows": rows, "aggregate_ratio_L2_L0": round(gain, 3),
               "delivery_ratio": round(deliv[2] / deliv[0], 3),
               "cond_mean_ratio": round(cond[2] / cond[0], 3),
               "fisher_style_note": "aggregate ratio ~= delivery ratio x cond ratio; cond ratio < 1"}
out["C_delivery_decomposition"] = C

# ---------- D. ScienceAgentBench ----------
sab = {"L0": [28, 31, 29], "L1": [33, 31, 29], "L2": [30, 34, 33]}
k0, k2 = sum(sab["L0"]), sum(sab["L2"])
n = 306
p0, p2 = k0 / n, k2 / n
se = math.sqrt(p0 * (1 - p0) / n + p2 * (1 - p2) / n)
D = {"pooled": {g: [sum(v), n, round(sum(v) / n, 4)] for g, v in sab.items()},
     "L2_minus_L0_pp": round(100 * (p2 - p0), 2),
     "z_independent_runs": round((p2 - p0) / se, 2),
     "note": "z treats 306 runs as independent; the same 102 tasks recur, so the true SE is larger "
             "for task-heterogeneous outcomes; the paper itself makes no significance claim here",
     "trial_means_pct": {g: round(100 * sum(v) / 306, 2) for g, v in sab.items()},
     "text_says": "28.7 -> 31.8 (p.6 body) vs 28.8 -> 31.7 (Table 7): rounding inconsistency"}
out["D_scienceagentbench"] = D

# ---------- E. Fig 6 interpolation ----------
S = [(1.82, 44.0), (9.11, 59.0), (42.0, 64.0)]
def interp(x):
    for (x0, y0), (x1, y1) in zip(S, S[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return None
E = {"M_gap_pp": round(56.0 - interp(3.64), 2), "Mplus_gap_pp": round(68.3 - interp(28.82), 2),
     "reported": [8.3, 6.3], "token_ratio_Spp_over_Mplus": round(42.0 / 28.82, 3),
     "pct_fewer_tokens_Mplus": round(100 * (1 - 28.82 / 42.0), 1),
     "S_below_base": "S (17 single-agent episodes) scores 44.0% vs base: the lower interpolation anchor is a "
                     "model made WORSE than base by fine-tuning, which lifts every gap measured from that line",
     "gap_if_anchor_were_base_50pct_at_S_tokens": round(56.0 - (50 + (59 - 50) * (3.64 - 1.82) / (9.11 - 1.82)), 2)}
out["E_fig6_interpolation"] = E

# ---------- F. Fig 2 score-per-token ratios ----------
# score L0, L2 from Table 7; per-token ratio printed in Fig 2 (p.3)
F = {}
for name, s0, s2, r in [("MLR-Bench", 1.58, 2.40, 1.60), ("DSBench", 0.473, 0.482, 1.35),
                        ("ScienceAgentBench", 28.8, 31.7, 1.20), ("AstaBench", 0.053, 0.067, 1.28),
                        ("Terminal-Bench 2.0", 37.5, 35.2, 0.96), ("SWE-bench Verified", 62.6, 61.1, 0.94)]:
    sr = s2 / s0
    F[name] = {"score_ratio": round(sr, 3), "per_token_ratio": r,
               "implied_token_ratio_L2_over_L0": round(sr / r, 3),
               "share_of_log_gain_from_fewer_tokens": round(math.log(r / sr) / math.log(r), 2) if r > 1 else None}
F["_note"] = ("abstract reports 1.2-1.6x on the four 'research' benchmarks; the two remaining "
              "benchmarks are 0.94x and 0.96x. On DSBench the score change (+0.009, trial SD 0.025-0.029) "
              "is noise-size and ~94% of the log per-token gain is fewer output tokens.")
out["F_per_token"] = F

# ---------- G. M+ vs S++ ----------
def diff_ci(p1, p2, n1, n2):
    se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    return round(p1 - p2, 3), round(se, 3), round((p1 - p2) / se, 2)
G = {"Mplus_vs_Spp_judgment_unit_n300": diff_ci(0.683, 0.640, 300, 300),
     "Mplus_vs_Spp_pair_unit_n50": diff_ci(0.683, 0.640, 50, 50),
     "M_vs_S_judgment_unit": diff_ci(0.560, 0.440, 300, 300),
     "M_vs_S_pair_unit": diff_ci(0.560, 0.440, 50, 50),
     "note": "S++ n not printed (Table 8 dashes); 50 pairs assumed like its siblings. Also S/M/X/S+ "
             "checkpoints were chosen by external judgments on tasks 51/53/56/307, which are 4 of the 5 "
             "evaluation tasks (App. D.1): selection on the evaluation set, and it fixes the x-coordinate "
             "(processed tokens) of Fig 6 as well as the y."}
out["G_student_comparisons"] = G

# ---------- H. README's larger MLR-Bench run (107 tasks x 3 trials; not in the paper) ----------
# README "Benchmark results" (repo commit fb40358): Overall 1.71/1.77/2.25, papers delivered 57/59/76 %.
H = {"aggregate": [1.71, 1.77, 2.25], "delivered": [0.57, 0.59, 0.76]}
H["implied_mean_among_delivered"] = [round(a / d, 3) for a, d in zip(H["aggregate"], H["delivered"])]
H["aggregate_ratio_L2_L0"] = round(2.25 / 1.71, 3)
H["delivery_ratio_L2_L0"] = round(0.76 / 0.57, 3)
H["note"] = ("Independent replication of section C on 107 tasks: implied quality among delivered papers is "
             "flat (about 3.0 at every generation); the whole aggregate gain is the delivery rate. "
             "Implied values are approximate because delivered % is rounded to whole percent.")
out["H_readme_mlr107"] = H

here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "m01_out.json"), "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps(out, indent=1))
