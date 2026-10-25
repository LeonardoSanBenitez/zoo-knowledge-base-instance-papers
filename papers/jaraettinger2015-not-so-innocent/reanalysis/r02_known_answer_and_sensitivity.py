"""Known-answer test of the paper's inferential tools at its own sample size, plus two sensitivities.

(a) NULL: both groups p = 0.5 (and p = 0.3125 / 0.6875 pooled-rate variants), n = 16 each.
    How often does the authors' procedure -- a non-stratified 'basic' bootstrap 95% CI of the difference
    in proportions -- exclude 0? How often does Fisher's exact test give p < .05?  A calibrated 95% tool
    should be near 5%.
(b) EFFECT FORCED IN: p1 = 11/16, p2 = 5/16 (exactly the nicer-vs-baseline effect the paper observed).
    Power of each tool at n = 16 per group, i.e. how likely the study was to detect what it reports.
(c) Sensitivities on the deposited counts: the exact duplicate row in the control condition removed;
    non-responders (no choice in 30 s) counted at the bounds.
No arguments; deterministic seed. Writes out/r02.json.
"""
import json, os
from math import comb
import numpy as np

rng = np.random.default_rng(7)
N = 16

def fisher_two_sided(a, b, c, d):
    r1, r2, c1 = a + b, c + d, a + c
    n = r1 + r2
    p = lambda x: comb(r1, x) * comb(r2, c1 - x) / comb(n, c1)
    po = p(a)
    return sum(p(x) for x in range(max(0, c1 - r2), min(r1, c1) + 1) if p(x) <= po * (1 + 1e-7))

# precompute Fisher p for every table with n=16 per row
FP = np.array([[fisher_two_sided(i, N - i, j, N - j) for j in range(N + 1)] for i in range(N + 1)])

def basic_ci_excludes_zero(xa, xb, B=2000):
    x = np.r_[xa, xb]; g = np.r_[np.zeros(len(xa)), np.ones(len(xb))]
    idx = rng.integers(0, len(x), (B, len(x)))
    xs, gs = x[idx], g[idx]
    na = (gs == 0).sum(1); nb = (gs == 1).sum(1); ok = (na > 0) & (nb > 0)
    t = (xs * (gs == 0)).sum(1)[ok] / na[ok] - (xs * (gs == 1)).sum(1)[ok] / nb[ok]
    t0 = xa.mean() - xb.mean()
    lo = 2 * t0 - np.quantile(t, 0.975); hi = 2 * t0 - np.quantile(t, 0.025)
    return (lo > 0) or (hi < 0)

def rates(p1, p2, sims):
    boot = fish = 0
    for _ in range(sims):
        ka, kb = rng.binomial(N, p1), rng.binomial(N, p2)
        xa = np.r_[np.ones(ka), np.zeros(N - ka)]; xb = np.r_[np.ones(kb), np.zeros(N - kb)]
        boot += basic_ci_excludes_zero(xa, xb)
        fish += FP[ka, kb] < 0.05
    return boot / sims, fish / sims

out = {}
for lab, p1, p2 in (("null_p0.5", .5, .5), ("null_p0.6875", .6875, .6875), ("null_p0.3125", .3125, .3125),
                    ("effect_11v5", 11 / 16, 5 / 16)):
    b, f = rates(p1, p2, 4000)
    out[lab] = {"bootstrap_CI_excludes_0": b, "fisher_p_lt_05": f, "sims": 4000}
    print(f"{lab:14s}  basic-bootstrap CI excludes 0: {b:.3f}   Fisher p<.05: {f:.3f}")

# exact (non-simulated) Fisher power at the observed effect
pw = sum(comb(N, i) * (11/16)**i * (5/16)**(N-i) * comb(N, j) * (5/16)**j * (11/16)**(N-j)
         for i in range(N + 1) for j in range(N + 1) if FP[i, j] < 0.05)
out["fisher_power_exact_11v5"] = pw
print(f"exact Fisher power for a true 11/16 vs 5/16 difference at n=16/16: {pw:.3f}")

# (c) sensitivities
sens = {}
sens["nicer_vs_control_as_published"] = fisher_two_sided(5, 11, 11, 5)
sens["nicer_vs_control_duplicate_removed(control 10/15)"] = fisher_two_sided(5, 11, 10, 5)
# non-responders: nicer 5, control 3. Bounds on 'incompetent chosen'.
sens["nicer_vs_control_nonresponders_against_paper"] = fisher_two_sided(5 + 5, 11, 11, 5 + 3)  # nicer NR->competent, control NR->incompetent
sens["nicer_vs_control_nonresponders_for_paper"] = fisher_two_sided(5, 11 + 5, 11 + 3, 5)
sens["play_vs_nicer_as_published"] = fisher_two_sided(13, 3, 5, 11)
# pooled 'refusal, play question' (Exp 2 + Exp 3 play) vs chance
from math import comb as C
k, n = 24, 32
pk = C(n, k) / 2**n
sens["pooled_exp2_exp3play_binomial_two_sided(24/32)"] = sum(C(n, i) / 2**n for i in range(n + 1) if C(n, i) / 2**n <= pk * (1 + 1e-9))
out["sensitivity_p"] = sens
for k_, v in sens.items():
    print(f"{k_:58s} p = {v:.4f}")

od = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(od, exist_ok=True)
with open(os.path.join(od, "r02.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(out, f, indent=1)

# (d) added after (a): Fisher is conservative here (1.6-1.8% under the null), so test the same tables with
#     unconditional exact tests, which do not condition on both margins.
from scipy.stats import boschloo_exact, barnard_exact
unc = {}
for lab, tab in (("nicer_vs_control", [[5, 11], [11, 5]]), ("play_vs_nicer", [[13, 3], [5, 11]])):
    unc[lab] = {"boschloo": float(boschloo_exact(tab, alternative="two-sided").pvalue),
                "barnard": float(barnard_exact(tab, alternative="two-sided").pvalue)}
    print(f"{lab:18s} Boschloo p = {unc[lab]['boschloo']:.4f}   Barnard p = {unc[lab]['barnard']:.4f}")
out["unconditional_exact"] = unc
with open(os.path.join(od, "r02.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(out, f, indent=1)
