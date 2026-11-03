"""Reproduce saponara2026 Table 2 (Spearman of PRT / APD / cluster-JSD vs gold JSD, first period vs each later one)
on a 300-lemma random sample (seed 0) of the deposited synthetic data, with XL-LEXEME fp16 embeddings.

    <python with numpy/scipy/sklearn> r01_table2_on_300_lemmas.py <synthetic unzipped dir> <task-format gold dir EN> <emb dir> [out.json]

Gold, as in the paper's Section 3.4 / 5.2: q_i(t) = z_i(t) / sum_j z_j(t), z = log2(masked freq + 1), freq masked to 0
outside the sense's OED interval [start, end]; NO log for 2-sense lemmas (footnote 3). Delta_gold(t_r) = JSD(q(t1), q(t_r)).
The paper says "JSD"; scipy's jensenshannon returns the DISTANCE (sqrt). Spearman is rank-based, and sqrt is monotone,
so the choice does not change any correlation here (both computed to show it).
A second gold is computed from the deposited sentences' own sense counts (what a system actually sees).
Embeddings come from arena-lsc (tooling/embed.py, XL-LEXEME, target marked, mean pooling, fp16).
"""
import glob
import json
import math
import os
import sys
from collections import Counter, defaultdict

import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import jensenshannon
from scipy.stats import spearmanr

SYN, GOLD, EMB = sys.argv[1], sys.argv[2], sys.argv[3]
OUT = sys.argv[4] if len(sys.argv) > 4 else None
BINS = list(range(1810, 1991, 20))


def safe(word):
    import hashlib
    return "".join(c if c.isalnum() else "_" for c in word)[:40] + "_" + hashlib.sha1(word.encode()).hexdigest()[:8]


usages = defaultdict(list)
for l in open(os.path.join(GOLD, "usages.jsonl"), encoding="utf-8"):
    u = json.loads(l)
    usages[u["word"]].append(u)
labels = {}
for l in open(os.path.join(GOLD, "subtask1.jsonl"), encoding="utf-8"):
    r = json.loads(l)
    labels[(r["word"], r["sentence_id"])] = r["label"][0]

meta_files = {}
for f in glob.glob(os.path.join(SYN, "metadata", "*_senses", "*.json")):
    meta_files.setdefault(os.path.splitext(os.path.basename(f))[0], []).append(f)


def gold_q(lemma):
    fs = meta_files.get(lemma, [])
    if len(fs) != 1:
        return None
    m = json.load(open(fs[0], encoding="utf-8"))
    k = len(m)
    Z = []
    for sid, s in m.items():
        z = []
        for b in BINS:
            st, en = s["start"], s["end"] if s["end"] is not None else 9999
            att = (st <= b + 19) and (en >= b)
            x = s["frequencies"].get(str(b), 0) if att else 0
            z.append(x if k == 2 else math.log2(x + 1))
        Z.append(z)
    Z = np.array(Z, dtype=float)
    tot = Z.sum(0)
    return {b: (Z[:, i] / tot[i] if tot[i] > 0 else None) for i, b in enumerate(BINS)}


def jsd(p, q):
    return float(jensenshannon(p, q, base=2.0))


rows = []
for lemma, us in usages.items():
    X = np.load(os.path.join(EMB, safe(lemma) + ".npy"))
    ids = json.load(open(os.path.join(EMB, safe(lemma) + ".ids.json"), encoding="utf-8"))["ids"]
    pos = {s: i for i, s in enumerate(ids)}
    per = defaultdict(list)
    for u in us:
        per[int(u["period_label"][:4])].append(pos[u["sentence_id"]])
    q = gold_q(lemma)
    Zs = {t: linkage(X, method=m, metric="cosine") for t, m in [("avg", "average")]}
    cl = {th: fcluster(Zs["avg"], t=th, criterion="distance") for th in (0.32, 0.50)}
    first = min(per)
    for b in sorted(per):
        if b == first:
            continue
        A, B = X[per[first]], X[per[b]]
        ca, cb = A.mean(0), B.mean(0)
        prt = 1 - ca @ cb / (np.linalg.norm(ca) * np.linalg.norm(cb))
        apd = float(np.mean(1 - A @ B.T))
        r = {"lemma": lemma, "first": first, "t": b, "PRT": float(prt), "APD": apd}
        for th, lab in cl.items():
            la, lb = Counter(lab[per[first]]), Counter(lab[per[b]])
            keys = sorted(set(la) | set(lb))
            r[f"JSD{th}"] = jsd([la[k] / len(per[first]) for k in keys], [lb[k] / len(per[b]) for k in keys])
        sa = Counter(labels[(lemma, us_[ "sentence_id"])] for us_ in us if int(us_["period_label"][:4]) == first)
        sb = Counter(labels[(lemma, us_["sentence_id"])] for us_ in us if int(us_["period_label"][:4]) == b)
        keys = sorted(set(sa) | set(sb))
        r["gold_empirical"] = jsd([sa[k] / sum(sa.values()) for k in keys], [sb[k] / sum(sb.values()) for k in keys])
        if q is not None and q.get(first) is not None and q.get(b) is not None:
            r["gold_q_dist"] = jsd(q[first], q[b])
            r["gold_q_div"] = r["gold_q_dist"] ** 2
        rows.append(r)

out = {"n_lemmas": len(usages), "by_period": {}, "avg": {}}
metrics = ["PRT", "APD", "JSD0.32", "JSD0.5"]
for gname in ["gold_q_dist", "gold_q_div", "gold_empirical"]:
    acc = defaultdict(list)
    for b in BINS[1:]:
        rs = [r for r in rows if r["t"] == b and r["first"] == 1810 and gname in r]
        if len(rs) < 10:
            continue
        for mname in metrics:
            rho = spearmanr([r[gname] for r in rs], [r[mname] for r in rs])[0]
            out["by_period"].setdefault(gname, {}).setdefault(mname, {})[b] = (round(float(rho), 3), len(rs))
            acc[mname].append(rho)
    out["avg"][gname] = {m: round(float(np.mean(v)), 3) for m, v in acc.items()}
print(json.dumps(out["avg"], indent=1))
for gname in out["by_period"]:
    print(gname)
    for m in metrics:
        print("  ", m, " ".join(f"{b}:{v[0]:+.3f}(n{v[1]})" for b, v in sorted(out["by_period"][gname][m].items())))
if OUT:
    json.dump(out, open(OUT, "w"), indent=1)
