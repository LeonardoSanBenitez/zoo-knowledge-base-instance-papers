#!/usr/bin/env python3
"""v05 -- translate lnVR into something a person can act on, and test the
prediction that follows from it.

If a programme lowers the mean by SMD standard deviations AND multiplies the
standard deviation by VR, then under a location-scale reading the difference
between the arms at quantile tau is

    Q_tau(treated) - Q_tau(control) = SMD + (VR - 1) * z_tau     (in SD units)

so a VR below 1 means the people at the bad end of the distribution gain MORE
than the people at the good end. That is heterogeneity of treatment effect --
but CONVERGENT heterogeneity, which the variability-ratio literature has been
reading as "no heterogeneity" because it tests VR against 1 two-sided and finds
VR near 1 in drug trials.

THE PREDICTION, stated before it is tested. If the compression happens because
those who start worse improve more, then:

  P1  trials in SELECTED or INDICATED populations (recruited for being at higher
      risk, so more room to improve) should compress MORE than universal ones;
  P2  within a trial, a larger mean effect should come with more compression;
  P3  trials whose baseline sample is more severe, relative to other trials using
      the SAME instrument, should compress more.

Galante et al. report that MBPs targeted at higher-risk populations had larger
MEAN effects than universal ones. P1 is the variance analogue and they did not
test it.

Output: out_implied_quantiles.csv, out_moderators.csv
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
    flip = np.where(direction == "U", -1.0, 1.0)
    return g * flip, v


def main():
    d = pd.read_csv(os.path.join(HERE, "out_arms.csv"))
    d["lnvr"], d["lnvr_v"] = statlib.lnvr(d.sd_mbp, d.n_mbp, d.sd_ctl, d.n_ctl)
    d["g"], d["g_v"] = hedges_g(d.m_mbp, d.sd_mbp, d.n_mbp, d.m_ctl, d.sd_ctl,
                                d.n_ctl, d.dir_imp.values)
    post = d[(d.trange == "Postintervention") & (d.ctrl_cat == "passive")].copy()

    # ------------- implied quantile effects --------------------------------
    print("IMPLIED EFFECT AT EACH QUANTILE, passive-controlled, post-intervention")
    print("all four primary domains pooled and then each on its own\n")
    rows = []
    groups = [("ALL primary domains", post[post.domain.isin(
        ["Anxiety", "Depression", "Distress", "Mental wellbeing"])])]
    groups += [(dom, post[post.domain == dom])
               for dom in ["Distress", "Depression", "Anxiety", "Mental wellbeing"]]
    for label, sub in groups:
        if len(sub) < 5:
            continue
        gm = statlib.re_meta(sub.g.values, sub.g_v.values, method="PM")
        vm = statlib.re_meta(sub.lnvr.values, sub.lnvr_v.values, method="PM")
        gb = statlib.cluster_bootstrap_meta(sub.g.values, sub.g_v.values,
                                            sub.study.values, B=2000, seed=3)
        vb = statlib.cluster_bootstrap_meta(sub.lnvr.values, sub.lnvr_v.values,
                                            sub.study.values, B=2000, seed=3)
        SMD, VR = gm["mu"], np.exp(vm["mu"])
        print("%-22s SMD %+.3f [%+.3f, %+.3f]   VR %.3f [%.3f, %.3f]   "
              "(%d rows, %d studies)"
              % (label, SMD, gb["ci"][0], gb["ci"][1], VR,
                 np.exp(vb["ci"][0]), np.exp(vb["ci"][1]),
                 len(sub), sub.study.nunique()))
        line = []
        for tau in (0.10, 0.25, 0.50, 0.75, 0.90):
            z = stats.norm.ppf(tau)
            eff = SMD + (VR - 1) * z
            line.append("tau=%.2f: %+.3f" % (tau, eff))
            rows.append({"group": label, "tau": tau, "effect_sd_units": eff,
                         "SMD": SMD, "VR": VR})
        print("   effect in SD units by quantile of the OUTCOME (higher tau = worse "
              "on symptom scales):\n     " + "   ".join(line))
        z9, z1 = stats.norm.ppf(0.9), stats.norm.ppf(0.1)
        e9, e1 = SMD + (VR - 1) * z9, SMD + (VR - 1) * z1
        print("   worst decile gains %.2f SD, best decile gains %.2f SD -> "
              "ratio %.2f\n" % (abs(e9), abs(e1), abs(e9 / e1)))
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "out_implied_quantiles.csv"),
                              index=False)

    # ------------- P1: targeted vs universal -------------------------------
    print("P1  TARGETED vs UNIVERSAL populations")
    post["ptype"] = post.participanttype.astype(str).str.extract(
        r"(universal|selective|indicated)", expand=False)
    mods = []
    for lev, sub in post.groupby("ptype"):
        if len(sub) < 5:
            continue
        vm = statlib.re_meta(sub.lnvr.values, sub.lnvr_v.values, method="PM")
        vb = statlib.cluster_bootstrap_meta(sub.lnvr.values, sub.lnvr_v.values,
                                            sub.study.values, B=2000, seed=3)
        gm = statlib.re_meta(sub.g.values, sub.g_v.values, method="PM")
        print("  %-11s lnVR %+.4f [%+.4f, %+.4f]  VR %.3f   (SMD %+.3f)  "
              "%d rows, %d studies"
              % (lev, vm["mu"], vb["ci"][0], vb["ci"][1], np.exp(vm["mu"]),
                 gm["mu"], len(sub), sub.study.nunique()))
        mods.append({"moderator": "participant type", "level": lev,
                     "lnvr": vm["mu"], "lo": vb["ci"][0], "hi": vb["ci"][1],
                     "smd": gm["mu"], "k": len(sub), "studies": sub.study.nunique()})
    tgt = post[post.ptype.isin(["selective", "indicated"])]
    uni = post[post.ptype == "universal"]
    if len(tgt) > 4 and len(uni) > 4:
        a = statlib.re_meta(tgt.lnvr.values, tgt.lnvr_v.values, method="PM")
        b = statlib.re_meta(uni.lnvr.values, uni.lnvr_v.values, method="PM")
        se = np.hypot(a["se"], b["se"])
        print("  targeted minus universal: %+.4f (se %.4f, z = %.2f) -- "
              "P1 predicts NEGATIVE" % (a["mu"] - b["mu"], se, (a["mu"] - b["mu"]) / se))

    # ------------- P2: does a bigger mean effect come with more compression?
    print("\nP2  WITHIN-CORPUS relation between the mean effect and the compression")
    ok = np.isfinite(post.g) & np.isfinite(post.lnvr) & (post.g.abs() < 4)
    sl, ic, rr, pv, se = stats.linregress(post.g[ok], post.lnvr[ok])
    print("  lnVR = %+.4f %+.4f * SMD   (se %.4f, p = %.2g, r = %+.3f, n = %d)"
          % (ic, sl, se, pv, rr, ok.sum()))
    print("  a POSITIVE slope means: the more the mean improves (more negative SMD),")
    print("  the more the SD shrinks. Observed slope sign: %s"
          % ("POSITIVE - consistent with P2" if sl > 0 else "NEGATIVE - against P2"))
    print("  intercept: lnVR when the mean effect is exactly zero = %+.4f "
          "[%+.4f, %+.4f]" % (ic, ic - 1.96 * se, ic + 1.96 * se))
    print("  ^ this is the compression that is NOT accompanied by any mean change.")
    mods.append({"moderator": "SMD (within-corpus slope)", "level": "slope",
                 "lnvr": sl, "lo": sl - 1.96 * se, "hi": sl + 1.96 * se,
                 "smd": None, "k": int(ok.sum()), "studies": post.study.nunique()})

    # ------------- P3: baseline severity, standardised within instrument ---
    print("\nP3  BASELINE SEVERITY relative to other trials using the SAME instrument")
    base = d[(d.trange == "Baseline")].copy()
    base["pooled_m"] = (base.m_mbp * base.n_mbp + base.m_ctl * base.n_ctl) / \
                       (base.n_mbp + base.n_ctl)
    g = base.groupby("instrument")["pooled_m"]
    base["sev_z"] = (base.pooled_m - g.transform("mean")) / g.transform("std")
    # sign so that positive always means WORSE off
    base["sev_z"] = np.where(base.dir_imp == "U", -base.sev_z, base.sev_z)
    key = ["study", "instrument", "outcome"]
    sev = base.dropna(subset=["sev_z"]).drop_duplicates(key).set_index(key)["sev_z"]
    pp = post.set_index(key)
    pp = pp[~pp.index.duplicated()]
    j = pp.join(sev.rename("sev_z"), how="inner").dropna(subset=["sev_z"])
    print("  %d post-intervention rows matched to a within-instrument baseline "
          "severity z" % len(j))
    sl, ic, rr, pv, se = stats.linregress(j.sev_z, j.lnvr)
    print("  lnVR = %+.4f %+.4f * baseline severity z   (se %.4f, p = %.3f, n = %d)"
          % (ic, sl, se, pv, len(j)))
    print("  P3 predicts a NEGATIVE slope (sicker samples compress more). "
          "Observed: %s" % ("NEGATIVE" if sl < 0 else "POSITIVE - against P3"))
    for lab, m in (("more severe than average for the instrument", j.sev_z > 0),
                   ("less severe than average", j.sev_z <= 0)):
        s = j[m]
        vm = statlib.re_meta(s.lnvr.values, s.lnvr_v.values, method="PM")
        vb = statlib.cluster_bootstrap_meta(
            s.lnvr.values, s.lnvr_v.values,
            s.index.get_level_values("study").values, B=2000, seed=3)
        print("    %-42s lnVR %+.4f [%+.4f, %+.4f]  VR %.3f  (k=%d)"
              % (lab, vm["mu"], vb["ci"][0], vb["ci"][1], np.exp(vm["mu"]), len(s)))
        mods.append({"moderator": "baseline severity", "level": lab,
                     "lnvr": vm["mu"], "lo": vb["ci"][0], "hi": vb["ci"][1],
                     "smd": None, "k": len(s), "studies": None})

    pd.DataFrame(mods).to_csv(os.path.join(HERE, "out_moderators.csv"), index=False)
    print("\nwrote out_implied_quantiles.csv, out_moderators.csv")


if __name__ == "__main__":
    main()
