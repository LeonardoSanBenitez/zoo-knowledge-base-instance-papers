"""Is Function's deficit a token-budget artefact? Regress EM on method with generator x retriever fixed effects and
log(avg_token_cost); compare the Function coefficient with and without the cost term."""
import os, numpy as np, pandas as pd, statsmodels.formula.api as smf
PKG = os.environ.get('WU_PKG', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pkg', 'chunk'))
for split in ['api', 'line']:
    df = pd.read_csv(os.path.join(PKG, 'eval', 'repoeval', 'result', f'{split}_all_results.csv'))
    df = df[(df.method != 'baseline') & (df.llm != 'starcoder2-7b')].copy(); df['EMpp'] = df.EM * 100; df['lcost'] = np.log2(df.avg_token_cost)
    print(f'== {split}: mean token cost by method', df.groupby('method').avg_token_cost.mean().round(0).to_dict())
    for f in ['EMpp ~ C(method, Treatment("sliding")) + C(llm)*C(retriever)', 'EMpp ~ C(method, Treatment("sliding")) + lcost + C(llm)*C(retriever)']:
        m = smf.ols(f, df).fit(cov_type='cluster', cov_kwds={'groups': df.llm + df.retriever})
        k = [c for c in m.params.index if 'function' in c][0]
        extra = f", per doubling of tokens {m.params['lcost']:+.2f} pp" if 'lcost' in f else ''
        print(f"  {'with log cost' if 'lcost' in f else 'no cost term':14s}: Function - Sliding = {m.params[k]:+.2f} pp (cluster SE {m.bse[k]:.2f}){extra}")
