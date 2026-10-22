"""Try to break the selection-audit result before believing it.

Reads the corpus's own 1.6 fields (selection, origin) -- the same source `kb.py selection` reads.
Sections:
  1. headline, reader claims excluded (the 1.6 consumer rule)
  2. outcome threshold: strong defect vs ANY finding (defect or narrowed)
  3. adversarial reclassification: every record whose selection evidence was written after the
     finding is moved to 'suspected' if it has a defect, to 'not suspected' if it has none --
     the reclassification that most favours a selection effect
  4. power: smallest true difference in defect rate a Fisher test at these n would detect 80% of
     the time (simulation)
  5. known-answer control for the counting: synthetic corpora with a selection effect forced in
     (0.9 vs 0.3) and absent (0.5 vs 0.5), through the same outcome function and test
Usage (from zoo root): python -I zoo-knowledge-base/instance-papers/papers/maria2026-selection-and-reader-bias/reanalysis/sensitivity.py
stdlib only. Seeds fixed.
"""
import glob, json, os, random
from math import comb


def fisher_exact(t):
    """Two-sided Fisher exact test (sum of tables no more probable than the observed), stdlib only.
    Checked against scipy.stats.fisher_exact on [[5,3],[15,23]] -> 0.2674 and [[5,3],[14,15]] -> 0.6928."""
    (a, b), (c, d) = t
    r1, c1, n = a + b, a + c, a + b + c + d
    pr = lambda x: comb(c1, x) * comb(n - c1, r1 - x) / comb(n, r1)
    p0 = pr(a)
    lo, hi = max(0, r1 - (n - c1)), min(r1, c1)
    return None, min(1.0, sum(pr(x) for x in range(lo, hi + 1) if pr(x) <= p0 * (1 + 1e-7)))

HERE = os.path.dirname(os.path.abspath(__file__))
ZOO = HERE
while not os.path.isdir(os.path.join(ZOO, 'zoo-knowledge-base')):
    ZOO = os.path.dirname(ZOO)
PAPERS = os.path.join(ZOO, 'zoo-knowledge-base', 'instance-papers', 'papers')
STRONG_C = ('refuted', 'disputed', 'not-identifiable')
STRONG_Q = ('measures-something-else', 'disputed')
SUSPECTED = ('finding-first', 'hypothesis-test')


def outcome(r):
    strong = narrowed = False
    for c in r['claims']:
        if c.get('origin') == 'reader':
            continue
        st = c['our_assessment']['status']
        strong |= st in STRONG_C or any(q.get('status') in STRONG_Q for q in c.get('quantities', []))
        narrowed |= st == 'accepted-narrower-scope'
    return 'defect' if strong else ('narrowed' if narrowed else 'clean')


def fisher(a, b):
    """a, b: lists of booleans (event per record)."""
    t = [[sum(a), len(a) - sum(a)], [sum(b), len(b) - sum(b)]]
    return fisher_exact(t)[1]


recs = []
for f in sorted(glob.glob(os.path.join(PAPERS, '*', 'paper.json'))):
    r = json.load(open(f, encoding='utf-8'))
    if r.get('selection') and not r['id'].startswith('maria2026-'):
        recs.append(r)
print(f'n = {len(recs)} records with selection (zoo studies excluded)')

# 1
sus = [outcome(r) == 'defect' for r in recs if r['selection']['class'] in SUSPECTED]
oth = [outcome(r) == 'defect' for r in recs if r['selection']['class'] not in SUSPECTED + ('unknown',)]
print(f'1. strong defect: suspected {sum(sus)}/{len(sus)}, not suspected {sum(oth)}/{len(oth)}, '
      f'Fisher p = {fisher(sus, oth):.3f}')
clean = sum(outcome(r) == 'clean' for r in recs)
print(f'   clean records: {clean}/{len(recs)}')

# 2
sus2 = [outcome(r) != 'clean' for r in recs if r['selection']['class'] in SUSPECTED]
oth2 = [outcome(r) != 'clean' for r in recs if r['selection']['class'] not in SUSPECTED + ('unknown',)]
print(f'2. ANY finding: suspected {sum(sus2)}/{len(sus2)}, not suspected {sum(oth2)}/{len(oth2)}, '
      f'Fisher p = {fisher(sus2, oth2):.3f}')

# 3
hind = [r for r in recs if 'written after the finding' in r['selection']['evidence']]
s3, o3 = [], []
for r in recs:
    d = outcome(r) == 'defect'
    if r in hind:
        (s3 if d else o3).append(d)
    elif r['selection']['class'] in SUSPECTED:
        s3.append(d)
    elif r['selection']['class'] != 'unknown':
        o3.append(d)
print(f'3. adversarial reclassification of the {len(hind)} hindsight records '
      f'({", ".join(r["id"].split("-")[0] for r in hind)}): suspected {sum(s3)}/{len(s3)}, '
      f'not suspected {sum(o3)}/{len(o3)}, Fisher p = {fisher(s3, o3):.3f}')

# 4
rng = random.Random(20261022)
n1, n2, base = len(sus), len(oth), sum(oth) / len(oth)
print(f'4. power at n = {n1} vs {n2}, base rate {base:.2f}, alpha 0.05, 2000 sims per point:')
for p1 in (0.6, 0.7, 0.8, 0.9, 1.0):
    hits = 0
    for _ in range(2000):
        a = [rng.random() < p1 for _ in range(n1)]
        b = [rng.random() < base for _ in range(n2)]
        hits += fisher(a, b) < 0.05
    print(f'     true suspected rate {p1:.1f} (difference {p1 - base:+.2f}): power {hits / 2000:.2f}')

# 5
def synth(p_sus, p_oth, n_sus=40, n_oth=200, seed=1):
    g = random.Random(seed)
    out = []
    for cls, p in (('finding-first', p_sus), ('blind', p_oth)):
        n = n_sus if cls == 'finding-first' else n_oth
        for i in range(n):
            st = 'refuted' if g.random() < p else 'accepted'
            out.append({'id': f'x{i}', 'selection': {'class': cls},
                        'claims': [{'id': 'c1', 'our_assessment': {'status': st}},
                                   {'id': 'c2', 'origin': 'reader',
                                    'our_assessment': {'status': 'refuted'}}]})
    return out

for lab, ps, po in (('effect forced in (0.9 vs 0.3)', 0.9, 0.3), ('effect absent (0.5 vs 0.5)', 0.5, 0.5)):
    rs = synth(ps, po)
    a = [outcome(r) == 'defect' for r in rs if r['selection']['class'] in SUSPECTED]
    b = [outcome(r) == 'defect' for r in rs if r['selection']['class'] not in SUSPECTED]
    print(f'5. known answer, {lab}: {sum(a)}/{len(a)} vs {sum(b)}/{len(b)}, Fisher p = {fisher(a, b):.2g}'
          f'   (every record carries a refuted READER claim; if origin were ignored, both would read 100%)')
