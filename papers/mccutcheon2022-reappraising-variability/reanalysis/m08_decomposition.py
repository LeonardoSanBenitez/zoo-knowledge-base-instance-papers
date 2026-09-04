"""m08 -- Which component of the pipeline manufactures the number?

m07 showed the published pipeline reports ~14-16 PANSS points of individual
treatment-effect heterogeneity from a world containing exactly none. Two
candidate culprits, and it matters which:

  (i)  the correlation rho, which the estimator returns negative under a null
       because the placebo arm's mean sits on both sides of it (m02-m05); or
  (ii) the "compatibility" deletion, which removes every trial whose observed
       VR falls below sqrt(1 - rho^2) -- that is, every trial whose drug arm
       was LEAST variable, which is the evidence against heterogeneity.

A criticism that names a mechanism has to isolate it. This script crosses the
two: rho fixed at a series of values (including the true 0) x deletion on/off.
With deletion off, incompatible trials contribute sigma_TE = 0 rather than
being removed, which is the honest floor: the data say "no more variance in
the drug arm than the placebo arm", and the honest reading of that is zero,
not "unusable".

Also here: three robustness checks I would want if someone showed me m07 --
skewed change scores, trial-to-trial variation in the within-trial SD, and
DerSimonian-Laird instead of Paule-Mandel pooling.

Run: python m08_decomposition.py
"""
import csv
import math
import os
import sys

import numpy as np
from scipy import stats

sys.path.insert(0, os.path.join("..", "..", "..", "..", "tools"))
from statlib import re_meta  # noqa: E402

ARMS = os.path.join("..", "artifacts", "mcc2021_arm_sizes.csv")
RNG = np.random.default_rng(8080808)

MEAN_EFFECT = -8.6
TAU_EFFECT = 3.3


def load_arms():
    pl, dr = [], []
    with open(ARMS, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            n_p = float(r["n_placebo"])
            n_d = float(r["n_drug_total"]) / float(r["n_drug_arms"])
            if n_p >= 10 and n_d >= 10:
                pl.append(int(n_p))
                dr.append(int(round(n_d)))
    return np.array(pl), np.array(dr)


def draw_change(n, mu, sd, rng, skew=0.0):
    if skew == 0.0:
        return rng.normal(mu, sd, n)
    # skew-normal with the requested shape, rescaled to the target mean and sd
    x = stats.skewnorm.rvs(skew, size=n, random_state=rng)
    return mu + sd * (x - stats.skewnorm.mean(skew)) / stats.skewnorm.std(skew)


def one_world(n_pl, n_dr, sigma_te_true, tau_placebo, rng,
              sd_change=20.0, sd_change_tau=0.0, skew=0.0):
    k = len(n_pl)
    mu_pl = rng.normal(-9.0, tau_placebo, k)
    eff = rng.normal(MEAN_EFFECT, TAU_EFFECT, k)
    sds = (np.full(k, sd_change) if sd_change_tau == 0
           else np.abs(rng.normal(sd_change, sd_change_tau, k)))
    out = []
    for s in range(k):
        chg_p = draw_change(n_pl[s], mu_pl[s], sds[s], rng, skew)
        base_d = draw_change(n_dr[s], mu_pl[s], sds[s], rng, skew)
        d_i = (np.full(n_dr[s], eff[s]) if sigma_te_true == 0
               else rng.normal(eff[s], sigma_te_true, n_dr[s]))
        chg_d = base_d + d_i
        out.append(dict(n_p=n_pl[s], n_d=n_dr[s],
                        m_p=chg_p.mean(), sd_p=chg_p.std(ddof=1),
                        m_d=chg_d.mean(), sd_d=chg_d.std(ddof=1)))
    return out


def weighted_spearman(x, y, w):
    rx, ry = stats.rankdata(x), stats.rankdata(y)
    w = np.asarray(w, float)
    mx = (w * rx).sum() / w.sum()
    my = (w * ry).sum() / w.sum()
    cov = (w * (rx - mx) * (ry - my)).sum() / w.sum()
    vx = (w * (rx - mx) ** 2).sum() / w.sum()
    vy = (w * (ry - my) ** 2).sum() / w.sum()
    return cov / math.sqrt(vx * vy)


def pipeline(trials, rho=None, delete=True, method="PM"):
    if rho is None:
        P = np.array([-t["m_p"] for t in trials])
        T = np.array([t["m_p"] - t["m_d"] for t in trials])
        W = np.array([t["n_p"] + t["n_d"] for t in trials], float)
        rho = weighted_spearman(P, T, W)
    y, v, dropped = [], [], 0
    FLOOR = 1e-3
    for t in trials:
        vr = t["sd_d"] / t["sd_p"]
        disc = vr * vr - 1.0 + rho * rho
        if disc < 0 or (math.sqrt(max(disc, 0.0)) - rho) <= 0:
            if delete:
                dropped += 1
                continue
            s_te = FLOOR                      # honest floor: no excess variance
            dlnu = 0.0
        else:
            u = math.sqrt(disc) - rho
            s_te = max(t["sd_p"] * u, FLOOR)
            dlnu = (vr * vr / math.sqrt(disc)) / u
        v_p = 1.0 / (2 * (t["n_p"] - 1))
        v_d = 1.0 / (2 * (t["n_d"] - 1))
        y.append(math.log(s_te))
        v.append(max(v_p * (1 - dlnu) ** 2 + v_d * dlnu ** 2, 1e-8))
    if len(y) < 3:
        return rho, float("nan"), dropped
    m = re_meta(np.array(y), np.array(v), method=method)
    return rho, math.exp(m["mu"]), dropped


def main():
    n_pl, n_dr = load_arms()
    reps = 250
    rows = []

    print("=" * 100)
    print("1. DECOMPOSITION -- null world (true sigma_TE = 0), tau_placebo = 5")
    print("=" * 100)
    print(f"{'rho used':>28} | {'deletion ON (published)':>26} | "
          f"{'deletion OFF':>18} | {'dropped':>8}")
    for label, rho in (("estimated by their method", None),
                       ("-0.39  their study level", -0.39),
                       ("-0.32  their headline", -0.32),
                       ("-0.20", -0.20),
                       ("-0.10", -0.10),
                       (" 0.00  the truth here", 0.0)):
        on, off, dr = [], [], []
        for _ in range(reps):
            tr = one_world(n_pl, n_dr, 0.0, 5.0, RNG)
            r1, s1, d1 = pipeline(tr, rho=rho, delete=True)
            _, s2, _ = pipeline(tr, rho=(r1 if rho is None else rho), delete=False)
            on.append(s1)
            off.append(s2)
            dr.append(d1)
        print(f"{label:>28} | {np.nanmean(on):10.1f} "
              f"[{np.nanpercentile(on,2.5):.1f},{np.nanpercentile(on,97.5):.1f}]"
              f"   | {np.nanmean(off):8.2f}          | "
              f"{np.mean(dr):5.1f}/{len(n_pl)}")
        rows.append(dict(check="decomposition", rho=label,
                         deletion_on=float(np.nanmean(on)),
                         deletion_off=float(np.nanmean(off)),
                         dropped=float(np.mean(dr))))
    print()
    print("  Read the two columns against each other. The published answer is")
    print("  13.5 PANSS points. Anything in the 'deletion OFF' column that is")
    print("  near zero says the DELETION, not the correlation, is doing the work.")

    print()
    print("=" * 100)
    print("2. ROBUSTNESS of the null-world result (deletion ON, rho estimated)")
    print("=" * 100)
    variants = [
        ("baseline: normal, SD 20 fixed, PM", dict()),
        ("skewed change scores (skewnorm a=4)", dict(skew=4.0)),
        ("skewed the other way (a=-4)", dict(skew=-4.0)),
        ("within-trial SD varies (20 +/- 4)", dict(sd_change_tau=4.0)),
        ("smaller trials: SD 20, arms halved", dict(halve=True)),
        ("DerSimonian-Laird pooling", dict(method="DL")),
    ]
    for label, kw in variants:
        method = kw.pop("method", "PM")
        halve = kw.pop("halve", False)
        npl = np.maximum(10, n_pl // 2) if halve else n_pl
        ndr = np.maximum(10, n_dr // 2) if halve else n_dr
        vals, rhos = [], []
        for _ in range(reps):
            tr = one_world(npl, ndr, 0.0, 5.0, RNG, **kw)
            r, s, _ = pipeline(tr, delete=True, method=method)
            vals.append(s)
            rhos.append(r)
        print(f"  {label:<38} rho {np.mean(rhos):+.3f}   pooled sigma_TE "
              f"{np.nanmean(vals):6.1f} "
              f"[{np.nanpercentile(vals,2.5):.1f},{np.nanpercentile(vals,97.5):.1f}]")
        rows.append(dict(check="robustness", variant=label,
                         rho=float(np.mean(rhos)),
                         sigma_te=float(np.nanmean(vals))))
    print()
    print("  Published: 13.5 [12.7, 14.3]. Every row above comes from a world")
    print("  with zero individual treatment-effect heterogeneity.")

    keys = sorted({k for r in rows for k in r})
    with open("out_decomposition.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print("\nwrote out_decomposition.csv")


if __name__ == "__main__":
    main()
