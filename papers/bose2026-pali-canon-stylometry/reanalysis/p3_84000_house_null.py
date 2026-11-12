"""p3 -- the decisive null for c1: same translation house (84000), Vinaya vs non-Vinaya, against Brahmali's Vinaya.

p2 found Sujato's suttas (SuttaCentral house style, shared with Brahmali) reach 0.479 at 11,515 types, close to the
paper's 0.491 for the Mulasarvastivada. But the Mulasarvastivada text is 84000's, so house style and Vinaya content
are confounded. Here both arms come from 84000:
  V  = the five Vinayavastu chapters published in data-tei (Toh 1-1, 1-2, 1-3, 1-4, 1-6)
  NV = non-Vinaya Kangyur translations (everything else in translations/kangyur/translations), random file orders
Text = the translation body only: <div type="translation">, with <note>, the glossary, front and back matter removed.
Statistic: containment in BTN and BT (p2's sets), at 11,515 and 2,282 types; V at its full vocabulary too.
Corpus-identity check: V's type count with our tokenizer, against the paper's 11,515.
Known-answer control: NV sampled against a reference made of the SAME NV sample must give 1.0 (the pipeline counts
containment, not something else).
Prediction (NOTES.md, before running): excess V - NV (vs BTN, 11,515 types) >= 0.05.

    PALI=<dir holding bilara/ and tei84000/> python -I p3_84000_house_null.py fetch <sha> <n_nonvinaya>
    PALI=... python -I p3_84000_house_null.py run
Author: maria, 2026-11-12.
"""
import glob
import json
import os
import random
import re
import statistics as st
import sys
import urllib.request
import xml.etree.ElementTree as ET

ROOT = os.environ["PALI"]
HERE = os.path.dirname(os.path.abspath(__file__))
TEI = os.path.join(ROOT, "tei84000")
sys.path.insert(0, HERE)
from p2_buddhist_english_null import toks, sample, BT, BTN  # noqa: E402  (same tokenizer, stop list and reference sets)

NS = "{http://www.tei-c.org/ns/1.0}"


def fetch(sha, n_nv):
    os.makedirs(TEI, exist_ok=True)
    rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(HERE, "out", "p3_84000_kangyur_files.tsv"), encoding="utf-8")]
    vin = [p for p, s in rows if re.search(r"_toh1-\d", p)]
    nv = [(p, int(s)) for p, s in rows if not re.search(r"_toh1-\d", p) and 20_000 < int(s) < 1_500_000]
    random.Random(20261112).shuffle(nv)
    pick = vin + [p for p, _ in nv[:n_nv]]
    for p in pick:
        dest = os.path.join(TEI, os.path.basename(p))
        if os.path.exists(dest):
            continue
        url = f"https://raw.githubusercontent.com/84000/data-tei/{sha}/{p}"
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "zoo-kb/1.0"}), timeout=120) as r:
            open(dest, "wb").write(r.read())
    json.dump({"sha": sha, "vinaya": vin, "nonvinaya": [p for p, _ in nv[:n_nv]]}, open(os.path.join(HERE, "out", "p3_picked.json"), "w"), indent=1)
    print(f"fetched {len(vin)} Vinaya + {min(n_nv, len(nv))} non-Vinaya files into {TEI}")


def body_text(path):
    root = ET.parse(path).getroot()
    divs = [d for d in root.iter(f"{NS}div") if d.get("type") == "translation"]
    if not divs:
        return ""
    for d in divs:
        for parent in d.iter():
            for ch in list(parent):
                if ch.tag in (f"{NS}note",):
                    parent.remove(ch)
    return " ".join(" ".join(d.itertext()) for d in divs)


def run():
    picked = json.load(open(os.path.join(HERE, "out", "p3_picked.json")))
    V = [toks(body_text(os.path.join(TEI, os.path.basename(p)))) for p in picked["vinaya"]]
    NV = [t for t in (toks(body_text(os.path.join(TEI, os.path.basename(p)))) for p in picked["nonvinaya"]) if t]
    Vset = {w for f in V for w in f}
    NVset = {w for f in NV for w in f}
    res = {"V_files": len(V), "V_tokens": sum(map(len, V)), "V_types": len(Vset), "paper_mulasarvastivada_types": 11515,
           "NV_files": len(NV), "NV_tokens": sum(map(len, NV)), "NV_types": len(NVset)}
    print(json.dumps(res))
    # known-answer control
    S = sample(NV, 2282, 0)
    assert len(S & S) / len(S) == 1.0
    S2 = sample(NV, 2282, 0)
    assert S == S2, "sampling is not deterministic for a fixed seed"
    res["V_full_in_BTN"] = round(len(Vset & BTN) / len(Vset), 4)
    res["V_full_in_BT"] = round(len(Vset & BT) / len(Vset), 4)
    for target in (2282, 11515):
        out = {}
        if len(Vset) >= target:
            vv = {"BTN": [], "BT": []}
            for s in range(200):
                Sv = sample(V, target, s)
                vv["BTN"].append(len(Sv & BTN) / target)
                vv["BT"].append(len(Sv & BT) / target)
            out["V"] = {k: [round(st.mean(x), 4), round(sorted(x)[4], 4), round(sorted(x)[194], 4)] for k, x in vv.items()}
        if len(NVset) >= target:
            nn = {"BTN": [], "BT": []}
            for s in range(200):
                Sn = sample(NV, target, s)
                nn["BTN"].append(len(Sn & BTN) / target)
                nn["BT"].append(len(Sn & BT) / target)
            out["NV"] = {k: [round(st.mean(x), 4), round(sorted(x)[4], 4), round(sorted(x)[194], 4)] for k, x in nn.items()}
        if "V" in out and "NV" in out:
            out["excess_V_minus_NV_BTN"] = round(out["V"]["BTN"][0] - out["NV"]["BTN"][0], 4)
            out["excess_V_minus_NV_BT"] = round(out["V"]["BT"][0] - out["NV"]["BT"][0], 4)
        res[f"at_{target}"] = out
        print(target, json.dumps(out))
    json.dump(res, open(os.path.join(HERE, "out", "p3_84000_house_null.json"), "w"), indent=1)


if __name__ == "__main__":
    if sys.argv[1] == "fetch":
        fetch(sys.argv[2], int(sys.argv[3]))
    else:
        run()
