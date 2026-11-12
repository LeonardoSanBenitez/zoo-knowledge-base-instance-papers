"""a3 -- one inside-the-container check that needs no reading of the science: is a recorded file a Git-LFS pointer, and is
its object still served?

For every GitHub artifact with a single-file path_in_repo (globs, lists and directories are skipped and counted):
  gh api repos/<o>/<r>/contents/<path>[?ref=<pin>] -> size and content. A pointer is a small text file starting with
  'version https://git-lfs.github.com/spec/v1'. For a pointer, the media URL media.githubusercontent.com/media/<o>/<r>/<ref>/<path>
  is requested with a HEAD: 200 = object served, 404 = the pointer is all that is left.
Known answers (from the records): kim2025-correlated-errors a1 = LFS pointer whose object is gone (recorded 'dangling', checked at
endpoint level on 2026-09); kim2025 a3 = an ordinary file (recorded 'verified-usable').

    python -I a3_lfs_pointer_check.py <instance-papers dir> > out/a3_lfs_pointer_check.txt
Author: maria, 2026-11-12.
"""
import base64
import glob
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

GH_RE = re.compile(r"github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)")
PIN_RE = re.compile(r"^[0-9a-f]{7,40}$")


def contents(owner, repo, path, ref):
    url = f"repos/{owner}/{repo}/contents/{path}" + (f"?ref={ref}" if ref else "")
    r = subprocess.run(["gh", "api", url], capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        return None, (r.stderr or r.stdout).strip()[:80]
    try:
        return json.loads(r.stdout), None
    except json.JSONDecodeError:
        return None, "not json"


def media_status(owner, repo, ref, path):
    url = f"https://media.githubusercontent.com/media/{owner}/{repo}/{ref}/{path}"
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "zoo-kb-artifact-audit/1.0"})
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:  # noqa: BLE001
        return f"error {type(e).__name__}"


def raw_head(owner, repo, ref, path, n=200):
    """First n bytes as served by raw.githubusercontent.com. 2026-11-12: the CONTENTS API reports an LFS file's size as the
    size of the object its pointer describes (335,231,032 B for kim2025 a1, whose object is gone), so size from the contents
    API cannot detect a pointer. raw serves the pointer text itself."""
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "zoo-kb-artifact-audit/1.0", "Range": f"bytes=0-{n - 1}"})
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status, r.read(n).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # noqa: BLE001
        return f"error {type(e).__name__}", ""


def check(owner, repo, path, pin):
    d, err = contents(owner, repo, path, pin)
    if d is None:
        return "missing", err
    if isinstance(d, list):
        return "skipped-dir", f"{len(d)} entries"
    ref = pin or "HEAD"
    st, head = raw_head(owner, repo, ref, path)
    if head.startswith("version https://git-lfs.github.com/spec/v1"):
        ms = media_status(owner, repo, ref, path)
        return ("lfs-pointer-object-served" if ms == 200 else "lfs-pointer-object-GONE"), \
               f"raw {st}: LFS pointer; contents API size {d.get('size')}; media HEAD {ms}"
    return "ordinary-file", f"raw {st}; contents API size {d.get('size')} B"


def main():
    root = sys.argv[1]
    rows, skipped = [], 0
    for p in sorted(glob.glob(os.path.join(root, "papers", "*", "paper.json"))):
        d = json.load(open(p, encoding="utf-8"))
        for a in d.get("artifacts", []):
            m, path = GH_RE.search(a.get("locator") or ""), a.get("path_in_repo")
            if not (m and path):
                continue
            if any(ch in path for ch in "[]{}*,") or path.endswith("/") or " " in path.strip():
                skipped += 1
                continue
            pin = a.get("repo_commit") if PIN_RE.match(a.get("repo_commit") or "") else None
            cls, det = check(m.group(1), m.group(2).removesuffix(".git"), path.strip(), pin)
            rows.append({"record": d["id"], "artifact": a["id"], "recorded": a.get("status"), "now": cls, "detail": det})
            print(f"{d['id'][:40]:40s} {a['id']:4s} recorded {a.get('status', ''):24s} {cls:28s} {det}", flush=True)
    known = {(r["record"], r["artifact"]): r["now"] for r in rows}
    ctl = {"kim a1 is a dead LFS pointer": known.get(("kim2025-correlated-errors", "a1")) == "lfs-pointer-object-GONE",
           "kim a3 is an ordinary file": known.get(("kim2025-correlated-errors", "a3")) == "ordinary-file"}
    print("CONTROLS", json.dumps(ctl), "| skipped (glob/list/dir paths):", skipped)
    json.dump({"rows": rows, "controls": ctl, "skipped": skipped},
              open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "a3_lfs_pointer_check.json"), "w", encoding="utf-8"), indent=1)
    if not all(ctl.values()):
        sys.exit("a known-answer control failed: the rows above are not to be reported")


if __name__ == "__main__":
    main()
