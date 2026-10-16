"""Colour (zaslavsky2018) in the same weighting-free metric as x1: net Pareto dominance of each WCS language's mode map
over (a) random partitions and (b) random CONVEX (Voronoi in CIELAB) partitions with the same number of terms.
Axes: IB complexity I(M;W) (lower better) and accuracy I(W;U) (higher better), both in bits, released model.
Needs IBC = folder with pM_pUM.npz (extracted from the authors' model zip, sha256 eb25ae01...) and wcs/{term,chip,cnum-vhcm-lab-new}.txt"""
import os, json, random, statistics as st, numpy as np, pandas as pd
ROOT = os.environ.get('IBC', '.'); HERE = os.path.dirname(os.path.abspath(__file__))
Z = np.load(os.path.join(ROOT, 'pM_pUM.npz')); pM = Z['pM'].reshape(-1, 1); pU_M = Z['pU_M']
if os.environ.get('PRIOR') == 'uniform': pM = np.full((330, 1), 1 / 330)  # prior NOT estimated from the naming data
def xlogx(v):
    with np.errstate(divide='ignore', invalid='ignore'): return np.where(v > 1e-16, v * np.log2(v), 0)
def H(p): return -xlogx(p).sum()
def MI(p): return H(p.sum(0)) + H(p.sum(1)) - H(p)
def comp(q): return MI(q * pM)
def acc(q): return MI((q * pM).T @ pU_M)
term = pd.read_csv(os.path.join(ROOT, 'wcs', 'term.txt'), sep='\t', header=None, names=['lang', 'spk', 'cnum', 'term'])
term = term[term.term.astype(str).str.strip() != '*']
lab = pd.read_csv(os.path.join(ROOT, 'wcs', 'cnum-vhcm-lab-new.txt'), sep='\t').sort_values('#cnum')[['L*', 'a*', 'b*']].values
enc = {}; nresp = {}
for l, g in term.groupby('lang'):
    t = g.groupby(['cnum', 'term']).size().unstack(fill_value=0).reindex(range(1, 331), fill_value=0)
    nresp[l] = t.sum(1).values.min(); q = t.values + 0.0; enc[l] = q / np.maximum(q.sum(1, keepdims=True), 1)
keep = [l for l in sorted(enc) if nresp[l] >= 5]
def hard(lbl, K): q = np.zeros((330, K)); q[np.arange(330), lbl] = 1; return q
rng = np.random.default_rng(20261016); R = random.Random(1)
def net(pt, nulls):
    c, a = pt
    dom = np.mean([(c <= x and a >= y and (c < x or a > y)) for x, y in nulls]); sub = np.mean([(x <= c and y >= a and (x < c or y > a)) for x, y in nulls])
    return dom - sub
rows = []
for l in keep:
    modal = enc[l].argmax(1); used = np.unique(modal); K = len(used); qh = hard(np.searchsorted(used, modal), K)
    pt = (comp(qh), acc(qh))
    vor, rnd = [], []
    for _ in range(60):
        cen = lab[rng.choice(330, K, replace=False)]; lbl = ((lab[:, None, :] - cen[None, :, :]) ** 2).sum(-1).argmin(1)
        vor.append((comp(hard(lbl, K)), acc(hard(lbl, K))))
        while True:
            lbl2 = rng.integers(0, K, 330)
            if len(np.unique(lbl2)) == K: break
        rnd.append((comp(hard(lbl2, K)), acc(hard(lbl2, K))))
    rows.append((l, K, net(pt, rnd), net(pt, vor), pt[0], pt[1], np.mean([v[0] for v in vor]), np.mean([v[1] for v in vor])))
D = pd.DataFrame(rows, columns=['lang', 'K', 'net_vs_random', 'net_vs_convex', 'comp', 'acc', 'comp_convex_mean', 'acc_convex_mean'])
def boot(x): b = [np.mean(R.choices(list(x), k=len(x))) for _ in range(2000)]; return [round(float(np.mean(x)), 3), np.percentile(b, [2.5, 97.5]).round(3).tolist(), len(x)]
out = {'random partitions, same K': boot(D.net_vs_random), 'convex (Voronoi) partitions, same K': boot(D.net_vs_convex),
       'per-axis: mode map minus convex mean': {'complexity_bits': round(float((D.comp - D.comp_convex_mean).mean()), 3), 'accuracy_bits': round(float((D.acc - D.acc_convex_mean).mean()), 3)}}
print(json.dumps(out, indent=1))
suf = '_uniform' if os.environ.get('PRIOR') == 'uniform' else ''
D.to_csv(os.path.join(HERE, 'out', f'x2_colour_per_language{suf}.csv'), index=False)
json.dump(out, open(os.path.join(HERE, 'out', f'x2_colour_dominance{suf}.json'), 'w'), indent=1)
