"""Break-test for vacuous_flag.py.

A detector that reports a defect on every input is not a detector. This builds
two synthetic `executions` tables with the answer known by construction and
checks that the same three falsification tests fire on one and stay silent on
the other.

CLEAN world  -- E_SAME_RESULTS is set only when cells were actually compared and
                the comparison found no differences. Expect: 0 vacuous rows,
                the falsification tests all pass trivially, and the corrected
                count equals the published count.
BROKEN world -- the pipeline sets E_SAME_RESULTS whenever the comparison loop is
                empty, exactly as run_notebook.py does. Expect: the vacuous rows
                are found, and the corrected count is strictly below the
                published one by the number of vacuous rows.

A third world is included because it is the one that would make me wrong:
NOISY world  -- rows with count=0 exist but are NOT flagged same-results (i.e.
                the pipeline handles the empty-loop case correctly). Expect the
                detector to report vacuous EXECUTIONS but no inflation of the
                reproduction count. This distinguishes "zero cells compared"
                from "wrongly flagged", which are different claims.
"""
import os
import sqlite3
import random

E_EXCEPTION, E_TIMEOUT, E_SAME, E_EXECUTED, E_LOADED, E_INSTALLED = 4, 8, 16, 32, 2, 1
FINISHED_MASK = E_EXECUTED + E_TIMEOUT + E_EXCEPTION
VAC = "(count = 0 OR (count = 1 AND (processed & 8) = 8))"


def build(path, world, n=4000, seed=1):
    rng = random.Random(seed)
    if os.path.exists(path):
        os.remove(path)
    c = sqlite3.connect(path)
    c.execute("create table executions (id integer primary key, mode int, "
              "processed int, reason text, count int, diff_count int)")
    rows = []
    for i in range(n):
        r = rng.random()
        if r < 0.40:                                    # exception
            cnt = rng.randint(1, 30)
            rows.append((i, 5, E_EXECUTED | E_EXCEPTION | E_LOADED | E_INSTALLED,
                         "ModuleNotFoundError", cnt, rng.randint(0, 3)))
        elif r < 0.45:                                  # timeout
            rows.append((i, 5, E_EXECUTED | E_TIMEOUT | E_LOADED | E_INSTALLED,
                         None, rng.randint(2, 20), 0))
        elif r < 0.75:                                  # genuine finish, differs
            cnt = rng.randint(1, 30)
            rows.append((i, 5, E_EXECUTED | E_LOADED | E_INSTALLED, None, cnt,
                         rng.randint(1, cnt)))
        elif r < 0.90:                                  # genuine finish, identical
            cnt = rng.randint(1, 30)
            rows.append((i, 5, E_EXECUTED | E_SAME | E_LOADED | E_INSTALLED, None, cnt, 0))
        else:                                           # nothing ran
            if world == "clean":
                # a correct pipeline: nothing ran, so nothing is asserted about
                # the outputs -- record it as an exception, not as a match
                rows.append((i, 3, E_EXECUTED | E_EXCEPTION | E_LOADED | E_INSTALLED,
                             "KernelStartFailure", 0, None))
            elif world == "broken":
                rows.append((i, 3, E_EXECUTED | E_SAME | E_LOADED | E_INSTALLED, None, 0, 0))
            else:                                       # noisy
                rows.append((i, 3, E_EXECUTED | E_LOADED | E_INSTALLED, None, 0, 0))
    c.executemany("insert into executions values (?,?,?,?,?,?)", rows)
    c.commit()
    return c


def probe(c):
    q = lambda s: c.execute(s).fetchone()[0]
    fin = q("select count(*) from executions where (processed & %d)=%d" % (FINISHED_MASK, E_EXECUTED))
    same = q("select count(*) from executions where (processed & %d)=%d and (processed & 16)=16"
             % (FINISHED_MASK, E_EXECUTED))
    same_real = q("select count(*) from executions where (processed & %d)=%d and (processed & 16)=16 "
                  "and not %s" % (FINISHED_MASK, E_EXECUTED, VAC))
    vac = q("select count(*) from executions where %s" % VAC)
    vac_same = q("select count(*) from executions where %s and (processed & 16)=16" % VAC)
    contradiction = q("select count(*) from executions where count=0 and diff_count>0")
    return dict(finished=fin, same=same, same_real=same_real, vacuous=vac,
                vacuous_flagged_same=vac_same, contradictions=contradiction)


if __name__ == "__main__":
    expect = {
        "clean":  "vacuous rows exist but NONE is flagged same; same_real == same",
        "broken": "vacuous rows all flagged same; same_real << same",
        "noisy":  "vacuous rows exist, none flagged same; same_real == same",
    }
    ok = True
    for world in ("clean", "broken", "noisy"):
        c = build("_bt_%s.sqlite" % world, world)
        r = probe(c)
        c.close()
        os.remove("_bt_%s.sqlite" % world)
        print("%-7s %s" % (world.upper(), expect[world]))
        print("        finished=%d same=%d same_real=%d vacuous=%d vacuous_flagged_same=%d "
              "contradictions=%d" % (r["finished"], r["same"], r["same_real"], r["vacuous"],
                                     r["vacuous_flagged_same"], r["contradictions"]))
        if world == "broken":
            good = r["vacuous_flagged_same"] > 0 and r["same_real"] < r["same"] and r["contradictions"] == 0
        else:
            good = r["vacuous_flagged_same"] == 0 and r["same_real"] == r["same"]
        ok &= good
        print("        -> %s" % ("as expected" if good else "UNEXPECTED"))
    print()
    print("BREAK-TEST PASSED" if ok else "BREAK-TEST FAILED -- the detector is not specific")
