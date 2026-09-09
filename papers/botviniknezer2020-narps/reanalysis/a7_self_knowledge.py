"""A7. Do analysts know how idiosyncratic they are?

Each team rated, per hypothesis, on 1-10:
    Confidence -- "How confident are you about this result?"
    Similar    -- "How similar do you think your result is to the other analysis teams?"

NARPS's Supplementary Information relates BOTH ratings to the team's own binary outcome
(similarity: p<0.001; confidence: p=0.732). It does not ask the calibration question:
is the similarity rating related to the team's ACTUAL similarity to the other teams --
either of its whole-brain map, or of its conclusion?

Two ground truths, both in the deposit:
    actual map similarity  = the team's median Spearman r with all other teams, per
                             hypothesis, from NARPS's own correlation matrices
    actual conclusion agreement = did the team's yes/no match the majority for that
                             hypothesis?

Everything is computed WITHIN hypothesis (hypotheses differ hugely in difficulty and in
majority direction) and every p-value is from a team-level permutation, because a team
contributes up to nine rows.
"""
import sys, os, json
import numpy as np
import pandas as pd
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import load

HYPS = [1, 2, 5, 6, 7, 8, 9]
NPERM = 20000


def _rank_within_col(M):
    """Rank-transform each column (= each hypothesis) to (0,1), NaN-safe."""
    R = np.full(M.shape, np.nan)
    for j in range(M.shape[1]):
        col = M[:, j]
        ok = np.isfinite(col)
        if ok.sum() < 5:
            continue
        R[ok, j] = stats.rankdata(col[ok]) / (ok.sum() + 1)
    return R


def _stat(RX, RY):
    ok = np.isfinite(RX) & np.isfinite(RY)
    x = RX[ok]; y = RY[ok]
    return float(stats.spearmanr(x, y).statistic), int(ok.sum())


def build_wide(df, xcol, ycol, teamcol='teamID', hypcol='varnum'):
    X = df.pivot_table(index=teamcol, columns=hypcol, values=xcol)
    Y = df.pivot_table(index=teamcol, columns=hypcol, values=ycol)
    teams = sorted(set(X.index) | set(Y.index))
    hyps = sorted(set(X.columns) | set(Y.columns))
    X = X.reindex(index=teams, columns=hyps)
    Y = Y.reindex(index=teams, columns=hyps)
    return X.values.astype(float), Y.values.astype(float)


def team_perm_p(df, xcol, ycol, teamcol='teamID', hypcol='varnum', nperm=NPERM, seed=0):
    """Permute the rating matrix BETWEEN teams, keeping each team's whole nine-row
    profile intact. That is the right exchangeable unit: a team's ratings are one
    realisation, and its nine rows are not nine independent observations."""
    Xv, Yv = build_wide(df, xcol, ycol, teamcol, hypcol)
    RX = _rank_within_col(Xv)
    RY = _rank_within_col(Yv)
    obs, n = _stat(RX, RY)
    rng = np.random.default_rng(seed)
    null = np.empty(nperm)
    idx = np.arange(RX.shape[0])
    for i in range(nperm):
        null[i], _ = _stat(RX[rng.permutation(idx)], RY)
    p2 = (1 + min((null >= obs).sum(), (null <= obs).sum()) * 2) / (1 + nperm)
    return dict(rho=obs, n_rows=n, p_two_sided=float(min(1.0, p2)),
                null_mean=float(null.mean()), null_sd=float(null.std(ddof=1)),
                nperm=nperm)


def main():
    m = load.metadata()
    m['Confidence'] = pd.to_numeric(m['Confidence'], errors='coerce')
    m['Similar'] = pd.to_numeric(m['Similar'], errors='coerce')
    D = load.decisions()

    # ground truth 1: actual median map correlation with other teams, per team per hyp
    rows = []
    for h in HYPS:
        C = load.unthresh_corr(h)
        A = C.values.astype(float).copy()
        np.fill_diagonal(A, np.nan)
        med = np.nanmedian(A, axis=1)
        for t, v in zip(C.index, med):
            rows.append((t, h, float(v)))
    actual = pd.DataFrame(rows, columns=['teamID', 'varnum', 'actual_map_r'])

    # ground truth 2: agreement with the majority decision for that hypothesis
    maj = (D.mean(0) > 0.5).astype(int)
    agree = D.apply(lambda col: (col == maj[col.name]).astype(int))
    agr = agree.stack().rename('agrees_majority').reset_index()
    agr.columns = ['teamID', 'varnum', 'agrees_majority']

    df = (m[['teamID', 'varnum', 'Decision', 'Confidence', 'Similar']]
          .merge(agr, on=['teamID', 'varnum'], how='left')
          .merge(actual, on=['teamID', 'varnum'], how='left'))

    out = {'n_rows': int(len(df)), 'n_rows_with_map': int(df.actual_map_r.notna().sum())}

    pairs = [
        ('Similar', 'actual_map_r', 'self-rated similarity vs ACTUAL map similarity'),
        ('Similar', 'agrees_majority', 'self-rated similarity vs agreeing with the majority'),
        ('Confidence', 'agrees_majority', 'confidence vs agreeing with the majority'),
        ('Confidence', 'actual_map_r', 'confidence vs ACTUAL map similarity'),
        ('Confidence', 'Similar', 'confidence vs self-rated similarity'),
        ('Similar', 'Decision', 'self-rated similarity vs own yes/no (NARPS supp reports this)'),
        ('Confidence', 'Decision', 'confidence vs own yes/no (NARPS supp reports this)'),
    ]
    for x, y, label in pairs:
        sub = df[df.varnum.isin(HYPS)] if y == 'actual_map_r' else df
        r = team_perm_p(sub, x, y, seed=abs(hash(label)) % 10000)
        r['label'] = label
        out[f'{x}__{y}'] = r
        print(f"{label:62s} rho={r['rho']:+.4f}  p={r['p_two_sided']:.4f}  n={r['n_rows']}")

    # the same thing, without ranks, as means: does a dissenting team rate itself as
    # MORE similar to the others?
    tab = df.groupby(['varnum', 'agrees_majority'])[['Similar', 'Confidence']].mean().round(3)
    out['means_by_agreement'] = tab.reset_index().to_dict(orient='records')
    print('\nmean ratings by whether the team agreed with the majority:')
    print(tab.to_string())
    ov = df.groupby('agrees_majority')[['Similar', 'Confidence']].agg(['mean', 'count'])
    print('\npooled:'); print(ov.to_string())
    out['pooled_means_by_agreement'] = {str(k): {c: float(ov.loc[k, (c, 'mean')])
                                                 for c in ['Similar', 'Confidence']}
                                        for k in ov.index}
    df.to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                           'artifacts', 'a7_selfknowledge_rows.csv'), index=False)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                           'artifacts', 'a7_self_knowledge.json'), 'w') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()
