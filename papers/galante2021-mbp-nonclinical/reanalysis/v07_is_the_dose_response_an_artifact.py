#!/usr/bin/env python3
"""v07 -- the dose-response in v06 test 3 may be an artifact of the estimator, and
this script decides.

v06 found a clean monotone pattern, stratifying outcomes by their observed
standardised mean difference:

    |SMD| < 0.15          lnVR +0.013 [-0.057, +0.096]   VR 1.013
    SMD in [-0.35,-0.15]  lnVR -0.049 [-0.112, +0.013]   VR 0.952
    SMD < -0.35           lnVR -0.162 [-0.222, -0.106]   VR 0.851

read as "where the programme moved the mean it also narrowed the distribution,
and where it did not, it did not". But at the DOMAIN level the same corpus shows
no relation at all between the pooled SMD and the pooled lnVR (r = -0.12,
p = 0.75), and "relationship with self" has the largest mean effect (-0.75) with
almost no compression (-0.031).

Those two facts are in tension, and there is a mechanism that produces exactly
this tension without any real dose-response:

    g = (m1 - m2) / s_pooled       and       lnVR = log(s1 / s2)

share the treated arm's sample SD. A chance-high s1 makes lnVR larger and |g|
smaller, simultaneously. So SELECTING rows on their observed |g| selects on
sampling error in s1, and manufactures a gradient in lnVR even when the true VR
is exactly 1 in every row. Pooling to the domain level averages that noise away,
which is why the domain-level relation could vanish.

THE TEST. Simulate rows with the corpus's own n and true-SMD distribution, set
the true VR to a KNOWN constant, run v06 test 3's stratification, and read off
what it reports. Twice: with true VR = 1.00 (is the gradient manufactured?) and
with true VR = 0.90 (is the observed gradient steeper than the truth?).

Output: out_dose_response_check.csv
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "..", "tools"))
import statlib  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
STRATA = [(-0.15, 0.15, "|SMD| < 0.15"),
          (-0.35, -0.15, "SMD in [-0.35, -0.15]"),
          (-99.0, -0.35, "SMD < -0.35")]
OBSERVED = {"|SMD| < 0.15": 0.0133, "SMD in [-0.35, -0.15]": -0.0488,
            "SMD < -0.35": -0.1615}


def simulate(n1s, n2s, true_smds, true_lnvr, rng):
    """Draw one synthetic corpus with the given per-row n and true SMD."""
    g, lnv = np.empty(len(n1s)), np.empty(len(n1s))
    for i, (n1, n2, dtrue) in enumerate(zip(n1s, n2s, true_smds)):
        sd_t = np.exp(true_lnvr)
        x1 = rng.normal(-dtrue, sd_t, n1)      # treated; negative = improvement
        x2 = rng.normal(0.0, 1.0, n2)
        s1, s2 = x1.std(ddof=1), x2.std(ddof=1)
        sp = np.sqrt(((n1 - 1) * s1 ** 2 + (n2 - 1) * s2 ** 2) / (n1 + n2 - 2))
        J = 1 - 3.0 / (4 * (n1 + n2) - 9)
        g[i] = J * (x1.mean() - x2.mean()) / sp
        y, _ = statlib.lnvr(s1, n1, s2, n2)
        lnv[i] = y
    return g, lnv


def main():
    d = pd.read_csv(os.path.join(HERE, "out_arms.csv"))
    d["lnvr"], d["lnvr_v"] = statlib.lnvr(d.sd_mbp, d.n_mbp, d.sd_ctl, d.n_ctl)
    post = d[(d.trange == "Postintervention") & (d.ctrl_cat == "passive")].copy()
    n1s = post.n_mbp.values.astype(int)
    n2s = post.n_ctl.values.astype(int)
    print("corpus: %d rows, arm n median %d / %d, quartiles %s"
          % (len(post), int(np.median(n1s)), int(np.median(n2s)),
             np.percentile(np.r_[n1s, n2s], [25, 75]).round(0)))

    # true SMDs: the corpus's own random-effects mean and heterogeneity, so the
    # simulated corpus has the same spread of real effects as the real one.
    def hg(m1, sd1, na, m2, sd2, nb, direc):
        sp = np.sqrt(((na - 1) * sd1 ** 2 + (nb - 1) * sd2 ** 2) / (na + nb - 2))
        J = 1 - 3.0 / (4 * (na + nb) - 9)
        gg = J * (m1 - m2) / sp
        vv = ((na + nb) / (na * nb) + gg ** 2 / (2 * (na + nb - 2))) * J ** 2
        return gg * np.where(direc == "U", -1.0, 1.0), vv

    post["g"], post["g_v"] = hg(post.m_mbp, post.sd_mbp, post.n_mbp,
                                post.m_ctl, post.sd_ctl, post.n_ctl,
                                post.dir_imp.values)
    gm = statlib.re_meta(post.g.values, post.g_v.values, method="PM")
    mu_d, tau_d = -gm["mu"], gm["tau"]     # positive = improvement in the sim
    print("true-SMD generator: mean %.3f, tau %.3f (from the corpus itself)"
          % (mu_d, tau_d))

    rng = np.random.default_rng(20260902)
    out = []
    for true_vr in (1.00, 0.95, 0.90, 0.85):
        acc = {lab: [] for _, _, lab in STRATA}
        overall = []
        for rep in range(120):
            dtrue = np.clip(rng.normal(mu_d, tau_d, len(n1s)), -1.5, 3.0)
            g, lnv = simulate(n1s, n2s, dtrue, np.log(true_vr), rng)
            overall.append(lnv.mean())
            for lo, hi, lab in STRATA:
                m = (g > lo) & (g <= hi) if lo > -50 else (g <= hi)
                if m.sum() >= 5:
                    acc[lab].append(lnv[m].mean())
        print("\ntrue lnVR = %+.4f  (VR %.2f);  simulated overall mean lnVR %+.4f"
              % (np.log(true_vr), true_vr, np.mean(overall)))
        for _, _, lab in STRATA:
            a = np.array(acc[lab])
            print("   %-24s simulated %+.4f  (mc se %.4f, %d reps)   "
                  "REAL CORPUS %+.4f"
                  % (lab, a.mean(), a.std(ddof=1) / np.sqrt(len(a)), len(a),
                     OBSERVED[lab]))
            out.append({"true_vr": true_vr, "stratum": lab,
                        "simulated_lnvr": float(a.mean()),
                        "mc_se": float(a.std(ddof=1) / np.sqrt(len(a))),
                        "observed_lnvr": OBSERVED[lab]})
        sim_grad = acc[STRATA[2][2]] and (np.mean(acc[STRATA[2][2]])
                                          - np.mean(acc[STRATA[0][2]]))
        print("   gradient (strongest stratum minus weakest): simulated %+.4f, "
              "real %+.4f" % (sim_grad, OBSERVED["SMD < -0.35"] - OBSERVED["|SMD| < 0.15"]))

    pd.DataFrame(out).to_csv(os.path.join(HERE, "out_dose_response_check.csv"),
                             index=False)
    print("\nHOW TO READ THIS")
    print("  If the true-VR = 1.00 block reproduces the real gradient, the")
    print("  dose-response in v06 test 3 is an artifact of stratifying on a")
    print("  quantity that shares a denominator with the outcome, and the correct")
    print("  reading is the domain-level one: no relation between how much the")
    print("  mean moved and how much the variance shrank.")
    print("  If the true-VR = 1.00 block is FLAT and only a real VR < 1 reproduces")
    print("  the overall level, the compression is real and the gradient tells us")
    print("  something about mechanism.")
    print("\nwrote out_dose_response_check.csv")


if __name__ == "__main__":
    main()
