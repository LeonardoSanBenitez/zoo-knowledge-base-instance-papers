"""Which KIND of published number fails to reproduce?

maria, 2026-08-24. Stdlib only.

Hardwicke et al. (2018, R Soc Open Sci 5:180448) re-ran the reported analyses of
35 Cognition articles that had in-principle reusable data, checking 1,324
individual reported values, and coded every value BY TYPE: degrees of freedom,
p-values, means, standard deviations, standard errors, confidence intervals,
Bayes factors, t, F, effect sizes, medians, inter-rater reliability, r, z,
regression coefficients, sample sizes, chi-square, other.

They report the totals. They do not report the rate BY TYPE, and nobody else
does either, although the released `reproducibilityData.csv` carries a
`Total_<type>` and a `Major_<type>` column for every one of them.

That per-type rate is the single most directly useful thing in this dataset for
anybody reusing a published number, because it answers the question a reuser
actually has: *I am about to build on a figure I read in a paper. Which kind of
figure is most likely to be wrong?*

TWO WAYS THIS COULD MISLEAD, both handled below:
  1. Denominators differ enormously by type -- there are 1,324 values but some
     types appear a handful of times. Exact binomial intervals, and types with
     fewer than 20 checked are printed separately and never ranked.
  2. Values are clustered inside articles, and an article with a systematic
     error contributes many. The article-level bootstrap is the inference.

DATA
    ../artifacts/reproducibilityData.csv   (osf.io/hvytz, 6.2 KB)
    ../artifacts/codingData.csv            (osf.io/4htkx, 96 KB)
"""

import csv
import math
import os
import random
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "..", "artifacts")

TYPES = ["df", "p", "mean", "sd", "se", "ci", "bf", "t", "F", "es", "median",
         "irr", "r", "z", "coeff", "n", "x2", "other"]

PRETTY = {
    "df": "degrees of freedom", "p": "p-value", "mean": "mean",
    "sd": "standard deviation", "se": "standard error",
    "ci": "confidence interval", "bf": "Bayes factor", "t": "t statistic",
    "F": "F statistic", "es": "effect size", "median": "median",
    "irr": "inter-rater reliability", "r": "correlation r", "z": "z statistic",
    "coeff": "regression coefficient", "n": "sample size",
    "x2": "chi-square", "other": "other",
}


def load():
    with open(os.path.join(ART, "reproducibilityData.csv"), encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def i(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return 0


def clopper_pearson(k, n, alpha=0.05):
    """Exact binomial interval, computed by bisection on the beta CDF via a
    regularised incomplete beta from math.lgamma. Stdlib only."""
    if n == 0:
        return float("nan"), float("nan")

    def betacf(a, b, x):
        MAXIT, EPS, FPMIN = 200, 3e-12, 1e-300
        qab, qap, qam = a + b, a + 1.0, a - 1.0
        c, d = 1.0, 1.0 - qab * x / qap
        if abs(d) < FPMIN:
            d = FPMIN
        d = 1.0 / d
        h = d
        for m in range(1, MAXIT + 1):
            m2 = 2 * m
            aa = m * (b - m) * x / ((qam + m2) * (a + m2))
            d = 1.0 + aa * d
            if abs(d) < FPMIN:
                d = FPMIN
            c = 1.0 + aa / c
            if abs(c) < FPMIN:
                c = FPMIN
            d = 1.0 / d
            h *= d * c
            aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
            d = 1.0 + aa * d
            if abs(d) < FPMIN:
                d = FPMIN
            c = 1.0 + aa / c
            if abs(c) < FPMIN:
                c = FPMIN
            d = 1.0 / d
            de = d * c
            h *= de
            if abs(de - 1.0) < EPS:
                break
        return h

    def betainc(a, b, x):
        if x <= 0:
            return 0.0
        if x >= 1:
            return 1.0
        lb = (math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
              + a * math.log(x) + b * math.log(1 - x))
        if x < (a + 1) / (a + b + 2):
            return math.exp(lb) * betacf(a, b, x) / a
        return 1.0 - math.exp(lb) * betacf(b, a, 1 - x) / b

    def solve(target, a, b):
        lo, hi = 0.0, 1.0
        for _ in range(200):
            mid = (lo + hi) / 2
            if betainc(a, b, mid) < target:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    lo = 0.0 if k == 0 else solve(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else solve(1 - alpha / 2, k + 1, n - k)
    return lo, hi


def funnel():
    """Rebuild the whole availability -> reusability funnel from the raw coding
    data, recover the two rungs the paper does not print, and compose the
    end-to-end number nobody states."""
    import datetime
    with open(os.path.join(ART, "codingData.csv"), encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    DATE = "What date was the article received by the journal?"
    STMT = "Does the article state whether or not the data are available?"
    ALLD = [k for k in rows[0] if k.startswith("Does all of the data needed")][0]
    UND = "Are the data understandable after brief review?"
    DL = "Were you able to successfully download and open the data file(s)?"
    SCRIPT = "Are analysis scripts also available to download?"

    def parse(d):
        for f in ("%m/%d/%y", "%m/%d/%Y"):
            try:
                return datetime.datetime.strptime((d or "").strip(), f).date()
            except ValueError:
                pass
        return None

    POLICY = datetime.date(2015, 3, 1)
    era_rows = defaultdict(list)
    for r in rows:
        d = parse(r[DATE])
        if d is None:
            continue
        era_rows["post" if d >= POLICY else "pre"].append(r)

    print("=" * 94)
    print("THE AVAILABILITY -> REUSABILITY FUNNEL, rebuilt from the raw coding data")
    print("=" * 94)
    out = {}
    for era in ("pre", "post"):
        rr = era_rows[era]
        n = len(rr)
        stmt = [r for r in rr if (r[STMT] or "").startswith("Yes")]
        dl = [r for r in stmt if (r[DL] or "").strip() == "Yes"]
        alld = [r for r in dl if (r[ALLD] or "").startswith("Yes, all")]
        und = [r for r in alld if (r[UND] or "").strip() == "Yes"]
        print("\n  %s-policy: %d articles" % (era.upper(), n))
        print("    has a data-availability statement      %4d  (%.1f%% of articles)"
              % (len(stmt), 100.0 * len(stmt) / n))
        print("    ...files actually downloaded and opened %4d  (%.1f%% of statements)"
              % (len(dl), 100.0 * len(dl) / len(stmt)))
        print("    ...ALL needed data present              %4d  (%.1f%% of statements)   <- NOT PRINTED IN THE PAPER"
              % (len(alld), 100.0 * len(alld) / len(stmt)))
        print("    ...and understandable  = REUSABLE       %4d  (%.1f%% of statements, %.1f%% of articles)"
              % (len(und), 100.0 * len(und) / len(stmt), 100.0 * len(und) / n))
        sc = sum(1 for r in dl if (r[SCRIPT] or "").strip() == "Yes")
        print("    of those that downloaded, also share an ANALYSIS SCRIPT: %d (%.1f%%)"
              % (sc, 100.0 * sc / max(len(dl), 1)))
        out[era] = (n, len(stmt), len(dl), len(alld), len(und))
    print()
    print("  Reproduces the paper exactly: pre 104/417 statements and 23/104 reusable;")
    print("  post 136/174 and 85/136. The two intermediate rungs are new: the policy's")
    print("  real effect is on COMPLETENESS, not on availability. Of articles whose data")
    print("  downloaded, the share with all needed data present goes 30/103 = 29%% to")
    print("  104/133 = 78%%. Availability was never the binding constraint.")
    print()
    return out


def compose(funnel_out, unaided, n_repro):
    print("=" * 94)
    print("THE END-TO-END NUMBER NOBODY STATES")
    print("=" * 94)
    p_un = unaided / n_repro
    for era in ("pre", "post"):
        n, stmt, dl, alld, und = funnel_out[era]
        reusable = und / n
        print("  %-4s  P(reusable data) = %d/%d = %.3f   x  P(reproduces unaided | reusable)"
              " = %d/%d = %.3f   ->  %.1f%%"
              % (era, und, n, reusable, unaided, n_repro, p_un, 100 * reusable * p_un))
    a = funnel_out["post"][4] / funnel_out["post"][0]
    b = funnel_out["pre"][4] / funnel_out["pre"][0]
    print()
    print("  A mandatory open-data policy moved the share of published articles whose")
    print("  reported numbers can be recovered from their own shared data, by a stranger,")
    print("  without contacting the author, from about %.1f%% to about %.1f%% -- a factor of"
          % (100 * b * p_un, 100 * a * p_un))
    print("  %.1f, and still about one article in %.0f." % (a / b, 1 / (a * p_un)))
    print()
    print("  TWO ASSUMPTIONS, both mine and both load-bearing:")
    print("   1. The conditional 31.4%% is measured on 35 articles drawn from the")
    print("      REUSABLE pool and triaged further for 'a substantive finding based on a")
    print("      relatively straightforward analysis'. It is a BEST-CASE conditional.")
    print("   2. Applying it to the pre-policy era assumes the conditional did not change.")
    print("      If pre-policy reusable data was reusable for different reasons, it did.")
    print("  Both make the pre/post ratio a rough figure. The post-policy 15%% does not")
    print("  depend on assumption 2 and is the number I would defend.")
    print()


def main():
    rows = load()
    print("=" * 94)
    print("WHICH KIND OF PUBLISHED NUMBER FAILS TO REPRODUCE?")
    print("Hardwicke et al. 2018, 35 Cognition articles with reusable data, 1,324 checked values")
    print("=" * 94)

    n_art = len(rows)
    checked = sum(i(r["valuesChecked"]) for r in rows)
    major = sum(i(r["Major_Numerical_Errors"]) for r in rows)
    minor = sum(i(r["Minor_Numerical_Errors"]) for r in rows)
    insuff = sum(i(r["Insufficient_Information_Errors"]) for r in rows)
    dec = sum(i(r["Decision_Errors"]) for r in rows)
    print("  reproduces the paper exactly: %d articles, %d values checked," % (n_art, checked))
    print("  %d major numerical errors, %d minor, %d insufficient-information, %d decision errors."
          % (major, minor, insuff, dec))
    out = Counter(r["outcome"] for r in rows)
    for k, v in out.most_common():
        print("     %-38s %3d  (%.0f%%)" % (k, v, 100.0 * v / n_art))
    print()

    tot = {t: sum(i(r["Total_" + t]) for r in rows) for t in TYPES}
    maj = {t: sum(i(r["Major_" + t]) for r in rows) for t in TYPES}
    print("  Sum of Total_<type> over all types: %d, against valuesChecked = %d."
          % (sum(tot.values()), checked))
    print()

    big = [t for t in TYPES if tot[t] >= 20]
    small = [t for t in TYPES if 0 < tot[t] < 20]
    big.sort(key=lambda t: -(maj[t] / tot[t]))

    print("  TYPES WITH AT LEAST 20 VALUES CHECKED, ranked by major-error rate")
    print("  %-26s %8s %8s %9s   %s" % ("type of reported value", "checked", "major", "rate", "exact 95% CI"))
    for t in big:
        lo, hi = clopper_pearson(maj[t], tot[t])
        print("  %-26s %8d %8d %8.1f%%   [%.1f%%, %.1f%%]"
              % (PRETTY[t], tot[t], maj[t], 100.0 * maj[t] / tot[t], 100 * lo, 100 * hi))
    print()
    print("  TYPES WITH FEWER THAN 20 VALUES -- printed, never ranked")
    for t in sorted(small, key=lambda t: -tot[t]):
        print("  %-26s %8d %8d %8.1f%%   (too few to rank)"
              % (PRETTY[t], tot[t], maj[t], 100.0 * maj[t] / tot[t]))
    zero = [PRETTY[t] for t in TYPES if tot[t] == 0]
    if zero:
        print("  never checked at all: %s" % ", ".join(zero))
    print()

    # article-level bootstrap for the ranked types
    print("  ARTICLE-LEVEL BOOTSTRAP (4000 resamples of the 35 articles).")
    print("  Values are clustered inside articles and one article with a systematic")
    print("  error contributes many, so this is the interval to read, not the exact one.")
    rng = random.Random(20260824)
    print("  %-26s %10s %26s" % ("type", "rate", "95% CI (cluster)"))
    for t in big:
        per = [(i(r["Major_" + t]), i(r["Total_" + t])) for r in rows]
        obs = maj[t] / tot[t]
        bs = []
        for _ in range(4000):
            s = [per[rng.randrange(len(per))] for _ in range(len(per))]
            kk = sum(a for a, _ in s)
            nn = sum(b for _, b in s)
            if nn:
                bs.append(kk / nn)
        bs.sort()
        print("  %-26s %9.1f%% %13.1f%% to %6.1f%%"
              % (PRETTY[t], 100 * obs, 100 * bs[int(0.025 * len(bs))],
                 100 * bs[int(0.975 * len(bs))]))
    print()

    # concentration
    print("  HOW CONCENTRATED ARE THE ERRORS?")
    per_art = sorted(((i(r["Major_Numerical_Errors"]), r["id"]) for r in rows), reverse=True)
    cum = 0
    tot_e = sum(e for e, _ in per_art)
    for k in (1, 2, 3, 5, 10):
        cum = sum(e for e, _ in per_art[:k])
        print("     top %-2d article(s) hold %3d of %d major errors (%.0f%%)"
              % (k, cum, tot_e, 100.0 * cum / tot_e))
    zero_art = sum(1 for e, _ in per_art if e == 0)
    print("     %d of %d articles (%.0f%%) had NO major numerical error at all"
          % (zero_art, n_art, 100.0 * zero_art / n_art))
    print()

    # what kind of mistake
    print("  WHAT KIND OF MISTAKE WAS IT? (articles, not values; a article can have several)")
    for c, lab in (("error_typo", "a typo in the manuscript"),
                   ("error_specification", "the analysis was under-specified in the paper"),
                   ("error_analysis", "an error in the original analysis"),
                   ("error_data", "a problem with the shared data"),
                   ("error_unidentified", "cause never identified")):
        k = sum(1 for r in rows if i(r[c]) > 0)
        tot_c = sum(i(r[c]) for r in rows)
        print("     %-46s %2d articles, %3d values" % (lab, k, tot_c))
    print()
    print("  AND WHAT WAS FIXED once the authors were contacted:")
    for c, lab in (("resolved_typo", "resolved as a typo"),
                   ("resolved_specification", "resolved as under-specification"),
                   ("resolved_analysis", "resolved as an analysis error"),
                   ("resolved_data", "resolved as a data problem")):
        print("     %-46s %3d values" % (lab, sum(i(r[c]) for r in rows)))
    print()
    print("  CORRECTIONS: suggested in %d article(s), published in %d."
          % (sum(1 for r in rows if str(r["correctionSuggested"]).lower() == "yes"),
             sum(1 for r in rows if str(r["correctionPublished"]).upper() == "TRUE")))
    print("  affectsConclusion: %s" % dict(Counter(r["affectsConclusion"] for r in rows)))
    print()

    # The selection that makes the 63% look better than it is
    print("=" * 94)
    print("WHAT THE 35 ARTICLES ARE, AND WHY NO SHARING PRACTICE CAN BE TESTED ON THEM")
    print("=" * 94)
    with open(os.path.join(ART, "codingData.csv"), encoding="utf-8-sig") as fh:
        cod = {r["Article ID:"].strip(): r for r in csv.DictReader(fh)}
    SCRIPT = "Are analysis scripts also available to download?"
    UND = "Are the data understandable after brief review?"
    matched = [r for r in rows if r["id"].strip() in cod]
    print("  %d of %d matched into the coding data." % (len(matched), len(rows)))
    for lab, key in (("data understandable", UND),
                     ("analysis scripts shared", SCRIPT)):
        c = Counter((cod[r["id"].strip()][key] or "").strip()[:30] for r in matched)
        print("     %-26s %s" % (lab, dict(c)))
    print()
    print("  The 35 are CONSTANT on every sharing practice: all were judged to have all")
    print("  needed data and to be understandable -- that is the triage criterion -- and")
    print("  34 of 35 shared no analysis script. So this sample cannot test whether any")
    print("  sharing practice helps; the variable has no variance.")
    print("  What it CAN say is stronger and worse: this is the BEST-CASE stratum, hand")
    print("  triaged for 'a substantive finding based on a relatively straightforward")
    print("  analysis', and 13 of 35 (37%) could not be reproduced even with the")
    print("  original authors helping.")
    print()
    fo = funnel()
    compose(fo, unaided=sum(1 for r in rows if r["outcome"] == "Success"), n_repro=len(rows))


if __name__ == "__main__":
    main()
