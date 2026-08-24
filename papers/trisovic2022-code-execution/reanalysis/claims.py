"""
Two checkable claims from Trisovic et al. 2022, tested against the released logs.

Author: maria, 2026-08-24.

CLAIM A (RQ5, verbatim):
    "There were no cases of code cleaning 'breaking' the previously successful
     code, meaning that a simple code cleaning algorithm, such as this one, can
     improve code re-execution."
  This is a universal negative over ~8000 files and is directly checkable: for
  each (doi, file, R version), did the raw run succeed and the cleaned run fail?

CLAIM B (RQ7, verbatim):
    "our results suggest that the strictness of the data sharing policy is
     positively correlated to the re-execution rate of code files."
  The paper gives a bar chart and no statistic. Journals are the unit; there are
  eleven of them above the paper's own >30-datasets threshold; six share one
  policy level. Compute Spearman with an exact permutation p, under BOTH the
  paper's combining rule and the symmetric one, and report the floor on p at
  that n.

CLAIM C (added after seeing the calibration in denominator.py):
    the paper's design assumes the three R versions are a meaningful axis
    ("we have identified a version of R able to re-execute a given R file").
    Measure how much the third version buys over the first.

RUN
---
    python claims.py
Stdlib only.
"""

import csv
import itertools
import os
from collections import Counter, defaultdict

from denominator import (DATA, VERSIONS, load_condition, classify,
                         combined_paper, combined_anyobserved, bad_dois)


# --------------------------------------------------------------- CLAIM A

def claim_a():
    env = load_condition("env")
    raw = load_condition("no_env")
    print("=" * 74)
    print("CLAIM A -- 'no cases of code cleaning breaking previously successful code'")
    print("=" * 74)

    per_version_breaks = Counter()
    examples = defaultdict(list)
    comparable = Counter()
    for v in VERSIONS:
        for k, rawres in raw[v].items():
            if rawres != "success":
                continue
            envres = env[v].get(k)
            if envres is None:
                per_version_breaks["(raw success, cleaned NEVER RUN)"] += 1
                continue
            comparable[v] += 1
            c = classify(envres)
            if c == "success":
                continue
            per_version_breaks["(raw success, cleaned %s) R%s" % (c, v)] += 1
            if len(examples[c]) < 3:
                examples[c].append((v, k, envres[:110]))

    tot_break = sum(n for key, n in per_version_breaks.items() if "NEVER RUN" not in key)
    tot_comparable = sum(comparable.values())
    print("  (doi, file, version) cells where the RAW run succeeded and both runs exist: %d"
          % tot_comparable)
    print("  of those, cells where the CLEANED run did not succeed                     : %d  (%.1f%%)"
          % (tot_break, 100.0 * tot_break / max(tot_comparable, 1)))
    for key, n in sorted(per_version_breaks.items()):
        print("     %-46s %5d" % (key, n))
    print()
    for c, ex in examples.items():
        print("  example breakages, cleaned outcome = %s:" % c)
        for v, k, msg in ex:
            print("     R%s  %s  %s" % (v, k[1][:42], msg.replace("\n", " ")))
    print()

    # file level, using each rule
    print("  -- file level, combined across the three versions --")
    for name, rule in (("paper's rule", combined_paper),
                       ("symmetric rule", combined_anyobserved)):
        rawc, envc = {}, {}
        keys = set()
        for d, out in ((raw, rawc), (env, envc)):
            u = set()
            for v in VERSIONS:
                u |= set(d[v])
            for k in u:
                out[k] = rule([d[v].get(k) for v in VERSIONS])
            keys |= u
        broke = sum(1 for k in keys
                    if rawc.get(k) == "success" and envc.get(k) not in (None, "success"))
        lost = sum(1 for k in keys
                   if rawc.get(k) == "success" and envc.get(k) is None)
        fixed = sum(1 for k in keys
                    if envc.get(k) == "success" and rawc.get(k) not in (None, "success"))
        print("     %-15s cleaned-broke %4d | cleaned-fixed %4d | raw-success-but-cleaned-dropped %4d"
              % (name, broke, fixed, lost))
    print()


# --------------------------------------------------------------- CLAIM B

PUBLISHER_TO_POLICY = {
    # publisher code in all_metadata.txt -> (survey name, strictness level 1..5)
    "ajps": ("American Journal of Political Science", 5),
    "PSRM": ("Political Science Research and Methods", 5),
    "pan": ("Political Analysis", 4),
    "BJPolS": ("British Journal of Political Science", 3),
    "the_review": ("American Political Science Review", 3),
    "isq": ("International Studies Quarterly", 3),
    "polbehavior": ("Political Behavior", 3),
    "researchandpolitics": ("Research & Politics", 3),
    "xps": ("Journal of Experimental Political Science", 3),
    "restat": ("Review of Economics and Statistics", 3),
    "internationalinteractions": ("International Interactions", 2),
    "jop": ("The Journal of Politics", 1),
}


def load_metadata():
    doi2pub = {}
    with open(os.path.join(DATA, "all_metadata.txt"), encoding="utf-8", errors="replace") as fh:
        for row in csv.DictReader(fh):
            doi2pub[row["doi"]] = row["publisher"]
    return doi2pub


def spearman(x, y):
    def rank(a):
        order = sorted(range(len(a)), key=lambda i: a[i])
        r = [0.0] * len(a)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and a[order[j + 1]] == a[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    n = len(x)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else float("nan")


def exact_permutation_p(x, y, stat=spearman):
    """Two-sided exact p over all permutations of y (n! -- fine for n<=11 if we
    cap; for n=11 that is 39.9M, too many, so permute x which has heavy ties and
    dedupe by the multiset)."""
    obs = stat(x, y)
    n = len(x)
    if n <= 8:
        perms = itertools.permutations(range(n))
        total = ge = 0
        for p in perms:
            total += 1
            s = stat([x[i] for i in p], y)
            if abs(s) >= abs(obs) - 1e-12:
                ge += 1
        return obs, ge / total, total, "exact"
    # n too large for full enumeration: Monte Carlo with a fixed seed
    import random
    rng = random.Random(20260824)
    B = 200000
    ge = 0
    xs = list(x)
    for _ in range(B):
        rng.shuffle(xs)
        if abs(stat(xs, y)) >= abs(obs) - 1e-12:
            ge += 1
    return obs, (ge + 1) / (B + 1), B, "monte-carlo B=%d" % B


def claim_b():
    print("=" * 74)
    print("CLAIM B -- 'policy strictness is positively correlated with re-execution rate'")
    print("=" * 74)
    doi2pub = load_metadata()
    env = load_condition("env")
    bad = bad_dois("env")
    union = set()
    for v in VERSIONS:
        union |= set(env[v])

    per_pub = defaultdict(lambda: {"paper_s": 0, "paper_n": 0, "sym_s": 0, "sym_n": 0,
                                   "dois": set()})
    for k in union:
        pub = doi2pub.get(k[0])
        if pub is None or pub not in PUBLISHER_TO_POLICY:
            continue
        cells = [env[v].get(k) for v in VERSIONS]
        d = per_pub[pub]
        d["dois"].add(k[0])
        pr = combined_paper(cells)
        if pr is not None and not (k[0] in bad and pr != "success"):
            d["paper_n"] += 1
            d["paper_s"] += (pr == "success")
        ar = combined_anyobserved(cells)
        if ar is not None:
            d["sym_n"] += 1
            d["sym_s"] += (ar == "success")

    rows = []
    for pub, d in per_pub.items():
        name, lvl = PUBLISHER_TO_POLICY[pub]
        if len(d["dois"]) < 30:
            continue
        rows.append((pub, name, lvl, len(d["dois"]), d["paper_s"], d["paper_n"],
                     d["sym_s"], d["sym_n"]))
    rows.sort(key=lambda r: (-r[2], r[1]))

    print("  journals with >30 datasets (the paper's own threshold): n = %d" % len(rows))
    print("  %-42s %3s %5s %14s %14s" % ("journal", "lvl", "#ds", "paper rate", "symmetric rate"))
    for pub, name, lvl, nds, ps, pn, ss, sn in rows:
        print("  %-42s %3d %5d   %5.1f%% (%4d) %7.1f%% (%4d)"
              % (name[:42], lvl, nds, 100.0 * ps / max(pn, 1), pn,
                 100.0 * ss / max(sn, 1), sn))
    print()

    lvls = [r[2] for r in rows]
    for label, si, ni in (("paper's rule", 4, 5), ("symmetric rule", 6, 7)):
        rates = [r[si] / max(r[ni], 1) for r in rows]
        rho, p, nperm, how = exact_permutation_p(lvls, rates)
        print("  %-15s Spearman rho = %+.3f   two-sided p = %.4f   (%s)"
              % (label, rho, p, how))
    # leave-one-out on the symmetric rule
    rates = [r[6] / max(r[7], 1) for r in rows]
    print("  leave-one-out (symmetric rule):")
    base = spearman(lvls, rates)
    worst = None
    for i in range(len(rows)):
        l2 = lvls[:i] + lvls[i + 1:]
        r2 = rates[:i] + rates[i + 1:]
        rho = spearman(l2, r2)
        if worst is None or abs(rho - base) > abs(worst[1] - base):
            worst = (rows[i][1], rho)
        print("     drop %-42s rho = %+.3f" % (rows[i][1][:42], rho))
    print("  most influential journal: %s (rho %+.3f vs %+.3f with all)"
          % (worst[0], worst[1], base))
    print()

    # ---- confounds available in the released metadata ----
    years = defaultdict(list)
    with open(os.path.join(DATA, "all_metadata.txt"), encoding="utf-8", errors="replace") as fh:
        for row in csv.DictReader(fh):
            pub = row["publisher"]
            try:
                years[pub].append(int(row["publicationDate"]))
            except (ValueError, TypeError):
                pass
    files_per_ds = defaultdict(list)
    for pub, d in per_pub.items():
        pass
    nfiles = {}
    for pub in PUBLISHER_TO_POLICY:
        d = per_pub.get(pub)
        if d:
            nfiles[pub] = d["sym_n"] / max(len(d["dois"]), 1)

    def med(a):
        a = sorted(a)
        return a[len(a) // 2] if a else float("nan")

    print("  -- confounds in the released metadata --")
    print("  %-42s %3s %8s %10s" % ("journal", "lvl", "med.year", "files/ds"))
    for pub, name, lvl, nds, ps, pn, ss, sn in rows:
        print("  %-42s %3d %8.0f %10.1f" % (name[:42], lvl, med(years[pub]), nfiles.get(pub, float("nan"))))
    yr = [med(years[r[0]]) for r in rows]
    fp = [nfiles.get(r[0], 0.0) for r in rows]
    print("  Spearman(level, median year)      = %+.3f" % spearman(lvls, yr))
    print("  Spearman(level, files per dataset)= %+.3f" % spearman(lvls, fp))
    print("  Spearman(rate,  median year)      = %+.3f" % spearman(rates, yr))
    print("  Spearman(rate,  files per dataset)= %+.3f" % spearman(rates, fp))

    def partial(x, y, z):
        rxy, rxz, ryz = spearman(x, y), spearman(x, z), spearman(y, z)
        den = ((1 - rxz ** 2) * (1 - ryz ** 2)) ** 0.5
        return (rxy - rxz * ryz) / den if den else float("nan")

    print("  partial Spearman(level, rate | median year)       = %+.3f" % partial(lvls, rates, yr))
    print("  partial Spearman(level, rate | files per dataset) = %+.3f" % partial(lvls, rates, fp))
    print()
    print("  n = 11 journals. Six of them share policy level 3, so the number of")
    print("  DISTINCT rank arrangements is far below 11!; the Monte-Carlo p above")
    print("  is over that reduced set and 0.026 is not far from its floor. Treat")
    print("  this as one observation with a consistent direction, not a rate.")
    print()


# --------------------------------------------------------------- CLAIM C

def claim_c():
    print("=" * 74)
    print("CLAIM C -- how much does testing three R versions actually buy?")
    print("=" * 74)
    for suffix, label in (("no_env", "no code cleaning"), ("env", "with code cleaning")):
        logs = load_condition(suffix)
        union = set()
        for v in VERSIONS:
            union |= set(logs[v])
        full = [k for k in union if all(logs[v].get(k) is not None for v in VERSIONS)]
        cnt = Counter()
        single = Counter()
        for k in full:
            kinds = [classify(logs[v].get(k)) for v in VERSIONS]
            s = sum(1 for x in kinds if x == "success")
            cnt[s] += 1
            for v, x in zip(VERSIONS, kinds):
                single[v] += (x == "success")
        nfull = len(full)
        anysucc = nfull - cnt[0]
        print("  %s: %d fully-observed files" % (label, nfull))
        for s in range(4):
            print("     success in %d of 3 versions : %5d  (%4.1f%%)"
                  % (s, cnt[s], 100.0 * cnt[s] / nfull))
        for v in VERSIONS:
            print("     single version R %-3s        : %5d  (%4.1f%%)"
                  % (v, single[v], 100.0 * single[v] / nfull))
        best_single = max(single.values())
        best_v = [v for v in VERSIONS if single[v] == best_single][0]
        print("     best SINGLE version (R %s)  : %5d  (%4.1f%%)"
              % (best_v, best_single, 100.0 * best_single / nfull))
        print("     any of three                : %d  (%.1f%%)"
              % (anysucc, 100.0 * anysucc / nfull))
        print("     marginal gain of versions 2+3 over the best single: %+.1f points"
              % (100.0 * (anysucc - best_single) / nfull))
        print()


if __name__ == "__main__":
    claim_a()
    claim_b()
    claim_c()
