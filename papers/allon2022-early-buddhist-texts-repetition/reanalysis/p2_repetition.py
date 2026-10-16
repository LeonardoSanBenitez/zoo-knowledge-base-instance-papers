"""Allon (1997; restated Allon 2022, J Indian Philos 50:523) hand-counted DN 25: ~30% verbatim repetition, ~35% more
with minor modification, ~87% 'quantifiable repetition of one kind or another'. Measure: share of a sutta's words covered
by any word n-gram occurring >= 2 times WITHIN the same sutta, for n = 3..12, on the Pali root text (bilara-data, MS ed.).
Known-answer control: the same sutta with its words shuffled. Then: where DN 25 sits among DN and MN."""
import os, re, json, glob, random, statistics as st
ROOT = os.environ.get('PALI', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
W = re.compile(r"[a-zA-ZĀ-ſḀ-ỿ]+")
def words(path):
    d = json.load(open(path, encoding='utf-8'))
    return [w.lower() for seg in d.values() for w in W.findall(seg)]
def coverage(ws, n):
    if len(ws) < n: return 0.0
    from collections import Counter
    grams = [tuple(ws[i:i + n]) for i in range(len(ws) - n + 1)]; c = Counter(grams)
    cov = [False] * len(ws)
    for i, g in enumerate(grams):
        if c[g] >= 2:
            for j in range(i, i + n): cov[j] = True
    return sum(cov) / len(ws)
NS = (3, 4, 6, 8, 12)
files = sorted(glob.glob(os.path.join(ROOT, 'bilara', 'root', 'pli', 'ms', 'sutta', d, '*.json')) for d in ('dn', 'mn'))
files = [f for grp in files for f in grp]
rows = {}
for f in files:
    k = os.path.basename(f).split('_')[0]; ws = words(f)
    rows[k] = {'words': len(ws), **{f'n{n}': round(coverage(ws, n), 3) for n in NS}}
dn25 = rows['dn25']; ws = words([f for f in files if os.path.basename(f).startswith('dn25_')][0])
rng = random.Random(0); sh = ws[:]; rng.shuffle(sh)
print('DN 25:', dn25, '| shuffled control:', {f'n{n}': round(coverage(sh, n), 3) for n in NS})
print("Allon's hand count for DN 25: verbatim ~0.30; verbatim + minor modification ~0.65; any quantifiable repetition ~0.87")
for n in NS:
    v = sorted(r[f'n{n}'] for r in rows.values()); rank = sum(1 for x in v if x > dn25[f'n{n}'])
    print(f'n={n:2d}: DN25 {dn25[f"n{n}"]:.3f} | corpus (DN+MN, {len(v)} suttas) median {st.median(v):.3f}, IQR {v[len(v)//4]:.3f}-{v[3*len(v)//4]:.3f} | suttas above DN25: {rank}')
# correlation with length (longer suttas have more chance to repeat)
import math
L = [math.log(r['words']) for r in rows.values()]; C = [r['n6'] for r in rows.values()]
mL, mC = st.mean(L), st.mean(C); r = sum((a - mL) * (b - mC) for a, b in zip(L, C)) / math.sqrt(sum((a - mL) ** 2 for a in L) * sum((b - mC) ** 2 for b in C))
print(f'corr(log length, coverage n=6) = {r:.2f}; DN25 words {dn25["words"]}, corpus median words {st.median(x["words"] for x in rows.values())}')
json.dump(rows, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'p2_repetition_rows.json'), 'w'), indent=0)
