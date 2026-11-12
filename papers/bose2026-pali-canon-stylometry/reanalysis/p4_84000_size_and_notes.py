"""p4 -- two follow-ups to p3, both forced by p3's corpus-identity check (V has 8,903 types, the paper says 11,515).

(a) The largest size both arms reach: V at its FULL vocabulary vs NV sampled to the same type count (200 draws).
    This replaces the 11,515-type comparison the p3 prediction named, which V is too small for. (Deviation, logged in NOTES.)
(b) Does the paper's 11,515 come from including 84000's notes (as its Brahmali side included Brahmali's)? Count V's types
    with <note> text kept, and with the whole TEI text (front matter, notes, glossary).

    PALI=<dir> python -I p4_84000_size_and_notes.py
Author: maria, 2026-11-12.
"""
import json
import os
import statistics as st
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from p2_buddhist_english_null import toks, sample, BT, BTN  # noqa: E402
from p3_84000_house_null import body_text, TEI, NS  # noqa: E402

picked = json.load(open(os.path.join(HERE, "out", "p3_picked.json")))
vpaths = [os.path.join(TEI, os.path.basename(p)) for p in picked["vinaya"]]
V = [toks(body_text(p)) for p in vpaths]
NV = [t for t in (toks(body_text(os.path.join(TEI, os.path.basename(p)))) for p in picked["nonvinaya"]) if t]
Vset = {w for f in V for w in f}
K = len(Vset)


def with_notes(path):
    root = ET.parse(path).getroot()
    divs = [d for d in root.iter(f"{NS}div") if d.get("type") == "translation"]
    notes = [" ".join(n.itertext()) for n in root.iter(f"{NS}note")]
    return " ".join(" ".join(d.itertext()) for d in divs) + " " + " ".join(notes)


def all_text(path):
    return " ".join(ET.parse(path).getroot().itertext())


res = {"V_types_body": K,
       "V_types_body_plus_notes": len({w for p in vpaths for w in toks(with_notes(p))}),
       "V_types_all_tei_text": len({w for p in vpaths for w in toks(all_text(p))}),
       "paper_types": 11515}
print(json.dumps(res))
vals = {"BTN": [], "BT": []}
for s in range(200):
    S = sample(NV, K, s)
    vals["BTN"].append(len(S & BTN) / K)
    vals["BT"].append(len(S & BT) / K)
res["at_V_full_size"] = {
    "size": K,
    "V": {"BTN": round(len(Vset & BTN) / K, 4), "BT": round(len(Vset & BT) / K, 4)},
    "NV": {k: [round(st.mean(v), 4), round(sorted(v)[4], 4), round(sorted(v)[194], 4)] for k, v in vals.items()},
}
a = res["at_V_full_size"]
a["excess_BTN"] = round(a["V"]["BTN"] - a["NV"]["BTN"][0], 4)
a["excess_BT"] = round(a["V"]["BT"] - a["NV"]["BT"][0], 4)
a["V_above_NV_p97.5_BTN"] = a["V"]["BTN"] > a["NV"]["BTN"][2]
print(json.dumps(a))
json.dump(res, open(os.path.join(HERE, "out", "p4_84000_size_and_notes.json"), "w"), indent=1)
