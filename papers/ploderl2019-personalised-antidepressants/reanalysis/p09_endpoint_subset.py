"""p09 -- the decisive test of the CVR mechanism, using the authors' own
supplementary table.

THE PREDICTION, WRITTEN BEFORE LOOKING AT THE SUPPLEMENT. p02 showed that per
trial lnCVR - lnVR = ln(m_PL/m_AD) exactly. In the main analysis the reported
"mean" is a pre-post CHANGE, and the drug arm changes MORE, so m_AD > m_PL and
CVR < VR. Their supplementary table 1 runs the identical analysis on the 84
trials that reported an ENDPOINT score instead. An endpoint score is a level:
the drug arm's is the SMALLER one, because the drug works. So m_AD < m_PL and
the identity requires

        CVR > VR > CVR_change_subset

i.e. the same statistic, the same drugs, the same authors, must come out ABOVE 1
on the endpoint subset and BELOW 1 on the change subset -- with the direction set
by nothing but which of two equivalent ways a trial happened to report its
outcome.

WHAT THE SUPPLEMENT ACTUALLY SAYS (read after writing the above):

    AD all      84 trials   VR 0.98 (0.96-1.00)   CVR 1.15 (1.11-1.18)
    SSRI        40          VR 0.99               CVR 1.13
    SNRI        13          VR 0.99               CVR 1.15
    atypical    31          VR 0.97               CVR 1.12
    tricyclics  13          VR 0.93               CVR 1.37

Against the main table's CVR of 0.82 (and 0.65 for tricyclics). The prediction
holds, including the ordering of the subgroups: tricyclics, which have the
largest drug-placebo gap in this dataset, are the most extreme in BOTH
directions.

This script rebuilds the endpoint subset from the upstream data and checks the
arithmetic: CVR/VR should equal the endpoint mean ratio m_PL/m_AD in each row.
"""
import csv
import io
import json
import os
import sys

import numpy as np
from scipy import stats

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "tools"))
import statlib  # noqa: E402
sys.path.insert(0, HERE)
from p01_build import DRUGS, CLASS, canon, num, XLSX  # noqa: E402


def build_post():
    """same as p01, but keeping outcome == 'post' instead of 'diff'."""
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    ws = wb["DATA"]
    studies, order = {}, []
    for r in ws.iter_rows(min_row=4, values_only=True):
        sid = r[0]
        if sid is None or str(sid).strip() == "":
            continue
        sid = str(sid).strip()
        rec = dict(drug=canon(r[2]), scale=str(r[13] or "").strip(),
                   n=num(r[16]), m=num(r[17]), sd=num(r[18]))
        if sid not in studies:
            studies[sid] = []
            order.append(sid)
        studies[sid].append(rec)

    out = []
    for sid in order:
        arms = studies[sid]
        pl = [a for a in arms if a["drug"] == "placebo"
              and None not in (a["m"], a["sd"], a["n"])]
        ad = [a for a in arms if a["drug"] in DRUGS
              and None not in (a["m"], a["sd"], a["n"])]
        if not pl or not ad:
            continue
        signs = {1 if a["m"] > 0 else -1 for a in ad + pl}
        if len(signs) > 1 or signs != {1}:      # 'post' = positive means
            continue
        out.append(dict(
            study=sid, scale=ad[0]["scale"],
            cls="|".join(sorted({CLASS[a["drug"]] for a in ad})),
            all_n=sum(a["n"] for a in ad),
            all_sd=sum(a["sd"] for a in ad) / len(ad),
            all_m=sum(abs(a["m"]) for a in ad) / len(ad),
            placebo_n=sum(a["n"] for a in pl),
            placebo_sd=sum(a["sd"] for a in pl) / len(pl),
            placebo_m=sum(abs(a["m"]) for a in pl) / len(pl)))
    return out


def knha(y, v, tau2):
    w = 1.0 / (v + tau2)
    mu = (w * y).sum() / w.sum()
    k = len(y)
    s2 = (w * (y - mu) ** 2).sum() / (k - 1)
    se = np.sqrt(s2 / w.sum())
    t = stats.t.ppf(0.975, k - 1)
    return mu, (mu - t * se, mu + t * se)


def main():
    rows = build_post()
    A = lambda k, sub=None: np.array([r[k] for r in (sub if sub is not None
                                                     else rows)], float)
    n1, s1, m1 = A("all_n"), A("all_sd"), A("all_m")
    n2, s2, m2 = A("placebo_n"), A("placebo_sd"), A("placebo_m")
    print("endpoint subset rebuilt: %d trials, %d drug and %d placebo patients"
          % (len(rows), n1.sum(), n2.sum()))
    print("  their supplementary table 1 says 84 trials, 10,879 and 7,346")

    yv, vv = statlib.lnvr(s1, n1, s2, n2)
    yc, vc = statlib.lncvr(m1, s1, n1, m2, s2, n2)
    out = {}
    for lab, y, v, theirs in (("VR ", yv, vv, "0.98 (0.96-1.00)"),
                              ("CVR", yc, vc, "1.15 (1.11-1.18)")):
        m = statlib.re_meta(y, v, method="DL")
        mu, ci = knha(y, v, m["tau2"])
        print("  %s = %.4f [%.4f, %.4f]   theirs: %s"
              % (lab, np.exp(mu), np.exp(ci[0]), np.exp(ci[1]), theirs))
        out[lab.strip()] = dict(value=float(np.exp(mu)),
                                ci=[float(np.exp(ci[0])), float(np.exp(ci[1]))])

    print()
    print("the identity, on this subset:")
    d = yc - yv
    lr = np.log(m2 / m1)
    print("  max |lnCVR_i - lnVR_i - ln(m_PL/m_AD)| = %.2e" % np.abs(d - lr).max())
    print("  trials where the DRUG arm has the smaller mean: %d of %d (%.0f%%)"
          % (int(np.sum(m1 < m2)), len(rows), 100 * np.mean(m1 < m2)))
    print("  n-weighted endpoint score: drug %.2f, placebo %.2f, ratio %.4f"
          % ((n1 * m1).sum() / n1.sum(), (n2 * m2).sum() / n2.sum(),
             ((n2 * m2).sum() / n2.sum()) / ((n1 * m1).sum() / n1.sum())))
    out["identity_max_dev"] = float(np.abs(d - lr).max())

    print()
    print("=== the same statistic, both reporting conventions ===")
    print("  %-12s %-10s %-10s %-10s" % ("subgroup", "VR change", "CVR change",
                                         "CVR endpoint"))
    their_change = {"AD all": (1.01, 0.82), "SSRI": (1.01, 0.83),
                    "SNRI": (1.00, 0.81), "atypical": (1.00, 0.83),
                    "tricyclic": (1.04, 0.65)}
    their_end = {"AD all": (0.98, 1.15), "SSRI": (0.99, 1.13),
                 "SNRI": (0.99, 1.15), "atypical": (0.97, 1.12),
                 "tricyclic": (0.93, 1.37)}
    for g in ("AD all", "SSRI", "SNRI", "atypical", "tricyclic"):
        print("  %-12s %-10.2f %-10.2f %-10.2f   <- their own two tables"
              % (g, their_change[g][0], their_change[g][1], their_end[g][1]))
    print()
    print("  VR is stable across the two conventions (1.01 vs 0.98).")
    print("  CVR moves from 0.82 to 1.15 -- it crosses 1 -- and for tricyclics")
    print("  from 0.65 to 1.37, a factor of 2.1, on the same drugs.")
    print("  Nothing about the patients changed. Only which of two equivalent")
    print("  summaries the trial reports.")

    print()
    print("=== does the CVR/VR ratio equal the endpoint mean ratio per subgroup? ===")
    print("  %-12s %6s %8s %10s" % ("subgroup", "k", "CVR/VR", "m_PL/m_AD"))
    for g, sel in (("AD all", lambda r: True),
                   ("SSRI", lambda r: r["cls"] == "SSRI"),
                   ("SNRI", lambda r: r["cls"] == "SNRI"),
                   ("atypical", lambda r: r["cls"] == "atypical"),
                   ("tricyclic", lambda r: r["cls"] == "tricyclic")):
        sub = [r for r in rows if sel(r)]
        if len(sub) < 3:
            continue
        i = np.array([j for j, r in enumerate(rows) if sel(r)])
        a = statlib.re_meta(*statlib.lnvr(s1[i], n1[i], s2[i], n2[i]), method="DL")
        b = statlib.re_meta(*statlib.lncvr(m1[i], s1[i], n1[i], m2[i], s2[i],
                                           n2[i]), method="DL")
        ratio = np.exp(np.mean(np.log(m2[i] / m1[i])))
        print("  %-12s %6d %8.3f %10.3f"
              % (g, len(sub), np.exp(b["mu"] - a["mu"]), ratio))
        out.setdefault("by_group", {})[g] = dict(
            k=len(sub), cvr_over_vr=float(np.exp(b["mu"] - a["mu"])),
            mean_ratio=float(ratio))

    with io.open(os.path.join(HERE, "out_p09.json"), "w", encoding="utf-8",
                 newline="\n") as f:
        json.dump(out, f, indent=1)
    print()
    print("wrote out_p09.json")


if __name__ == "__main__":
    main()
