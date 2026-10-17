"""Known-answer test for pimentel2019_stream.py: a synthetic tar.bz2 holding a plain pg_dump with a planted executions block.
Planted: 2 vacuous 'same' (count 0, processed 32|16; count 1 + timeout is NOT finished so not counted), 3 real 'same'
(count >= 1), 1 count-0 row WITH diffs (must be counted by the falsification counter), 2 not-finished rows."""
import bz2, io, os, subprocess, sys, tarfile, json, tempfile, pathlib
B = chr(92)
rows = [  # id, notebook_id, mode, processed, count, diff_count, skip
 (1, 1, 3, 32 | 16, 0, 0, 0), (2, 2, 3, 32 | 16, 0, 0, 0),
 (3, 3, 3, 32 | 16, 4, 0, 0), (4, 4, 3, 32 | 16, 2, 0, 0), (5, 5, 5, 32 | 16, 7, 0, 0),
 (6, 6, 3, 32, 0, 3, 0),
 (7, 7, 3, 32 | 4, 1, 0, 0), (8, 8, 3, 32 | 8 | 16, 1, 0, 0)]
lines = ['--', '-- PostgreSQL database dump', 'COPY public.cells (id, source) FROM stdin;', '1' + '\t' + 'print(1)', B + '.',
         'COPY public.executions (id, notebook_id, mode, processed, count, diff_count, skip) FROM stdin;']
lines += ['\t'.join(str(x) for x in r) for r in rows] + [B + '.', 'COPY public.features (id) FROM stdin;', '1', B + '.', '']
payload = '\n'.join(lines).encode()
tmp = pathlib.Path(tempfile.mkdtemp()); raw = io.BytesIO()
with tarfile.open(fileobj=raw, mode='w') as tf:
    ti = tarfile.TarInfo('db.dump'); ti.size = len(payload); tf.addfile(ti, io.BytesIO(payload))
(tmp / 'd.tar.bz2').write_bytes(bz2.compress(raw.getvalue()))
env = dict(os.environ, DUMP_URL=(tmp / 'd.tar.bz2').as_uri())
out = tmp / 'r.json'
subprocess.run([sys.executable, 'pimentel2019_stream.py', str(out)], env=env, check=True, capture_output=True)
r = json.load(open(out))['all']
expect = {'rows': 8, 'finished': 6, 'same': 5, 'same_vacuous': 2, 'count0': 3, 'count0_and_diff_gt0': 1, 'same_count_ge1': 3}
bad = {k: (r.get(k), v) for k, v in expect.items() if r.get(k) != v}
print('BREAKTEST', 'PASS' if not bad else f'FAIL {bad}', '| parsed:', r)
