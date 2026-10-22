"""r03: (A) is the gap L_r - L a property of the language or of the corpus size?
          (B) is the larger gap in duration than in characters lexical, or reduction in speech?

(A) For the largest CV corpora, draw T' tokens without replacement (multivariate hypergeometric) at
    T' = 1e3 ... 1e6 and full, 5 replicates; report n, L, L_r, g = (L_r - L)/L_r, tau, r.
    Same for random typing calibrated to English CV (L, character distribution) at each T'.
    Prediction if g measures compression of the LEXICON: g roughly stable in T'.
    Prediction if g is driven by the type count (rare long types accumulate): g rises with T'.
(B) Per CV language: OLS of log median duration on log length-in-characters and log frequency,
    over types. A negative frequency coefficient at fixed character length means frequent words are
    spoken faster per character -- reduction in speech production, which inflates the duration gap
    beyond any property of the word forms.
Usage: python -I r03_sample_size_and_duration.py <repo_dir> <out_dir>
"""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: F401  (user site for numpy/scipy)
import numpy as np
from common import read_cv, summary

root, out = sys.argv[1], sys.argv[2]
rng = np.random.default_rng(20261023)
codes = {}
with open(os.path.join(root, 'data', 'filtered', 'descriptive_tables', 'common_voice.csv'), encoding='utf-8') as fh:
    for row in csv.DictReader(fh):
        codes[row['iso_code']] = row['language']

rows = []
print('(A) gap ratio g vs corpus size T (mean of 5 draws)')
for code in ('eng', 'deu', 'fra', 'cat', 'kin', 'spa'):
    f, l = read_cv(root, code, 'n_characters')
    T = int(f.sum())
    line = []
    for Tp in (1_000, 10_000, 100_000, 1_000_000, T):
        if Tp > T:
            continue
        gs, taus, rs, ns = [], [], [], []
        for _ in range(5 if Tp < T else 1):
            d = rng.multivariate_hypergeometric(f.astype(np.int64), Tp, method='marginals') if Tp < T else f
            k = d > 0
            s = summary(d[k].astype(float), l[k])
            gs.append((s['Lr'] - s['L']) / s['Lr']); taus.append(s['tau']); rs.append(s['r']); ns.append(s['n'])
            rows.append(dict(part='A', source='corpus', language=codes[code], T=Tp, n=s['n'], L=s['L'], Lr=s['Lr'],
                             g=gs[-1], tau=s['tau'], r=s['r']))
        line.append(f'T={Tp:>8d}: n={np.mean(ns):8.0f} g={np.mean(gs):.3f} tau={np.mean(taus):+.3f} r={np.mean(rs):+.3f}')
    print(f'  {codes[code]:10s} ' + '\n             '.join(line))

# random typing calibrated to English CV
words = []
with open(os.path.join(root, 'data', 'filtered', 'corpora', 'cv', 'eng-word.csv'), encoding='utf-8') as fh:
    rd = csv.reader(fh); h = next(rd); wi, fi = h.index('word'), h.index('frequency')
    for row in rd:
        words.append((row[wi], int(row[fi])))
cnt = {}
for w, k in words:
    for ch in w:
        cnt[ch] = cnt.get(ch, 0) + k
pchar = np.array(list(cnt.values()), float); pchar /= pchar.sum()
fE, lE = read_cv(root, 'eng', 'n_characters')
LE = float((fE * lE).sum() / fE.sum())
print('  random typing calibrated to English CV (L = %.2f, A = %d):' % (LE, len(pchar)))
for Tp in (1_000, 10_000, 100_000, 1_000_000):
    gs, taus = [], []
    for _ in range(5 if Tp < 1_000_000 else 2):
        lens = rng.geometric(1 / LE, size=Tp)
        chars = rng.choice(len(pchar), size=int(lens.sum()), p=pchar).astype(np.int32)
        b = chars.tobytes(); ends = np.cumsum(lens); starts = ends - lens
        wd = {}
        for s_, e_ in zip(starts, ends):
            kk = b[4 * s_:4 * e_]; wd[kk] = wd.get(kk, 0) + 1
        ff = np.fromiter(wd.values(), float); ll = np.array([len(x) // 4 for x in wd], float)
        s = summary(ff, ll)
        gs.append((s['Lr'] - s['L']) / s['Lr']); taus.append(s['tau'])
        rows.append(dict(part='A', source='random-typing', language='English-calibrated', T=Tp, n=s['n'], L=s['L'],
                         Lr=s['Lr'], g=gs[-1], tau=s['tau'], r=s['r']))
    print(f'             T={Tp:>8d}: g={np.mean(gs):.3f} tau={np.mean(taus):+.3f}')

print('\n(B) log median duration ~ log n_characters + log frequency, over types (OLS)')
neg = 0; tot = 0; coefs = []
for code, lang in sorted(codes.items(), key=lambda kv: kv[1]):
    path = os.path.join(root, 'data', 'filtered', 'corpora', 'cv', code + '-word.csv')
    F, C, D = [], [], []
    with open(path, encoding='utf-8') as fh:
        rd = csv.reader(fh); h = next(rd)
        fi, ci, di = h.index('frequency'), h.index('n_characters'), h.index('medianDuration')
        for row in rd:
            if len(row) == len(h) + 1:
                row = row[1:]
            if row[di] in ('NA', '') or float(row[di]) <= 0:
                continue
            F.append(float(row[fi])); C.append(float(row[ci])); D.append(float(row[di]))
    F, C, D = np.array(F), np.array(C), np.array(D)
    if len(F) < 50:
        continue
    X = np.column_stack([np.ones_like(F), np.log(C), np.log(F)])
    beta, *_ = np.linalg.lstsq(X, np.log(D), rcond=None)
    resid = np.log(D) - X @ beta
    se = np.sqrt(np.diag(np.linalg.inv(X.T @ X)) * resid.var(ddof=3))
    tot += 1; neg += beta[2] < 0
    coefs.append(beta[2])
    rows.append(dict(part='B', source='corpus', language=lang, T=int(F.sum()), n=len(F), L='', Lr='',
                     g='', tau='', r='', b_logchar=beta[1], b_logfreq=beta[2], se_logfreq=se[2]))
print(f'  frequency coefficient negative in {neg}/{tot} languages (types >= 50); median {np.median(coefs):+.4f}, '
      f'range {min(coefs):+.4f} to {max(coefs):+.4f}. Interpretation: duration ratio per e-fold of frequency.')
with open(os.path.join(out, 'r03_sample_size_and_duration.csv'), 'w', newline='', encoding='utf-8') as fh:
    keys = sorted({k for r in rows for k in r}, key=lambda k: list(rows[-1].keys()).index(k) if k in rows[-1] else 99)
    w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)
