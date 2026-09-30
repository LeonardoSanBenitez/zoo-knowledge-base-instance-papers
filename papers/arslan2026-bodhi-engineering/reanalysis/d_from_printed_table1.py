"""Recompute every Cohen's d in Arslan et al. 2026 Table 1 from the printed seed-level mean +- SD.
Table 1 reports 'mean +- SD across five seeds'. If d = diff / pooled seed-SD reproduces the printed d,
the effect size was standardised by the between-SEED spread of a 200-case average, i.e. by the
reproducibility of the mean, not by the spread of the behaviour. Stdlib. Run: python d_from_printed_table1.py
"""
from math import sqrt
rows = [  # metric, baseline mean, sd, bodhi mean, sd, printed d
    ('4.1-mini overall score',        2.5, 1.8, 19.1, 1.0, 11.56),
    ('4.1-mini context-seeking',      7.8, 6.8, 97.3, 3.7, 16.38),
    ('4.1-mini hedging',              1.7, 1.7, 21.9, 4.6,  5.80),
    ('4.1-mini communication',       70.1, 5.4, 57.5, 2.6, -2.94),
    ('4o-mini overall score',         0.0, 0.0,  2.2, 2.0,  1.56),
    ('4o-mini context-seeking',       0.0, 0.0, 73.5, 5.3, 19.54),
    ('4o-mini hedging',               0.0, 0.0,  4.1, 5.0,  1.16),
    ('4o-mini communication',        62.7, 4.6, 51.4, 6.5, -2.02),
]
J5 = 1 - 3 / (4 * (5 + 5) - 9)   # Hedges small-sample factor for n1 = n2 = 5
print(f"{'metric':28s} {'d_seed':>7s} {'g_seed':>7s} {'printed':>8s} {'d_response(binary)':>19s}")
for m, a, sa, b, sb, pd in rows:
    d = (b - a) / sqrt((sa**2 + sb**2) / 2)
    resp = ''
    if 'context' in m or 'hedging' in m:   # binary per-response outcome: SD = sqrt(p(1-p))
        pa, pb = a / 100, b / 100
        resp = f"{(pb - pa) / sqrt((pa*(1-pa) + pb*(1-pb)) / 2):19.2f}"
    print(f"{m:28s} {d:7.2f} {J5*d:7.2f} {pd:8.2f} {resp}")
# binomial check: SD across seeds of a 200-case proportion cannot exceed sqrt(p(1-p)/200) if seeds
# only resample the model on fixed cases (it should be smaller); compare.
for m, p, sd in [('4.1-mini context-seeking baseline', .078, 6.8), ('4.1-mini hedging bodhi', .219, 4.6)]:
    print(f"{m}: printed seed SD {sd} pp vs binomial ceiling {100*sqrt(p*(1-p)/200):.1f} pp")
