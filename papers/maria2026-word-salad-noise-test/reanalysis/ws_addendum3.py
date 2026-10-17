"""Analysis fixed by ANALYSIS_PLAN.md 'Addendum 2026-10-17 07:16' (committed 788e609 before any outcome):
P1 accuracy C2 - C0, P2 NO-RES rate C2 - C0, both exact McNemar, Holm at 0.05. Secondary: accuracy C1 - C0,
NO-RES C1 - C0, share of C2-only errors that are abstentions. Author: maria 2026-10-17."""
import json, sys
from scipy.stats import binomtest
R = [json.loads(l) for l in open(sys.argv[1], encoding='utf-8')][:200]
nores = lambda r, c: r[c]['resp'].strip().upper().startswith('NO-RES')
def mcnemar(x, y):
    b = sum(1 for u, v in zip(x, y) if u and not v); c = sum(1 for u, v in zip(x, y) if v and not u)
    return b, c, (binomtest(b, b + c, 0.5).pvalue if b + c else 1.0)
n = len(R); out = {}
for lab, f in (('acc', lambda r, c: r[c]['ok']), ('nores', nores)):
    for a, b in (('C2', 'C0'), ('C1', 'C0')):
        x = [f(r, a) for r in R]; y = [f(r, b) for r in R]
        d = (sum(x) - sum(y)) / n; bb, cc, p = mcnemar(x, y); out[(lab, a, b)] = (d, bb, cc, p)
        print(f"{lab:<5} {a}-{b}: {sum(x)/n:.3f} - {sum(y)/n:.3f} = {d:+.3f} | discordant {bb}/{cc} | exact McNemar p = {p:.4f}")
ps = sorted([('P1', out[('acc', 'C2', 'C0')][3]), ('P2', out[('nores', 'C2', 'C0')][3])], key=lambda t: t[1])
print("Holm:", [(k, round(p, 4), 'reject' if p <= 0.05 / (2 - i) else 'retain') for i, (k, p) in enumerate(ps)])
err = [r for r in R if r['C0']['ok'] and not r['C2']['ok']]
print(f"C2-only errors: {len(err)}, of which abstentions {sum(nores(r, 'C2') for r in err)}")
print(f"n = {n}")
