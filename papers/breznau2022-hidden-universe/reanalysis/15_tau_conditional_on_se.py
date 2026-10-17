"""15 -- Do the tau functionals that disagree 13x on the pooled CRI models agree WITHIN strata of precision?
Hypothesis (2026-10-17, from 06's quintile table): the pooled disagreement arises because tau rises with SE and the
imprecise tail is heavy, so precision-weighted and unweighted functionals read different strata. Prediction, written
before running: within each SE quintile the max/min ratio across DL, PM, REML and the robust IQR functional is far
below the pooled 13x. If it is NOT, the explanation is wrong. Author: maria 2026-10-17."""
import importlib.util, os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
def mod(name):
    s = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + '.py')); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
t4, t6 = mod('04_tau_estimators'), mod('06_stratified')
d = t6.load()
import pandas as pd
def robust(y, v):
    q75, q25 = np.percentile(y, [75, 25]); return float(np.sqrt(max(0.0, ((q75 - q25) / 1.349) ** 2 - np.median(v))))
# 04's dl/pm/reml return tau^2 (checked: PM pooled 0.0003 = 0.0187^2, matching 06's PM tau 0.01868) -> sqrt here
F = {'DL': lambda y, v: np.sqrt(t4.dl(y, v)), 'PM': lambda y, v: np.sqrt(t4.pm(y, v)), 'REML': lambda y, v: np.sqrt(t4.reml(y, v)), 'IQR-robust': robust}
def row(sub, label):
    y, v = sub.AME_Z.values.astype(float), sub.v.values.astype(float)
    t = {k: float(f(y, v)) for k, f in F.items()}
    pos = [x for x in t.values() if x > 0]
    ratio = max(pos) / min(pos) if len(pos) == len(t) else float('inf')
    print(f"  {label:<22} n {len(sub):5d} | " + "  ".join(f"{k} {x:.4f}" for k, x in t.items()) + f" | max/min {ratio:6.2f}")
    return ratio
print("tau by functional, pooled and within SE quintiles (CRI model level)")
pooled = row(d, 'POOLED')
d['q'] = pd.qcut(d.se_z, 5, labels=False)
rs = [row(d[d.q == k], f'SE quintile {k+1}') for k in range(5)]
print(chr(10) + f"pooled max/min {pooled:.2f}; within-quintile max/min median {np.median(rs):.2f}, max {max(rs):.2f}")
