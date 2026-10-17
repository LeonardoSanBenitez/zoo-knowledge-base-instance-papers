"""g2 -- Known-answer test of g1, and uncertainty from macro resting on 100 bases.
(a) Plant p_b ~ Beta(mu k, (1-mu) k) with known k, draw outcomes for EVERY variant, take a uniform 4K sample,
    compute micro and macro there as the paper would, refit k with g1's method, and compare g1's predicted
    full-set macro with the TRUE full-set macro of the same simulated world.
(b) Assumption break: within-base heterogeneity by template (half of each base's variants at p_b + d, half
    at p_b - d) -- variants no longer exchangeable. Does the prediction still land?
(c) Sampling uncertainty: the printed macro is k/100; redraw it as Binomial(100, macro)/100, refit, and report
    the 90% interval of the predicted full-set and m = 10 macro. Author: maria 2026-10-17."""
import sys, numpy as np
sys.argv = [sys.argv[0], '.']
import importlib.util
spec = importlib.util.spec_from_file_location('g1', 're/g1_macro_classsize.py'); g1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(g1)
rng = np.random.default_rng(1); S = g1.sizes; lab = g1.lab
def world(mu, k, d=0.0):
    p = rng.beta(mu * k, (1 - mu) * k, len(S))
    pv = np.clip(p[lab] + d * np.where(rng.random(lab.size) < .5, 1, -1), 0, 1)
    y = rng.random(lab.size) < pv
    idx = rng.choice(lab.size, 4000, replace=False)
    micro = y[idx].mean(); ok = np.ones(len(S), bool); np.logical_and.at(ok, lab[idx], y[idx])
    true_full = np.mean([y[lab == b].all() for b in range(len(S))])
    true_m10 = np.mean([y[rng.choice(np.where(lab == b)[0], 10, replace=False)].all() for b in range(len(S))])
    return micro, ok.mean(), true_full, true_m10
print("(a)/(b) known-answer: true k, d -> fitted k; predicted vs true macro (full set; m=10)")
for mu, k, d in ((.72, 3.9, 0), (.78, 2.4, 0), (.93, 5.5, 0), (.72, 3.9, .15), (.78, 2.4, .15)):
    R = []
    for _ in range(20):
        mi, ma, tf, t10 = world(mu, k, d); kf = g1.fit_k(mi, ma)
        if np.isnan(kf): continue
        R.append((kf, g1.macro(mi, kf, S), tf, g1.macro(mi, kf, np.full(len(S), 10)), t10))
    R = np.array(R).mean(0)
    print(f"  mu {mu} k {k} d {d}: k_fit {R[0]:.2f} | full pred {R[1]:.3f} true {R[2]:.3f} | m10 pred {R[3]:.3f} true {R[4]:.3f}")
print("\n(c) uncertainty from 100 bases (Binomial redraw of the printed macro), 90% intervals")
for name, mu, mac in (('COT', .724, .06), ('LTM', .775, .18), ('LTM+SC', .934, .45)):
    F, T = [], []
    for _ in range(300):
        m2 = rng.binomial(100, mac) / 100
        kf = g1.fit_k(mu, m2)
        if np.isnan(kf): continue
        F.append(g1.macro(mu, kf, S)); T.append(g1.macro(mu, kf, np.full(len(S), 10)))
    print(f"  {name:<7} full-set macro {np.percentile(F,5):.3f}-{np.percentile(F,95):.3f} | m=10 macro {np.percentile(T,5):.3f}-{np.percentile(T,95):.3f}  (printed 4K value {mac})")
