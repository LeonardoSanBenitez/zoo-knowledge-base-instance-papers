"""
Does pinning your dependency versions actually make your code re-executable?

Author: maria, 2026-08-24. Stdlib only.

WHY
---
"Capture your library versions" is the first recommendation of essentially every
paper in this literature. Trisovic et al. 2022 lead with it (`renv`, DESCRIPTION,
`sessionInfo()`). Samuel & Mietchen 2024 conclude that the large majority of
notebooks fail "mostly due to issues with the documentation of dependencies".
Pimentel et al. 2019 recommend it. Every "ten simple rules" paper repeats it.

I have not found anyone who tested it, at scale, against an actual re-execution
outcome. The Samuel & Mietchen archive makes it testable, because it ships both
the verbatim CONTENT of every requirement file and the per-notebook execution
outcome:

    requirement_files(repository_id, name, reqformat, content)
    executions(repository_id, notebook_id, reason, processed)

So: classify each repository by how tightly its Python requirements are pinned,
then compare re-execution success. The unit is the REPOSITORY, because
cluster_and_age.py measured ICC = 0.435 for this outcome -- a repository is close
to one Bernoulli trial, not to m independent ones.

TWO WAYS THIS COULD FOOL ME, both tested below:
  1. Confounding by repository quality. A repo that pins is a repo that cares.
     Stratify on a crude quality proxy (stars, releases, licence) and see if the
     association survives.
  2. Confounding by dependency count. Pinned repos might simply depend on less.
     Adjust for the number of declared requirements.

And the direction that matters most is NOT the one everybody assumes. A pin says
"install exactly numpy==1.16.4". In 2021-23, on a modern Python, that build can
FAIL where an unpinned `numpy` would have installed fine. So the prior should be
genuinely two-sided, and the outcome is split into the two stages the pipeline
separates: did the environment install at all, and given that, did the notebook run.

DATA: see cluster_and_age.py for the fetch command. 371 MB, not kept.
"""

import math
import os
import re
import sqlite3
from collections import Counter, defaultdict

DB_PATH = os.environ.get(
    "CRPMC_DB",
    r"C:/tmp/crpmcdb/computational-reproducibility-pmc/computational-reproducibility-pmc/analyses/db.sqlite",
)

MASK_FINISHED = 32 + 8 + 4
BIT_SAME = 16

PIN_EXACT = re.compile(r"==|===")
PIN_RANGE = re.compile(r">=|<=|~=|>|<|!=")


def classify_requirements(content):
    """Return (n_specs, n_exact, n_range) for a requirements.txt-style file."""
    n = exact = rng = 0
    for raw in (content or "").splitlines():
        line = raw.split("#")[0].strip()
        if not line or line.startswith("-"):
            continue
        if line.startswith(("git+", "http://", "https://")):
            n += 1
            continue
        n += 1
        if PIN_EXACT.search(line):
            exact += 1
        elif PIN_RANGE.search(line):
            rng += 1
    return n, exact, rng


def load():
    con = sqlite3.connect(DB_PATH)

    # repository -> execution outcomes
    repo = defaultdict(lambda: {"att": 0, "fin": 0, "same": 0, "depfail": 0})
    q = "SELECT repository_id, reason, processed FROM executions"
    for rid, reason, processed in con.execute(q):
        if reason == "<Skipping notebook>":
            continue
        processed = processed or 0
        d = repo[rid]
        d["att"] += 1
        d["depfail"] += (reason == "<Install Dependency Error>")
        fin = (processed & MASK_FINISHED) == 32
        d["fin"] += fin
        d["same"] += fin and (processed & BIT_SAME) == BIT_SAME

    # repository -> requirement pinning
    reqs = defaultdict(lambda: {"n": 0, "exact": 0, "range": 0,
                                "has_txt": False, "has_setup": False, "has_lock": False})
    for rid, name, fmt, content in con.execute(
            "SELECT repository_id, name, reqformat, content FROM requirement_files"):
        r = reqs[rid]
        nm = (name or "").lower()
        if "pipfile.lock" in nm:
            r["has_lock"] = True
            continue
        if nm.endswith("setup.py"):
            r["has_setup"] = True
            continue
        if "requirements" in nm or nm.endswith(".txt"):
            r["has_txt"] = True
            n, e, g = classify_requirements(content)
            r["n"] += n
            r["exact"] += e
            r["range"] += g

    meta = {}
    for rid, created, stars, forks, rel, lic, arch, commits in con.execute(
        "SELECT repository_id, created_at, stargazers_count, forks_count, "
        "total_releases, license_key, archived, total_commits_after_published_date "
        "FROM repository_data"
    ):
        meta[rid] = {"year": int(created[:4]) if created else None,
                     "stars": stars or 0, "forks": forks or 0,
                     "releases": rel or 0, "license": lic,
                     "archived": arch, "commits_after": commits or 0}
    con.close()
    return repo, reqs, meta


def bucket(r):
    """Pinning class for a repository with a requirements-style file."""
    if r["has_lock"]:
        return "pipfile.lock (fully locked)"
    if not r["has_txt"] or r["n"] == 0:
        return "no requirements.txt"
    frac = r["exact"] / r["n"]
    if frac >= 0.9:
        return "requirements.txt, >=90% exact pins"
    if frac >= 0.5:
        return "requirements.txt, 50-90% exact pins"
    if r["exact"] + r["range"] == 0:
        return "requirements.txt, no version constraints at all"
    return "requirements.txt, <50% exact pins"


ORDER = ["requirements.txt, no version constraints at all",
         "requirements.txt, <50% exact pins",
         "requirements.txt, 50-90% exact pins",
         "requirements.txt, >=90% exact pins",
         "pipfile.lock (fully locked)",
         "no requirements.txt"]


def se_prop(k, n):
    if n == 0:
        return float("nan")
    p = k / n
    return math.sqrt(p * (1 - p) / n)


def two_prop_z(k1, n1, k2, n2):
    if n1 == 0 or n2 == 0:
        return float("nan")
    p1, p2 = k1 / n1, k2 / n2
    p = (k1 + k2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    return (p1 - p2) / se if se else float("nan")


def norm_sf(z):
    return 0.5 * math.erfc(abs(z) / math.sqrt(2))


def table(groups, label, num, den):
    print("  %-46s %8s %8s %10s" % (label, "k", "n", "rate"))
    for b in ORDER:
        g = groups.get(b)
        if not g:
            continue
        k = sum(x[num] for x in g)
        n = sum(x[den] for x in g)
        if n == 0:
            continue
        print("  %-46s %8d %8d %7.1f%% +- %.1f"
              % (b, k, n, 100.0 * k / n, 100 * se_prop(k, n)))
    print()


def main():
    repo, reqs, meta = load()

    # repository-level records, restricted to repos that were actually attempted
    recs = []
    for rid, d in repo.items():
        if d["att"] == 0:
            continue
        r = reqs.get(rid, {"n": 0, "exact": 0, "range": 0,
                           "has_txt": False, "has_setup": False, "has_lock": False})
        m = meta.get(rid, {})
        recs.append({
            "rid": rid, "bucket": bucket(r), "n_specs": r["n"],
            "att": d["att"], "fin": d["fin"], "same": d["same"],
            "depfail": d["depfail"],
            "env_ok": 1 if d["depfail"] < d["att"] else 0,     # at least one env built
            "any_fin": 1 if d["fin"] > 0 else 0,
            "any_same": 1 if d["same"] > 0 else 0,
            "one": 1,
            "stars": m.get("stars", 0), "releases": m.get("releases", 0),
            "exact_frac": (r["exact"] / r["n"]) if r["n"] else 0.0,
            "license": m.get("license"), "year": m.get("year"),
        })

    print("=" * 78)
    print("DOES PINNING DEPENDENCY VERSIONS PREDICT RE-EXECUTION?")
    print("Unit = repository (ICC of the outcome within repositories is 0.435)")
    print("=" * 78)
    print("  %d repositories with at least one attempted execution" % len(recs))
    print()

    groups = defaultdict(list)
    for r in recs:
        groups[r["bucket"]].append(r)

    print("STAGE 1 -- did the declared environment install at all?")
    table(groups, "pinning class", "env_ok", "one")

    print("STAGE 2 -- given a repository, did ANY notebook run end to end?")
    table(groups, "pinning class", "any_fin", "one")

    print("STAGE 3 -- did ANY notebook run AND match its recorded output?")
    table(groups, "pinning class", "any_same", "one")

    # headline contrast: heavily pinned vs unconstrained
    hi = groups.get("requirements.txt, >=90% exact pins", [])
    lo = groups.get("requirements.txt, no version constraints at all", [])
    mid = (groups.get("requirements.txt, <50% exact pins", []) +
           groups.get("requirements.txt, 50-90% exact pins", []))
    print("=" * 78)
    print("HEADLINE CONTRASTS")
    print("=" * 78)
    for stage in ("env_ok", "any_fin", "any_same"):
        k1, n1 = sum(x[stage] for x in hi), len(hi)
        k2, n2 = sum(x[stage] for x in lo), len(lo)
        z = two_prop_z(k1, n1, k2, n2)
        print("  %-8s  >=90%% pinned %d/%d = %5.1f%%   vs   unconstrained %d/%d = %5.1f%%"
              % (stage, k1, n1, 100.0 * k1 / max(n1, 1), k2, n2, 100.0 * k2 / max(n2, 1)))
        print("            two-proportion z = %+.2f, p = %.3f" % (z, 2 * norm_sf(z)))
    print()

    # ---- confound 1: number of declared requirements ----
    print("=" * 78)
    print("CONFOUND 1 -- does pinning just track HOW MANY things you depend on?")
    print("=" * 78)
    withreq = [r for r in recs if r["n_specs"] > 0]
    withreq.sort(key=lambda r: r["n_specs"])
    q = len(withreq) // 3
    strata = [("few deps  (n_specs %d-%d)" % (withreq[0]["n_specs"], withreq[q - 1]["n_specs"]), withreq[:q]),
              ("mid deps  (n_specs %d-%d)" % (withreq[q]["n_specs"], withreq[2 * q - 1]["n_specs"]), withreq[q:2 * q]),
              ("many deps (n_specs %d-%d)" % (withreq[2 * q]["n_specs"], withreq[-1]["n_specs"]), withreq[2 * q:])]
    for name, st in strata:
        pinned = [r for r in st if r["bucket"] == "requirements.txt, >=90% exact pins"]
        other = [r for r in st if r["bucket"] != "requirements.txt, >=90% exact pins"]
        k1, n1 = sum(x["any_fin"] for x in pinned), len(pinned)
        k2, n2 = sum(x["any_fin"] for x in other), len(other)
        print("  %-34s pinned %3d/%-3d = %5.1f%%   other %3d/%-3d = %5.1f%%   z=%+.2f"
              % (name, k1, n1, 100.0 * k1 / max(n1, 1), k2, n2, 100.0 * k2 / max(n2, 1),
                 two_prop_z(k1, n1, k2, n2)))
    print()
    print("  and the raw association of dependency COUNT with success:")
    for name, st in strata:
        k, n = sum(x["any_fin"] for x in st), len(st)
        print("  %-34s %3d/%-3d = %5.1f%%" % (name, k, n, 100.0 * k / max(n, 1)))
    print()

    # ---- confound 2: repository care proxies ----
    print("=" * 78)
    print("CONFOUND 2 -- is pinning a proxy for 'this repository is maintained'?")
    print("=" * 78)
    for proxy, fn in (("has a licence", lambda r: bool(r["license"]) and r["license"] != "other"),
                      ("has >=1 release", lambda r: r["releases"] >= 1),
                      ("has >=10 stars", lambda r: r["stars"] >= 10)):
        a = [r for r in recs if fn(r)]
        b = [r for r in recs if not fn(r)]
        ka, na = sum(x["any_fin"] for x in a), len(a)
        kb, nb = sum(x["any_fin"] for x in b), len(b)
        print("  %-16s yes %3d/%-4d = %5.1f%%   no %3d/%-4d = %5.1f%%   z=%+.2f"
              % (proxy, ka, na, 100.0 * ka / max(na, 1), kb, nb, 100.0 * kb / max(nb, 1),
                 two_prop_z(ka, na, kb, nb)))
    print()
    print("  stratified: >=90%-pinned vs everything else, WITHIN each proxy level")
    for proxy, fn in (("has a licence", lambda r: bool(r["license"]) and r["license"] != "other"),
                      ("has >=1 release", lambda r: r["releases"] >= 1),
                      ("has >=10 stars", lambda r: r["stars"] >= 10)):
        for val in (True, False):
            st = [r for r in recs if fn(r) == val]
            pinned = [r for r in st if r["bucket"] == "requirements.txt, >=90% exact pins"]
            other = [r for r in st if r["bucket"] != "requirements.txt, >=90% exact pins"]
            k1, n1 = sum(x["any_fin"] for x in pinned), len(pinned)
            k2, n2 = sum(x["any_fin"] for x in other), len(other)
            print("    %-16s = %-5s  pinned %3d/%-4d = %5.1f%%   other %3d/%-4d = %5.1f%%   z=%+.2f"
                  % (proxy, val, k1, n1, 100.0 * k1 / max(n1, 1),
                     k2, n2, 100.0 * k2 / max(n2, 1), two_prop_z(k1, n1, k2, n2)))
    print()
    adjusted(recs)


def fisher_exact_2x2(a, b, c, d):
    """Two-sided Fisher exact p for [[a,b],[c,d]]."""
    def lc(n, k):
        return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
    n = a + b + c + d
    r1, r2, c1 = a + b, c + d, a + c
    def prob(x):
        return math.exp(lc(r1, x) + lc(r2, c1 - x) - lc(n, c1))
    p0 = prob(a)
    tot = 0.0
    lo = max(0, c1 - r2)
    hi = min(r1, c1)
    for x in range(lo, hi + 1):
        p = prob(x)
        if p <= p0 * (1 + 1e-9):
            tot += p
    return min(tot, 1.0)


def logit_fit(X, y, iters=400):
    """Plain Newton-Raphson logistic regression. X includes an intercept column.
    Returns (beta, se)."""
    p = len(X[0])
    b = [0.0] * p
    H = None
    for _ in range(iters):
        g = [0.0] * p
        H = [[0.0] * p for _ in range(p)]
        for xi, yi in zip(X, y):
            eta = sum(bj * xj for bj, xj in zip(b, xi))
            eta = max(-30.0, min(30.0, eta))
            mu = 1.0 / (1.0 + math.exp(-eta))
            w = mu * (1 - mu)
            for j in range(p):
                g[j] += (yi - mu) * xi[j]
                for k in range(p):
                    H[j][k] += w * xi[j] * xi[k]
        # ridge for stability at these sample sizes
        for j in range(p):
            H[j][j] += 1e-6
        step = solve(H, g)
        if step is None:
            break
        b = [bj + s for bj, s in zip(b, step)]
        if max(abs(s) for s in step) < 1e-10:
            break
    inv = invert(H)
    se = [math.sqrt(inv[j][j]) if inv and inv[j][j] > 0 else float("nan") for j in range(p)]
    return b, se


def solve(A, v):
    n = len(A)
    M = [row[:] + [v[i]] for i, row in enumerate(A)]
    for i in range(n):
        piv = max(range(i, n), key=lambda r: abs(M[r][i]))
        if abs(M[piv][i]) < 1e-14:
            return None
        M[i], M[piv] = M[piv], M[i]
        d = M[i][i]
        M[i] = [x / d for x in M[i]]
        for r in range(n):
            if r != i and M[r][i] != 0:
                f = M[r][i]
                M[r] = [x - f * y for x, y in zip(M[r], M[i])]
    return [M[i][n] for i in range(n)]


def invert(A):
    if A is None:
        return None
    n = len(A)
    M = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(A)]
    for i in range(n):
        piv = max(range(i, n), key=lambda r: abs(M[r][i]))
        if abs(M[piv][i]) < 1e-14:
            return None
        M[i], M[piv] = M[piv], M[i]
        d = M[i][i]
        M[i] = [x / d for x in M[i]]
        for r in range(n):
            if r != i and M[r][i] != 0:
                f = M[r][i]
                M[r] = [x - f * y for x, y in zip(M[r], M[i])]
    return [row[n:] for row in M]


def adjusted(recs):
    """Restrict to repositories that DECLARED requirements -- the only arm where
    pinning is even defined -- and adjust for dependency count and care proxies."""
    sub = [r for r in recs if r["n_specs"] > 0]
    print("=" * 78)
    print("THE COMPARISON THAT IS ACTUALLY LIKE-FOR-LIKE")
    print("=" * 78)
    print("  Repositories WITHOUT a requirements file are not a control group: the")
    print("  pipeline gives them a large default conda environment instead, which is a")
    print("  different treatment. They are dropped here.")
    print("  n = %d repositories that declared requirements, %d with >=1 notebook that ran."
          % (len(sub), sum(r["any_fin"] for r in sub)))
    print()
    hi = [r for r in sub if r["n_specs"] and r["exact_frac"] >= 0.9]
    lo = [r for r in sub if r["n_specs"] and r["exact_frac"] < 0.9]
    a = sum(r["any_fin"] for r in hi); b = len(hi) - a
    c = sum(r["any_fin"] for r in lo); d = len(lo) - c
    print("  2x2, outcome = repository has >=1 notebook that ran end to end")
    print("      >=90%% exact pins : %d ran / %d   = %5.1f%%" % (a, len(hi), 100.0 * a / len(hi)))
    print("      < 90%% exact pins : %d ran / %d   = %5.1f%%" % (c, len(lo), 100.0 * c / len(lo)))
    print("      Fisher exact two-sided p = %.4f" % fisher_exact_2x2(a, b, c, d))
    print("      odds ratio = %.3f" % ((a / max(b, 1)) / max(c / max(d, 1), 1e-9)))
    print()

    X, y = [], []
    for r in sub:
        X.append([1.0,
                  r["exact_frac"],
                  math.log(1 + r["n_specs"]),
                  1.0 if (r["license"] and r["license"] != "other") else 0.0,
                  math.log(1 + r["stars"])])
        y.append(float(r["any_fin"]))
    names = ["intercept", "fraction of specs exactly pinned", "log(1+n_specs)",
             "has a licence", "log(1+stars)"]
    b, se = logit_fit(X, y)
    print("  logistic regression, outcome = repository has >=1 notebook that ran")
    print("  %-34s %9s %9s %8s %10s" % ("term", "beta", "SE", "z", "OR"))
    for nm, bi, si in zip(names, b, se):
        z = bi / si if si and si == si else float("nan")
        print("  %-34s %+9.3f %9.3f %+8.2f %10.3f" % (nm, bi, si, z, math.exp(bi)))
    print()
    print("  Read the pinning row and nothing else. n = %d with %d events; every other"
          % (len(sub), int(sum(y))))
    print("  coefficient here is under-powered and is present only as an adjustment.")
    print()


if __name__ == "__main__":
    main()
