#!/usr/bin/env python3
"""Scout PLOS papers whose Data Availability statement names an OSF deposit, and LIST (never
download) what each deposit actually holds.

    python tools/scout_plos_osf.py --n 40 --seed 20261014 --out papers/_scouting/plos_osf.jsonl
    python tools/scout_plos_osf.py --summary papers/_scouting/plos_osf.jsonl

Written 2026-10-14 by maria. A search record for choosing calibration paper #4, NOT a decision
(SELECTION.md: mark proposes, Leonardo picks at the SELECT gate). It exists because OSF and
figshare backends were added to acquire.py that day and no calibration paper has exercised them.

WHAT IT MEASURES, per paper: the OSF GUIDs in the DAS (not the reference list -- a cited
preregistration of someone else's study is not this paper's data), and per GUID: its type,
whether it is 404/410, the number of files and bytes across every provider (acquire._osf_walk,
the same walker S1 uses), unreadable listings, child components, licence, and which files look
like code by extension. Archives (.zip, .tar.gz, .7z, .rar) are counted separately because what
is inside them cannot be known without downloading, and this tool does not download.

KNOWN-ANSWER CONTROLS, run first, every time; the run aborts if either fails:
    osf.io/cbhdv -> 1 file, 1,301,939 B (Gamma & Metzinger's deposit, verified by sha256)
    osf.io/3bzu8 -> 0 files, github add-on listing 404 (Laurinavichyute 2022)
A scout whose instrument cannot tell those two apart has nothing to report.

Resumable: papers already in --out are skipped. Every line is one paper.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import random
import re
import sys
import time
import urllib.parse
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import acquire  # noqa: E402

UA = {"User-Agent": "retro-repro-scout/1.0 (+dev-science-ops/paper-retrospective-reproducibility)"}
JOURNAL_SLUG = {"pone": "plosone", "pbio": "plosbiology", "pcbi": "ploscompbiol",
                "pgen": "plosgenetics", "ppat": "plospathogens", "pmed": "plosmedicine",
                "pntd": "plosntds", "pclm": "climate", "pdig": "digitalhealth",
                "pgph": "globalpublichealth", "pmen": "mentalhealth", "pwat": "water",
                "pstr": "sustainabilitytransformation", "pcsy": "complexsystems"}
CODE_EXT = {".r", ".rmd", ".qmd", ".py", ".ipynb", ".m", ".jl", ".do", ".ado", ".sps", ".sas",
            ".stan", ".sh", ".cpp", ".c", ".java", ".js", ".mlx", ".nb", ".wl", ".pl", ".rs",
            ".go", ".jasp", ".omv"}
ARCHIVE_EXT = (".zip", ".tar.gz", ".tgz", ".tar", ".7z", ".rar", ".gz")
GUID_RE = re.compile(r"osf\.io/(?:preprints/[a-z]+/)?([a-z0-9]{5})\b([^\s)<>\"]*)", re.I)
PROBE_VERSION = 3   # 2: view_only keys carried (v1 dropped them). 3: per-file dates and
                    # versions kept, so "did the deposit change after the paper?" is answerable
_LICENCES: dict = {}


def get_bytes(url: str, tries: int = 3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and i + 1 < tries:
                time.sleep(5 * (i + 1))
                continue
            return e.code, b""
        except Exception:
            time.sleep(2)
    return -1, b""


def plos_ids(n_max: int = 1000) -> list[dict]:
    q = ('everything:"osf.io" AND everything:"code" AND publication_date:[2026-01-01T00:00:00Z '
         'TO NOW] AND doc_type:full AND article_type:"Research Article"')
    url = "https://api.plos.org/search?" + urllib.parse.urlencode(
        {"q": q, "fl": "id,journal,publication_date,title_display", "rows": n_max})
    s, b = get_bytes(url)
    if s != 200:
        sys.exit("PLOS search answered %s" % s)
    d = json.loads(b)["response"]
    return d["docs"], d["numFound"], q


def das_of(doi: str):
    """(status, data-availability text or None) from the article's JATS."""
    code = doi.split("journal.")[1].split(".")[0]
    slug = JOURNAL_SLUG.get(code)
    if not slug:
        return "unknown-journal-%s" % code, None
    s, b = get_bytes("https://journals.plos.org/%s/article/file?id=%s&type=manuscript"
                     % (slug, doi))
    if s != 200:
        return s, None
    x = b.decode("utf-8", "replace")
    m = re.search(r'<custom-meta[^>]*id="data-availability"[^>]*>.*?<meta-value>(.*?)</meta-value>',
                  x, re.S)
    if not m:
        return "no-das-in-jats", None
    return 200, re.sub(r"<[^>]+>", " ", m.group(1))


def licence_name(lic_id):
    if not lic_id:
        return None
    if lic_id not in _LICENCES:
        s, d = acquire.osf_get("%s/licenses/%s/" % (acquire.OSF_API, lic_id))
        _LICENCES[lic_id] = ((d or {}).get("data") or {}).get("attributes", {}).get("name") \
            if s == 200 else "unreadable-%s" % s
    return _LICENCES[lic_id]


def guids_in(das: str) -> list:
    """(guid, view_only key or None) for every OSF link in the DAS; the key is read from the
    same URL as the GUID, never from a neighbouring one."""
    out: dict = {}
    for g, tail in GUID_RE.findall(das or ""):
        g = g.lower()
        k = acquire.osf_view_only(tail)
        if g not in out or (k and not out[g]):
            out[g] = k
    return sorted(out.items())


def probe_guid(guid: str, key=None) -> dict:
    r = {"guid": guid, "view_only": bool(key)}
    G = lambda u: acquire.osf_get(acquire.with_key(u, key))
    s, g = G("%s/guids/%s/" % (acquire.OSF_API, guid))
    r["guids_status"] = s
    if s != 200:
        return r
    typ = ((g or {}).get("data") or {}).get("type")
    r["type"] = typ
    if typ == "files":
        s, f = G("%s/files/%s/" % (acquire.OSF_API, guid))
        a = ((f or {}).get("data") or {}).get("attributes") or {}
        r.update({"n_files": 1 if a.get("kind") == "file" else 0, "bytes": a.get("size") or 0,
                  "names": [a.get("name")],
                  "files": [[a.get("name"), a.get("size"), a.get("date_modified"),
                             a.get("current_version")]]})
    elif typ in ("nodes", "registrations"):
        s, n = G("%s/%s/%s/" % (acquire.OSF_API, typ, guid))
        na = ((n or {}).get("data") or {}).get("attributes") or {}
        r["node_date_created"], r["node_date_modified"] = na.get("date_created"), na.get("date_modified")
        lic = ((((n or {}).get("data") or {}).get("relationships") or {}).get("license") or {}).get("data")
        r["licence"] = licence_name((lic or {}).get("id"))
        entries, providers, unreadable = acquire._osf_walk(typ, guid, key=key)
        r.update({"providers": providers, "unreadable": unreadable, "n_files": len(entries),
                  "bytes": sum(((e.get("attributes") or {}).get("size") or 0) for _, e in entries),
                  "names": [((e.get("attributes") or {}).get("materialized_path") or "")
                            for _, e in entries],
                  # [path, size, date_modified, current_version] per file, capped. date_modified
                  # later than the paper's publication date, or current_version > 1, means the
                  # bytes a reader gets today may not be the bytes the paper used.
                  "files": [[(e.get("attributes") or {}).get("materialized_path"),
                             (e.get("attributes") or {}).get("size"),
                             (e.get("attributes") or {}).get("date_modified"),
                             (e.get("attributes") or {}).get("current_version")]
                            for _, e in entries[:600]]})
        cs, c = G("%s/%s/%s/children/?page[size]=100" % (acquire.OSF_API, typ, guid))
        r["children"] = [k.get("id") for k in ((c or {}).get("data") or [])] if cs == 200 else None
    else:
        return r
    low = [x.lower() for x in r.get("names", []) if x]
    r["n_code"] = sum(1 for x in low if pathlib.PurePosixPath(x).suffix in CODE_EXT)
    r["n_archive"] = sum(1 for x in low if x.endswith(ARCHIVE_EXT))
    r["names"] = r["names"][:40]
    return r


def controls() -> None:
    a = probe_guid("cbhdv")
    b = probe_guid("3bzu8")
    ok_a = a.get("n_files") == 1 and a.get("bytes") == 1301939
    ok_b = b.get("n_files") == 0 and any(u.get("status") == 404 for u in b.get("unreadable", []))
    print("control cbhdv: %s   control 3bzu8: %s" % ("ok" if ok_a else "FAIL", "ok" if ok_b else "FAIL"))
    if not (ok_a and ok_b):
        sys.exit("a known-answer control failed; the instrument cannot be trusted today:\n%s\n%s"
                 % (json.dumps(a)[:400], json.dumps(b)[:400]))


def run(args) -> None:
    controls()
    docs, found, q = plos_ids()
    rnd = random.Random(args.seed)
    sample = rnd.sample(docs, min(args.n, len(docs)))
    out = pathlib.Path(args.out)
    done = set()
    if out.is_file():
        for line in out.read_text(encoding="utf-8").splitlines():
            if line.strip():
                done.add(json.loads(line)["doi"])
    print("PLOS: %d hits for the query; sampled %d (seed %d); %d already done"
          % (found, len(sample), args.seed, len(done & {d["id"] for d in sample})))
    with out.open("a", encoding="utf-8") as fh:
        for d in sample:
            doi = d["id"]
            if doi in done:
                continue
            rec = {"doi": doi, "journal": d.get("journal"), "date": d.get("publication_date", "")[:10],
                   "title": d.get("title_display"), "query": q, "seed": args.seed,
                   "population": found, "checked_on": time.strftime("%Y-%m-%d")}
            s, das = das_of(doi)
            rec["jats_status"] = s
            rec["das"] = (das or "")[:1500] if das else None
            pairs = guids_in(das)
            rec["das_guids"] = [g for g, _ in pairs]
            rec["probe_version"] = PROBE_VERSION
            rec["osf"] = [probe_guid(g, k) for g, k in pairs]
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fh.flush()
            summ = "; ".join("%s:%s files=%s code=%s arch=%s" % (
                o["guid"], o.get("type") or o.get("guids_status"), o.get("n_files"),
                o.get("n_code"), o.get("n_archive")) for o in rec["osf"]) or "no OSF GUID in DAS"
            print("%s  %s" % (doi, summ))
            time.sleep(args.sleep)


def reprobe(src: str, dst: str) -> None:
    """Recompute every record's OSF probe from its stored DAS, without refetching the JATS."""
    controls()
    rows = [json.loads(l) for l in pathlib.Path(src).read_text(encoding="utf-8").splitlines() if l.strip()]
    with pathlib.Path(dst).open("w", encoding="utf-8") as fh:
        for r in rows:
            pairs = guids_in(r.get("das") or "")
            r["das_guids"] = [g for g, _ in pairs]
            r["osf"] = [probe_guid(g, k) for g, k in pairs]
            r["probe_version"] = PROBE_VERSION
            r["reprobed_on"] = time.strftime("%Y-%m-%d")
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
            fh.flush()
            print(r["doi"], [(o["guid"], o.get("guids_status"), o.get("n_files")) for o in r["osf"]])
            time.sleep(0.5)


def summary(path: str) -> None:
    rows = [json.loads(l) for l in pathlib.Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]
    c = collections.Counter()
    for r in rows:
        c["papers"] += 1
        if any(o.get("guids_status") in (401, 403) for o in r.get("osf", [])):
            c["paper-has-private-guid(401/403)"] += 1
        if any(o.get("view_only") for o in r.get("osf", [])):
            c["paper-das-uses-view_only-link"] += 1
        if r.get("jats_status") != 200:
            c["jats-unreadable"] += 1
            continue
        if not r["das_guids"]:
            c["no-osf-guid-in-das"] += 1
            continue
        c["papers-with-das-guid"] += 1
        live = [o for o in r["osf"] if o.get("guids_status") == 200]
        files = sum(o.get("n_files") or 0 for o in live)
        code = sum(o.get("n_code") or 0 for o in live)
        arch = sum(o.get("n_archive") or 0 for o in live)
        if any(o.get("guids_status") in (404, 410) for o in r["osf"]):
            c["paper-has-dead-guid"] += 1
        if files == 0:
            c["paper-zero-files"] += 1
        elif code:
            c["paper-files-and-visible-code"] += 1
        elif arch:
            c["paper-files-archive-only-code-unknown"] += 1
        else:
            c["paper-files-no-visible-code"] += 1
        if any(o.get("unreadable") for o in live):
            c["paper-has-unreadable-listing"] += 1
    for k, v in c.items():
        print("%-40s %d" % (k, v))
    # change after publication (probe_version >= 3 only)
    ch = collections.Counter()
    for r in rows:
        if r.get("probe_version", 1) < 3:
            continue
        files = [f for o in r.get("osf", []) if o.get("guids_status") == 200
                 for f in (o.get("files") or [])]
        if not files:
            continue
        ch["papers-with-listed-files"] += 1
        pub = r.get("date") or ""
        after = [f for f in files if f[2] and f[2][:10] > pub]
        multi = [f for f in files if (f[3] or 1) > 1]
        if after:
            ch["paper-has-file-modified-after-publication"] += 1
        if multi:
            ch["paper-has-file-with-version>1"] += 1
        ch["files"] += len(files)
        ch["files-modified-after-publication"] += len(after)
    if ch:
        print("--- change after publication (file date_modified > paper date) ---")
        for k, v in ch.items():
            print("%-40s %d" % (k, v))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--seed", type=int, default=20261014)
    ap.add_argument("--out", default=str(HERE.parent / "papers" / "_scouting" / "plos_osf.jsonl"))
    ap.add_argument("--sleep", type=float, default=1.0)
    ap.add_argument("--summary")
    ap.add_argument("--reprobe", nargs=2, metavar=("SRC", "DST"))
    a = ap.parse_args()
    if a.reprobe:
        reprobe(*a.reprobe)
    elif a.summary:
        summary(a.summary)
    else:
        run(a)


if __name__ == "__main__":
    main()
