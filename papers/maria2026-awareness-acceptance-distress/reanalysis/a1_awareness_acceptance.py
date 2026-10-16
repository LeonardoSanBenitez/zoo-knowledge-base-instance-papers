"""Antunes, Chiodelli & Jesus (Zenodo 14946661, n=114): do the two PHLMS facets relate differently to distress?
Hypothesis from the meditation-harms literature: awareness WITHOUT acceptance goes with more distress.
Zero-order correlations, then OLS of each outcome on standardised awareness, acceptance and their product."""
import os, numpy as np, pandas as pd, pyreadstat, statsmodels.formula.api as smf
P = os.environ.get('ANTUNES_SAV', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'DataBase.sav'))
df, meta = pyreadstat.read_sav(P)
print('n', len(df), '| missing per column:', df.isna().sum().to_dict())
df['DASS'] = df.DASSDep + df.DASSAnx + df.DASSStress
z = lambda s: (s - s.mean()) / s.std()
df['aw'] = z(df.PHLMSAw); df['acc'] = z(df.PHLMSAcc)
print('r(awareness, acceptance) =', round(df.PHLMSAw.corr(df.PHLMSAcc), 3))
outs = ['DASS', 'DASSDep', 'DASSAnx', 'DASSStress', 'DERStotal', 'Sattotal', 'Ottotal']
for o in outs:
    r_aw = df.PHLMSAw.corr(df[o]); r_acc = df.PHLMSAcc.corr(df[o])
    m = smf.ols(f'{o} ~ aw * acc', df).fit()
    yz = z(df[o]); mz = smf.ols('yz ~ aw * acc', df.assign(yz=yz)).fit()
    print(f"{o:10s} r(aw) {r_aw:+.2f}  r(acc) {r_acc:+.2f} | std betas: aw {mz.params['aw']:+.2f} (p {mz.pvalues['aw']:.3f}), acc {mz.params['acc']:+.2f} (p {mz.pvalues['acc']:.3f}), aw:acc {mz.params['aw:acc']:+.2f} (p {mz.pvalues['aw:acc']:.3f})  R2 {mz.rsquared:.2f}")
# simple slopes of awareness on DASS at low/high acceptance
m = smf.ols('DASS ~ aw * acc', df).fit()
for lvl in (-1, 1):
    print(f'slope of awareness on DASS at acceptance {lvl:+d} SD: {m.params["aw"] + lvl * m.params["aw:acc"]:+.2f} DASS points per SD')
print('DASS total mean', round(df.DASS.mean(), 1), 'SD', round(df.DASS.std(), 1))
