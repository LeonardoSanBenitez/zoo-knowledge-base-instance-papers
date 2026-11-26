"""How much of APD's graded-change correlation on DWUG is period-blind (polysemy / dispersion)?

    python period_blind.py --set NAME GOLD_SUBTASK1_JSONL EMB_DIR [--set ...] --out period_blind.json

Per word: gold = JSD(base 2) of the two periods' gold sense distributions; APD (cross-period mean cosine distance);
DISP = mean cosine distance over ALL usage pairs of the word, periods ignored; K = number of gold senses;
EXCESS = APD - DISP. Spearman of each with gold, and partial Spearman of APD given DISP (rank residuals).
Paired word bootstrap (2000, seed 0) of rho(APD) - rho(DISP).
"""
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.spatial.distance import cdist, jensenshannon
from scipy.stats import rankdata, spearmanr

from amd_check import safe


def rows_for(gold_path, emb_dir):
    by = defaultdict(list)
    for l in open(gold_path, encoding="utf-8"):
        r = json.loads(l); by[r["word"]].append(r)
    out = {}
    for w, rs in by.items():
        periods = sorted({r["period_label"] for r in rs})
        if len(periods) != 2:
            continue
        ids = json.load(open(Path(emb_dir) / f"{safe(w)}.ids.json", encoding="utf-8"))
        X = np.load(Path(emb_dir) / f"{safe(w)}.npy").astype(np.float64)
        pos = {s: i for i, s in enumerate(ids["ids"])}
        rs = [r for r in rs if r["sentence_id"] in pos]
        dist = [Counter(r["label"][0] for r in rs if r["period_label"] == p) for p in periods]
        senses = sorted(set(dist[0]) | set(dist[1]))
        P = np.array([[d[s] for s in senses] for d in dist], dtype=float); P = P / P.sum(1, keepdims=True)
        gold = float(jensenshannon(P[0], P[1], base=2)) if len(senses) > 1 else 0.0
        Xw = X[[pos[r["sentence_id"]] for r in rs]]
        ma = np.array([r["period_label"] == periods[0] for r in rs])
        D = cdist(Xw, Xw, "cosine")
        iu = np.triu_indices(len(Xw), 1)
        out[w] = {"gold": gold, "APD": float(D[np.ix_(ma, ~ma)].mean()), "DISP": float(D[iu].mean()), "K": len(senses)}
        out[w]["EXCESS"] = out[w]["APD"] - out[w]["DISP"]
    return out


def rho(rows, ws, k):
    return float(spearmanr([rows[w]["gold"] for w in ws], [rows[w][k] for w in ws])[0])


def partial(rows, ws, k, ctrl):
    g, x, c = (rankdata([rows[w][key] for w in ws]) for key in ("gold", k, ctrl))
    rg = g - np.polyval(np.polyfit(c, g, 1), c); rx = x - np.polyval(np.polyfit(c, x, 1), c)
    return float(np.corrcoef(rg, rx)[0, 1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", nargs=3, action="append", metavar=("NAME", "GOLD", "EMB"), required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = {}
    for name, g, e in a.set:
        rows = rows_for(g, e); ws = sorted(rows)
        r = {"n_words": len(ws), **{f"rho_{k}": rho(rows, ws, k) for k in ("APD", "DISP", "K", "EXCESS")},
             "partial_APD_given_DISP": partial(rows, ws, "APD", "DISP")}
        rng = np.random.default_rng(0); d = []
        for _ in range(2000):
            pick = [ws[i] for i in rng.integers(0, len(ws), len(ws))]
            d.append(rho(rows, pick, "APD") - rho(rows, pick, "DISP"))
        r["APD_minus_DISP_ci95"] = [float(x) for x in np.nanpercentile(d, [2.5, 97.5])]
        res[name] = r
        print(name, json.dumps(r), flush=True)
    json.dump(res, open(a.out, "w"), indent=1)
    print("PERIOD_BLIND_OK")


if __name__ == "__main__":
    main()
