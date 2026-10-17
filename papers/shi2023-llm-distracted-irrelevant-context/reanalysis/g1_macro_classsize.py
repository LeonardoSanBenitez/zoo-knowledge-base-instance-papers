"""g1 -- How much of GSM-IC 'macro accuracy' is the number of variants per base?

Macro accuracy (Shi et al. 2023 s3.2) counts a base problem as solved only if EVERY sampled variant is
solved. Its value therefore falls with the number of variants m_b per base even if the model is unchanged.
Model: per-base accuracy p_b ~ Beta(mu*k, (1-mu)*k), variants conditionally independent given p_b, so
E[macro | m] = mean_b B(a+m_b, b)/B(a, b). mu is pinned to the paper's micro accuracy; k (concentration)
is solved so the predicted macro on a uniform 4,000-of-58,052 sample (their GSM-IC-4K) equals the printed
macro. Then: predicted macro at the full dataset (m_b = class size, 192-640) and at fixed small m.
Class sizes are read from the released data. Author: maria 2026-10-17.
"""
import json, collections, sys
import numpy as np
from scipy.special import betaln
from scipy.optimize import brentq
HERE = sys.argv[1] if len(sys.argv) > 1 else '.'
A = json.load(open(f'{HERE}/GSM-IC_2step.json', encoding='utf-8')) + json.load(open(f'{HERE}/GSM-IC_mstep.json', encoding='utf-8'))
sizes = np.array(sorted(collections.Counter(x['original_question'] for x in A).values()))
N, n4k = sizes.sum(), 4000
rng = np.random.default_rng(0)
lab = np.repeat(np.arange(len(sizes)), sizes)
M4 = np.array([np.bincount(rng.choice(lab, n4k, replace=False), minlength=len(sizes)) for _ in range(200)])  # 200 x 100

def macro(mu, k, m):  # m: array of per-base counts (any shape, last axis bases)
    a, b = mu * k, (1 - mu) * k
    return np.exp(betaln(a + m, b) - betaln(a, b)).mean(axis=-1)

def fit_k(mu, mac):
    f = lambda lk: macro(mu, np.exp(lk), M4).mean() - mac
    lo, hi = np.log(1e-3), np.log(1e4)
    if f(lo) * f(hi) > 0: return np.nan
    return np.exp(brentq(f, lo, hi))

if __name__ == '__main__':
    print(f"bases {len(sizes)}, variants {N}, class size min/median/max {sizes.min()}/{int(np.median(sizes))}/{sizes.max()}")
    print(f"uniform 4K sample: variants per base mean {M4.mean():.1f}, min over bases (median rep) {np.median(M4.min(1)):.0f}, max {np.median(M4.max(1)):.0f}")
    # Table 3 rows (code-davinci-002, exemplar w/o irrelevant context; overall micro, overall macro), as printed
    rows = [('COT', .724, .060), ('COT+INST', .778, .150), ('LTM', .775, .180), ('LTM+INST', .806, .250),
            ('PROGRAM', .544, .050), ('COT+SC', .881, .300), ('LTM+SC', .934, .450), ('PROGRAM+SC', .746, .130)]
    print(f"\n{'method':<11}{'micro':>6}{'macro4K':>8}{'k_fit':>8} | predicted macro at m = 1, 5, 10, 44(4K median), FULL set")
    for name, mu, mac in rows:
        k = fit_k(mu, mac)
        if np.isnan(k): print(f"{name:<11} no fit"); continue
        pred = [macro(mu, k, np.full(len(sizes), m)) for m in (1, 5, 10, 44)] + [macro(mu, k, sizes)]
        print(f"{name:<11}{mu:6.3f}{mac:8.3f}{k:8.2f} | " + "  ".join(f"{p:.3f}" for p in pred))
    # independence reference: if all bases had p_b = micro, macro at 4K would be micro^m
    print(f"\nreference: homogeneous p = 0.724 at m = 44 gives macro {0.724**44:.1e} -- observed 0.06 means errors are concentrated in some bases")
