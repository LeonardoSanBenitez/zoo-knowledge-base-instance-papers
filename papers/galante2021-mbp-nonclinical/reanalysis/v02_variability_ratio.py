#!/usr/bin/env python3
"""v02 -- does a mindfulness-based programme change the VARIANCE of the outcome,
or only its mean?

Three things happen here, in this order, and the order is the method:

  STEP 1  REPRODUCTION CHECK. Pool the standardised mean differences from my own
          extraction and compare with the four headline SMDs Galante et al.
          report. If those do not land close, the extraction is wrong and nothing
          after this point means anything. (They used multivariate meta-analysis
          with within-study covariances and I use univariate random effects with a
          cluster bootstrap, so agreement should be close, not exact.)

  STEP 2  NEGATIVE CONTROL. Pool lnVR at BASELINE. Randomisation makes the two
          arms draws from the same distribution, so the answer must be zero. If it
          is not, the post-intervention number is uninterpretable and the right
          thing to do is stop.

  STEP 3  THE QUESTION. Pool lnVR post-intervention and at 1-6 months, by control
          category and by outcome domain.

Interpretation, stated before the numbers are seen so it cannot be adjusted to
them:
  VR > 1  the treated arm is MORE spread out -> some people respond much more than
          others -> individual differences in response exist and personalising has
          something to work with.
  VR = 1  the programme shifts everyone by about the same amount -> the average
          effect IS the individual effect -> nothing to personalise.
  VR < 1  the programme compresses -> or the scale has a floor and the mean moved
          toward it, which is why STEP 4 exists.

  STEP 4  THE CONFOUND. On a bounded questionnaire, lowering the mean lowers the
          SD by itself. The usual fix is lnCVR, which divides by the mean and so
          assumes SD is proportional to the mean. Rather than assume that, this
          script MEASURES the mean-variance coupling in this very corpus, from the
          control arms' own pre-to-post change (untreated, so any coupling there is
          the instrument's, not the treatment's), and uses it to predict the lnVR a
          pure location shift would produce.

Output: out_vr.csv, out_smd_check.csv, out_coupling.csv
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
B = int(os.environ.get("NBOOT", 4000))


def hedges_g(m1, sd1, n1, m2, sd2, n2, direction):
    """SMD with Hedges' small-sample correction, signed so that NEGATIVE always
    means the mindfulness arm is better (the review's convention for D-scales)."""
    sp = np.sqrt(((n1 - 1) * sd1 ** 2 + (n2 - 1) * sd2 ** 2) / (n1 + n2 - 2))
    d = (m1 - m2) / sp
    J = 1 - 3.0 / (4 * (n1 + n2) - 9)
    g = J * d
    v = (n1 + n2) / (n1 * n2) + g ** 2 / (2 * (n1 + n2 - 2))
    # 'U' = higher is better; flip so that negative = MBP better on every scale
    flip = np.where(direction == "U", -1.0, 1.0)
    return g * flip, v * J ** 2


def pooled(y, v, cluster, label, transform=None, B=B):
    r = statlib.re_meta(y, v, method="PM")
    cb = statlib.cluster_bootstrap_meta(y, v, cluster, B=B, seed=11)
    f = transform or (lambda x: x)
    line = ("  %-42s k=%3d studies=%3d   %7.4f  [%7.4f, %7.4f] RE   "
            "[%7.4f, %7.4f] cluster-boot   tau=%.3f  I2=%s"
            % (label, r["k"], cb["n_clusters"], f(r["mu"]),
               f(r["ci"][0]), f(r["ci"][1]), f(cb["ci"][0]), f(cb["ci"][1]),
               r["tau"], ("%.0f%%" % (100 * r["I2"])) if r["I2"] is not None else "n/a"))
    print(line)
    return {"label": label, "k": r["k"], "studies": cb["n_clusters"],
            "mu": r["mu"], "ci_lo": r["ci"][0], "ci_hi": r["ci"][1],
            "boot_lo": cb["ci"][0], "boot_hi": cb["ci"][1], "boot_p": cb["p"],
            "tau": r["tau"], "I2": r["I2"], "p_re": r["p"],
            "exp_mu": np.exp(r["mu"]),
            "exp_boot_lo": np.exp(cb["ci"][0]), "exp_boot_hi": np.exp(cb["ci"][1])}


def main():
    d = pd.read_csv(os.path.join(HERE, "out_arms.csv"))
    d["lnvr"], d["lnvr_v"] = statlib.lnvr(d.sd_mbp, d.n_mbp, d.sd_ctl, d.n_ctl)
    ok_cvr = (d.m_mbp > 0) & (d.m_ctl > 0)
    d["lncvr"], d["lncvr_v"] = np.nan, np.nan
    y, v = statlib.lncvr(d.loc[ok_cvr, "m_mbp"], d.loc[ok_cvr, "sd_mbp"],
                         d.loc[ok_cvr, "n_mbp"], d.loc[ok_cvr, "m_ctl"],
                         d.loc[ok_cvr, "sd_ctl"], d.loc[ok_cvr, "n_ctl"])
    d.loc[ok_cvr, "lncvr"] = y
    d.loc[ok_cvr, "lncvr_v"] = v
    d["g"], d["g_v"] = hedges_g(d.m_mbp, d.sd_mbp, d.n_mbp,
                                d.m_ctl, d.sd_ctl, d.n_ctl, d.dir_imp.values)
    print("%d rows; %d have a nonpositive mean so lnCVR is undefined for them"
          % (len(d), (~ok_cvr).sum()))

    # ---------------- STEP 1: reproduction check --------------------------
    print("\nSTEP 1 -- REPRODUCTION CHECK against the four headline SMDs")
    print("  Galante et al., MBP vs PASSIVE control, 1-6 months post-programme:")
    print("  anxiety -0.56, depression -0.53, distress -0.45, well-being +0.33")
    print("  (their sign convention: negative favours MBP on symptom scales,")
    print("   positive favours MBP on well-being. Mine is negative-favours-MBP")
    print("   throughout, so their +0.33 is my -0.33.)")
    paper = {"Anxiety": -0.56, "Depression": -0.53, "Distress": -0.45,
             "Mental wellbeing": -0.33}
    chk = []
    for dom, want in paper.items():
        m = ((d.domain == dom) & (d.ctrl_cat == "passive") & (d.trange == "1-6months"))
        if m.sum() < 2:
            print("  %-18s only %d row(s) -- not poolable" % (dom, m.sum()))
            continue
        r = statlib.re_meta(d.loc[m, "g"], d.loc[m, "g_v"], method="PM")
        cb = statlib.cluster_bootstrap_meta(d.loc[m, "g"], d.loc[m, "g_v"],
                                            d.loc[m, "study"], B=1500, seed=5)
        print("  %-18s mine %+.3f [%+.3f, %+.3f]  paper %+.3f   diff %+.3f   "
              "(k=%d rows, %d studies)"
              % (dom, r["mu"], cb["ci"][0], cb["ci"][1], want, r["mu"] - want,
                 r["k"], cb["n_clusters"]))
        chk.append({"domain": dom, "mine": r["mu"], "paper": want,
                    "diff": r["mu"] - want, "k": r["k"],
                    "studies": cb["n_clusters"], "lo": cb["ci"][0], "hi": cb["ci"][1]})
    pd.DataFrame(chk).to_csv(os.path.join(HERE, "out_smd_check.csv"), index=False)

    rows = []
    # ---------------- STEP 2: negative control ----------------------------
    print("\nSTEP 2 -- NEGATIVE CONTROL: lnVR at BASELINE, where it must be 0")
    print("  %-42s %-24s %-9s %-25s %-25s"
          % ("", "", "", "", ""))
    for cc in ["passive", "active-nonspecific", "active-specific", "ALL"]:
        m = (d.trange == "Baseline") & ((d.ctrl_cat == cc) if cc != "ALL" else True)
        if m.sum() < 3:
            continue
        r = pooled(d.loc[m, "lnvr"].values, d.loc[m, "lnvr_v"].values,
                   d.loc[m, "study"].values, "baseline lnVR, control = %s" % cc)
        r["step"] = "negative-control"
        rows.append(r)

    # ---------------- STEP 3: the question --------------------------------
    print("\nSTEP 3 -- lnVR AFTER the programme  (exp(mu) = VR is in out_vr.csv)")
    for tp in ["Postintervention", "1-6months"]:
        for cc in ["passive", "active-nonspecific", "active-specific", "ALL"]:
            m = (d.trange == tp) & ((d.ctrl_cat == cc) if cc != "ALL" else True)
            if m.sum() < 3:
                continue
            r = pooled(d.loc[m, "lnvr"].values, d.loc[m, "lnvr_v"].values,
                       d.loc[m, "study"].values, "%s lnVR, control = %s" % (tp, cc))
            r["step"] = "main"
            rows.append(r)

    print("\n  by outcome domain, post-intervention, passive controls only")
    for dom in d.domain.value_counts().index:
        m = (d.trange == "Postintervention") & (d.ctrl_cat == "passive") & (d.domain == dom)
        if m.sum() < 4:
            continue
        r = pooled(d.loc[m, "lnvr"].values, d.loc[m, "lnvr_v"].values,
                   d.loc[m, "study"].values, "  domain = %s" % dom, B=2000)
        r["step"] = "by-domain"
        rows.append(r)

    print("\n  lnCVR (divides out the mean; assumes the scale has a real zero)")
    for tp in ["Baseline", "Postintervention"]:
        m = (d.trange == tp) & (d.ctrl_cat == "passive") & d.lncvr.notna()
        r = pooled(d.loc[m, "lncvr"].values, d.loc[m, "lncvr_v"].values,
                   d.loc[m, "study"].values, "%s lnCVR, passive" % tp, B=2000)
        r["step"] = "cvr"
        rows.append(r)

    pd.DataFrame(rows).to_csv(os.path.join(HERE, "out_vr.csv"), index=False)

    # ---------------- STEP 4: the mean-variance coupling ------------------
    print("\nSTEP 4 -- MEASURE the mean-variance coupling instead of assuming it")
    print("  Within each study x outcome, the CONTROL arm has a baseline and a")
    print("  post-intervention mean and SD. It received no programme, so the")
    print("  relation between its change in log(mean) and its change in log(SD)")
    print("  is a property of the instrument and the population, not of MBPs.")
    key = ["study", "domain", "instrument", "outcome", "ctrl_cat"]
    b = d[d.trange == "Baseline"].set_index(key)
    p = d[d.trange == "Postintervention"].set_index(key)
    b = b[~b.index.duplicated()]
    p = p[~p.index.duplicated()]
    j = b.join(p, lsuffix="_b", rsuffix="_p", how="inner")
    j = j[(j.m_ctl_b > 0) & (j.m_ctl_p > 0) & (j.m_mbp_b > 0) & (j.m_mbp_p > 0)]
    print("  %d study x outcome pairs matched at both timepoints" % len(j))
    dlm_c = np.log(j.m_ctl_p / j.m_ctl_b)
    dls_c = np.log(j.sd_ctl_p / j.sd_ctl_b)
    dlm_t = np.log(j.m_mbp_p / j.m_mbp_b)
    dls_t = np.log(j.sd_mbp_p / j.sd_mbp_b)
    sl, ic, rr, pv, se = stats.linregress(dlm_c, dls_c)
    print("  CONTROL arms:  d log(SD) = %+.4f %+.4f * d log(mean)   "
          "(se %.4f, p = %.2g, r = %.3f, n = %d)"
          % (ic, sl, se, pv, rr, len(j)))
    pred = ic + sl * dlm_t
    resid = dls_t - pred
    tsl, tic, trr, tpv, tse = stats.linregress(dlm_t, dls_t)
    print("  TREATED arms:  d log(SD) = %+.4f %+.4f * d log(mean)   (se %.4f, p = %.2g)"
          % (tic, tsl, tse, tpv))
    print("  slope difference treated - control = %+.4f (se %.4f, z = %.2f)"
          % (tsl - sl, np.hypot(tse, se), (tsl - sl) / np.hypot(tse, se)))
    # cluster bootstrap of the residual mean, over studies
    studies = j.index.get_level_values("study").values
    uq = np.unique(studies)
    rng = np.random.default_rng(23)
    idx = {s: np.flatnonzero(studies == s) for s in uq}
    bs = []
    for _ in range(2000):
        sel = np.concatenate([idx[s] for s in rng.choice(uq, len(uq), replace=True)])
        bs.append(float(np.mean(resid.values[sel])))
    lo, hi = np.percentile(bs, [2.5, 97.5])
    print("  MEAN RESIDUAL for the treated arms, i.e. the change in SD NOT")
    print("  explained by the coupling and their own change in mean:")
    print("      %+.4f  95%% cluster-bootstrap CI [%+.4f, %+.4f]  (%d studies)"
          % (resid.mean(), lo, hi, len(uq)))
    pd.DataFrame({"dlogmean_ctl": dlm_c, "dlogsd_ctl": dls_c,
                  "dlogmean_mbp": dlm_t, "dlogsd_mbp": dls_t,
                  "predicted_dlogsd_mbp": pred, "residual": resid}).to_csv(
        os.path.join(HERE, "out_coupling.csv"), index=True)
    print("\nwrote out_vr.csv, out_smd_check.csv, out_coupling.csv")


if __name__ == "__main__":
    main()
