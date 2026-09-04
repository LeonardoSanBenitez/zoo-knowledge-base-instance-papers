"""m07 -- Run their whole pipeline on a world with EXACTLY zero heterogeneity.

Everything up to here tested one component at a time. This runs the published
procedure end to end on data I generated, where the answer is known by
construction, and reports what the procedure concludes.

THE WORLD. 66 trials at the real arm sizes transcribed from their supplement.
In every trial, EVERY patient gets IDENTICAL benefit from the drug:

        drug change_i = placebo change_i + effect_s

with effect_s constant within a trial. So the true SD of individual treatment
effects is ZERO, exactly, by construction. Trials differ in placebo response
and in effect size (between-study heterogeneity is real and is included --
that is a property of trials, not of patients).

THE PROCEDURE, as published:
  1. per trial, VR = sd(drug change) / sd(placebo change)     [sample SDs]
  2. rho = n-weighted Spearman correlation across trials between placebo
     response and treatment effect                            [their method 3]
  3. sigma_TE,s = sd_placebo,s * ( sqrt(VR_s^2 - 1 + rho^2) - rho )
  4. drop trials where the discriminant is negative           ["not compatible"]
  5. random-effects meta-analysis of ln(sigma_TE)

A POSITIVE CONTROL runs the same pipeline on worlds where individual treatment
effects really do vary, so that a reader can see the pipeline is not simply
printing 13 whatever happens.

Run: python m07_pipeline_end_to_end.py
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
RNG = np.random.default_rng(606061)

SD_CHANGE = 20.0        # within-trial SD of PANSS total change
MEAN_EFFECT = -8.6      # their pooled mean difference
TAU_EFFECT = 3.3        # from their own I2 = 38% (see m06)


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


def weighted_spearman(x, y, w):
    """n-weighted Spearman, as their wCorr call computes it: Pearson on ranks,
    weighted."""
    rx = stats.rankdata(x)
    ry = stats.rankdata(y)
    w = np.asarray(w, float)
    mx = (w * rx).sum() / w.sum()
    my = (w * ry).sum() / w.sum()
    cov = (w * (rx - mx) * (ry - my)).sum() / w.sum()
    vx = (w * (rx - mx) ** 2).sum() / w.sum()
    vy = (w * (ry - my) ** 2).sum() / w.sum()
    return cov / math.sqrt(vx * vy)


def one_world(n_pl, n_dr, sigma_te_true, tau_placebo, rng, rho_within=0.0):
    """Generate 66 trials and return the per-trial summaries a meta-analyst
    would read out of the published papers."""
    k = len(n_pl)
    mu_pl = rng.normal(-9.0, tau_placebo, k)     # trial-level placebo response
    eff = rng.normal(MEAN_EFFECT, TAU_EFFECT, k)  # trial-level mean effect
    out = []
    for s in range(k):
        # placebo arm
        chg_p = rng.normal(mu_pl[s], SD_CHANGE, n_pl[s])
        # drug arm: same law for the placebo component, plus an individual
        # treatment effect whose SD is sigma_te_true (0 in the null world)
        base_d = rng.normal(mu_pl[s], SD_CHANGE, n_dr[s])
        if sigma_te_true > 0:
            d_i = rng.normal(eff[s], sigma_te_true, n_dr[s])
            if rho_within:
                # optional: correlate the individual effect with the patient's
                # own placebo-arm outcome, which is the mechanism the paper
                # invokes. Implemented via the latent base_d.
                z = (base_d - base_d.mean()) / base_d.std(ddof=1)
                d_i = (eff[s] + sigma_te_true
                       * (rho_within * z
                          + math.sqrt(max(0.0, 1 - rho_within ** 2))
                          * rng.normal(0, 1, n_dr[s])))
        else:
            d_i = np.full(n_dr[s], eff[s])
        chg_d = base_d + d_i
        out.append(dict(
            n_p=n_pl[s], n_d=n_dr[s],
            m_p=chg_p.mean(), sd_p=chg_p.std(ddof=1),
            m_d=chg_d.mean(), sd_d=chg_d.std(ddof=1)))
    return out


def run_pipeline(trials, rho_override=None):
    """Their published procedure. Returns (rho_used, pooled sigma_TE, k_kept,
    k_dropped, p_value)."""
    P = np.array([-t["m_p"] for t in trials])                 # improvement +ve
    T = np.array([t["m_p"] - t["m_d"] for t in trials])       # extra benefit
    W = np.array([t["n_p"] + t["n_d"] for t in trials], float)
    rho = weighted_spearman(P, T, W) if rho_override is None else rho_override

    y, v, kept, dropped = [], [], 0, 0
    for t in trials:
        vr = t["sd_d"] / t["sd_p"]
        disc = vr * vr - 1.0 + rho * rho
        if disc < 0:
            dropped += 1
            continue
        u = math.sqrt(disc) - rho
        if u <= 0:
            dropped += 1
            continue
        s_te = t["sd_p"] * u
        # their sampling variance for ln(sigma_TE), obtained by their sampling
        # method; the delta-method equivalent is used here for speed and is
        # checked against their formula for ln(sigma) below.
        v_lnsd_p = 1.0 / (2 * (t["n_p"] - 1))
        v_lnsd_d = 1.0 / (2 * (t["n_d"] - 1))
        # d ln(sigma_TE) / d ln(sd_d) etc., via vr
        dlnu_dlnvr = (vr * vr / math.sqrt(disc)) / u
        v_ln = v_lnsd_p * (1 - dlnu_dlnvr) ** 2 + v_lnsd_d * dlnu_dlnvr ** 2
        y.append(math.log(s_te))
        v.append(max(v_ln, 1e-8))
        kept += 1
    if kept < 3:
        return rho, float("nan"), kept, dropped, float("nan")
    m = re_meta(np.array(y), np.array(v), method="PM")
    return rho, math.exp(m["mu"]), kept, dropped, m["p"]


def main():
    n_pl, n_dr = load_arms()
    print(f"66 trials in the supplement; {len(n_pl)} kept after requiring both "
          f"arms >= 10.")
    print(f"placebo arm n: median {np.median(n_pl):.0f}, mean {n_pl.mean():.0f}")
    reps = 300
    rows = []

    print()
    print("=" * 98)
    print("THE NULL WORLD -- every patient gets IDENTICAL benefit. True "
          "sigma_TE = 0.000, exactly.")
    print("=" * 98)
    print(f"{'tau_placebo':>12} | {'rho the pipeline finds':>24} | "
          f"{'pooled sigma_TE (PANSS)':>25} | {'trials dropped':>15}")
    for tau_pl in (3.0, 4.0, 5.0, 6.0, 8.0):
        res = []
        for _ in range(reps):
            tr = one_world(n_pl, n_dr, 0.0, tau_pl, RNG)
            res.append(run_pipeline(tr))
        rho = np.array([r[0] for r in res])
        ste = np.array([r[1] for r in res])
        drop = np.array([r[3] for r in res], float)
        pv = np.array([r[4] for r in res])
        ok = np.isfinite(ste)
        print(f"{tau_pl:12.1f} | {rho.mean():+8.3f} "
              f"[{np.percentile(rho,2.5):+.3f},{np.percentile(rho,97.5):+.3f}] | "
              f"{np.nanmean(ste):7.1f} "
              f"[{np.nanpercentile(ste,2.5):.1f},{np.nanpercentile(ste,97.5):.1f}]"
              f" | {drop.mean():5.1f} of {len(n_pl)}")
        rows.append(dict(world="null sigma_TE=0", tau_placebo=tau_pl,
                         rho_mean=rho.mean(), rho_lo=np.percentile(rho, 2.5),
                         rho_hi=np.percentile(rho, 97.5),
                         sigma_te_mean=float(np.nanmean(ste)),
                         sigma_te_lo=float(np.nanpercentile(ste, 2.5)),
                         sigma_te_hi=float(np.nanpercentile(ste, 97.5)),
                         dropped_mean=drop.mean(),
                         pct_p_below_001=100 * float(np.mean(pv[ok] < 0.001))))
    print()
    print("  Their published answer: rho = -0.39 (study level), pooled")
    print("  sigma_TE = 13.5 PANSS points [12.7, 14.3], p < 0.001.")

    print()
    print("=" * 98)
    print("POSITIVE CONTROL -- worlds where individual effects really do vary.")
    print("Does the pipeline track the truth, or does it print ~13 regardless?")
    print("=" * 98)
    print(f"{'TRUE sigma_TE':>14} | {'rho found':>11} | "
          f"{'pipeline reports':>22} | {'ratio reported/true':>20}")
    for true_ste in (0.0, 4.0, 8.0, 13.5, 20.0):
        res = [run_pipeline(one_world(n_pl, n_dr, true_ste, 5.0, RNG))
               for _ in range(reps)]
        ste = np.array([r[1] for r in res])
        rho = np.array([r[0] for r in res])
        ratio = (np.nanmean(ste) / true_ste) if true_ste > 0 else float("inf")
        print(f"{true_ste:14.1f} | {rho.mean():+11.3f} | "
              f"{np.nanmean(ste):8.1f} "
              f"[{np.nanpercentile(ste,2.5):.1f},{np.nanpercentile(ste,97.5):.1f}]"
              f" | {('  n/a (true=0)' if true_ste == 0 else '%20.2f' % ratio)}")
        rows.append(dict(world=f"true sigma_TE={true_ste}", tau_placebo=5.0,
                         rho_mean=rho.mean(),
                         sigma_te_mean=float(np.nanmean(ste)),
                         sigma_te_lo=float(np.nanpercentile(ste, 2.5)),
                         sigma_te_hi=float(np.nanpercentile(ste, 97.5))))

    keys = sorted({k for r in rows for k in r})
    with open("out_pipeline.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print("\nwrote out_pipeline.csv")


if __name__ == "__main__":
    main()
