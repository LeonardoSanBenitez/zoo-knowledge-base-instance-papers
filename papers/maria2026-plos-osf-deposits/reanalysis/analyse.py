#!/usr/bin/env python3
"""What does an OSF link in a PLOS Data Availability statement deliver? Counts with Wilson CIs.

    python reanalysis/analyse.py artifacts/plos_osf.jsonl                  # offline, from the scout
    python reanalysis/analyse.py artifacts/plos_osf.jsonl --verify-dates   # + OSF versions API
    python reanalysis/analyse.py --selftest                                # known-answer check

Input: the jsonl written by dev-science-ops/paper-retrospective-reproducibility/tools/
scout_plos_osf.py (probe_version 3), copied into artifacts/ with its sha256 in paper.json.

THE DATE CLASSIFIER, and why it is not trusted on its own. A file whose `date_modified` is later
than the paper's publication date can mean three different things:
    replaced   a new VERSION was uploaded after publication (the bytes changed)
    late       the file's FIRST version was uploaded after publication (the deposit was
               incomplete when the paper appeared)
    metadata   neither: a rename, move or other edit that touched date_modified only
`--verify-dates` asks OSF for each flagged file's versions (`date_created` per version) and sorts
it into exactly one of the three. Without that flag the script reports only the unverified count
and says so.

Stdlib only. All file I/O declares its encoding.
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import pathlib
import sys
import time
import urllib.error
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

UA = {"User-Agent": "maria-kb-reanalysis/1.0", "Accept": "application/vnd.api+json"}


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (100 * (c - h), 100 * (c + h))


def classify(rows: list[dict]) -> dict:
    """Pure function of the scout rows. Returns the counts every claim is built from."""
    c = collections.Counter()
    flagged = []                      # (doi, guid, path, pub_date, key)
    for r in rows:
        c["sampled"] += 1
        if r.get("jats_status") != 200:
            c["jats_unreadable"] += 1
            continue
        if not r.get("das_guids"):
            c["das_no_osf"] += 1
            continue
        c["das_osf"] += 1
        osf = r.get("osf") or []
        if any(o.get("view_only") for o in osf):
            c["das_view_only"] += 1
        states = []
        for o in osf:
            s = o.get("guids_status")
            if s in (404, 410):
                states.append("dead")
            elif s in (401, 403):
                states.append("private")
            elif s == 200 and (o.get("n_files") or 0) > 0:
                states.append("files")
            elif s == 200:
                states.append("empty-or-children" if o.get("children") else "empty")
            else:
                states.append("unchecked")
        # A paper's state is the BEST of its GUIDs: one live deposit means the data is reachable.
        for st in ("files", "empty-or-children", "empty", "private", "dead", "unchecked"):
            if st in states:
                c["paper_" + st] += 1
                break
        if any(st == "private" for st in states):
            c["paper_any_private"] += 1
        live = [o for o in osf if o.get("guids_status") == 200]
        files = [f for o in live for f in (o.get("files") or [])]
        if files:
            c["paper_with_listed_files"] += 1
            code = sum(o.get("n_code") or 0 for o in live)
            arch = sum(o.get("n_archive") or 0 for o in live)
            c["paper_visible_code"] += 1 if code else 0
            c["paper_archive_only"] += 1 if (not code and arch) else 0
            pub = (r.get("date") or "")[:10]
            hit = False
            for o in live:
                for f in o.get("files") or []:
                    path, _size, mod, ver = (list(f) + [None] * 4)[:4]
                    c["files"] += 1
                    if (ver or 1) > 1:
                        c["files_version_gt1"] += 1
                    if mod and mod[:10] > pub:
                        c["files_modified_after_pub"] += 1
                        flagged.append((r["doi"], o["guid"], path, pub,
                                        o.get("view_only")))
                        hit = True
            c["paper_modified_after_pub_unverified"] += 1 if hit else 0
    return {"counts": dict(c), "flagged": flagged}


def _get(url: str):
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 or e.code >= 500:
                time.sleep(3 * (i + 1))
                continue
            return e.code, None
        except Exception:
            time.sleep(2)
    return -1, None


def verify_dates(flagged: list, keys: dict) -> list[dict]:
    """For each flagged file: find it in its node's listing, read its versions, sort it into
    replaced / late / metadata. `keys` maps guid -> view_only key (the scout stores only a flag,
    so keys are re-read from the DAS)."""
    out = []
    by_node = collections.defaultdict(list)
    for doi, guid, path, pub, _vo in flagged:
        by_node[(doi, guid, pub)].append(path)
    for (doi, guid, pub), paths in by_node.items():
        key = keys.get(guid)
        k = ("&view_only=" + key) if key else ""
        # walk the node until every flagged path is found (bounded)
        want, found, queue, calls = set(paths), {}, [f"https://api.osf.io/v2/nodes/{guid}/files/?page[size]=100{k}"], 0
        while queue and want - set(found) and calls < 200:
            u = queue.pop(0)
            calls += 1
            s, d = _get(u)
            if s != 200:
                continue
            nxt = (d.get("links") or {}).get("next")
            if nxt:
                queue.append(nxt if "view_only" in nxt or not key else nxt + k)
            for e in d.get("data") or []:
                a = e.get("attributes") or {}
                if a.get("kind") == "folder":
                    h = (((e.get("relationships") or {}).get("files") or {}).get("links") or {}).get("related", {}).get("href")
                    if h:
                        queue.append(h + ("&" if "?" in h else "?") + "page[size]=100" + k)
                elif a.get("materialized_path") in want:
                    found[a["materialized_path"]] = e
        for p in paths:
            e = found.get(p)
            rec = {"doi": doi, "guid": guid, "path": p, "pub": pub}
            if not e:
                rec["class"] = "not-found-again"
                out.append(rec)
                continue
            vh = (((e.get("relationships") or {}).get("versions") or {}).get("links") or {}).get("related", {}).get("href")
            s, v = _get(vh + ("&" if "?" in vh else "?") + "page[size]=100" + k) if vh else (-1, None)
            dates = sorted(((x.get("attributes") or {}).get("date_created") or "")[:10]
                           for x in ((v or {}).get("data") or []))
            rec["version_dates"] = dates
            if not dates:
                rec["class"] = "versions-unreadable"
            elif dates[0] > pub:
                rec["class"] = "late"
            elif dates[-1] > pub:
                rec["class"] = "replaced"
            else:
                rec["class"] = "metadata"
            if dates and rec["class"] in ("late", "replaced"):
                import datetime as _dt
                d0 = _dt.date.fromisoformat(pub)
                rel = dates[0] if rec["class"] == "late" else dates[-1]
                rec["lag_days"] = (_dt.date.fromisoformat(rel) - d0).days
            out.append(rec)
            time.sleep(0.3)
    return out


def report(rows: list[dict], verified: list | None) -> dict:
    res = classify(rows)
    c = res["counts"]
    n_osf = c.get("das_osf", 0)
    lines = []

    def share(name, k, n):
        lo, hi = wilson(k, n)
        lines.append(f"{name:55} {k:3}/{n:<3} = {100*k/n if n else float('nan'):5.1f}%  95% CI [{lo:4.1f}, {hi:4.1f}]")
        return {"k": k, "n": n, "pct": round(100 * k / n, 1) if n else None,
                "ci95": [round(lo, 1), round(hi, 1)]}

    out = {"counts": c}
    out["das_names_osf"] = share("DAS names an OSF GUID (of sampled with readable JATS)", n_osf,
                                 c["sampled"] - c.get("jats_unreadable", 0))
    out["files_reachable"] = share("...and a GUID delivers >=1 file", c.get("paper_files", 0), n_osf)
    out["view_only"] = share("...DAS link carries a view_only token", c.get("das_view_only", 0), n_osf)
    out["private"] = share("...a cited GUID is private to the public (401/403)", c.get("paper_any_private", 0), n_osf)
    out["empty_parent_children"] = share("...best GUID empty but has child components", c.get("paper_empty-or-children", 0), n_osf)
    out["empty"] = share("...best GUID empty, no children", c.get("paper_empty", 0), n_osf)
    out["dead"] = share("...every cited GUID 404/410", c.get("paper_dead", 0), n_osf)
    nf = c.get("paper_with_listed_files", 0)
    out["visible_code"] = share("of papers with files: a code file is visible", c.get("paper_visible_code", 0), nf)
    out["mod_after_pub_unverified"] = share("of papers with files: a file date_modified > pub date (UNVERIFIED)",
                                            c.get("paper_modified_after_pub_unverified", 0), nf)
    if verified is not None:
        per_paper = collections.defaultdict(set)
        for v in verified:
            per_paper[v["doi"]].add(v["class"])
        out["verified_classes_files"] = dict(collections.Counter(v["class"] for v in verified))
        out["replaced_after_pub"] = share("of papers with files: bytes REPLACED after pub (verified)",
                                          sum(1 for s in per_paper.values() if "replaced" in s), nf)
        out["late_after_pub"] = share("of papers with files: a file FIRST uploaded after pub (verified)",
                                      sum(1 for s in per_paper.values() if "late" in s), nf)
        # Lag matters: uploads 1-4 days after publication are authors finishing around the date,
        # not drift. Report the >= 7 day subset separately.
        big = collections.defaultdict(set)
        for v in verified:
            if v.get("lag_days") is not None and v["lag_days"] >= 7:
                big[v["doi"]].add(v["class"])
        out["changed_7d_plus"] = share("of papers with files: replaced OR first-uploaded >= 7 days after pub",
                                       len(big), nf)
        out["lag_days_all"] = sorted(v["lag_days"] for v in verified if v.get("lag_days") is not None)
        print("lag days (late+replaced files):", out["lag_days_all"])
    print("\n".join(lines))
    print(json.dumps({k: v for k, v in out.items() if k == "verified_classes_files"}))
    return out


def selftest() -> int:
    """Known answers: a synthetic sample whose every count is fixed by construction."""
    rows = [
        {"doi": "a", "date": "2026-01-01", "jats_status": 200, "das_guids": [], "osf": []},
        {"doi": "b", "date": "2026-01-01", "jats_status": 404},
        {"doi": "c", "date": "2026-01-01", "jats_status": 200, "das_guids": ["g1"], "osf": [
            {"guid": "g1", "guids_status": 200, "n_files": 2, "n_code": 1, "n_archive": 0,
             "files": [["/a.R", 1, "2025-12-01T00:00", 1], ["/b.csv", 1, "2026-02-01T00:00", 2]]}]},
        {"doi": "d", "date": "2026-01-01", "jats_status": 200, "das_guids": ["g2", "g3"], "osf": [
            {"guid": "g2", "guids_status": 401, "view_only": True},
            {"guid": "g3", "guids_status": 410}]},
        {"doi": "e", "date": "2026-01-01", "jats_status": 200, "das_guids": ["g4"], "osf": [
            {"guid": "g4", "guids_status": 200, "n_files": 0, "children": ["k1"], "files": []}]},
        # one private GUID and one live one: the paper's data IS reachable (best-of), and it
        # still counts once in paper_any_private. Added after a mutation reordering the
        # best-of priority survived the first version of this test.
        {"doi": "f", "date": "2026-01-01", "jats_status": 200, "das_guids": ["g5", "g6"], "osf": [
            {"guid": "g5", "guids_status": 403},
            {"guid": "g6", "guids_status": 200, "n_files": 1, "n_code": 0, "n_archive": 1,
             "files": [["/d.zip", 5, "2025-06-01T00:00", 1]]}]},
    ]
    c = classify(rows)["counts"]
    want = {"sampled": 6, "jats_unreadable": 1, "das_no_osf": 1, "das_osf": 4, "das_view_only": 1,
            "paper_files": 2, "paper_private": 1, "paper_any_private": 2,
            "paper_empty-or-children": 1, "files": 3, "files_version_gt1": 1,
            "files_modified_after_pub": 1, "paper_modified_after_pub_unverified": 1,
            "paper_visible_code": 1, "paper_archive_only": 1, "paper_with_listed_files": 2}
    bad = {k: (c.get(k), v) for k, v in want.items() if c.get(k) != v}
    lo, hi = wilson(20, 53)
    ok_w = abs(lo - 25.9) < 0.1 and abs(hi - 51.2) < 0.1    # the shell-or-payload record's own CI
    print("selftest:", "PASS" if not bad and ok_w else "FAIL", bad or "", "" if ok_w else (lo, hi))
    return 0 if not bad and ok_w else 1


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("jsonl", nargs="?")
    ap.add_argument("--verify-dates", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    rows = [json.loads(l) for l in pathlib.Path(a.jsonl).read_text(encoding="utf-8").splitlines() if l.strip()]
    verified = None
    if a.verify_dates:
        import re
        keys = {}
        for r in rows:
            for g, tail in re.findall(r"osf\.io/([a-z0-9]{5})\b([^\s)<>\"]*)", (r.get("das") or ""), re.I):
                m = re.search(r"view_only=([A-Za-z0-9]+)", tail)
                if m:
                    keys[g.lower()] = m.group(1)
        verified = verify_dates(classify(rows)["flagged"], keys)
    out = report(rows, verified)
    if verified is not None:
        out["verified_files"] = verified
    if a.out:
        # newline="\n" so the output's sha256 does not depend on the host (Windows text mode
        # wrote CRLF; found 2026-10-14 by kb.py health's artifact-hash check).
        pathlib.Path(a.out).write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n",
                                       encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
