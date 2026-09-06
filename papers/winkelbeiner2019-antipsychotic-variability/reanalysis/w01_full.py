"""w01 -- the antipsychotic corpus: reproduce, then run the same four questions
already answered on the two antidepressant corpora.

TARGETS, taken from the abstract BEFORE computing anything:
    52 RCTs, 15 360 patients, VR = 0.97 (95% CI 0.95-0.99), P = .01
    outcome: PANSS pre-post difference scores, one scale throughout

WHY THIS CORPUS. It is the paper the whole psychiatric variability literature
descends from, it is the one McCutcheon et al. (2022) reanalysed, and it is
genuinely independent of the two antidepressant corpora: different disease,
different drugs, different authors, different data source, no shared trials.
Winkelbeiner & Homan deposited data AND code AND the manuscript source
(https://osf.io/qarvs/), which is the standard the other two did not meet.

FOUR QUESTIONS, the same as on the antidepressant corpora:
  1. does the published VR reproduce, and does it survive clustering
     (75 comparisons sit in 52 studies)?
  2. lambda: how far is this corpus from additive homogeneity? lnVR assumes 0,
     lnCVR assumes 1, and this is the first antipsychotic estimate of it.
  3. D = sigma_AT^2 - sigma_PL^2 in PANSS points^2, corrected weight, with the
     leave-one-out influence beside it. Never reported for antipsychotics.
  4. what D bounds: sigma_TE against rho, and p(1-p)delta^2 <= D_upper.
"""
import csv
import io
import json
import os
import sys

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "tools"))
import statlib  # noqa: E402

CSV = os.path.join(HERE, "..", "artifacts", "response.csv")


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def load():
    rows = []
    with io.open(CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            v = {k: num(r.get(k)) for k in
                 ("mu1tx", "mu1ct", "sd1tx", "sd1ct", "ntx", "nct", "year",
                  "sd0tx", "sd0ct")}
            if any(v[k] is None for k in
                   ("mu1tx", "mu1ct", "sd1tx", "sd1ct", "ntx", "nct")):
                continue
            v["id"] = r["id"]
            v["tx"] = r["tx"]
            rows.append(v)
    return rows


def aggregate_by_study(rows):
    """their model 3: pool comparisons within a study. Their formula
    (response_do.R:425-429) is the CORRECT within-arm pooling
    sqrt(sum(sd^2 (n-1)) / (N - k)), not a mean of SDs."""
    byid = {}
    for r in rows:
        byid.setdefault(r["id"], []).append(r)
    out = []
    for sid, rs in byid.items():
        ntx = sum(r["ntx"] for r in rs)
        nct = sum(r["nct"] for r in rs)
        k = len(rs)
        sdtx = np.sqrt(sum(r["sd1tx"] ** 2 * (r["ntx"] - 1) for r in rs) / (ntx - k))
        sdct = np.sqrt(sum(r["sd1ct"] ** 2 * (r["nct"] - 1) for r in rs) / (nct - k))
        out.append(dict(id=sid, ntx=ntx, nct=nct, sd1tx=sdtx, sd1ct=sdct,
                        mu1tx=float(np.mean([r["mu1tx"] for r in rs])),
                        mu1ct=float(np.mean([r["mu1ct"] for r in rs])),
                        k=k))
    return out


def A(rows, key):
    return np.array([r[key] for r in rows], float)


def main():
    rows = load()
    out = {}
    print("comparisons: %d in %d studies; %d treated and %d control patients"
          % (len(rows), len({r["id"] for r in rows}),
             A(rows, "ntx").sum(), A(rows, "nct").sum()))
    print("  target from the abstract: 52 RCTs, 15 360 patients")

    print()
    print("=== 1. reproduce ===")
    for label, rs in (("per comparison (k=%d)" % len(rows), rows),
                      ("per study, their pooling", aggregate_by_study(rows))):
        n1, s1 = A(rs, "ntx"), A(rs, "sd1tx")
        n2, s2 = A(rs, "nct"), A(rs, "sd1ct")
        y, v = statlib.lnvr(s1, n1, s2, n2)
        m = statlib.re_meta(y, v, method="DL")
        print("  %-26s VR = %.4f [%.4f, %.4f]  p = %.4f  I2 = %.0f%%"
              % (label, np.exp(m["mu"]), np.exp(m["ci"][0]), np.exp(m["ci"][1]),
                 m["p"], 100 * (m["I2"] or 0)))
        out["VR_" + label.split(" (")[0].replace(" ", "_")] = dict(
            value=float(np.exp(m["mu"])),
            ci=[float(np.exp(m["ci"][0])), float(np.exp(m["ci"][1]))],
            p=m["p"], I2=m["I2"], k=m["k"])
    print("  published: VR = 0.97 [0.95, 0.99], p = .01")

    n1, s1, m1 = A(rows, "ntx"), A(rows, "sd1tx"), np.abs(A(rows, "mu1tx"))
    n2, s2, m2 = A(rows, "nct"), A(rows, "sd1ct"), np.abs(A(rows, "mu1ct"))
    y, v = statlib.lnvr(s1, n1, s2, n2)
    cl = np.array([r["id"] for r in rows])
    b = statlib.cluster_bootstrap_meta(y, v, cl, B=4000, seed=7)
    mm = statlib.re_meta(y, v, method="DL")
    print("  clustered on the 52 studies: VR = %.4f [%.4f, %.4f]  (naive SE %.4f, "
          "cluster SE %.4f, ratio %.2f)"
          % (np.exp(mm["mu"]), np.exp(b["ci"][0]), np.exp(b["ci"][1]),
             mm["se"], b["se"], b["se"] / mm["se"]))
    out["VR_cluster_bootstrap"] = dict(
        ci=[float(np.exp(b["ci"][0])), float(np.exp(b["ci"][1]))],
        se_ratio=float(b["se"] / mm["se"]), n_clusters=b["n_clusters"])

    print()
    print("=== 2. lambda: SD proportional to mean^lambda ===")
    rng = np.random.default_rng(52019)

    def slope(s1_, n1_, m1_, s2_, n2_, m2_):
        yy, _ = statlib.lnvr(s1_, n1_, s2_, n2_)
        return stats.linregress(np.log(m1_ / m2_), yy).slope

    def simulate(lam, B=400):
        res = []
        for _ in range(B):
            M1, S1, M2, S2 = [], [], [], []
            for i in range(len(rows)):
                kk = (m1[i] / m2[i]) ** lam
                a = rng.normal(m1[i], s2[i] * kk, int(n1[i]))
                p = rng.normal(m2[i], s2[i], int(n2[i]))
                M1.append(abs(a.mean())); S1.append(a.std(ddof=1))
                M2.append(abs(p.mean())); S2.append(p.std(ddof=1))
            res.append(slope(np.array(S1), n1, np.array(M1),
                             np.array(S2), n2, np.array(M2)))
        return np.array(res)

    b_obs = slope(s1, n1, m1, s2, n2, m2)
    b0, b1 = simulate(0.0), simulate(1.0)
    lam = (b_obs - b0.mean()) / (b1.mean() - b0.mean())
    boots = []
    idx = np.arange(len(rows))
    for _ in range(4000):
        j = rng.choice(idx, size=len(idx), replace=True)
        boots.append((slope(s1[j], n1[j], m1[j], s2[j], n2[j], m2[j])
                      - b0.mean()) / (b1.mean() - b0.mean()))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    print("  observed slope %+.4f; null at lambda=0 %+.4f, at lambda=1 %+.4f"
          % (b_obs, b0.mean(), b1.mean()))
    print("  lambda = %.3f  [%.3f, %.3f]" % (lam, lo, hi))
    print("  lnVR assumes 0: %s   lnCVR assumes 1: %s"
          % ("INSIDE" if lo <= 0 <= hi else "outside",
             "INSIDE" if lo <= 1 <= hi else "outside"))
    out["lambda"] = dict(value=float(lam), ci=[float(lo), float(hi)],
                         b_obs=float(b_obs), b0=float(b0.mean()),
                         b1=float(b1.mean()))

    print()
    print("=== 3. D = sigma_AT^2 - sigma_PL^2, PANSS points^2 ===")
    print("  arm sizes: treated total %d, control total %d; control smaller in "
          "%d of %d comparisons"
          % (n1.sum(), n2.sum(), int(np.sum(n2 < n1)), len(rows)))
    for w in ("naive", "pooled"):
        d, vv = statlib.var_diff(s1, n1, s2, n2, weight=w)
        m = statlib.re_meta(d, vv, method="PM")
        full, half, worst, arg = statlib.max_loo_influence(d, vv)
        print("  %-7s D = %+7.3f [%+7.3f, %+7.3f]  I2 = %2.0f%%   "
              "max LOO %+6.3f (%2.0f%% of CI half) = %s"
              % (w, m["mu"], m["ci"][0], m["ci"][1], 100 * (m["I2"] or 0),
                 worst, 100 * abs(worst) / half, rows[arg]["id"]))
        out["D_" + w] = dict(value=m["mu"], ci=list(m["ci"]), I2=m["I2"],
                             max_loo=float(worst),
                             loo_ratio=float(abs(worst) / half),
                             worst_study=rows[arg]["id"])
    d, vv = statlib.var_diff(s1, n1, s2, n2, weight="pooled")
    bD = statlib.cluster_bootstrap_meta(d, vv, cl, B=4000, seed=11)
    print("  clustered on the 52 studies: D CI [%+.3f, %+.3f] (SE ratio %.2f)"
          % (bD["ci"][0], bD["ci"][1], bD["se"] / statlib.re_meta(d, vv, "PM")["se"]))
    out["D_cluster_ci"] = [float(bD["ci"][0]), float(bD["ci"][1])]

    print()
    print("=== 4. what D bounds ===")
    mP = statlib.re_meta(d, vv, method="PM")
    Dhi = mP["ci"][1]
    sPL = float(np.median(s2))
    mean_eff = float(np.average(np.abs(A(rows, "mu1tx") - A(rows, "mu1ct")),
                                weights=n1 + n2))
    print("  median control-arm SD %.2f PANSS points; n-weighted mean "
          "drug-placebo difference %.2f points" % (sPL, mean_eff))
    print("  %-8s %-22s %-16s" % ("rho", "sigma_TE <= (points)", "as x the mean effect"))
    band = {}
    for rho in (0.0, -0.10, -0.21, -0.32, -0.62):
        disc = (rho * sPL) ** 2 + Dhi
        st = max(0.0, -rho * sPL + np.sqrt(disc)) if disc >= 0 else 0.0
        band["%.2f" % rho] = float(st)
        print("  %-8.2f %-22.2f %-16.2f" % (rho, st, st / mean_eff))
    out["sigma_te_upper"] = band
    out["mean_effect"] = mean_eff
    out["sd_placebo_median"] = sPL
    print()
    print("  benefiter bound at rho = 0, p(1-p)delta^2 <= %.3f:" % Dhi)
    for pfrac in (0.05, 0.10, 0.20, 0.50):
        dm = np.sqrt(Dhi / (pfrac * (1 - pfrac))) if Dhi > 0 else 0.0
        print("    p = %4.2f  ->  delta <= %6.2f PANSS points" % (pfrac, dm))
        out.setdefault("benefiter_bound", {})["%.2f" % pfrac] = float(dm)

    with io.open(os.path.join(HERE, "out_w01.json"), "w", encoding="utf-8",
                 newline="\n") as f:
        json.dump(out, f, indent=1)
    print()
    print("wrote out_w01.json")


if __name__ == "__main__":
    main()
