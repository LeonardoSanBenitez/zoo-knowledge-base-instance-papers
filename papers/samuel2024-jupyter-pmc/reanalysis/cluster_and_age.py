"""
Samuel & Mietchen -- repository clustering and the age association, on the
released database rather than on the printed cohort table.

Author: maria, 2026-08-24. Stdlib only (sqlite3 is stdlib).

WHY THIS EXISTS
---------------
`age_trend.py` works from the cohort table printed inside the authors' own
notebook and cannot see inside a cohort. Two questions it cannot answer:

  Q1. Notebooks are not independent. Every notebook in a repository shares one
      conda environment, one set of data files and one author. How strongly do
      outcomes cluster by repository, i.e. what is the intra-class correlation?
      That number decides whether ANY notebook-level confidence interval in this
      literature means anything.

  Q2. The oldest cohorts have the highest success rates. Is that a property of
      old code, or of one or two large well-maintained repositories that happen
      to be old? Only the per-notebook records can say.

DATA
----
The 2021 run's full database, shipped as SQLite inside the Zenodo archive:

    curl -sL -o crpmc-data.zip \
      "https://zenodo.org/api/records/6802158/files/computational-reproducibility-pmc.zip/content"
    python -c "import zipfile; zipfile.ZipFile('crpmc-data.zip').extract(
      'computational-reproducibility-pmc/computational-reproducibility-pmc/analyses/db.sqlite','db')"

371 MB uncompressed, so it is NOT kept here -- the command above regenerates it.
Point DB_PATH at it (or set the CRPMC_DB environment variable) to re-run.

IMPORTANT SCOPE NOTE. This archive is the **2021 run**, i.e. the values the
published paper prints in parentheses after a lightning symbol, not the 2023
re-run that the paper's main numbers describe. 1,419 articles / 2,177
repositories / 9,625 notebooks here, against 3,467 / 2,660 / 27,271 in 2023.
Everything below is therefore a measurement of the 2021 corpus, used as the best
available estimate of a structural property (clustering) that has no reason to
have changed. Do not quote these as the paper's numbers.

The success definition is the authors' own, lifted from
analyses/analysis_helpers_executions.py:

    attempted  : executions row with reason != '<Skipping notebook>'
    finished   : (processed & (32+8+4)) == 32
    same value : finished AND (processed & 16) == 16
"""

import math
import os
import sqlite3
from collections import Counter, defaultdict

DB_PATH = os.environ.get(
    "CRPMC_DB",
    r"C:/tmp/crpmcdb/computational-reproducibility-pmc/computational-reproducibility-pmc/analyses/db.sqlite",
)

MASK_FINISHED = 32 + 8 + 4
BIT_SAME = 16


def rows():
    if not os.path.exists(DB_PATH):
        raise SystemExit(
            "database not found at %s\nSee the fetch command in this file's docstring."
            % DB_PATH
        )
    con = sqlite3.connect(DB_PATH)
    q = """
        SELECT e.id, e.notebook_id, e.repository_id, e.reason, e.processed,
               e.duration, rd.created_at
        FROM executions e
        LEFT JOIN repository_data rd ON rd.repository_id = e.repository_id
    """
    out = []
    for eid, nid, rid, reason, processed, duration, created in con.execute(q):
        if reason == "<Skipping notebook>":
            continue
        processed = processed or 0
        fin = (processed & MASK_FINISHED) == 32
        same = fin and (processed & BIT_SAME) == BIT_SAME
        year = int(created[:4]) if created else None
        out.append({"nid": nid, "rid": rid, "reason": reason,
                    "finished": fin, "same": same, "year": year,
                    "duration": duration})
    con.close()
    return out


def funnel(rs):
    print("=" * 74)
    print("FUNNEL, 2021 run, recomputed from the shipped database")
    print("=" * 74)
    n = len(rs)
    fin = sum(r["finished"] for r in rs)
    same = sum(r["same"] for r in rs)
    dep = sum(1 for r in rs if r["reason"] == "<Install Dependency Error>")
    print("  attempted executions (reason != skipping) : %6d" % n)
    print("  install-dependency errors                 : %6d  (%.1f%%)" % (dep, 100.0 * dep / n))
    print("  finished with no exception                : %6d  (%.1f%% of attempted)" % (fin, 100.0 * fin / n))
    print("  finished AND identical results            : %6d  (%.1f%% of attempted)" % (same, 100.0 * same / n))
    print("  finished but DIFFERENT results            : %6d  (%.1f%% of attempted)"
          % (fin - same, 100.0 * (fin - same) / n))
    print("  different / (different + identical)       : %6.3f" % ((fin - same) / fin if fin else float("nan")))
    print()
    print("  Paper's printed 2021 values for comparison: attempted 4,169 (43.45%),")
    print("  finished 396 (9.50%), identical 245 (5.88%), different 151 (3.62%),")
    print("  ratio different/(different+identical) = 0.38.")
    print("  Small differences are expected: the archive is a snapshot and the paper")
    print("  applies one further language filter. Report the discrepancy, do not hide it.")
    print()
    return n, fin, same


def icc(rs, key="finished"):
    """ANOVA intra-class correlation for a binary outcome clustered by repository.
    ICC = (MSB - MSW) / (MSB + (m0 - 1) * MSW) with m0 the usual size correction.
    """
    by = defaultdict(list)
    for r in rs:
        by[r["rid"]].append(1.0 if r[key] else 0.0)
    groups = [v for v in by.values() if len(v) >= 1]
    k = len(groups)
    N = sum(len(v) for v in groups)
    if k < 2:
        return float("nan"), 0, 0, 0.0
    grand = sum(sum(v) for v in groups) / N
    ssb = sum(len(v) * (sum(v) / len(v) - grand) ** 2 for v in groups)
    ssw = sum(sum((x - sum(v) / len(v)) ** 2 for x in v) for v in groups)
    msb = ssb / (k - 1)
    msw = ssw / (N - k) if N > k else 0.0
    m0 = (N - sum(len(v) ** 2 for v in groups) / N) / (k - 1)
    denom = msb + (m0 - 1) * msw
    val = (msb - msw) / denom if denom else float("nan")
    return val, k, N, m0


def clustering(rs):
    print("=" * 74)
    print("Q1 -- HOW MUCH DO OUTCOMES CLUSTER BY REPOSITORY?")
    print("=" * 74)
    for key, label in (("finished", "executes without exception"),
                       ("same", "executes AND matches the recorded output")):
        val, k, N, m0 = icc(rs, key)
        deff = 1 + (m0 - 1) * val
        print("  outcome = %-42s" % label)
        print("     repositories %d, executions %d, mean cluster size m0 = %.2f" % (k, N, m0))
        print("     ICC = %.3f   design effect = %.2f   effective n = %.0f (not %d)"
              % (val, deff, N / deff, N))
        print()
    sizes = Counter()
    by = defaultdict(list)
    for r in rs:
        by[r["rid"]].append(r)
    for v in by.values():
        sizes[len(v)] += 1
    allsame = sum(1 for v in by.values()
                  if len(v) >= 3 and len({x["finished"] for x in v}) == 1)
    big = [v for v in by.values() if len(v) >= 3]
    print("  repositories contributing >= 3 executions: %d" % len(big))
    print("  of those, repositories where EVERY execution had the same outcome: %d (%.1f%%)"
          % (allsame, 100.0 * allsame / max(len(big), 1)))
    print("  -> a repository is close to a single Bernoulli trial, not to m independent ones.")
    print()


def age_by_level(rs):
    print("=" * 74)
    print("Q2 -- THE AGE ASSOCIATION AT NOTEBOOK LEVEL AND AT REPOSITORY LEVEL")
    print("=" * 74)
    REF = 2021
    nb = defaultdict(lambda: [0, 0])         # year -> [success, total] notebooks
    rp = defaultdict(lambda: [0, 0])         # year -> [repos with >=1 success, repos]
    byrepo = defaultdict(list)
    ryear = {}
    for r in rs:
        if r["year"] is None:
            continue
        nb[r["year"]][1] += 1
        nb[r["year"]][0] += r["finished"]
        byrepo[r["rid"]].append(r)
        ryear[r["rid"]] = r["year"]
    for rid, v in byrepo.items():
        y = ryear[rid]
        rp[y][1] += 1
        rp[y][0] += any(x["finished"] for x in v)

    years = sorted(nb)
    print("  %6s %5s | %8s %8s %8s | %8s %8s %8s | %s"
          % ("year", "age", "nb_succ", "nb_tot", "nb_rate", "rp_succ", "rp_tot", "rp_rate",
             "top-repo share of cohort successes"))
    nb_rows, rp_rows = [], []
    for y in years:
        s, t = nb[y]
        rs_, rt = rp[y]
        # concentration: what share of this cohort's successes come from its single
        # most successful repository?
        per = Counter()
        for rid, v in byrepo.items():
            if ryear[rid] == y:
                per[rid] += sum(1 for x in v if x["finished"])
        top = max(per.values()) if per else 0
        share = top / s if s else float("nan")
        print("  %6d %5d | %8d %8d %7.1f%% | %8d %8d %7.1f%% | %6.0f%% (%d of %d)"
              % (y, REF - y, s, t, 100.0 * s / t, rs_, rt, 100.0 * rs_ / rt,
                 100 * share if s else 0, top, s))
        nb_rows.append({"age": REF - y, "s": s, "n": t})
        rp_rows.append({"age": REF - y, "s": rs_, "n": rt})
    print()
    for rows_, label in ((nb_rows, "NOTEBOOK level (the authors' unit)"),
                         (rp_rows, "REPOSITORY level (the independent unit)")):
        z = cochran_armitage(rows_)
        b, se = logistic_slope(rows_)
        print("  %-40s trend z = %+6.2f  p = %-10.3g  OR/year = %.3f"
              % (label, z, 2 * norm_sf(abs(z)), math.exp(b)))
    print()
    print("  If the notebook-level trend is much stronger than the repository-level")
    print("  one, the age association is about which REPOSITORIES are old, not about")
    print("  what happens to code as it ages.")
    print()


# --- statistics reused from age_trend.py, kept local so this file stands alone ---

def cochran_armitage(rows_):
    N = sum(r["n"] for r in rows_)
    S = sum(r["s"] for r in rows_)
    if N == 0 or S == 0:
        return float("nan")
    p = S / N
    xbar = sum(r["n"] * r["age"] for r in rows_) / N
    num = sum(r["age"] * (r["s"] - r["n"] * p) for r in rows_)
    var = p * (1 - p) * sum(r["n"] * (r["age"] - xbar) ** 2 for r in rows_)
    return num / math.sqrt(var) if var > 0 else float("nan")


def logistic_slope(rows_):
    b0, b1 = 0.0, 0.0
    det = 1.0
    h00 = 1.0
    for _ in range(200):
        g0 = g1 = h00 = h01 = h11 = 0.0
        for r in rows_:
            n, s = r["n"], r["s"]
            eta = b0 + b1 * r["age"]
            eta = max(-30.0, min(30.0, eta))
            pi = 1.0 / (1.0 + math.exp(-eta))
            g0 += s - n * pi
            g1 += r["age"] * (s - n * pi)
            w = n * pi * (1 - pi)
            h00 += w
            h01 += w * r["age"]
            h11 += w * r["age"] ** 2
        det = h00 * h11 - h01 * h01
        if det <= 0:
            break
        d0 = (h11 * g0 - h01 * g1) / det
        d1 = (-h01 * g0 + h00 * g1) / det
        b0 += d0
        b1 += d1
        if abs(d0) < 1e-12 and abs(d1) < 1e-12:
            break
    return b1, (math.sqrt(h00 / det) if det > 0 else float("nan"))


def norm_sf(z):
    return 0.5 * math.erfc(z / math.sqrt(2))


# The 2023 re-run cohort table, transcribed from the authors' PMC4 notebook
# output (see ../artifacts/age_cohorts.csv). Held here so the two runs of the
# SAME pipeline can be put side by side, which is the point.
COHORTS_2023 = {          # repo creation year -> (successes, executions)
    2022: (80, 680), 2021: (121, 1368), 2020: (231, 3670), 2019: (267, 1549),
    2018: (208, 1283), 2017: (75, 666), 2016: (51, 420), 2015: (60, 235),
    2014: (27, 317), 2013: (69, 141),
}


def two_runs(rs):
    print("=" * 74)
    print("Q3 -- THE SAME PIPELINE, TWO YEARS APART, ON OVERLAPPING COHORTS")
    print("=" * 74)
    nb = defaultdict(lambda: [0, 0])
    for r in rs:
        if r["year"] is None:
            continue
        nb[r["year"]][1] += 1
        nb[r["year"]][0] += r["finished"]
    print("  %6s | %18s | %18s | %s"
          % ("year", "2021 run", "2023 run", "rate ratio"))
    for y in sorted(set(nb) & set(COHORTS_2023)):
        s1, n1 = nb[y]
        s2, n2 = COHORTS_2023[y]
        r1 = s1 / n1 if n1 else float("nan")
        r2 = s2 / n2 if n2 else float("nan")
        ratio = (r2 / r1) if r1 else float("inf")
        print("  %6d | %5d/%-5d = %5.1f%% | %5d/%-5d = %5.1f%% | x%.1f"
              % (y, s1, n1, 100 * r1, s2, n2, 100 * r2, ratio))
    print()
    print("  Same code, same variable (GitHub repository creation year), same team,")
    print("  overlapping repositories. If a cohort's rate can move by an order of")
    print("  magnitude between two runs of one pipeline, the cohort rate is not a")
    print("  property of the cohort. Neither run's age trend should be believed:")
    print("  the 2021 data give a NEGATIVE age association and the 2023 table a")
    print("  strongly POSITIVE one (age_trend.py: z = +11.7).")
    print()


def concentration(rs):
    print("=" * 74)
    print("Q4 -- HOW MANY REPOSITORIES PRODUCE THE SUCCESSES?")
    print("=" * 74)
    per = Counter()
    for r in rs:
        if r["finished"]:
            per[r["rid"]] += 1
    total = sum(per.values())
    ordered = [c for _, c in per.most_common()]
    print("  %d successes come from %d distinct repositories" % (total, len(per)))
    cum = 0
    for k in (1, 3, 5, 10, 20, 50):
        cum = sum(ordered[:k])
        if k <= len(ordered):
            print("     top %-3d repositories account for %4d successes (%4.1f%%)"
                  % (k, cum, 100.0 * cum / total))
    # Gini
    n = len(ordered)
    s = sorted(ordered)
    g = (2 * sum((i + 1) * v for i, v in enumerate(s)) / (n * sum(s))) - (n + 1) / n
    print("  Gini of successes across contributing repositories: %.3f" % g)
    print("  -> any per-cohort or per-field rate in this design is a statement about")
    print("     a handful of repositories, reported with a notebook-sized n.")
    print()


def main():
    rs = rows()
    funnel(rs)
    clustering(rs)
    age_by_level(rs)
    two_runs(rs)
    concentration(rs)


if __name__ == "__main__":
    main()
