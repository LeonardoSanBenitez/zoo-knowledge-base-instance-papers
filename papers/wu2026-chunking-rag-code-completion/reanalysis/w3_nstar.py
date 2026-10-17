"""Second corpus for the RAG area's candidate quantity n* (benchmark saturation size):
n* = median[p0(1-p0) + p1(1-p1)] / tau^2, tau^2 = between-configuration variance of the effect minus its mean sampling
variance (independent-arms binomial, as in the area's definition; the paired design makes true sampling variance smaller,
so tau^2 here is a LOWER bound and n* an UPPER bound). N per split = 1,600 tasks, recovered from the printed EM decimals
(88% exact at k/1600 with half-up rounding, the rest +0.0001)."""
import os, numpy as np, pandas as pd
PKG = os.environ.get('WU_PKG', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pkg', 'chunk'))
N = 1600
def nstar(p0, p1):
    eff = p1 - p0; v = (p0 * (1 - p0) + p1 * (1 - p1)) / N
    tau2 = max(eff.var(ddof=1) - v.mean(), 0); num = np.median(p0 * (1 - p0) + p1 * (1 - p1))
    return (num / tau2 if tau2 > 0 else float('inf')), eff.mean(), np.sqrt(tau2), np.sqrt(v.mean())
for split in ('api', 'line'):
    d = pd.read_csv(os.path.join(PKG, 'eval', 'repoeval', 'result', f'{split}_all_results.csv'))
    d = d[(d.method != 'baseline') & (d.llm != 'starcoder2-7b')]
    pv = d.pivot_table(index=['retriever', 'llm', 'max_chunk_size', 'max_crossfile_context'], columns='method', values='EM')
    cx = d.pivot_table(index=['retriever', 'llm', 'max_chunk_size', 'method'], columns='max_crossfile_context', values='EM')
    for name, p0, p1 in [('function - sliding', pv['sliding'], pv['function']), ('cast - sliding', pv['sliding'], pv['cast']),
                         ('context 8192 - 2048', cx[2048], cx[8192])]:
        ns, mu, tau, se = nstar(p0.values, p1.values)
        print(f'{split:4s} {name:22s} k={len(p0):3d} mean effect {mu*100:+.2f} pp | tau {tau*100:.2f} pp | single-config SE {se*100:.2f} pp | n* = {ns:,.0f} | N/n* = {N/ns:.2f}')

print('\nBOUNDS (paired arms: true sampling variance of a difference is unknown without per-item outputs, between 0 and the independent value)')
for split in ('api', 'line'):
    d = pd.read_csv(os.path.join(PKG, 'eval', 'repoeval', 'result', f'{split}_all_results.csv'))
    d = d[(d.method != 'baseline') & (d.llm != 'starcoder2-7b')]
    pv = d.pivot_table(index=['retriever', 'llm', 'max_chunk_size', 'max_crossfile_context'], columns='method', values='EM')
    cx = d.pivot_table(index=['retriever', 'llm', 'max_chunk_size', 'method'], columns='max_crossfile_context', values='EM')
    for name, p0, p1 in [('function - sliding', pv['sliding'], pv['function']), ('cast - sliding', pv['sliding'], pv['cast']),
                         ('context 8192 - 2048', cx[2048], cx[8192])]:
        eff = (p1 - p0).values; sd = eff.std(ddof=1); num = np.median(p0 * (1 - p0) + p1 * (1 - p1))
        se_ind = np.sqrt(np.mean((p0 * (1 - p0) + p1 * (1 - p1)) / N))
        print(f'{split:4s} {name:22s} observed SD of effect across configs {sd*100:.2f} pp (< independent SE {se_ind*100:.2f} pp) | n* >= {num/sd**2:,.0f} (N = {N})')
