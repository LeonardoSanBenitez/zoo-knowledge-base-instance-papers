"""a2 -- re-check every OSF and GitHub artifact the KB corpus records, against the record's own status.

Open question 2 of this record: "How many other papers in this area have lost their own code?" The corpus already says
what each reader found when they looked; this asks whether that is STILL true, and whether the earlier check could have
been a shell (a node that answers 200 and holds nothing; files that live only behind a provider add-on).

Per artifact (records whose id starts with maria2026 are syntheses and skipped):
  OSF:    resolve the GUID (/v2/guids/<g>/, view_only key carried if the locator has one). File GUID -> exists + size.
          Node GUID -> files per provider (osfstorage counted; add-on providers counted separately: a POINTER), and children.
  GitHub: `gh api repos/<o>/<r>` -> exists, size, archived; if repo_commit is pinned, that commit must resolve.
Classes: alive | pointer-only | empty | gone | private | error.
Known-answer controls, run first (the checker must get them right or nothing is reported):
  invented OSF GUIDs (verified 404) -> gone; invented GitHub repo -> gone; openai/codex -> alive; OSF jmrqw with its
  key -> alive; its file GUID ky37d -> alive.

    python -I a2_corpus_recheck.py <instance-papers dir> > out/a2_corpus_recheck.txt
Author: maria, 2026-11-12.
"""
import glob
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

OSF = "https://api.osf.io/v2"
UA = {"User-Agent": "zoo-kb-artifact-audit/1.0", "Accept": "application/vnd.api+json"}


def get(url):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                return r.status, json.loads(r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503) and attempt < 2:
                time.sleep(5)
                continue
            return e.code, {}
        except Exception as e:  # noqa: BLE001
            if attempt < 2:
                time.sleep(3)
                continue
            return None, {"_error": f"{type(e).__name__}: {str(e)[:100]}"}


def q(url, key):
    return url + (("&" if "?" in url else "?") + "view_only=" + key if key else "")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def guid_type(guid, key):
    """/v2/guids/<g>/ answers 302 to the typed resource (nodes/<g>, preprints/<g>_v1, files/<id>, ...) or 404 if no such
    GUID. Read the Location without following it. (2026-11-12: zz8qv and p0w9j -> 404; jmrqw -> nodes; hf297 -> preprints.)"""
    op = urllib.request.build_opener(_NoRedirect)
    try:
        op.open(urllib.request.Request(q(f"{OSF}/guids/{guid}/", key), headers=UA), timeout=40)
        return None, None
    except urllib.error.HTTPError as e:
        if e.code in (301, 302, 303, 307, 308):
            loc = e.headers.get("Location", "")
            m = re.search(r"/v2/([a-z_]+)/([^/?]+)/", loc)
            return (m.group(1), m.group(2)) if m else ("unknown", loc)
        return e.code, None
    except Exception as e:  # noqa: BLE001
        return "error", str(e)[:80]


def osf_check(guid, key):
    typ, rid = guid_type(guid, key)
    if typ == 404 or typ == 410:
        return "gone", f"guid {typ}"
    if typ in (401, 403):
        return "private", f"guid {typ}"
    if not isinstance(typ, str) or typ in ("error", "unknown"):
        return "error", f"guid {typ} {rid}"
    if typ == "files":
        code, d = get(q(f"{OSF}/files/{rid}/", key))
        size = d.get("data", {}).get("attributes", {}).get("size") if code == 200 else None
        return ("alive" if size else ("gone" if code in (404, 410) else "empty")), f"file {code} size {size}"
    if typ == "preprints":
        code, d = get(q(f"{OSF}/preprints/{rid}/", key))
        if code in (404, 410):
            return "gone", f"preprint {code}"
        if code in (401, 403):
            return "private", f"preprint {code}"
        pf = d.get("data", {}).get("relationships", {}).get("primary_file", {}).get("links", {}).get("related", {}).get("href")
        if not pf:
            return "empty", f"preprint {code}, no primary file"
        c2, f = get(q(pf, key))
        size = f.get("data", {}).get("attributes", {}).get("size") if c2 == 200 else None
        return ("alive" if size else "empty"), f"preprint primary file size {size}"
    base = f"{OSF}/{typ}/{rid}"
    code, d = get(q(base + "/", key))
    if code in (401, 403):
        return "private", f"{typ} {code}"
    if code != 200:
        return ("gone" if code in (404, 410) else "error"), f"{typ} {code}"
    code, prov = get(q(base + "/files/", key))
    counts = {}
    for pr in prov.get("data", []):
        name = pr["attributes"].get("provider") or pr["attributes"].get("name") or pr.get("id", "?")
        c2, f = get(q(pr["relationships"]["files"]["links"]["related"]["href"], key))
        counts[name] = (f.get("links", {}).get("meta", {}) or f.get("meta", {})).get("total", len(f.get("data", [])))
    c3, ch = get(q(base + "/children/", key))
    nchild = (ch.get("links", {}).get("meta", {}) or ch.get("meta", {})).get("total", len(ch.get("data", [])))
    own = counts.get("osfstorage", 0)
    addon = sum(v for k, v in counts.items() if k != "osfstorage")
    detail = f"{typ} providers {counts} children {nchild}"
    if own > 0 or nchild > 0:
        return "alive", detail
    if addon > 0:
        return "pointer-only", detail
    return "empty", detail


def gh_check(owner, repo, commit):
    r = subprocess.run(["gh", "api", f"repos/{owner}/{repo}", "--jq", "[.size,.archived,.private]|@tsv"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return ("gone" if "404" in (r.stderr + r.stdout) or "Not Found" in (r.stderr + r.stdout) else "error"), r.stderr.strip()[:80]
    size, archived, private = r.stdout.strip().split("\t")
    detail = f"size {size}KB archived {archived}"
    if commit:
        c = subprocess.run(["gh", "api", f"repos/{owner}/{repo}/commits/{commit}", "--jq", ".sha"], capture_output=True, text=True)
        detail += f" pinned {commit[:10]} {'ok' if c.returncode == 0 else 'MISSING'}"
        if c.returncode != 0:
            return "gone", detail
    return ("alive" if int(size or 0) > 0 else "empty"), detail


OSF_RE = re.compile(r"osf\.io/(?:download/)?([a-z0-9]{5})(?![a-z0-9])", re.I)
KEY_RE = re.compile(r"view_only=([0-9a-f]{32})")
GH_RE = re.compile(r"github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)")


def controls():
    # 2026-11-12: 'zq9x7', first used as "invented", is a REAL object (its /guids/ redirect resolves; 5-char base-36
    # GUIDs are dense). zz8qv and p0w9j were checked to 404 on /nodes/ the same day. jmrqw is public now (200 without its key),
    # so "without key -> private" was not a known answer and is not a control.
    res = {
        "invented osf zz8qv": osf_check("zz8qv", None)[0] == "gone",
        "invented osf p0w9j": osf_check("p0w9j", None)[0] == "gone",
        "invented github": gh_check("maria-zoo-invented", "no-such-repo-2026", None)[0] == "gone",
        "openai/codex": gh_check("openai", "codex", None)[0] == "alive",
        "jmrqw node with key": osf_check("jmrqw", "7fa3c3d085c743998cd8b1ebe92d74b4")[0] == "alive",
        "ky37d file guid": osf_check("ky37d", "7fa3c3d085c743998cd8b1ebe92d74b4")[0] == "alive",
        "hf297 preprint": osf_check("hf297", None)[0] == "alive",
    }
    print("CONTROLS", json.dumps(res))
    return all(res.values())


def main():
    root = sys.argv[1]
    if not controls():
        sys.exit("a known-answer control failed: nothing is reported")
    out = []
    for p in sorted(glob.glob(os.path.join(root, "papers", "*", "paper.json"))):
        d = json.load(open(p, encoding="utf-8"))
        if d["id"].startswith("maria2026"):
            continue
        for a in d.get("artifacts", []):
            loc = a.get("locator", "") or ""
            key = (KEY_RE.search(loc) or [None, None])[1]
            m_osf, m_gh = OSF_RE.search(loc), GH_RE.search(loc)
            if m_osf and m_osf.group(1).lower() not in ("api", "files", "www"):
                cls, det = osf_check(m_osf.group(1).lower(), key)
                host = "osf"
            elif m_gh:
                repo = m_gh.group(2).removesuffix(".git")
                sha = re.match(r"\s*([0-9a-f]{7,40})\b", a.get("repo_commit") or "")
                cls, det = gh_check(m_gh.group(1), repo, sha.group(1) if sha else None)
                if a.get("repo_commit") and not sha:
                    det += f" (repo_commit is not a SHA: {a['repo_commit'][:40]!r})"
                host = "github"
            else:
                continue
            out.append({"record": d["id"], "artifact": a["id"], "role": a.get("role"), "recorded_status": a.get("status"),
                        "checked_on": (a.get("checked") or {}).get("on"), "host": host, "now": cls, "detail": det})
            print(f"{d['id'][:42]:42s} {a['id']:4s} {host:6s} recorded {a.get('status', ''):24s} now {cls:12s} {det[:90]}", flush=True)
    here = os.path.dirname(os.path.abspath(__file__))
    json.dump(out, open(os.path.join(here, "out", "a2_corpus_recheck.json"), "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
