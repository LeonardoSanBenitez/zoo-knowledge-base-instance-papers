"""p3 helper -- list 84000 data-tei Kangyur translation files at a pinned commit, with their Toh numbers and titles.

    python -I p3_list_84000.py <commit_sha> > out/p3_84000_kangyur_files.tsv
Author: maria, 2026-11-12.
"""
import json
import re
import subprocess
import sys

sha = sys.argv[1]
r = subprocess.run(["gh", "api", f"repos/84000/data-tei/git/trees/{sha}?recursive=1"], capture_output=True, text=True, encoding="utf-8")
tree = json.loads(r.stdout)
assert not tree.get("truncated"), "tree truncated: list per directory instead"
rows = [(t["path"], t.get("size", 0)) for t in tree["tree"]
        if t["type"] == "blob" and re.match(r"translations/kangyur/translations/.*\.xml$", t["path"])]
for p, s in sorted(rows):
    print(f"{p}\t{s}")
sys.stderr.write(f"{len(rows)} files\n")
