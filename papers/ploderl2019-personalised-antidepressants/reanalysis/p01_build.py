"""p01 -- rebuild Plöderl & Hengartner (2019) analysis dataset from the ORIGINAL
Cipriani et al. (2018) GRISELDA workbook.

Why rebuild rather than download theirs: https://osf.io/98kex/files/ is cited in
the paper as holding "the R-code and data of this publication". It holds ten
files, all of them code or supplementary PDFs. The modified CSV the code reads
(`Cipriani et al_GRISELDA_Lancet 2018_Open data_averaged_doses.csv`) is not
there. So the input is reconstructed here from the public upstream file, using
exactly the transformations their code documents.

Their transformations, from the header comment of
`cipriani-variance-data-generation-2.r` and its lines 99-100, 162-164:

  * arm mean used is abs(Mean.1) -- the magnitude of the pre-post change
  * outcome type is read off the SIGN of Mean.1: negative => change score
    ("diff"), positive => endpoint score ("post"). Main analysis uses "diff".
  * multiple antidepressant arms in one trial are collapsed with
        all.n  = SUM of arm n
        all.sd = unweighted MEAN of arm SDs        <-- note
        all.m  = unweighted MEAN of arm means      <-- note
  * dose arms of the same drug were collapsed the same way, by hand, in the CSV
    (so the collapse is applied twice; here it happens once, over all AD arms)
  * one typo fix: Learned2012a Study1 had "Placebo" instead of "placebo"

Writes: dat.csv (one row per trial), and prints reconstruction diagnostics.
"""
import io
import json
import os
import sys

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
XLSX = os.path.join(HERE, "..", "artifacts", "cipriani2018_griselda.xlsx")

DRUGS = """agomelatine amitriptyline bupropion citalopram clomipramine
desvenlafaxine duloxetine escitalopram fluoxetine fluvoxamine levomilnacipran
milnacipran mirtazapine nefazodone paroxetine reboxetine sertraline trazodone
venlafaxine vilazodone vortioxetine""".split()

CLASS = {}
for d in "citalopram escitalopram fluoxetine fluvoxamine paroxetine sertraline".split():
    CLASS[d] = "SSRI"
for d in ("desvenlafaxine duloxetine levomilnacipran milnacipran reboxetine "
          "venlafaxine").split():
    CLASS[d] = "SNRI"
for d in ("agomelatine bupropion mirtazapine nefazodone trazodone vilazodone "
          "vortioxetine").split():
    CLASS[d] = "atypical"
for d in "amitriptyline clomipramine".split():
    CLASS[d] = "tricyclic"


def canon(label):
    """'fluoxetine 20mg' -> 'fluoxetine'; 'venlafaxine xr 75-150mg' -> 'venlafaxine'.

    The upstream file labels a dose arm with drug + dose. Plöderl & Hengartner
    collapsed dose arms BY HAND in their private CSV ("For multiple dosages of
    medications, the data was aggregated, using mean values outcome (Mean, SD)
    and the sum of the sample sizes"); doing it programmatically here is the
    same operation. 73 of the 94 distinct arm labels are dose arms.
    """
    lab = str(label or "").strip().lower()
    if lab == "placebo":
        return "placebo"
    head = lab.split()[0] if lab.split() else ""
    return head if head in DRUGS else lab


def num(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(",", ".")
    if s in ("", "*", "NA", "-"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def main():
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    ws = wb["DATA"]
    rows = list(ws.iter_rows(min_row=4, values_only=True))
    print("raw arm rows:", len(rows))

    studies = {}
    order = []
    for r in rows:
        sid = r[0]
        if sid is None or str(sid).strip() == "":
            continue
        sid = str(sid).strip()
        drug = canon(r[2])
        rec = dict(
            drug=drug,
            year=num(r[1]),
            randomised=num(r[3]),
            dropouts=num(r[11]),
            scale=str(r[13] or "").strip(),
            baseline=num(r[14]),
            weeks=num(r[15]),
            n=num(r[16]),
            m=num(r[17]),
            sd=num(r[18]),
        )
        if sid not in studies:
            studies[sid] = []
            order.append(sid)
        studies[sid].append(rec)

    print("distinct StudyIDs:", len(studies))
    drugnames = sorted({a["drug"] for arms in studies.values() for a in arms})
    unknown = [d for d in drugnames if d not in DRUGS and d != "placebo"]
    print("distinct arm labels:", len(drugnames), "| not a listed AD or placebo:", unknown)

    out = []
    n_multi = 0
    skip = {"no placebo arm": 0, "no usable AD arm": 0, "outcome not diff": 0,
            "mixed sign": 0, "incomplete": 0}
    for sid in order:
        arms = studies[sid]
        pl = [a for a in arms if a["drug"] == "placebo"]
        ad = [a for a in arms if a["drug"] in DRUGS]
        if not pl:
            skip["no placebo arm"] += 1
            continue
        ad_ok = [a for a in ad if a["m"] is not None and a["sd"] is not None
                 and a["n"] is not None]
        pl_ok = [a for a in pl if a["m"] is not None and a["sd"] is not None
                 and a["n"] is not None]
        if not ad_ok or not pl_ok:
            skip["incomplete"] += 1
            continue
        signs = {1 if a["m"] > 0 else -1 for a in ad_ok + pl_ok}
        if len(signs) > 1:
            skip["mixed sign"] += 1
            continue
        outcome = "diff" if signs == {-1} else "post"
        if outcome != "diff":
            skip["outcome not diff"] += 1
            continue

        if len(ad_ok) > 1:
            n_multi += 1
        # THEIR aggregation
        all_n = sum(a["n"] for a in ad_ok)
        all_sd = sum(a["sd"] for a in ad_ok) / len(ad_ok)
        all_m = sum(abs(a["m"]) for a in ad_ok) / len(ad_ok)
        # placebo: if more than one placebo arm, same rule
        p_n = sum(a["n"] for a in pl_ok)
        p_sd = sum(a["sd"] for a in pl_ok) / len(pl_ok)
        p_m = sum(abs(a["m"]) for a in pl_ok) / len(pl_ok)

        # CORRECT mixture pooling of the AD arms (variance of a finite mixture)
        N = all_n
        grand = sum(a["n"] * abs(a["m"]) for a in ad_ok) / N
        within = sum((a["n"] - 1) * a["sd"] ** 2 for a in ad_ok)
        between = sum(a["n"] * (abs(a["m"]) - grand) ** 2 for a in ad_ok)
        pooled_sd = ((within + between) / (N - 1)) ** 0.5

        classes = {CLASS[a["drug"]] for a in ad_ok}
        out.append(dict(
            study=sid,
            year=ad_ok[0]["year"],
            scale=ad_ok[0]["scale"],
            weeks=ad_ok[0]["weeks"],
            baseline=ad_ok[0]["baseline"],
            k_ad_arms=len(ad_ok),
            drugs="|".join(sorted(a["drug"] for a in ad_ok)),
            cls="|".join(sorted(classes)),
            all_n=all_n, all_sd=all_sd, all_m=all_m,
            pooled_sd=pooled_sd, pooled_m=grand,
            placebo_n=p_n, placebo_sd=p_sd, placebo_m=p_m,
        ))

    print("trials kept (outcome=diff, complete):", len(out))
    print("  of which with >1 AD arm:", n_multi)
    print("skipped:", json.dumps(skip))
    print("total n, AD arms:", int(sum(r["all_n"] for r in out)))
    print("total n, placebo arms:", int(sum(r["placebo_n"] for r in out)))
    print("total n:", int(sum(r["all_n"] + r["placebo_n"] for r in out)))

    cols = list(out[0].keys())
    with io.open(os.path.join(HERE, "dat.csv"), "w", encoding="utf-8",
                 newline="\n") as f:
        f.write(";".join(cols) + "\n")
        for r in out:
            f.write(";".join("" if r[c] is None else str(r[c]) for c in cols) + "\n")
    print("wrote dat.csv")


if __name__ == "__main__":
    main()
