"""A11. Before reading a null Mantel result, compute what it could have seen.

My own treatment-effect-heterogeneity area file carries the rule: *before reading any
"no difference", compute the smallest effect the design could resolve*. It applies here.
a10d found CRI choices~estimate rho = +0.120, p = 0.118 -- a number, not a zero, and
whether it means "no association" or "cannot tell" is a property of the design.

Calibration by injection, which is the only honest way: build a response whose
association with the choice distances is CONTROLLED, at a range of strengths, run the
real test on it, and report the strength at which the test rejects 80% of the time.
Same procedure on the NARPS matrices, so the two corpora are on one scale.

Injection: y = lambda * s + sqrt(1-lambda^2) * e, where s is the first principal
coordinate of the choice-distance matrix (the direction in which choices differ most)
and e is independent noise. The response distance is |y_i - y_j|. lambda = 0 is the null
by construction and is included as a false-positive check.
"""
import sys, os, json
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mantel_fast import mantel_fast, _rank_matrix
import load

HERE = os.path.dirname(os.path.abspath(__file__))
CRI = os.path.join(HERE, '..', '..', 'breznau2022-hidden-universe', 'data')
DV_COLS = ['Jobs', 'Unemp', 'IncDiff', 'OldAge', 'House', 'Health']
NSIM = 300
NPERM = 2000


def dist(P):
    P = np.asarray(P, float)
    sd = P.std(0)
    P = (P - P.mean(0)) / np.where(sd > 0, sd, 1)
    return np.sqrt(((np.nan_to_num(P)[:, None, :] - np.nan_to_num(P)[None, :, :]) ** 2).sum(-1))


def pcoa1(D):
    n = D.shape[0]
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ (D ** 2) @ J
    w, V = np.linalg.eigh(B)
    v = V[:, -1] * np.sqrt(max(w[-1], 0))
    return (v - v.mean()) / v.std()


def power_curve(Dc, lambdas, nsim=NSIM, nperm=NPERM, seed=0):
    n = Dc.shape[0]
    s = pcoa1(Dc)
    rng = np.random.default_rng(seed)
    RA, iu = _rank_matrix(Dc)
    a = RA[iu]; ma, sa = a.mean(), a.std()
    rows = []
    for lam in lambdas:
        rej, rhos = 0, []
        for k in range(nsim):
            e = rng.normal(size=n)
            y = lam * s + np.sqrt(max(1 - lam ** 2, 0)) * (e - e.mean()) / e.std()
            Dr = np.abs(y[:, None] - y[None, :])
            RB, _ = _rank_matrix(Dr)
            b = RB[iu]; mb, sb = b.mean(), b.std(); m = len(b)
            obs = float(np.corrcoef(a, b)[0, 1])
            rhos.append(obs)
            null = np.empty(nperm)
            for i in range(nperm):
                p = rng.permutation(n)
                sdot = float((RA[np.ix_(p, p)] * RB).sum() * 0.5)
                null[i] = (sdot / m - ma * mb) / (sa * sb)
            rej += (( (1 + (null >= obs).sum()) / (1 + nperm) ) <= 0.05)
        rows.append(dict(lam=float(lam), mean_rho=float(np.mean(rhos)),
                         sd_rho=float(np.std(rhos, ddof=1)),
                         power=float(rej / nsim)))
        print(f"    lambda={lam:.2f}  mean observed rho={np.mean(rhos):+.4f}  "
              f"power={rej/nsim:.2f}")
    return rows


def main():
    out = {}
    lambdas = [0.0, 0.15, 0.25, 0.35, 0.45, 0.6]

    print('NARPS (64 teams, choice distance from the coded pipeline table):')
    m = load.metadata(); g = m.groupby('teamID')
    CATS = ['package', 'testing', 'correction_method', 'statistic_type',
            'inter_subject_reg', 'motion_correction', 'model_type',
            'used_fmriprep_data', 'regions_definition']
    NUMS = ['smoothing_coef', 'movement_modeling', 'n_participants']
    t = pd.DataFrame(index=sorted(m.teamID.unique()))
    for c in CATS:
        t[c] = g[c].first().astype(str).str.strip().str.lower()
    for c in NUMS:
        t[c] = pd.to_numeric(g[c].first(), errors='coerce')
    C1 = load.unthresh_corr(1)
    teams = [x for x in C1.index if x in t.index]
    X = pd.get_dummies(t.loc[teams], columns=CATS, dummy_na=True).astype(float)
    Dc_narps = dist(X.values)
    out['narps'] = dict(n=len(teams), curve=power_curve(Dc_narps, lambdas, seed=1))

    print('CRI (team level, DV = Jobs):')
    d = pd.read_csv(os.path.join(CRI, 'cri_model_level.csv'))
    blocks = json.load(open(os.path.join(CRI, 'column_blocks.json')))
    dec = [c for c in blocks['decisions'] if c in d.columns and c not in DV_COLS]
    d = d[np.isfinite(d['AME_Z']) & np.isfinite(d['error']) & (d['error'] > 0)]
    sub = d[d['Jobs'] == 1]
    gg = sub.groupby('u_teamid')
    P = gg[dec].mean()
    P = P.loc[:, P.std() > 0]
    Dc_cri = dist(P.values)
    out['cri_jobs'] = dict(n=int(P.shape[0]), curve=power_curve(Dc_cri, lambdas, seed=2))

    for k in ['narps', 'cri_jobs']:
        c = out[k]['curve']
        det = [r for r in c if r['power'] >= 0.8]
        out[k]['rho_at_80pct_power'] = det[0]['mean_rho'] if det else None
        out[k]['false_positive_rate_at_lambda0'] = c[0]['power']
        print(f"{k}: n={out[k]['n']}  false-positive rate at lambda=0: "
              f"{c[0]['power']:.3f}   smallest rho reaching 80% power: "
              f"{out[k]['rho_at_80pct_power']}")
    with open(os.path.join(HERE, '..', 'artifacts', 'a11_mantel_power.json'), 'w') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()


def power_curve_multi(Dc, P, lambdas, nsim=200, nperm=2000, seed=0):
    """Same, but the injected signal is a RANDOM linear combination of all standardised
    choice columns, redrawn each simulation. Closer to a real alternative, in which the
    response depends on many choices at once rather than on the single direction of
    greatest variation."""
    n = Dc.shape[0]
    Z = np.asarray(P, float)
    sd = Z.std(0); Z = (Z - Z.mean(0)) / np.where(sd > 0, sd, 1); Z = np.nan_to_num(Z)
    rng = np.random.default_rng(seed)
    RA, iu = _rank_matrix(Dc)
    a = RA[iu]; ma, sa = a.mean(), a.std()
    rows = []
    for lam in lambdas:
        rej, rhos = 0, []
        for k in range(nsim):
            w = rng.normal(size=Z.shape[1])
            s = Z @ w; s = (s - s.mean()) / s.std()
            e = rng.normal(size=n); e = (e - e.mean()) / e.std()
            y = lam * s + np.sqrt(max(1 - lam ** 2, 0)) * e
            Dr = np.abs(y[:, None] - y[None, :])
            RB, _ = _rank_matrix(Dr)
            b = RB[iu]; mb, sb = b.mean(), b.std(); m = len(b)
            obs = float(np.corrcoef(a, b)[0, 1]); rhos.append(obs)
            null = np.empty(nperm)
            for i in range(nperm):
                p = rng.permutation(n)
                sdot = float((RA[np.ix_(p, p)] * RB).sum() * 0.5)
                null[i] = (sdot / m - ma * mb) / (sa * sb)
            rej += (((1 + (null >= obs).sum()) / (1 + nperm)) <= 0.05)
        rows.append(dict(lam=float(lam), mean_rho=float(np.mean(rhos)),
                         sd_rho=float(np.std(rhos, ddof=1)), power=float(rej / nsim)))
        print(f"    lambda={lam:.2f}  mean rho={np.mean(rhos):+.4f}  power={rej/nsim:.2f}")
    return rows


def main_extend():
    import json as _json
    out = _json.load(open(os.path.join(HERE, '..', 'artifacts', 'a11_mantel_power.json')))
    lam2 = [0.75, 0.9]
    m = load.metadata(); g = m.groupby('teamID')
    CATS = ['package', 'testing', 'correction_method', 'statistic_type',
            'inter_subject_reg', 'motion_correction', 'model_type',
            'used_fmriprep_data', 'regions_definition']
    NUMS = ['smoothing_coef', 'movement_modeling', 'n_participants']
    t = pd.DataFrame(index=sorted(m.teamID.unique()))
    for c in CATS:
        t[c] = g[c].first().astype(str).str.strip().str.lower()
    for c in NUMS:
        t[c] = pd.to_numeric(g[c].first(), errors='coerce')
    teams = [x for x in load.unthresh_corr(1).index if x in t.index]
    X = pd.get_dummies(t.loc[teams], columns=CATS, dummy_na=True).astype(float)
    Dc_n = dist(X.values)
    print('NARPS, extra lambdas, 1-D injection:')
    out['narps']['curve'] += power_curve(Dc_n, lam2, nsim=200, seed=11)
    print('NARPS, multi-dimensional injection:')
    out['narps']['curve_multi'] = power_curve_multi(Dc_n, X.values,
                                                    [0.0, 0.3, 0.5, 0.7], seed=21)

    d = pd.read_csv(os.path.join(CRI, 'cri_model_level.csv'))
    blocks = _json.load(open(os.path.join(CRI, 'column_blocks.json')))
    dec = [c for c in blocks['decisions'] if c in d.columns and c not in DV_COLS]
    d = d[np.isfinite(d['AME_Z']) & np.isfinite(d['error']) & (d['error'] > 0)]
    P = d[d['Jobs'] == 1].groupby('u_teamid')[dec].mean()
    P = P.loc[:, P.std() > 0]
    Dc_c = dist(P.values)
    print('CRI, extra lambdas, 1-D injection:')
    out['cri_jobs']['curve'] += power_curve(Dc_c, lam2, nsim=200, seed=12)
    print('CRI, multi-dimensional injection:')
    out['cri_jobs']['curve_multi'] = power_curve_multi(Dc_c, P.values,
                                                       [0.0, 0.3, 0.5, 0.7], seed=22)
    for k in ['narps', 'cri_jobs']:
        for cname in ['curve', 'curve_multi']:
            c = sorted(out[k][cname], key=lambda r: r['lam'])
            det = [r for r in c if r['power'] >= 0.8]
            out[k][f'rho_at_80pct_power_{cname}'] = det[0]['mean_rho'] if det else None
            print(f"{k} {cname}: smallest rho at 80% power = "
                  f"{out[k][f'rho_at_80pct_power_{cname}']}")
    with open(os.path.join(HERE, '..', 'artifacts', 'a11_mantel_power.json'), 'w') as f:
        _json.dump(out, f, indent=1)
