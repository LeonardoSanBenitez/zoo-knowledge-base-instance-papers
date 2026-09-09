"""A7b. Same calibration question, against a defensible ground truth, and broken out
per hypothesis so the pooled number cannot hide a sign flip.

'Agreeing with the majority' is not 'being right' -- NARPS says explicitly there is no
ground truth for these effects. The nearest thing the study itself produces is the
IMAGE-BASED META-ANALYSIS across all teams, which pools the unthresholded maps. From the
deposit's own ThresholdSimulation/simulation_results.csv, IBMA voxels inside the ROI:

    H1 0   H2 7   H3 0   H4 7   H5 2101   H6 39   H7 0   H8 0   H9 0

so the aggregate verdict is YES for H2, H4, H5, H6 and NO for H1, H3, H7, H8, H9.
Note this already disagrees with the majority of teams on H2, H4 and H6, where 67-79%
of teams said no and the pooled maps say yes.
"""
import sys, os, json
import numpy as np
import pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import load
from a7_self_knowledge import team_perm_p, build_wide, _rank_within_col, _stat

HYPS_MAP = [1, 2, 5, 6, 7, 8, 9]


def main():
    m = load.metadata()
    m['Confidence'] = pd.to_numeric(m['Confidence'], errors='coerce')
    m['Similar'] = pd.to_numeric(m['Similar'], errors='coerce')
    D = load.decisions()
    sim = pd.read_csv(os.path.join(load.ROOT, 'figures', 'ThresholdSimulation',
                                   'simulation_results.csv'))
    ibma = dict(zip(sim['Hypothesis'], (sim['IBMA (n voxels in ROI)'] > 0).astype(int)))
    cbma = dict(zip(sim['Hypothesis'], (sim['CBMA (n voxels in ROI)'] > 0).astype(int)))
    maj = (D.mean(0) > 0.5).astype(int).to_dict()
    out = {'ibma_verdict': {str(k): int(v) for k, v in ibma.items()},
           'cbma_verdict': {str(k): int(v) for k, v in cbma.items()},
           'majority_verdict': {str(k): int(v) for k, v in maj.items()},
           'majority_vs_ibma_disagree_on': [int(h) for h in ibma if ibma[h] != maj[h]]}

    agr_maj = D.apply(lambda c: (c == maj[c.name]).astype(int))
    agr_ibma = D.apply(lambda c: (c == ibma[c.name]).astype(int))
    rows = []
    for h in HYPS_MAP:
        C = load.unthresh_corr(h)
        A = C.values.astype(float).copy(); np.fill_diagonal(A, np.nan)
        for t, v in zip(C.index, np.nanmedian(A, axis=1)):
            rows.append((t, h, float(v)))
    actual = pd.DataFrame(rows, columns=['teamID', 'varnum', 'actual_map_r'])

    df = m[['teamID', 'varnum', 'Decision', 'Confidence', 'Similar']].copy()
    df = df.merge(agr_maj.stack().rename('agr_majority').reset_index()
                  .rename(columns={'level_0': 'teamID', 'level_1': 'varnum'}),
                  on=['teamID', 'varnum'], how='left')
    df = df.merge(agr_ibma.stack().rename('agr_ibma').reset_index()
                  .rename(columns={'level_0': 'teamID', 'level_1': 'varnum'}),
                  on=['teamID', 'varnum'], how='left')
    df = df.merge(actual, on=['teamID', 'varnum'], how='left')

    for x, y in [('Similar', 'agr_ibma'), ('Confidence', 'agr_ibma')]:
        r = team_perm_p(df, x, y, seed=hash(x + y) % 9999)
        out[f'{x}__{y}'] = r
        print(f"{x} vs agreeing with the IBMA verdict: rho={r['rho']:+.4f} "
              f"p={r['p_two_sided']:.4f} n={r['n_rows']}")

    # per-hypothesis, so a pooled sign cannot hide a flip
    per = {}
    for h in sorted(df.varnum.unique()):
        g = df[df.varnum == h]
        e = {}
        for x, y in [('Similar', 'agr_majority'), ('Confidence', 'agr_majority'),
                     ('Similar', 'agr_ibma'), ('Confidence', 'agr_ibma'),
                     ('Similar', 'actual_map_r'), ('Confidence', 'actual_map_r')]:
            d = g[[x, y]].dropna()
            if d[y].nunique() < 2 or len(d) < 6:
                e[f'{x}~{y}'] = None
                continue
            e[f'{x}~{y}'] = round(float(stats.spearmanr(d[x], d[y]).statistic), 4)
        per[str(int(h))] = e
    out['per_hypothesis'] = per
    print('\nper hypothesis (Spearman):')
    print(pd.DataFrame(per).T.to_string())

    # excluding H5, the only hypothesis whose majority is YES
    sub = df[df.varnum != 5]
    for x, y in [('Similar', 'agr_majority'), ('Confidence', 'agr_majority')]:
        r = team_perm_p(sub, x, y, seed=1234)
        out[f'{x}__{y}__excluding_h5'] = r
        print(f"\nexcluding H5: {x} vs agreeing with majority rho={r['rho']:+.4f} "
              f"p={r['p_two_sided']:.4f} n={r['n_rows']}")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                           'artifacts', 'a7b_ibma_ground_truth.json'), 'w') as f:
        json.dump(out, f, indent=1)
    print('\nmajority vs IBMA disagree on hypotheses:', out['majority_vs_ibma_disagree_on'])


if __name__ == '__main__':
    main()
