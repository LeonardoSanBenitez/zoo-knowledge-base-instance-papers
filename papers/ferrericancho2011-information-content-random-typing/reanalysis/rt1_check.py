"""Check Ferrer-i-Cancho & Moscoso del Prado's closed form I0(l) = a*l + b for generalized random typing by simulation.
Alphabet: space (p0) + 26 letters with Zipf-like unequal probabilities; minimum word length l0. For each simulated word,
-ln p(w) is computed EXACTLY from eq. (7); the per-length mean is compared with a*l + b."""
import numpy as np
rng = np.random.default_rng(0)
lam = 27; p0 = 0.18; l0 = 1
w = 1 / np.arange(1, lam) ** 0.9; w = w / w.sum() * (1 - p0)       # letter probabilities after the prefix
P = np.concatenate([[p0], w])                                       # index 0 = space
H = -(P * np.log(P)).sum()
a = (H + p0 * np.log(p0)) / (1 - p0); b = np.log((1 - p0) ** l0 / p0)
def word():
    s = []
    while True:
        if len(s) < l0: c = rng.choice(np.arange(1, lam), p=w / w.sum())
        else: c = rng.choice(lam, p=P)
        if c == 0: return s
        s.append(c)
by = {}
for _ in range(200000):
    s = word(); L = len(s)
    lp = np.log(p0) - l0 * np.log(1 - p0) + sum(np.log(P[c]) for c in s)   # eq. (7)
    by.setdefault(L, []).append(-lp)
print(f'a = {a:.4f}, b = {b:.4f}')
for L in range(1, 9):
    v = np.array(by.get(L, [np.nan])); print(f'l={L}: simulated I0 {v.mean():.4f} (n={len(v)})  closed form {a*L+b:.4f}  diff {v.mean()-(a*L+b):+.4f}')
Ls = np.array([L for L in by if len(by[L]) > 200]); m = np.array([np.mean(by[L]) for L in Ls])
print('OLS on simulated means: slope %.4f intercept %.4f R2 %.6f' % (*np.polyfit(Ls, m, 1), np.corrcoef(Ls, m)[0, 1] ** 2))
