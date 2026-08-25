"""Who ships a built environment, and does it go with an artifact that runs?

WHY. "Containerise your artifact" is Trisovic et al.'s recommendation #4 and the
one with the best theoretical case. Trisovic could not test it: her Harvard
Dataverse corpus contains **9 Dockerfiles in 2,060 packages**, and on that basis
this house recorded that the recommendation "has never been tried at a scale
anyone could measure". This script shows that conclusion was about the corpus,
not about the world.

WHAT THIS CAN AND CANNOT ESTABLISH -- read before quoting anything below.

The Samuel & Mietchen pipeline **never uses a repository's Dockerfile.** It
builds its own conda or raw-python environment from the declared dependencies
(mode 3) or from an anaconda base (mode 5). So the presence of a Dockerfile is
not a treatment here; it cannot raise or lower the measured success rate through
any causal path involving containers.

What it can be is a **marker**: does an artifact whose authors bothered to ship a
container run better *by other means*? That is a real question -- it asks whether
containerisation is a signal of a well-formed artifact -- and it is emphatically
NOT the question "does shipping a container help a reader". Nothing here bears on
that. The study that would is still unwritten, and would have to actually build
the images.

OUTCOMES. Two, both untouched by the vacuous-comparison defect recorded in
`papers/maria2026-vacuous-reproduction-flag/`:
  install_ok  -- at least one execution in the repository got past
                 `<Install Dependency Error>` (mode 3 only; mode 5 has no
                 install step)
  ran_ok      -- at least one execution finished with no error reason AND
                 actually executed a cell (`count > 0`). The `count > 0` is the
                 correction; without it 815 of 1,203 "successes" ran nothing.

Data: db2023.sqlite. Regeneration command in
`papers/maria2026-vacuous-reproduction-flag/reanalysis/vacuous_flag.py`.
Usage:  python env_markers.py /path/to/db2023.sqlite
"""
import collections
import math
import re
import sqlite3
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "..", "tools"))
from statlib import logit_fit          # noqa: E402

MARKERS = {
    "Dockerfile":      r"(^|/)dockerfile(\.[^/]*)?$",
    "docker-compose":  r"(^|/)docker-compose\.ya?ml$",
    "Singularity":     r"(^|/)singularity(\.[^/]*)?$",
    "environment.yml": r"(^|/)environment\.ya?ml$",
    "Pipfile.lock":    r"(^|/)pipfile\.lock$",
    "poetry.lock":     r"(^|/)poetry\.lock$",
    "renv.lock":       r"(^|/)renv\.lock$",
    "binder dir":      r"(^|/)\.?binder/",
    "devcontainer":    r"(^|/)\.devcontainer",
    "pyproject.toml":  r"(^|/)pyproject\.toml$",
    "Makefile":        r"(^|/)makefile$",
    "nix":             r"(^|/)(default|shell|flake)\.nix$",
    "CITATION.cff":    r"(^|/)citation\.cff$",
}
ANY_BUILT = ("Dockerfile", "docker-compose", "Singularity", "Pipfile.lock",
             "poetry.lock", "renv.lock", "nix", "devcontainer")


def scan(c):
    comp = {k: re.compile(v) for k, v in MARKERS.items()}
    hits = collections.defaultdict(set)
    n = 0
    for rid, path in c.execute("select repository_id, path from repository_files"):
        n += 1
        p = (path or "").lower()
        for k, rx in comp.items():
            if rx.search(p):
                hits[k].add(rid)
    return hits, n


def main(path):
    c = sqlite3.connect(path)
    nrepo = c.execute("select count(*) from repositories").fetchone()[0]
    hits, npaths = scan(c)

    print("PREVALENCE  (%d paths over %d repositories)" % (npaths, nrepo))
    print("  %-17s %6s %8s" % ("marker", "repos", "%"))
    for k in MARKERS:
        print("  %-17s %6d %7.2f%%" % (k, len(hits[k]), 100.0 * len(hits[k]) / nrepo))
    anyb = set().union(*[hits[k] for k in ANY_BUILT])
    print("  %-17s %6d %7.2f%%" % ("ANY built/locked", len(anyb), 100.0 * len(anyb) / nrepo))
    print()
    print("  For contrast, Trisovic et al. 2022 on Harvard Dataverse: 9 Dockerfiles")
    print("  in 2,060 packages = 0.44%%. Here: %.2f%%, a factor of %.0f."
          % (100.0 * len(hits["Dockerfile"]) / nrepo,
             (len(hits["Dockerfile"]) / nrepo) / (9.0 / 2060)))
    print("  Same recommendation, same era, two corpora of research artifacts.")
    print("  WHERE YOU LOOK DECIDES WHETHER THE RECOMMENDATION IS TESTABLE AT ALL.")

    # ---- outcomes, per repository, per arm
    outc = {}
    for rid, mode, n, inst_ok, ran_ok in c.execute(
            "select repository_id, mode, count(*), "
            "sum(processed != 0), "
            "sum(reason is null and (processed & 44) = 32 and count > 0) "
            "from executions group by repository_id, mode"):
        outc[(rid, mode)] = (n, inst_ok, ran_ok)

    print()
    print("ASSOCIATION -- marker present vs absent, per arm.  NOT a treatment effect:")
    print("the pipeline never uses these files. Read as 'is this a marker of an")
    print("artifact that runs by other means'.")
    for mode, lab, outidx in ((3, "mode 3 (deps declared)  install got past the error", 1),
                              (3, "mode 3 (deps declared)  a notebook ran >=1 cell clean", 2),
                              (5, "mode 5 (nothing declared) a notebook ran >=1 cell clean", 2)):
        rows = [(rid, v) for (rid, m), v in outc.items() if m == mode]
        print()
        print("  %s   [%d repositories]" % (lab, len(rows)))
        print("    %-17s %6s %7s | %6s %7s | %8s" %
              ("marker", "n+", "rate+", "n-", "rate-", "log OR"))
        for k in list(MARKERS) + ["ANY built/locked"]:
            hs = anyb if k == "ANY built/locked" else hits[k]
            a = [v for rid, v in rows if rid in hs]
            b = [v for rid, v in rows if rid not in hs]
            if len(a) < 10:
                continue
            ra = sum(1 for v in a if v[outidx] > 0) / len(a)
            rb = sum(1 for v in b if v[outidx] > 0) / len(b)
            # Haldane-corrected log odds ratio + SE
            a1 = sum(1 for v in a if v[outidx] > 0) + 0.5
            a0 = len(a) - a1 + 1.0
            b1 = sum(1 for v in b if v[outidx] > 0) + 0.5
            b0 = len(b) - b1 + 1.0
            lor = math.log((a1 / a0) / (b1 / b0))
            se = math.sqrt(1 / a1 + 1 / a0 + 1 / b1 + 1 / b0)
            star = "*" if abs(lor / se) > 1.96 else " "
            print("    %-17s %6d %6.1f%% | %6d %6.1f%% | %+7.2f +/-%.2f%s"
                  % (k, len(a), 100 * ra, len(b), 100 * rb, lor, 1.96 * se, star))
        print("    * = 95%% interval excludes 0.  No multiplicity correction; with "
              "%d markers" % (len(MARKERS) + 1))
        print("    tested, expect about %.1f false positives per arm at alpha = 0.05."
              % (0.05 * (len(MARKERS) + 1)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "db2023.sqlite"))
