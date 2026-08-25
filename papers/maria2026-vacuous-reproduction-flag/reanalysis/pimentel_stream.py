"""Does Pimentel et al.'s notebook corpus carry the same vacuous-comparison flag?

Samuel & Mietchen state they used Pimentel's reproducibility code. If the defect
documented in this record is inherited, then the two largest notebook
reproducibility studies in existence share it, and the agreement between them
that `maria2026-executability-denominators#c3` reported as convergent validity
was two runs of one bug. That disjunction is the open question in c5, and this
script closes it.

THE OBSTACLE, and why this file is a streamer rather than a query. The released
database is a **14.2 GB gzipped plain-text PostgreSQL dump** (Zenodo 3519618).
There is no PostgreSQL on this machine and no Docker to run one in. But a plain
pg_dump writes each table as a `COPY ... FROM stdin;` block of tab-separated
rows, so the file can be decompressed **as it downloads**, scanned for the one
block that matters, parsed, and discarded. Peak disk use: zero. Peak memory: one
chunk.

WHAT IT COMPUTES, using exactly the definitions established on the Samuel &
Mietchen databases, because the schema is identical (verified: the executions
table has the same `cell`, `count`, `diff_count`, `processed` columns, plus
`has_diffs` and `use_docker`):

    finished = processed & (32+8+4) == 32        E_EXECUTED, no timeout, no exception
    same     = finished & 16                     E_SAME_RESULTS
    vacuous  = count = 0, or count = 1 with the timeout bit

and the same falsification test the reading must pass: **no row may have
count = 0 together with diff_count > 0**, because the comparison loop's bound and
the stored `count` are the same expression.

BONUS. This schema has a `use_docker` column that the Samuel & Mietchen one does
not, so the breakdown by that flag comes free and is the only direct evidence in
either corpus about executions actually run in a container.

Run:
    curl -sL "https://zenodo.org/api/records/3519618/files/db2020-09-22.dump.gz/content" \\
      | python pimentel_stream.py

It stops downloading as soon as the executions block ends, so it does not
necessarily read all 14.2 GB.
"""
import sys
import zlib

TABLE = b"COPY public.executions "
END = b"\\."

# column order from `CREATE TABLE public.executions` in the dump header
COLS = ["id", "notebook_id", "mode", "reason", "msg", "diff", "cell", "count",
        "diff_count", "timeout", "duration", "processed", "skip",
        "repository_id", "has_diffs", "use_docker"]
IDX = {c: i for i, c in enumerate(COLS)}


def ival(s):
    return None if s == "\\N" else int(s)


def main():
    dec = zlib.decompressobj(16 + zlib.MAX_WBITS)
    buf = b""
    in_block = False
    order = None
    n = 0
    read_bytes = 0
    stat = dict(total=0, finished=0, same=0, vac=0, vac_same=0, contradiction=0,
                fin_real=0, same_real=0, docker=0, docker_same=0, docker_vac=0,
                nondocker=0, nondocker_same=0, nondocker_vac=0)
    src = sys.stdin.buffer
    while True:
        chunk = src.read(1 << 20)
        if not chunk:
            break
        prev = read_bytes
        read_bytes += len(chunk)
        # Progress every 500 MB. WITHOUT THIS a run that dies halfway is
        # indistinguishable from a run that finished and found nothing, which
        # is exactly what happened on 2026-08-25: an empty stderr was the only
        # evidence either way.
        if read_bytes // (500 << 20) != prev // (500 << 20):
            sys.stderr.write("... %.1f GB of compressed input read\n"
                             % (read_bytes / 1e9))
            sys.stderr.flush()
        try:
            data = dec.decompress(chunk)
        except zlib.error as e:
            sys.stderr.write("zlib: %s\n" % e)
            break
        if not data:
            continue
        buf += data
        if b"\n" not in buf:
            continue
        lines = buf.split(b"\n")
        buf = lines.pop()
        for ln in lines:
            if not in_block:
                if ln.startswith(TABLE):
                    in_block = True
                    inner = ln.split(b"(", 1)[1].split(b")", 1)[0].decode()
                    order = [c.strip().strip('"') for c in inner.split(",")]
                    sys.stderr.write("found executions block at ~%.2f GB of input\n"
                                     % (read_bytes / 1e9))
                    sys.stderr.write("columns: %s\n" % ", ".join(order))
                continue
            if ln.rstrip() == END:
                in_block = False
                sys.stderr.write("end of block after %d rows\n" % n)
                buf = b""
                src = None
                break
            f = ln.decode("utf-8", "replace").split("\t")
            if len(f) < len(order):
                continue
            g = dict(zip(order, f))
            n += 1
            pr = ival(g.get("processed"))
            cnt = ival(g.get("count"))
            dc = ival(g.get("diff_count"))
            if pr is None:
                continue
            stat["total"] += 1
            fin = (pr & (32 + 8 + 4)) == 32
            same = fin and (pr & 16) == 16
            vac = (cnt == 0) or (cnt == 1 and (pr & 8) == 8)
            if cnt == 0 and dc is not None and dc > 0:
                stat["contradiction"] += 1
            stat["finished"] += fin
            stat["same"] += same
            stat["vac"] += vac
            stat["vac_same"] += (vac and (pr & 16) == 16)
            stat["fin_real"] += (fin and not vac)
            stat["same_real"] += (same and not vac)
            d = str(g.get("use_docker", "")).strip() in ("t", "true", "1")
            k = "docker" if d else "nondocker"
            stat[k] += 1
            stat[k + "_same"] += same
            stat[k + "_vac"] += vac
        if src is None:
            break

    if not stat["total"]:
        print("NO executions rows parsed after %.2f GB of compressed input."
              % (read_bytes / 1e9))
        print("The block was not reached, the transport ended early, or the format")
        print("differs. NOTHING IS CLAIMED -- and note WHICH WAY this fails: a")
        print("version that reported its zero counts as findings would have")
        print("announced a clean corpus. That is Pattern 2 of instance-general/")
        print("software-engineering/silent-data-loss-patterns.md, and refusing to")
        print("conclude from zero operands is the whole of the fix.")
        print("")
        print("The 2026-08-25 run read ~7 GB of 14.2 in 1h55m at about 1 MB/s and")
        print("the transport ended there. If you want it to survive a dropped")
        print("connection, fetch to a local file with `curl --fail --retry 5")
        print("--retry-all-errors -C -` first; the streaming form trades that")
        print("robustness for zero disk.")
        return 1
    print("PIMENTEL et al. executions table  (Zenodo 3519618, db2020-09-22)")
    print("-" * 70)
    print("  rows parsed                                   %9d" % stat["total"])
    print("  finished  (processed & 44 == 32)              %9d" % stat["finished"])
    print("  same results (finished & 16)                  %9d" % stat["same"])
    print()
    print("  FALSIFICATION: rows with count=0 AND diff_count>0  %5d   must be 0"
          % stat["contradiction"])
    print("  executions where ZERO cells were compared     %9d  (%.1f%%)"
          % (stat["vac"], 100.0 * stat["vac"] / stat["total"]))
    print("  ...of which flagged SAME_RESULTS              %9d" % stat["vac_same"])
    print()
    print("  'finished'      %8d  ->  with >=1 cell run       %8d  (%.1f%%)"
          % (stat["finished"], stat["fin_real"],
             100.0 * stat["fin_real"] / max(stat["finished"], 1)))
    print("  'same results'  %8d  ->  with >=1 cell compared  %8d  (%.1f%%)"
          % (stat["same"], stat["same_real"],
             100.0 * stat["same_real"] / max(stat["same"], 1)))
    if stat["same_real"]:
        print("  overstatement of the reproduction count: %.1fx"
              % (stat["same"] / stat["same_real"]))
    print()
    print("  BY use_docker (a column the Samuel & Mietchen schema does not have)")
    for k in ("docker", "nondocker"):
        t = stat[k]
        if not t:
            continue
        print("    %-10s n=%9d  same=%8d (%.2f%%)  vacuous=%8d (%.1f%%)"
              % (k, t, stat[k + "_same"], 100.0 * stat[k + "_same"] / t,
                 stat[k + "_vac"], 100.0 * stat[k + "_vac"] / t))
    return 0


if __name__ == "__main__":
    sys.exit(main())
