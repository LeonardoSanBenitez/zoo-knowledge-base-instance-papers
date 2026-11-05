"""Pawel & Held (2020, PLoS ONE 15(4):e0231416) -- reproduce Tables 2-3 and the Fig 7 coverages from the
RProjects data shipped in the R package ReplicationSuccess 1.3.3 (CRAN), in Python, from the paper's equations only.

Model (paper eqs 3, 4, 6), on the Fisher-z scale with t_o = fiso/se_fiso, c = se_o^2/se_r^2, d = tau^2/se_o^2:
  N  : flat prior, tau = 0      t_r ~ N(sqrt(c) t_o, c + 1)
  H  : flat prior, tau = 0.08   t_r ~ N(sqrt(c) t_o, c + 1 + 2cd)
  S  : sceptical,  tau = 0      s = max(1 - 1/t_o^2, 0);        t_r ~ N(s sqrt(c) t_o, s c + 1)
  SH : sceptical,  tau = 0.08   s = max(1 - (1+d)/t_o^2, 0);    t_r ~ N(s sqrt(c) t_o, s(c + cd) + 1 + cd)
Forecast of "significant replication" = P(t_r beyond z_.025 in the direction of the original).

Usage: python p01_reproduce.py <path to RProjects.rda>     Writes out/p01.json.
"""
import json, os, sys
import numpy as np, pandas as pd, pyreadr
from scipy import stats

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"); os.makedirs(OUT, exist_ok=True)
R = pyreadr.read_r(sys.argv[1])["RProjects"]
Z = stats.norm.isf(0.025)


def predictive(to, c, d, method):
    if method in ("N", "S"):  # tau = 0 BEFORE the shrinkage factor is computed (first version had this order wrong)
        d = np.zeros_like(to)
    if method in ("N", "H"):
        s = np.ones_like(to)
    else:
        s = np.maximum(1 - (1 + d) / to ** 2, 0)
    mean = s * np.sqrt(c) * to
    var = s * (c + c * d) + 1 + c * d if method in ("S", "SH") else c + 1 + 2 * c * d
    return mean, var


def p_sig(to, c, d, method):
    m, v = predictive(to, c, d, method)
    sgn = np.sign(to)
    return stats.norm.sf((Z - sgn * m) / np.sqrt(v))  # P(sgn * t_r > Z)


def evaluate(df, tau=0.08, outcome=None):
    to = (df.fiso / df.se_fiso).values; tr = (df.fisr / df.se_fisr).values
    c = (df.se_fiso ** 2 / df.se_fisr ** 2).values; d = tau ** 2 / df.se_fiso.values ** 2
    y = outcome if outcome is not None else ((np.sign(tr) == np.sign(to)) & (np.abs(tr) > Z)).astype(int)
    rows = {}
    for mth in ("N", "S", "H", "SH"):
        p = p_sig(to, c, d, mth)
        bs = float(np.mean((p - y) ** 2)); bs0 = float(np.mean((y.mean() - y) ** 2))
        m, v = predictive(to, c, d, mth)
        # 95% prediction interval for t_r -> coverage (paper Fig 7, effect-estimate scale is equivalent)
        cov = float(np.mean(np.abs(tr - m) <= Z * np.sqrt(v)))
        pit = stats.norm.cdf((tr - m) / np.sqrt(v))
        # Spiegelhalter z
        zs = float(np.sum((y - p) * (1 - 2 * p)) / np.sqrt(np.sum((1 - 2 * p) ** 2 * p * (1 - p))))
        chi = float(((y.sum() - p.sum()) ** 2) / np.sum(p * (1 - p)))  # 1-df approximation; paper does not say which
        rows[mth] = {"observed": int(y.sum()), "expected": round(float(p.sum()), 1), "BS": round(bs, 3), "BSnorm": round((bs0 - bs) / bs0, 3),
                     "coverage": round(cov, 3), "spiegelhalter_z": round(zs, 2), "PIT_mean": round(float(pit.mean()), 3),
                     "PIT_share_below_.1": round(float(np.mean(pit < 0.1)), 3), "chi2_1df_p": round(float(stats.chi2.sf(chi, 1)), 4)}
    return rows


PUB = {  # Table 2 expected, Table 3 BS, Fig 7 coverage -- transcribed from the PDF
    "Experimental Economics": {"N": (15.0, .271, .83), "S": (13.6, .226, .83), "H": (14.3, .262, .94), "SH": (12.4, .227, .89), "obs": 11},
    "Experimental Philosophy": {"N": (27.8, .193, .84), "S": (26.2, .173, .84), "H": (26.5, .170, .94), "SH": (24.1, .148, .90), "obs": 23},
    "Psychology": {"N": (55.4, .394, .70), "S": (49.2, .335, .75), "H": (53.5, .363, .81), "SH": (45.9, .289, .88), "obs": 24},
    "Social Sciences": {"N": (19.9, .346, .67), "S": (19.2, .324, .76), "H": (18.9, .310, .90), "SH": (17.6, .272, .95), "obs": 13},
}
res = {}
print(f"{'project':24s} {'m':3s} {'obs':>4s} {'exp pub/re':>12s} {'BS pub/re':>13s} {'cov pub/re':>12s}  spz")
for proj, df in R.groupby("project"):
    r = evaluate(df); res[proj] = r
    for mth, v in r.items():
        e, b, cv = PUB[proj][mth]
        print(f"{proj:24s} {mth:3s} {v['observed']:4d} {e:5.1f}/{v['expected']:5.1f} {b:.3f}/{v['BS']:.3f} {cv:.2f}/{v['coverage']:.2f}  {v['spiegelhalter_z']}")
# prediction-market Brier (Table 3: EE .243, SS .114)
for proj in ("Experimental Economics", "Social Sciences"):
    df = R[R.project == proj]; to = df.fiso / df.se_fiso; tr = df.fisr / df.se_fisr
    y = ((np.sign(tr) == np.sign(to)) & (np.abs(tr) > Z)).astype(int)
    res[proj]["PM_BS"] = round(float(np.mean((df.pm_belief - y) ** 2)), 3)
    print(proj, "PM Brier", res[proj]["PM_BS"], "(paper .243 / .114)")
json.dump(res, open(os.path.join(OUT, "p01.json"), "w"), indent=1)
