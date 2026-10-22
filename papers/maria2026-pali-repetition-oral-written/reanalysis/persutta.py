"""EXPLORATORY (added after the pre-registered run; see PLAN.md Deviations).
(1) Calibration: R8 within DN 25 (Udumbarika, div id dn3_2) against Allon's ~30% verbatim repetition.
(2) Paired, length-matched, within-text comparison: each sutta (div type="sutta"; for MN, which this
    edition divides only by vagga, each vagga of ten suttas) vs its own commentary and
    sub-commentary (same div id), all three truncated to the shortest of the three (>= 1,000 tokens), R8
    within each. Wilcoxon signed-rank across suttas. Removes cross-sutta stock passages and holds topic fixed.
Usage: python -I persutta.py <text_dir> <out_dir>
"""
import csv, json, os, re, site, sys
sys.path.append(site.getusersitepackages())
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy import stats
from repetition import BOOKS, LAYERS, coverage


def suttas(path):
    raw = open(path, 'rb').read().decode('utf-16')
    raw = re.sub(r'<note\b.*?</note>', ' ', raw, flags=re.S | re.I)
    unit = 'sutta' if 'type="sutta"' in raw else 'vagga'      # MN in this edition is divided only by vagga
    parts = re.split(r'(<div[^>]*type="' + unit + r'"[^>]*>)', raw)
    out = {}
    for i in range(1, len(parts), 2):
        sid = re.search(r'id="([^"]+)"', parts[i]).group(1)
        body = re.sub(r'<[^>]+>', ' ', parts[i + 1])
        toks = [w for w in re.findall(r'[^\W\d_]+', body.lower()) if w != 'pe']
        out[sid] = out.get(sid, []) + toks
    return out


src, out = sys.argv[1], sys.argv[2]
rows = []
for nik, books in BOOKS.items():
    for b in books:
        L = {layer: suttas(os.path.join(src, f'{b}{suf}.xml')) for layer, suf in LAYERS.items()}
        for sid in L['mula']:
            if not all(sid in L[x] for x in LAYERS):
                continue
            n = min(len(L[x][sid]) for x in LAYERS)
            if n < 1000:
                continue
            r = {x: coverage(L[x][sid][:n], 8) for x in LAYERS}
            rows.append(dict(nikaya=nik, sutta=sid, matched_len=n, full_mula_len=len(L['mula'][sid]), **r))
            if sid == 'dn3_2':
                full = coverage(L['mula'][sid], 8)
                print(f'DN 25 (dn3_2) full text: {len(L["mula"][sid])} tokens, R8 = {full:.3f} (Allon: ~30% verbatim, ~35% more with variation)')
with open(os.path.join(out, 'persutta.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
res = {'n_pairs': len(rows)}
for nik in ('DN', 'MN', 'all'):
    rr = [r for r in rows if nik == 'all' or r['nikaya'] == nik]
    m = np.array([r['mula'] for r in rr]); a = np.array([r['atthakatha'] for r in rr]); t = np.array([r['tika'] for r in rr])
    w1 = stats.wilcoxon(m, a, alternative='greater'); w2 = stats.wilcoxon(a, t, alternative='greater')
    res[nik] = {'n': len(rr), 'median_matched_len': float(np.median([r['matched_len'] for r in rr])),
                'median_R8': [float(np.median(m)), float(np.median(a)), float(np.median(t))],
                'share_mula_gt_att': float(np.mean(m > a)), 'share_att_gt_tika': float(np.mean(a > t)),
                'p_mula_gt_att': float(w1.pvalue), 'p_att_gt_tika': float(w2.pvalue)}
    print(f'{nik}: {len(rr)} suttas, median matched length {res[nik]["median_matched_len"]:.0f}; median R8 mula {np.median(m):.3f} '
          f'att {np.median(a):.3f} tika {np.median(t):.3f}; mula > att in {100 * np.mean(m > a):.0f}% (p {w1.pvalue:.1g}); '
          f'att > tika in {100 * np.mean(a > t):.0f}% (p {w2.pvalue:.2g})')
json.dump(res, open(os.path.join(out, 'persutta_out.json'), 'w'), indent=1)
