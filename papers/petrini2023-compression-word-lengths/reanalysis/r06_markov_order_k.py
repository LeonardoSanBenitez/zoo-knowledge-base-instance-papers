"""r06: how far up the Markov ladder before typing reproduces the lexicon -- and with it the lexicon's
'compression'? Order-k character typing (context = previous k characters, START-padded, END a symbol),
fitted per language on its own tokens, k = 1, 2, 3. For each k: observed gap ratio above / below every
replicate, and the share of generated TOKENS that are real word types of the language (how much of the
lexicon the null has started to copy).
Prediction written before running (2026-10-23): the above-count rises with k toward the observed
(the null converges on the real lexicon), and the real-type share passes 50% by k = 3 in most files;
the k at which the verdict flips is the order at which 'the null contains the lexicon'.
PUD files only (small, 20 files): this is a ladder, not a census.
Usage: python -I r06_markov_order_k.py <repo_dir> <out_dir> [reps=5]
"""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: F401
import numpy as np
from common import read_pud, summary

root, out = sys.argv[1], sys.argv[2]
REPS = int(sys.argv[3]) if len(sys.argv) > 3 else 5
rng = np.random.default_rng(20261023)
PUD = {'Arabic': 'ara_pud', 'Czech': 'ces_pud', 'German': 'deu_pud', 'English': 'eng_pud', 'Finnish': 'fin_pud',
       'French': 'fra_pud', 'Hindi': 'hin_pud', 'Indonesian': 'ind_pud', 'Icelandic': 'isl_pud', 'Italian': 'ita_pud',
       'Japanese': 'jpn_pud', 'Korean': 'kor_pud', 'Polish': 'pol_pud', 'Portuguese': 'por_pud', 'Russian': 'rus_pud',
       'Spanish': 'spa_pud', 'Swedish': 'swe_pud', 'Thai': 'tha_pud', 'Turkish': 'tur_pud', 'Chinese': 'zho_pud'}
START, END = '\x02', '\x03'


def words_of(code):
    ws = []
    with open(os.path.join(root, 'data', 'filtered', 'corpora', 'pud', code + '.csv'), encoding='utf-8') as fh:
        for row in csv.DictReader(fh):
            ws.append(row['word'])
    return ws


def fit(words, f, k):
    t = {}
    for w, c in zip(words, f):
        s = START * k + w + END
        for i in range(k, len(s)):
            ctx = s[i - k:i]; d = t.setdefault(ctx, {}); d[s[i]] = d.get(s[i], 0) + c
    model = {}
    for ctx, d in t.items():
        sy = list(d.keys()); p = np.array(list(d.values()), float)
        model[ctx] = (sy, np.cumsum(p) / p.sum())
    return model


def generate(T, model, k, maxlen=60):
    counts = {}
    u = rng.random((T, maxlen + 1))
    for i in range(T):
        ctx = START * k; w = []
        for j in range(maxlen):
            sy, c = model[ctx]
            ch = sy[min(int(np.searchsorted(c, u[i, j])), len(sy) - 1)]
            if ch == END:
                break
            w.append(ch); ctx = (ctx + ch)[-k:]
        w = ''.join(w) or 'x'
        counts[w] = counts.get(w, 0) + 1
    return counts


rows = []
for lang, code in sorted(PUD.items()):
    f, l = read_pud(root, code)
    words = words_of(code)
    obs = summary(f, l, with_tests=False)
    g_obs = (obs['Lr'] - obs['L']) / obs['Lr']
    real = set(words); T = int(f.sum())
    line = f'{lang[:12]:12s} g_obs {g_obs:.3f}'
    for k in (1, 2, 3):
        model = fit(words, f, k)
        gs, share = [], []
        for _ in range(REPS):
            cnt = generate(T, model, k)
            ff = np.fromiter(cnt.values(), float); ll = np.array([len(w) for w in cnt], float)
            s = summary(ff, ll, with_tests=False)
            gs.append((s['Lr'] - s['L']) / s['Lr'])
            share.append(sum(v for w, v in cnt.items() if w in real) / T)
        gs = np.array(gs)
        side = 'ABOVE' if g_obs > gs.max() else 'below' if g_obs < gs.min() else 'within'
        rows.append(dict(language=lang, k=k, g_obs=g_obs, g_mean=gs.mean(), g_min=gs.min(), g_max=gs.max(),
                         side=side, real_token_share=float(np.mean(share))))
        line += f' | k={k}: g {gs.mean():.3f} {side:6s} real {np.mean(share):.2f}'
    print(line, flush=True)
with open(os.path.join(out, 'r06_markov_order_k.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
for k in (1, 2, 3):
    rk = [r for r in rows if r['k'] == k]
    print(f'k={k}: above {sum(r["side"] == "ABOVE" for r in rk)}, below {sum(r["side"] == "below" for r in rk)}, '
          f'within {sum(r["side"] == "within" for r in rk)} of {len(rk)}; median real-token share '
          f'{np.median([r["real_token_share"] for r in rk]):.2f}')
