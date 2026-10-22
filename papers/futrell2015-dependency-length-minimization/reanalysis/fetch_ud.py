"""Fetch the twelve pre-registered UD treebanks at tag r2.14, every .conllu file, each verified against its
git blob SHA-1 from the GitHub contents listing.
Usage (from zoo root): python -I zoo-knowledge-base/instance-papers/papers/futrell2015-dependency-length-minimization/reanalysis/fetch_ud.py <dest_dir>
"""
import hashlib, json, os, sys, urllib.request

TAG = 'r2.14'
TREEBANKS = ['UD_English-EWT', 'UD_German-GSD', 'UD_Italian-ISDT', 'UD_Indonesian-GSD', 'UD_Irish-IDT',
             'UD_Finnish-TDT', 'UD_Japanese-GSD', 'UD_Korean-GSD', 'UD_Turkish-IMST', 'UD_Telugu-MTG',
             'UD_Ancient_Greek-Perseus', 'UD_Chinese-GSD']
H = {'User-Agent': 'zoo-kb/1.0'}


def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=120).read()


def main(dest):
    bad = total = 0
    for tb in TREEBANKS:
        lst = json.loads(get(f'https://api.github.com/repos/UniversalDependencies/{tb}/contents/?ref={TAG}'))
        os.makedirs(os.path.join(dest, tb), exist_ok=True)
        for x in lst:
            if not x['name'].endswith('.conllu'):
                continue
            b = get(x['download_url'])
            ok = hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest() == x['sha']
            open(os.path.join(dest, tb, x['name']), 'wb').write(b)
            total += len(b); bad += not ok
            print(f'{"ok " if ok else "BAD"} {tb}/{x["name"]} {len(b)}')
    print(f'{total / 1e6:.1f} MB, {bad} hash mismatches, tag {TAG}')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
