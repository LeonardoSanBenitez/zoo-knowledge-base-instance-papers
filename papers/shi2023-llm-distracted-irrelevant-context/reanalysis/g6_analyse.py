"""g6 -- analysis of re/g3_results.jsonl exactly as fixed in re/PLAN.md (Q1-Q5). Only bases with all five conditions
(B, N, V1-V3) complete enter Q2-Q5. Bootstrap over bases, 10,000 resamples, seed 11. Author: maria 2026-10-17."""
import json, sys, collections, numpy as np
if len(sys.argv) < 2: sys.exit('usage: g6_analyse.py <results.jsonl>  (no default: see CONTRIBUTING, interim looks)')
f = sys.argv[1]
R = [json.loads(l) for l in open(f, encoding='utf-8')]
by = collections.defaultdict(dict)
for r in R: by[r['unit']][r['cond']] = r
bases = {u: c for u, c in by.items() if u.startswith('b') and all(k in c for k in ('B', 'N', 'V1', 'V2', 'V3'))}
dev = [c['B']['ok'] for u, c in by.items() if u.startswith('d') and 'B' in c]
rng = np.random.default_rng(11)
def boot(fn, units, B=10000):
    units = list(units); est = fn(units); idx = rng.integers(0, len(units), (B, len(units)))
    bs = np.array([fn([units[i] for i in row]) for row in idx]); return est, np.percentile(bs, [2.5, 97.5])
accB = np.mean([c['B']['ok'] for c in bases.values()]) if bases else float('nan')
print(f"complete bases {len(bases)}/100; dev problems {len(dev)}/200")
if dev:
    d = accB - np.mean(dev)
    print(f"Q1 selection: acc_B(bases) {accB:.3f} - acc_B(dev) {np.mean(dev):.3f} = {d:+.3f}  (n_bases {len(bases)}, n_dev {len(dev)})")
S = [c for c in bases.values() if c['B']['ok']]
print(f"S = bases this model solves: {len(S)}/{len(bases)}")
microV = lambda U: np.mean([np.mean([c[v]['ok'] for v in ('V1', 'V2', 'V3')]) for c in U])
accN = lambda U: np.mean([c['N']['ok'] for c in U])
if S:
    e, ci = boot(lambda U: 1 - microV(U), S); print(f"Q2 paper-style drop on S: 1 - micro_V = {e:.3f}  95% CI [{ci[0]:.3f}, {ci[1]:.3f}]")
    e, ci = boot(lambda U: 1 - accN(U), S); print(f"Q3 neutral drop on S:     1 - acc_N  = {e:.3f}  95% CI [{ci[0]:.3f}, {ci[1]:.3f}]")
    e, ci = boot(lambda U: accN(U) - microV(U), S); print(f"Q4 content-specific:  acc_N - micro_V = {e:+.3f}  95% CI [{ci[0]:+.3f}, {ci[1]:+.3f}]")
    mac = np.mean([all(c[v]['ok'] for v in ('V1', 'V2', 'V3')) for c in S]); mv = microV(S)
    print(f"Q5 macro at m=3 on S: {mac:.3f} (independence would give micro^3 = {mv**3:.3f})")
    # secondary, exploratory: by sentence type and by question-edited bases
    tv = collections.defaultdict(list)
    for c in S:
        for v in ('V1', 'V2', 'V3'): tv[c[v].get('sentence_label')].append(c[v]['ok'])
    print("   exploratory micro_V by topic:", {k: (round(np.mean(x), 3), len(x)) for k, x in tv.items()})
    # exploratory: bases whose GSM-IC variants also rewrite the question (g5) vs pure insertion
    import re as _re, os as _os
    if _os.path.exists('GSM-IC_2step.json'):
        A = json.load(open('GSM-IC_2step.json', encoding='utf-8')) + json.load(open('GSM-IC_mstep.json', encoding='utf-8'))
        ws = lambda s: ' '.join(s.split()); edited = set()
        for x in A:
            so = _re.split(r'(?<=[.!?])\s+', ws(x['original_question'])); sn = _re.split(r'(?<=[.!?])\s+', ws(x['new_question']))
            if not (len(sn) == len(so) + 1 and any(sn[:i] + sn[i + 1:] == so for i in range(len(sn)))): edited.add(ws(x['original_question']))
        grp = {True: [], False: []}
        for c in S: grp[ws(c['B'].get('q', '')) in edited].append(c)
        for k, U in grp.items():
            if U: print(f"   exploratory, question-edited bases={k}: n {len(U)}, acc_N {accN(U):.3f}, micro_V {microV(U):.3f}, N - V {accN(U) - microV(U):+.3f}")
