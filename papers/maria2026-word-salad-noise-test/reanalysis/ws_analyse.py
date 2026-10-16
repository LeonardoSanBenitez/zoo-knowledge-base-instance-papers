"""Pre-registered analysis (ANALYSIS_PLAN.md): paired exact McNemar + bootstrap CI for C1-C0 and C2-C0."""
import json, random, sys
from scipy.stats import binomtest
R = [json.loads(l) for l in open(sys.argv[1] if len(sys.argv) > 1 else 'results_qwen3.5_4b.jsonl', encoding='utf-8')]
n = len(R); acc = {k: sum(r[k]['ok'] for r in R) / n for k in ('C0', 'C1', 'C2')}
print('n', n, {k: round(v, 4) for k, v in acc.items()})
rng = random.Random(0)
for a, b in (('C1', 'C0'), ('C2', 'C0'), ('C1', 'C2')):
    up = sum(r[a]['ok'] and not r[b]['ok'] for r in R); dn = sum(r[b]['ok'] and not r[a]['ok'] for r in R)
    p = binomtest(up, up + dn, 0.5).pvalue if up + dn else 1.0
    d = [r[a]['ok'] - r[b]['ok'] for r in R]
    bs = sorted(sum(rng.choices(d, k=n)) / n for _ in range(10000))
    print(f'{a}-{b}: diff {sum(d)/n:+.4f} 95% CI [{bs[250]:+.4f}, {bs[9750]:+.4f}]  discordant {up}/{dn}  McNemar exact p {p:.4f}')
nores = {k: sum('NO-RES' in r[k]['resp'].upper() for r in R) / n for k in ('C0', 'C1', 'C2')}
alen = {k: sum(len(r[k]['resp'].split()) for r in R) / n for k in ('C0', 'C1', 'C2')}
print('NO-RES rate', {k: round(v, 3) for k, v in nores.items()}, '| mean answer words', {k: round(v, 2) for k, v in alen.items()})
