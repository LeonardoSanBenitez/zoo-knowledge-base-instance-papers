#!/usr/bin/env python3
"""v04 -- the decisive version of the bounded-scale test.

THE THREAT THAT SURVIVED v03.  On any bounded questionnaire, moving the mean
toward a bound compresses the standard deviation, with no heterogeneity of
treatment effect involved. v03 tested this two ways and neither is airtight:

  * The zero-floor simulation says the artifact needs the mean within about two
    SDs of the floor, and the corpus median is 4.23 SDs above ZERO. But the
    relevant bound is the SCALE MINIMUM, not zero, and for MAAS (1-6), PANAS
    (10-50) or STAI (20-80) the scale minimum is far above zero. The proxy
    understates floor pressure for exactly those instruments.
  * The coupling regression in v03 extrapolates a LINEAR slope, fitted over the
    small mean-changes control arms happen to show, to the larger changes the
    treated arms show. If the coupling accelerates near a bound, that
    under-corrects.

THE FIX, which needs no knowledge of any scale's bounds and no linearity.

In each trial x outcome there are FOUR arm-observations of (mean, SD, n), and
THREE of them are untreated:

      baseline mindfulness arm     untreated (measured before the programme)
      baseline control arm         untreated
      post-intervention control    untreated
      post-intervention MBP        the only treated one

So the untreated observations trace out, empirically and per instrument, the
relation between an arm's mean and its SD -- whatever shape that relation has,
whatever bounds the instrument has, including any acceleration near them. Fit
that reference curve on untreated arms only, then ask where the one treated
observation sits relative to it.

If mindfulness only shifts the mean, the treated arm must land ON the curve. Any
systematic shortfall BELOW it is variance reduction the mean movement does not
explain.

Two fits, because the shape matters:
  LINEAR     log SD ~ a + b log mean, per instrument (instrument fixed effects)
  QUADRATIC  log SD ~ a + b log mean + c (log mean)^2, per instrument
and a nonparametric version that uses only within-instrument rank position.

Output: out_reference_curve.csv
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


def long_form(d):
    """One row per ARM-OBSERVATION, flagged treated / untreated."""
    out = []
    for _, r in d.iterrows():
        treated_post = r.trange in ("Postintervention", "1-6months", "6+months")
        out.append({"study": r.study, "instrument": r.instrument, "outcome": r.outcome,
                    "domain": r.domain, "trange": r.trange, "arm": "mbp",
                    "m": r.m_mbp, "sd": r.sd_mbp, "n": r.n_mbp,
                    "treated": treated_post, "ctrl_cat": r.ctrl_cat})
        out.append({"study": r.study, "instrument": r.instrument, "outcome": r.outcome,
                    "domain": r.domain, "trange": r.trange, "arm": "ctl",
                    "m": r.m_ctl, "sd": r.sd_ctl, "n": r.n_ctl,
                    "treated": False, "ctrl_cat": r.ctrl_cat})
    return pd.DataFrame(out)


def main():
    d = pd.read_csv(os.path.join(HERE, "out_arms.csv"))
    L = long_form(d)
    L = L[(L.m > 0) & (L.sd > 0)]
    L["lm"] = np.log(L.m)
    L["ls"] = np.log(L.sd)
    print("%d arm-observations, %d untreated / %d treated, over %d instruments"
          % (len(L), (~L.treated).sum(), L.treated.sum(), L.instrument.nunique()))
    print("NOTE: 'untreated' includes the mindfulness arm AT BASELINE, which is the "
          "\n      point of the design -- it is the same people on the same "
          "instrument\n      before anything happened to them.")

    # instruments with enough untreated points to fit a curve
    cnt = L[~L.treated].groupby("instrument").size()
    rows = []
    for degree, name in ((1, "LINEAR"), (2, "QUADRATIC")):
        need = 6 if degree == 1 else 9
        keep = set(cnt[cnt >= need].index)
        resid, wts, studies, insts = [], [], [], []
        for inst in keep:
            sub = L[L.instrument == inst]
            ref = sub[~sub.treated]
            tre = sub[sub.treated & (sub.arm == "mbp")]
            if len(tre) == 0 or ref.lm.nunique() < degree + 1:
                continue
            X = np.column_stack([ref.lm ** k for k in range(degree + 1)])
            w = np.sqrt(ref.n.values)
            try:
                beta, *_ = np.linalg.lstsq(X * w[:, None], ref.ls.values * w, rcond=None)
            except np.linalg.LinAlgError:
                continue
            Xt = np.column_stack([tre.lm ** k for k in range(degree + 1)])
            pred = Xt @ beta
            r = tre.ls.values - pred
            resid.extend(r)
            wts.extend(tre.n.values)
            studies.extend(tre.study.values)
            insts.extend([inst] * len(tre))
        resid = np.array(resid)
        studies = np.array(studies)
        uq = np.unique(studies)
        idx = {s: np.flatnonzero(studies == s) for s in uq}
        rng = np.random.default_rng(SEED)
        bs = [float(np.mean(resid[np.concatenate(
            [idx[s] for s in rng.choice(uq, len(uq), replace=True)])]))
            for _ in range(4000)]
        lo, hi = np.percentile(bs, [2.5, 97.5])
        p = 2 * min(np.mean(np.array(bs) <= 0), np.mean(np.array(bs) >= 0))
        print("\n%s reference curve, %d instruments with >= %d untreated points"
              % (name, len({i for i in insts}), need))
        print("  treated arms sit  %+.4f  in log SD relative to the untreated curve"
              % resid.mean())
        print("  95%% cluster bootstrap over %d studies [%+.4f, %+.4f]  p = %.4f"
              % (len(uq), lo, hi, max(p, 1 / 4000)))
        print("  i.e. SD ratio %.3f  (%d treated observations)"
              % (np.exp(resid.mean()), len(resid)))
        rows.append({"fit": name, "n_treated_obs": len(resid),
                     "n_instruments": len(set(insts)), "n_studies": len(uq),
                     "mean_log_resid": float(resid.mean()), "lo": lo, "hi": hi,
                     "sd_ratio": float(np.exp(resid.mean())), "p": max(p, 1 / 4000)})

    # ---------- nonparametric: within instrument, is the treated SD low for its
    # rank in the mean? Uses only orderings, so no functional form at all.
    print("\nNONPARAMETRIC within-instrument check")
    print("  For each instrument, rank all arm-observations by mean and by SD.")
    print("  A pure location shift moves an arm along BOTH rankings together, so")
    print("  (rank in SD) - (rank in mean) should be 0 on average for treated arms")
    print("  exactly as it is for untreated ones.")
    diffs = {True: [], False: []}
    for inst, sub in L.groupby("instrument"):
        if len(sub) < 8:
            continue
        rm = stats.rankdata(sub.m.values) / (len(sub) + 1)
        rs = stats.rankdata(sub.sd.values) / (len(sub) + 1)
        for t, dd in zip(sub.treated.values, rs - rm):
            diffs[bool(t)].append(dd)
    for t in (False, True):
        a = np.array(diffs[t])
        print("  %-9s n = %4d   mean (rank in SD - rank in mean) = %+.4f  (se %.4f)"
              % ("treated" if t else "untreated", len(a), a.mean(),
                 a.std(ddof=1) / np.sqrt(len(a))))
    a, b = np.array(diffs[True]), np.array(diffs[False])
    dd = a.mean() - b.mean()
    se = np.hypot(a.std(ddof=1) / np.sqrt(len(a)), b.std(ddof=1) / np.sqrt(len(b)))
    print("  difference %+.4f (se %.4f, z = %.2f)  -- negative means treated arms"
          % (dd, se, dd / se))
    print("  have a LOWER SD than their mean rank predicts")
    rows.append({"fit": "NONPARAMETRIC rank", "n_treated_obs": len(a),
                 "n_instruments": None, "n_studies": None,
                 "mean_log_resid": float(dd), "lo": dd - 1.96 * se,
                 "hi": dd + 1.96 * se, "sd_ratio": None,
                 "p": float(2 * (1 - stats.norm.cdf(abs(dd / se))))})

    pd.DataFrame(rows).to_csv(os.path.join(HERE, "out_reference_curve.csv"), index=False)
    print("\nwrote out_reference_curve.csv")


if __name__ == "__main__":
    main()
