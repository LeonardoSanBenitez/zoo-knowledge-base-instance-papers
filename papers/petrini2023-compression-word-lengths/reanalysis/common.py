"""Shared helpers. Reads the authors' filtered corpora (fetch.py output) and computes the paper's statistics.

L   = sum_i p_i l_i          (token-weighted mean length; p_i = f_i / T)
L_r = M = mean_i l_i          (type-weighted mean length; Property 2.1: the random baseline)
tau = Kendall tau-b(frequency, length), r = Pearson r(frequency, length), both one-sided 'less'.
"""
import csv, math, os, site, sys
sys.path.append(site.getusersitepackages())       # scipy lives in the user site; -I removes it
import numpy as np
from scipy import stats

CV_LANGS = None


def read_pud(root, code):
    """PUD file: word,frequency,n_characters (strokes/pinyin/romaji variants are separate files)."""
    f, l = [], []
    with open(os.path.join(root, 'data', 'filtered', 'corpora', 'pud', code + '.csv'), encoding='utf-8') as fh:
        for row in csv.DictReader(fh):
            f.append(int(row['frequency'])); l.append(float(row['n_characters']))
    return np.array(f, float), np.array(l, float)


def read_cv(root, code, length='n_characters'):
    """Deposit quirk: abk-word.csv rows carry one extra leading field (the word, as an unnamed row label)
    that the header does not name -- 7 fields under a 6-name header. Every row of it, nowhere else."""
    f, l = [], []
    with open(os.path.join(root, 'data', 'filtered', 'corpora', 'cv', code + '-word.csv'), encoding='utf-8') as fh:
        rd = csv.reader(fh)
        h = next(rd)
        fi, li = h.index('frequency'), h.index(length)
        for row in rd:
            if len(row) == len(h) + 1:
                row = row[1:]
            assert len(row) == len(h), (code, row)
            f.append(int(row[fi])); l.append(float(row[li]))
    return np.array(f, float), np.array(l, float)


def summary(f, l, with_tests=True):
    T = f.sum(); n = len(f)
    p = f / T
    L = float((p * l).sum()); M = float(l.mean())
    out = {'n': n, 'T': int(T), 'L': L, 'Lr': M}
    if with_tests:
        tau = stats.kendalltau(f, l, alternative='less')
        r = stats.pearsonr(f, l, alternative='less')
        out.update(tau=float(tau.statistic), tau_p=float(tau.pvalue), r=float(r.statistic), r_p=float(r.pvalue))
        # Appendix A identity: L - L_r = (n - 1) s_p s_l r   (sample SDs, ddof=1)
        out['identity_gap'] = float((L - M) - (n - 1) * p.std(ddof=1) * l.std(ddof=1) * r.statistic)
    return out


def holm(ps):
    """R p.adjust(method='holm')."""
    ps = np.asarray(ps, float); m = len(ps); o = np.argsort(ps)
    adj = np.empty(m); run = 0.0
    for k, i in enumerate(o):
        run = max(run, min(1.0, (m - k) * ps[i])); adj[i] = run
    return adj
