"""Recover Goldberg et al. (2022) Figure 1 bar heights from the PDF's vector paths; calibrate on the reported totals."""
import fitz, json, os, sys
pdf = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'goldberg2021.pdf')
p = [pg for pg in fitz.open(pdf) if 'Figure 1.' in pg.get_text()][0]
COL = {(1.0, 0.47, 0.43): 'any_mrae_single_item', (0.64, 0.65, 0.0): 'mraes_1plus', (0.0, 0.75, 0.48): 'any_impairment',
       (0.0, 0.7, 0.98): 'impairment_gt_1day', (1.0, 0.42, 0.97): 'impairment_ge_1month'}
bars = []
for x in p.get_drawings():
    f = x.get('fill'); r = x['rect']
    if f is None: continue
    k = tuple(round(c, 2) for c in f)
    if k in COL and r.y1 > 227 and r.y1 < 228 and r.x0 < 440: bars.append((r.x0, COL[k], 227.2 - r.y0))
groups = sorted(set(round(b[0] - 8.4 * list(COL.values()).index(b[1]), 0) for b in bars))
# cluster by group start: bars of a group are contiguous; group starts are the red bars
starts = sorted(b[0] for b in bars if b[1] == 'any_mrae_single_item')
labels = ['Total', '0-10', '11-100', '101-500', '501-1000', '1001-5000', '5001+']  # ASSUMED order, checked below
scale = [b[2] for b in bars if b[1] == 'any_mrae_single_item' and abs(b[0] - starts[0]) < 1][0] / 32.26  # px per percentage point
out = {}
for i, s in enumerate(starts):
    nxt = starts[i + 1] if i + 1 < len(starts) else 1e9
    g = {name: 0.0 for name in COL.values()}
    for b in bars:
        if s - 0.5 <= b[0] < nxt - 0.5: g[b[1]] = round(b[2] / scale, 1)
    out[labels[i]] = g
print(json.dumps(out, indent=1))
# axis labels near the y axis, to check the scale independently
ticks = [(round(w[1], 1), w[4]) for w in p.get_text('words') if w[0] < 100 and 40 < w[1] < 240]
print('y-axis words (y, text):', ticks)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figure1_bars.json'), 'w'), indent=1)
