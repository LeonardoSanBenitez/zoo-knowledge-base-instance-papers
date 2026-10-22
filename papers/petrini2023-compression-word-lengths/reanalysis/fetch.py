"""Fetch the authors' deposit at the commit current when arXiv v2 appeared (2023-05-27).

Pinned commit: e8c15fd67b (2023-03-29, last commit on main before v2; later commits of 2023-09 re-ran
filtering for a different article, so HEAD is NOT the paper's state). Files are verified against the
git blob SHA-1 from the tree listing (git's own content hash: sha1(b'blob <len>\\0' + bytes)).

Usage (from zoo root): python -I zoo-knowledge-base/instance-papers/papers/petrini2023-compression-word-lengths/reanalysis/fetch.py <dest_dir>
Downloads data/filtered/corpora/**, data/filtered/descriptive_tables/**, results/filtered/**,
code/analysis/** (about 64 MB). Network: GitHub API (1 call) + raw.githubusercontent.com.
"""
import hashlib, json, os, sys, urllib.request

REPO = 'IQL-course/IQL-Research-Project-21-22'
COMMIT = 'e8c15fd67b'
H = {'User-Agent': 'zoo-kb/1.0'}
WANT = ('data/filtered/corpora/', 'data/filtered/descriptive_tables/', 'results/filtered/', 'code/analysis/')


def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=120).read()


def main(dest):
    tree = json.loads(get(f'https://api.github.com/repos/{REPO}/git/trees/{COMMIT}?recursive=1'))
    assert not tree['truncated']
    full = tree['sha']
    n = bad = 0
    for x in tree['tree']:
        if x['type'] != 'blob' or not x['path'].startswith(WANT):
            continue
        b = get(f'https://raw.githubusercontent.com/{REPO}/{full}/{x["path"]}')
        ok = hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest() == x['sha']
        p = os.path.join(dest, *x['path'].split('/'))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'wb').write(b)
        n += 1
        bad += not ok
        if not ok:
            print('HASH MISMATCH', x['path'])
    print(f'{n} files, {bad} hash mismatches, tree {full}')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
