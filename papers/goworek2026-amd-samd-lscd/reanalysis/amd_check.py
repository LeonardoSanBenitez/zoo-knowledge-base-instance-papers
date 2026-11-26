"""Independent check of goworek2026 (AMD/SAMD vs APD/PRT) on DWUG EN/DE/SV with XL-LEXEME usage embeddings.

    python amd_check.py --set NAME GOLD_SUBTASK1_JSONL EMB_DIR [--set ...] --out result.json

GOLD: one JSON line per usage {"word", "period_label", "sentence_id", "label": [int]} with exactly two periods per word
(DWUG converted to the SemEval-2027 Task 3 format). Graded gold = JSD (base 2) between the two periods' label distributions.
EMB_DIR: <safe(word)>.npy + <safe(word)>.ids.json ({"word", "ids"}) per word.
Metrics as defined in the paper (Sec. 3.2), cosine distance: APD, PRT, AMD (symmetric mean of directional nearest-neighbour
distances), SAMD (equal-size random subsample, seed 0, greedy one-to-one matching). Spaces: FULL and per-word PCA with K
components (K = 4, close to the paper's mean number of definitions for DE/SV; the paper sets K per word).
Uncertainty: Spearman per set, paired word bootstrap (2000, seed 0) of metric minus APD.
Control: period labels permuted within word (gold unchanged) -> every metric's Spearman should be near 0.
"""
import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.spatial.distance import cdist, jensenshannon
from scipy.stats import spearmanr


def safe(word):
    h = hashlib.sha1(word.encode("utf-8")).hexdigest()[:8]
    keep = "".join(c if c.isalnum() else "_" for c in word)[:40]
    return f"{keep}_{h}"


def metrics(A, B, rng):
    D = cdist(A, B, "cosine")
    out = {"APD": float(D.mean()),
           "PRT": float(cdist(A.mean(0, keepdims=True), B.mean(0, keepdims=True), "cosine")[0, 0]),
           "AMD": float((D.min(1).mean() + D.min(0).mean()) / 2)}
    n = min(len(A), len(B))
    ia = rng.choice(len(A), n, replace=False); ib = rng.choice(len(B), n, replace=False)
    S = D[np.ix_(ia, ib)].copy(); tot = 0.0
    for _ in range(n):
        i, j = np.unravel_index(np.argmin(S), S.shape)
        tot += S[i, j]; S[i, :] = np.inf; S[:, j] = np.inf
    out["SAMD"] = float(tot / n)
    return out


def pca(X, k):
    Xc = X - X.mean(0)
    _, _, vt = np.linalg.svd(Xc, full_matrices=False)
    return Xc @ vt[:k].T


def one_set(gold_path, emb_dir, shuffle=False, k=4):
    by = defaultdict(list)
    for l in open(gold_path, encoding="utf-8"):
        r = json.loads(l); by[r["word"]].append(r)
    rng = np.random.default_rng(0)
    rows = {}
    for w, rs in by.items():
        periods = sorted({r["period_label"] for r in rs})
        if len(periods) != 2:
            continue
        ids = json.load(open(Path(emb_dir) / f"{safe(w)}.ids.json", encoding="utf-8"))
        assert ids["word"] == w
        X = np.load(Path(emb_dir) / f"{safe(w)}.npy").astype(np.float64)
        pos = {s: i for i, s in enumerate(ids["ids"])}
        rs = [r for r in rs if r["sentence_id"] in pos]
        lab = [r["period_label"] for r in rs]
        if shuffle:
            lab = list(rng.permutation(lab))
        dist = []
        for p in periods:
            c = Counter(r["label"][0] for r, q in zip(rs, lab) if q == p)
            dist.append(c)
        senses = sorted(set(dist[0]) | set(dist[1]))
        P = np.array([[d[s] for s in senses] for d in dist], dtype=float)
        P = P / P.sum(1, keepdims=True)
        gold = float(jensenshannon(P[0], P[1], base=2)) if len(senses) > 1 else 0.0
        if shuffle:   # gold must stay the TRUE change; recompute it from the true period labels
            dist = [Counter(r["label"][0] for r in rs if r["period_label"] == p) for p in periods]
            senses = sorted(set(dist[0]) | set(dist[1]))
            P = np.array([[d[s] for s in senses] for d in dist], dtype=float); P = P / P.sum(1, keepdims=True)
            gold = float(jensenshannon(P[0], P[1], base=2)) if len(senses) > 1 else 0.0
        Xw = X[[pos[r["sentence_id"]] for r in rs]]
        ma = np.array([q == periods[0] for q in lab])
        full = metrics(Xw[ma], Xw[~ma], rng)
        Z = pca(Xw, k)
        red = metrics(Z[ma], Z[~ma], rng)
        rows[w] = {"gold": gold, "n": len(rs), **{f"{m}_FULL": v for m, v in full.items()}, **{f"{m}_PCA{k}": v for m, v in red.items()}}
    return rows


def spear(rows, words, key):
    return float(spearmanr([rows[w]["gold"] for w in words], [rows[w][key] for w in words])[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", nargs=3, action="append", metavar=("NAME", "GOLD", "EMB"), required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = {}
    for name, g, e in a.set:
        rows = one_set(g, e)
        ctrl = one_set(g, e, shuffle=True)
        words = sorted(rows)
        keys = [k for k in rows[words[0]] if k not in ("gold", "n")]
        r = {"n_words": len(words), "spearman": {k: spear(rows, words, k) for k in keys},
             "control_shuffled_periods": {k: spear(ctrl, words, k) for k in keys}}
        rng = np.random.default_rng(0); boots = defaultdict(list)
        for _ in range(2000):
            pick = [words[i] for i in rng.integers(0, len(words), len(words))]
            for sp in ("FULL", "PCA4"):
                base = spear(rows, pick, f"APD_{sp}")
                for m in ("PRT", "AMD", "SAMD"):
                    boots[f"{m}-APD_{sp}"].append(spear(rows, pick, f"{m}_{sp}") - base)
        r["diff_vs_APD_ci95"] = {k: [float(x) for x in np.nanpercentile(v, [2.5, 97.5])] for k, v in boots.items()}
        res[name] = r
        print(name, json.dumps(r), flush=True)
    json.dump(res, open(a.out, "w"), indent=1)
    print("AMD_CHECK_OK")


if __name__ == "__main__":
    main()
