"""Close c5: does Pimentel et al. 2019's OWN execution data show the vacuous 'same results' flag?
Code audit (2026-10-16 evening): Pimentel's archaeology/run_notebook.py (Zenodo 2592524, jupyter_reproducibility.tar.bz2,
md5 e35b9fd702cc9048a227ce7dc23bdb0c) has the identical comparison: loop bound = last_try[0] + 1 - timeout = count - timeout,
and E_SAME_RESULTS is set when the diff list is empty, including after zero iterations. Latent; whether it FIRES is a data
question. Streams Zenodo 2592524 dump.tar.bz2 (7.65 GB -> one 55.7 GB plain-SQL pg_dump inside a tar) through Python's bz2,
parses only the `COPY public.executions` block, stops at its end. Nothing written to disk.
Definitions are the authors' (N8.Execution.ipynb): finished = processed & (32+8+4) == 32; same = finished & 16."""
import bz2, json, sys, time, urllib.request, collections
import os
URL = os.environ.get('DUMP_URL', 'https://zenodo.org/api/records/2592524/files/dump.tar.bz2/content')
OUT = sys.argv[1] if len(sys.argv) > 1 else 'pimentel2019_stream.json'
req = urllib.request.Request(URL, headers={'User-Agent': 'zoo-kb/1.0'})
resp = urllib.request.urlopen(req, timeout=120)
dec = bz2.BZ2Decompressor(); buf = b''; skipped_tar_header = False; state = 'seek'; cols = None
st = collections.Counter(); bymode = collections.defaultdict(collections.Counter); t0 = time.time(); nin = 0; last = t0
def handle(row):
    v = dict(zip(cols, row))
    def i(k):
        x = v.get(k, r'\N'); return None if x in (r'\N', '') else int(float(x))
    pr = i('processed') or 0; cnt = i('count'); dc = i('diff_count'); mode = v.get('mode', '?'); skip = i('skip') or 0
    fin = (pr & 44) == 32; same = fin and bool(pr & 16); timeout = bool(pr & 8)
    vac = same and (cnt == 0 or (cnt == 1 and timeout))
    for key, c in (('all', st), (f'mode={mode}', bymode[mode])):
        c['rows'] += 1; c['finished'] += fin; c['same'] += same; c['same_vacuous'] += vac
        c['count0'] += (cnt == 0); c['count0_and_diff_gt0'] += (cnt == 0 and (dc or 0) > 0)
        c['same_count_ge1'] += (same and (cnt or 0) >= 1)
        if skip == 0: c['skip0_same'] += same; c['skip0_same_vacuous'] += vac
while True:
    chunk = resp.read(1 << 20)
    if not chunk: break
    nin += len(chunk)
    try: data = dec.decompress(chunk)
    except EOFError: break
    if not skipped_tar_header:
        data = data[512:]; skipped_tar_header = True
    buf += data
    lines = buf.split(b'\n'); buf = lines.pop()
    for ln in lines:
        if state == 'seek':
            if ln.startswith(b'COPY public.executions '):
                s = ln.decode(); cols = [c.strip().strip('"') for c in s[s.index('(') + 1:s.index(')')].split(',')]
                state = 'in'; print('found executions block; columns:', cols, flush=True)
        elif state == 'in':
            if ln == b'\\.': state = 'done'; break
            handle(ln.decode('utf-8', 'replace').split('\t'))
    if time.time() - last > 60:
        last = time.time(); print(f'{nin/1e9:.2f} GB downloaded, {time.time()-t0:.0f}s, state={state}, exec rows={st["rows"]}', flush=True)
    if state == 'done': break
res = {'state': state, 'compressed_bytes_read': nin, 'seconds': round(time.time() - t0), 'all': dict(st), 'by_mode': {k: dict(v) for k, v in bymode.items()}}
json.dump(res, open(OUT, 'w'), indent=1); print(json.dumps(res, indent=1))
if state != 'done': print('EXECUTIONS BLOCK NOT COMPLETED -- nothing is claimed.')
