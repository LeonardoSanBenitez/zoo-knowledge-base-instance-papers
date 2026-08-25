"""E_SAME_RESULTS is set whenever ZERO cells were compared.

Samuel & Mietchen 2024 (GigaScience 13:giad113) report that of 27,271 Jupyter
notebooks from PubMed Central papers, 1,203 ran without errors and 879 "produced
results identical to those recorded in the original notebook". This script shows
that 815 of those 879 had no comparison performed at all.

THE MECHANISM, from their own `archaeology/run_notebook.py`:

    ep.last_try = (-1, -1)                                     # line 174
    ...
    self.execution.count = ep.last_try[0] + 1                  # line 224
    ...
    for _, index in zip(range(ep.last_try[0] + 1 - timeout), ep.cell_order):
        ...  compare old vs new cell, append to `diff` ...     # line 229-250
    if not diff:
        self.execution.processed |= consts.E_SAME_RESULTS      # line 259-264
        self.execution.diff_count = 0

The stored `count` column and the loop bound are THE SAME EXPRESSION,
`ep.last_try[0] + 1`. So `count == 0` implies the loop ran zero iterations,
implies `diff == []`, implies E_SAME_RESULTS is set unconditionally -- whether or
not the notebook executed anything. Likewise `count == 1` with the timeout flag
set gives `range(0)`.

The paper's own analysis helper (`analyses/analysis_helpers_executions.py`) is
where the reported numbers come from, and it is reproduced here verbatim:

    finished = executions[ np.bitwise_and(processed, 32+8+4) == 32 ]   # 1,203
    same     = finished[   np.bitwise_and(processed, 16)     == 16 ]   #   879

Bit meanings from `archaeology/consts.py`:
    E_INSTALLED 1, E_LOADED 2, E_EXCEPTION 4, E_TIMEOUT 8,
    E_SAME_RESULTS 16, E_EXECUTED 32

DATA. 1.49 GB SQLite inside a 415.6 MB zip. Not committed anywhere. Regenerate:

    curl -sL -o crpmc-2023.zip \\
      "https://zenodo.org/api/records/8226725/files/computational-reproducibility-pmc.zip/content"
    python -c "import zipfile,shutil; z=zipfile.ZipFile('crpmc-2023.zip'); \\
      shutil.copyfileobj(z.open('computational-reproducibility-pmc/computational-reproducibility-pmc/analyses/db.sqlite'), \\
      open('db2023.sqlite','wb'), 1<<23)"

Usage:  python vacuous_flag.py /path/to/db2023.sqlite
"""
import sqlite3
import sys

E_EXCEPTION, E_TIMEOUT, E_SAME, E_EXECUTED = 4, 8, 16, 32
FINISHED = "(processed & %d) = %d" % (E_EXECUTED + E_TIMEOUT + E_EXCEPTION, E_EXECUTED)
SAME = "(processed & %d) = %d" % (E_SAME, E_SAME)
# zero cells were compared: the loop bound range(count - timeout_flag) is empty
VACUOUS = "(count = 0 OR (count = 1 AND (processed & %d) = %d))" % (E_TIMEOUT, E_TIMEOUT)


def one(c, sql):
    return c.execute(sql).fetchone()[0]


def main(path):
    c = sqlite3.connect(path)
    rule = "-" * 74

    print("REPRODUCING THE PAPER'S OWN NUMBERS, using the authors' own filters")
    print(rule)
    attempted = one(c, "select count(*) from executions")
    notebooks = one(c, "select count(*) from notebooks")
    finished = one(c, "select count(*) from executions where %s" % FINISHED)
    same = one(c, "select count(*) from executions where %s and %s" % (FINISHED, SAME))
    print("  notebooks in corpus                     %6d   (paper: 27,271)" % notebooks)
    print("  executions attempted                    %6d" % attempted)
    print("  'ran through without any errors'        %6d   (paper: 1,203)" % finished)
    print("  'results identical to those recorded'   %6d   (paper:   879)" % same)
    ok = (notebooks, finished, same) == (27271, 1203, 879)
    print("  exact match to the published figures: %s" % ("YES" if ok else "NO -- STOP"))
    if not ok:
        return 1

    print()
    print("FALSIFICATION TESTS of the reading of the loop bound")
    print(rule)
    bad = one(c, "select count(*) from executions where count = 0 and diff_count > 0")
    print("  rows with count=0 AND diff_count>0        %6d   must be 0" % bad)
    z = one(c, "select count(*) from executions where count = 0")
    zs = one(c, "select count(*) from executions where count = 0 and %s" % SAME)
    print("  rows with count=0                        %6d" % z)
    print("  ...of which flagged SAME_RESULTS         %6d   must equal the line above" % zs)
    mn = c.execute("select min(count) from executions where diff_count > 0").fetchone()[0]
    print("  min `count` among rows with diff_count>0 %6s   must be >= 1" % mn)
    passed = (bad == 0 and z == zs and (mn or 0) >= 1)
    print("  reading of the loop bound: %s" % ("CONFIRMED" if passed else "REFUTED -- STOP"))
    if not passed:
        return 1

    print()
    print("THE CORRECTION")
    print(rule)
    vac_all = one(c, "select count(*) from executions where %s" % VACUOUS)
    vac_same = one(c, "select count(*) from executions where %s and %s" % (VACUOUS, SAME))
    print("  executions where ZERO cells were compared          %6d  (%.1f%% of attempts)"
          % (vac_all, 100.0 * vac_all / attempted))
    print("  ...of which carry the SAME_RESULTS flag            %6d  (%.1f%%)"
          % (vac_same, 100.0 * vac_same / vac_all))
    fin_real = one(c, "select count(*) from executions where %s and not %s" % (FINISHED, VACUOUS))
    same_real = one(c, "select count(*) from executions where %s and %s and not %s"
                    % (FINISHED, SAME, VACUOUS))
    print()
    print("  'ran without errors'    published %5d  ->  with >=1 cell run      %5d  (%.1f%%)"
          % (finished, fin_real, 100.0 * fin_real / finished))
    print("  'identical results'     published %5d  ->  with >=1 cell compared %5d  (%.1f%%)"
          % (same, same_real, 100.0 * same_real / same))
    print("  overstatement of the reproduction count: %.1fx" % (same / same_real))
    print()
    print("  reproduction rate over all notebooks, published  %.4f  (%d/%d)"
          % (same / notebooks, same, notebooks))
    print("  reproduction rate over all notebooks, corrected  %.4f  (%d/%d)"
          % (same_real / notebooks, same_real, notebooks))

    print()
    print("BY ARM -- and why the arms must NOT be compared on this outcome")
    print(rule)
    print("  mode 3 = repository DECLARED dependencies, they were installed")
    print("  mode 5 = repository declared NOTHING, executed in an anaconda base env")
    print()
    print("  mode      n   finished  same  same&real   exception-rows  of those count=0")
    for m in (3, 5):
        n = one(c, "select count(*) from executions where mode=%d" % m)
        f = one(c, "select count(*) from executions where mode=%d and %s" % (m, FINISHED))
        s = one(c, "select count(*) from executions where mode=%d and %s and %s" % (m, FINISHED, SAME))
        sr = one(c, "select count(*) from executions where mode=%d and %s and %s and not %s"
                 % (m, FINISHED, SAME, VACUOUS))
        ex = one(c, "select count(*) from executions where mode=%d and (processed & 4)=4" % m)
        ex0 = one(c, "select count(*) from executions where mode=%d and (processed & 4)=4 and count=0" % m)
        print("   %d   %6d %7d %7d %8d %14d %14d" % (m, n, f, s, sr, ex, ex0))
    print()
    print("  A row that raised a CELL execution error must have run a cell. In mode 3")
    print("  such rows have count=0 almost always, so `count` is not a faithful record")
    print("  of cells executed in that arm -- the tracker does not advance there. That")
    print("  does NOT weaken the correction above (the loop bound is the same variable,")
    print("  so nothing was compared either way) but it does mean the declared-vs-not")
    print("  comparison on this outcome measures the instrumentation, not the world.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "db2023.sqlite"))
