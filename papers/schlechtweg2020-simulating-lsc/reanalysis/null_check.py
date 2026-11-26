"""How much of the SemCor-LSC graded gold is sampling noise? (maria, 2026-11-26 night)

    python papers/schlechtweg2020-simulating-lsc/reanalysis/null_check.py > papers/schlechtweg2020-simulating-lsc/reanalysis/null_check.out.txt

Data: semcor_lsc.zip (IMS), testset/testset.tsv: per lemma the sense frequency distributions T1, T2 in the two halves,
poly, freq, graded (= JS distance base 2 of T1, T2), binary. Per the paper (Sec. 3.3), non-target lemmas were split by a
random half-split of sentences, so their 'change' is pure sampling noise; target lemmas (frequency 100-1000) got senses
pushed to one side. The paper does not release which lemmas were targets.
Checks:
 (0) reproduce graded from T1, T2 (known answer: the file's own number);
 (1) per lemma, a no-change permutation null (pool T1 + T2 uses, re-split at the same sizes, 500 draws) and the
     chi-square expectation (instance-general statistics/divergence-between-small-samples-under-no-change.md);
     count lemmas whose gold exceeds its own null 95th percentile;
 (2) Spearman of gold with the null expectation, with poly (the paper's polysemy baseline), and within the lemmas that
     do NOT exceed their null (the noise-only part of the gold).
"""
import ast
import csv
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.spatial.distance import jensenshannon
from scipy.special import gammaln
from scipy.stats import spearmanr

KB = Path(__file__).resolve().parents[4]
ROOT = Path(subprocess.run([sys.executable, str(KB / "tools" / "assets.py"), "path",
                            "paper-downloads/schlechtweg2020-simulating-lsc"], capture_output=True, text=True,
                           check=True).stdout.strip())
rows = list(csv.DictReader(open(ROOT / "data/semcor_lsc/testset/testset.tsv", encoding="utf-8"), delimiter="\t"))
rng = np.random.default_rng(0)


def jsd(a, b):
    return float(jensenshannon(a / a.sum(), b / b.sum(), base=2))


def e_d0(n1, n2, k):
    if k < 2:
        return 0.0
    N = n1 + n2
    return math.sqrt((1 / n1 + 1 / n2) / (8 * math.log(2)) * N / (N - 1)) * math.sqrt(2) * math.exp(gammaln(k / 2) - gammaln((k - 1) / 2))


g, nm, an, poly, above, maxerr, big = [], [], [], [], [], 0.0, []
for r in rows:
    t1 = np.array(ast.literal_eval(r["T1"]), float); t2 = np.array(ast.literal_eval(r["T2"]), float)
    gold = float(r["graded"]); maxerr = max(maxerr, abs(jsd(t1, t2) - gold))
    labels = np.repeat(np.arange(len(t1)), (t1 + t2).astype(int)); n1 = int(t1.sum())
    nulls = []
    for _ in range(500):
        p = rng.permutation(labels)
        nulls.append(jsd(np.bincount(p[:n1], minlength=len(t1)).astype(float), np.bincount(p[n1:], minlength=len(t1)).astype(float)))
    k = int(((t1 + t2) > 0).sum())
    g.append(gold); nm.append(np.mean(nulls)); an.append(e_d0(n1, int(t2.sum()), k)); poly.append(int(r["poly"]))
    above.append(gold > np.percentile(nulls, 95)); big.append(min(t1.sum(), t2.sum()))
g, nm, an, poly, above = map(np.array, (g, nm, an, poly, above))
print(f"(0) graded recomputed from T1/T2: max abs error {maxerr:.2e} over {len(rows)} lemmas")
print(f"(1) lemmas above their own no-change 95th pct: {above.sum()}/{len(g)} ({above.mean():.1%}); 5% expected if nothing changed")
print(f"    annotated uses per half: min {int(min(big))}, median {int(np.median(big))}")
print(f"    mean gold {g.mean():.3f}; mean null {nm.mean():.3f}; formula vs permutation mean: Spearman {spearmanr(an, nm)[0]:.3f}, ratio {an.mean()/nm.mean():.3f}")
print(f"(2) Spearman(gold, null mean) = {spearmanr(g, nm)[0]:.3f}; Spearman(gold, formula) = {spearmanr(g, an)[0]:.3f}; Spearman(gold, poly) = {spearmanr(g, poly)[0]:.3f}")
print(f"    within the {int((~above).sum())} lemmas NOT above their null: Spearman(gold, null mean) = {spearmanr(g[~above], nm[~above])[0]:.3f}")
print(f"    within the {int(above.sum())} lemmas above: Spearman(gold, null mean) = {spearmanr(g[above], nm[above])[0]:.3f}; mean gold {g[above].mean():.3f}")
print("NULL_CHECK_OK")
