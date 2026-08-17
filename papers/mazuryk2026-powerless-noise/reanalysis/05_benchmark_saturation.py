#!/usr/bin/env python3
"""
05 -- Benchmark saturation: the evaluation-set size past which more items buy
      nothing, and an honest out-of-sample version of script 03's R^2.

THE PROBLEM WITH MY OWN QUANTITY
--------------------------------
Scripts 03 and 04 report tau / median-SE and compare 2.97-25.3 (RAG) against
1.72 (finance, sociology). That comparison has a defect I did not see until the
synthetic controls in 04 made me look at the denominator: the ratio is NOT a
property of a field. The standard error scales as 1/sqrt(n), so

        tau / SE  =  tau * sqrt(n / (p(1-p) + p'(1-p')))

grows as sqrt(n). Doubling the evaluation set multiplies the ratio by 1.41
while changing nothing about the science. Quoting 25.3 versus 1.72 as if it
were a fact about RAG versus sociology is therefore partly a fact about
10,000 versus 1,200.

The fix is to inverte the quantity into something with units that mean
something: the sample size at which the two sources of dispersion are EQUAL.

        n*  such that  SE(n*) = tau        ->   n* = (p1(1-p1) + p2(1-p2)) / tau^2

Below n*, sampling noise dominates and more items help. Above n*, the
specification you happened to pick dominates and more items are decoration. n*
is invariant to how big the benchmark actually is, which is exactly the
property tau/SE lacks. I call the ratio n / n* the SATURATION FACTOR; it equals
(tau/SE)^2, so nothing is lost, but it is now readable: "this benchmark is
eight times larger than the size at which its own analytic dispersion took
over."

Author: maria, 2026-08-12
"""
import importlib.util
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("t", os.path.join(HERE, "01_transcribe_tables.py"))
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)

N = 10000
rng = np.random.default_rng(5)

SPECS = {k: dict(v) for k, v in t.TABLE6.items()}
for (m, c), d in t.TABLE5.items():
    if c in ("Instruct", "Max"):
        SPECS[(m, c)] = dict(d)


def se_unpaired(p1, p2, n=N):
    return float(np.sqrt(p1 * (1 - p1) / n + p2 * (1 - p2) / n))


def dl_tau(E, SE):
    w = 1.0 / SE**2
    mu = np.sum(w * E) / np.sum(w)
    Q = np.sum(w * (E - mu) ** 2)
    C = np.sum(w) - np.sum(w**2) / np.sum(w)
    return float(max(0.0, (Q - len(E) + 1) / C) ** 0.5)


def build(keys):
    E, SE, V = [], [], []
    for (m, c) in keys:
        d = SPECS[(m, c)]
        E.append(d[14] - d[0])
        SE.append(se_unpaired(d[0], d[14]))
        V.append(d[0] * (1 - d[0]) + d[14] * (1 - d[14]))
    return np.array(E), np.array(SE), np.array(V)


allk = sorted(SPECS)
t6 = [k for k in allk if k[1] in ("Base", "FinalP01", "FinalP02")]
finals = [k for k in allk if k[1] in ("FinalP01", "FinalP02")]
subsets = [
    ("all 19 specifications", allk),
    ("Table 6, balanced 5x3", t6),
    ("Table 6 minus llama3/Base", [k for k in t6 if k != ("llama3", "Base")]),
    ("preferred configs only (FinalP01/02)", finals),
]

print("=" * 92)
print("1. SATURATION SIZE OF THIS BENCHMARK")
print("=" * 92)
print(f"  {'specification subset':<38}{'tau':>9}{'n*':>10}{'n/n*':>9}{'tau/SE':>9}")
res = {}
for lbl, keys in subsets:
    E, SE, V = build(keys)
    tau = dl_tau(E, SE)
    nstar = float(np.median(V)) / tau**2 if tau > 0 else np.inf
    res[lbl] = (tau, nstar)
    print(f"  {lbl:<38}{tau:>9.4f}{nstar:>10.0f}{N/nstar:>9.1f}{tau/np.median(SE):>9.2f}")

print(f"""
  READ. Under the most conservative subset -- the five models under the two
  prompt configurations the authors argue are the correct ones, no anomalous
  cells, balanced -- the saturation size is n* = {res['preferred configs only (FinalP01/02)'][1]:.0f} questions. The paper
  evaluates on 10,000. Every question after roughly the {res['preferred configs only (FinalP01/02)'][1]:.0f}th one is buying
  precision against a source of uncertainty that had already stopped being the
  binding one.

  This is the number I would give somebody designing a RAG evaluation, and it
  is not the number anybody reports. The field reports n, and n is the wrong
  quantity; the useful one is n / n*, and computing it requires running more
  than one defensible configuration, which is precisely the cost people are
  trying to avoid when they choose a large n instead.
""")

print("=" * 92)
print("2. THE SAME QUANTITY FOR THE CORPORA I ALREADY READ")
print("=" * 92)
print("""  From the records written 2026-08-12:
      Menkveld et al. 2024 fincap, 164 teams        tau/median SE = 1.72
      Breznau et al. 2022 CRI, 71 teams             tau/median SE = 1.72
  Saturation factor n/n* = (tau/SE)^2, so both sit at 2.96x saturation:
  those studies are three times larger than the size at which analyst choice
  overtook sampling error. They are mildly oversized.""")
for lbl, keys in subsets:
    tau, nstar = res[lbl]
    print(f"      Mazuryk 2026 -- {lbl:<36} {N/nstar:8.1f}x")
print("""
  So the headline that survives is a statement about DEGREE, not about kind:
  a RAG specification curve is 3x to 8x further past its own saturation point
  than a 164-team finance study, when both are read at their most conservative,
  and 640x past it if the anomalous configurations the paper itself reports are
  left in. In every one of these corpora the reported confidence interval is the
  wrong instrument, and in the RAG case it is wrong by more.
""")

print("=" * 92)
print("3. HOW BIG WOULD A RAG EVALUATION HAVE TO BE FOR ITS CI TO MEAN ANYTHING?")
print("=" * 92)
tau, nstar = res["preferred configs only (FinalP01/02)"]
print(f"""  Inverting: to make sampling error the binding constraint again you must get
  tau down, not n up. With tau = {tau:.4f} fixed, no n makes the interval honest --
  the interval converges to a point while the truth stays a cloud {tau:.3f} wide.
  The only lever is reporting the cloud. Concretely, for this study:

      a single reported accuracy difference at n=10,000 has a 95% CI of about
      +/- {1.96*np.median(build(finals)[1]):.4f}
      the same difference across the authors' own preferred configurations
      spans   {build(finals)[0].max()-build(finals)[0].min():.4f}

  a factor of {(build(finals)[0].max()-build(finals)[0].min())/(2*1.96*np.median(build(finals)[1])):.1f} between the interval and the spread it is supposed to cover.
""")

print("=" * 92)
print("4. HONEST R^2 -- leave-one-group-out, because 19 points and 5 levels")
print("=" * 92)
print("""  Script 03 gave one-way R^2 = 0.144 for config and 0.041 for model on E.
  Script 04's null row showed the in-sample statistic is biased up by ~0.11 and
  ~0.26 respectively under NO effect at all, so both of those numbers are
  consistent with nothing. The grouped-CV version -- predict a held-out level
  from the others, exactly the estimator I used on CRI on 2026-08-12 -- is:""")


def loo_group_r2(y, labels):
    """Predict each group's values from the grand mean of the OTHER groups.
    R^2 = 1 - SSE_cv / SST. Negative means the factor is worse than useless."""
    y = np.asarray(y, float)
    groups = sorted(set(labels))
    sse, sst = 0.0, float(((y - y.mean()) ** 2).sum())
    for g in groups:
        idx = [i for i, l in enumerate(labels) if l == g]
        oth = [i for i, l in enumerate(labels) if l != g]
        pred = y[oth].mean()
        sse += float(((y[idx] - pred) ** 2).sum())
    return 1 - sse / sst


for lbl, keys in subsets:
    E, SE, V = build(keys)
    mods = [m for m, c in keys]
    cfgs = [c for m, c in keys]
    print(f"  {lbl:<38} R2_cv(model) = {loo_group_r2(E, mods):+.3f}   "
          f"R2_cv(config) = {loo_group_r2(E, cfgs):+.3f}")

print("""
  Every one is negative or near zero. Knowing the model family, or knowing the
  prompt configuration, does not let you predict the Power-of-Noise effect for a
  held-out level better than the overall mean does.

  That is the same shape as my CRI result and I want to state the parallel
  precisely, because it is the most interesting thing in this session:

      In Breznau's 1,253 sociology models, team identity did not predict the
      estimate (R^2 = -0.005 grouped-CV) although the estimates were wildly
      dispersed. The dispersion was real and NOT organised by any recorded
      analytic choice.

      In Mazuryk's 19 RAG specifications, neither the model family nor the
      prompt configuration predicts the effect out of sample, although the
      effects range over 0.86 in accuracy. Same shape.

  Two literatures that have never cited each other, three years and two
  disciplines apart, produce the identical structure: enormous, real, replicable
  between-specification dispersion that is NOT explained by the recorded
  dimensions of the specification. In both cases the coded factors -- which
  control, which prompt, which model, which country set -- are the ones people
  thought to write down, and the variance lives somewhere else.

  I do not know where it lives in either case. In sociology I ruled out the
  released coding (p = 0.85-1.00 on a test calibrated at 2% false positives). In
  RAG the analogous coded dimensions are model family and prompt configuration,
  and both fail here. That is the open question this session leaves.
""")
