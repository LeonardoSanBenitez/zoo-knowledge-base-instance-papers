"""Open question of this record: does a real text's I0(l) (mean self-information of word tokens of length l, from corpus
word frequencies) match random typing built from the SAME text's character statistics (letter frequencies, space
probability p0, l0 = 1)? Text: Moby-Dick (Gutenberg 2701), lowercased a-z words. Token-weighted means, as in the paper."""
import os, re, sys, collections, numpy as np
path = sys.argv[1]
s = open(path, encoding='utf-8', errors='ignore').read()
a = s.find('*** START'); b = s.find('*** END'); s = s[s.find('\n', a):b].lower()
words = re.findall(r'[a-z]+', s); N = len(words)
wf = collections.Counter(words)
# character statistics of the word stream with one space per word boundary
letters = collections.Counter(''.join(words)); n_let = sum(letters.values())
p0 = N / (N + n_let)                                    # probability of the space
P = np.array([p0] + [letters[c] / (N + n_let) for c in sorted(letters)])
H = -(P * np.log(P)).sum(); l0 = 1
slope_rt = (H + p0 * np.log(p0)) / (1 - p0); icpt_rt = np.log((1 - p0) ** l0 / p0)
rows = []
for L in range(1, 15):
    toks = [w for w in words if len(w) == L]
    if len(toks) < 200: continue
    I = np.mean([-np.log(wf[w] / N) for w in toks]); rows.append((L, I, len(toks)))
Ls = np.array([r[0] for r in rows]); Is = np.array([r[1] for r in rows])
sl, ic = np.polyfit(Ls, Is, 1); r2 = np.corrcoef(Ls, Is)[0, 1] ** 2
print(f'tokens {N}, types {len(wf)}, p0 {p0:.3f}, char entropy {H:.3f} nats')
for L, I, n in rows: print(f'  l={L:2d}  real I0 {I:6.2f}   random-typing I0 {slope_rt*L+icpt_rt:6.2f}   (n tokens {n})')
print(f'real text: slope {sl:.3f} intercept {ic:.3f} R2 {r2:.3f} | random typing with same character statistics: slope {slope_rt:.3f} intercept {icpt_rt:.3f}')
print(f'ratio real/random slope: {sl/slope_rt:.3f}')
