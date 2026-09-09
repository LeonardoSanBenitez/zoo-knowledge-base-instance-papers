#!/usr/bin/env python3
"""Does a resolving data link return a PAYLOAD or a SHELL?

    python shell_or_payload.py --validate      # known-answer cases first, no corpus
    python shell_or_payload.py --corpus        # das_links.json
    python shell_or_payload.py --url <URL>

THE QUESTION. Every measurement of data availability in the literature asks whether a link
RESOLVES. None asks whether what comes back is the thing. Briney 2024 gets closest (13.4% of
shared URLs point at a website homepage) and her own resolution criterion counts a login wall
as available. Meanwhile a Git LFS pointer answers HTTP 200 with 134 bytes, and OSF answers
HTTP 200 with a byte-identical 4,207-byte application shell for a live deposit, a deleted one,
and two identifiers invented for the purpose.

THE METHOD, and it is the only part of this worth keeping: **per-host null calibration.**

    For every link L, construct a NONSENSE SIBLING L' on the same host, of the same shape,
    with the identifier replaced by a random token. Fetch both.

    If L and L' come back the same, the host is not discriminating, and L tells you nothing
    about whether the resource exists. That is a SHELL.
    If L' fails where L succeeds, the host IS discriminating, and L's success means something.

This is the generalisation of a one-line control: *run your check against an identifier you
invented.* It costs one extra request per host and it converts "the link resolved" from an
assertion into a measurement.

CLASSES
    payload        200, and the nonsense sibling does not come back the same. Or a non-HTML
                   content type, which a shell essentially never is.
    shell          200, and the nonsense sibling comes back the same (or near-identical).
    homepage       the URL has no path beyond "/" -- Briney's category, detectable without
                   fetching anything.
    drifted        200, but the final URL after redirects has lost its path: it landed on a
                   homepage or a generic page.
    lfs-pointer    200, and the body is a Git LFS pointer.
    dead           4xx/5xx.
    blocked        403/429/TLS/timeout. NOT a classification -- we could not look.

FALSE PASS of this instrument: a host that serves the same generic 404 page for both L and
L' with status 200, where L genuinely exists but is behind a login. Called `shell`, which is
the right answer for "can a machine get the data", and the wrong answer for "does it exist".
Reported as a known limit, not as a solved problem.
FALSE FAIL: a host that rate-limits the second (nonsense) request and returns 429, making a
real payload look unclassifiable. Guarded by ordering (nonsense first is worse), a delay, and
by reporting `blocked` rather than guessing.
"""
import argparse
import hashlib
import json
import random
import re
import string
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

UA = {"User-Agent": "Mozilla/5.0 (compatible; zoo-research/1.0; +mailto:lsbenitezpereira@gmail.com)"}
TIMEOUT = 30
MAXBYTES = 400_000
LFS_MARK = b"version https://git-lfs.github.com/spec/v1"


class R308(urllib.request.HTTPRedirectHandler):
    def http_error_308(self, req, fp, code, msg, headers):
        return self.http_error_301(req, fp, 301, msg, headers)


OPENER = urllib.request.build_opener(R308)


def fetch(url):
    """Returns a dict. Never raises."""
    out = {"url": url}
    try:
        r = OPENER.open(urllib.request.Request(url, headers=UA), timeout=TIMEOUT)
        body = r.read(MAXBYTES)
        out.update({"status": r.status, "final": r.geturl(),
                    "ctype": (r.headers.get("Content-Type") or "").split(";")[0].strip().lower(),
                    "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
                    "is_lfs": body[:len(LFS_MARK)] == LFS_MARK,
                    "clen": r.headers.get("Content-Length")})
    except urllib.error.HTTPError as e:
        out.update({"status": e.code, "final": url, "ctype": None, "bytes": 0,
                    "sha256": None, "is_lfs": False, "err": "http"})
    except Exception as e:  # noqa: BLE001
        out.update({"status": "EXC", "final": url, "ctype": None, "bytes": 0,
                    "sha256": None, "is_lfs": False, "err": type(e).__name__})
    return out


def nonsense_sibling(url):
    """Same host, same shape, an identifier that cannot exist.

    Replaces the LAST non-empty path segment with a random token of the same length class,
    keeping any extension. If there is no path, there is nothing to falsify and we say so --
    a bare homepage is already its own category.
    """
    p = urllib.parse.urlsplit(url)
    segs = [s for s in p.path.split("/") if s]
    if not segs:
        return None
    tok = "zz" + "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
    last = segs[-1]
    if "." in last:
        stem, _, ext = last.rpartition(".")
        segs[-1] = tok + "." + ext
    else:
        segs[-1] = tok
    return urllib.parse.urlunsplit((p.scheme or "https", p.netloc, "/" + "/".join(segs), "", ""))


def path_of(url):
    return urllib.parse.urlsplit(url).path.strip("/")


def classify(url, pause=0.8):
    """The whole instrument. Two fetches: the link, then its nonsense sibling."""
    if not url.startswith("http"):
        url = "https://" + url
    res = {"url": url, "host": urllib.parse.urlsplit(url).netloc.lower()}

    if not path_of(url):
        res["klass"] = "homepage"
        res["why"] = ("The URL carries no path. There is nothing to falsify and nothing "
                      "specific to retrieve; Briney 2024 measures this category at 13.4% of "
                      "shared URLs.")
        return res

    a = fetch(url)
    res["link"] = a
    if a["status"] in (403, 429) or a["status"] == "EXC":
        res["klass"] = "blocked"
        res["why"] = "Could not look (%s). NOT a classification." % a.get("err", a["status"])
        return res
    if isinstance(a["status"], int) and a["status"] >= 400:
        res["klass"] = "dead"
        res["why"] = "HTTP %d." % a["status"]
        return res
    if a["is_lfs"]:
        res["klass"] = "lfs-pointer"
        res["why"] = ("200 with a Git LFS pointer body. Present, non-empty, hashable and "
                      "useless.")
        return res

    time.sleep(pause)
    sib = nonsense_sibling(url)
    res["nonsense"] = sib
    b = fetch(sib) if sib else None
    res["control"] = b

    if b and b["status"] in (403, 429, "EXC"):
        res["klass"] = "blocked"
        res["why"] = ("The link answered but the control could not be fetched (%s), so the "
                      "host's discrimination is unmeasured." % b.get("err", b["status"]))
        return res

    same_hash = bool(b and a["sha256"] and a["sha256"] == b["sha256"])
    both_200 = bool(b and b["status"] == 200)
    near_size = bool(b and b["bytes"] and a["bytes"]
                     and abs(a["bytes"] - b["bytes"]) / max(a["bytes"], b["bytes"]) < 0.02)
    same_ctype = bool(b and a["ctype"] == b["ctype"])

    drifted = bool(path_of(a["final"]) == "" and path_of(url) != "")

    if same_hash:
        res["klass"] = "shell"
        res["why"] = ("Byte-identical to a nonsense identifier on the same host (sha256 "
                      "match). The host is not discriminating; the 200 means nothing.")
    elif both_200 and near_size and same_ctype:
        res["klass"] = "shell"
        res["why"] = ("A nonsense identifier on the same host returns 200 with the same "
                      "content type and a size within 2%%: %d vs %d bytes. Almost certainly "
                      "the same application shell with a different token in it."
                      % (a["bytes"], b["bytes"]))
    elif drifted:
        res["klass"] = "drifted"
        res["why"] = ("Resolved, but the final URL after redirects has no path: it landed on "
                      "a homepage. %s -> %s" % (url, a["final"]))
    elif a["ctype"] and not a["ctype"].startswith("text/html"):
        res["klass"] = "payload"
        res["why"] = "Non-HTML content type (%s), %d bytes." % (a["ctype"], a["bytes"])
    elif both_200:
        res["klass"] = "payload"
        res["why"] = ("HTML, but the nonsense control differs from it (%d vs %d bytes, "
                      "different sha256), so the host does discriminate." % (a["bytes"], b["bytes"]))
    else:
        res["klass"] = "payload"
        res["why"] = ("The nonsense control fails (HTTP %s) where the link succeeds, so the "
                      "host discriminates and the 200 carries information."
                      % (b["status"] if b else "n/a"))
    return res


# ------------------------------------------------------------------ validation

KNOWN = [
    ("https://osf.io/xerhg/download", "payload",
     "the MPE-92M zip; verified against OSF's own published sha256 on 2026-09-08"),
    ("https://osf.io/gb76x", "shell",
     "deleted OSF guid; api.osf.io/v2/guids/gb76x/ returns 410 Gone"),
    ("https://osf.io/xerhg", "shell",
     "LIVE OSF guid. Deliberately in the KNOWN list as a SHELL, because the browser URL "
     "returns the same application frame as a deleted or invented one. The resource exists "
     "and this URL does not demonstrate it -- which is exactly the distinction being measured."),
    ("https://raw.githubusercontent.com/nikhgarg/llm_correlated_errors_public/"
     "30a2c0aa88af3f428f1f7034538373d24c209176/data/helm/all_mmlu_data_limitedcols.csv",
     "lfs-pointer", "335 MB by its own declaration; 134 bytes in fact"),
    ("https://zenodo.org/records/4059767", "payload",
     "a real Zenodo record; Zenodo 404s on a nonsense record id"),
    ("https://www.dhsprogram.com", "homepage",
     "cited as a data link in a 2016 PLOS ONE data availability statement, verbatim"),
]


def validate():
    print("VALIDATION -- cases where the answer is known before the instrument runs.\n"
          "An instrument that has never been shown to get a known case right is an assertion.\n")
    bad = 0
    for url, expect, why in KNOWN:
        r = classify(url)
        ok = r["klass"] == expect
        bad += 0 if ok else 1
        print("  %-5s %-12s (expected %-12s) %s" % ("ok" if ok else "FAIL", r["klass"], expect,
                                                    url[:78]))
        print("        %s" % r.get("why", "")[:150])
        print("        known because: %s" % why[:150])
        time.sleep(0.8)
    print("\n%s  %d/%d known cases classified correctly"
          % ("FAIL" if bad else "PASS", len(KNOWN) - bad, len(KNOWN)))
    return bad


def run_corpus():
    d = json.load(open("das_links.json", encoding="utf-8"))
    links = []
    for a in d["articles"]:
        for u in (a.get("urls") or []):
            links.append({"year": a["year"], "pmcid": a["pmcid"], "url": u, "kind": "url"})
        for doi in (a.get("dois") or []):
            links.append({"year": a["year"], "pmcid": a["pmcid"],
                          "url": "https://doi.org/" + doi, "kind": "doi"})
    seen, uniq = set(), []
    for l in links:
        if l["url"].lower() not in seen:
            seen.add(l["url"].lower())
            uniq.append(l)
    print("%d links (%d unique) from %d articles\n" % (len(links), len(uniq), d["n_articles"]))
    out = []
    for i, l in enumerate(uniq, 1):
        r = classify(l["url"])
        r.update({"year": l["year"], "pmcid": l["pmcid"], "kind": l["kind"]})
        out.append(r)
        print("  %3d/%d  %-14s %s" % (i, len(uniq), r["klass"], l["url"][:86]))
        time.sleep(0.5)
    with open("shell_or_payload_results.json", "w", encoding="utf-8") as fh:
        json.dump({"n": len(out), "results": out}, fh, indent=1, ensure_ascii=False)
    print("\nwrote shell_or_payload_results.json")


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
        print(json.dumps(classify(a.url), indent=1, ensure_ascii=False))
        return
    if a.corpus:
        run_corpus()
        return
    ap.print_help()


if __name__ == "__main__":
    main()
