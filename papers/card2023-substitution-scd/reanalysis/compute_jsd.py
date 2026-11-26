"""Step 3 (CPU): raw and rescaled JSD vs SemEval-2020 English graded gold. WRITTEN 2026-11-26 23:10, BEFORE any
substitute output existed (pre-registration of the readout; the GPU job was running).

    python papers/card2023-substitution-scd/reanalysis/compute_jsd.py > papers/card2023-substitution-scd/reanalysis/compute_jsd.out.txt

Per term and corpus: Counter of the top-5 substitutes over its mentions; JSD = scipy jensenshannon base 2 over the union
vocabulary (the repo's common/compute_jsd.py, i.e. the DISTANCE). Frequency = total aligned occurrences (both corpora).

Readouts (n = 37 targets, Spearman with truth/graded.txt):
 R0  raw JSD                                                    (the paper does not report it)
 R1  frequency quantile among background terms with freq in [f/2, 2f]  (the paper's scaled JSD, F = 2)
 R2  quantile among the 200 background terms nearest in (z log freq, z pooled substitute entropy)  (null conditioned on
     n AND diversity; the plug-in bias formula says both matter)
 R3  exploratory: excess divergence d^2 - (K-1)(1/n1+1/n2)/(8 ln 2), K = distinct substitute types of the pair,
     n = mentions per corpus (substitutes of one mention are not independent, so this is a rough correction)
 Also: Spearman(raw JSD, log freq) over background (the paper's Figure 1 top), and paired word-bootstrap CIs
 (4,000 draws) for R1 - R0 and R2 - R1.
Pre-stated reading: R1 - R0 > 0 with CI excluding 0 = 'the rescaling helps' reproduced; R2 - R1 CI excluding 0 = the
diversity term adds information. Comparison with the printed .547 is 'consistent' if within .1 (scale-downs: no MLM
fine-tuning, 2,000 mentions max, 2,000 background terms).
"""
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.spatial.distance import jensenshannon
from scipy.stats import spearmanr

KB = Path(__file__).resolve().parents[4]
ROOT = Path(subprocess.run([sys.executable, str(KB / "tools" / "assets.py"), "path",
                            "paper-downloads/card2023-substitution-scd"], capture_output=True, text=True,
                           check=True).stdout.strip())
W = ROOT / "work"
MODEL = sys.argv[1] if len(sys.argv) > 1 else "bert-large-uncased"


def entropy(c):
    v = np.array(list(c.values()), float); p = v / v.sum()
    return float(-(p * np.log2(p)).sum())


def main():
    ments = [json.loads(l) for l in open(W / "mentions.jsonl", encoding="utf-8")]
    sub_dir = W / f"subs_{MODEL}"
    chunks = sorted(sub_dir.glob("chunk_*.npy"))
    subs = np.concatenate([np.load(c) for c in chunks])
    assert len(subs) == len(ments), (len(subs), len(ments))
    assert (subs.sum(1) == 0).sum() == 0, "mentions without substitutes"
    info = json.load(open(W / "counts.json"))
    freq = {w: sum(v) for w, v in info["freq"].items()}
    tgt = info["targets"]  # lemma -> tagged target
    C = defaultdict(lambda: {1: Counter(), 2: Counter()}); N = defaultdict(lambda: {1: 0, 2: 0})
    for m, s in zip(ments, subs):
        C[m["term"]][m["corpus"]].update(s.tolist()); N[m["term"]][m["corpus"]] += 1
    raw, H, K, exc = {}, {}, {}, {}
    for w, c in C.items():
        voc = sorted(set(c[1]) | set(c[2]))
        p = np.array([c[1][v] for v in voc], float); q = np.array([c[2][v] for v in voc], float)
        raw[w] = float(jensenshannon(p / p.sum(), q / q.sum(), base=2))
        H[w] = entropy(c[1] + c[2]); K[w] = len(voc)
        e0 = (K[w] - 1) * (1 / N[w][1] + 1 / N[w][2]) / (8 * np.log(2))
        exc[w] = raw[w] ** 2 - e0
    bg = [w for w in C if w not in tgt]
    gold = {l.split("\t")[0].rsplit("_", 1)[0]: float(l.split("\t")[1]) for l in
            open(ROOT / "corpus" / "semeval2020_ulscd_eng" / "truth" / "graded.txt", encoding="utf-8") if l.strip()}
    T = sorted(tgt)
    lf = {w: np.log(freq[w]) for w in C}
    mu = np.array([[lf[w], H[w]] for w in bg]); m0, s0 = mu.mean(0), mu.std(0)

    def r1(w):
        near = [b for b in bg if freq[w] / 2 <= freq[b] <= freq[w] * 2]
        return float(np.mean([raw[w] >= raw[b] for b in near])) if near else np.nan, len(near)

    def r2(w):
        z = (np.array([lf[w], H[w]]) - m0) / s0
        d = (((mu - m0) / s0 - z) ** 2).sum(1)
        near = [bg[i] for i in np.argsort(d)[:200]]
        return float(np.mean([raw[w] >= raw[b] for b in near]))

    R = {"R0_raw": [raw[w] for w in T], "R1_freq_quantile": [r1(w)[0] for w in T],
         "R2_freq_entropy_quantile": [r2(w) for w in T], "R3_excess": [exc[w] for w in T]}
    g = np.array([gold[w] for w in T])
    print(f"model {MODEL}; targets {len(T)}; background {len(bg)}; median background terms in the F=2 window "
          f"{int(np.median([r1(w)[1] for w in T]))}")
    print(f"Figure 1 check: Spearman(raw JSD, log freq) over background = {spearmanr([raw[w] for w in bg], [lf[w] for w in bg])[0]:.3f}; "
          f"Spearman(raw JSD, pooled entropy) = {spearmanr([raw[w] for w in bg], [H[w] for w in bg])[0]:.3f}")
    for k, v in R.items():
        print(f"{k:28s} Spearman with gold = {spearmanr(v, g)[0]:.3f}")
    rng = np.random.default_rng(0)
    A = {k: np.array(v) for k, v in R.items()}
    for x, y in (("R1_freq_quantile", "R0_raw"), ("R2_freq_entropy_quantile", "R1_freq_quantile"), ("R3_excess", "R0_raw")):
        diffs = []
        for _ in range(4000):
            i = rng.integers(0, len(T), len(T))
            diffs.append(spearmanr(A[x][i], g[i])[0] - spearmanr(A[y][i], g[i])[0])
        lo, hi = np.nanpercentile(diffs, [2.5, 97.5])
        print(f"{x} - {y}: {spearmanr(A[x], g)[0] - spearmanr(A[y], g)[0]:+.3f} [{lo:+.3f}, {hi:+.3f}]")
    print("per target: word gold raw R1 R2 freq K")
    for j, w in enumerate(T):
        print(f"  {w:14s} {gold[w]:.3f} {raw[w]:.3f} {R['R1_freq_quantile'][j]:.2f} {R['R2_freq_entropy_quantile'][j]:.2f} {freq[w]} {K[w]}")
    print("COMPUTE_JSD_OK")


if __name__ == "__main__":
    main()
