"""Open question: depression effect (passive control, 1-6 months) is -0.89 among trials reporting mean+SD in both arms vs the
review's -0.53. Is that a reporting-completeness effect or a small-study effect? The 14 passive-control rows, from
artifacts/galante_csv/Outcomes_extracted_from_trials.csv. Incomplete rows converted under STATED assumptions:
Barrett 2018: 'Mean, 95% CI' read as mean +/- 1.96 SD (SD = width / 3.92) -- the interval is far too wide to be a CI of a mean
at n = 138; Moynihan 2013: 'NR ns', g = 0 with SE from n (100/100 assumed by the extractors); Vieten 2008: Cohen's d 0.58,
taken as favouring MBP. Sign: negative favours MBP."""
import numpy as np, pandas as pd, statsmodels.api as sm
def g_from(m1, s1, n1, m2, s2, n2):
    sp = np.sqrt(((n1 - 1) * s1 ** 2 + (n2 - 1) * s2 ** 2) / (n1 + n2 - 2)); J = 1 - 3 / (4 * (n1 + n2) - 9)
    g = J * (m1 - m2) / sp; v = (n1 + n2) / (n1 * n2) + g ** 2 / (2 * (n1 + n2)); return g, v
rows = [('Aeamla-Or 2015', 15.79, 8.04, 63, 19.02, 9.56, 63), ('Benn 2012', 30.82, 9.1, 24, 35.51, 9.83, 19),
        ('Carmody 2011', 3.4, 2.2, 57, 4.3, 3.7, 53), ('Christopher 2018', 48.15, 8.5, 24, 46.27, 7.37, 25),
        ('Dziok 2010', 12.3, 9.6, 23, 18.4, 13.1, 6), ('Haarig 2016', 7.1, 6.8, 14, 15.6, 10.5, 14),
        ('Kaviani 2008', 10.23, 3.9, 14, 20.34, 5.5, 15), ('Kor 2019', 17.78, 10, 18, 21.56, 11.81, 18),
        ('Roeser 2013', 21.09, 4.32, 24, 28.43, 5.28, 27), ('VanDam 2014', 31.48, 7.23, 21, 42.77, 11.23, 13),
        ('Yazdanimehr 2016', 9.03, 2.95, 30, 16.03, 2.45, 33)]
D = [dict(study=r[0], complete=1, n=r[3] + r[6], **dict(zip(('g', 'v'), g_from(*r[1:])))) for r in rows]
sdB1, sdB2 = (12.4 + 2.7) / 3.92, (12.9 + 3.2) / 3.92
g, v = g_from(3.9, sdB1, 138, 4.9, sdB2, 138); D.append(dict(study='Barrett 2018*', complete=0, n=276, g=g, v=v))
D.append(dict(study='Moynihan 2013*', complete=0, n=200, g=0.0, v=(200) / (100 * 100)))
D.append(dict(study='Vieten 2008*', complete=0, n=31, g=-0.58, v=31 / (13 * 18) + 0.58 ** 2 / 62))
d = pd.DataFrame(D); d['se'] = np.sqrt(d.v)
def re(dd):
    w = 1 / dd.v; mu_fe = (w * dd.g).sum() / w.sum(); Q = (w * (dd.g - mu_fe) ** 2).sum(); k = len(dd)
    tau2 = max(0, (Q - (k - 1)) / (w.sum() - (w ** 2).sum() / w.sum())); ws = 1 / (dd.v + tau2)
    mu = (ws * dd.g).sum() / ws.sum(); return mu, np.sqrt(1 / ws.sum()), tau2
print(d.round(3).to_string(index=False))
for lab, dd in [('complete only (11)', d[d.complete == 1]), ('all 14 (stated conversions)', d)]:
    mu, se, t2 = re(dd); print(f'{lab:30s} RE (DL) g = {mu:+.3f} [{mu-1.96*se:+.3f}, {mu+1.96*se:+.3f}] tau2 {t2:.3f}')
X = sm.add_constant(d.se); eg = sm.WLS(d.g, X, weights=1 / d.v).fit()
print(f"Egger-type regression of g on SE (all 14, WLS): slope {eg.params['se']:+.2f} (p {eg.pvalues['se']:.4f}), intercept {eg.params['const']:+.3f} (p {eg.pvalues['const']:.3f})")
X2 = sm.add_constant(d[['se', 'complete']]); m2 = sm.WLS(d.g, X2, weights=1 / d.v).fit()
print(f"g ~ SE + complete (WLS): complete {m2.params['complete']:+.3f} (p {m2.pvalues['complete']:.3f}), SE {m2.params['se']:+.2f} (p {m2.pvalues['se']:.4f})")
print('median n: complete', d[d.complete == 1].n.median(), '| incomplete', d[d.complete == 0].n.median())
