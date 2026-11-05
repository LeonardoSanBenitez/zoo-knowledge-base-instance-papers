"""Maglio & Polman (2014): is the set of five cross-dimension tests (Studies 2, 3a, 3b, 4, 5) too consistent?

Five independent studies, each with n = 45-100, each reporting p between .011 and .051. Two instruments:
  (1) TIVA (Schimmack 2014): variance of the probit-transformed p-values. Independent studies of any true effect give
      var(z) >= 1 in expectation; much less means the set is more homogeneous than sampling allows.
  (2) Joint power (Francis 2012 style): product of each study's power at the pooled effect.

Both instruments are tested on worlds where the answer is KNOWN before they are trusted on the real set:
  W0  true d = pooled observed, no selection       -> TIVA should NOT flag (false-positive rate ~ alpha)
  W1  true d = 0, publish only if p < .06 (file drawer)        -> should flag
  W2  true d = 0.2, publish only if p < .06                      -> should flag
  W3  true d = pooled observed, publish only if p < .06          -> the honest question: how often is THIS flagged?
Usage: python r02_excess_significance.py   (no inputs; the observed p-values and ns are typed from r01 output)
Writes out/r02.json.
"""
import json, os
import numpy as np
from scipy import stats

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"); os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(20261105)

# (study, n1, n2, reported p) -- two-group contrasts that carry the cross-dimension claim (r01 reproduced all five)
obs = [("S2", 40, 40, 0.0318), ("S3a", 52, 48, 0.0116), ("S3b", 44, 42, 0.0105), ("S4", 25, 25, 0.0173), ("S5", 22, 23, 0.0509)]
S1 = ("S1-toward", 101, 101, 2.0e-7)  # the spatial study, reframed toward-vs-away contrast (r01, Mann-Whitney)


def p_to_z(p):
    return stats.norm.isf(np.asarray(p) / 2)


def tiva(ps):
    z = p_to_z(ps); k = len(z); v = np.var(z, ddof=1)
    return float(v), float(stats.chi2.cdf(v * (k - 1), k - 1))  # left tail: too little variance


def d_from_p(p, n1, n2):
    t = stats.t.isf(p / 2, n1 + n2 - 2)
    return t * np.sqrt(1 / n1 + 1 / n2)


res = {}
ps = [o[3] for o in obs]
res["observed_z"] = [round(float(z), 3) for z in p_to_z(ps)]
res["tiva_5"] = tiva(ps)
res["tiva_6_with_S1"] = tiva(ps + [S1[3]])
ds = [d_from_p(o[3], o[1], o[2]) for o in obs]
w = [1 / (1 / o[1] + 1 / o[2]) for o in obs]
d_pool = float(np.average(ds, weights=w))
res["d_each"] = [round(float(x), 3) for x in ds]
res["d_pooled_fixed"] = d_pool


def power(d, n1, n2, alpha=0.05):
    df = n1 + n2 - 2; nc = d / np.sqrt(1 / n1 + 1 / n2); tc = stats.t.isf(alpha / 2, df)
    return float(stats.nct.sf(tc, df, nc) + stats.nct.cdf(-tc, df, nc))


res["power_at_pooled"] = {o[0]: round(power(d_pool, o[1], o[2]), 3) for o in obs}
res["power_at_pooled_alpha.06"] = {o[0]: round(power(d_pool, o[1], o[2], 0.06), 3) for o in obs}
res["joint_power_alpha.05"] = float(np.prod([power(d_pool, o[1], o[2]) for o in obs]))
res["joint_power_alpha.06"] = float(np.prod([power(d_pool, o[1], o[2], 0.06) for o in obs]))
# pooled d is itself inflated if selection happened; also report at half the pooled effect
res["joint_power_at_half_pooled_.06"] = float(np.prod([power(d_pool / 2, o[1], o[2], 0.06) for o in obs]))


def sim_study(d, n1, n2):
    a = rng.normal(d, 1, n1); b = rng.normal(0, 1, n2)
    return float(stats.ttest_ind(a, b).pvalue)


def world(d, select, reps=4000):
    flags, vs = 0, []
    for _ in range(reps):
        set_p = []
        for o in obs:
            while True:
                p = sim_study(d, o[1], o[2])
                if not select or p < 0.06:
                    break
            set_p.append(p)
        v, pt = tiva(set_p)
        vs.append(v); flags += pt < 0.05
    return {"flag_rate_tiva_p<.05": flags / reps, "median_var_z": float(np.median(vs)), "q10_var_z": float(np.quantile(vs, .1))}


res["W0_true_pooled_no_selection"] = world(d_pool, False)
res["W1_null_file_drawer"] = world(0.0, True)
res["W2_d0.2_file_drawer"] = world(0.2, True)
res["W3_true_pooled_file_drawer"] = world(d_pool, True)
res["W4_d0.8_file_drawer"] = world(0.8, True)
# How rare is the observed variance under W0? Monte Carlo rank, no chi-square assumption
vs0 = []
for _ in range(20000):
    vs0.append(tiva([sim_study(d_pool, o[1], o[2]) for o in obs])[0])
res["W0_MC_p_var_le_observed"] = float(np.mean(np.array(vs0) <= res["tiva_5"][0]))
# Probability under W0 that all five land in (.01, .06): the observed "window"
win = 0
for _ in range(20000):
    pp = [sim_study(d_pool, o[1], o[2]) for o in obs]
    win += all(0.01 < x < 0.06 for x in pp)
res["W0_MC_p_all_in_.01_.06_window"] = win / 20000
print(json.dumps(res, indent=1))
json.dump(res, open(os.path.join(OUT, "r02.json"), "w"), indent=1)
