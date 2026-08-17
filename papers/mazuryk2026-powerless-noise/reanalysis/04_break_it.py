#!/usr/bin/env python3
"""
04 -- Trying to break script 03 before believing it.

CONTRIBUTING.md section 3: "Try to break the result before you try to believe
it." Script 03 reported tau / median-SE = 25.3 for the RAG specification curve
against 1.72 in finance and sociology. Three things could make that number a
lie, and this script tests all three, plus the denominator.

  (a) TWO BROKEN CELLS. The paper itself calls llama3/Base anomalous -- 73.6% of
      its outputs are the placeholder "___ (extract max 5 tokens)" -- and
      llama2/Instruct sits at 9.10% accuracy, which is not a configuration
      anybody would defend. If dropping them collapses the ratio, the headline
      is about two bugs and must be reported as such.

  (b) UNBALANCED DESIGN. Instruct and Max exist only for llama2 and llama3, so
      the 19-point set over-weights those two models.

  (c) THE DENOMINATOR. Everything rests on n = 10,000. If it is really the
      2,889-item test split, every SE is 1.86x larger and the ratio falls.

  (d) DOES THE MACHINERY WORK AT ALL. Feed it synthetic specification sets where
      the answer is known: zero configuration effect, and configuration-
      determines-everything. An estimator that cannot see an injected effect,
      or that sees one in pure noise, is not measuring what I say it measures.

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
KS = [0, 10, 12, 14]
rng = np.random.default_rng(4)

SPECS = {k: dict(v) for k, v in t.TABLE6.items()}
for (m, c), d in t.TABLE5.items():
    if c in ("Instruct", "Max"):
        SPECS[(m, c)] = dict(d)


def se_unpaired(p1, p2, n=N):
    return float(np.sqrt(p1 * (1 - p1) / n + p2 * (1 - p2) / n))


def build(keys, n=N):
    E, SE, mods, cfgs = [], [], [], []
    for (m, c) in keys:
        d = SPECS[(m, c)]
        E.append(d[14] - d[0])
        SE.append(se_unpaired(d[0], d[14], n))
        mods.append(m)
        cfgs.append(c)
    return np.array(E), np.array(SE), mods, cfgs


def dl_tau(E, SE):
    w = 1.0 / SE**2
    mu = np.sum(w * E) / np.sum(w)
    Q = np.sum(w * (E - mu) ** 2)
    C = np.sum(w) - np.sum(w**2) / np.sum(w)
    return float(max(0.0, (Q - len(E) + 1) / C) ** 0.5)


def summarise(label, keys, n=N):
    E, SE, mods, cfgs = build(keys, n)
    tau = dl_tau(E, SE)
    med = float(np.median(SE))
    iqr = float(np.percentile(E, 75) - np.percentile(E, 25))
    z = E / SE
    pos, neg = int((z > 2.576).sum()), int((z < -2.576).sum())
    print(f"  {label:<44} k={len(E):>2}  tau={tau:.4f}  tau/SE={tau/med:6.2f}  "
          f"IQR={iqr:.4f}  IQR/SE={iqr/med:5.2f}  +{pos}/0{len(E)-pos-neg}/-{neg}")
    return tau / med


print("=" * 96)
print("(a)+(b) ROBUSTNESS LADDER -- every subset a reasonable person might defend")
print("=" * 96)
allk = sorted(SPECS)
t6 = [k for k in allk if k[1] in ("Base", "FinalP01", "FinalP02")]
finals = [k for k in allk if k[1] in ("FinalP01", "FinalP02")]
anom = {("llama3", "Base"), ("llama2", "Instruct")}

ladder = [
    ("all 19 specifications (script 03 headline)", allk),
    ("Table 6 only: balanced 5 models x 3 configs", t6),
    ("all 19 minus the 2 the paper calls broken", [k for k in allk if k not in anom]),
    ("Table 6 minus llama3/Base", [k for k in t6 if k != ("llama3", "Base")]),
    ("only the paper's PREFERRED configs (FinalP01/02)", finals),
    ("only Base (the original study's regime)", [k for k in allk if k[1] == "Base"]),
]
ratios = {}
for lbl, keys in ladder:
    ratios[lbl] = summarise(lbl, keys)

print(f"""
  READ IT HONESTLY. The 25.3 headline does not survive contact with the ladder:
  it is carried by llama3/Base, a cell the paper itself explains as a formatting
  artifact. The defensible statement is the RANGE
      tau / median SE  from {min(ratios.values()):.2f} to {max(ratios.values()):.2f} across six subsets,
  and the load-bearing comparison is the most conservative rung, not the
  loudest: even restricted to the five models under the two configurations the
  authors argue ARE correct -- no anomalies, balanced, all n = 10,000 --
  tau/median SE = {ratios["only the paper's PREFERRED configs (FinalP01/02)"]:.2f}, against 1.72 in finance and sociology.

  So the claim that stands is not 'two orders of magnitude'. It is: after
  removing every cell anyone would call a bug, the dispersion of a RAG effect
  across defensible pipeline configurations is still a small multiple of the
  many-analysts benchmark, on a design where the standard error is FIXED by
  construction and cannot absorb any of it. Script 03's section 1 is corrected
  by this file; the corrected number is the one to quote.
""")

print("=" * 96)
print("(c) IS n REALLY 10,000? -- a forensic test on the printed decimals")
print("=" * 96)
vals = sorted({v for d in SPECS.values() for v in d.values()})
vals += [a for (_n, _p, _m, a, _d, _s) in t.TABLE1 + t.TABLE2]
vals = np.array(sorted(set(vals)))


def worst_residual(n):
    """Largest distance from a printed 4-dp accuracy to the nearest achievable k/n.
    If the table were computed on n items, every printed value must lie within
    half of the 4th decimal (5e-5) of some k/n. One violation kills that n."""
    k = np.round(vals * n)
    return float(np.max(np.abs(vals - k / n)))


for n in (10000, 2889, 5000, 3610, 1000):
    wr = worst_residual(n)
    verdict = "consistent" if wr <= 5e-5 + 1e-12 else "RULED OUT"
    print(f"  n = {n:>6}: worst |printed - k/n| = {wr:.6f}   {verdict}")
print(f"""
  {len(vals)} distinct printed accuracies. Only n = 10,000 survives, and it
  survives exactly (residual 0). The 2,889-item test split is ruled out by a
  margin of {worst_residual(2889)/5e-5:.0f}x the rounding tolerance. So the denominators in
  script 03 are right.

  *** CORRECTION, added after script 06 ***
  An earlier version of this paragraph went on to claim the same for Table 3.
  That was an overclaim: the `vals` array above is built from Tables 1, 2 and
  4-7 and has never contained a single Table 3 value, so nothing here could
  bear on it. Script 06 section 5 runs the test on Table 3 properly and reaches
  a weaker, correctly-hedged conclusion. The sentence is removed rather than
  quietly fixed, and the removal is stated here, because a script that silently
  stops being wrong teaches nobody anything.
""")

print("=" * 96)
print("(d) DOES THE MACHINERY DETECT WHAT IT CLAIMS TO? -- synthetic controls")
print("=" * 96)


def synth(n_model, n_config, config_sd, model_sd, reps=400, n=N, base=0.75):
    """Fake specification curve with KNOWN structure, measured through the same
    pipeline: binomial sampling at n items, DL tau, one-way R^2 by factor."""
    out = []
    for _ in range(reps):
        cfg_eff = rng.normal(0, config_sd, n_config)
        mod_eff = rng.normal(0, model_sd, n_model)
        E, SE, cfgs, mods = [], [], [], []
        for i in range(n_model):
            for j in range(n_config):
                true_E = cfg_eff[j] + mod_eff[i]
                p0 = np.clip(base - true_E / 2, 0.02, 0.98)
                p14 = np.clip(base + true_E / 2, 0.02, 0.98)
                a0 = rng.binomial(n, p0) / n
                a14 = rng.binomial(n, p14) / n
                E.append(a14 - a0)
                SE.append(se_unpaired(a0, a14, n))
                cfgs.append(j)
                mods.append(i)
        E = np.array(E)
        SE = np.array(SE)
        out.append((dl_tau(E, SE) / np.median(SE), r2(E, cfgs), r2(E, mods)))
    return np.array(out)


def r2(y, labels):
    y = np.asarray(y, float)
    sst = ((y - y.mean()) ** 2).sum()
    if sst == 0:
        return np.nan
    ssb = sum(len([i for i, l in enumerate(labels) if l == g]) *
              (y[[i for i, l in enumerate(labels) if l == g]].mean() - y.mean()) ** 2
              for g in set(labels))
    return float(ssb / sst)


scenarios = [
    ("NULL: no config effect, no model effect", 0.0, 0.0),
    ("config effect only, sd = 0.02", 0.02, 0.0),
    ("config effect only, sd = 0.10", 0.10, 0.0),
    ("model  effect only, sd = 0.10", 0.0, 0.10),
    ("both, sd = 0.05 each", 0.05, 0.05),
]
print(f"  5 models x 3 configs = 15 specs, n = {N:,}, 400 replicates each")
print(f"  {'scenario':<42}{'tau/SE med':>11}{'tau/SE 95%':>12}{'R2 config':>11}{'R2 model':>10}")
for lbl, cs, ms in scenarios:
    a = synth(5, 3, cs, ms)
    print(f"  {lbl:<42}{np.median(a[:,0]):>11.2f}{np.percentile(a[:,0],95):>12.2f}"
          f"{np.nanmedian(a[:,1]):>11.3f}{np.nanmedian(a[:,2]):>10.3f}")

print(f"""
  CALIBRATION VERDICT.
  * Under the exact null the estimator returns tau/SE = 0 at the median and does
    not exceed ~1 at the 95th percentile, so the 4-6 range measured on the real
    Table 6 subsets is not something this pipeline manufactures from noise.
  * It recovers an injected config effect monotonically and attributes it to the
    config factor rather than the model factor, and vice versa. The one-way R^2
    is biased UP by roughly 1/(levels) under the null -- visible in the null row
    -- which is why script 03's R^2 = 0.144 for config must not be read as
    'config explains 14%'. Script 05 does the leave-one-group-out version.
""")
