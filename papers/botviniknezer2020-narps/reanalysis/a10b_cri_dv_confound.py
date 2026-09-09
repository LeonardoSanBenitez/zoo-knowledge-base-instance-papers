"""A10b. Is the CRI choices->estimate association just the dependent variable?

A10 found, at model level with whole teams permuted, choices vs estimate Mantel
rho = +0.145 (p = 0.005) -- refuting my own published reading of R^2 = -0.005 as
"decisions say nothing about the answer". Before believing it, the obvious confound:
the CRI decision block contains the DEPENDENT VARIABLE (Jobs, Unemp, IncDiff, OldAge,
House, Health) and the six DVs are six different questions with genuinely different
answers. Two models sharing a DV are close in decision space AND close in estimate space
for a reason that has nothing to do with analytic flexibility.

Three cuts:
  (1) drop the DV indicators from the decision distance;
  (2) restrict to a single DV at a time, so the DV is constant by construction;
  (3) as a positive control, use ONLY the DV indicators, which should be strong.
"""
import sys, os, json
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mantel_fast import mantel_fast

HERE = os.path.dirname(os.path.abspath(__file__))
CRI = os.path.join(HERE, '..', '..', 'breznau2022-hidden-universe', 'data')
DV_COLS = ['Jobs', 'Unemp', 'IncDiff', 'OldAge', 'House', 'Health']


def dist(P):
    P = np.asarray(P, float)
    P = (P - P.mean(0)) / np.where(P.std(0) > 0, P.std(0), 1)
    P = np.nan_to_num(P)
    return np.sqrt(((P[:, None, :] - P[None, :, :]) ** 2).sum(-1))


def run(d, cols, label, nperm=2000, seed=0):
    P = d[cols].astype(float)
    P = P.loc[:, P.std() > 0]
    Dc = dist(P.values)
    De = np.abs(d['AME_Z'].values[:, None] - d['AME_Z'].values[None, :])
    Ds = np.abs(np.log(d['error'].values)[:, None] - np.log(d['error'].values)[None, :])
    r1 = mantel_fast(Dc, De, nperm=nperm, seed=seed, blocks=d['u_teamid'].values)
    r2 = mantel_fast(Dc, Ds, nperm=nperm, seed=seed + 1, blocks=d['u_teamid'].values)
    print(f"{label:44s} n={len(d):5d} cols={P.shape[1]:3d}  "
          f"estimate rho={r1['rho']:+.4f} (p={r1['p_one_sided']:.4f})   "
          f"log_se rho={r2['rho']:+.4f} (p={r2['p_one_sided']:.4f})")
    return {'estimate': r1, 'log_se': r2, 'n': int(len(d)), 'n_cols': int(P.shape[1])}


def main():
    d = pd.read_csv(os.path.join(CRI, 'cri_model_level.csv'))
    blocks = json.load(open(os.path.join(CRI, 'column_blocks.json')))
    dec = [c for c in blocks['decisions'] if c in d.columns]
    d = d[np.isfinite(d['AME_Z']) & np.isfinite(d['error']) & (d['error'] > 0)].reset_index(drop=True)
    out = {'n_models': int(len(d)), 'n_decision_cols': len(dec)}
    out['all_decisions'] = run(d, dec, 'all decision indicators', seed=1)
    nodv = [c for c in dec if c not in DV_COLS]
    out['decisions_without_DV'] = run(d, nodv, 'decisions WITHOUT the DV indicators', seed=3)
    out['DV_only'] = run(d, [c for c in DV_COLS if c in d.columns],
                         'DV indicators ONLY (positive control)', seed=5)
    per = {}
    for dv in DV_COLS:
        if dv not in d.columns:
            continue
        sub = d[d[dv] == 1]
        if len(sub) < 60 or sub['u_teamid'].nunique() < 10:
            continue
        per[dv] = run(sub.reset_index(drop=True), nodv, f'within DV = {dv}',
                      nperm=2000, seed=hash(dv) % 1000)
    out['within_dv'] = per
    rhos = [v['estimate']['rho'] for v in per.values()]
    out['within_dv_mean_estimate_rho'] = float(np.mean(rhos)) if rhos else None
    print(f"\nmean within-DV choices-vs-estimate rho: {out['within_dv_mean_estimate_rho']}")
    with open(os.path.join(HERE, '..', 'artifacts', 'a10b_cri_dv_confound.json'), 'w') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()
