"""r02: known-answer controls for the paper's two tests (Kendall tau < 0, and L < L_r).

NULL-WITH-NO-COMPRESSION (random typing, Miller 1957): characters drawn i.i.d. from the language's own
character distribution (token-weighted, from its own file), word boundary with probability q after each
character, q = 1/L so the expected token length matches the language. No word is ever chosen for being
short; there is no lexicon and no optimisation. T tokens, matched to the language.
  -> If the tests detect "compression" here, they cannot discriminate compression from random typing.

NULL-WITH-NO-LINK (calibration): a lexicon whose type lengths are the language's own type lengths and
whose type probabilities are the language's own relative frequencies, paired at RANDOM, then T tokens
sampled from it (multinomial) and statistics computed on the observed types, as a corpus would be.
  -> The tests should fire at their nominal rate here (size check under finite sampling).

Per language: the observed gap ratio g = (L_r - L)/L_r and the random-typing distribution of g.
Usage: python -I r02_known_answer.py <repo_dir> <out_dir> [reps]
"""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402  (adds the user site, where numpy/scipy live, before they are imported)
import numpy as np
from common import read_pud, read_cv, summary
PUD = {'Arabic': 'ara_pud', 'Czech': 'ces_pud', 'German': 'deu_pud', 'English': 'eng_pud', 'Finnish': 'fin_pud',
       'French': 'fra_pud', 'Hindi': 'hin_pud', 'Indonesian': 'ind_pud', 'Icelandic': 'isl_pud', 'Italian': 'ita_pud',
       'Japanese': 'jpn_pud', 'Japanese-romaji': 'jpn_pud_romaji', 'Korean': 'kor_pud', 'Polish': 'pol_pud',
       'Portuguese': 'por_pud', 'Russian': 'rus_pud', 'Spanish': 'spa_pud', 'Swedish': 'swe_pud', 'Thai': 'tha_pud',
       'Turkish': 'tur_pud', 'Chinese': 'zho_pud', 'Chinese-pinyin': 'zho_pud_pinyin'}
cv_codes = {}
with open(os.path.join(sys.argv[1], 'data', 'filtered', 'descriptive_tables', 'common_voice.csv'), encoding='utf-8') as fh:
    for row in csv.DictReader(fh):
        cv_codes[row['language']] = row['iso_code']
TMAX = 1_000_000   # larger corpora are thinned to TMAX tokens (multivariate hypergeometric) before comparison

root, out = sys.argv[1], sys.argv[2]
REPS = int(sys.argv[3]) if len(sys.argv) > 3 else 20
rng = np.random.default_rng(20261023)


def char_dist(words, f):
    cnt = {}
    for w, k in zip(words, f):
        for ch in w:
            cnt[ch] = cnt.get(ch, 0) + k
    chars = sorted(cnt); p = np.array([cnt[c] for c in chars], float)
    return len(chars), p / p.sum()


def random_typing(T, L, pchar):
    q = 1.0 / L
    lens = rng.geometric(q, size=T)                     # >= 1
    chars = rng.choice(len(pchar), size=int(lens.sum()), p=pchar).astype(np.int32)
    # word identity = the character sequence; hash each word by a polynomial code on its slice
    ends = np.cumsum(lens); starts = ends - lens
    words = {}
    b = chars.tobytes()
    for s, e in zip(starts, ends):
        k = b[4 * s:4 * e]
        words[k] = words.get(k, 0) + 1
    f = np.fromiter(words.values(), float); l = np.array([len(k) // 4 for k in words], float)
    return f, l


def no_link(f, l, T):
    p = f / f.sum()
    lperm = rng.permutation(l)
    draw = rng.multinomial(T, p)
    keep = draw > 0
    return draw[keep].astype(float), lperm[keep]


def words_of(coll, code):
    path = os.path.join(root, 'data', 'filtered', 'corpora', coll,
                        code + ('.csv' if coll == 'pud' else '-word.csv'))
    ws = []
    with open(path, encoding='utf-8') as fh:
        rd = csv.reader(fh); h = next(rd); wi = h.index('word')
        for row in rd:
            if len(row) == len(h) + 1:
                row = row[1:]
            ws.append(row[wi])
    return ws


rows = []
for coll, names in (('pud', PUD), ('cv', cv_codes)):
    for lang, code in sorted(names.items()):
        if coll == 'pud' and ('strokes' in code):
            continue                                       # strokes are not characters; no typing model
        if coll == 'pud':
            f, l = read_pud(root, code)
        else:
            f, l = read_cv(root, code, 'n_characters')
        words = words_of(coll, code)
        thinned = False
        if f.sum() > TMAX:
            draw = rng.multivariate_hypergeometric(f.astype(np.int64), TMAX, method='marginals')
            keep = draw > 0
            f, l = draw[keep].astype(float), l[keep]
            words = [w for w, k in zip(words, keep) if k]
            thinned = True
        obs = summary(f, l)
        A, pchar = char_dist(words, f)
        T = int(f.sum())
        g_obs = (obs['Lr'] - obs['L']) / obs['Lr']
        rt, nl = [], []
        reps = REPS if T <= 200_000 else max(5, REPS // 4)
        for _ in range(reps):
            rf, rl = random_typing(T, obs['L'], pchar)
            s = summary(rf, rl)
            rt.append(((s['Lr'] - s['L']) / s['Lr'], s['tau'], s['tau_p'], s['L'], s['Lr']))
            nf, nl_ = no_link(f, l, T)
            s2 = summary(nf, nl_)
            nl.append(((s2['Lr'] - s2['L']) / s2['Lr'], s2['tau'], s2['tau_p']))
        rt = np.array(rt); nl = np.array(nl)
        rows.append(dict(collection=coll, language=lang, T=T, thinned=thinned, n=obs['n'], A=A, L=obs['L'], Lr=obs['Lr'],
                         g_obs=g_obs, tau_obs=obs['tau'],
                         rt_reps=reps, rt_g_mean=rt[:, 0].mean(), rt_g_min=rt[:, 0].min(), rt_g_max=rt[:, 0].max(),
                         rt_tau_mean=rt[:, 1].mean(), rt_share_tau_p01=(rt[:, 2] < 0.01).mean(),
                         rt_share_L_below_Lr=(rt[:, 3] < rt[:, 4]).mean(),
                         obs_g_minus_rt_mean=g_obs - rt[:, 0].mean(),
                         nl_g_mean=nl[:, 0].mean(), nl_tau_mean=nl[:, 1].mean(), nl_share_tau_p01=(nl[:, 2] < 0.01).mean()))
        r = rows[-1]
        print(f"{coll} {lang[:16]:16s} T={T:8d} A={A:4d}  g_obs={g_obs:.3f}  random typing g={r['rt_g_mean']:.3f} "
              f"[{r['rt_g_min']:.3f},{r['rt_g_max']:.3f}] tau={r['rt_tau_mean']:+.3f} p<.01 {r['rt_share_tau_p01']:.2f} "
              f"| no-link g={r['nl_g_mean']:+.3f} tau={r['nl_tau_mean']:+.3f} p<.01 {r['nl_share_tau_p01']:.2f}", flush=True)
with open(os.path.join(out, 'r02_known_answer.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
rt_fire = sum(r['rt_share_tau_p01'] == 1.0 and r['rt_share_L_below_Lr'] == 1.0 for r in rows)
beyond = sum(r['g_obs'] > r['rt_g_max'] for r in rows)
below = sum(r['g_obs'] < r['rt_g_min'] for r in rows)
print(f'\nrandom typing: both tests fire in every replicate for {rt_fire}/{len(rows)} files')
print(f'observed gap ratio above EVERY random-typing replicate: {beyond}/{len(rows)}; below every one: {below}/{len(rows)}')
nl_rate = np.mean([r['nl_share_tau_p01'] for r in rows])
print(f'no-link null: mean share of replicates with tau p < .01 = {nl_rate:.3f} (nominal 0.01)')
