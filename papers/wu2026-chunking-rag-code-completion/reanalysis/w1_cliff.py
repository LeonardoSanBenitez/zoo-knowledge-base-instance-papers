"""Wu et al. 2026: the reported 'Cliff's delta' is a paired sign statistic. Recompute the real (unpaired) Cliff's delta,
the paired sign statistic (to reproduce their table), and the paired EM difference distribution."""
import os, sys, numpy as np, pandas as pd
from scipy.stats import wilcoxon
from itertools import combinations
PKG = os.environ.get('WU_PKG', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pkg', 'chunk'))  # unzip chunk.zip into reanalysis/pkg
def cliff_unpaired(x, y):
    x = np.asarray(x)[:, None]; y = np.asarray(y)[None, :]; return float(((x > y).sum() - (x < y).sum()) / (x.size * y.size))
def sign_paired(x, y): return float((np.sum(x > y) - np.sum(x < y)) / len(x))
M = ['function', 'declaration', 'sliding', 'cast']
for split in ['api', 'line']:
    df = pd.read_csv(os.path.join(PKG, 'eval', 'repoeval', 'result', f'{split}_all_results.csv'))
    keep_sc2 = os.environ.get('INCLUDE_STARCODER2') == '1'   # variant: include StarCoder2 (180 configurations)
    df = df[df.method.isin(M) & (keep_sc2 | (df.llm != 'starcoder2-7b'))]  # the notebook drops StarCoder2 for RepoEval (paper: 4 x 4 x 9 = 144)
    pv = df.pivot_table(index=['retriever', 'llm', 'max_chunk_size', 'max_crossfile_context'], columns='method', values='EM')
    print(f'== RepoEval {split}: {len(pv)} matched configurations')
    for a, b in combinations(M, 2):
        x, y = pv[a].values, pv[b].values; d = (x - y) * 100
        print(f'  {a:11s} vs {b:11s} paired-sign {sign_paired(x, y):+.3f} | TRUE Cliff delta {cliff_unpaired(x, y):+.3f} | paired diff pp mean {d.mean():+.2f} [min {d.min():+.2f}, max {d.max():+.2f}]')
    # how much of the configuration-level variance is generator vs strategy?
    sd_gen = df.groupby('llm').EM.mean().std() * 100; sd_meth = df.groupby('method').EM.mean().std() * 100; sd_ctx = df.groupby('max_crossfile_context').EM.mean().std() * 100
    print(f'  SD of marginal means (pp): generator {sd_gen:.2f} | method {sd_meth:.2f} | context length {sd_ctx:.2f}')
