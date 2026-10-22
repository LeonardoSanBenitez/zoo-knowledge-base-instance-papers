"""Selection audit cross-tab: selection class x defect outcome, per RUBRIC.md (mapping fixed before running).
Usage (from zoo root): python -I zoo-knowledge-base/instance-papers/papers/maria2026-selection-and-reader-bias/reanalysis/crosstab.py
"""
import json, glob, os, collections, math, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZOO = HERE
while not os.path.isdir(os.path.join(ZOO, 'zoo-knowledge-base')):
    ZOO = os.path.dirname(ZOO)
CLS = os.path.join(HERE, 'classification.json')
if not os.path.exists(CLS):
    CLS = os.path.join(HERE, '..', 'artifacts', 'classification.json')
PAPERS = os.path.join(ZOO, 'zoo-knowledge-base', 'instance-papers', 'papers')
STRONG_C = {'refuted', 'disputed', 'not-identifiable'}
STRONG_Q = {'measures-something-else', 'disputed'}

def outcome(p):
    strong = [];  narrowed = False
    for c in p['claims']:
        s = (c.get('our_assessment') or {}).get('status')
        if s in STRONG_C: strong.append(c['id'] + ':' + s)
        if s == 'accepted-narrower-scope': narrowed = True
        for q in c.get('quantities', []):
            if q.get('status') in STRONG_Q: strong.append(c['id'] + '/q:' + q['status'])
    if strong: return 'defect', sorted(set(strong))
    return ('narrowed' if narrowed else 'clean'), []

def wilson(k, n, z=1.96):
    if n == 0: return (float('nan'),) * 2
    ph = k / n; d = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / d; h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / d
    return c - h, c + h

def main():
    rows = json.load(open(CLS, encoding='utf-8'))['rows']
    recs = {}
    for f in glob.glob(os.path.join(PAPERS, '*', 'paper.json')):
        p = json.load(open(f, encoding='utf-8')); recs[p['id']] = p
    pop = {i for i, p in recs.items() if not i.startswith('maria2026')
           and p['read_depth'] in ('read-and-reanalysed', 'read-and-ran-artifacts')}
    cls = {r[0]: r[1] for r in rows}
    assert set(cls) == pop, (pop - set(cls), set(cls) - pop)
    tab = collections.defaultdict(collections.Counter); detail = []
    for i in sorted(pop):
        o, why = outcome(recs[i]); c = cls[i]
        tab[c][o] += 1; tab[c[0]][o] += 1 if len(c) > 1 else 0
        detail.append((c, o, i, why))
    out = {'n': len(pop), 'table': {}, 'detail': detail}
    print(f'population n={len(pop)}')
    for c in ['F', 'F1', 'F2', 'K', 'C', 'B']:
        t = tab[c]; n = sum(t.values())
        if c == 'F': n = sum(tab['F1'].values()) + sum(tab['F2'].values()); t = tab['F1'] + tab['F2']
        k = t['defect']; lo, hi = wilson(k, n)
        out['table'][c] = {'n': n, 'defect': k, 'narrowed': t['narrowed'], 'clean': t['clean'], 'wilson95': [lo, hi]}
        print(f'{c:3s} n={n:2d} defect={k:2d} narrowed={t["narrowed"]:2d} clean={t["clean"]:2d}  rate={k/n if n else float("nan"):.2f} [{lo:.2f},{hi:.2f}]')
    nb = sum(tab['B'].values()) + sum(tab['C'].values()); kb = tab['B']['defect'] + tab['C']['defect']
    print(f'B+C (not finding-first, not dispute) n={nb} defect={kb} rate={kb/nb:.2f} {wilson(kb, nb)}')
    for d in detail: print('  ', d[0].ljust(3), d[1].ljust(9), d[2], ' '.join(d[3])[:110])
    json.dump(out, open(os.path.join(HERE, '..', 'artifacts', 'crosstab_out.json'), 'w', encoding='utf-8'), indent=1)

if __name__ == '__main__':
    main()
