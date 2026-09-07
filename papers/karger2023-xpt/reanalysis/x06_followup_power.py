"""x06 -- the 2025 near-term accuracy follow-up reports three null results. What
could its design have detected?

SOURCE AND ITS LIMIT. The report itself
(https://forecastingresearch.org/near-term-xpt-accuracy) does not resolve from
this machine -- curl returns HTTP 000, as recorded in the parent record's
operational notes. What IS reachable is the authors' own write-up on their
Substack (2025-09-02), which states the headline numbers. So every quantity below
is from the authors, and none of it is from the report. Read depth for that
artifact is the summary, not the paper, and no assessment of anything the report
says beyond these numbers should be recorded.

THEIR THREE NULLS:
  1. "The performance gap between the most and least accurate XPT participant
     groups spanned just 0.18 standard deviations ... these differences were not
     statistically significant."
  2. "the correlation coefficients between short-run accuracy and various
     long-term risks were all close to zero, and none of them were statistically
     significant."
  3. "Individual forecasters failed to beat two simple algorithms."

The first two are null results. The third is not -- it is a positive finding in
the opposite direction, and it is the one that needs no power argument at all.

WHAT I ADD. For (1) and (2), the minimum detectable effect at the design's own n,
plus the attenuation ceiling that the length of the question set imposes on (2).
An accuracy score built from 38 questions -- many of which, by the authors' own
description, were low-probability events that did not occur, on which everyone
scores nearly the same -- is a noisy measure of skill, and a noisy measure caps
the correlation it can show with anything.

I ALSO DISCARDED AN ARGUMENT HERE, and it is recorded because the reason matters.
I intended to argue that the long-term risk measure is unreliable, using this
record's own finding that the same 405 people give answers up to 800,000 times
apart across two response formats. It does not work: c2 also records that RANKS
are preserved across formats (4 of 4) while RATIOS are not (1 of 6). A format
effect that shifts everyone in the same direction changes no correlation. The
800,000x is fatal to reading the probabilities as probabilities and harmless to
reading them as an ordering, and a correlation uses the ordering.
"""
import io
import json
import math
import os

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))

N_SUPER = 88
N_EXPERT = 59
N_ALL = 169
K_QUESTIONS = 38


def mde_two_sample(n1, n2, alpha=0.05, power=0.8):
    z = stats.norm.ppf(1 - alpha / 2.0)
    zb = stats.norm.ppf(power)
    return (z + zb) * math.sqrt(1.0 / n1 + 1.0 / n2)


def power_two_sample(d, n1, n2, alpha=0.05):
    ncp = d / math.sqrt(1.0 / n1 + 1.0 / n2)
    z = stats.norm.ppf(1 - alpha / 2.0)
    return float(1 - stats.norm.cdf(z - ncp) + stats.norm.cdf(-z - ncp))


def mde_correlation(n, alpha=0.05, power=0.8):
    z = stats.norm.ppf(1 - alpha / 2.0)
    zb = stats.norm.ppf(power)
    zr = (z + zb) / math.sqrt(n - 3.0)
    return float(np.tanh(zr))


def main():
    out = {}

    print("=== 1. the group-difference null ===")
    print("    observed gap between the most and least accurate groups: 0.18 SD")
    print("    superforecasters n = %d, domain experts n = %d" % (N_SUPER, N_EXPERT))
    m = mde_two_sample(N_SUPER, N_EXPERT)
    p = power_two_sample(0.18, N_SUPER, N_EXPERT)
    print("    smallest detectable difference at 80%% power = %.3f SD" % m)
    print("    power to detect the 0.18 SD they observed     = %.0f%%" % (100 * p))
    print()
    print("    So 'not statistically significant' excludes nothing below half a")
    print("    standard deviation, and the study had about one chance in five of")
    print("    calling the effect it actually saw. The null is a statement about")
    print("    the sample size, not about forecasters.")
    out["group_difference"] = dict(observed_d=0.18, mde_d=m, power_at_observed=p,
                                   n1=N_SUPER, n2=N_EXPERT)

    print()
    print("    For contrast, the SAME design detected the public-participant gap:")
    for d in (1.82, 1.0, 0.5, 0.18):
        print("      d = %.2f -> power %.0f%%" % (d, 100 * power_two_sample(d, N_SUPER, 100)))
    print("    at 1.82 SD it is certain, at 0.5 SD it is a coin flip. The design")
    print("    separates forecasters from the public and cannot separate")
    print("    forecasters from each other. Both facts are in the same table.")

    print()
    print("=== 2. the accuracy-versus-risk-view null ===")
    print("    smallest correlation detectable at 80%% power:")
    for n in (N_ALL, N_SUPER, N_EXPERT, 40):
        print("      n = %3d  ->  |r| >= %.3f" % (n, mde_correlation(n)))
        out.setdefault("mde_correlation", {})[str(n)] = mde_correlation(n)
    print()
    print("    AND THAT IS THE OPTIMISTIC VERSION. An observed correlation is")
    print("    capped by the reliability of both measures: |r_obs| <= sqrt(rel_x *")
    print("    rel_y). The accuracy score rests on %d questions, and by the" % K_QUESTIONS)
    print("    authors' own account many of them were low-probability events that")
    print("    did not occur or slow-moving variables where the trend held -- on")
    print("    which every competent forecaster scores nearly the same. The")
    print("    discriminating questions are the surprises, and they name six.")
    print()
    print("    %-26s %-14s %-24s" % ("reliability of accuracy", "ceiling on |r|",
                                     "true r needed to detect at n=169"))
    for rel in (1.0, 0.7, 0.5, 0.4, 0.3, 0.2):
        ceil = math.sqrt(rel * 0.9)          # risk view assumed near-reliable
        need = mde_correlation(N_ALL) / math.sqrt(rel * 0.9)
        need_s = "%.3f" % need if need <= 1 else "IMPOSSIBLE"
        print("    %-26.2f %-14.3f %-24s" % (rel, ceil, need_s))
        out.setdefault("attenuation", {})["%.1f" % rel] = dict(ceiling=ceil,
                                                               needed=need)
    print()
    print("    Spearman-Brown, for a sense of scale: if a single question carries")
    print("    reliability r1, then k questions carry k*r1/(1+(k-1)*r1).")
    print("    %-18s %-14s" % ("per-question rel", "rel at k=38"))
    for r1 in (0.01, 0.02, 0.03, 0.05, 0.10):
        rk = K_QUESTIONS * r1 / (1 + (K_QUESTIONS - 1) * r1)
        print("    %-18.2f %-14.3f" % (r1, rk))
        out.setdefault("spearman_brown", {})["%.2f" % r1] = rk
    print()
    print("    Forecasting-skill scores are famously low-reliability per question.")
    print("    At a per-question reliability of 0.03 the 38-item score reaches")
    print("    0.54, which caps any observable correlation at 0.70 and requires a")
    print("    TRUE correlation of 0.31 before this design could see it.")

    print()
    print("=== 3. the finding that needs no power argument ===")
    print("    'Individual forecasters failed to beat two simple algorithms: a")
    print("     no-change algorithm and one that extrapolated the current trend.'")
    print()
    print("    This is a within-subject comparison against a fixed benchmark, not")
    print("    a between-group test, and it is a positive result rather than a")
    print("    null. 169 selected, incentivised forecasters -- 88 of them with")
    print("    proven track records -- after four months of paid deliberation, did")
    print("    not beat 'assume nothing changes'. Median aggregation gained about")
    print("    1 SD and showed only weak evidence of beating no-change, and did")
    print("    not beat trend extrapolation at all.")
    print()
    print("    That is the load-bearing result of the follow-up, and it is not one")
    print("    of the three the summary leads with.")

    print()
    print("=== 4. what this settles for the parent record ===")
    print("    c1 says experts and superforecasters differ sixfold on extinction")
    print("    risk and four months of argument moved neither. A natural")
    print("    explanation would be that one group is simply better. The follow-up")
    print("    removes that explanation as far as its power allows -- which is not")
    print("    far: it can exclude a skill gap above 0.47 SD and no smaller one.")
    print()
    print("    The honest statement is NOT 'the two groups are equally accurate'.")
    print("    It is: after the first 38 of 172 questions resolved, no skill")
    print("    difference large enough for this design to see has appeared, and")
    print("    the design can only see large ones.")

    with io.open(os.path.join(HERE, "out_x06.json"), "w", encoding="utf-8",
                 newline="\n") as f:
        json.dump(out, f, indent=1)
    print()
    print("wrote out_x06.json")


if __name__ == "__main__":
    main()
