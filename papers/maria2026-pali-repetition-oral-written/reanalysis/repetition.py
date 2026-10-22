"""Within-text verbatim repetition by layer (mula / atthakatha / tika), DN and MN, per reanalysis/PLAN.md.

  python -I repetition.py fetch <dest_dir>          # 18 files at the pinned commit, git blob SHA-1 checked
  python -I repetition.py test                      # known-answer checks on synthetic token lists
  python -I repetition.py run <dest_dir> <out_dir>  # the measurement
"""
import csv, hashlib, json, os, re, sys, urllib.request

REPO, COMMIT = 'VipassanaTech/tipitaka-xml', '05d5d3c7cede'
BOOKS = {'DN': ['s0101', 's0102', 's0103'], 'MN': ['s0201', 's0202', 's0203']}
LAYERS = {'mula': 'm.mul', 'atthakatha': 'a.att', 'tika': 't.tik'}
SEG = 20000
H = {'User-Agent': 'zoo-kb/1.0'}


def fetch(dest):
    os.makedirs(dest, exist_ok=True)
    lst = json.loads(urllib.request.urlopen(urllib.request.Request(
        f'https://api.github.com/repos/{REPO}/contents/romn?ref={COMMIT}', headers=H), timeout=60).read())
    want = {f'{b}{s}.xml' for bs in BOOKS.values() for b in bs for s in LAYERS.values()}
    bad = 0
    for x in lst:
        if x['name'] not in want:
            continue
        b = urllib.request.urlopen(urllib.request.Request(x['download_url'], headers=H), timeout=120).read()
        ok = hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest() == x['sha']
        bad += not ok
        open(os.path.join(dest, x['name']), 'wb').write(b)
        print(('ok ' if ok else 'BAD'), x['name'], len(b))
    return bad


def read_tokens(path):
    raw = open(path, 'rb').read()
    for enc in ('utf-8', 'utf-16'):
        try:
            t = raw.decode(enc); break
        except UnicodeDecodeError:
            continue
    t = re.sub(r'<note\b.*?</note>', ' ', t, flags=re.S | re.I)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = re.sub(r'&[a-z]+;', ' ', t)
    toks = re.findall(r'[^\W\d_]+', t.lower())
    pe = sum(1 for w in toks if w == 'pe')
    return [w for w in toks if w != 'pe'], pe


def coverage(toks, n):
    """Share of tokens covered by at least one n-gram occurring >= 2 times in `toks`."""
    if len(toks) < n:
        return 0.0
    grams = {}
    for i in range(len(toks) - n + 1):
        g = tuple(toks[i:i + n]); grams[g] = grams.get(g, 0) + 1
    cov = bytearray(len(toks))
    for i in range(len(toks) - n + 1):
        if grams[tuple(toks[i:i + n])] >= 2:
            cov[i:i + n] = b'\x01' * n
    return sum(cov) / len(toks)


def test():
    import random
    rng = random.Random(1)
    vocab = [f'w{i}' for i in range(5000)]
    toks = [rng.choice(vocab) for _ in range(SEG)]
    assert coverage(toks, 8) < 0.01, coverage(toks, 8)
    half = toks[:10000]
    assert coverage(half + half, 8) == 1.0
    print('known-answer: random tokens R8 =', round(coverage(toks, 8), 4), '; passage + itself R8 =', coverage(half + half, 8))


def run(src, out):
    import random
    rows, layer_stats = [], {}
    for nik, books in BOOKS.items():
        for layer, suf in LAYERS.items():
            toks, pe = [], 0
            for b in books:
                t, p = read_tokens(os.path.join(src, f'{b}{suf}.xml')); toks += t; pe += p
            layer_stats[f'{nik}|{layer}'] = {'tokens': len(toks), 'pe': pe, 'pe_per_1000': 1000 * pe / max(len(toks), 1)}
            for k in range(len(toks) // SEG):
                seg = toks[k * SEG:(k + 1) * SEG]
                r = {f'R{n}': coverage(seg, n) for n in (4, 8, 12)}
                sh = seg[:]; random.Random(k).shuffle(sh)
                r['R8_shuffled'] = coverage(sh, 8)
                rows.append(dict(nikaya=nik, layer=layer, segment=k, **r))
            print(f'{nik} {layer:10s} tokens {len(toks):7d} segments {len(toks) // SEG:3d} pe/1000 {1000 * pe / max(len(toks), 1):.2f}', flush=True)
    with open(os.path.join(out, 'segments.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    json.dump(layer_stats, open(os.path.join(out, 'layer_stats.json'), 'w'), indent=1)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'fetch':
        sys.exit(fetch(sys.argv[2]))
    if cmd == 'test':
        test()
    if cmd == 'run':
        run(sys.argv[2], sys.argv[3])
