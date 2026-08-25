"""Shared helpers for the MPE-92M replicability reanalysis (maria, 2026-08-16).

Design notes, so a future reader can tell what is a choice and what is forced:

- The paper (Gamma & Metzinger 2021) ran EFA on SPEARMAN correlations with
  principal-factor extraction and an oblique quartimin rotation. `oblimin` with
  the default gamma=0 IS quartimin, so `rotation='oblimin'` reproduces them.
- Items are 92 visual-analogue scales, 0-100, columns mpe01..mpe92.
- Analysis sample is `over85items == 1` -> N=1403, exactly as printed.
- Item missingness is small (max 1.7%); item medians are imputed so that every
  subsample uses the same item set. Imputation happens ONCE on the full sample,
  never per-subsample, so a group's structure is not shaped by its own medians.
"""
import numpy as np
import pandas as pd
from factor_analyzer import FactorAnalyzer
from scipy.optimize import linear_sum_assignment

DTA = 'MPE92M_Gamma_Metzinger_271020_stata14_R.dta'


def load(dta=DTA):
    """Return (items_df, covariates_df) for the N=1403 analysis sample."""
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        df = pd.read_stata(dta, convert_categoricals=False)
    sub = df[df['over85items'] == 1].copy()
    items = sorted([c for c in df.columns
                    if c.startswith('mpe') and c[3:5].isdigit()],
                   key=lambda c: int(c[3:5]))
    assert len(items) == 92, len(items)
    X = sub[items].astype(float)
    X = X.fillna(X.median())          # ONCE, on the full analysis sample
    X.index = range(len(X))
    cov = sub.drop(columns=items).reset_index(drop=True)
    return X, cov


def loadings(X, k, method='principal', rotation='oblimin'):
    """EFA loading matrix (p x k) from a raw item matrix, on SPEARMAN R.

    factor_analyzer refuses `method='principal'` on a correlation matrix
    ("only implemented using the full data set"). Rather than switch estimator
    and quietly stop reproducing the paper, the items are RANK-TRANSFORMED and
    passed as raw data: Pearson correlation of ranks IS the Spearman
    correlation, so the model sees exactly the matrix the paper analysed.
    Verified numerically in check_rank_trick() below.
    """
    Xr = X.rank(axis=0)
    fa = FactorAnalyzer(n_factors=k, method=method, rotation=rotation)
    fa.fit(Xr.values)
    return fa.loadings_


def check_rank_trick(X):
    """Assert Pearson-of-ranks == Spearman, to the printed precision."""
    a = X.rank(axis=0).corr(method='pearson').values
    b = X.corr(method='spearman').values
    return np.abs(a - b).max()


def congruence_matrix(A, B):
    """Tucker's phi between every column of A and every column of B."""
    An = A / np.sqrt((A ** 2).sum(0, keepdims=True))
    Bn = B / np.sqrt((B ** 2).sum(0, keepdims=True))
    return An.T @ Bn


def match(A, B):
    """Match factors of A to factors of B maximising total |Tucker phi|.

    Returns (phis_sorted_descending, column_pairs). Sign is ignored because a
    factor's sign is arbitrary under rotation; magnitude is the similarity.
    """
    C = np.abs(congruence_matrix(A, B))
    r, c = linear_sum_assignment(-C)
    phis = C[r, c]
    order = np.argsort(-phis)
    return phis[order], list(zip(r[order], c[order]))


def split_half_congruence(X, k, n_splits=50, seed=0, sizes=None):
    """Distribution of matched Tucker phi over random half-splits.

    sizes: optionally (n1, n2) to force subsample sizes (for the sample-size
    control that keeps a group comparison honest). Default is a clean half-split.
    """
    rng = np.random.default_rng(seed)
    N = len(X)
    out = []
    for _ in range(n_splits):
        perm = rng.permutation(N)
        if sizes is None:
            h = N // 2
            i1, i2 = perm[:h], perm[h:2 * h]
        else:
            n1, n2 = sizes
            i1, i2 = perm[:n1], perm[n1:n1 + n2]
        A = loadings(X.iloc[i1], k)
        B = loadings(X.iloc[i2], k)
        phis, _ = match(A, B)
        out.append(phis)
    return np.array(out)          # (n_splits, k), each row sorted descending


def group_congruence(X, idx_a, idx_b, k, n_boot=0, seed=0):
    """Matched phi between two fixed groups; optionally bootstrap within groups."""
    A = loadings(X.iloc[idx_a], k)
    B = loadings(X.iloc[idx_b], k)
    phis, _ = match(A, B)
    if not n_boot:
        return phis, None
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(n_boot):
        ia = rng.choice(idx_a, len(idx_a), replace=True)
        ib = rng.choice(idx_b, len(idx_b), replace=True)
        boots.append(match(loadings(X.iloc[ia], k), loadings(X.iloc[ib], k))[0])
    return phis, np.array(boots)


# Conventional Tucker phi thresholds (Lorenzo-Seva & ten Berge 2006):
#   phi >= .95  factors can be considered equal
#   .85-.94     fair similarity
#   < .85       not the same factor
THRESH_EQUAL, THRESH_FAIR = 0.95, 0.85
