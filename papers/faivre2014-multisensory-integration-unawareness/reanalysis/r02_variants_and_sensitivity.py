"""Follow-up to r01. (1) Try to find the aggregation that reproduces Table 4 before calling a mismatch:
group-level exp of mean log RT vs per-participant, drop first 5 trials of the experiment vs of each
block vs none, RT window. (2) Prime-awareness measured properly: participants partly copy their target
answer into the prime question, so raw prime accuracy mixes sensitivity with response carryover.
Estimate sensitivity to prime identity WITHIN each target-response level, then average (a stratified
hit-minus-false-alarm rate), and test it against 0.
Usage: same argument as r01. Writes out/r02.json."""
import glob, json, os, sys, itertools
import numpy as np, pandas as pd
from scipy import stats
D = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
cols = ["ini", "id", "trial", "primecong", "rel", "audU", "visU", "aP", "aT", "vP", "vT", "respT", "rtT", "respP", "rtP"]
paper = {1: (89, 47, -17), 2: (61, -11, 37), 3: (95, 59, -32), 4: (79, 25, 4)}
res = {}

def load(e):
    fs = sorted(glob.glob(os.path.join(D, f"Exp{e}", "*.dat")))
    x = pd.concat([pd.read_csv(f, sep=r"\s+", header=None, names=cols).assign(file=os.path.basename(f)) for f in fs])
    x["pi"] = (x.primecong == "cong").astype(int); x["ti"] = (x.aT == x.vT).astype(int)
    x["cg"] = (x.pi == x.ti).astype(int)
    x["masked"] = ((x.audU == 0) | (x.visU == 0)).astype(int)
    x["exp_trial"] = x.groupby("file").cumcount() + 1
    x["blk_trial"] = x.groupby(["file", "masked"]).cumcount() + 1
    x["okT"] = (x.respT == x.ti).astype(int)
    return x

def cells(x, drop, lo, hi, level):
    m = x[(x.okT == 1) & (x.rtT >= lo) & (x.rtT < hi)]
    if drop == "exp5": m = m[m.exp_trial > 5]
    if drop == "blk5": m = m[m.blk_trial > 5]
    m = m.assign(l=np.log(m.rtT))
    if level == "participant":
        c = m.groupby(["file", "ti", "cg"]).l.mean().unstack(["ti", "cg"])
        e = np.exp(c)
        sem = (e[(0, 0)] + e[(0, 1)]) / 2 - (e[(1, 0)] + e[(1, 1)]) / 2
        return float(sem.mean()), float((e[(1, 0)] - e[(1, 1)]).mean()), float((e[(0, 0)] - e[(0, 1)]).mean())
    c = m.groupby(["file", "ti", "cg"]).l.mean().groupby(["ti", "cg"]).mean()
    e = np.exp(c)
    return float((e[(0, 0)] + e[(0, 1)]) / 2 - (e[(1, 0)] + e[(1, 1)]) / 2), float(e[(1, 0)] - e[(1, 1)]), float(e[(0, 0)] - e[(0, 1)])

for e in (1, 2, 3, 4):
    x = load(e); u = x[x.masked == 1] if e != 4 else x
    best = []
    for drop, lo, hi, level in itertools.product(("none", "exp5", "blk5"), (300,), (4000, 10**9), ("participant", "group")):
        v = cells(u, drop, lo, hi, level)
        err = sum(abs(a - b) for a, b in zip(v, paper[e]))
        best.append((err, f"{drop}|{lo}|{hi}|{level}", [round(t, 1) for t in v]))
    best.sort()
    res[f"exp{e}_closest_variants"] = best[:3]
    # stratified prime sensitivity (unconscious trials)
    s = []
    for f, g in u.groupby("file"):
        d = []
        for rt_ in (0, 1):
            gg = g[g.respT == rt_]
            if gg.pi.nunique() == 2:
                d.append(gg[gg.pi == 1].respP.mean() - gg[gg.pi == 0].respP.mean())
        s.append(np.mean(d))
    s = np.array(s)
    raw = u.groupby("file").apply(lambda g: (g.respP == g.pi).mean()).values
    res[f"exp{e}_prime_sensitivity_stratified"] = {"mean_H_minus_FA": float(s.mean()), "t": float(stats.ttest_1samp(s, 0).statistic),
                                                   "p": float(stats.ttest_1samp(s, 0).pvalue), "n": len(s)}
    res[f"exp{e}_prime_raw_acc_all_unconscious_trials"] = {"mean": float(raw.mean() * 100), "t": float(stats.ttest_1samp(raw, .5).statistic), "p": float(stats.ttest_1samp(raw, .5).pvalue)}
    print(f"Exp {e}: closest Table-4 variants (abs err, spec, [sem, ident, diff]) vs paper {paper[e]}:", best[:2])
    print(f"   prime sensitivity within target-response strata: H-FA = {s.mean():.3f}, t({len(s)-1}) = {res[f'exp{e}_prime_sensitivity_stratified']['t']:.2f}, p = {res[f'exp{e}_prime_sensitivity_stratified']['p']:.3f};"
          f" raw prime accuracy, all unconscious trials: {raw.mean()*100:.1f}% (t = {res[f'exp{e}_prime_raw_acc_all_unconscious_trials']['t']:.2f}, p = {res[f'exp{e}_prime_raw_acc_all_unconscious_trials']['p']:.3f})")
with open(os.path.join(OUT, "r02.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(res, f, indent=1, default=float)
