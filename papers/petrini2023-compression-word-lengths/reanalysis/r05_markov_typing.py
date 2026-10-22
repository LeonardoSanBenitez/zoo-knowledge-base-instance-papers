"""r05: a stronger structural null -- character-bigram ('Markov') typing.

Per language, transition probabilities START->c, c->c', c->END are estimated from the language's own
tokens (token-weighted). T words are generated from that chain. It keeps the phonotactics and the
word-length distribution approximately, and still optimises nothing: no word is chosen for being short.
(A higher-order model would start to reproduce the lexicon itself, and with it whatever compression the
lexicon has; bigram is the mildest step up from i.i.d. typing.)

Question: is the observed gap ratio g = (L_r - L)/L_r above or below this null, and does the
30-above / 32-below split of r02 survive?
Corpora above 1e6 tokens are thinned to 1e6 (same seed scheme as r02). 10 replicates per file
(4 above 2e5 tokens). Romanised PUD files excluded (word column not in the romanisation).
Usage: python -I r05_markov_typing.py <repo_dir> <out_dir> [reps]
"""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: F401
import numpy as np
from common import read_pud, read_cv, summary

root, out = sys.argv[1], sys.argv[2]
REPS = int(sys.argv[3]) if len(sys.argv) > 3 else 10
rng = np.random.default_rng(20261023)
TMAX = 1_000_000
PUD = {'Arabic': 'ara_pud', 'Czech': 'ces_pud', 'German': 'deu_pud', 'English': 'eng_pud', 'Finnish': 'fin_pud',
       'French': 'fra_pud', 'Hindi': 'hin_pud', 'Indonesian': 'ind_pud', 'Icelandic': 'isl_pud', 'Italian': 'ita_pud',
       'Japanese': 'jpn_pud', 'Korean': 'kor_pud', 'Polish': 'pol_pud', 'Portuguese': 'por_pud', 'Russian': 'rus_pud',
       'Spanish': 'spa_pud', 'Swedish': 'swe_pud', 'Thai': 'tha_pud', 'Turkish': 'tur_pud', 'Chinese': 'zho_pud'}
cv_codes = {}
with open(os.path.join(root, 'data', 'filtered', 'descriptive_tables', 'common_voice.csv'), encoding='utf-8') as fh:
    for row in csv.DictReader(fh):
        cv_codes[row['language']] = row['iso_code']


def words_of(coll, code):
    path = os.path.join(root, 'data', 'filtered', 'corpora', coll, code + ('.csv' if coll == 'pud' else '-word.csv'))
    ws = []
    with open(path, encoding='utf-8') as fh:
        rd = csv.reader(fh); h = next(rd); wi = h.index('word')
        for row in rd:
            if len(row) == len(h) + 1:
                row = row[1:]
            ws.append(row[wi])
    return ws


def fit_chain(words, f):
    chars = sorted({c for w in words for c in w})
    idx = {c: i + 1 for i, c in enumerate(chars)}        # 0 = START (as a source) and END (as a target)
    K = len(chars) + 1
    trans = {}
    for w, k in zip(words, f):
        prev = 0
        for c in w:
            j = idx[c]; d = trans.setdefault(prev, {}); d[j] = d.get(j, 0) + k; prev = j
        d = trans.setdefault(prev, {}); d[0] = d.get(0, 0) + k
    cdf = {}
    for s, d in trans.items():
        tg = np.fromiter(d.keys(), int); w_ = np.fromiter(d.values(), float)
        cdf[s] = (tg, np.cumsum(w_) / w_.sum())
    return cdf


def markov_words(T, cdf, maxlen=60):
    state = np.zeros(T, int); active = np.ones(T, bool)
    seqs = np.zeros((T, maxlen), np.int32); lens = np.zeros(T, int)
    for step in range(maxlen):
        if not active.any():
            break
        nxt = np.zeros(T, int)
        for s in np.unique(state[active]):
            m = active & (state == s)
            tg, c = cdf[s]
            nxt[m] = tg[np.minimum(np.searchsorted(c, rng.random(m.sum())), len(tg) - 1)]
        ended = active & (nxt == 0) & (step > 0)
        # a word must have >= 1 character: if START->END were drawn it cannot be, START never emits END
        cont = active & ~ended
        seqs[cont, step] = nxt[cont]; lens[cont] += 1
        state[cont] = nxt[cont]; active = cont
    lens = np.maximum(lens, 1)
    keys = {}
    for i in range(T):
        k = seqs[i, :lens[i]].tobytes(); keys[k] = keys.get(k, 0) + 1
    f = np.fromiter(keys.values(), float); l = np.array([len(k) // 4 for k in keys], float)
    return f, l


rows = []
for coll, names in (('pud', PUD), ('cv', cv_codes)):
    for lang, code in sorted(names.items()):
        f, l = read_pud(root, code) if coll == 'pud' else read_cv(root, code, 'n_characters')
        words = words_of(coll, code)
        if f.sum() > TMAX:
            d = rng.multivariate_hypergeometric(f.astype(np.int64), TMAX, method='marginals'); k = d > 0
            f, l = d[k].astype(float), l[k]; words = [w for w, kk in zip(words, k) if kk]
        obs = summary(f, l)
        g_obs = (obs['Lr'] - obs['L']) / obs['Lr']
        cdf = fit_chain(words, f)
        T = int(f.sum())
        reps = REPS if T <= 200_000 else max(4, REPS // 3)
        g, taus, Ls = [], [], []
        for _ in range(reps):
            mf, ml = markov_words(T, cdf)
            s = summary(mf, ml)
            g.append((s['Lr'] - s['L']) / s['Lr']); taus.append(s['tau']); Ls.append(s['L'])
        g = np.array(g)
        rows.append(dict(collection=coll, language=lang, T=T, L=obs['L'], Lr=obs['Lr'], g_obs=g_obs, tau_obs=obs['tau'],
                         mk_reps=reps, mk_L_mean=float(np.mean(Ls)), mk_g_mean=float(g.mean()), mk_g_min=float(g.min()),
                         mk_g_max=float(g.max()), mk_tau_mean=float(np.mean(taus))))
        r = rows[-1]
        side = 'ABOVE' if g_obs > r['mk_g_max'] else 'below' if g_obs < r['mk_g_min'] else 'within'
        print(f"{coll} {lang[:16]:16s} T={T:8d} L={obs['L']:.2f} (markov {r['mk_L_mean']:.2f})  g_obs={g_obs:.3f}  "
              f"markov g={r['mk_g_mean']:.3f} [{r['mk_g_min']:.3f},{r['mk_g_max']:.3f}] tau {obs['tau']:+.3f} vs "
              f"{r['mk_tau_mean']:+.3f}  {side}", flush=True)
with open(os.path.join(out, 'r05_markov_typing.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
above = sum(r['g_obs'] > r['mk_g_max'] for r in rows); below = sum(r['g_obs'] < r['mk_g_min'] for r in rows)
tau_stronger = sum(r['tau_obs'] < r['mk_tau_mean'] for r in rows)
print(f'\n{len(rows)} files: observed gap ratio above every Markov-typing replicate {above}, below every one {below}, '
      f'within {len(rows) - above - below}. Observed tau more negative than Markov mean: {tau_stronger}/{len(rows)}')
