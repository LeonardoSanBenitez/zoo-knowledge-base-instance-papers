"""Is a shipped container a SUBSTITUTE for a complete declared environment?

env_markers.py found that repositories shipping a Dockerfile install their
DECLARED dependencies less often than repositories that do not (28.8% vs 37.6%),
and that repositories shipping an `environment.yml` install them MORE often
(44.2% vs 34.6%). Two opposite signs among things that both look like "the
authors took care of the environment".

The mechanism that would explain both: **a container absorbs the complexity that
a requirements file would otherwise have to express.** If your Dockerfile does
the `apt-get install libgdal-dev`, sets the compiler, and pins the base image,
your `requirements.txt` never has to be self-sufficient and quietly stops being
so. An `environment.yml` is the opposite -- it is a *more complete declaration*,
carrying channels and non-Python packages, not a substitute for one.

If that is right, "ship a container AND a requirements.txt" is not belt and
braces. The presence of the container predicts that the requirements file alone
will not work.

THE CONFOUND THAT HAS TO BE RULED OUT FIRST. Earlier the same day, on the same
corpus, the apparent penalty for *pinning* turned out to be dependency COUNT in
disguise (`pins_vs_count.py`). Repositories that ship a Dockerfile are plausibly
larger and declare more dependencies, and dependency count is the strongest
predictor of install failure there is. So every model below carries
log1p(n_deps), and the unadjusted and adjusted coefficients are printed side by
side. If the marker coefficient collapses when the count enters, the finding is
the count again and must be reported as such.

Usage:  python container_substitution.py /path/to/db2023.sqlite
"""
import collections
import math
import os
import re
import sqlite3
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "..", "tools"))
from statlib import logit_fit          # noqa: E402

NAME = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")
MARK = {
    "Dockerfile":      r"(^|/)dockerfile(\.[^/]*)?$",
    "environment.yml": r"(^|/)environment\.ya?ml$",
    "Makefile":        r"(^|/)makefile$",
    "CITATION.cff":    r"(^|/)citation\.cff$",
    "pyproject.toml":  r"(^|/)pyproject\.toml$",
}


def build(path):
    c = sqlite3.connect(path)
    comp = {k: re.compile(v) for k, v in MARK.items()}
    hits = collections.defaultdict(set)
    for rid, p in c.execute("select repository_id, path from repository_files"):
        pl = (p or "").lower()
        for k, rx in comp.items():
            if rx.search(pl):
                hits[k].add(rid)
    deps = collections.Counter()
    nfiles = collections.Counter()
    for rid, content in c.execute(
            "select repository_id, content from requirement_files "
            "where reqformat='requirements.txt' and content is not null"):
        nfiles[rid] += 1
        for line in content.splitlines():
            ls = line.strip()
            if ls and ls[0] not in "#-" and NAME.match(ls):
                deps[rid] += 1
    size = collections.Counter()
    for rid, n in c.execute("select repository_id, count(*) from repository_files group by 1"):
        size[rid] = n
    rows = []
    for rid, n, ok in c.execute(
            "select repository_id, count(*), sum(processed != 0) from executions "
            "where mode = 3 group by 1"):
        if deps[rid] == 0:
            continue
        rows.append(dict(rid=rid, install_ok=1 if ok > 0 else 0,
                         deps=deps[rid], reqfiles=nfiles[rid], files=size[rid],
                         **{k: (1 if rid in hits[k] else 0) for k in MARK}))
    return rows


def fit(rows, marker, extra):
    import numpy as np
    y = np.array([r["install_ok"] for r in rows], float)
    cols, names = [np.array([r[marker] for r in rows], float)], [marker]
    for e in extra:
        cols.append(np.array([math.log1p(r[e]) for r in rows]))
        names.append("log1p(%s)" % e)
    f = logit_fit(np.column_stack(cols), y)
    return f, names


def main(path):
    rows = build(path)
    print("repositories with a requirements.txt and mode-3 executions: %d" % len(rows))
    print("outcome: at least one execution got past `<Install Dependency Error>`")
    print("         base rate %.1f%%" % (100.0 * sum(r["install_ok"] for r in rows) / len(rows)))
    print()
    print("Is the marker confounded with size? mean declared dependencies and mean")
    print("files in the repository, by marker:")
    print("  %-16s %8s %10s %10s | %8s %10s %10s"
          % ("marker", "n+", "deps+", "files+", "n-", "deps-", "files-"))
    for k in MARK:
        a = [r for r in rows if r[k]]
        b = [r for r in rows if not r[k]]
        if not a:
            continue
        m = lambda z, f: sum(x[f] for x in z) / len(z)
        print("  %-16s %8d %10.1f %10.0f | %8d %10.1f %10.0f"
              % (k, len(a), m(a, "deps"), m(a, "files"), len(b), m(b, "deps"), m(b, "files")))
    print()
    print("UNADJUSTED vs ADJUSTED coefficient on the marker (logit, install_ok)")
    print("  %-16s %20s %22s %20s"
          % ("marker", "unadjusted", "+ log1p(deps)", "+ log1p(deps)+log1p(files)"))
    for k in MARK:
        out = []
        for extra in ([], ["deps"], ["deps", "files"]):
            f, names = fit(rows, k, extra)
            b, se, p = f["beta"][1], f["se"][1], f["p"][1]
            star = "*" if p < 0.05 else " "
            out.append("%+6.2f +/-%.2f%s" % (b, 1.96 * se, star))
        print("  %-16s %20s %22s %20s" % (k, out[0], out[1], out[2]))
    print()
    print("  * = 95%% interval excludes 0. Positive = the marker goes with the")
    print("  DECLARED environment installing more often.")
    print()
    print("READ THE MIDDLE AND RIGHT COLUMNS AGAINST THE LEFT. If a coefficient")
    print("collapses toward zero once dependency count enters, the marker was")
    print("standing in for repository size, exactly as the pinning result was.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "db2023.sqlite"))
