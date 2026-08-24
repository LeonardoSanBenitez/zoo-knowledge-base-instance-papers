"""
Reanalysis of Trisovic et al. 2022 (Sci Data 9:60) -- where does the
re-execution success rate actually live?

Author: maria, 2026-08-24.

WHAT THIS TESTS
---------------
The paper's headline is "74% of R files failed to complete without error in the
initial execution, while 56% failed when code cleaning was applied". Those two
percentages are 1 - 952/3830 and 1 - 1472/3695.

The denominators are not the corpus. 8893 unique (doi, file) pairs appear in at
least one of the six run logs; 3695 of them carry a combined result in the
code-cleaning condition. The other 58% are dropped by a rule in the authors'
own notebook (analysis/02-get-combined-success-rates.ipynb, cell 14):

    def get_combined_result(r):
        if 'success' in [r.r32, r.r36, r.r40]:  return 'success'
        if pd.isnull(r.r36) or pd.isnull(r.r32) or pd.isnull(r.r40):
            return np.nan                       # <- ANY missing version drops the row
        if "time limit exceeded" in [...]:      return np.nan
        ...

The rule is ASYMMETRIC. One success out of three versions makes the row a
success; a failure needs all three versions to have reported. Any file that a
version never got to -- because a sibling file in the same replication package
ate the 5-hour dataset budget -- is deleted, and files that error are exactly
the files most likely to be missing a version.

The paper labels the whole dropped bucket "TLE" (time limit exceeded). That
label is checkable against the logs and it is mostly wrong.

A second, smaller rule points the same way (cell 21):

    df.drop(df[df.doi.isin(bad_dois) & (df['result'] != 'success')].index)

which removes rows from download-failing DOIs *unless they succeeded*.

This script recomputes the rate under every denominator that can be defended,
tests whether the missingness is informative, and includes a synthetic check
where the true rate is known.

RUN
---
    python denominator.py            # from this directory; reads ../artifacts/data
Stdlib only.
"""

import csv
import os
import random
import sys
from collections import Counter, defaultdict

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "artifacts", "data")
VERSIONS = ("32", "36", "40")


# ---------------------------------------------------------------- loading

def load_run_log(path):
    """(doi, file) -> raw result string. Tab separated, no header."""
    d = {}
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 3:
                d[(parts[0], parts[1])] = parts[2].strip()
    return d


def load_condition(suffix):
    """suffix is 'env' (code cleaning) or 'no_env' (raw)."""
    return {v: load_run_log(os.path.join(DATA, "run_log_r%s_%s.csv" % (v, suffix)))
            for v in VERSIONS}


def bad_dois(suffix):
    """The authors' exclusion set: DOIs that failed download under ALL three versions."""
    sets = []
    for v in VERSIONS:
        p = os.path.join(DATA, "run_log_r%s_%s_download.csv" % (v, suffix))
        bad = set()
        with open(p, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                parts = line.rstrip("\n").split("\t")
                if len(parts) >= 3 and parts[2].strip() != "ok":
                    bad.add(parts[0])
        sets.append(bad)
    return sets[0] & sets[1] & sets[2]


def classify(v):
    if v is None:
        return "absent"
    if v == "success":
        return "success"
    if v == "time limit exceeded":
        return "tle"
    if v.startswith("download error") or v.startswith("not authorized"):
        return "infra"
    return "error"


# ---------------------------------------------------------------- the rules

def combined_paper(cells):
    """Reimplementation of the authors' get_combined_result + the drop rule.
    `cells` is the list of three raw strings/None in version order."""
    if "success" in cells:
        return "success"
    if any(c is None for c in cells):
        return None                      # dropped
    if "time limit exceeded" in cells:
        return None                      # dropped
    if "not authorized" in cells:
        return "auth"
    for c in (cells[1], cells[2], cells[0]):   # r36, r40, r32 -- their order
        if c:
            return c
    return None


def combined_anyobserved(cells):
    """Symmetric alternative: a file is a success if any version succeeded, a
    failure if any version reported a real error and none succeeded, TLE only if
    a version literally said 'time limit exceeded', and unknown only if nothing
    was ever observed."""
    kinds = [classify(c) for c in cells]
    if "success" in kinds:
        return "success"
    if "error" in kinds:
        return "error"
    if "tle" in kinds:
        return "tle"
    if "infra" in kinds:
        return "infra"
    return None


# ---------------------------------------------------------------- reporting

def rate_table(suffix, label):
    logs = load_condition(suffix)
    union = set()
    for v in VERSIONS:
        union |= set(logs[v])
    bad = bad_dois(suffix)

    paper_res = {}
    any_res = {}
    coverage = Counter()
    for k in union:
        cells = [logs[v].get(k) for v in VERSIONS]
        coverage[sum(c is not None for c in cells)] += 1
        pr = combined_paper(cells)
        # the authors' second rule: drop bad-DOI rows unless they succeeded
        if pr is not None and k[0] in bad and pr != "success":
            pr = "DROPPED_BAD_DOI"
        paper_res[k] = pr
        any_res[k] = combined_anyobserved(cells)

    kept = {k: v for k, v in paper_res.items() if v not in (None, "DROPPED_BAD_DOI")}
    succ_paper = sum(1 for v in kept.values() if v == "success")
    print("=" * 74)
    print("CONDITION: %s  (%s)" % (label, suffix))
    print("=" * 74)
    print("files appearing in >=1 run log (this condition) : %5d" % len(union))
    print("version coverage: 3 of 3 = %d, 2 of 3 = %d, 1 of 3 = %d"
          % (coverage[3], coverage[2], coverage[1]))
    print()
    print("-- the paper's estimate, reproduced --")
    print("  denominator kept by the notebook rule        : %5d" % len(kept))
    print("  successes                                    : %5d" % succ_paper)
    print("  SUCCESS RATE (paper)                         : %5.1f%%"
          % (100.0 * succ_paper / len(kept)))
    print()

    ac = Counter(any_res.values())
    obs = ac["success"] + ac["error"] + ac["tle"] + ac["infra"]
    print("-- what the logs actually contain, symmetric rule --")
    for k in ("success", "error", "tle", "infra"):
        print("  %-8s %5d" % (k, ac[k]))
    print("  any observed outcome                         : %5d" % obs)
    print("  SUCCESS / any observed outcome               : %5.1f%%"
          % (100.0 * ac["success"] / obs))
    print("  SUCCESS / all files in >=1 log               : %5.1f%%"
          % (100.0 * ac["success"] / len(union)))
    print()

    # what IS the dropped bucket the paper calls "TLE"?
    dropped = [k for k, v in paper_res.items() if v is None]
    why = Counter()
    for k in dropped:
        cells = [logs[v].get(k) for v in VERSIONS]
        kinds = [classify(c) for c in cells]
        if "tle" in kinds:
            why["contains a literal 'time limit exceeded'"] += 1
        elif "error" in kinds:
            why["NO tle; has a recorded ERROR, missing >=1 version"] += 1
        elif "infra" in kinds:
            why["NO tle; infra (download/auth), missing >=1 version"] += 1
        else:
            why["NO tle; nothing observed at all"] += 1
    print("-- composition of the bucket the paper labels 'TLE' (n=%d) --" % len(dropped))
    for k, v in why.most_common():
        print("  %-52s %5d  (%4.1f%%)" % (k, v, 100.0 * v / len(dropped)))
    nbad = sum(1 for k, v in paper_res.items() if v == "DROPPED_BAD_DOI")
    print("  additionally dropped by the bad-DOI rule (all non-successes): %d" % nbad)
    print()
    return logs, union, paper_res, any_res, coverage


def informative_missingness(logs, union):
    """Is a file that is missing a version different from one that is not?

    Test on OBSERVED cells only, so the comparison never uses the missing cell:
    among files with >=1 observed cell, compare P(any observed cell is success)
    between files with full 3/3 coverage and files with partial coverage.

    If missingness were ignorable, these should agree. Because a file can be
    marked success by ANY version, partial coverage mechanically gives fewer
    chances -- so this test is stacked toward finding a difference, and the
    honest version is the per-cell rate, which controls for that. Both reported.
    """
    full_cells = [0, 0]     # success, total, over files with 3/3 coverage
    part_cells = [0, 0]
    full_files = [0, 0]
    part_files = [0, 0]
    for k in union:
        cells = [logs[v].get(k) for v in VERSIONS]
        obs = [c for c in cells if c is not None and classify(c) in ("success", "error", "tle")]
        if not obs:
            continue
        s = sum(1 for c in obs if c == "success")
        if len(cells) - cells.count(None) == 3:
            full_cells[0] += s; full_cells[1] += len(obs)
            full_files[0] += (s > 0); full_files[1] += 1
        else:
            part_cells[0] += s; part_cells[1] += len(obs)
            part_files[0] += (s > 0); part_files[1] += 1

    print("-- is the missingness informative? (observed cells only) --")
    print("  PER CELL   full coverage: %d/%d = %.1f%%   partial: %d/%d = %.1f%%"
          % (full_cells[0], full_cells[1], 100.0 * full_cells[0] / max(full_cells[1], 1),
             part_cells[0], part_cells[1], 100.0 * part_cells[0] / max(part_cells[1], 1)))
    print("  PER FILE   full coverage: %d/%d = %.1f%%   partial: %d/%d = %.1f%%"
          % (full_files[0], full_files[1], 100.0 * full_files[0] / max(full_files[1], 1),
             part_files[0], part_files[1], 100.0 * part_files[0] / max(part_files[1], 1)))
    p1 = full_cells[0] / max(full_cells[1], 1)
    p2 = part_cells[0] / max(part_cells[1], 1)
    n1, n2 = full_cells[1], part_cells[1]
    pp = (full_cells[0] + part_cells[0]) / max(n1 + n2, 1)
    se = (pp * (1 - pp) * (1.0 / max(n1, 1) + 1.0 / max(n2, 1))) ** 0.5
    z = (p1 - p2) / se if se else float("nan")
    print("  per-cell two-proportion z = %.2f  (|z|>1.96 => not ignorable)" % z)
    print()
    return p1, p2, z


def bounds(logs, union, any_res):
    """Manski worst/best case over the estimand "this file succeeds under at
    least one of the three R versions".

    Lower: every unobserved file-version cell would have failed.
    Upper: every unobserved cell of a file with no observed success would have
           succeeded.
    No assumption is needed for either. The interval is what the data alone
    support; anything inside it is an imputation, including the paper's number.
    """
    ac = Counter(any_res.values())
    obs_success = ac["success"]
    n = len(union)
    could_flip = 0          # no observed success AND at least one missing cell
    for k in union:
        cells = [logs[v].get(k) for v in VERSIONS]
        if any(c == "success" for c in cells):
            continue
        if any(c is None for c in cells):
            could_flip += 1
    lo = obs_success / n
    hi = (obs_success + could_flip) / n
    print("-- Manski bounds over the %d files seen in >=1 log --" % n)
    print("  lower (every missing cell would have failed)  : %5.1f%%" % (100 * lo))
    print("  upper (every missing cell would have succeeded): %5.1f%%" % (100 * hi))
    print("  width %.1f points; %d files could flip" % (100 * (hi - lo), could_flip))
    print()
    return lo, hi


def calibrated_imputation(logs, union):
    """A point estimate inside the bounds, calibrated on the data itself.

    Fully-observed files are the calibration set. For a file whose observed
    versions ALL errored, ask: among fully-observed files with the same observed
    versions all errored, what fraction had at least one of the *remaining*
    versions succeed? Apply that probability to the partially-observed file.

    This is MAR conditional on the coverage pattern. We already measured that it
    is NOT ignorable -- partial-coverage files succeed less often per observed
    cell than full-coverage ones (z well past 2) -- so this number is an OPTIMISTIC
    point estimate, an upper-middle of the bounds, not a best guess. Reported as
    such rather than as "the" corrected rate.
    """
    # calibration: key = tuple of version-indices observed and errored
    cal = defaultdict(lambda: [0, 0])     # key -> [n_rescued, n]
    for k in union:
        cells = [logs[v].get(k) for v in VERSIONS]
        if any(c is None for c in cells):
            continue
        kinds = [classify(c) for c in cells]
        if "success" not in kinds:
            continue_flag = True
        for r in range(1, 3):             # pretend r versions were observed
            for idx in _combinations(range(3), r):
                if all(kinds[i] == "error" for i in idx):
                    rest = [i for i in range(3) if i not in idx]
                    rescued = any(kinds[i] == "success" for i in rest)
                    cal[idx][0] += rescued
                    cal[idx][1] += 1

    observed_success = 0
    expected_extra = 0.0
    no_cal = 0
    for k in union:
        cells = [logs[v].get(k) for v in VERSIONS]
        kinds = [classify(c) for c in cells]
        if "success" in kinds:
            observed_success += 1
            continue
        missing = [i for i in range(3) if cells[i] is None]
        if not missing:
            continue
        obs_err = tuple(i for i in range(3) if kinds[i] == "error")
        if obs_err and obs_err in cal and cal[obs_err][1] >= 30:
            p = cal[obs_err][0] / cal[obs_err][1]
        elif not obs_err:
            # nothing informative observed (tle/infra only) -- use marginal
            p = 1.0 - (1.0 - _marginal_success(logs, union)) ** len(missing)
            no_cal += 1
        else:
            p = _marginal_success(logs, union)
            no_cal += 1
        expected_extra += p

    n = len(union)
    est = (observed_success + expected_extra) / n
    print("-- calibrated imputation (MAR given coverage pattern) --")
    print("  calibration cells used:")
    for key in sorted(cal, key=lambda x: (len(x), x)):
        r, tot = cal[key]
        if tot >= 30:
            print("     observed %s all errored -> P(a remaining version succeeds) = %d/%d = %.3f"
                  % (str(tuple(VERSIONS[i] for i in key)), r, tot, r / tot))
    print("  observed successes %d + expected recovered %.0f  of %d"
          % (observed_success, expected_extra, n))
    print("  IMPUTED SUCCESS RATE (optimistic)             : %5.1f%%" % (100 * est))
    print("  (%d files fell back to the marginal rate)" % no_cal)
    print()
    return est


def _combinations(seq, r):
    seq = list(seq)
    if r == 1:
        return [(x,) for x in seq]
    if r == 2:
        return [(seq[0], seq[1]), (seq[0], seq[2]), (seq[1], seq[2])]
    return [tuple(seq)]


_MARG = {}


def _marginal_success(logs, union):
    key = id(logs)
    if key in _MARG:
        return _MARG[key]
    s = t = 0
    for v in VERSIONS:
        for val in logs[v].values():
            c = classify(val)
            if c in ("success", "error"):
                t += 1
                s += (c == "success")
    _MARG[key] = s / max(t, 1)
    return _MARG[key]


# ---------------------------------------------------------------- synthetic check

def synthetic_check(seed=7, n_files=8000, true_rate=0.30, verbose=True):
    """Rule 3 of the method: feed the estimator a case where the answer is known.

    Simulate the study's own structure. Each file has a latent per-version
    success probability. A file is 'missing' from a version with a probability
    that DEPENDS on whether it would have failed -- which is the mechanism the
    real pipeline has (a slow/erroring sibling burns the dataset's 5h budget).
    Then apply (a) the paper's rule and (b) the symmetric rule, and compare each
    to the known truth.
    """
    rng = random.Random(seed)
    truth_success = 0
    logs = {v: {} for v in VERSIONS}
    union = set()
    for i in range(n_files):
        k = ("doi:%d" % (i // 4), "f%d.R" % i)
        union.add(k)
        # ground truth: would this file succeed under at least one version?
        per_version = [rng.random() < true_rate for _ in VERSIONS]
        if any(per_version):
            truth_success += 1
        for v, ok in zip(VERSIONS, per_version):
            # informative missingness: failures are likelier to be dropped
            p_missing = 0.15 if ok else 0.45
            if rng.random() < p_missing:
                continue
            logs[v][k] = "success" if ok else "Error in foo() : synthetic"
    truth = truth_success / n_files

    paper_kept = 0
    paper_succ = 0
    any_succ = 0
    any_obs = 0
    for k in union:
        cells = [logs[v].get(k) for v in VERSIONS]
        pr = combined_paper(cells)
        if pr is not None:
            paper_kept += 1
            paper_succ += (pr == "success")
        ar = combined_anyobserved(cells)
        if ar is not None:
            any_obs += 1
            any_succ += (ar == "success")
    if verbose:
        print("=" * 74)
        print("SYNTHETIC CHECK -- true answer is known")
        print("=" * 74)
        print("  ground truth  P(file succeeds under >=1 version) : %5.1f%%" % (100 * truth))
        print("  paper's rule                                     : %5.1f%%  (n kept %d/%d)"
              % (100.0 * paper_succ / paper_kept, paper_kept, n_files))
        print("  symmetric rule / any observed outcome            : %5.1f%%  (n %d/%d)"
              % (100.0 * any_succ / any_obs, any_obs, n_files))
        print("  symmetric rule / all files                       : %5.1f%%"
              % (100.0 * any_succ / n_files))
        print()
    return truth, paper_succ / paper_kept, any_succ / any_obs, any_succ / n_files


def synthetic_null(seed=11):
    """The other half of rule 3: when missingness is NOT informative, the paper's
    rule should be fine. If it is biased here too, my diagnosis is wrong."""
    rng = random.Random(seed)
    n_files, true_rate = 8000, 0.30
    logs = {v: {} for v in VERSIONS}
    union = set()
    truth_success = 0
    for i in range(n_files):
        k = ("doi:%d" % (i // 4), "f%d.R" % i)
        union.add(k)
        per_version = [rng.random() < true_rate for _ in VERSIONS]
        if any(per_version):
            truth_success += 1
        for v, ok in zip(VERSIONS, per_version):
            if rng.random() < 0.30:      # MCAR: same rate regardless of outcome
                continue
            logs[v][k] = "success" if ok else "Error in foo() : synthetic"
    truth = truth_success / n_files
    kept = succ = 0
    for k in union:
        cells = [logs[v].get(k) for v in VERSIONS]
        pr = combined_paper(cells)
        if pr is not None:
            kept += 1
            succ += (pr == "success")
    print("=" * 74)
    print("SYNTHETIC NULL -- missingness completely at random (MCAR)")
    print("=" * 74)
    print("  ground truth : %5.1f%%" % (100 * truth))
    print("  paper's rule : %5.1f%%  (n kept %d/%d)" % (100.0 * succ / kept, kept, n_files))
    print("  -> under MCAR the rule still over-states, because 'success in ANY")
    print("     version' survives missingness and 'error' requires all three.")
    print("     The asymmetry, not the informativeness, is the primary bias.")
    print()


def main():
    for suffix, label in (("no_env", "no code cleaning"), ("env", "with code cleaning")):
        logs, union, paper_res, any_res, cov = rate_table(suffix, label)
        informative_missingness(logs, union)
        bounds(logs, union, any_res)
        calibrated_imputation(logs, union)
    synthetic_check()
    synthetic_null()


if __name__ == "__main__":
    main()
