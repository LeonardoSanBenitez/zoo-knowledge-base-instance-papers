"""Selection-aware forecasting of replication outcomes -- maria's extension of Pawel & Held (2020).

Pawel & Held's SH forecast shrinks each original estimate by its own evidence, s = max(1 - (1+d)/t_o^2, 0). That is
James-Stein-like shrinkage for an UNSELECTED estimate. Originals that reached print were selected on |t_o| > 1.96,
and a per-study rule cannot see that. This module estimates the distribution g(theta) of true original effects
(Fisher-z scale) across a SET of originals by nonparametric maximum likelihood on a grid, with the likelihood of each
original conditioned on having been selected (truncated at |t| > z_crit), then forecasts each replication from the
posterior of its own theta. It uses only original-study data and the replication's planned n -- never replication
outcomes -- so evaluations remain out-of-sample in the paper's sense.

Shared by p02 (known-answer worlds), p03 (the four projects), f01 (FReD out-of-sample).
"""
import numpy as np
from scipy import stats

ZC = stats.norm.isf(0.025)
GRID = np.linspace(-0.6, 1.6, 221)  # Fisher-z true effects, in the ORIGINAL's direction


def fit_g(to_abs, se_o, truncate=True, iters=3000, grid=GRID, tol=1e-9):
    """NPMLE of g on grid via EM. to_abs: |t_o| (direction folded); se_o: SE of fisher z of originals.
    truncate=True: each likelihood divided by P(|t| > ZC | theta, se) (selection on significance, both tails)."""
    mu = grid[None, :] / se_o[:, None]  # noncentrality per study x grid
    L = stats.norm.pdf(to_abs[:, None] - mu)
    if truncate:
        sel = stats.norm.sf(ZC - mu) + stats.norm.cdf(-ZC - mu)
        L = L / np.maximum(sel, 1e-300)
    w = np.full(len(grid), 1 / len(grid))
    prev = -np.inf
    for _ in range(iters):
        m = L * w[None, :]
        den = m.sum(1, keepdims=True)
        w = (m / den).mean(0)
        ll = float(np.log(den).sum())
        if ll - prev < tol:
            break
        prev = ll
    return w, ll


def posterior(to_abs, se_o, w, grid=GRID, truncate=True):
    mu = grid[None, :] / se_o[:, None]
    L = stats.norm.pdf(to_abs[:, None] - mu)
    # NB: the selection factor depends on theta, so it must stay in the posterior when selection is modelled.
    if truncate:
        sel = stats.norm.sf(ZC - mu) + stats.norm.cdf(-ZC - mu)
        L = L / np.maximum(sel, 1e-300)
    p = L * w[None, :]
    return p / p.sum(1, keepdims=True)


def p_sig_selection(to_abs, se_o, se_r, w, tau=0.0, grid=GRID, truncate=True):
    """P(replication significant in the original's direction) under the fitted g; theta_r = theta_o + N(0, 2 tau^2)."""
    post = posterior(to_abs, se_o, w, grid, truncate)
    sd = np.sqrt(se_r[:, None] ** 2 + 2 * tau ** 2)
    ps = stats.norm.sf((ZC * se_r[:, None] - grid[None, :]) / sd)  # P(theta_hat_r > ZC * se_r)
    return (post * ps).sum(1), post


def p_sig_pawel(to_abs, c, d, method="SH"):
    if method in ("N", "S"):
        d = np.zeros_like(to_abs)
    s = np.ones_like(to_abs) if method in ("N", "H") else np.maximum(1 - (1 + d) / to_abs ** 2, 0)
    m = s * np.sqrt(c) * to_abs
    v = (s * (c + c * d) + 1 + c * d) if method in ("S", "SH") else (c + 1 + 2 * c * d)
    return stats.norm.sf((ZC - m) / np.sqrt(v))


def scores(p, y):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    bs = float(np.mean((p - y) ** 2)); bs0 = float(np.mean((y.mean() - y) ** 2))
    zs = float(np.sum((y - p) * (1 - 2 * p)) / np.sqrt(np.sum((1 - 2 * p) ** 2 * p * (1 - p))))
    try:
        from sklearn.metrics import roc_auc_score
        auc = float(roc_auc_score(y, p)) if 0 < y.sum() < len(y) else float("nan")
    except Exception:
        auc = float("nan")
    return {"n": int(len(y)), "observed": int(y.sum()), "expected": round(float(p.sum()), 1), "BS": round(bs, 4),
            "BSnorm": round((bs0 - bs) / bs0, 3) if bs0 > 0 else None, "spiegelhalter_z": round(zs, 2), "AUC": round(auc, 3),
            "log_score": round(float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))), 4)}
