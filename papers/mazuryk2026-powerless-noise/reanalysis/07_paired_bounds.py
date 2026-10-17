#!/usr/bin/env python3
"""07 -- Paired-design bounds on the saturation size n* of script 05.

Script 05 uses the INDEPENDENT-arms variance p0(1-p0) + p1(1-p1) for a contrast
measured on the SAME 10,000 questions. For a paired binary contrast the per-item
variance of the difference is P(discordant) - delta^2, and P(discordant) >= |delta|,
so it lies in [ |delta|(1-|delta|),  p0(1-p0)+p1(1-p1) ] (the upper end assumes the two
arms are not negatively correlated across questions, which for the same model on
the same questions is the safe assumption). Per-item outputs are gated, so the
true value is unknown; this script reports n* at both ends, with tau re-estimated
under each variance (DL at the upper end as in 05; method of moments at the lower end, see below).

Found 2026-10-17 while doing the same analysis on wu2026 (w3_nstar.py), where the
independent formula drives tau^2 below zero. Author: maria.
"""
import importlib.util, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("s05", os.path.join(HERE, "05_benchmark_saturation.py"))
import contextlib, io
s = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(s)
N = s.N
print(f"{'subset':<38}{'k':>3}{'SD(E)':>8}{'tau_ind':>9}{'n*_ind':>8}{'tau_lo':>8}{'n*_lo':>7}{'n/n* range':>14}")
for lbl, keys in s.subsets:
    E, SE, V = s.build(keys)
    Vlo = np.abs(E) * (1 - np.abs(E))
    Vlo = np.maximum(Vlo, 1e-6)
    t_i = s.dl_tau(E, SE)
    # Lower end: method-of-moments tau (var(E) - mean SE^2), which is monotone in the assumed
    # sampling variance. DL is NOT used here: with Vlo the weights 1/SE^2 span orders of
    # magnitude (near-zero effects get near-infinite weight) and DL's tau collapses -- an
    # estimator pathology, seen in the first run of this script (tau_lo 0.037 vs SD 0.156).
    t_l = float(np.sqrt(max(0.0, E.var(ddof=1) - np.mean(Vlo / N))))
    n_i = np.median(V) / t_i**2; n_l = np.median(Vlo) / t_l**2
    print(f"{lbl:<38}{len(E):>3}{E.std(ddof=1):>8.4f}{t_i:>9.4f}{n_i:>8.0f}{t_l:>8.4f}{n_l:>7.0f}   {N/n_i:5.1f}-{N/n_l:5.1f}x")
print("""
READ. n*_ind is script 05's number (an UPPER bound on n* if the arms are non-negatively
correlated); n*_lo is the smallest n* consistent with the printed accuracies. Every
conclusion of 05 of the form 'the benchmark is past saturation' gets STRONGER under
pairing, never weaker: the true saturation factor is at least 05's figure.""")

# Calibrated middle: the paired/independent variance ratio measured on my own same-question
# NQ-open context-composition contrasts (maria2026-word-salad-noise-test/reanalysis/out/ws_pairing_ratio.txt):
# 0.25-0.29 for qwen3.5:4b (n=597), 0.32-0.48 for gemma4 (n=200). Different models from Mazuryk's,
# same task and same kind of contrast -- a calibration, not a measurement of their data.
print("\nCALIBRATED (ratio r = paired / independent per-item variance, from my own NQ-open runs)")
for lbl, keys in s.subsets:
    E, SE, V = s.build(keys)
    row = []
    for r in (0.25, 0.48):
        t = float(np.sqrt(max(0.0, E.var(ddof=1) - r * np.mean(SE**2))))
        row.append(r * np.median(V) / t**2)
    print(f"  {lbl:<38} n* = {row[0]:.0f} (r=0.25) to {row[1]:.0f} (r=0.48)  ->  n/n* = {N/row[1]:.1f}x to {N/row[0]:.1f}x")

# KNOWN-ANSWER TEST. Simulate k=10 specifications on the SAME n=10,000 items: item latent
# z_i ~ N(0,1) shared by both arms (this is what makes them paired), arm-specific noise, a
# specification effect drawn with true tau. Check: (a) independent SE overstates the SD of the
# per-spec estimate; (b) moment estimator with the TRUE paired variance recovers tau; (c) with
# the independent variance it understates tau (or hits 0) when tau is small.
from scipy.stats import norm
rng = np.random.default_rng(17)
def sim(tau, reps=200, k=10, n=N, rho=0.85):
    out = []
    for _ in range(reps):
        z = rng.standard_normal(n)
        E, Vi, Vp = [], [], []
        for _ in range(k):
            eff = rng.normal(0, tau)
            u0 = rho * z + np.sqrt(1 - rho**2) * rng.standard_normal(n)
            u1 = rho * z + np.sqrt(1 - rho**2) * rng.standard_normal(n)
            a = u0 < norm.ppf(0.75); b = u1 < norm.ppf(min(0.99, 0.75 + eff))
            d = b.astype(int) - a.astype(int); p0, p1 = a.mean(), b.mean()
            E.append(d.mean()); Vi.append(p0*(1-p0)+p1*(1-p1)); Vp.append(d.var())
        E = np.array(E)
        ti = np.sqrt(max(0, E.var(ddof=1) - np.mean(Vi)/n)); tp = np.sqrt(max(0, E.var(ddof=1) - np.mean(Vp)/n))
        out.append((ti, tp, np.mean(Vp)/np.mean(Vi)))
    o = np.array(out); return o.mean(0), (o[:, 0] == 0).mean()
print("\nKNOWN-ANSWER TEST (true tau planted; rho=0.85 latent item correlation)")
for tau in (0.0, 0.005, 0.0187):
    (ti, tp, r), z0 = sim(tau)
    print(f"  true tau {tau:.4f}: mean tau_hat independent {ti:.4f} (zero in {z0:.0%} of reps) | paired {tp:.4f} | realised ratio {r:.2f}")
