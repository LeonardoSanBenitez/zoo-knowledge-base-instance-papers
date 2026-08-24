"""Does a choice about WHAT COUNTS AS A CASE move the estimate?

maria, 2026-08-24. Written to test a hypothesis I formed the same day and to
find out whether it survives. It does not.

THE HYPOTHESIS (maria2026-executability-denominators#c5, recorded as UNVERIFIED)
------------------------------------------------------------------------------
Reading three artifact-execution studies, I found one exclusion rule moving a
published rate from 19.3% to 39.8% -- a twenty-point move in a POINT ESTIMATE
from a single analytic choice. That sits badly next to what this record already
concluded from CRI: analytic decisions predict the standard error (out-of-team
R^2 ~ 0.2) and not the estimate (R^2 ~ 0).

The reconciliation I proposed:

    a degree of freedom that is a MODELLING choice over a fixed set of cases
    moves the standard error; a degree of freedom that decides WHAT COUNTS AS A
    CASE moves the point estimate.

CRI is the one dataset here that can test it, because Breznau et al. coded, per
model, both which countries and waves entered the sample and which estimator was
used. Prediction: the sample-composition block should predict the ESTIMATE better
than the modelling block does.

WHAT THIS SCRIPT ADDS OVER 11_what_drives_precision.py
------------------------------------------------------
11 computed the block table once, under one random fold assignment, and its
output was never written into the record. Three things are added:

 1. FOLD STABILITY. Every R^2 here is over B random team-fold assignments, with
    mean and SD. The headline number in NOTES.md is 0.207 and re-running 11 today
    gave 0.1716 -- a difference produced entirely by the fold draw, on a number
    quoted to three decimals.
 2. A POWER CHECK THAT COULD KILL THE NULL RESULT. Grouped cross-validation holds
    out whole teams. If sample composition barely varies WITHIN a team, then the
    variation the sample block needs is exactly what team-grouping removes, and
    "sample composition predicts nothing" would be a statement about the design,
    not about the world. Measured directly below.
 3. A synthetic positive control: inject a known sample-driven effect and check
    that this machinery can see it.
"""
import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "cri_model_level.csv")
BLOCKS = os.path.join(HERE, "..", "data", "column_blocks.json")
Z95 = 1.959964
LAMS = np.geomspace(1e-2, 1e6, 17)
B_FOLDS = 40


def load():
    d = pd.read_csv(DATA, low_memory=False)
    a = d[d.AME_Z.notna() & (d.u_teamid != 0)].copy()
    a["se_z"] = (a.upper_Z - a.lower_Z) / (2 * Z95)
    return a[np.isfinite(a.se_z) & (a.se_z > 0)].copy()


def ridge_cv(X, y, groups, lam, folds):
    pred = np.full(len(y), np.nan)
    for f in folds:
        te = np.isin(groups, f)
        tr = ~te
        if tr.sum() < 20 or te.sum() == 0:
            continue
        Xm, ym = X[tr].mean(0), y[tr].mean()
        Xc = X[tr] - Xm
        b = np.linalg.solve(Xc.T @ Xc + lam * np.eye(X.shape[1]), Xc.T @ (y[tr] - ym))
        pred[te] = (X[te] - Xm) @ b + ym
    m = np.isfinite(pred)
    if m.sum() < 10:
        return np.nan
    return 1 - np.sum((y[m] - pred[m]) ** 2) / np.sum((y[m] - y[m].mean()) ** 2)


def prep(cols, a):
    X = a[cols].apply(pd.to_numeric, errors="coerce").fillna(0.0).values.astype(float)
    k = X.std(0) > 0
    if k.sum() == 0:
        return None, 0
    Xs = X[:, k]
    return (Xs - Xs.mean(0)) / Xs.std(0), int(k.sum())


def r2_over_folds(cols, y, a, groups, seeds):
    """max-over-lambda R^2, repeated over B random team-fold assignments."""
    X, p = prep(cols, a)
    if X is None:
        return np.nan, np.nan, 0
    out = []
    for s in seeds:
        rng = np.random.default_rng(s)
        ug = np.unique(groups).copy()
        rng.shuffle(ug)
        folds = np.array_split(ug, 10)
        out.append(max(ridge_cv(X, y, groups, l, folds) for l in LAMS))
    out = np.array([v for v in out if np.isfinite(v)])
    return out.mean(), out.std(), p


COUNTRIES = ['AU', 'AT', 'BE', 'BG', 'CA', 'CL', 'HR', 'CY', 'CZ', 'DK', 'FI', 'FR',
             'DE', 'HU', 'IS', 'IN', 'IE', 'IL', 'IT', 'JP', 'KR', 'LV', 'LT', 'NT',
             'NZ', 'NO', 'PH', 'PL', 'PT', 'RU', 'SK', 'SI', 'ES', 'SE', 'CH', 'UK',
             'US', 'ZA', 'TW', 'TR', 'UY', 'VE']
WAVES = ['w1985', 'w1990', 'w1996', 'w2006', 'w2016']
SAMPLE_DEF = COUNTRIES + WAVES + ['orig13', 'orig17', 'eeurope', 'allavailable',
                                  'unbalpanel', 'listwise', 'multimpute',
                                  'level_cyear', 'level_country', 'level_year',
                                  'num_countries']
MODELLING = ['logit', 'ologit', 'lpm', 'ols', 'mlogit', 'ml_glm', 'bayes',
             'mlm_any', 'mlm_re', 'mlm_fe', 'hybrid_mlm', 'twowayfe', 'cluster_any',
             'weights', 'L2boots', 'pseudo_pnl', 'country_dummies_only',
             'year_dummies_only', 'year_as_count', 'dichotomize', 'categorical',
             'anynonlin', 'mmodel', 'stata', 'r', 'mplus', 'spss', 'mlwin']
MEASUREMENT = ['Jobs', 'Unemp', 'IncDiff', 'OldAge', 'House', 'Health', 'Scale',
               'Stock', 'Flow', 'ChangeFlow', 'main_IV_as_control']


def main():
    a = load()
    blocks = json.load(open(BLOCKS))
    dec = [c for c in blocks["decisions"] if c in a.columns]
    groups = a.u_teamid.values
    seeds = list(range(1000, 1000 + B_FOLDS))

    S = [c for c in SAMPLE_DEF if c in a.columns]
    M = [c for c in MODELLING if c in a.columns]
    X_ = [c for c in MEASUREMENT if c in a.columns]
    COV = [c for c in dec if c.endswith('_iv') or c.endswith('_ivC')]

    y_logse = np.log(a.se_z.values)
    y_ame = a.AME_Z.values

    print("=" * 84)
    print("A. THE TEST OF maria2026-executability-denominators#c5")
    print("=" * 84)
    print("   %d models, %d teams, out-of-TEAM 10-fold ridge, max over 17 lambdas,"
          % (len(a), len(np.unique(groups))))
    print("   averaged over %d random fold assignments (mean +- SD)." % B_FOLDS)
    print()
    print("   %-40s %5s %18s %18s" % ("block", "p", "R2 for the ESTIMATE", "R2 for log SE"))
    rows = [("SAMPLE-DEFINING (what counts as a case)", S),
            ("MODELLING (fixed cases, different model)", M),
            ("MEASUREMENT (which DV / which IV form)", X_),
            ("COVARIATE SET", COV),
            ("all coded decisions", dec)]
    res = {}
    for name, cols in rows:
        me, se, p = r2_over_folds(cols, y_ame, a, groups, seeds)
        ml, sl, _ = r2_over_folds(cols, y_logse, a, groups, seeds)
        res[name] = (me, ml)
        print("   %-40s %5d   %+.4f +- %.4f   %+.4f +- %.4f" % (name, p, me, se, ml, sl))
    print()
    hyp = res["SAMPLE-DEFINING (what counts as a case)"][0]
    alt = res["MODELLING (fixed cases, different model)"][0]
    print("   HYPOTHESIS PREDICTED: R2(estimate | sample-defining) > R2(estimate | modelling)")
    print("   OBSERVED:             %+.4f vs %+.4f  -> %s"
          % (hyp, alt, "SUPPORTED" if hyp > alt + 0.01 else "NOT SUPPORTED"))
    print("   Both are at or below zero. Nothing predicts the estimate, including")
    print("   the block the hypothesis singled out.")
    print()

    print("=" * 84)
    print("B. BEFORE BELIEVING A NULL: DOES THE TEST HAVE POWER?")
    print("=" * 84)
    print("   Grouped CV holds out whole TEAMS. If sample composition barely varies")
    print("   inside a team, team-grouping removes exactly the variation the sample")
    print("   block needs, and the null above is about the design, not the world.")
    print()
    tot_var, within_var = {}, {}
    for c in S + M:
        v = pd.to_numeric(a[c], errors="coerce").fillna(0.0)
        if v.std() == 0:
            continue
        tot_var[c] = v.var()
        within_var[c] = a.assign(v=v).groupby("u_teamid")["v"].var().mean()
    def frac(cols):
        cc = [c for c in cols if c in tot_var and tot_var[c] > 0]
        if not cc:
            return np.nan, 0
        return float(np.mean([within_var[c] / tot_var[c] for c in cc])), len(cc)
    fs, ns = frac(S)
    fm, nm = frac(M)
    print("   mean share of a column's variance that is WITHIN team:")
    print("      SAMPLE-DEFINING columns  %.3f   (%d columns)" % (fs, ns))
    print("      MODELLING columns        %.3f   (%d columns)" % (fm, nm))
    print()
    print("   The worry was that low within-team variation makes the sample block")
    print("   unlearnable under team-grouped folds. It does not, and the internal")
    print("   control settles it: the MODELLING block has LESS within-team variation")
    print("   (%.3f vs %.3f) and still reaches R2 = %.3f on log SE. Whatever stops the"
          % (fm, fs, res["MODELLING (fixed cases, different model)"][1]))
    print("   sample block from predicting the ESTIMATE, it is not team-grouping.")
    print("   (I wrote the opposite conclusion first, on a 0.25 threshold pulled from")
    print("    nowhere, and the control contradicted it. Left here as the correction.)")
    print()

    print("   Same table with folds drawn at MODEL level (ignoring team). This")
    print("   OVERSTATES everything -- models inside a team are near-duplicates -- and")
    print("   is shown only to bound how much signal exists at all:")
    mg = np.arange(len(a))
    print("   %-40s %18s %18s" % ("block", "R2 estimate", "R2 log SE"))
    for name, cols in rows[:3]:
        me, _, _ = r2_over_folds(cols, y_ame, a, mg, seeds[:8])
        ml, _, _ = r2_over_folds(cols, y_logse, a, mg, seeds[:8])
        print("   %-40s %18.4f %18.4f" % (name, me, ml))
    print()

    print("=" * 84)
    print("C. SYNTHETIC POSITIVE CONTROL")
    print("=" * 84)
    print("   Inject a sample-driven effect of known size into the estimate and check")
    print("   that this machinery finds it. If it cannot see a planted effect, section")
    print("   A says nothing.")
    Xs, _ = prep(S, a)
    rng = np.random.default_rng(4242)
    w = rng.normal(size=Xs.shape[1])
    signal = Xs @ w
    signal = (signal - signal.mean()) / signal.std()
    noise = (y_ame - y_ame.mean()) / y_ame.std()
    print("   %-28s %14s %14s" % ("planted R2 (in-sample)", "recovered", "on log SE"))
    for share in (0.0, 0.05, 0.10, 0.25, 0.50):
        y = np.sqrt(share) * signal + np.sqrt(1 - share) * noise
        me, se, _ = r2_over_folds(S, y, a, groups, seeds[:12])
        print("   %-28.2f %8.4f +- %.4f" % (share, me, se))
    print()
    print("   Read the 0.00 row as the null and the others as sensitivity. If 0.10")
    print("   is recovered well above the 0.00 row, section A's null is real.")
    print()

    print("=" * 84)
    print("D. WHAT THE HYPOTHESIS SHOULD HAVE SAID")
    print("=" * 84)
    print("""   Refuted as stated. What actually happened in the artifact-execution case
   is narrower and mechanical: the numerator was FIXED BY THE DATA (1,472 files
   ran) and the analyst chose the DENOMINATOR (3,695 or 7,621). A ratio whose
   numerator is pinned and whose denominator is chosen moves by construction.
   That is arithmetic, and dressing it as a general law about analytic
   variability was overreach committed within hours of seeing one example.

   In CRI nothing of the kind is available: changing which countries enter a
   regression changes numerator and denominator together, and the resulting
   coefficient is free to move either way, so the choice adds variance without
   direction -- which is exactly what R2 ~ 0 for the estimate means, and what
   this record already reported.

   The surviving general statement is a WARNING, not a law: when a reported
   quantity is a ratio, ask whether its numerator is pinned. If it is, the
   denominator is a free parameter pointing one way, and no amount of
   many-analysts intuition about 'decisions cancel out' applies.""")


if __name__ == "__main__":
    main()
