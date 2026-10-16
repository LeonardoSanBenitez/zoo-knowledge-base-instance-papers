"""Chaabouni et al. 2021 judge emergent NN colour systems 'efficient like humans' because their Inef (Euclidean distance
to the IB curve, beta >= 1) falls within the human (WCS) range. Does a random CONVEX partition of CIELAB -- no learning,
no communication -- also fall within the human range? Uses the released IB model (pM, pU_M, IB_curve; sha256 eb25ae01 zip)."""
import os, json, numpy as np, pandas as pd
ROOT = os.environ.get('IBC', '.'); HERE = os.path.dirname(os.path.abspath(__file__))
Z = np.load(os.path.join(ROOT, 'pM_pUM.npz')); pM = Z['pM'].reshape(-1, 1); pU_M = Z['pU_M']; curve = Z['IB_curve']; betas = Z['betas']
cx, cy = curve[0][betas >= 1], curve[1][betas >= 1]
def xlogx(v):
    with np.errstate(divide='ignore', invalid='ignore'): return np.where(v > 1e-16, v * np.log2(v), 0)
def MI(p): return -xlogx(p.sum(0)).sum() - xlogx(p.sum(1)).sum() + xlogx(p).sum()
def comp(q): return MI(q * pM)
def acc(q): return MI((q * pM).T @ pU_M)
def inef(q): c, a = comp(q), acc(q); return float(np.min(np.hypot(cx - c, cy - a))), c, a
term = pd.read_csv(os.path.join(ROOT, 'wcs', 'term.txt'), sep='\t', header=None, names=['lang', 'spk', 'cnum', 'term'])
term = term[term.term.astype(str).str.strip() != '*']
lab = pd.read_csv(os.path.join(ROOT, 'wcs', 'cnum-vhcm-lab-new.txt'), sep='\t').sort_values('#cnum')[['L*', 'a*', 'b*']].values
enc = {}; nresp = {}
for l, g in term.groupby('lang'):
    t = g.groupby(['cnum', 'term']).size().unstack(fill_value=0).reindex(range(1, 331), fill_value=0)
    nresp[l] = t.sum(1).values.min(); q = t.values + 0.0; enc[l] = q / np.maximum(q.sum(1, keepdims=True), 1)
keep = [l for l in sorted(enc) if nresp[l] >= 5]
def hard(lbl, K): q = np.zeros((330, K)); q[np.arange(330), lbl] = 1; return q
H = [inef(enc[l]) for l in keep]; hi = np.array([h[0] for h in H]); hc = np.array([h[1] for h in H])
Ks = [len(np.unique(enc[l].argmax(1))) for l in keep]
rng = np.random.default_rng(7); V, R = [], []
for _ in range(600):
    K = int(rng.choice(Ks)); cen = lab[rng.choice(330, K, replace=False)]
    V.append(inef(hard(((lab[:, None, :] - cen[None]) ** 2).sum(-1).argmin(1), K)))
    while True:
        l2 = rng.integers(0, K, 330)
        if len(np.unique(l2)) == K: break
    R.append(inef(hard(l2, K)))
vi = np.array([v[0] for v in V]); vc = np.array([v[1] for v in V]); ri = np.array([r[0] for r in R])
lo, hi_ = hi.min(), hi.max()
out = {'human_WCS_soft': {'n': len(hi), 'inef_median': round(float(np.median(hi)), 3), 'inef_range': [round(float(lo), 3), round(float(hi_), 3)], 'complexity_range_bits': [round(float(hc.min()), 2), round(float(hc.max()), 2)]},
       'random_convex_voronoi': {'n': len(vi), 'inef_median': round(float(np.median(vi)), 3), 'share_within_human_range': round(float(np.mean((vi >= lo) & (vi <= hi_))), 3), 'share_below_human_max': round(float(np.mean(vi <= hi_)), 3), 'complexity_range_bits': [round(float(vc.min()), 2), round(float(vc.max()), 2)]},
       'random_partition': {'n': len(ri), 'inef_median': round(float(np.median(ri)), 3), 'share_below_human_max': round(float(np.mean(ri <= hi_)), 3)}}
print(json.dumps(out, indent=1)); json.dump(out, open(os.path.join(HERE, 'out', 'x4_inef_convex.json'), 'w'), indent=1)
