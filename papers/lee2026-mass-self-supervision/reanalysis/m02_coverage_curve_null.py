"""m02 -- Is Fig 3a ("post-trained models discover successful workflows earlier") distinguishable
from a world in which workflow search does nothing at all?

Fig 3a plots C_i = number of the 12 tasks with at least one unanimous (6/6) external win over bare
L(0) among iterations 0..i. That is a running maximum over noisy executions. The paper itself shows
(App. E.3, Table 11) a byte-identical workflow going 6-0 then 0-6, and (Table 10) P(flip) 0.22-0.40
per step independent of edit size. So each iteration is close to a fresh draw.

NULL world (no optimisation): task t has a fixed per-execution probability q_t of a 6/6 win;
iterations are i.i.d. draws. Then the first-hit time of task t is geometric(q_t), and C_i is the
empirical CDF of first-hit times. Optimisation that works = hazard RISING with i.

Data: integer step heights read off Fig 3a at 500 dpi (fig3a.png in the download folder).
  L0: 3,4,7,7,7,7,8,9,9,9,9 (i=0..10)    L1: 5,5,8,10,11,11,11,11,11,11,11    L2: 6,10,11,12,12,12 (i=0..5)
Executor confound: for g>=1, C_i compares L(g)(x+w) against BARE L(0); a better executor raises q
with no optimiser change. Paper's own fixed-executor control is Table 1 (0.64), not Fig 3a.

Models fitted by maximum likelihood on first-hit times (right-censored at the last iteration):
  H0  homogeneous q, no trend                       (1 param)
  H0b beta-geometric: q_t ~ Beta(a,b), no trend      (2 params) -- task heterogeneity
  H1  q_i = sigmoid(alpha + beta*i), homogeneous     (2 params) -- trend; beta>0 = search works
Known-answer checks: simulate worlds with beta = 0 and beta > 0, 12 tasks, same horizon, and see
how often the H1 fit returns beta_hat > 0 and how often LR(H1 vs H0) > 3.84.
Run: python -I m02_coverage_curve_null.py   (numpy, scipy)
"""
import json, os
import numpy as np
from scipy.optimize import minimize
from scipy.special import betaln, expit

CURVES = {"L0": [3, 4, 7, 7, 7, 7, 8, 9, 9, 9, 9],
          "L1": [5, 5, 8, 10, 11, 11, 11, 11, 11, 11, 11],
          "L2": [6, 10, 11, 12, 12, 12]}
N = 12

def first_hits(curve):
    """list of (k, censored) where k = number of draws up to and including first hit (1-based)."""
    out, prev = [], 0
    for i, c in enumerate(curve):
        out += [(i + 1, False)] * (c - prev)
        prev = c
    out += [(len(curve), True)] * (N - prev)
    return out

def nll_h0(p, d):
    q = expit(p[0]); ll = 0
    for k, cen in d:
        ll += k * np.log1p(-q) if cen else (k - 1) * np.log1p(-q) + np.log(q)
    return -ll

def nll_h0b(p, d):
    a, b = np.exp(p); ll = 0
    for k, cen in d:
        # P(first hit at k) = B(a+1, b+k-1)/B(a,b);  P(no hit in k) = B(a, b+k)/B(a,b)
        ll += (betaln(a, b + k) if cen else betaln(a + 1, b + k - 1)) - betaln(a, b)
    return -ll

def nll_h1(p, d):
    al, be = p; ll = 0
    for k, cen in d:
        qs = expit(al + be * np.arange(k))
        if cen:
            ll += np.sum(np.log1p(-qs))
        else:
            ll += np.sum(np.log1p(-qs[:-1])) + np.log(qs[-1])
    return -ll

def fit(d):
    r0 = minimize(nll_h0, [0.0], args=(d,), method="Nelder-Mead")
    r0b = minimize(nll_h0b, [0.0, 1.0], args=(d,), method="Nelder-Mead")
    r1 = minimize(nll_h1, [-1.0, 0.0], args=(d,), method="Nelder-Mead")
    return {"q_H0": float(expit(r0.x[0])), "nll_H0": float(r0.fun),
            "ab_H0b": [float(x) for x in np.exp(r0b.x)], "nll_H0b": float(r0b.fun),
            "alpha_H1": float(r1.x[0]), "beta_H1": float(r1.x[1]), "nll_H1": float(r1.fun),
            "LR_H1_vs_H0": float(2 * (r0.fun - r1.fun)), "LR_H0b_vs_H0": float(2 * (r0.fun - r0b.fun))}

def hazards(curve):
    prev, risk, h = 0, N, []
    for c in curve:
        h.append((c - prev, risk)); risk -= c - prev; prev = c
    return h

def expected_curve(q, T):
    return [round(N * (1 - (1 - q) ** (i + 1)), 2) for i in range(T)]

out = {}
for g, cur in CURVES.items():
    d = first_hits(cur)
    f = fit(d)
    f["hazard_per_iter (hits, at_risk)"] = hazards(cur)
    f["null_expected_curve_with_q_from_iter0"] = expected_curve(cur[0] / N, len(cur))
    f["observed"] = cur
    out[g] = f

# ---------- known-answer simulation ----------
rng = np.random.default_rng(20261107)
def sim_curve(alpha, beta, T, het_sd=0.0):
    task_off = rng.normal(0, het_sd, N)
    hit = np.full(N, T)
    for t in range(N):
        for i in range(T):
            if rng.random() < expit(alpha + task_off[t] + beta * i):
                hit[t] = i; break
    return [int(np.sum(hit <= i)) for i in range(T)]

ka = {}
for label, alpha, beta, het in [("null_homog", np.log(0.25 / 0.75), 0.0, 0.0),
                                ("null_hetero_sd1.5", np.log(0.25 / 0.75), 0.0, 1.5),
                                ("trend_beta0.15", np.log(0.25 / 0.75), 0.15, 0.0),
                                ("trend_beta0.30", np.log(0.25 / 0.75), 0.30, 0.0),
                                ("trend_beta0.30_hetero", np.log(0.25 / 0.75), 0.30, 1.5)]:
    pos, sig, cov10, betas = 0, 0, [], []
    R = 400
    for _ in range(R):
        c = sim_curve(alpha, beta, 11, het)
        f = fit(first_hits(c))
        betas.append(f["beta_H1"]); pos += f["beta_H1"] > 0; sig += (f["LR_H1_vs_H0"] > 3.84 and f["beta_H1"] > 0)
        cov10.append(c[-1])
    ka[label] = {"P(beta_hat>0)": pos / R, "P(LR>3.84 & beta>0)": sig / R,
                 "median_beta_hat": float(np.median(betas)),
                 "C10_mean": float(np.mean(cov10)), "C10_p05_p95": [float(np.percentile(cov10, 5)), float(np.percentile(cov10, 95))]}
out["known_answer"] = ka

here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "m02_out.json"), "w") as fh:
    json.dump(out, fh, indent=1)
print(json.dumps(out, indent=1))
