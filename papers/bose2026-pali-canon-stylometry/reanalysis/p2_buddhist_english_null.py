"""p2 -- open question 1: separate 'monastic-law heritage' from 'Buddhist English'.

Bose 2026 reads the Mulasarvastivada Vinaya's overlap with the Theravada Vinaya (overlap coefficient 0.491 at 11,515 types;
Dharmaguptaka 0.816 at 2,282 types) as shared legal heritage. p1 showed English with NO Buddhist connection already reaches
0.31-0.34 (11,515) and 0.49-0.64 (2,282). The missing comparison is Buddhist English WITHOUT Vinaya: Sujato's sutta
translations (SuttaCentral, same project family, different translator), sampled to the same vocabulary sizes.

Reference sets, from bilara-data @ 10ad8c8 (CC0), same tokenizer and stop list as p1:
  BT  = Brahmali Vinaya, translation segments only (no notes)
  BTN = BT + Brahmali's notes (closest to the paper's PDF corpus, which carried them)
Sampling: files of the sutta corpus in random order (seed s), tokens read in order until the target type count is reached.
200 draws per size. Statistic: containment |S & B| / |S| (= the overlap coefficient whenever |S| <= |B|, as here).
Known-answer control: a sample drawn from BT itself must give containment 1.0 against BT, and against BTN.
Prediction (NOTES.md, written before running): Sujato @ 11,515 vs BTN in 0.50-0.60.

    PALI=<dir holding bilara/> python -I p2_buddhist_english_null.py
Author: maria, 2026-11-12.
"""
import glob
import json
import os
import random
import re
import statistics as st

ROOT = os.environ["PALI"]
TOK = re.compile(r"[A-Za-zÀ-ɏḀ-ỿ]+(?:'[A-Za-z]+)?")
STOP = set(list(dict.fromkeys(
    "the a an and or but if of to in on at by for with from as is are was were be been being this that these those it its he she "
    "they them his her their there here which who whom what when where why how not no so than then too very can will would should "
    "could may might must shall do does did have has had i you we me my your our us".split()))[:60])  # identical to p1


def toks(text):
    return [w for w in (t.lower() for t in TOK.findall(text)) if len(w) > 1 and "'" not in w and w not in STOP]


def corpus_tokens(pattern, strip_html=False):
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "bilara", pattern), recursive=True)):
        segs = json.load(open(f, encoding="utf-8")).values()
        out.append([w for s in segs for w in toks(re.sub(r"<[^>]+>", " ", s) if strip_html else s)])
    return out


bt_files = corpus_tokens("translation/en/brahmali/vinaya/**/*.json")
bc_files = corpus_tokens("comment/en/brahmali/vinaya/**/*.json", strip_html=True)
BT = {w for f in bt_files for w in f}
BTN = BT | {w for f in bc_files for w in f}
sutta_files = [f for f in corpus_tokens("translation/en/sujato/sutta/**/*.json") if f]
print(f"BT {len(BT)} types (p1: 7,418); BTN {len(BTN)} types (p1: 15,170); sutta files {len(sutta_files)}, "
      f"{sum(map(len, sutta_files))} tokens, {len({w for f in sutta_files for w in f})} types")


def sample(files, target, seed):
    order = list(range(len(files)))
    random.Random(seed).shuffle(order)
    S = set()
    for i in order:
        for w in files[i]:
            S.add(w)
            if len(S) >= target:
                return S
    return None


def main():
    res = {"BT_types": len(BT), "BTN_types": len(BTN), "draws": 200, "sizes": {}}
    # known-answer control
    for target in (2282, 7000):
        S = sample(bt_files, target, 0)
        c1, c2 = len(S & BT) / len(S), len(S & BTN) / len(S)
        assert c1 == 1.0 and c2 == 1.0, (target, c1, c2)
    print("control: BT samples are fully contained in BT and BTN (1.0, 1.0) at 2,282 and 7,000 types")
    for target in (2282, 11515):
        vals = {"BT": [], "BTN": []}
        for s in range(200):
            S = sample(sutta_files, target, s)
            vals["BT"].append(len(S & BT) / len(S))
            vals["BTN"].append(len(S & BTN) / len(S))
        res["sizes"][str(target)] = {k: {"mean": round(st.mean(v), 4), "p2.5": round(sorted(v)[4], 4), "p97.5": round(sorted(v)[194], 4)}
                                     for k, v in vals.items()}
        print(f"Sujato sutta @ {target:,} types: containment in BT {res['sizes'][str(target)]['BT']}, in BTN {res['sizes'][str(target)]['BTN']}")
    print("paper: Mulasarvastivada @ 11,515 types 0.491; Dharmaguptaka @ 2,282 types 0.816 (vs the PDF corpus WITH notes)")
    print("p1 (non-Buddhist English vs BTN): @ 11,515 0.31-0.34; @ 2,282 0.49-0.64")
    json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "p2_buddhist_english_null.json"), "w"), indent=1)



if __name__ == "__main__":
    main()
