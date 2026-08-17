"""Follow-up checks on analyze.py's results. Each one is a way the headline
could be wrong; run them before believing it.

1. Is the text-unicorn / palmyra-x-v3 pair identical on ALL items, not just
   the ones where both are wrong? (If yes: not "correlated", but the same model.)
2. Does controlling for item structure DESTROY the provenance signal or SHARPEN it?
   (Cohen's d and AUC for same_provider under each metric.)
3. Is the 93.8% robust to restricting to items where the item-null is well
   estimated (many other models also wrong)?
4. Does it hold per subject, or is it driven by one weird subject (moral_scenarios
   is notoriously degenerate)?
"""
import json, os, glob, itertools, collections
import numpy as np
import pandas as pd
from analyze import load, RAW, OUT, HERE

answers, correct, nopts, order_sig = load()
models = sorted({m for (m, _) in answers})
qkeys = sorted(correct)

# ---------- 1. the anomalous pair, on ALL items ----------
A, B = "google_text-unicorn@001", "writer_palmyra-x-v3"
both = [q for q in qkeys if answers.get((A, q)) is not None
        and answers.get((B, q)) is not None]
same = sum(answers[(A, q)] == answers[(B, q)] for q in both)
bw = [q for q in both if answers[(A, q)] != correct[q] and answers[(B, q)] != correct[q]]
print("=" * 70)
print("1. text-unicorn@001 vs palmyra-x-v3, ALL items")
print(f"   items both answered      : {len(both)}")
print(f"   identical answer         : {same}  ({same/len(both):.4%})")
print(f"   items where both wrong   : {len(bw)}")
print(f"   accuracy A={np.mean([answers[(A,q)]==correct[q] for q in both]):.4f} "
      f"B={np.mean([answers[(B,q)]==correct[q] for q in both]):.4f}")
# how does this compare to the next-most-identical pair overall?
ov = []
for m1, m2 in itertools.combinations(models, 2):
    qs = [q for q in qkeys if answers.get((m1, q)) is not None
          and answers.get((m2, q)) is not None]
    if len(qs) < 500:
        continue
    ov.append((sum(answers[(m1, q)] == answers[(m2, q)] for q in qs) / len(qs), m1, m2))
ov.sort(reverse=True)
print("   top-5 pairs by OVERALL identical-answer rate:")
for r, m1, m2 in ov[:5]:
    print(f"     {r:.4f}  {m1} | {m2}")

# ---------- 2. does the correction sharpen or destroy the provenance signal ----------
df = pd.read_csv(os.path.join(OUT, "pairs.csv"))
print("=" * 70)
print("2. discrimination of same-provider pairs, per metric")


def auc(pos, neg):
    n = 0
    for p in pos:
        n += sum(1 for q in neg if p > q) + 0.5 * sum(1 for q in neg if p == q)
    return n / (len(pos) * len(neg))


for metric in ["A_obs", "excess_vs_unif", "excess_vs_item"]:
    pos = df.loc[df.same_provider, metric].values
    neg = df.loc[~df.same_provider, metric].values
    d = (pos.mean() - neg.mean()) / np.sqrt(((pos.std(ddof=1) ** 2) + (neg.std(ddof=1) ** 2)) / 2)
    print(f"   {metric:>16s}: cohen_d={d:+.3f}  auc={auc(pos, neg):.3f}  "
          f"(n_same={len(pos)}, n_diff={len(neg)})")

# ---------- 3. robustness: restrict to well-estimated items ----------
print("=" * 70)
print("3. robustness of the 93.8% to minimum number of other-models-wrong")
wrong = {q: {m: answers[(m, q)] for m in models
             if answers.get((m, q)) is not None and answers[(m, q)] != correct[q]}
         for q in qkeys}
for minother in [2, 5, 8, 12, 15]:
    obs = unif = item = n = 0.0
    for m1, m2 in itertools.combinations(models, 2):
        for q in qkeys:
            w = wrong[q]
            if m1 not in w or m2 not in w:
                continue
            others = [a for mm, a in w.items() if mm not in (m1, m2)]
            if len(others) < minother:
                continue
            n += 1
            obs += (w[m1] == w[m2])
            unif += 1.0 / (nopts[q] - 1)
            c = collections.Counter(others); tot = len(others)
            item += sum(v * (v - 1) for v in c.values()) / (tot * (tot - 1))
    if n == 0:
        continue
    eu, ei = obs / n - unif / n, item / n - unif / n
    print(f"   >={minother:2d} other models wrong: N={int(n):7d}  A_obs={obs/n:.4f}  "
          f"A_item={item/n:.4f}  share explained by item structure = {ei/eu:6.1%}")

# ---------- 4. per subject ----------
print("=" * 70)
print("4. per subject (is it one degenerate subject?)")
subjects = sorted({q[0] for q in qkeys})
rows = []
for subj in subjects:
    sq = [q for q in qkeys if q[0] == subj]
    obs = unif = item = n = 0.0
    for m1, m2 in itertools.combinations(models, 2):
        for q in sq:
            w = wrong[q]
            if m1 not in w or m2 not in w:
                continue
            others = [a for mm, a in w.items() if mm not in (m1, m2)]
            if len(others) < 2:
                continue
            n += 1
            obs += (w[m1] == w[m2])
            unif += 1.0 / (nopts[q] - 1)
            c = collections.Counter(others); tot = len(others)
            item += sum(v * (v - 1) for v in c.values()) / (tot * (tot - 1))
    if n < 100:
        continue
    eu, ei = obs / n - unif / n, item / n - unif / n
    rows.append(dict(subject=subj, n_items=len(sq), N_pairitems=int(n),
                     A_obs=obs / n, A_item=item / n, share_item=ei / eu))
r = pd.DataFrame(rows).sort_values("share_item")
print(r.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
r.to_csv(os.path.join(OUT, "by_subject.csv"), index=False)
