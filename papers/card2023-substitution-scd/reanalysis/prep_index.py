"""Step 1 of the reduced-scale reproduction of card2023 (SemEval-2020 English): align lemma/token lines, index
targets and random background lemmas, sample mentions. CPU only.

    python papers/card2023-substitution-scd/reanalysis/prep_index.py --max-per-term 2000 --n-background 2000

Simplifications vs the paper (stated in NOTES before running):
- Alignment: a line is used only if, after dropping punctuation-only tokens, the token line and the lemma line have the
  same number of tokens; then position i of one is position i of the other. (Paper: landmark + Levenshtein alignment.)
  Kept the paper's filters: raw token >= 2 chars and same first letter as the lemma.
- Target POS tags (_nn, _vb) ignored, as in the paper.
- Background: n random lemmas (alphabetic, >= 2 chars, not a stopword, count >= 20 in each corpus); paper: 10,000.
- Mentions: up to --max-per-term per term in total, split in proportion to the two corpora's counts (paper: 4,000).
Output: mentions.jsonl (term, corpus, line, pos), counts.json, stats printed.
"""
import argparse
import gzip
import json
import random
import string
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

KB = Path(__file__).resolve().parents[4]
ROOT = Path(subprocess.run([sys.executable, str(KB / "tools" / "assets.py"), "path",
                            "paper-downloads/card2023-substitution-scd"], capture_output=True, text=True,
                           check=True).stdout.strip())
C = ROOT / "corpus" / "semeval2020_ulscd_eng"
OUT = ROOT / "work"
PUNCT = set(string.punctuation) | {"``", "''", "--", "..."}


def is_punct(t):
    return all(ch in PUNCT for ch in t)


def load(corpus):
    lem = gzip.open(C / f"corpus{corpus}" / "lemma" / f"ccoha{corpus}.txt.gz", "rt", encoding="utf-8").read().splitlines()
    tok = gzip.open(C / f"corpus{corpus}" / "token" / f"ccoha{corpus}.txt.gz", "rt", encoding="utf-8").read().splitlines()
    assert len(lem) == len(tok), (len(lem), len(tok))
    return lem, tok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-per-term", type=int, default=2000)
    ap.add_argument("--n-background", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    stop = set((KB / "instance-papers" / "papers" / "card2023-substitution-scd" / "reanalysis" / "stopwords_snowball_en.txt")
               .read_text(encoding="utf-8").split())
    targets = [l.split("\t")[0].strip() for l in open(C / "truth" / "graded.txt", encoding="utf-8") if l.strip()]
    tlem = {t.rsplit("_", 1)[0]: t for t in targets}
    occ = defaultdict(lambda: defaultdict(list))  # lemma -> corpus -> [(line, pos_in_token_line)]
    counts = {1: Counter(), 2: Counter()}
    aligned = {}
    for corpus in (1, 2):
        lem, tok = load(corpus)
        ok = 0
        for i, (l, t) in enumerate(zip(lem, tok)):
            ls = l.split(); ts = t.split()
            tpos = [j for j, w in enumerate(ts) if not is_punct(w)]
            ls_np = [w for w in ls if not is_punct(w)]
            if len(ls_np) != len(tpos):
                continue
            ok += 1
            for k, w in enumerate(ls_np):
                if w.endswith(("_nn", "_vb")):  # targets carry their POS tag in the lemma corpus; the paper ignores POS
                    w = w[:-3]
                raw = ts[tpos[k]]
                counts[corpus][w] += 1
                if len(raw) < 2 or raw[0].lower() != w[0].lower():
                    continue
                occ[w][corpus].append((i, tpos[k]))
        aligned[corpus] = (ok, len(lem))
        print(f"corpus{corpus}: {ok}/{len(lem)} lines aligned ({ok/len(lem):.1%})", flush=True)
    rng = random.Random(a.seed)
    pool = [w for w in counts[1] if w.isalpha() and len(w) >= 2 and w not in stop and w not in tlem
            and len(occ[w][1]) >= 20 and len(occ[w][2]) >= 20]
    bg = rng.sample(sorted(pool), min(a.n_background, len(pool)))
    terms = list(tlem) + bg
    n_m = 0
    with open(OUT / "mentions.jsonl", "w", encoding="utf-8") as f:
        for w in terms:
            c1, c2 = len(occ[w][1]), len(occ[w][2])
            tot = c1 + c2
            k1 = min(c1, round(a.max_per_term * c1 / tot)) if tot > a.max_per_term else c1
            k2 = min(c2, round(a.max_per_term * c2 / tot)) if tot > a.max_per_term else c2
            for corpus, k in ((1, k1), (2, k2)):
                for (line, pos) in rng.sample(occ[w][corpus], k):
                    f.write(json.dumps({"term": w, "target": w in tlem, "corpus": corpus, "line": line, "pos": pos}) + "\n")
                    n_m += 1
    json.dump({"freq": {w: [len(occ[w][1]), len(occ[w][2])] for w in terms}, "targets": tlem,
               "aligned": aligned, "args": vars(a)}, open(OUT / "counts.json", "w"), indent=0)
    miss = [t for t in tlem if len(occ[t][1]) + len(occ[t][2]) == 0]
    print(f"targets {len(tlem)} (none found: {miss}); background {len(bg)} from pool {len(pool)}; mentions {n_m}")
    tf = sorted(len(occ[t][1]) + len(occ[t][2]) for t in tlem)
    print(f"target total counts min/median/max {tf[0]}/{tf[len(tf)//2]}/{tf[-1]}")
    print("PREP_OK")


if __name__ == "__main__":
    main()
