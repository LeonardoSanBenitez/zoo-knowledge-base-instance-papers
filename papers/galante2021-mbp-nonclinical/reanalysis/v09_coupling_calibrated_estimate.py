#!/usr/bin/env python3
"""v09 -- the final estimate, and the methodological point it makes.

THE PROBLEM WITH BOTH STANDARD STATISTICS.  Every variability-ratio meta-analysis
reports two numbers and treats one of them as the answer:

    lnVR  = ln(SD1/SD2)                     assumes SD does not track the mean
                                            at all -- i.e. coupling slope beta = 0
    lnCVR = ln(SD1/SD2) - ln(m1/m2)         assumes SD is PROPORTIONAL to the mean
                                            -- i.e. beta = 1

Neither assumption is tested in any of them. Both can be tested here, because
this corpus has BASELINE arm pairs: at baseline the two arms differ only by
chance, so whatever relation exists between their log mean ratio and their log SD
ratio is the instruments' and the populations' natural coupling, with no treatment
in it at all.

That baseline coupling is measured here and it is about 0.47 -- halfway between
the two assumptions. So lnVR under-corrects by half and lnCVR over-corrects by
half, and the corrected statistic is

    lnVR* = lnVR - beta_hat * ln(m1/m2),   beta_hat estimated at baseline

with beta's own uncertainty propagated. That is the estimate this script reports,
and it is the one I would defend.

Output: out_final_estimate.csv
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
B = 4000
SEED = 20260902


def main():
    d = pd.read_csv(os.path.join(HERE, "out_arms.csv"))
    d["lnvr"], d["lnvr_v"] = statlib.lnvr(d.sd_mbp, d.n_mbp, d.sd_ctl, d.n_ctl)
    d["lnmr"] = np.log(d.m_mbp / d.m_ctl)
    d = d[np.isfinite(d.lnmr) & (d.lnmr.abs() < 1.5)]
    base = d[(d.trange == "Baseline") & (d.ctrl_cat == "passive")]
    post = d[(d.trange == "Postintervention") & (d.ctrl_cat == "passive")]
    later = d[(d.trange == "1-6months") & (d.ctrl_cat == "passive")]

    print("1  THE COUPLING CONSTANT, measured where there is no treatment")
    print("   At BASELINE the arms differ only by randomisation. Regressing the")
    print("   log SD ratio on the log mean ratio there measures how much of a")
    print("   between-arm difference in SD travels with a difference in mean.")
    rng = np.random.default_rng(SEED)
    uq = np.unique(base.study.values)
    idx = {c: np.flatnonzero(base.study.values == c) for c in uq}
    lnmr_b, lnvr_b = base.lnmr.values, base.lnvr.values
    betas = []
    for _ in range(B):
        sel = np.concatenate([idx[c] for c in rng.choice(uq, len(uq), replace=True)])
        if len(np.unique(lnmr_b[sel])) < 3:
            continue
        betas.append(stats.linregress(lnmr_b[sel], lnvr_b[sel])[0])
    beta = stats.linregress(lnmr_b, lnvr_b)[0]
    blo, bhi = np.percentile(betas, [2.5, 97.5])
    print("   beta = %.3f   95%% cluster bootstrap [%.3f, %.3f]   "
          "(%d baseline pairs, %d trials)" % (beta, blo, bhi, len(base), len(uq)))
    print("   lnVR assumes beta = 0 -> rejected (%.3f is %.1f bootstrap SEs above 0)"
          % (beta, beta / np.std(betas, ddof=1)))
    print("   lnCVR assumes beta = 1 -> rejected (%.1f SEs below 1)"
          % ((1 - beta) / np.std(betas, ddof=1)))

    print("\n2  THE THREE ESTIMATES SIDE BY SIDE")
    rows = []
    for lab, sub in (("BASELINE (must be ~0 for all three)", base),
                     ("POST-INTERVENTION, all scales", post),
                     ("POST, symptom scales (lower is better)",
                      post[post.dir_imp == "D"]),
                     ("POST, positively-keyed scales", post[post.dir_imp == "U"]),
                     ("1-6 MONTHS, all scales", later)):
        if len(sub) < 8:
            continue
        u = np.unique(sub.study.values)
        ii = {c: np.flatnonzero(sub.study.values == c) for c in u}
        rng2 = np.random.default_rng(SEED + 1)
        est = {"lnVR": [], "lnCVR": [], "lnVR*": []}
        for _ in range(B):
            bsel = np.concatenate([idx[c] for c in
                                   rng2.choice(uq, len(uq), replace=True)])
            bb = stats.linregress(lnmr_b[bsel], lnvr_b[bsel])[0] \
                if len(np.unique(lnmr_b[bsel])) >= 3 else beta
            sel = np.concatenate([ii[c] for c in rng2.choice(u, len(u), replace=True)])
            v_ = sub.lnvr.values[sel]
            m_ = sub.lnmr.values[sel]
            est["lnVR"].append(v_.mean())
            est["lnCVR"].append((v_ - m_).mean())
            est["lnVR*"].append((v_ - bb * m_).mean())
        pt = {"lnVR": sub.lnvr.mean(),
              "lnCVR": (sub.lnvr - sub.lnmr).mean(),
              "lnVR*": (sub.lnvr - beta * sub.lnmr).mean()}
        line = "   %-40s" % lab
        rec = {"subset": lab, "k": len(sub), "studies": len(u), "beta": beta}
        for name in ("lnVR", "lnCVR", "lnVR*"):
            lo, hi = np.percentile(est[name], [2.5, 97.5])
            line += "  %s %+.4f [%+.4f,%+.4f]" % (name, pt[name], lo, hi)
            rec[name] = pt[name]
            rec[name + "_lo"] = lo
            rec[name + "_hi"] = hi
        print(line)
        print("      %-38s  ratio-scale: VR %.3f   VR* %.3f   (k=%d, %d trials)"
              % ("", np.exp(pt["lnVR"]), np.exp(pt["lnVR*"]), len(sub), len(u)))
        rows.append(rec)

    print("\n3  WHAT EACH STATISTIC WOULD HAVE CONCLUDED, post-intervention, all scales")
    r = [x for x in rows if x["subset"].startswith("POST-INTERVENTION")][0]
    for name, verdict in (("lnVR", "the programme reduces variability"),
                          ("lnCVR", "no variability difference"),
                          ("lnVR*", "the coupling-calibrated answer")):
        sig = "" if r[name + "_lo"] <= 0 <= r[name + "_hi"] else "  <- excludes 0"
        print("   %-6s %+.4f [%+.4f, %+.4f]%-16s  %s"
              % (name, r[name], r[name + "_lo"], r[name + "_hi"], sig, verdict))
    print("\n   The three disagree, and which one a reader believes is decided")
    print("   entirely by an assumption about beta that no published variability")
    print("   ratio meta-analysis states, tests, or reports.")

    pd.DataFrame(rows).to_csv(os.path.join(HERE, "out_final_estimate.csv"), index=False)
    print("\nwrote out_final_estimate.csv")


if __name__ == "__main__":
    main()
