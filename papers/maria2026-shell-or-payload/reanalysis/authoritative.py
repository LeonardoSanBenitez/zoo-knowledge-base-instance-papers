#!/usr/bin/env python3
"""Ask each host the question that decides, instead of asking every host the question that
is easy.

    python authoritative.py --validate
    python authoritative.py --corpus            # over shell_or_payload_results.json
    python authoritative.py --url <URL>

WHAT THIS IS FOR. Fetching a URL and reading HTTP 200 is a specification-side check: it tells
you the host answered, not that the resource is there. `shell_or_payload.py` shows how far
that goes wrong -- 37.7% of data links in a PLOS ONE sample resolve without delivering
anything -- but it can only ever say "this URL does not demonstrate the resource exists".

The question people actually have is "is the data there?", and for the handful of hosts that
carry most research data, there IS an endpoint that answers it. This file is that lookup
table. It is deliberately small: one host, one API, one mapping from that API's answers to a
fixed vocabulary. Adding a host is ten lines; guessing about a host is forbidden.

STATES, and the two that no link checker in the literature reports:
    exists            the host's own API says the resource is there
    gone              the host says it existed and was removed (e.g. HTTP 410)
    never-existed     the host says this identifier was never minted (404 on the API)
    PRIVATE           the host says it exists and you may not have it. MEASURED: an OSF node
                      cited in a published data availability statement is `public: false` and
                      reachable only via the anonymous-peer-review token left in the printed
                      URL. Every resolution check in the literature scores it as available.
    unknown-host      no authoritative endpoint is implemented. Say so; do not guess.
    api-error         the API did not answer. Not a classification.

FALSE PASS: a host API that reports a record as present while its files are empty -- the OSF
node with a title, a wiki and zero files that this project's CONTRIBUTING.md already
documents. Guarded for OSF only, by asking for the file listing when the guid is a node.
FALSE FAIL: a private-but-legitimately-restricted deposit reported as a problem. `private` is
a STATE, not a defect, and the caller decides. A dataset behind a data-use agreement is normal
in health research and is not a failure of the authors.
"""
import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
UA = {"User-Agent": "zoo-research/1.0 (mailto:lsbenitezpereira@gmail.com)"}
TIMEOUT = 30


def api(url, accept=None):
    h = dict(UA)
    if accept:
        h["Accept"] = accept
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=TIMEOUT)
        raw = r.read(300_000)
        try:
            return r.status, json.loads(raw)
        except Exception:  # noqa: BLE001
            return r.status, None
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:  # noqa: BLE001
        return "EXC:" + type(e).__name__, None


# ---------------------------------------------------------------- per-host resolvers

def _osf(u):
    p = urllib.parse.urlsplit(u)
    segs = [s for s in p.path.split("/") if s]
    if not segs:
        return {"state": "unknown-host", "why": "no guid in the path"}
    guid = segs[0]
    q = urllib.parse.parse_qs(p.query)
    tok = (q.get("view_only") or [None])[0]
    base = "https://api.osf.io/v2/guids/%s/" % guid
    s, m = api(base, "application/vnd.api+json")
    out = {"endpoint": base, "status": s, "guid": guid}
    if s == 410:
        out.update(state="gone", why="OSF returns 410 Gone: it existed and was removed.")
        return out
    if s == 404:
        out.update(state="never-existed", why="OSF returns 404: no such guid, ever.")
        return out
    if s == 401:
        if tok:
            s2, m2 = api(base + "?view_only=" + tok, "application/vnd.api+json")
            if s2 == 200 and m2:
                a = m2["data"]["attributes"]
                out.update(state="private", status2=s2,
                           public=a.get("public"), title=(a.get("title") or a.get("name")),
                           why=("Reachable ONLY with the view_only token that was left in the "
                                "printed URL. `public` is %s. An anonymous-review token can be "
                                "revoked by the owner at any time, and when it is, nothing about "
                                "the printed link changes." % a.get("public")))
                return out
        out.update(state="private",
                   why="OSF returns 401: the resource is not public and no token was supplied.")
        return out
    if s == 200 and m:
        a = m["data"]["attributes"]
        typ = m["data"].get("type")
        out.update(state="exists", osf_type=typ, public=a.get("public"),
                   title=(a.get("title") or a.get("name")), size=a.get("size"))
        if typ == "nodes":
            s3, m3 = api("https://api.osf.io/v2/nodes/%s/files/osfstorage/" % guid,
                         "application/vnd.api+json")
            n = len(m3["data"]) if (s3 == 200 and m3 and "data" in m3) else None
            out["n_files_at_root"] = n
            if n == 0:
                out.update(state="exists-but-empty",
                           why=("The node exists and its osfstorage root holds ZERO files. This "
                                "is the exact case paper-retrospective-reproducibility's "
                                "CONTRIBUTING.md names as its canonical false pass."))
        return out
    out.update(state="api-error", why="OSF API returned %s." % s)
    return out


def _zenodo(u):
    m = re.search(r"/records?/(\d+)", u)
    if not m:
        return {"state": "unknown-host", "why": "no record id in the path"}
    ep = "https://zenodo.org/api/records/" + m.group(1)
    s, j = api(ep)
    out = {"endpoint": ep, "status": s}
    if s == 200 and j:
        files = j.get("files") or []
        out.update(state="exists" if files else "exists-but-empty",
                   n_files=len(files), title=(j.get("metadata") or {}).get("title", "")[:80],
                   access=(j.get("metadata") or {}).get("access_right"))
    elif s == 410:
        out.update(state="gone", why="Zenodo returns 410: the record was removed.")
    elif s == 404:
        out.update(state="never-existed")
    elif s in (401, 403):
        out.update(state="private")
    else:
        out.update(state="api-error")
    return out


def _figshare(u):
    m = re.search(r"/(\d{4,})(?:$|[/?#])", u)
    if not m:
        return {"state": "unknown-host",
                "why": ("no numeric article id in the path. figshare private-share links "
                        "(/s/<hash>) have no public API form, which is itself why they cannot "
                        "be verified.")}
    ep = "https://api.figshare.com/v2/articles/" + m.group(1)
    s, j = api(ep)
    out = {"endpoint": ep, "status": s}
    if s == 200 and j:
        files = j.get("files") or []
        out.update(state="exists" if files else "exists-but-empty", n_files=len(files),
                   title=(j.get("title") or "")[:80], is_embargoed=j.get("is_embargoed"))
    elif s == 404:
        out.update(state="never-existed")
    elif s in (401, 403):
        out.update(state="private")
    else:
        out.update(state="api-error")
    return out


def _github(u):
    m = re.search(r"github\.com/([^/]+)/([^/?#]+)", u)
    if not m:
        return {"state": "unknown-host"}
    ep = "https://api.github.com/repos/%s/%s" % (m.group(1), m.group(2).replace(".git", ""))
    s, j = api(ep, "application/vnd.github+json")
    out = {"endpoint": ep, "status": s}
    if s == 200 and j:
        out.update(state="exists", archived=j.get("archived"), pushed_at=j.get("pushed_at"),
                   license=(j.get("license") or {}).get("spdx_id"), size_kb=j.get("size"))
        if not j.get("license"):
            out["note"] = ("No licence declared. Under default copyright that is all rights "
                           "reserved.")
    elif s == 404:
        out.update(state="never-existed",
                   why="404 covers both `never existed` and `private` on GitHub; they are "
                       "indistinguishable without authentication.")
    else:
        out.update(state="api-error")
    return out


def _doi(u):
    m = re.search(r"(10\.\d{4,9}/[^\s?#]+)", u)
    if not m:
        return {"state": "unknown-host"}
    doi = m.group(1).rstrip(".")
    s, j = api("https://api.crossref.org/works/" + doi)
    if s == 200 and j:
        msg = j["message"]
        return {"endpoint": "crossref", "status": s, "state": "exists",
                "registrant": "crossref", "type": msg.get("type"),
                "updated_by": [(e.get("type"), e.get("DOI")) for e in (msg.get("updated-by") or [])]}
    s2, j2 = api("https://api.datacite.org/dois/" + urllib.parse.quote(doi.lower(), safe=""))
    if s2 == 200 and j2:
        a = j2["data"]["attributes"]
        return {"endpoint": "datacite", "status": s2,
                "state": "exists" if a.get("state") == "findable" else "private",
                "registrant": "datacite", "datacite_state": a.get("state"),
                "title": (a.get("titles") or [{}])[0].get("title", "")[:80]}
    if s == 404 and s2 == 404:
        if doi.lower().startswith("10.5061/dryad"):
            r = _dryad_doi(doi)
            r["why"] = (r.get("why", "") + " (Neither Crossref nor DataCite has this DOI; "
                        "Dryad's own API was consulted because the two answers differ.)")
            return r
        return {"state": "never-existed", "status": [s, s2],
                "why": "Neither Crossref nor DataCite has this DOI."}
    return {"state": "api-error", "status": [s, s2]}


def _dryad_doi(doi):
    """Dryad, because `never registered` and `deleted` are different messages to an author.

    MEASURED 2026-09-08 on 10.5061/dryad.fttdz08wm, printed verbatim in the data availability
    statement of PLOS ONE 10.1371/journal.pone.0279890 (2022): doi.org 404, DataCite 404 both
    cases and 0 hits on a DOI search, Crossref 404 -- and yet Dryad's OWN api answers 200 with
    `{"identifier": "doi:10.5061/dryad.fttdz08wm", "id": 95584, "message": "Identifier cannot
    be viewed. Either you lack permission to view it, or it is missing"}`. The submission
    exists inside Dryad and was never published, so the DOI was never registered. Telling the
    authors "your DOI does not resolve" is true and useless; telling them "your Dryad
    submission id 95584 was never published" is the actionable form.
    """
    ep = "https://datadryad.org/api/v2/datasets/" + urllib.parse.quote("doi:" + doi, safe="")
    s, j = api(ep)
    if s == 200 and isinstance(j, dict) and j.get("message"):
        return {"endpoint": ep, "status": s, "state": "reserved-never-published",
                "dryad_id": j.get("id"), "dryad_message": j.get("message")[:160],
                "why": ("Dryad holds the submission but the DOI was never registered with "
                        "DataCite. This is the reserve-a-DOI-then-never-publish failure and it "
                        "is fixable by the authors in one click.")}
    if s == 200:
        return {"endpoint": ep, "status": s, "state": "exists"}
    return {"endpoint": ep, "status": s, "state": "api-error"}


HOSTS = [
    (r"(^|\.)osf\.io$", _osf),
    (r"(^|\.)zenodo\.org$", _zenodo),
    (r"(^|\.)figshare\.com$", _figshare),
    (r"(^|\.)github\.com$", _github),
    (r"(^|\.)(dx\.)?doi\.org$", _doi),
]


def authoritative(url):
    if not url.startswith("http"):
        url = "https://" + url
    host = urllib.parse.urlsplit(url).netloc.lower()
    for pat, fn in HOSTS:
        if re.search(pat, host):
            r = fn(url)
            r["url"] = url
            r["host"] = host
            return r
    return {"url": url, "host": host, "state": "unknown-host",
            "why": ("No authoritative endpoint is implemented for this host. Saying `unknown` "
                    "is the whole point: a link checker that reports `available` for a host it "
                    "cannot interrogate is reporting that the host answered, and calling it "
                    "something else.")}


KNOWN = [
    ("https://osf.io/xerhg", "exists", "the MPE-92M deposit, verified byte-for-byte 2026-09-08"),
    ("https://osf.io/gb76x", "gone", "deleted; the URL corrected by PLOS in 2024"),
    ("https://osf.io/zzzz9", "never-existed", "an identifier invented for this test"),
    ("https://osf.io/ysxuz/?view_only=d847c7e96f51428e9d70c942ae2af15b", "private",
     "cited in a published PLOS ONE data availability statement; `public: false`"),
    ("https://zenodo.org/records/4059767", "exists", "the CODECHECK register deposit"),
    ("https://doi.org/10.5281/zenodo.999999999", "never-existed", "invented Zenodo DOI"),
    ("https://doi.org/10.5061/dryad.fttdz08wm", "reserved-never-published",
     "printed in a 2022 PLOS ONE data availability statement; 404 at doi.org, DataCite and "
     "Crossref, but Dryad's own API returns submission id 95584 with `Identifier cannot be "
     "viewed`"),
]


def validate():
    print("VALIDATION -- known answers first.\n")
    bad = 0
    for url, expect, why in KNOWN:
        r = authoritative(url)
        ok = r["state"] == expect
        bad += 0 if ok else 1
        print("  %-5s %-16s (expected %-14s) %s" % ("ok" if ok else "FAIL", r["state"], expect,
                                                    url[:66]))
        if not ok:
            print("        got: %s" % json.dumps({k: v for k, v in r.items()
                                                  if k not in ("url", "host")})[:220])
        print("        known because: %s" % why)
        time.sleep(0.5)
    print("\n%s  %d/%d" % ("FAIL" if bad else "PASS", len(KNOWN) - bad, len(KNOWN)))
    return bad


def run_corpus():
    d = json.load(open("shell_or_payload_results.json", encoding="utf-8"))["results"]
    out = []
    for r in d:
        a = authoritative(r["url"])
        a["shell_or_payload_class"] = r["klass"]
        a["year"] = r.get("year")
        out.append(a)
        print("  %-16s %-14s %s" % (a["state"], r["klass"], r["url"][:74]))
        time.sleep(0.4)
    with open("authoritative_results.json", "w", encoding="utf-8") as fh:
        json.dump({"n": len(out), "results": out}, fh, indent=1, ensure_ascii=False)
    print("\nwrote authoritative_results.json")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--corpus", action="store_true")
    ap.add_argument("--url")
    a = ap.parse_args()
    if a.validate:
        sys.exit(1 if validate() else 0)
    if a.url:
        print(json.dumps(authoritative(a.url), indent=1, ensure_ascii=False))
        return
    if a.corpus:
        run_corpus()
        return
    ap.print_help()


if __name__ == "__main__":
    main()
