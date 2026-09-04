"""m05 -- The coupling artifact on real data, and a correction meta-analysts
can actually compute.

m02-m04 showed by simulation that the study-level estimator of rho is biased
negative because the placebo arm's mean appears on both sides of the
correlation with opposite signs:

    placebo response  P_s = (baseline or zero) - m_pbo
    treatment effect  T_s = m_pbo - m_drug

so Cov(P, T) carries a term -Var(sampling error of m_pbo), which is negative
whatever the truth is.

THE POINT OF THIS SCRIPT. That sampling variance is not unknown. A meta-analysis
already has it: Var(m_pbo) = sd_pbo^2 / n_pbo, printed in every forest plot. So
the artifact can be removed analytically from published aggregate data, with no
new design and no individual patient data:

    Cov_corrected  = Cov_obs + mean(sd_pbo^2 / n_pbo)
    Var_P_corrected = Var_obs(P) - mean(sd_pbo^2 / n_pbo)
    Var_T_corrected = Var_obs(T) - mean(sd_pbo^2 / n_pbo) - mean(sd_drug^2 / n_drug)
    rho_corrected  = Cov_c / sqrt(Var_P_c * Var_T_c)

This is an ordinary errors-in-variables correction; the only novelty is
noticing that the two error terms are the SAME error and therefore correlated
across the two variables rather than independent.

DATA: the Cipriani GRISELDA workbook extraction produced for
munkholm2020-antidepressant-variability, 344 drug-vs-placebo comparisons in 221
studies, 61,144 adults. Sign convention here: positive = improvement.

Run: python m05_real_data.py
"""
import csv
import math
import os

import numpy as np
from scipy import stats

SRC = os.path.join("..", "..", "munkholm2020-antidepressant-variability",
                   "reanalysis", "out_comparisons.csv")
RNG = np.random.default_rng(31415)


def load():
    rows = []
    with open(SRC, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            try:
                d = dict(
                    study=r["study"], scale=r["scale"],
                    is_change=r["is_change"] == "True",
                    n_drug=float(r["n_drug"]), m_drug=float(r["m_drug"]),
                    sd_drug=float(r["sd_drug"]), n_pbo=float(r["n_pbo"]),
                    m_pbo=float(r["m_pbo"]), sd_pbo=float(r["sd_pbo"]),
                    base_pbo=float(r["base_pbo"]) if r["base_pbo"] else float("nan"),
                )
            except (ValueError, KeyError):
                continue
            if d["n_drug"] < 2 or d["n_pbo"] < 2 or d["sd_pbo"] <= 0:
                continue
            # improvement-positive
            if d["is_change"]:
                d["P"] = -d["m_pbo"]
            else:
                if not math.isfinite(d["base_pbo"]):
                    continue
                d["P"] = d["base_pbo"] - d["m_pbo"]
            d["T"] = d["m_pbo"] - d["m_drug"]
            d["var_mp"] = d["sd_pbo"] ** 2 / d["n_pbo"]
            d["var_md"] = d["sd_drug"] ** 2 / d["n_drug"]
            rows.append(d)
    return rows


def corrected_rho(P, T, var_mp, var_md):
    """Pearson rho with the shared placebo sampling error removed."""
    cov = np.cov(P, T, ddof=1)
    vP, vT, cPT = cov[0, 0], cov[1, 1], cov[0, 1]
    m_p, m_d = var_mp.mean(), var_md.mean()
    vP_c = vP - m_p
    vT_c = vT - m_p - m_d
    cPT_c = cPT + m_p
    if vP_c <= 0 or vT_c <= 0:
        return float("nan"), vP_c, vT_c, cPT_c
    return cPT_c / math.sqrt(vP_c * vT_c), vP_c, vT_c, cPT_c


def raw_rhos(P, T):
    return (stats.pearsonr(P, T).statistic, stats.spearmanr(P, T).statistic)


def cluster_bootstrap(rows, studies, B=4000):
    """Resample whole studies, since comparisons within a study share arms."""
    by = {}
    for r in rows:
        by.setdefault(r["study"], []).append(r)
    keys = list(by)
    out_raw, out_corr = [], []
    for _ in range(B):
        pick = RNG.choice(len(keys), len(keys), replace=True)
        sub = [r for i in pick for r in by[keys[i]]]
        P = np.array([r["P"] for r in sub])
        T = np.array([r["T"] for r in sub])
        vp = np.array([r["var_mp"] for r in sub])
        vd = np.array([r["var_md"] for r in sub])
        if len(P) < 5:
            continue
        out_raw.append(stats.pearsonr(P, T).statistic)
        c, *_ = corrected_rho(P, T, vp, vd)
        if math.isfinite(c):
            out_corr.append(c)
    return np.array(out_raw), np.array(out_corr)


def report(label, rows):
    P = np.array([r["P"] for r in rows])
    T = np.array([r["T"] for r in rows])
    vp = np.array([r["var_mp"] for r in rows])
    vd = np.array([r["var_md"] for r in rows])
    n_studies = len({r["study"] for r in rows})
    pear, spear = raw_rhos(P, T)
    corr, vP_c, vT_c, cPT_c = corrected_rho(P, T, vp, vd)
    br, bc = cluster_bootstrap(rows, n_studies)
    print(f"\n--- {label}: {len(rows)} comparisons in {n_studies} studies ---")
    print(f"  mean placebo response  {P.mean():7.3f}   SD {P.std(ddof=1):6.3f}")
    print(f"  mean treatment effect  {T.mean():7.3f}   SD {T.std(ddof=1):6.3f}")
    print(f"  mean Var(m_pbo)        {vp.mean():7.3f}   "
          f"= {100*vp.mean()/P.var(ddof=1):5.1f}% of Var(placebo response)")
    print(f"  mean Var(m_drug)       {vd.mean():7.3f}")
    print(f"  rho  Spearman (their statistic)   {spear:+.3f}")
    print(f"  rho  Pearson,   as published      {pear:+.3f}   "
          f"[{np.percentile(br,2.5):+.3f},{np.percentile(br,97.5):+.3f}] cluster boot")
    print(f"  rho  Pearson,   DE-COUPLED        {corr:+.3f}   "
          f"[{np.percentile(bc,2.5):+.3f},{np.percentile(bc,97.5):+.3f}] cluster boot")
    print(f"  share of the raw correlation that is shared sampling error: "
          f"{100*(1 - (corr/pear if pear else 0)):.0f}%")
    return dict(subset=label, k=len(rows), studies=n_studies,
                spearman=spear, pearson_raw=pear,
                pearson_raw_lo=np.percentile(br, 2.5),
                pearson_raw_hi=np.percentile(br, 97.5),
                pearson_corrected=corr,
                pearson_corrected_lo=np.percentile(bc, 2.5),
                pearson_corrected_hi=np.percentile(bc, 97.5),
                mean_var_mpbo=vp.mean(), mean_var_mdrug=vd.mean())


def validate_correction():
    """Before trusting the correction on real data, check it on data where the
    answer is known. Generate studies with a KNOWN true study-level rho, add
    sampling error of a known size, and see whether the correction recovers it."""
    print("=" * 92)
    print("0. VALIDATION -- does the correction recover a known truth?")
    print("=" * 92)
    print(f"{'true rho':>9} {'arm n':>7} | {'raw Pearson':>13} | {'corrected':>13}")
    out = []
    for true_rho in (0.0, -0.30, -0.50, +0.30):
        for arm_n in (30, 60, 130):
            raws, cors = [], []
            for _ in range(300):
                k = 200
                sd_within = 9.0
                cov = np.array([[36.0, true_rho * 6.0 * 3.0],
                                [true_rho * 6.0 * 3.0, 9.0]])
                lat = RNG.multivariate_normal([10.0, 2.5], cov, k)
                Ptrue, Ttrue = lat[:, 0], lat[:, 1]
                e_p = RNG.normal(0, sd_within / math.sqrt(arm_n), k)
                e_d = RNG.normal(0, sd_within / math.sqrt(arm_n), k)
                # P observed carries -e_p ; T observed carries +e_p - e_d
                P = Ptrue + e_p
                T = Ttrue - e_p + e_d
                vp = np.full(k, sd_within ** 2 / arm_n)
                vd = np.full(k, sd_within ** 2 / arm_n)
                raws.append(stats.pearsonr(P, T).statistic)
                c, *_ = corrected_rho(P, T, vp, vd)
                cors.append(c)
            raws, cors = np.array(raws), np.array(cors)
            print(f"{true_rho:9.2f} {arm_n:7d} | {raws.mean():+13.3f} | "
                  f"{cors.mean():+13.3f}")
            out.append(dict(true_rho=true_rho, arm_n=arm_n,
                            raw=raws.mean(), corrected=cors.mean()))
    print("\n  The correction is only worth using if the right-hand column")
    print("  tracks the left-hand one. Read it before reading anything below.")
    return out


def main():
    val = validate_correction()
    rows = load()
    print()
    print("=" * 92)
    print("1. REAL DATA -- Cipriani GRISELDA, antidepressants vs placebo")
    print("=" * 92)
    res = [report("all comparisons", rows)]
    ch = [r for r in rows if r["is_change"]]
    ep = [r for r in rows if not r["is_change"]]
    if len(ch) > 20:
        res.append(report("change scores only (correction exact here)", ch))
    if len(ep) > 20:
        res.append(report("raw endpoint scores only", ep))

    with open("out_real_validation.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(val[0].keys()))
        w.writeheader()
        w.writerows(val)
    with open("out_real_rho.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(res[0].keys()))
        w.writeheader()
        w.writerows(res)
    print("\nwrote out_real_validation.csv, out_real_rho.csv")


if __name__ == "__main__":
    main()
