"""Minimal IRLS logistic regression -- numpy only.

Written because the machine has numpy/scipy but no statsmodels, and because a
reanalysis that needs a pip install is a reanalysis nobody will re-run.

Returns coefficients, standard errors (from the inverse observed information),
z and two-sided p. Verified against a closed-form 2x2 odds ratio and against a
synthetic model with known coefficients in `verify_standardisation.py`.
"""
import numpy as np
from scipy import stats


def logit_fit(X, y, add_const=True, tol=1e-10, maxit=200):
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    if add_const:
        X = np.column_stack([np.ones(len(y)), X])
    b = np.zeros(X.shape[1])
    for _ in range(maxit):
        eta = X @ b
        mu = 1.0 / (1.0 + np.exp(-eta))
        W = mu * (1 - mu)
        W = np.clip(W, 1e-12, None)
        H = X.T @ (X * W[:, None])
        g = X.T @ (y - mu)
        step = np.linalg.solve(H, g)
        b = b + step
        if np.max(np.abs(step)) < tol:
            break
    eta = X @ b
    mu = 1.0 / (1.0 + np.exp(-eta))
    W = np.clip(mu * (1 - mu), 1e-12, None)
    cov = np.linalg.inv(X.T @ (X * W[:, None]))
    se = np.sqrt(np.diag(cov))
    z = b / se
    p = 2 * stats.norm.sf(np.abs(z))
    ll = float(np.sum(y * np.log(np.clip(mu, 1e-15, 1)) +
                      (1 - y) * np.log(np.clip(1 - mu, 1e-15, 1))))
    p0 = y.mean()
    ll0 = float(len(y) * (p0 * np.log(p0) + (1 - p0) * np.log(1 - p0)))
    return dict(beta=b, se=se, z=z, p=p, ll=ll, ll0=ll0,
                pseudo_r2=1 - ll / ll0 if ll0 else float("nan"))


def standardise(X):
    X = np.asarray(X, float)
    mu, sd = X.mean(axis=0), X.std(axis=0, ddof=0)
    sd = np.where(sd == 0, 1.0, sd)
    return (X - mu) / sd, sd
