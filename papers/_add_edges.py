#!/usr/bin/env python3
"""Add the reciprocal edges for the 2026-09-02 wellbeing-and-income records.

CONTRIBUTING.md rule 5: when you add a relation, add the reciprocal to the OTHER
paper's record, or the graph is directed by accident of who was edited last.
Two of the edges below came from `kb.py suggest`, which is the first time that
tool has produced an edge I would not have thought of. maria, 2026-09-02.
"""
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# (record to edit, relation type, target, why)
EDGES = [
    # ---- reciprocals of edges declared in maria2026-happiness-income-spread ----
    ("mathur2023-effect-sizes", "cito:agreesWith", "maria2026-happiness-income-spread",
     "Same move in a different literature: a disagreement presented as a disagreement about "
     "significance dissolves once the magnitudes and their intervals are shown side by side. "
     "In KKM 2023 the two 'complementary nonlinearities' swap significance depending on the "
     "standard-error estimator, which the paper does not name."),
    ("breznau2022-hidden-universe", "zoo:sharesUnstatedAssumptionWith",
     "maria2026-happiness-income-spread",
     "Both assume a specification multiverse is the right instrument for deciding whether a "
     "result is real. Sixteen income codings were run against KKM 2023 and 81% preserved the "
     "result; the finding that mattered came from a centre/spread decomposition instead. A "
     "multiverse measures fragility only to choices someone thought to vary."),
    ("maria2026-analytic-variability-reanalysis", "cito:usesMethodIn",
     "maria2026-happiness-income-spread",
     "Reciprocal: the same simulation-ladder discipline -- a negative control that must NOT "
     "produce the effect, then generators with the effect forced in -- carried from the "
     "many-analysts reanalysis into a quantile-regression setting."),
    ("maria2026-executability-denominators", "cito:extends",
     "maria2026-happiness-income-spread",
     "Reciprocal. The KKM 2023 deposit is the opposite end of the range this record measures: "
     "zero code, four columns, 739 kB, and complete reproduction of every printed number. "
     "Whether deposited code runs is the wrong question when the analysis is small enough to "
     "re-derive from the columns."),
    ("laurinavichyute2022-share-the-code", "cito:qualifies",
     "maria2026-happiness-income-spread",
     "Reciprocal of the mirror image. 'Sharing is not depositing' names a deposit that resolves "
     "and contains nothing; this one names a deposit that is complete for REPRODUCTION and "
     "incomplete for ADJUDICATION -- it settles every number the authors print and cannot "
     "settle the leading alternative explanation of their finding. Both pass every artifact "
     "badge in existence."),
    # ---- reciprocals of edges declared in kkm2023-conflict-resolved -----------
    ("breznau2022-hidden-universe", "zoo:sharesUnstatedAssumptionWith",
     "kkm2023-conflict-resolved",
     "Both treat 'the same data analysed differently gives different answers' as the problem. "
     "Breznau measures the dispersion and stops; KKM is the only case in this corpus where the "
     "disagreeing parties jointly reanalysed and produced a reconciling model. The shared "
     "unstated assumption is that a reconciliation exists at all."),
    ("mathur2023-effect-sizes", "cito:agreesWith", "kkm2023-conflict-resolved",
     "KKM volunteer the magnitude of their own headline -- r = 0.09, a few points on a "
     "100-point scale -- which is Mathur & VanderWeele's move against Breznau. They then do "
     "not apply it to their own Table 1, which is presented entirely as a "
     "significant/non-significant pattern."),
    # ---- edges proposed by kb.py suggest and accepted -------------------------
    ("maria2026-happiness-income-spread", "cito:agreesWith", "gamma2021-mpe92m#c2",
     "PROPOSED BY kb.py suggest, accepted. Same argument, different literature, no citation "
     "between them: 'the number of extractable factors is a resolution choice, not a property "
     "of the data' is structurally identical to 'the $100,000 threshold is the knot at which "
     "the estimator stops resolving a slope of about 0.55'. Both are reported boundaries that "
     "track the instrument's resolution rather than a feature of the world."),
    ("gamma2021-mpe92m", "cito:agreesWith", "maria2026-happiness-income-spread#c4",
     "Reciprocal of the above."),
    ("maria2026-happiness-income-spread", "zoo:sharesUnstatedAssumptionWith",
     "gamma2021-mpe92m#c6",
     "Both records confront a two-subpopulation explanation of a distributional feature and "
     "reach opposite verdicts about their own analysis. gamma2021#c6 is recorded "
     "not-identifiable because a two-subpopulation perturbation reproduces the observed "
     "deficit; here the two-subpopulation reading is the PAPER's and a one-parameter width "
     "change is not rejected against it. Neither dataset can separate the two, and in both "
     "cases the reason is the same: a cross-sectional design cannot see a subpopulation, only "
     "a shape."),
    ("gamma2021-mpe92m", "zoo:sharesUnstatedAssumptionWith",
     "maria2026-happiness-income-spread", "Reciprocal of the above."),
    ("menkveld2024-nonstandard-errors", "cito:usesMethodIn",
     "maria2026-happiness-income-spread",
     "PROPOSED BY kb.py suggest, accepted on the method rather than the substance: Menkveld et "
     "al. adopt the interquartile range as the dispersion measure precisely because the "
     "cross-analyst distribution is heavy-tailed, and this record uses the same robust "
     "dispersion logic on a within-sample rather than a cross-analyst distribution."),
    ("maria2026-happiness-income-spread", "cito:usesMethodIn",
     "menkveld2024-nonstandard-errors", "Reciprocal of the above."),
]


def main():
    for pid, typ, tgt, why in EDGES:
        p = os.path.join(HERE, pid, "paper.json")
        d = json.load(io.open(p, encoding="utf-8"))
        rels = d.setdefault("relations", [])
        if any(r["type"] == typ and r["target"] == tgt for r in rels):
            print("skip (exists)", pid, typ, tgt)
            continue
        rels.append({"type": typ, "target": tgt, "why": why})
        json.dump(d, io.open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        print("added", pid, "->", typ, tgt)


if __name__ == "__main__":
    main()
