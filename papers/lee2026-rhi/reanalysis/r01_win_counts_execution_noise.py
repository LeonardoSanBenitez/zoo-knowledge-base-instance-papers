"""r01 -- RHI (arXiv 2607.15524): what the error bars leave out, and how much is 'any harness' vs 'RHI'.

Inputs: win counts out of 30 tasks, read off Figs 5a and 7 at 150-400 dpi (+-0.5; renders fig5a.png,
p14.png in the download folder). Each bar = mean over 3 judge seeds; the error bar = SD over judge seeds.
Every harness H[i] and every baseline is EXECUTED ONCE per task (Sec 5.1, Alg. 1), so the bars carry
judging noise only; execution noise -- which the follow-up MASS paper shows is large (an identical
workflow went 6-0 then 0-6, MASS Table 11) -- is absent from every interval in the paper.

A. Execution-noise SD of a 30-task win count: sqrt(sum p_t(1-p_t)) <= sqrt(7.5) = 2.74; computed for
   heterogeneous p_t ~ Beta with the observed mean and a range of dispersions.
B. Decomposition (opus-4.8, sonnet-4.6): bare -> H[0] (unoptimised starting harness) -> best H[i].
C. Null for the sonnet sequence 14,16,20.3,20.3,22.3 (gpt judge): if H[1..4] were no better than H[0],
   how often would 5 single-execution win counts look this ordered and this spread?
   Statistic: Kendall tau of (i, W_i) and W_4 - W_0. Known-answer: a forced trend (+2 wins/iteration)
   must be detected most of the time; the null must give ~nominal rates.
Run: python r01_win_counts_execution_noise.py   (numpy)
"""
import json, os, itertools
import numpy as np

rng = np.random.default_rng(15524)
N = 30

FIG5_SONNET_VS_MAX = {"gpt-5.5-max": [14.0, 16.0, 20.3, 20.3, 22.3], "opus-4.7-xhigh": [14.0, 16.0, 21.3, 20.0, 18.7]}
FIG7_OPUS48 = {  # wins of the high-effort player out of 30; [gpt-5.5-max judge, opus-4.8-xhigh judge]
    "vs_xhigh":     {"bare": [7.5, 7.2], "H0": [16.0, 20.0], "H1": [16.3, 18.0], "H2": [22.7, 25.0]},
    "vs_ultracode": {"bare": [4.5, 3.5], "H0": [9.0, 10.0], "H1": [13.3, 12.7], "H2": [20.0, 19.3]},
    "vs_max":       {"bare": [7.3, 4.0], "H0": [14.3, 18.0], "H1": [16.7, 19.3], "H2": [23.3, 23.7]},
}

out = {}
# ---- A ----
A = {}
for mean in (0.5, 0.67):
    for conc in (2.0, 5.0, 1e6):  # Beta concentration; 1e6 = homogeneous p
        a, b = mean * conc, (1 - mean) * conc
        sds = []
        for _ in range(2000):
            p = rng.beta(a, b, N) if conc < 1e5 else np.full(N, mean)
            sds.append(np.sqrt(np.sum(p * (1 - p))))
        A[f"mean{mean}_conc{conc:g}"] = round(float(np.mean(sds)), 2)
A["note"] = ("Execution-noise SD of a 30-task win count is 2.0-2.7 wins unless outcomes are near-deterministic "
             "per task; the SD of a DIFFERENCE between two iterations is about 1.4x that. The paper's error "
             "bars (judge seeds) are 0-2.7 and do not include it.")
out["A_execution_noise_sd"] = A

# ---- B ----
B = {}
for comp, d in FIG7_OPUS48.items():
    for j, judge in enumerate(["gpt-5.5-max", "opus-4.8-xhigh"]):
        bare, h0, h2 = d["bare"][j], d["H0"][j], d["H2"][j]
        B[f"opus48_{comp}_{judge}"] = {"bare_to_H0": round(h0 - bare, 1), "H0_to_H2": round(h2 - h0, 1),
                                       "share_from_unoptimised_harness": round((h0 - bare) / (h2 - bare), 2)}
B["_mean_share_from_H0"] = round(float(np.mean([v["share_from_unoptimised_harness"] for v in B.values()])), 2)
out["B_decomposition"] = B

# ---- C ----
def kendall(x):
    s = 0
    for i, j in itertools.combinations(range(len(x)), 2):
        s += np.sign(x[j] - x[i])
    return s / (len(x) * (len(x) - 1) / 2)

def sim_seq(p_t, slope=0.0, iters=5):
    seq = []
    for i in range(iters):
        logit = np.log(p_t / (1 - p_t)) + slope * i
        q = 1 / (1 + np.exp(-logit))
        seq.append(float(np.sum(rng.random(N) < q)))
    return seq

obs = FIG5_SONNET_VS_MAX["gpt-5.5-max"]
obs_tau, obs_gap = kendall(obs), obs[-1] - obs[0]
C = {"observed": obs, "observed_tau": round(obs_tau, 3), "observed_gap_W4_W0": obs_gap}
R = 20000
for label, conc, slope in [("null_homog", 1e6, 0.0), ("null_conc2", 2.0, 0.0),
                           ("trend_0.3logit_conc2", 2.0, 0.3), ("trend_0.15logit_conc2", 2.0, 0.15)]:
    hits_both, hits_tau = 0, 0
    for _ in range(R):
        m = 14.0 / 30
        p = rng.beta(m * conc, (1 - m) * conc, N) if conc < 1e5 else np.full(N, m)
        p = np.clip(p, 1e-4, 1 - 1e-4)
        s = sim_seq(p, slope)
        t = kendall(s)
        hits_tau += t >= obs_tau - 1e-9
        hits_both += (t >= obs_tau - 1e-9) and (s[-1] - s[0] >= obs_gap - 0.5)
    C[label] = {"P(tau>=obs)": round(hits_tau / R, 4), "P(tau>=obs and gap>=obs)": round(hits_both / R, 4)}
C["reading"] = ("Under the null the sonnet sequence is rare (a few per thousand at most) -> the sonnet trend is "
                "unlikely to be pure execution noise, even with single executions. The opus-4.8 H0->H1 step "
                "(+0.3 / -2.0 wins vs xhigh) is inside noise; only H2 separates.")
out["C_sonnet_trend_null"] = C

here = os.path.dirname(os.path.abspath(__file__))
json.dump(out, open(os.path.join(here, "r01_out.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
