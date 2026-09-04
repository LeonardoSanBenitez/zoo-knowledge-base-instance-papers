#!/usr/bin/env python3
"""w01 -- rebuild Munkholm, Winkelbeiner & Homan (2020) from the Cipriani GRISELDA
dataset, and check the reproduction before doing anything else with it.

THE PAPER.  222 placebo-controlled antidepressant RCTs, 345 comparisons, 61,144
adults, HAMD-17/21 or MADRS. Variability ratio VR = SD(drug)/SD(placebo) at
endpoint: 0.98 (95% CI 0.96 to 1.00, I2 = 0%) for raw endpoint scores and 1.00
(0.99 to 1.02) for baseline-to-endpoint change scores. Conclusion: "we cannot
reject the null hypothesis of equal variances ... it may be most reasonable to
assume that the average effect of antidepressants applies also to the individual
patient."

THE DEPOSIT.  The OSF project (https://osf.io/5gpe4/) holds the analysis code and
a data dictionary, and its `data/` folder holds NOTHING ELSE: the dataset itself
is a pointer to a third party, data.mendeley.com/datasets/83rthbp8ys/2, the open
data from Cipriani et al., Lancet 2018. The pointer still resolves, six years on,
and the file's sha256 matches the hash Mendeley's API declares. Recorded because
this corpus has the opposite case on file too.

WHY I AM HERE.  In `maria2026-mbp-variability-ratio` I found that lnVR and lnCVR
embed opposite untested assumptions about how a group's SD tracks its mean, and
that the true coefficient in a mindfulness corpus is about 0.47 rather than the 0
lnVR assumes or the 1 lnCVR assumes. If that is also true here, then VR = 0.98 on
raw ENDPOINT scores -- where the drug arm's mean is lower than placebo's by
construction -- is not the null result it is read as.

This script only extracts and reproduces. The calibration is w02.

Output: out_arms.csv, out_comparisons.csv
"""
import os
import sys
from collections import Counter

import numpy as np
import pandas as pd
import openpyxl

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "..", "tools"))
import statlib  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
XLSX = os.path.join(HERE, "..", "artifacts", "cipriani2018.xlsx")
SCALES = {"HAMD17", "HAMD21", "MADRS"}


def num(v):
    """Return (value, note). The workbook marks imputed/absent values with '*'."""
    if v is None:
        return None, "empty"
    if isinstance(v, (int, float)):
        return float(v), ""
    s = str(v).strip()
    if s in ("", "*", "NA", "-"):
        return None, "flagged-or-absent:" + s
    try:
        return float(s), ""
    except ValueError:
        import re
        m = re.search(r"-?\d+(\.\d+)?", s)
        if m:
            return float(m.group(0)), "extracted-from:" + s[:20]
        return None, "unparseable:" + s[:20]


def main():
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    rows = list(wb["DATA"].iter_rows(values_only=True))
    # rows[0], rows[1] are grouped banner headers; rows[2] is the column header
    hdr = [str(h) for h in rows[2]]
    print("workbook rows %d, header row is row 3, %d named columns"
          % (len(rows), sum(1 for h in hdr if h != "None")))
    COL = {"study": 0, "year": 1, "drug": 2, "n_rand": 3, "scale": 13,
           "base_mean": 14, "weeks": 15, "n_end": 16, "end_mean": 17, "end_sd": 18}

    rej = Counter()
    arms = []
    for r in rows[3:]:
        if r[0] is None:
            rej["blank row"] += 1
            continue
        scale = str(r[COL["scale"]]).strip() if r[COL["scale"]] else ""
        rec = {"study": str(r[COL["study"]]).strip(),
               "year": r[COL["year"]],
               "drug": str(r[COL["drug"]]).strip().lower(),
               "scale": scale}
        notes = []
        bad = False
        for k in ("n_rand", "base_mean", "n_end", "end_mean", "end_sd"):
            v, note = num(r[COL[k]])
            rec[k] = v
            if note:
                notes.append(k + ":" + note)
            if k in ("n_end", "end_mean", "end_sd") and v is None:
                rej["%s missing (%s)" % (k, note)] += 1
                bad = True
                break
        if bad:
            continue
        if scale not in SCALES:
            rej["scale not HAMD17/HAMD21/MADRS: " + (scale or "(blank)")] += 1
            continue
        if rec["end_sd"] <= 0 or rec["n_end"] < 3:
            rej["nonpositive SD or n < 3"] += 1
            continue
        rec["notes"] = ";".join(notes)
        # the dictionary: negative endpoint means are baseline-to-endpoint CHANGE
        rec["is_change"] = rec["end_mean"] < 0
        arms.append(rec)

    A = pd.DataFrame(arms)
    print("\nKEPT %d arms in %d studies" % (len(A), A.study.nunique()))
    print("dropped, with reasons:")
    for k, v in rej.most_common(12):
        print("  %5d  %s" % (v, k))
    print("  (total dropped %d of %d data rows)" % (sum(rej.values()), len(rows) - 3))
    print("\nby scale:", dict(A.scale.value_counts()))
    print("endpoint kind: %d raw endpoint, %d change score"
          % ((~A.is_change).sum(), A.is_change.sum()))
    print("placebo arms: %d; distinct drugs: %d"
          % ((A.drug == "placebo").sum(), A.drug.nunique()))
    A.to_csv(os.path.join(HERE, "out_arms.csv"), index=False)

    # ---- build drug vs placebo comparisons within study -------------------
    comps = []
    for (study, scale, ischg), g in A.groupby(["study", "scale", "is_change"]):
        pbo = g[g.drug == "placebo"]
        act = g[g.drug != "placebo"]
        if len(pbo) == 0 or len(act) == 0:
            continue
        # if a trial has more than one placebo arm, pool them by inverse variance
        if len(pbo) > 1:
            w = pbo.n_end.values
            m = (w * pbo.end_mean.values).sum() / w.sum()
            v = ((pbo.n_end - 1) * pbo.end_sd ** 2).sum() / (pbo.n_end.sum() - len(pbo))
            p = {"end_mean": m, "end_sd": np.sqrt(v), "n_end": pbo.n_end.sum(),
                 "base_mean": pbo.base_mean.mean()}
        else:
            p = pbo.iloc[0]
        for _, a in act.iterrows():
            comps.append({
                "study": study, "scale": scale, "is_change": ischg,
                "drug": a.drug, "year": a.year,
                "n_drug": a.n_end, "m_drug": a.end_mean, "sd_drug": a.end_sd,
                "n_pbo": p["n_end"], "m_pbo": p["end_mean"], "sd_pbo": p["end_sd"],
                "base_drug": a.base_mean, "base_pbo": p["base_mean"],
            })
    C = pd.DataFrame(comps)
    C["lnvr"], C["lnvr_v"] = statlib.lnvr(C.sd_drug, C.n_drug, C.sd_pbo, C.n_pbo)
    C["lnmr"] = np.log(np.abs(C.m_drug) / np.abs(C.m_pbo))
    sp = np.sqrt(((C.n_drug - 1) * C.sd_drug ** 2 + (C.n_pbo - 1) * C.sd_pbo ** 2)
                 / (C.n_drug + C.n_pbo - 2))
    J = 1 - 3.0 / (4 * (C.n_drug + C.n_pbo) - 9)
    C["g"] = J * (C.m_drug - C.m_pbo) / sp
    C["g_v"] = ((C.n_drug + C.n_pbo) / (C.n_drug * C.n_pbo)
                + C.g ** 2 / (2 * (C.n_drug + C.n_pbo - 2))) * J ** 2
    C.to_csv(os.path.join(HERE, "out_comparisons.csv"), index=False)
    print("\n%d drug-vs-placebo comparisons in %d studies "
          "(%d raw endpoint, %d change score)"
          % (len(C), C.study.nunique(), (~C.is_change).sum(), C.is_change.sum()))
    print("paper reports 345 comparisons in 222 RCTs, 19 drugs; here %d drugs"
          % C.drug.nunique())

    # ---- REPRODUCTION CHECK ----------------------------------------------
    print("\nREPRODUCTION CHECK -- variability ratio, drug vs placebo")
    print("  paper: raw endpoint VR 0.98 [0.96, 1.00] I2 0%%;  "
          "change score VR 1.00 [0.99, 1.02] I2 0%%")
    for lab, sub in (("raw endpoint scores", C[~C.is_change]),
                     ("baseline-to-endpoint change scores", C[C.is_change]),
                     ("all comparisons", C)):
        if len(sub) < 5:
            continue
        r = statlib.re_meta(sub.lnvr.values, sub.lnvr_v.values, method="DL")
        cb = statlib.cluster_bootstrap_meta(sub.lnvr.values, sub.lnvr_v.values,
                                            sub.study.values, B=3000, seed=5)
        print("  %-36s VR %.3f  RE 95%% [%.3f, %.3f]  cluster-boot [%.3f, %.3f]  "
              "I2 %s  (k=%d, %d studies)"
              % (lab, np.exp(r["mu"]), np.exp(r["ci"][0]), np.exp(r["ci"][1]),
                 np.exp(cb["ci"][0]), np.exp(cb["ci"][1]),
                 "%.0f%%" % (100 * r["I2"]) if r["I2"] is not None else "n/a",
                 r["k"], sub.study.nunique()))
    print("\n  mean effect, for orientation:")
    for lab, sub in (("raw endpoint", C[~C.is_change]),):
        r = statlib.re_meta(sub.g.values, sub.g_v.values, method="DL")
        print("    SMD %+.3f [%+.3f, %+.3f]  -- the paper's companion literature "
              "puts the HAMD difference near 2 points" % (r["mu"], *r["ci"]))
        print("    mean HAMD/MADRS endpoint: drug %.2f, placebo %.2f, "
              "ln ratio %+.4f" % (sub.m_drug.mean(), sub.m_pbo.mean(),
                                  sub.lnmr.mean()))
    print("\nwrote out_arms.csv, out_comparisons.csv")


if __name__ == "__main__":
    main()
