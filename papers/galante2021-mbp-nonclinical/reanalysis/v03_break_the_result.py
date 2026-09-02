#!/usr/bin/env python3
"""v03 -- try to break the VR = 0.90 result before believing it.

v02 found that after a mindfulness-based programme the treated arm's standard
deviation is about 10% SMALLER than the control arm's (lnVR = -0.101, 95% cluster
bootstrap [-0.144, -0.059], 212 outcomes in 71 trials), while at BASELINE in the
same trials it is zero (+0.011, [-0.017, +0.041]). Six ways it could still be an
artifact, each tested here:

  A  FLOOR / MEAN-VARIANCE COUPLING, done properly. Decompose lnVR into the part
     a pure location shift would produce under the coupling measured in the
     UNTREATED control arms, and the remainder. Also show numerically why lnCVR
     -- which assumes the coupling slope is exactly 1 -- over-corrects here.

  B  A SIMULATION WITH THE ANSWER KNOWN. Generate bounded-scale data in which
     every participant improves by EXACTLY the same amount (no heterogeneity at
     all), censor at the scale floor, and run the whole pipeline. How much
     negative lnVR does a pure location shift on a floored scale manufacture?

  C  DIFFERENTIAL ATTRITION. If the treated arm loses its most extreme
     participants, its SD shrinks for a reason that has nothing to do with the
     programme. The deposit carries per-arm n at baseline and post.

  D  SMALL-STUDY / REPORTING ASYMMETRY. Does lnVR correlate with its own standard
     error? Egger-type regression on the variability scale.

  E  INFLUENCE. Leave one study out, 71 times.

  F  EXTRACTION SENSITIVITY. Drop the rows where the review authors annotated an
     assumed n; drop cluster-randomised trials; drop trials at high risk of bias
     on 3+ RoB2 domains.

Output: out_break_tests.csv, out_simulation_floor.csv
"""
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "..", "tools"))
import statlib  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 20260902


def load():
    d = pd.read_csv(os.path.join(HERE, "out_arms.csv"))
    d["lnvr"], d["lnvr_v"] = statlib.lnvr(d.sd_mbp, d.n_mbp, d.sd_ctl, d.n_ctl)
    d["lncvr"], d["lncvr_v"] = statlib.lncvr(d.m_mbp, d.sd_mbp, d.n_mbp,
                                             d.m_ctl, d.sd_ctl, d.n_ctl)
    return d


def pool(d, label, col="lnvr", vcol="lnvr_v", B=2000, quiet=False):
    if len(d) < 3:
        return None
    r = statlib.re_meta(d[col].values, d[vcol].values, method="PM")
    cb = statlib.cluster_bootstrap_meta(d[col].values, d[vcol].values,
                                        d.study.values, B=B, seed=11)
    if not quiet:
        print("  %-52s k=%3d st=%3d  lnVR %+.4f  boot [%+.4f, %+.4f]  VR %.3f"
              % (label, r["k"], cb["n_clusters"], r["mu"], cb["ci"][0], cb["ci"][1],
                 np.exp(r["mu"])))
    return {"test": label, "k": r["k"], "studies": cb["n_clusters"], "lnvr": r["mu"],
            "lo": cb["ci"][0], "hi": cb["ci"][1], "vr": float(np.exp(r["mu"])),
            "tau": r["tau"], "I2": r["I2"]}


def main():
    d = load()
    post = d[(d.trange == "Postintervention") & (d.ctrl_cat == "passive")].copy()
    rows = [pool(post, "AS FOUND: post-intervention, passive control")]

    # ---------------- A: coupling decomposition ---------------------------
    print("\nA  MEAN-VARIANCE COUPLING, decomposed")
    key = ["study", "domain", "instrument", "outcome"]
    b = d[(d.trange == "Baseline") & (d.ctrl_cat == "passive")].set_index(key)
    p = d[(d.trange == "Postintervention") & (d.ctrl_cat == "passive")].set_index(key)
    b, p = b[~b.index.duplicated()], p[~p.index.duplicated()]
    j = b.join(p, lsuffix="_b", rsuffix="_p", how="inner")
    j = j[(j[["m_ctl_b", "m_ctl_p", "m_mbp_b", "m_mbp_p"]] > 0).all(axis=1)]
    dlm_c = np.log(j.m_ctl_p / j.m_ctl_b).values
    dls_c = np.log(j.sd_ctl_p / j.sd_ctl_b).values
    beta, alpha, r_, p_, se_b = stats.linregress(dlm_c, dls_c)
    print("  coupling measured in UNTREATED control arms: "
          "d log SD = %+.4f %+.4f * d log mean  (se %.4f, n = %d study x outcome)"
          % (alpha, beta, se_b, len(j)))
    dlm_rel = np.log(j.m_mbp_p / j.m_mbp_b).values - dlm_c   # treated minus control
    lnvr_post = j.lnvr_p.values
    predicted = beta * dlm_rel
    residual = lnvr_post - predicted
    print("  mean relative change in log(mean), treated vs control: %+.4f" % dlm_rel.mean())
    print("  lnVR predicted by a PURE LOCATION SHIFT under that coupling: %+.4f"
          % predicted.mean())
    print("  lnVR observed:                                             %+.4f"
          % lnvr_post.mean())
    print("  residual (compression not explained by the mean moving):   %+.4f"
          % residual.mean())
    uq = np.unique(j.index.get_level_values("study"))
    idx = {s: np.flatnonzero(j.index.get_level_values("study") == s) for s in uq}
    rng = np.random.default_rng(SEED)
    bs = [float(np.mean(residual[np.concatenate(
        [idx[s] for s in rng.choice(uq, len(uq), replace=True)])])) for _ in range(3000)]
    lo, hi = np.percentile(bs, [2.5, 97.5])
    print("     95%% cluster bootstrap [%+.4f, %+.4f] over %d studies" % (lo, hi, len(uq)))
    rows.append({"test": "A residual after measured coupling", "k": len(j),
                 "studies": len(uq), "lnvr": float(residual.mean()),
                 "lo": lo, "hi": hi, "vr": float(np.exp(residual.mean()))})
    print("  WHY lnCVR DISAGREES: lnCVR = lnVR - (relative change in log mean),")
    print("  i.e. it assumes the coupling slope is 1. The measured slope is %.2f," % beta)
    print("  so lnCVR subtracts about %.0f%% too much and biases the answer toward"
          % (100 * (1 - beta)))
    print("  zero, or past it. Predicted lnCVR under a pure location shift: %+.4f"
          % ((beta - 1) * dlm_rel.mean()))

    # ---------------- B: simulation with a known answer -------------------
    print("\nB  SIMULATION: every participant improves by EXACTLY the same amount")
    print("   (zero heterogeneity of treatment effect), on a scale with a floor at 0")
    sim = []
    rng = np.random.default_rng(SEED)
    for floor_pressure in (0.5, 1.0, 1.5, 2.0, 3.0, 4.23, 6.0):
        # baseline mean sits `floor_pressure` SDs above the floor
        for shift_sd in (0.0, 0.25, 0.5):
            ln = []
            for rep in range(600):
                n1 = n2 = int(rng.integers(20, 120))
                base = 10.0
                sd0 = base / floor_pressure
                c = np.clip(rng.normal(base, sd0, n2), 0, None)
                t = np.clip(rng.normal(base, sd0, n1) - shift_sd * sd0, 0, None)
                y, v = statlib.lnvr(t.std(ddof=1), n1, c.std(ddof=1), n2)
                ln.append(float(y))
            sim.append({"floor_sd_units": floor_pressure, "shift_sd": shift_sd,
                        "mean_lnvr": float(np.mean(ln)),
                        "vr": float(np.exp(np.mean(ln)))})
            print("   baseline mean %.1f SD above floor, shift %.2f SD -> "
                  "lnVR %+.4f (VR %.3f)"
                  % (floor_pressure, shift_sd, np.mean(ln), np.exp(np.mean(ln))))
    pd.DataFrame(sim).to_csv(os.path.join(HERE, "out_simulation_floor.csv"), index=False)
    obs_pressure = (post.m_mbp / post.sd_mbp).median()
    print("   OBSERVED in the corpus: the treated arm's mean sits a median of "
          "%.2f SDs\n   above zero, so read the row nearest that." % obs_pressure)

    # ---------------- C: differential attrition ---------------------------
    print("\nC  DIFFERENTIAL ATTRITION")
    jj = j.copy()
    jj["ret_mbp"] = jj.n_mbp_p / jj.n_mbp_b
    jj["ret_ctl"] = jj.n_ctl_p / jj.n_ctl_b
    jj["dret"] = np.log(jj.ret_mbp / jj.ret_ctl)
    print("   retention MBP median %.3f, control median %.3f; "
          "%d of %d pairs have identical n at both timepoints"
          % (jj.ret_mbp.median(), jj.ret_ctl.median(),
             int(((jj.n_mbp_p == jj.n_mbp_b) & (jj.n_ctl_p == jj.n_ctl_b)).sum()),
             len(jj)))
    ok = np.isfinite(jj.dret) & (jj.dret.abs() < 2)
    sl, ic, rr, pv, se = stats.linregress(jj.dret[ok], jj.lnvr_p[ok])
    print("   lnVR on log relative retention: slope %+.4f (se %.4f, p = %.3f, n = %d)"
          % (sl, se, pv, ok.sum()))
    print("   intercept (lnVR at EQUAL retention) = %+.4f" % ic)
    sub = jj[(jj.n_mbp_p == jj.n_mbp_b) & (jj.n_ctl_p == jj.n_ctl_b)].reset_index()
    sub = sub.rename(columns={"lnvr_p": "lnvr", "lnvr_v_p": "lnvr_v"})
    r = pool(sub, "C  trials with NO attrition recorded in either arm")
    if r:
        rows.append(r)

    # ---- floor-proximity moderator: assumption-free about where the floor is
    print("")
    print("   FLOOR-PROXIMITY MODERATOR: if a floor drives the compression, lnVR")
    print("   must be MORE negative where the treated mean sits closer to the")
    print("   scale minimum, i.e. at a smaller mean/SD ratio.")
    prox = (post.m_mbp / post.sd_mbp).values
    fin = np.isfinite(prox) & (prox < 30)
    sl, ic, rr, pv, se = stats.linregress(prox[fin], post.lnvr.values[fin])
    print("   lnVR = %+.4f %+.4f * (mean/SD)   (se %.4f, p = %.3f, n = %d)"
          % (ic, sl, se, pv, fin.sum()))
    print("   a floor artifact predicts a POSITIVE slope (compression fades as the")
    print("   mean moves away from the floor). Observed sign: %s"
          % ("POSITIVE - consistent with a floor" if sl > 0 else
             "NEGATIVE or flat - not what a floor predicts"))
    lowp = post[fin][prox[fin] <= np.median(prox[fin])]
    hip = post[fin][prox[fin] > np.median(prox[fin])]
    r1 = pool(lowp, "   closest half to the floor (mean/SD <= %.2f)" % np.median(prox[fin]))
    r2 = pool(hip, "   furthest half from the floor")
    for r_ in (r1, r2):
        if r_:
            rows.append(r_)

    # ---------------- D: small-study asymmetry ----------------------------
    print("\nD  SMALL-STUDY ASYMMETRY (Egger-type, on the lnVR scale)")
    se_v = np.sqrt(post.lnvr_v.values)
    sl, ic, rr, pv, sse = stats.linregress(se_v, post.lnvr.values)
    print("   lnVR = %+.4f %+.4f * SE   (se %.4f, p = %.3f)" % (ic, sl, sse, pv))
    print("   the intercept is the small-study-adjusted estimate: lnVR = %+.4f "
          "(VR %.3f)" % (ic, np.exp(ic)))
    rows.append({"test": "D  Egger intercept (small-study adjusted)", "k": len(post),
                 "studies": post.study.nunique(), "lnvr": ic,
                 "lo": ic - 1.96 * sse, "hi": ic + 1.96 * sse, "vr": float(np.exp(ic))})

    # ---------------- E: leave one study out ------------------------------
    print("\nE  LEAVE ONE STUDY OUT")
    base = statlib.re_meta(post.lnvr.values, post.lnvr_v.values, method="PM")["mu"]
    loo = []
    for s in post.study.unique():
        m = post.study != s
        loo.append((s, statlib.re_meta(post.lnvr[m].values, post.lnvr_v[m].values,
                                       method="PM")["mu"]))
    loo.sort(key=lambda t: t[1])
    print("   full %+.4f;  range over 71 leave-one-out fits [%+.4f, %+.4f]"
          % (base, loo[0][1], loo[-1][1]))
    print("   most influential (pulls the pooled value most toward zero when "
          "removed): %s -> %+.4f" % (loo[-1][0], loo[-1][1]))
    rows.append({"test": "E  worst-case leave-one-study-out", "k": len(post),
                 "studies": post.study.nunique(), "lnvr": loo[-1][1],
                 "lo": np.nan, "hi": np.nan, "vr": float(np.exp(loo[-1][1]))})

    # ---------------- F: extraction sensitivity ---------------------------
    print("\nF  EXTRACTION SENSITIVITY")
    rows.append(pool(post[post.parse_notes.isna()],
                     "F  drop rows with an assumed n"))
    rows.append(pool(post[post.design == "Randomized controlled trial"],
                     "F  drop cluster-randomised trials"))
    hi_rob = post[["d1", "d2", "d3", "d4", "d5"]].apply(
        lambda r: sum(str(x).strip().lower() == "high" for x in r), axis=1)
    rows.append(pool(post[hi_rob < 3], "F  drop trials high-risk on 3+ RoB2 domains"))
    rows.append(pool(post[post.USA.astype(str).str.strip().str.lower() == "no"],
                     "F  non-USA trials only"))
    rows.append(pool(post[post.dir_imp == "D"],
                     "F  symptom scales only (lower is better)"))
    rows.append(pool(post[post.dir_imp == "U"],
                     "F  positively-keyed scales only (higher is better)"))

    out = pd.DataFrame([r for r in rows if r])
    out.to_csv(os.path.join(HERE, "out_break_tests.csv"), index=False)
    print("\nwrote out_break_tests.csv, out_simulation_floor.csv")


if __name__ == "__main__":
    main()
