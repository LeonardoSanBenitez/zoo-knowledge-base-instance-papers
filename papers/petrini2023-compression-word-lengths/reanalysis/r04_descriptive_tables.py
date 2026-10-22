"""r04: do the paper's descriptive tables (n types, T tokens; Tables 4, 5, B1, B2 -- generated from
data/filtered/descriptive_tables/*.csv) describe the files the results were computed from?
The results (L, L_r, tau, r) reproduce exactly from the corpora files (r01), so the files are the
analysed data; a mismatch means the printed n, T describe some other state of the pipeline.
Usage: python -I r04_descriptive_tables.py <repo_dir>
"""
import csv, os, sys

root = sys.argv[1]


def rows(p):
    out = []
    with open(p, encoding='utf-8') as fh:
        rd = csv.reader(fh); h = next(rd)
        for r in rd:
            if len(r) == len(h) + 1:
                r = r[1:]
            out.append(dict(zip(h, r)))
    return out


for coll, desc, pat in (('pud', 'pud.csv', 'pud/{}_pud.csv'), ('cv', 'common_voice.csv', 'cv/{}-word.csv')):
    mism = tot = 0
    for d in csv.DictReader(open(os.path.join(root, 'data', 'filtered', 'descriptive_tables', desc), encoding='utf-8')):
        p = os.path.join(root, 'data', 'filtered', 'corpora', *pat.format(d['iso_code']).split('/'))
        r = rows(p)
        n, T = len(r), sum(int(x['frequency']) for x in r)
        tot += 1
        if n != int(d['#types']) or T != int(d['#tokens']):
            mism += 1
            print(f"  {coll} {d['language'][:18]:18s} printed n={d['#types']:>7s} T={d['#tokens']:>8s}   "
                  f"file n={n:7d} T={T:8d}   dn={n - int(d['#types']):+d} dT={T - int(d['#tokens']):+d}")
    print(f'{coll}: {mism} of {tot} descriptive rows do not describe the analysed file')
