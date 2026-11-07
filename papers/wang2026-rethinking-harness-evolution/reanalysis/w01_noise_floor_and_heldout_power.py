"""w01 -- Wang et al. 2026 (arXiv 2607.12227v4): how large must a difference be to be seen?

A. Built-in replicate: 'direct sampling using initial harness' is the same procedure in Table 1 and
   Table 2 (unit tests play no role in direct sampling), run separately. Its two values per model are
   a free measurement of run-to-run noise on 89 tasks x 2 runs.
B. Held-out power (Table 3: 34 test tasks x 2 runs per arm). Simulate tasks with p_t ~ Beta (mean 0.63,
   matching the 63.2 baseline), arms run independently; a true harness gain of +delta pp (logit shift).
   What is P(observed gain <= +1.2) -- i.e. how often would a REAL gain look like Table 3?
   Known answers: delta=0 gives a symmetric distribution around 0.
C. The 'overfitting' contrast: in-sample pass@1 gains of Harness Evolution over direct sampling
   (Tables 1-2) vs held-out (Table 3). Overfitting needs an in-sample gain to lose.
Run: python w01_noise_floor_and_heldout_power.py   (numpy)
"""
import json, os
import numpy as np

rng = np.random.default_rng(12227)
out = {}

t1 = {"opus46": 69.9, "gpt54": 75.3, "gpt54mini": 59.4}
t2 = {"opus46": 69.9, "gpt54": 75.9, "gpt54mini": 56.9}
out["A_same_procedure_two_runs_pp"] = {m: round(t2[m] - t1[m], 1) for m in t1}
out["A_note"] = ("Same configuration, two separate evaluations: differences 0.0, +0.6, -2.5 pp. "
                 "Method differences of about 2 pp on one model are inside this floor.")

def sim(delta_pp, n_tasks=34, runs=2, mean=0.632, conc=1.5, R=20000):
    a, b = mean * conc, (1 - mean) * conc
    res = []
    for _ in range(R):
        p = np.clip(rng.beta(a, b, n_tasks), 1e-3, 1 - 1e-3)
        lo = np.log(p / (1 - p))
        # find logit shift giving +delta_pp on average (approx: solve on this draw)
        if delta_pp == 0:
            p2 = p
        else:
            s_lo, s_hi = -5.0, 5.0
            for _ in range(30):
                s = (s_lo + s_hi) / 2
                if np.mean(1 / (1 + np.exp(-(lo + s)))) - np.mean(p) < delta_pp / 100: s_lo = s
                else: s_hi = s
            p2 = 1 / (1 + np.exp(-(lo + s)))
        base = rng.random((runs, n_tasks)) < p
        evo = rng.random((runs, n_tasks)) < p2
        res.append(100 * (evo.mean() - base.mean()))
    res = np.array(res)
    return res

B = {}
for d in (0, 3, 5, 8):
    r = sim(d)
    B[f"true_gain_{d}pp"] = {"sd_of_observed_gain_pp": round(float(r.std()), 2),
                             "P(observed<=+1.2)": round(float(np.mean(r <= 1.2)), 3),
                             "P(observed<=0)": round(float(np.mean(r <= 0)), 3)}
# three models averaged (independent)
r3 = (sim(5, R=8000) + sim(5, R=8000) + sim(5, R=8000)) / 3
B["three_model_average_true_5pp"] = {"sd": round(float(r3.std()), 2), "P(avg<=0)": round(float(np.mean(r3 <= 0)), 3)}
# calibrate task determinism to the paper's own replicate: E[p(1-p)] implied by RMS(0, 0.6, 2.5) on 89x2
rms = float(np.sqrt(np.mean(np.square([0.0, 0.6, 2.5]))))
epq = (rms / 100) ** 2 * (2 * 89) / 2
# Beta(mean m, conc c): E[p(1-p)] = m(1-m) c/(c+1)  ->  c = epq / (m(1-m) - epq)
m = 0.632
conc_cal = epq / (m * (1 - m) - epq)
B["calibration"] = {"rms_replicate_pp": round(rms, 2), "implied_E_p1mp": round(epq, 4), "implied_beta_conc": round(conc_cal, 3),
                    "caveat": "three replicate pairs only; the identical 69.9 for opus may be a reused run, which would make tasks look more deterministic than they are"}
for d in (0, 5):
    r = sim(d, conc=conc_cal)
    B[f"calibrated_true_gain_{d}pp"] = {"sd_of_observed_gain_pp": round(float(r.std()), 2),
                                        "P(observed<=+1.2)": round(float(np.mean(r <= 1.2)), 3)}
out["B_heldout_power"] = B

C = {"in_sample_gain_no_tests_pp": {"opus46": round(71.4 - 69.9, 1), "gpt54": round(69.7 - 75.3, 1), "gpt54mini": round(61.3 - 59.4, 1), "avg": round(67.4 - 68.2, 1)},
     "in_sample_gain_with_tests_pass1_pp": {"opus46": round(73.0 - 69.9, 1), "gpt54": round(78.6 - 75.9, 1), "gpt54mini": round(57.4 - 56.9, 1), "avg": round(69.7 - 67.6, 1)},
     "heldout_gain_pp": {"opus46": 1.2, "gpt54": 0.0, "gpt54mini": -1.4, "avg": 0.0},
     "reading": ("In-sample pass@1 gains of Harness Evolution are -0.8 (no tests) and +2.1 (tests) on average, "
                 "both inside the replicate floor; held-out is 0.0. There is no in-sample gain for overfitting "
                 "to explain. 'Fails to generalize' is supported as 'no gain anywhere at pass@1', not as a "
                 "train/test gap. The in-sample gain the paper contrasts with is pass@5 (79.0 vs pass@1 base), "
                 "which measures selection among 5 tries, not a better harness.")}
out["C_overfitting_contrast"] = C

here = os.path.dirname(os.path.abspath(__file__))
json.dump(out, open(os.path.join(here, "w01_out.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
