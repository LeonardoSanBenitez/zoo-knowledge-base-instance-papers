"""w02 -- w01 found D = -27.5 [-45.1, -10.0] PANSS points^2 on the antipsychotic
corpus: the treated arm is SIGNIFICANTLY LESS variable than the control arm.

WHY THAT IS NOT AN ORDINARY RESULT. The decomposition this whole literature runs on is

    D = sigma_AT^2 - sigma_PL^2 = sigma_TE^2 + 2 rho sigma_PL sigma_TE

At rho = 0 -- the assumption every "VR near 1 means no heterogeneity" reading makes,
including this paper's -- D = sigma_TE^2, which cannot be negative. So a D whose
confidence interval excludes zero from below says the model is wrong somewhere. Either
rho < 0 (the patients who would have done worse on placebo are the ones who gain most),
or something outside the model is compressing the treated arm.

BEFORE claiming the first, rule out the boring versions of the second. Four tests, in
increasing order of how much I expect them to explain:

  A. RANDOMISATION CHECK / negative control. Run the identical statistic on the
     BASELINE SDs, which are in the deposit for 38 of the 75 comparisons. Under
     randomisation the baseline variability ratio is 1 by construction. If it is
     already below 1, the endpoint result is an extraction or allocation artifact and
     not a treatment effect.

  B. FLOOR. PANSS has a hard minimum of 30. A larger mean reduction pushes more
     patients toward it, and a floor compresses an arm's SD. The treated arm reduces
     more by definition of the drug working, so a floor produces D < 0 with NO
     heterogeneity anywhere. Simulate it with this corpus's own numbers.

  C. MULTIPLICATIVE SHRINKAGE. If the drug scales every patient's severity by k < 1
     rather than subtracting a constant, the treated SD scales by k too and D < 0
     follows. This is lambda = 1, and w01 measured lambda = -0.023 [-0.147, 0.078] --
     so it is already excluded, but state the size of the D it WOULD have produced, to
     show the exclusion is quantitative and not just a p-value.

  D. What is left, if anything, for rho.
"""
import csv
import io
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "tools"))
import statlib  # noqa: E402

CSV = os.path.join(HERE, "..", "artifacts", "response.csv")
PANSS_FLOOR = 30.0     # every item scored 1-7, 30 items -> minimum total 30


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
                 ("mu1tx", "mu1ct", "sd1tx", "sd1ct", "ntx", "nct",
                  "sd0tx", "sd0ct")}
            if any(v[k] is None for k in
                   ("mu1tx", "mu1ct", "sd1tx", "sd1ct", "ntx", "nct")):
                continue
            v["id"] = r["id"]
            rows.append(v)
    return rows


def A(rows, k):
    return np.array([r[k] for r in rows], float)


def pooled_D(s1, n1, s2, n2, method="PM"):
    d, v = statlib.var_diff(s1, n1, s2, n2, weight="pooled")
    return statlib.re_meta(d, v, method=method)


def main():
    rows = load()
    out = {}
    n1, s1, m1 = A(rows, "ntx"), A(rows, "sd1tx"), np.abs(A(rows, "mu1tx"))
    n2, s2, m2 = A(rows, "nct"), A(rows, "sd1ct"), np.abs(A(rows, "mu1ct"))
    obs = pooled_D(s1, n1, s2, n2)
    print("observed (w01): D = %+.3f [%+.3f, %+.3f] PANSS points^2, k = %d"
          % (obs["mu"], obs["ci"][0], obs["ci"][1], obs["k"]))

    print()
    print("=== A. randomisation / baseline negative control ===")
    base = [r for r in rows if r["sd0tx"] is not None and r["sd0ct"] is not None]
    print("  comparisons reporting a baseline SD for BOTH arms: %d of %d"
          % (len(base), len(rows)))
    if base:
        b1, bn1 = A(base, "sd0tx"), A(base, "ntx")
        b2, bn2 = A(base, "sd0ct"), A(base, "nct")
        y, v = statlib.lnvr(b1, bn1, b2, bn2)
        mv = statlib.re_meta(y, v, method="DL")
        mb = pooled_D(b1, bn1, b2, bn2)
        print("  BASELINE  VR = %.4f [%.4f, %.4f]  p = %.3f"
              % (np.exp(mv["mu"]), np.exp(mv["ci"][0]), np.exp(mv["ci"][1]), mv["p"]))
        print("  BASELINE  D  = %+.3f [%+.3f, %+.3f]" % (mb["mu"], mb["ci"][0], mb["ci"][1]))
        # and the endpoint statistic on the SAME subset, so it is like for like
        sub = pooled_D(A(base, "sd1tx"), bn1, A(base, "sd1ct"), bn2)
        ye, ve = statlib.lnvr(A(base, "sd1tx"), bn1, A(base, "sd1ct"), bn2)
        me = statlib.re_meta(ye, ve, method="DL")
        print("  same %d comparisons, ENDPOINT VR = %.4f [%.4f, %.4f], "
              "D = %+.3f [%+.3f, %+.3f]"
              % (len(base), np.exp(me["mu"]), np.exp(me["ci"][0]),
                 np.exp(me["ci"][1]), sub["mu"], sub["ci"][0], sub["ci"][1]))
        out["baseline"] = dict(k=len(base), vr=float(np.exp(mv["mu"])),
                               vr_ci=[float(np.exp(mv["ci"][0])),
                                      float(np.exp(mv["ci"][1]))],
                               D=mb["mu"], D_ci=list(mb["ci"]),
                               endpoint_same_subset_D=sub["mu"],
                               endpoint_same_subset_D_ci=list(sub["ci"]))

    print()
    print("=== B. floor at PANSS 30, additive homogeneity, no heterogeneity at all ===")
    rng = np.random.default_rng(2019)
    print("  simulate each comparison: baseline ~ N(mu_b, sd_b), change ~ N(m_i, s_i)")
    print("  with the SAME change SD in both arms, then cap the change at")
    print("  baseline - %.0f. sigma_TE = 0 by construction." % PANSS_FLOOR)
    for mu_b, sd_b in ((90.0, 15.0), (95.0, 18.0), (80.0, 12.0)):
        Ds = []
        for _ in range(200):
            e1, e2 = [], []
            for i in range(len(rows)):
                for (nn, mm, store) in ((n1[i], m1[i], e1), (n2[i], m2[i], e2)):
                    b = rng.normal(mu_b, sd_b, int(nn))
                    ch = rng.normal(mm, s2[i], int(nn))
                    ch = np.minimum(ch, np.maximum(b - PANSS_FLOOR, 0.0))
                    store.append(ch.std(ddof=1))
            Ds.append(pooled_D(np.array(e1), n1, np.array(e2), n2)["mu"])
        Ds = np.array(Ds)
        lo, hi = np.percentile(Ds, [2.5, 97.5])
        print("  baseline N(%.0f, %.0f):  D from a world with NO heterogeneity = "
              "%+7.3f  [%+7.3f, %+7.3f]" % (mu_b, sd_b, Ds.mean(), lo, hi))
        out.setdefault("floor", {})["N(%.0f,%.0f)" % (mu_b, sd_b)] = dict(
            mean=float(Ds.mean()), ci=[float(lo), float(hi)])
    print("  observed is %+.1f. A floor explains it only if these reach it."
          % obs["mu"])

    print()
    print("=== C. what a purely multiplicative drug would have produced ===")
    k_scale = float(np.average(m1 / m2, weights=n1 + n2))
    print("  n-weighted mean change ratio treated/control = %.3f" % k_scale)
    Ds = []
    for _ in range(200):
        e1, e2 = [], []
        for i in range(len(rows)):
            kk = m1[i] / m2[i]
            e1.append(rng.normal(m1[i], s2[i] * kk, int(n1[i])).std(ddof=1))
            e2.append(rng.normal(m2[i], s2[i], int(n2[i])).std(ddof=1))
        Ds.append(pooled_D(np.array(e1), n1, np.array(e2), n2)["mu"])
    Ds = np.array(Ds)
    print("  D under lambda = 1 (SD scales with the mean) = %+.1f [%+.1f, %+.1f]"
          % (Ds.mean(), *np.percentile(Ds, [2.5, 97.5])))
    print("  -> POSITIVE, because the treated arm's mean CHANGE is the larger one.")
    print("     Multiplicative shrinkage of the SCORE and multiplicative scaling of")
    print("     the CHANGE point opposite ways; on change scores lambda = 1 makes the")
    print("     treated arm MORE variable, so it cannot explain a negative D either.")
    out["multiplicative_D"] = dict(mean=float(Ds.mean()),
                                   ci=[float(x) for x in
                                       np.percentile(Ds, [2.5, 97.5])])

    print()
    print("=== D. what is left ===")
    sPL = float(np.median(s2))
    print("  If the decomposition holds and sigma_TE >= 0, then D < 0 requires")
    print("  rho < 0 and |2 rho sigma_PL sigma_TE| > sigma_TE^2, i.e.")
    print("  sigma_TE < -2 rho sigma_PL. At the observed D and sigma_PL = %.1f:" % sPL)
    print("  %-8s %-28s" % ("rho", "sigma_TE consistent with D (points)"))
    for rho in (-0.05, -0.10, -0.21, -0.32, -0.62):
        for lab, DD in (("point", obs["mu"]), ("upper", obs["ci"][1])):
            disc = (rho * sPL) ** 2 + DD
            st = -rho * sPL + np.sqrt(disc) if disc >= 0 else float("nan")
            if lab == "point":
                p_ = st
            else:
                u_ = st
        print("  %-8.2f point %6.2f   at D's upper limit %6.2f" % (rho, p_, u_))
        out.setdefault("sigma_te_given_negative_D", {})["%.2f" % rho] = \
            dict(at_point=float(p_), at_upper=float(u_))
    print("  (a NaN means no non-negative sigma_TE is consistent with that rho:")
    print("   the data exclude that value of rho outright)")

    with io.open(os.path.join(HERE, "out_w02.json"), "w", encoding="utf-8",
                 newline="\n") as f:
        json.dump(out, f, indent=1)
    print()
    print("wrote out_w02.json")


if __name__ == "__main__":
    main()
