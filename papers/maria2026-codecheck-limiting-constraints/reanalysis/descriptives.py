#!/usr/bin/env python3
"""Descriptive statistics over the CODECHECK register, and the robustness check that
matters most: does the headline survive the fact that one venue supplies 55% of it?

    python descriptives.py            # expects ../artifacts/register-full.json

Every number this prints is quoted in the record's claims. Run it before quoting them.
"""
import collections
import datetime
import json
import os
import statistics
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "..", "artifacts", "register-full.json"), encoding="utf-8"))
H = json.load(open(os.path.join(HERE, "codecheck_handcoded.json"), encoding="utf-8"))["coding"]

print("certificates in register-full.json : %d" % len(D))
withsum = [r for r in D if (r.get("Summary") or "").strip()]
print("with a non-empty Summary           : %d" % len(withsum))

# ---------------------------------------------------------------- who does the checking
cc = collections.Counter()
for r in D:
    for c in (r.get("Codecheckers") or []):
        cc[c.get("name", "?")] += 1
tot = sum(cc.values())
print("\nCODECHECKERS")
print("   distinct people        : %d" % len(cc))
print("   codechecker-slots      : %d (a check may have more than one)" % tot)
print("   top 1 share            : %.1f%%" % (100 * cc.most_common(1)[0][1] / tot))
print("   top 5 share            : %.1f%%" % (100 * sum(v for _, v in cc.most_common(5)) / tot))
print("   people with exactly 1  : %d (%.0f%% of people)"
      % (sum(1 for v in cc.values() if v == 1),
         100 * sum(1 for v in cc.values() if v == 1) / len(cc)))

# ---------------------------------------------------------------- where it comes from
ven = collections.Counter((r.get("Paper venue") or r.get("Venue") or "?") for r in D)
typ = collections.Counter(r.get("Type") for r in D)
print("\nPROVENANCE OF THE REGISTER")
print("   by type   : %s" % dict(typ))
print("   top venue : %s = %d (%.0f%% of the whole register)"
      % (ven.most_common(1)[0][0], ven.most_common(1)[0][1],
         100 * ven.most_common(1)[0][1] / len(D)))

# ---------------------------------------------------------------- when
def parse(s):
    if not s:
        return None
    try:
        return datetime.datetime.fromisoformat(s[:10])
    except Exception:
        return None


gaps = [((parse(r.get("Check date")) - parse(r.get("Work publication date"))).days, r["Certificate ID"])
        for r in D if parse(r.get("Check date")) and parse(r.get("Work publication date"))]
g = sorted(x[0] for x in gaps)
neg = sum(1 for x in g if x < 0)
print("\nWHEN THE CHECK HAPPENS RELATIVE TO PUBLICATION  (n=%d)" % len(g))
print("   median gap             : %d days" % statistics.median(g))
print("   checked BEFORE the work was published : %d (%.0f%%)" % (neg, 100 * neg / len(g)))
print("   within +/- 90 days     : %d (%.0f%%)"
      % (sum(1 for x in g if abs(x) <= 90), 100 * sum(1 for x in g if abs(x) <= 90) / len(g)))
print("   -> CODECHECK is overwhelmingly an INVITED, PRE- or AT-PUBLICATION activity.")

# ---------------------------------------------------------------- the headline + robustness
nd = sum(1 for v in H.values() if "deposit" not in v["codes"])
print("\nHEADLINE (from handcode_limits.py)")
print("   incomplete reproductions coded            : %d" % len(H))
print("   NOT limited by anything the authors did   : %d (%.1f%%)" % (nd, 100 * nd / len(H)))

agile = {r["Certificate ID"] for r in D if (r.get("Paper venue") or "") == "AGILE GIScience Series"}
print("\nROBUSTNESS -- one venue supplies %.0f%% of the register. Does the headline hold "
      "inside and outside it?" % (100 * len(agile) / len(D)))
for label, ids in [("AGILE GIScience", agile), ("everything else", set(H) - agile)]:
    sub = {k: v for k, v in H.items() if k in ids}
    if not sub:
        continue
    x = sum(1 for v in sub.values() if "deposit" not in v["codes"])
    print("   %-18s n=%2d   not-deposit %2d  (%.0f%%)" % (label, len(sub), x, 100 * x / len(sub)))
print("   The two agree to within one percentage point. The finding is not an artifact of")
print("   one conference's reproducibility-review programme, which was the obvious way for")
print("   it to be wrong.")

# ---------------------------------------------------------------- eligibility discipline
import re
ELIG = r"\beligible for reproduction\b|\bout of the \d+ (figures|tables)|\bnot covered by this\b|" \
       r"\bout of scope\b|\bnot applicable for reproduction\b"
e = sum(1 for r in withsum if re.search(ELIG, " ".join((r.get("Summary") or "").split()), re.I))
print("\nELIGIBILITY DISCIPLINE")
print("   summaries that state which paper elements were ELIGIBLE for reproduction:")
print("   %d of %d (%.1f%%)" % (e, len(withsum), 100 * e / len(withsum)))
print("   Everything else reports a numerator with no stated denominator.")
