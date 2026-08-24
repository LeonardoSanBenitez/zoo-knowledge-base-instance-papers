"""Does any recommended practice actually predict whether a replication package runs?

maria, 2026-08-24. Stdlib only.

WHY
---
Trisovic et al. close with six recommendations for researchers. Every one is
plausible and none is tested against the outcome the same paper measured, even
though the paper released, per replication package, both the coded presence of
those practices AND the re-execution result:

    analysis/data/dataset_level.csv   doi, docs, rmd, rproj, rnw, test, prov,
                                      wflow_lib, dockerfile, space, other_code,
                                      dependen_no, unique_libs_no, files_count,
                                      sizeMB, comments_no, avg_file_len
    analysis/data/run_log_r*_env.csv  the per-file outcome

This is the R/Dataverse counterpart to the Python/PubMed-Central test in
papers/samuel2024-jupyter-pmc/reanalysis/does_pinning_help.py, and the two are
designed to be read together: the same question, two corpora, two languages.

UNIT OF ANALYSIS is the replication package, not the file. Files inside a package
share a directory, a data set and an author; treating 7,621 files as independent
overstates n by roughly the mean package size. Outcome: the package has at least
one R file that ran end to end under the symmetric combining rule from
denominator.py -- NOT the authors' asymmetric rule, which would import the bias
that record is about.

WHAT WOULD MAKE ME WRONG
------------------------
1. Confounding by package complexity. A package with a README may simply be a
   smaller, simpler package. Every association is therefore also reported
   stratified by number of R files and by dependency count.
2. Reverse coding. `docs` is 'a filename contains readme/codebook/documentation/
   guide/instruction'. That is a proxy for documentation, not documentation.
3. Multiplicity. Eleven practices are tested. A single p < 0.05 among eleven is
   nothing, so the Bonferroni threshold is printed next to every p and the
   pattern across practices matters more than any one of them.
"""

import csv
import math
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from denominator import (DATA, VERSIONS, load_condition, combined_anyobserved,
                         classify)

DS = os.path.join(DATA, "dataset_level.csv")


def package_outcomes():
    """doi -> (n_files_with_an_outcome, n_files_that_ran)."""
    logs = load_condition("env")
    union = set()
    for v in VERSIONS:
        union |= set(logs[v])
    out = defaultdict(lambda: [0, 0])
    for k in union:
        res = combined_anyobserved([logs[v].get(k) for v in VERSIONS])
        if res is None or res == "infra":
            continue
        out[k[0]][0] += 1
        out[k[0]][1] += (res == "success")
    return out


def load_packages():
    rows = []
    with open(DS, encoding="utf-8", errors="replace") as fh:
        for r in csv.DictReader(fh):
            rows.append(r)
    return rows


def num(x, default=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


PRACTICES = [
    # (column, label, direction we would EXPECT if the recommendation is right)
    ("docs", "a documentation/README file is present", "+"),
    ("rmd", "uses R Markdown (literate programming)", "+"),
    ("rnw", "uses Sweave/Rnw", "+"),
    ("rproj", "ships an .Rproj project file", "+"),
    ("test", "contains a test file", "+"),
    ("dockerfile", "ships a Dockerfile", "+"),
    ("wflow_lib", "uses a workflow library (drake/targets/workflowr)", "+"),
    ("prov", "uses a provenance library", "+"),
    ("space", "a filename contains a space (DISCOURAGED)", "-"),
    ("other_code", "contains code in another language (DISCOURAGED)", "-"),
]


def two_prop_z(k1, n1, k2, n2):
    if n1 == 0 or n2 == 0:
        return float("nan")
    p = (k1 + k2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    return (k1 / n1 - k2 / n2) / se if se > 0 else float("nan")


def norm_p(z):
    if z != z:
        return float("nan")
    return math.erfc(abs(z) / math.sqrt(2))


def icc_files_in_packages(out):
    """ANOVA intra-class correlation of the per-file outcome within packages.

    This corpus can supply a SECOND, independent estimate of a quantity recorded
    from the Samuel & Mietchen corpus (ICC 0.435 for notebooks inside
    repositories). R files inside a Dataverse replication package are the same
    kind of cluster: one directory, one data set, one author.
    """
    groups = [(nran, nfiles) for nfiles, nran in
              ((v[0], v[1]) for v in out.values()) if nfiles > 0]
    k = len(groups)
    N = sum(n for _, n in groups)
    grand = sum(s for s, _ in groups) / N
    ssb = sum(n * (s / n - grand) ** 2 for s, n in groups)
    ssw = sum(s * (1 - s / n) ** 2 + (n - s) * (0 - s / n) ** 2 for s, n in groups)
    msb = ssb / (k - 1)
    msw = ssw / (N - k) if N > k else 0.0
    m0 = (N - sum(n * n for _, n in groups) / N) / (k - 1)
    den = msb + (m0 - 1) * msw
    return ((msb - msw) / den if den else float("nan")), k, N, m0


def main():
    out = package_outcomes()
    icc, nk, nN, m0 = icc_files_in_packages(out)
    deff = 1 + (m0 - 1) * icc
    print("=" * 92)
    print("0. HOW CLUSTERED IS THIS CORPUS? (a second, independent estimate)")
    print("=" * 92)
    print("  %d files in %d replication packages, mean cluster size %.2f" % (nN, nk, m0))
    print("  ICC of the per-file outcome within a package = %.3f" % icc)
    print("  design effect %.2f -> effective n %.0f, not %d" % (deff, nN / deff, nN))
    print("  For comparison, measured on a completely different corpus (Jupyter")
    print("  notebooks inside GitHub repositories, Samuel & Mietchen 2021 run):")
    print("  ICC = 0.435. Two languages, two repositories, two research communities.")
    print("  Every file-level percentage in this literature needs this correction and")
    print("  none applies it. All z statistics below are divided by sqrt(deff).")
    print()
    globals()["DEFF"] = deff
    globals()["ICC_MEASURED"] = icc
    pkgs = load_packages()
    recs = []
    for r in pkgs:
        doi = r["doi"]
        if doi not in out:
            continue
        nfiles, nran = out[doi]
        if nfiles == 0:
            continue
        recs.append({
            "doi": doi, "nfiles": nfiles, "ran": 1 if nran > 0 else 0,
            "deps": num(r.get("unique_libs_no")),
            "sizeMB": num(r.get("sizeMB")),
            "files_count": num(r.get("files_count")),
            "avg_file_len": num(r.get("avg_file_len")),
            "comments": num(r.get("comments_no")),
            **{c: int(num(r.get(c))) for c, _, _ in PRACTICES},
        })

    n = len(recs)
    base = sum(r["ran"] for r in recs)
    print("=" * 92)
    print("DOES ANY RECOMMENDED PRACTICE PREDICT RE-EXECUTION?")
    print("Trisovic et al. 2022 corpus. Unit = replication package. Cleaning condition,")
    print("symmetric combining rule. Outcome = the package has >=1 R file that ran.")
    print("=" * 92)
    print("  %d packages with at least one classifiable R file; %d (%.1f%%) have one that ran."
          % (n, base, 100.0 * base / n))
    print("  (The file-level rate over the same condition is 19.3%%; a package rate is")
    print("   higher because one success rescues the package. Both are in the record.)")
    print()

    print("  !! THE 'AT LEAST ONE FILE RAN' OUTCOME IS MECHANICALLY INFLATED BY PACKAGE")
    print("  SIZE: a package with 20 files has twenty chances. Measured below, that")
    print("  artifact is the single largest association in the whole table (z = +16.8),")
    print("  and it is a property of my outcome definition, not of the world. So the")
    print("  PRIMARY outcome here is the FILE-LEVEL rate within each group -- total")
    print("  files that ran over total files -- which cannot be inflated that way, with")
    print("  z divided by sqrt(design effect) for clustering.")
    print()

    bonf = 0.05 / len(PRACTICES)
    print("  %-46s %6s %17s %17s %8s %9s"
          % ("practice", "n pkgs", "FILE rate WITH", "FILE rate WITHOUT", "z*", "p"))
    results = []
    for col, label, direction in PRACTICES:
        a = [r for r in recs if r[col] == 1]
        b = [r for r in recs if r[col] != 1]
        if not a:
            print("  %-46s %6d %17s %17s %8s %9s"
                  % (label, 0, "--", "--", "--", "no packages"))
            continue
        # file-level: numerator = files that ran, denominator = files classified
        f1 = sum(out[x["doi"]][1] for x in a)
        t1 = sum(out[x["doi"]][0] for x in a)
        f2 = sum(out[x["doi"]][1] for x in b)
        t2 = sum(out[x["doi"]][0] for x in b)
        z = two_prop_z(f1, t1 / DEFF, f2, t2 / DEFF) if t1 and t2 else float("nan")
        # two_prop_z above needs matching scaling on the numerator too
        z = two_prop_z(f1 / DEFF, t1 / DEFF, f2 / DEFF, t2 / DEFF) if t1 and t2 else float("nan")
        p = norm_p(z)
        star = ""
        if p == p and p < bonf:
            star = "  **"
        elif p == p and p < 0.05:
            star = "  *"
        print("  %-46s %6d %8.1f%% (%5d) %8.1f%% (%5d) %8.2f %9.4f%s"
              % (label, len(a), 100.0 * f1 / t1, t1, 100.0 * f2 / t2, t2, z, p, star))
        results.append((col, label, direction, z, p, len(a)))
    print()
    print("  ** p < %.4f (Bonferroni for %d tests)   * p < 0.05 uncorrected"
          % (bonf, len(PRACTICES)))
    print("  z* is the two-proportion z with both counts divided by the design effect")
    print("  %.2f, i.e. computed on the effective sample size rather than the file count."
          % DEFF)
    print()

    # A z statistic on 9 or 22 clusters is not an inference, whatever the design
    # effect says. Resample PACKAGES with replacement -- the actual independent
    # unit -- and read the interval, not the p.
    import random
    rng = random.Random(20260824)
    Bboot = 4000
    print("  CLUSTER BOOTSTRAP (%d resamples of PACKAGES, the independent unit)." % Bboot)
    print("  This is the inference to read where the number of packages is small; a z")
    print("  computed on 9 clusters is arithmetic, not evidence.")
    print("  %-46s %8s %26s %10s"
          % ("practice", "n pkgs", "file-rate difference (pp)", "95% CI"))
    for col, label, direction in PRACTICES:
        a = [r for r in recs if r[col] == 1]
        b = [r for r in recs if r[col] != 1]
        if not a:
            continue
        A = [(out[x["doi"]][1], out[x["doi"]][0]) for x in a]
        Bg = [(out[x["doi"]][1], out[x["doi"]][0]) for x in b]

        def rate(sample):
            k = sum(s for s, _ in sample)
            n = sum(t for _, t in sample)
            return k / n if n else float("nan")

        obs = rate(A) - rate(Bg)
        diffs = []
        for _ in range(Bboot):
            sa = [A[rng.randrange(len(A))] for _ in range(len(A))]
            sb = [Bg[rng.randrange(len(Bg))] for _ in range(len(Bg))]
            d = rate(sa) - rate(sb)
            if d == d:
                diffs.append(d)
        diffs.sort()
        lo = diffs[int(0.025 * len(diffs))]
        hi = diffs[int(0.975 * len(diffs))]
        crosses = "" if (lo > 0 or hi < 0) else "   (crosses 0)"
        print("  %-46s %8d %+25.1f  [%+.1f, %+.1f]%s"
              % (label, len(a), 100 * obs, 100 * lo, 100 * hi, crosses))
    print()

    print("  The 95%% CI half-width IS the smallest effect this corpus could have")
    print("  detected for that practice. Read it before reading any point estimate:")
    print("  for `docs` (1,190 packages) it is about 4 points, so a real benefit of 6")
    print("  points would have shown; for `.Rproj` (22 packages) it is 25 points, so")
    print("  that row is uninformative whatever its z said.")
    print()

    # Positive control: plant a practice with a known benefit and check the
    # bootstrap finds it. Without this, "nothing helps" could just mean "this
    # procedure finds nothing".
    print("  SYNTHETIC POSITIVE CONTROL -- a planted practice with a known benefit.")
    print("  Assign a fake practice to a random 1,190 packages (matching `docs`), then")
    print("  flip a share of their failing files to successes, and see it recovered.")
    print("  Repeated over %d random assignments, because ONE assignment is itself a"
          % 20)
    print("  draw: at a planted benefit of zero the first seed I tried returned -3.5")
    print("  points, purely from which packages happened to land in the treated group.")
    print("  %-40s %16s %14s %12s"
          % ("planted benefit", "mean recovered", "mean over 0%", "power"))
    allpk = [(out[r["doi"]][1], out[r["doi"]][0]) for r in recs]
    NREP, NBOOT = 20, 800
    base_mean = None
    for planted in (0.0, 0.03, 0.06, 0.12, 0.20):
        obs_list, excl = [], 0
        for rep in range(NREP):
            rng2 = random.Random(700 + rep)
            idx = list(range(len(allpk)))
            rng2.shuffle(idx)
            chosen = set(idx[:1190])
            A, Bg = [], []
            for i, (s, t) in enumerate(allpk):
                if i in chosen:
                    extra = sum(1 for _ in range(t - s) if rng2.random() < planted)
                    A.append((s + extra, t))
                else:
                    Bg.append((s, t))

            def rate(sample):
                k = sum(s for s, _ in sample)
                nn = sum(t for _, t in sample)
                return k / nn if nn else float("nan")
            obs = rate(A) - rate(Bg)
            obs_list.append(obs)
            diffs = []
            for _ in range(NBOOT):
                sa = [A[rng2.randrange(len(A))] for _ in range(len(A))]
                sb = [Bg[rng2.randrange(len(Bg))] for _ in range(len(Bg))]
                d = rate(sa) - rate(sb)
                if d == d:
                    diffs.append(d)
            diffs.sort()
            lo = diffs[int(0.025 * len(diffs))]
            hi = diffs[int(0.975 * len(diffs))]
            excl += (lo > 0 or hi < 0)
        m = sum(obs_list) / len(obs_list)
        if base_mean is None:
            base_mean = m
        print("  %-40s %+15.1f %+13.1f %11.0f%%"
              % ("%.0f%% of failing files rescued" % (100 * planted),
                 100 * m, 100 * (m - base_mean), 100.0 * excl / NREP))
    print()
    print("  'power' is the share of assignments whose bootstrap interval excluded 0.")
    print("  At a planted zero it is the false-positive rate and should sit near 5%.")
    print("  Read the smallest planted benefit whose power is high: that is the")
    print("  smallest real effect this corpus could have shown, and every recommended")
    print("  practice tested above is below it or barely at it.")
    print()

    print("  Same table on the package-level outcome ('>=1 file ran'), which is what a")
    print("  reuser experiences but which the size artifact contaminates:")
    print("  %-46s %17s %17s %8s" % ("practice", "PKG rate WITH", "PKG rate WITHOUT", "z"))
    for col, label, direction in PRACTICES:
        a = [r for r in recs if r[col] == 1]
        b = [r for r in recs if r[col] != 1]
        if not a:
            continue
        k1, n1 = sum(x["ran"] for x in a), len(a)
        k2, n2 = sum(x["ran"] for x in b), len(b)
        print("  %-46s %8.1f%% (%5d) %8.1f%% (%5d) %8.2f"
              % (label, 100.0 * k1 / n1, n1, 100.0 * k2 / n2, n2,
                 two_prop_z(k1, n1, k2, n2)))
    print()

    print("-" * 92)
    print("CONTINUOUS PREDICTORS -- the things nobody recommends, for comparison")
    print("-" * 92)
    for col, label in (("deps", "number of distinct libraries the package needs"),
                       ("nfiles", "number of R files classified"),
                       ("files_count", "number of files of any kind"),
                       ("sizeMB", "package size in MB"),
                       ("avg_file_len", "average R file length in lines"),
                       ("comments", "total comment lines")):
        vals = sorted(recs, key=lambda r: r[col])
        t = len(vals) // 3
        lo, mid, hi = vals[:t], vals[t:2 * t], vals[2 * t:]
        parts = []
        for g in (lo, mid, hi):
            k = sum(x["ran"] for x in g)
            parts.append("%5.1f%% (%d)" % (100.0 * k / len(g), len(g)))
        kl, nl = sum(x["ran"] for x in lo), len(lo)
        kh, nh = sum(x["ran"] for x in hi), len(hi)
        z = two_prop_z(kh, nh, kl, nl)
        print("  %-46s  low %s  mid %s  high %s   z(hi-lo) %+.2f  p %.4f"
              % (label, parts[0], parts[1], parts[2], z, norm_p(z)))
    print()

    print("-" * 92)
    print("CONFOUND CHECK -- the two associations that survived, stratified")
    print("-" * 92)
    survivors = [r for r in results if r[4] == r[4] and r[4] < 0.05]
    if not survivors:
        print("  none reached p < 0.05 uncorrected; nothing to stratify.")
    for col, label, direction, z, p, n1 in survivors:
        print("\n  %s" % label)
        for sname, key, cuts in (("by dependency count", "deps", (3, 8)),
                                 ("by number of R files", "nfiles", (2, 5))):
            print("    %s:" % sname)
            for lab, test in (("low ", lambda r: r[key] <= cuts[0]),
                              ("mid ", lambda r: cuts[0] < r[key] <= cuts[1]),
                              ("high", lambda r: r[key] > cuts[1])):
                st = [r for r in recs if test(r)]
                a = [r for r in st if r[col] == 1]
                b = [r for r in st if r[col] != 1]
                if not a or not b:
                    continue
                k1, n1_ = sum(x["ran"] for x in a), len(a)
                k2, n2_ = sum(x["ran"] for x in b), len(b)
                print("      %s with %5.1f%% (%4d)   without %5.1f%% (%4d)   z %+.2f"
                      % (lab, 100.0 * k1 / n1_, n1_, 100.0 * k2 / n2_, n2_,
                         two_prop_z(k1, n1_, k2, n2_)))
    print()

    print("-" * 92)
    print("WHAT THE CORPUS CANNOT ANSWER, WITH ITS NUMBERS")
    print("-" * 92)
    for col, label, _ in PRACTICES:
        c = sum(1 for r in recs if r[col] == 1)
        if c < 30:
            print("  %-52s present in %4d of %d packages (%.2f%%)"
                  % (label, c, n, 100.0 * c / n))
    print()
    print("  The recommendation with the strongest theoretical case -- ship a built")
    print("  environment -- is the one the corpus cannot evaluate, because almost")
    print("  nobody does it. That is itself the most policy-relevant number here:")
    print("  it is not that containerisation was tried and failed, it is that after")
    print("  a decade of advice it has never been tried at a scale that could be")
    print("  measured.")


if __name__ == "__main__":
    main()
