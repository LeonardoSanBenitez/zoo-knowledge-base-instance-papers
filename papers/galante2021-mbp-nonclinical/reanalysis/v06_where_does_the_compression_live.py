#!/usr/bin/env python3
"""v06 -- the compression is real; the mechanism I proposed for it is not.

v05 stated three predictions in advance and two failed outright:
  P1  targeted populations should compress more than universal ones -- NO
      (targeted minus universal = -0.005, z = -0.12);
  P3  more severe baseline samples should compress more -- NO (slope -0.003,
      p = 0.92);
  P2  larger mean effects should come with more compression -- weakly, slope
      +0.058 (se 0.037, p = 0.13), and the intercept says there is compression of
      -0.075 [-0.149, -0.001] even where the mean does not move at all.

So "the worst-off improve most, which narrows the distribution" does not survive
its own predictions. A rival mechanism does not need it:

  RESPONSE-STYLE HOMOGENISATION.  Mindfulness programmes are taught in groups,
  over weeks, with a shared vocabulary for describing inner states. If that
  changes how participants USE a rating scale -- less extreme responding, more
  convergent interpretation of the items -- the treated arm's SD falls on every
  questionnaire regardless of population, severity or how much the mean moved.

The two mechanisms make opposite predictions about WHERE the variance in lnVR
lives, and this script tests that:

  a target-specific treatment effect  -> compression varies BETWEEN OUTCOMES
                                         within a trial, and tracks the outcome's
                                         mean effect;
  a response-style / delivery effect  -> compression is a property OF THE TRIAL:
                                         all outcomes in a trial compress
                                         together, and it does not track the
                                         mean effect.

Three tests:
  1  two-level variance decomposition of lnVR: between-trial vs within-trial;
  2  domain-level correlation between the pooled SMD and the pooled lnVR;
  3  the trials whose mean effect is essentially zero -- do they still compress?

Output: out_variance_components.csv, out_domain_level.csv
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


def hedges_g(m1, sd1, n1, m2, sd2, n2, direction):
    sp = np.sqrt(((n1 - 1) * sd1 ** 2 + (n2 - 1) * sd2 ** 2) / (n1 + n2 - 2))
    J = 1 - 3.0 / (4 * (n1 + n2) - 9)
    g = J * (m1 - m2) / sp
    v = ((n1 + n2) / (n1 * n2) + g ** 2 / (2 * (n1 + n2 - 2))) * J ** 2
    return g * np.where(direction == "U", -1.0, 1.0), v


def three_level(y, v, cluster, iters=400):
    """Method-of-moments two-variance-component fit:
       y_ij = mu + u_i + e_ij + sampling,  Var = tau2_between + tau2_within + v_ij.
    Simple iterative REML-like scheme; validated below against simulated data."""
    y, v = np.asarray(y, float), np.asarray(v, float)
    cl = np.asarray(cluster)
    uq = np.unique(cl)
    idx = [np.flatnonzero(cl == c) for c in uq]
    t_b, t_w = 0.01, 0.01
    mu = y.mean()
    for _ in range(iters):
        w = 1.0 / (v + t_w)
        # cluster means and their variances
        cm, cv = [], []
        for ii in idx:
            ww = w[ii]
            cm.append((ww * y[ii]).sum() / ww.sum())
            cv.append(1.0 / ww.sum())
        cm, cv = np.array(cm), np.array(cv)
        W = 1.0 / (cv + t_b)
        mu = (W * cm).sum() / W.sum()
        Qb = (W * (cm - mu) ** 2).sum()
        Cb = W.sum() - (W ** 2).sum() / W.sum()
        t_b_new = max(0.0, t_b + (Qb - (len(uq) - 1)) / max(Cb, 1e-9))
        # within: residuals around the cluster mean
        num, den = 0.0, 0.0
        for ii, m_ in zip(idx, cm):
            if len(ii) < 2:
                continue
            ww = 1.0 / (v[ii] + t_w)
            num += (ww * (y[ii] - m_) ** 2).sum() - (len(ii) - 1)
            den += ww.sum() - (ww ** 2).sum() / ww.sum()
        t_w_new = max(0.0, t_w + num / max(den, 1e-9)) if den > 0 else t_w
        if abs(t_b_new - t_b) < 1e-10 and abs(t_w_new - t_w) < 1e-10:
            t_b, t_w = t_b_new, t_w_new
            break
        t_b, t_w = 0.5 * t_b + 0.5 * t_b_new, 0.5 * t_w + 0.5 * t_w_new
    return {"mu": mu, "tau2_between": t_b, "tau2_within": t_w,
            "se_mu": float(np.sqrt(1.0 / W.sum()))}


def selftest():
    print("0  SELF-TEST of the variance-component fitter on data with the answer known")
    rng = np.random.default_rng(1)
    ok = True
    for tb, tw in ((0.04, 0.01), (0.01, 0.04), (0.0, 0.03), (0.03, 0.0)):
        bs, ws = [], []
        for rep in range(40):
            y, v, cl = [], [], []
            for s in range(70):
                u = rng.normal(0, np.sqrt(tb))
                for j in range(rng.integers(1, 6)):
                    vv = rng.uniform(0.005, 0.03)
                    y.append(-0.1 + u + rng.normal(0, np.sqrt(tw)) + rng.normal(0, np.sqrt(vv)))
                    v.append(vv)
                    cl.append(s)
            r = three_level(y, v, cl)
            bs.append(r["tau2_between"])
            ws.append(r["tau2_within"])
        good = abs(np.mean(bs) - tb) < 0.012 and abs(np.mean(ws) - tw) < 0.012
        ok &= good
        print("   true (between %.3f, within %.3f) -> estimated (%.4f, %.4f)  %s"
              % (tb, tw, np.mean(bs), np.mean(ws), "ok" if good else "OFF"))
    if not ok:
        print("   ^ the fitter is biased on at least one configuration. Read the "
              "numbers below as ordinal, not exact.")
    return ok


def main():
    fitter_ok = selftest()
    d = pd.read_csv(os.path.join(HERE, "out_arms.csv"))
    d["lnvr"], d["lnvr_v"] = statlib.lnvr(d.sd_mbp, d.n_mbp, d.sd_ctl, d.n_ctl)
    d["g"], d["g_v"] = hedges_g(d.m_mbp, d.sd_mbp, d.n_mbp, d.m_ctl, d.sd_ctl,
                                d.n_ctl, d.dir_imp.values)
    post = d[(d.trange == "Postintervention") & (d.ctrl_cat == "passive")].copy()
    multi = post.groupby("study").filter(lambda s: len(s) >= 2)

    print("\n1  WHERE DOES THE VARIANCE IN lnVR LIVE?")
    print("   %d rows in %d trials; %d rows in the %d trials with >=2 outcomes"
          % (len(post), post.study.nunique(), len(multi), multi.study.nunique()))
    rows = []
    for lab, col, vcol in (("lnVR", "lnvr", "lnvr_v"), ("SMD", "g", "g_v")):
        r = three_level(multi[col].values, multi[vcol].values, multi.study.values)
        tot = r["tau2_between"] + r["tau2_within"]
        share = r["tau2_between"] / tot if tot > 0 else float("nan")
        print("   %-5s mu %+.4f (se %.4f)   tau2 between-trial %.5f, within-trial "
              "%.5f   -> %.0f%% of the true heterogeneity is BETWEEN trials"
              % (lab, r["mu"], r["se_mu"], r["tau2_between"], r["tau2_within"],
                 100 * share))
        rows.append({"quantity": lab, "mu": r["mu"], "se": r["se_mu"],
                     "tau2_between": r["tau2_between"],
                     "tau2_within": r["tau2_within"], "between_share": share,
                     "k": len(multi), "studies": multi.study.nunique()})
    print("   READING: a target-specific treatment effect should put much of the")
    print("   heterogeneity WITHIN trials (different outcomes respond differently).")
    print("   A response-style or delivery effect should put it BETWEEN trials.")
    print("   The SMD row is the benchmark -- the mean effect is unquestionably")
    print("   outcome-specific, so its within-trial share is what 'outcome-specific'")
    print("   looks like in this corpus.")
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "out_variance_components.csv"),
                              index=False)

    print("\n2  DOMAIN-LEVEL: does compression track the mean effect across domains?")
    dom = []
    for name, sub in post.groupby("domain"):
        if len(sub) < 6:
            continue
        gm = statlib.re_meta(sub.g.values, sub.g_v.values, method="PM")
        vm = statlib.re_meta(sub.lnvr.values, sub.lnvr_v.values, method="PM")
        dom.append({"domain": name, "k": len(sub), "studies": sub.study.nunique(),
                    "smd": gm["mu"], "smd_se": gm["se"],
                    "lnvr": vm["mu"], "lnvr_se": vm["se"], "vr": np.exp(vm["mu"])})
    dm = pd.DataFrame(dom).sort_values("lnvr")
    print(dm.to_string(index=False, float_format=lambda v: "%.4f" % v))
    r_, p_ = stats.pearsonr(dm.smd, dm.lnvr)
    sl, ic, rr, pv, se = stats.linregress(dm.smd, dm.lnvr)
    print("   across %d domains: r = %+.3f (p = %.3f);  lnVR = %+.4f %+.4f * SMD"
          % (len(dm), r_, p_, ic, sl))
    print("   the intercept is the compression predicted for a domain with NO mean")
    print("   effect: %+.4f  (VR %.3f)" % (ic, np.exp(ic)))
    dm.to_csv(os.path.join(HERE, "out_domain_level.csv"), index=False)

    print("\n3  THE TRIALS WHERE THE MEAN BARELY MOVED")
    for lo, hi, lab in ((-0.15, 0.15, "|SMD| < 0.15  (no meaningful mean effect)"),
                        (-0.35, -0.15, "SMD in [-0.35, -0.15]  (small)"),
                        (-10, -0.35, "SMD < -0.35  (moderate or large)")):
        s = post[(post.g > lo) & (post.g <= hi)] if lo > -5 else post[post.g <= hi]
        if len(s) < 5:
            continue
        vm = statlib.re_meta(s.lnvr.values, s.lnvr_v.values, method="PM")
        vb = statlib.cluster_bootstrap_meta(s.lnvr.values, s.lnvr_v.values,
                                            s.study.values, B=2500, seed=7)
        print("   %-42s lnVR %+.4f [%+.4f, %+.4f]  VR %.3f  (k=%d, %d studies)"
              % (lab, vm["mu"], vb["ci"][0], vb["ci"][1], np.exp(vm["mu"]),
                 len(s), s.study.nunique()))

    print("\n4  IS THE COMPRESSION THERE ON OUTCOMES THE PROGRAMME DOES NOT TARGET?")
    distal = ["Cognitive functioning", "Real life functioning",
              "Relationship with self", "Psychosomatic outcomes"]
    for lab, m in (("proximal (anxiety/depression/distress/wellbeing/mindfulness)",
                    ~post.domain.isin(distal)),
                   ("distal (cognition, functioning, self, psychosomatic)",
                    post.domain.isin(distal))):
        s = post[m]
        vm = statlib.re_meta(s.lnvr.values, s.lnvr_v.values, method="PM")
        vb = statlib.cluster_bootstrap_meta(s.lnvr.values, s.lnvr_v.values,
                                            s.study.values, B=2500, seed=7)
        gm = statlib.re_meta(s.g.values, s.g_v.values, method="PM")
        print("   %-58s lnVR %+.4f [%+.4f, %+.4f]  (SMD %+.3f)  k=%d"
              % (lab, vm["mu"], vb["ci"][0], vb["ci"][1], gm["mu"], len(s)))

    if not fitter_ok:
        print("\n(the variance-component fitter failed part of its self-test; "
              "test 1 is ordinal only)")
    print("\nwrote out_variance_components.csv, out_domain_level.csv")


if __name__ == "__main__":
    main()
