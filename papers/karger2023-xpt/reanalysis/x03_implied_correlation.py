"""x03 -- Turn the criticism into a measurement: what within-person correlation
across risks does the reported residual imply?

WHERE x02 LEFT IT. At the person-to-person spread derived from the report's own
intervals (mean sigma_log = 3.95 on the extinction questions), taking a median
question-by-question manufactures a total-over-sum ratio of 7.77 even when every
forecaster is perfectly coherent and puts ZERO weight on unnamed causes. The
observed ratio is 2.13. So the residual carries no evidence about unnamed
causes -- the artifact is more than three times too big to leave any.

BUT x02 DREW EACH CAUSE INDEPENDENTLY ACROSS PEOPLE, and the report's own key
takeaway 5 says the opposite: "Predictions about risk were highly correlated
across topics." A person who is alarmed about AI is alarmed about pathogens too.
Positive correlation SHRINKS the artifact, because the person sitting at the
median of one question is closer to the median of the others.

So the ratio is not just a nuisance. It is an ESTIMATOR of that correlation,
and the report supplies everything needed to invert it: the medians, the
bootstrap intervals (hence the spread), and the group sizes.

MODEL. Each forecaster's log-probabilities across the five named causes are
multivariate normal with the per-cause means and SDs derived in x02, and
equicorrelation rho_w. Their total is the genuine union, 1 - prod(1 - p), so
every individual is coherent by construction and no unnamed cause exists. Solve
for the rho_w that reproduces the observed ratio.

WHAT WOULD BREAK THIS. If the true copula is not Gaussian, or the correlation
is not equal across pairs, the point estimate moves. Both are tested below by
re-solving under a strong-tail-dependence alternative and under a
one-factor-plus-noise structure. If the answer is unstable across those, it
should not be quoted as a number, only as a direction.

Run: python x03_implied_correlation.py
"""
import csv
import math
import os

import numpy as np

SRC = os.path.join("..", "artifacts", "xpt_tables_2_3.csv")
RNG = np.random.default_rng(1618033)
CAUSES = ["ai", "engineered_pathogen", "natural_pathogen", "nuclear",
          "non_anthropogenic"]
NGROUP = {"superforecasters": 88, "domain_experts": 59}


def load():
    d = {}
    for r in csv.DictReader(open(SRC, encoding="utf-8")):
        d[(r["outcome"], r["cause"], r["group"])] = (
            float(r["median_pct"]), float(r["ci_low"]), float(r["ci_high"]))
    return d


def sigma_log_from_ci(lo, hi, n):
    if lo <= 0 or hi <= 0 or hi <= lo:
        return None
    return (math.log(hi) - math.log(lo)) / 3.92 * math.sqrt(n) / 1.2533


def params(d, outcome, group):
    mus, sds = [], []
    for c in CAUSES:
        m, lo, hi = d[(outcome, c, group)]
        s = sigma_log_from_ci(lo, hi, NGROUP[group]) or 1.0
        mus.append(math.log(m / 100.0))
        sds.append(s)
    return np.array(mus), np.array(sds)


def ratio_at(mus, sds, n, rho_w, reps, rng, structure="equicorr"):
    k = len(mus)
    out = []
    for _ in range(reps):
        if structure == "equicorr":
            C = np.full((k, k), rho_w)
            np.fill_diagonal(C, 1.0)
            L = np.linalg.cholesky(C + 1e-9 * np.eye(k))
            Z = L @ rng.normal(size=(k, n))
        elif structure == "one-factor":
            # a single "alarm" factor plus idiosyncratic noise; same average
            # pairwise correlation, different higher-order structure
            f = rng.normal(size=(1, n))
            lam = math.sqrt(max(rho_w, 0.0))
            Z = lam * np.repeat(f, k, axis=0) + \
                math.sqrt(max(1 - rho_w, 0.0)) * rng.normal(size=(k, n))
        elif structure == "t-copula":
            # heavy joint tails: the same Gaussian correlation, scaled by a
            # common chi factor, so extreme people are extreme on everything
            C = np.full((k, k), rho_w)
            np.fill_diagonal(C, 1.0)
            L = np.linalg.cholesky(C + 1e-9 * np.eye(k))
            g = L @ rng.normal(size=(k, n))
            nu = 4.0
            w = np.sqrt(nu / rng.chisquare(nu, size=(1, n)))
            Z = g * w / math.sqrt(nu / (nu - 2))
        P = np.clip(np.exp(mus[:, None] + sds[:, None] * Z), 0, 0.999)
        total = 1.0 - np.prod(1.0 - P, axis=0)
        s = sum(np.median(P[j]) for j in range(k))
        out.append(np.median(total) / max(s, 1e-15))
    return float(np.mean(out))


def solve(mus, sds, n, target, rng, structure="equicorr", reps=200):
    lo, hi = 0.0, 0.995
    for _ in range(28):
        mid = (lo + hi) / 2
        r = ratio_at(mus, sds, n, mid, reps, rng, structure)
        if r > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def main():
    d = load()
    rows = []
    print("=" * 92)
    print("1. THE RATIO AS A FUNCTION OF WITHIN-PERSON CORRELATION")
    print("   Extinction questions, superforecasters, coherent, no unnamed cause")
    print("=" * 92)
    mus, sds = params(d, "extinction_by_2100", "superforecasters")
    n = NGROUP["superforecasters"]
    print(f"  {'rho_w':>7} {'ratio total/sum':>17}")
    for rw in (0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 0.95, 0.99):
        r = ratio_at(mus, sds, n, rw, 200, RNG)
        print(f"  {rw:7.2f} {r:17.2f}")
        rows.append(dict(check="curve", group="superforecasters",
                         outcome="extinction", rho_w=rw, ratio=r))
    print()
    print("  Monotone decreasing, as it must be: the more a person's risks move")
    print("  together, the closer the median person is to the median on every")
    print("  question, and the better the medians add up.")

    print()
    print("=" * 92)
    print("2. SOLVING FOR THE CORRELATION THE REPORT IMPLIES")
    print("=" * 92)
    targets = {("extinction_by_2100", "superforecasters"): 2.13,
               ("extinction_by_2100", "domain_experts"): 1.31,
               ("catastrophe_by_2100", "superforecasters"): 1.13,
               ("catastrophe_by_2100", "domain_experts"): 0.84}
    print(f"  {'outcome':<20} {'group':<20} {'observed ratio':>14} "
          f"{'implied rho_w':>14}")
    for (outcome, g), tgt in targets.items():
        mus, sds = params(d, outcome, g)
        n = NGROUP[g]
        r0 = ratio_at(mus, sds, n, 0.0, 200, RNG)
        if tgt >= r0:
            print(f"  {outcome:<20} {g:<20} {tgt:14.2f} "
                  f"{'<0 (ratio at rho=0 is ' + format(r0, '.2f') + ')':>14}")
            rows.append(dict(check="solve", outcome=outcome, group=g,
                             observed=tgt, implied_rho=None, ratio_at_zero=r0))
            continue
        rw = solve(mus, sds, n, tgt, RNG)
        print(f"  {outcome:<20} {g:<20} {tgt:14.2f} {rw:14.2f}")
        rows.append(dict(check="solve", outcome=outcome, group=g,
                         observed=tgt, implied_rho=rw, ratio_at_zero=r0))
    print()
    print("  A ratio BELOW the rho=0 value means the observed data are more")
    print("  coherent than independent answering would give -- consistent with")
    print("  the report's own key takeaway 5, that risk forecasts were highly")
    print("  correlated across topics. A ratio of 0.84 (domain experts,")
    print("  catastrophe) is below 1 entirely and needs no correlation to")
    print("  explain: it is what happens when the total question is answered")
    print("  more conservatively than the parts.")

    print()
    print("=" * 92)
    print("3. IS THE ANSWER STABLE UNDER A DIFFERENT DEPENDENCE STRUCTURE?")
    print("=" * 92)
    mus, sds = params(d, "extinction_by_2100", "superforecasters")
    n = NGROUP["superforecasters"]
    print(f"  {'structure':<16} {'implied rho_w for ratio 2.13':>30}")
    for st in ("equicorr", "one-factor", "t-copula"):
        rw = solve(mus, sds, n, 2.13, RNG, structure=st)
        print(f"  {st:<16} {rw:30.2f}")
        rows.append(dict(check="structure", structure=st, implied_rho=rw))
    print()
    print("  If these three disagree materially, the number is a property of my")
    print("  copula and not of their forecasters, and only the DIRECTION should")
    print("  be quoted. Read the spread before quoting anything.")

    keys = sorted({k for r in rows for k in r})
    with open("out_implied_correlation.csv", "w", newline="",
              encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print("\nwrote out_implied_correlation.csv")


if __name__ == "__main__":
    main()
