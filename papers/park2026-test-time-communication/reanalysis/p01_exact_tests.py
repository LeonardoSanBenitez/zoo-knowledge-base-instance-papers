"""p01 -- Park et al. 2026 (arXiv 2609.21032): exact tests for the ARC-AGI-3 claims at the unit that varies.

Counts from the text: 64 single-agent trials per game, 20 team trials per (game, k).
  LP85: team@5 13/20 (65%) vs single 0/64.     FT09: team@3 18/20 (90%) vs single 6/64 (9.4%).
  Furthest level: communication helps on 18 of 25 games, hurts on 7 (Fig 2a).
best@k from a finite pool, as the paper defines it: 1 - C(n-s,k)/C(n,k).
Known answer: best@3 on FT09 from s=6, n=64 must reproduce the printed 25.9%.
Run: python -I p01_exact_tests.py   (scipy)
"""
import json, math, os
from scipy.stats import fisher_exact, binomtest

def best_at_k(s, n, k):
    return 1 - math.comb(n - s, k) / math.comb(n, k)

out = {}
out["FT09_best3_from_6_of_64"] = round(100 * best_at_k(6, 64, 3), 1)          # paper: 25.9
out["LP85_best5_from_0_of_64"] = round(100 * best_at_k(0, 64, 5), 1)
out["LP85_team5_vs_single_fisher_p"] = float(fisher_exact([[13, 7], [0, 64]]).pvalue)
# team@5 (one trial = one team) vs a best@5 'trial' is not a per-agent comparison; compare team trials to
# best-of-5 success probability under the single-agent rate, as a binomial: P(X >= 13 | n=20, p=best@5)
p5 = best_at_k(0, 64, 5)
out["LP85_team5_vs_best5_binom_p"] = float(binomtest(13, 20, max(p5, 1e-9), alternative="greater").pvalue)
p3 = best_at_k(6, 64, 3)
out["FT09_team3_vs_best3_binom_p"] = float(binomtest(18, 20, p3, alternative="greater").pvalue)
out["furthest_level_sign_test_18_of_25_p_two_sided"] = round(float(binomtest(18, 25, 0.5).pvalue), 4)
out["note"] = ("The per-game effects on LP85 and FT09 are far beyond noise. The 25-game aggregate (8.0% vs 2.2%) "
               "is carried by 4 games, as the paper says. Furthest-level improvement on 18/25 games: sign test p = 0.043. "
               "best@k treats the 64-trial pool as the population, so its own sampling error (6/64) is ignored; "
               "at s = 0 the true single-agent rate could be up to about 4.6% (95% upper bound), and best@5 would then be "
               "about 21%, still far below 65%.")
out["LP85_single_rate_upper95"] = round(1 - 0.05 ** (1 / 64), 4)
out["LP85_best5_at_upper95"] = round(1 - (1 - out["LP85_single_rate_upper95"]) ** 5, 3)
here = os.path.dirname(os.path.abspath(__file__))
json.dump(out, open(os.path.join(here, "p01_out.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
