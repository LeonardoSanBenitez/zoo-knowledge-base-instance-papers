"""Jara-Ettinger, Tenenbaum & Schulz (2015) -- recount every number in Methods/Results from the
deposited CSV, then recompute the inferential statistics independently of the authors' R script.

Usage (from the zoo root):
  python -I zoo-knowledge-base/instance-papers/papers/jaraettinger2015-not-so-innocent/reanalysis/r01_recount_and_tests.py \
      "$(python zoo-knowledge-base/tools/assets.py path paper-downloads/jaraettinger2015-not-so-innocent)/osf_z9ikh/files/osfstorage/JaraEttinger_Tenenbaum_Schulz_Results.csv"
Writes out/r01.json next to this script.
"""
import csv, io, json, os, sys
from collections import Counter
from math import comb
import numpy as np

path = sys.argv[1]
raw = open(path, "rb").read()
ncr, nlf = raw.count(b"\r"), raw.count(b"\n")
print(f"bytes={len(raw)}  CR={ncr}  LF={nlf}  (classic-Mac CR line endings if LF=0)")
rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n"))))
print(f"rows={len(rows)}")
out = {"rows": len(rows)}

# --- exact duplicate rows -----------------------------------------------------------------------
c = Counter(tuple(r.values()) for r in rows)
dups = [(k, n) for k, n in c.items() if n > 1]
print("exact duplicate rows:", dups)
out["exact_duplicate_rows"] = [list(k) + [n] for k, n in dups]

def age_stats(sub, unit):
    d = np.array([float(r["DaysOld"]) for r in sub if r["DaysOld"] not in ("", "NA")])
    return {"n_with_age": len(d), "mean": d.mean() / unit, "sd_days": d.std(ddof=1),
            "min": d.min() / unit, "max": d.max() / unit}

for exp, unit in (("Experiment 1", 30.4368), ("Experiment 2", 365.25), ("Experiment 3", 365.25)):
    E = [r for r in rows if r["Experiment"] == exp]
    st = Counter(r["Status"] for r in E)
    tested = [r for r in E if r["Status"] != "WarmupFail"]
    data = [r for r in tested if r["Status"] == "Data"]
    o = {"status": dict(st), "tested": len(tested), "age_tested": age_stats(tested, unit)}
    by = {}
    for r in data:
        by.setdefault(r["Condition"], Counter())[r["Choice"]] += 1
    o["choices_by_condition"] = {k: dict(v) for k, v in by.items()}
    # excluded children's choices (what the result would be with them in)
    exc = Counter((r["Status"], r["Condition"], r["Choice"]) for r in tested if r["Status"] != "Data")
    o["excluded_with_choice"] = {"|".join(k): v for k, v in exc.items()}
    out[exp] = o
    print(f"\n{exp}: status={dict(st)} tested={len(tested)}")
    print("  age:", {k: round(v, 3) for k, v in o["age_tested"].items()})
    print("  choices:", o["choices_by_condition"])
    print("  excluded:", o["excluded_with_choice"])

# --- tests ----------------------------------------------------------------------------------------
def binom_two_sided(k, n, p=0.5):
    pk = comb(n, k) * p**k * (1 - p)**(n - k)
    return sum(comb(n, i) * p**i * (1 - p)**(n - i) for i in range(n + 1)
               if comb(n, i) * p**i * (1 - p)**(n - i) <= pk * (1 + 1e-7))

def fisher_two_sided(a, b, c, d):
    """2x2 [[a,b],[c,d]]; R's fisher.test two-sided rule (sum of tables with prob <= observed)."""
    r1, r2, c1 = a + b, c + d, a + c
    n = r1 + r2
    def p(x):
        return comb(r1, x) * comb(r2, c1 - x) / comb(n, c1)
    po = p(a)
    lo, hi = max(0, c1 - r2), min(r1, c1)
    return sum(p(x) for x in range(lo, hi + 1) if p(x) <= po * (1 + 1e-7))

cells = {"Exp1": (15, 16), "Exp2": (11, 16), "Exp3_play": (13, 16), "Exp3_nicer": (5, 16), "Exp3_control": (11, 16)}
out["binomial_vs_half_two_sided"] = {k: binom_two_sided(*v) for k, v in cells.items()}
print("\nbinomial vs 0.5 (two-sided):", {k: round(v, 4) for k, v in out["binomial_vs_half_two_sided"].items()})
out["fisher_play_vs_nicer"] = fisher_two_sided(13, 3, 5, 11)
out["fisher_nicer_vs_control"] = fisher_two_sided(5, 11, 11, 5)
print("Fisher play vs nicer   :", round(out["fisher_play_vs_nicer"], 5), "(paper: p < .05)")
print("Fisher nicer vs control:", round(out["fisher_nicer_vs_control"], 5), "(paper: p < .075)")

# --- bootstrap CIs, re-implemented (R boot 'basic': 2*t0 - quantile, norm.inter interpolation) -----
rng = np.random.default_rng(20261025)
R = 200_000

def norm_inter_q(t, alpha):
    """R boot:::norm.inter -- quantile on the normal-score scale, interpolated between order stats."""
    from statistics import NormalDist
    t = np.sort(t); Rn = len(t)
    rk = (Rn + 1) * alpha
    k = int(np.floor(rk))
    if k == rk:
        return t[k - 1]
    if k == 0: return t[0]
    if k >= Rn: return t[-1]
    N = NormalDist()
    a = N.inv_cdf(alpha); lo = N.inv_cdf(k / (Rn + 1)); hi = N.inv_cdf((k + 1) / (Rn + 1))
    return t[k - 1] + (a - lo) / (hi - lo) * (t[k] - t[k - 1])

def basic_ci(t, t0):
    return 2 * t0 - norm_inter_q(t, 0.975), 2 * t0 - norm_inter_q(t, 0.025)

ci = {}
for k, (s, n) in cells.items():
    x = np.r_[np.ones(s), np.zeros(n - s)]
    t = x[rng.integers(0, n, (R, n))].mean(1)
    ci[k] = [round(100 * v, 2) for v in basic_ci(t, s / n)]
def two_group(sa, sb, n=16):
    x = np.r_[np.ones(sa), np.zeros(n - sa), np.ones(sb), np.zeros(n - sb)]
    g = np.r_[np.zeros(n), np.ones(n)]
    idx = rng.integers(0, 2 * n, (R, 2 * n))
    xs, gs = x[idx], g[idx]
    na = (gs == 0).sum(1); nb = (gs == 1).sum(1)
    ok = (na > 0) & (nb > 0)
    t = (xs * (gs == 0)).sum(1)[ok] / na[ok] - (xs * (gs == 1)).sum(1)[ok] / nb[ok]
    return [round(100 * v, 2) for v in basic_ci(t, sa / n - sb / n)]
ci["diff_play_minus_nicer_nonstratified"] = two_group(13, 5)
ci["diff_control_minus_nicer_nonstratified"] = two_group(11, 5)
out["basic_bootstrap_ci_pct"] = ci
print("\nbasic bootstrap CIs (%):", json.dumps(ci))
print("paper: Exp1 [87.5,100]; Exp2 [50,93.75]; play [68.75,100] (R script comment: 62.50-100); "
      "nicer [6.25,50]; diff play-nicer [21.05,81.67]; diff control-nicer [6.17,71.03]")

od = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(od, exist_ok=True)
with open(os.path.join(od, "r01.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(out, f, indent=1, default=float)
