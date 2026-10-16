"""Apply a patterns backfill map to paper.json files -- as a TEXT edit, not a re-serialisation.

Records here were written by hand with mixed styles (indent 1 or 2, compact arrays).
Re-serialising them buried a one-field change in a ~10,000-line diff on the first try
(2026-10-16). So this script inserts `"patterns": [...]` directly after the claim's
`"status": "<value>"` in the raw text, bumps `schema_version` textually, and then PROVES
the edit: the re-parsed file must equal the original parse plus exactly the intended
fields. Anything else aborts before writing.

Idempotent: claims already carrying the same patterns are skipped. Bumps a record to
schema_version 1.5 only if it now uses the 1.5 field (no bulk migration,
MAPPING-AND-EVOLUTION.md).

    python instance-papers/schema/backfill/apply_patterns.py instance-papers/schema/backfill/patterns-2026-10-16.json
"""
import copy
import json
import os
import re
import sys

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(os.path.dirname(here))
m = json.load(open(sys.argv[1], encoding="utf-8"))["map"]
vocab = json.load(open(os.path.join(root, "schema", "patterns.json"), encoding="utf-8"))["patterns"]
bad = sorted({p for v in m.values() for p in v if p not in vocab})
if bad:
    sys.exit(f"unknown patterns: {bad}")
byrec = {}
for k, v in m.items():
    rid, cid = k.split("#")
    byrec.setdefault(rid, {})[cid] = v

done = 0
for rid, cl in byrec.items():
    p = os.path.join(root, "papers", rid, "paper.json")
    raw = open(p, encoding="utf-8", newline="").read()   # exact bytes: keep CRLF if present
    before = json.loads(raw)
    expected = copy.deepcopy(before)
    eclaims = {c["id"]: c for c in expected["claims"]}
    text = raw
    for cid, pats in cl.items():
        if cid not in eclaims:
            sys.exit(f"{rid}#{cid}: no such claim")
        oa = eclaims[cid].setdefault("our_assessment", {})
        if oa.get("patterns") == pats:
            continue
        if "patterns" in oa:
            sys.exit(f"{rid}#{cid}: already has different patterns {oa['patterns']}; edit by hand")
        oa["patterns"] = pats
        # locate the claim, then its our_assessment, then its status value
        mc = re.search(r'"id"\s*:\s*"%s"' % re.escape(cid), text)
        mo = re.compile(r'"our_assessment"\s*:\s*\{').search(text, mc.end())
        ms = re.compile(r'"status"\s*:\s*"[^"]*"').search(text, mo.end())
        ins = ', "patterns": ' + json.dumps(pats)
        text = text[:ms.end()] + ins + text[ms.end():]
        done += 1
    if expected.get("schema_version", "1.0") < "1.5":
        expected["schema_version"] = "1.5"
        text, k = re.subn(r'("schema_version"\s*:\s*)"[0-9.]+"', r'\g<1>"1.5"', text, count=1)
        if k != 1:
            sys.exit(f"{rid}: could not bump schema_version")
    if json.loads(text) != expected:
        sys.exit(f"{rid}: text edit does not reproduce the intended object; nothing written")
    if text != raw:
        open(p, "w", encoding="utf-8", newline="").write(text)
print(f"{done} claim(s) tagged across {len(byrec)} record(s)")
