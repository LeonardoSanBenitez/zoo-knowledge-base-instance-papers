"""Recompute the need distribution from the shipped modality corpus (fold 0 train+dev + test = one copy of the corpus),
approximating the authors' spaCy AUX filter by their own closed token list."""
import csv, re, collections, os
C = os.path.join(os.environ.get('MODALS_DS', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'artifacts')), 'corpus')
lab = {'S_knowledge': 'epistemic', 'S_rules': 'deontic', 'S_world': 'circumstantial'}
force = {"would": "strong", "ought": "strong", "may": "weak", "might": "weak", "ca": "weak", "could": "weak", "need": "strong", "can": "weak", "'d": "strong", "should": "strong", "must": "strong"}
cnt = collections.Counter()
for fn in ['0_train.txt', '0_dev.txt', 'test_test.txt']:
    for r in csv.DictReader(open(os.path.join(C, fn), encoding='utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE):
        g = re.sub(r'([a-z])\-([a-z])', r'\1_\2', r['gold_modal'] or '', flags=re.I)
        t = (r['token'] or '').lower()
        if g in lab and t in force: cnt[(force[t], lab[g])] += 1
tot = sum(cnt.values())
for fo in ['weak', 'strong']:
    print(fo, {fl: round(cnt[(fo, fl)] / tot, 3) for fl in ['epistemic', 'deontic', 'circumstantial']}, {fl: cnt[(fo, fl)] for fl in ['epistemic', 'deontic', 'circumstantial']})
print('total', tot)
