"""p04 -- try to break p03 before believing it, and adjudicate the CVR decision.

Three things, in this order:

A. CALIBRATE THE D ESTIMATOR. Feed it worlds whose answer is known by
   construction: D = 0, D = +5, D = -5, and the same under a SKEWED
   patient-level distribution (change scores are not normal). Report bias and
   the realised coverage of the nominal 95% interval. A difference of sample
   variances uses Var(s^2) = 2 sigma^4/(n-1), which is a NORMAL-THEORY result:
   under excess kurtosis the true variance is (mu4 - sigma^4)/n, which is
   larger, so the interval should be too narrow. Measure by how much.

B. ADJUDICATE ADDITIVE vs MULTIPLICATIVE on this corpus, the way that works:
   regress lnVR on log(m_AD/m_PL) and compare the OBSERVED slope with the
   slope the same estimator returns in a simulated world where additive
   homogeneity is true by construction. The null slope is not 0.

C. TEST THE STATED REASON FOR USING CVR. Their justification is the
   ACROSS-TRIAL correlation r(M, SD) = 0.55. The correction it licenses is a
   WITHIN-TRIAL, BETWEEN-ARM division. Check whether the across-trial
   correlation survives conditioning on the measurement scale -- if it is
   mostly scale mixing, it cannot license anything.
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

NUM = ("all_n all_sd all_m pooled_sd pooled_m placebo_n placebo_sd placebo_m "
       "k_ad_arms year baseline weeks").split()


def load():
    rows = []
    with io.open(os.path.join(HERE, "dat.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter=";"):
            for k in NUM:
                r[k] = float(r[k]) if r[k] not in ("", "None") else np.nan
            rows.append(r)
    return rows


def d_stat(sd1, n1, sd2, n2):
    d = sd1 ** 2 - sd2 ** 2
    v = 2 * sd1 ** 4 / (n1 - 1) + 2 * sd2 ** 4 / (n2 - 1)
    return d, v


def draw(n, mean, sd, rng, skew=False):
    """n draws with the requested mean and sd; optionally strongly right-skewed."""
    if not skew:
        return rng.normal(mean, sd, n)
    # shifted gamma, shape 2 -> skewness 1.41, excess kurtosis 3.0
    shape = 2.0
    g = rng.gamma(shape, 1.0, n)
    g = (g - shape) / np.sqrt(shape)          # mean 0, sd 1
    return mean + sd * g


def partA(rows, rng, B=600):
    n1 = np.array([r["all_n"] for r in rows])
    n2 = np.array([r["placebo_n"] for r in rows])
    s2 = np.array([r["placebo_sd"] for r in rows])
    print("=== A. calibration of the D estimator ===")
    print("    %d simulated corpora per cell, k=%d trials each, real n and SDs"
          % (B, len(rows)))
    print("    %-26s %10s %10s %10s" % ("world", "true D", "mean D-hat", "coverage"))
    for label, true_D, skew in (("normal, D = 0", 0.0, False),
                                ("normal, D = +5", 5.0, False),
                                ("normal, D = -5", -5.0, False),
                                ("gamma(2) skew, D = 0", 0.0, True),
                                ("gamma(2) skew, D = +5", 5.0, True)):
        hats, cov = [], 0
        for b in range(B):
            v1 = s2 ** 2 + true_D
            if np.any(v1 <= 0):
                continue
            sd1 = np.sqrt(v1)
            e1 = np.array([draw(int(a), 0.0, s, rng, skew).std(ddof=1)
                           for a, s in zip(n1, sd1)])
            e2 = np.array([draw(int(a), 0.0, s, rng, skew).std(ddof=1)
                           for a, s in zip(n2, s2)])
            d, v = d_stat(e1, n1, e2, n2)
            m = statlib.re_meta(d, v, method="PM")
            hats.append(m["mu"])
            if m["ci"][0] <= true_D <= m["ci"][1]:
                cov += 1
        hats = np.array(hats)
        print("    %-26s %10.3f %10.3f %9.1f%%"
              % (label, true_D, hats.mean(), 100.0 * cov / len(hats)))
        yield label, dict(true_D=true_D, mean_hat=float(hats.mean()),
                          coverage=float(cov) / len(hats), B=len(hats))


def partB(rows, rng, B=400):
    print()
    print("=== B. additive vs multiplicative, against a simulated null slope ===")
    n1 = np.array([r["all_n"] for r in rows])
    n2 = np.array([r["placebo_n"] for r in rows])
    m1 = np.array([r["all_m"] for r in rows])
    m2 = np.array([r["placebo_m"] for r in rows])
    s1 = np.array([r["all_sd"] for r in rows])
    s2 = np.array([r["placebo_sd"] for r in rows])

    y_obs, _ = statlib.lnvr(s1, n1, s2, n2)
    x_obs = np.log(m1 / m2)
    obs = stats.linregress(x_obs, y_obs)
    print("    observed slope = %+.4f  (SE %.4f, r = %+.3f)"
          % (obs.slope, obs.stderr, obs.rvalue))

    res = {"observed": dict(slope=float(obs.slope), se=float(obs.stderr),
                            r=float(obs.rvalue))}
    for world in ("additive", "multiplicative"):
        slopes = []
        for b in range(B):
            e1, e2, mm1, mm2 = [], [], [], []
            for i in range(len(rows)):
                if world == "additive":
                    # same SD in both arms; the arm means differ by the real gap
                    a = draw(int(n1[i]), m1[i], s2[i], rng)
                    p = draw(int(n2[i]), m2[i], s2[i], rng)
                else:
                    # treatment multiplies every patient's change by m1/m2
                    kk = m1[i] / m2[i]
                    a = draw(int(n1[i]), m2[i] * kk, s2[i] * kk, rng)
                    p = draw(int(n2[i]), m2[i], s2[i], rng)
                e1.append(a.std(ddof=1)); e2.append(p.std(ddof=1))
                mm1.append(abs(a.mean())); mm2.append(abs(p.mean()))
            e1 = np.array(e1); e2 = np.array(e2)
            mm1 = np.array(mm1); mm2 = np.array(mm2)
            yy, _ = statlib.lnvr(e1, n1, e2, n2)
            slopes.append(stats.linregress(np.log(mm1 / mm2), yy).slope)
        slopes = np.array(slopes)
        lo, hi = np.percentile(slopes, [2.5, 97.5])
        z = (obs.slope - slopes.mean()) / slopes.std(ddof=1)
        print("    %-16s null slope = %+.4f  [%+.4f, %+.4f]   observed is %+.1f SD away"
              % (world, slopes.mean(), lo, hi, z))
        res[world] = dict(null_slope=float(slopes.mean()),
                          ci=[float(lo), float(hi)], z=float(z), B=B)
    verdict = ("additive" if abs(res["additive"]["z"]) < abs(res["multiplicative"]["z"])
               else "multiplicative")
    print("    -> the corpus is closer to the %s null" % verdict)
    res["verdict"] = verdict
    return res


def partC(rows):
    print()
    print("=== C. does the stated reason for CVR survive conditioning on scale? ===")
    m1 = np.array([r["all_m"] for r in rows])
    s1 = np.array([r["all_sd"] for r in rows])
    m2 = np.array([r["placebo_m"] for r in rows])
    s2 = np.array([r["placebo_sd"] for r in rows])
    r_all_ad = stats.pearsonr(m1, s1)
    r_all_pl = stats.pearsonr(m2, s2)
    print("    across ALL 169 trials (their number): r(M,SD) AD %+.3f, placebo %+.3f"
          % (r_all_ad[0], r_all_pl[0]))
    res = {"all": dict(ad=float(r_all_ad[0]), placebo=float(r_all_pl[0]))}
    scales = {}
    for i, r in enumerate(rows):
        scales.setdefault(r["scale"], []).append(i)
    zs_ad, ws = [], []
    for sc in sorted(scales, key=lambda s: -len(scales[s])):
        idx = np.array(scales[sc])
        if len(idx) < 10:
            continue
        a = stats.pearsonr(m1[idx], s1[idx])[0]
        p = stats.pearsonr(m2[idx], s2[idx])[0]
        print("      within %-16s k=%3d   AD %+.3f   placebo %+.3f" % (sc, len(idx), a, p))
        res[sc] = dict(k=len(idx), ad=float(a), placebo=float(p))
        zs_ad.append(np.arctanh(a)); ws.append(len(idx) - 3)
    pooled_r = float(np.tanh(np.average(zs_ad, weights=ws)))
    print("    within-scale pooled (Fisher z, n-3 weights), AD arms: r = %+.3f"
          % pooled_r)
    print("    -> %.0f%% of the across-trial correlation is between-scale, not within"
          % (100 * (1 - pooled_r / r_all_ad[0])))
    res["within_scale_pooled_ad"] = pooled_r

    print()
    print("    the correlation that would actually license a CV normalisation is")
    print("    the WITHIN-trial, BETWEEN-arm one: does an arm with a bigger mean")
    print("    change also have a bigger SD, in the same trial?")
    r_within = stats.pearsonr(np.log(m1 / m2), np.log(s1 / s2))
    print("      r(log mean ratio, log SD ratio) over 169 trials = %+.3f  (p = %.3f)"
          % (r_within[0], r_within[1]))
    res["within_trial_between_arm"] = dict(r=float(r_within[0]),
                                           p=float(r_within[1]))
    return res


def main():
    rows = load()
    rng = np.random.default_rng(20260906)
    out = {"A_calibration": dict(partA(rows, rng))}
    out["B_null_slope"] = partB(rows, rng)
    out["C_cvr_justification"] = partC(rows)
    with io.open(os.path.join(HERE, "out_p04.json"), "w", encoding="utf-8",
                 newline="\n") as f:
        json.dump(out, f, indent=1)
    print()
    print("wrote out_p04.json")


if __name__ == "__main__":
    main()
