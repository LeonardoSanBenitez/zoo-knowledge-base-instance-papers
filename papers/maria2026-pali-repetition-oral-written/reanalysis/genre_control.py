"""Addendum A1/A2 of PLAN.md: Abhidhamma (Dhammasangani + Vibhanga, canonical, scholastic) vs Visuddhimagga
(5th-c. treatise, written). Same measure as repetition.py run.
Usage: python -I genre_control.py fetch <dest_dir> | run <dest_dir> <out_dir>
"""
import hashlib, json, os, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from repetition import REPO, COMMIT, H, SEG, read_tokens, coverage

TEXTS = {'abhidhamma': ['abh01m.mul.xml', 'abh02m.mul.xml'], 'visuddhimagga': ['e0101n.mul.xml', 'e0102n.mul.xml']}
TEXTS2 = {'dhatukatha': ['abh03m1.mul.xml'], 'puggalapannatti': ['abh03m2.mul.xml'], 'kathavatthu': ['abh03m3.mul.xml'],
          'milindapanha': ['s0518m.nrf.xml'], 'nettippakarana': ['s0519m.mul.xml'], 'petakopadesa': ['s0520m.nrf.xml']}
if len(sys.argv) > 4 and sys.argv[4] == 'addendum2':
    TEXTS = TEXTS2


def fetch(dest):
    lst = json.loads(urllib.request.urlopen(urllib.request.Request(
        f'https://api.github.com/repos/{REPO}/contents/romn?ref={COMMIT}', headers=H), timeout=60).read())
    want = {f for fs in list(TEXTS.values()) + list(TEXTS2.values()) for f in fs}
    bad = 0
    for x in lst:
        if x['name'] in want:
            b = urllib.request.urlopen(urllib.request.Request(x['download_url'], headers=H), timeout=120).read()
            ok = hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest() == x['sha']; bad += not ok
            open(os.path.join(dest, x['name']), 'wb').write(b); print(('ok ' if ok else 'BAD'), x['name'], len(b))
    return bad


def run(src, out):
    res = {}
    for name, files in TEXTS.items():
        toks, pe = [], 0
        for f in files:
            t, p = read_tokens(os.path.join(src, f)); toks += t; pe += p
        segs = [toks[k * SEG:(k + 1) * SEG] for k in range(len(toks) // SEG)] or [toks]   # short books: one window
        r = {n: [coverage(s, n) for s in segs] for n in (4, 8, 12)}
        res[name] = {'tokens': len(toks), 'segments': len(segs), 'pe_per_1000': 1000 * pe / len(toks),
                     **{f'R{n}_mean': sum(v) / len(v) for n, v in r.items()},
                     'R8_min': min(r[8]), 'R8_max': max(r[8])}
        print(f"{name:14s} tokens {len(toks)} segments {len(segs)} pe/1000 {res[name]['pe_per_1000']:.2f}  "
              f"R4 {res[name]['R4_mean']:.3f}  R8 {res[name]['R8_mean']:.3f} [{min(r[8]):.3f}, {max(r[8]):.3f}]  R12 {res[name]['R12_mean']:.3f}")
    if 'abhidhamma' in res:
        a, v = res['abhidhamma']['R8_mean'], res['visuddhimagga']['R8_mean']
        res['A1_held'] = a >= 0.30 and v < 0.10
        res['A2_held'] = a < 0.30 and v < 0.10
        print('A1 (canonical transmission) held:', res['A1_held'], '| A2 (discourse genre) held:', res['A2_held'])
        json.dump(res, open(os.path.join(out, 'genre_control_out.json'), 'w'), indent=1)
    else:
        res['B1_held'] = all(res[k]['R8_mean'] >= 0.30 for k in ('dhatukatha', 'puggalapannatti', 'kathavatthu'))
        res['B2_held'] = all(res[k]['R8_mean'] < 0.10 for k in ('milindapanha', 'nettippakarana', 'petakopadesa'))
        print('B1 (Abhidhamma books >= 0.30):', res['B1_held'], '| B2 (late books composed as books < 0.10):', res['B2_held'])
        json.dump(res, open(os.path.join(out, 'addendum2_out.json'), 'w'), indent=1)


if __name__ == '__main__':
    if sys.argv[1] == 'fetch':
        sys.exit(fetch(sys.argv[2]))
    run(sys.argv[2], sys.argv[3])
