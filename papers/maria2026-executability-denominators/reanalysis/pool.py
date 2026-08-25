"""
Is there such a thing as "the" rate at which published research artifacts work?

maria, 2026-08-24. Stdlib only.

THE QUESTION
------------
Seven large studies have measured whether deposited research code, notebooks or
data can be made to work. They are routinely quoted as agreeing with each other
around a quarter. This script asks two things:

  Q1. How much of the spread between these studies is a real difference between
      fields, and how much is the choice of denominator INSIDE each study?
  Q2. If every study is put on the widest denominator it defines itself, does the
      apparent agreement survive?

Method: random-effects meta-analysis of proportions on the logit scale
(DerSimonian-Laird, and also Paule-Mandel because DL is known to under-estimate
tau^2 -- I recorded that in maria2026-analytic-variability-reanalysis and it
applies here). Run twice: once on the rate each study PRINTED, once on the same
numerator over the widest denominator that study defines.

Two corrections that nobody in this literature applies:

  * CLUSTERING. Notebooks and script files are not independent; they sit in
    repositories and replication packages that share one environment. Measured
    ICC on the only corpus that ships per-unit records: 0.435
    (papers/samuel2024-jupyter-pmc/reanalysis/cluster_and_age.py). Effective n
    is divided by the design effect 1 + (m-1)*ICC.
  * EVENT MISMATCH. "The code builds", "the notebook runs to completion" and
    "the reported number comes out again" are three different events. They are
    kept as separate strata and never pooled together, which is the single
    commonest error in citing this literature.

INPUT: ../artifacts/funnels.csv -- every stage of every study, transcribed from
primary sources. See that file's header for provenance.
"""

import csv
import math
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
FUNNELS = os.path.join(HERE, "..", "artifacts", "funnels.csv")

ICC = 0.435          # measured, samuel2024 2021 corpus, outcome = executes

# Which event each study series measures. Pooling across these is the error.
EVENT_CLASS = {
    "trisovic2022": "runs",
    "samuel2024": "runs",
    "pimentel2019": "runs",
    "samuel2024out": "runs+output matches",
    "pimentel2019out": "runs+output matches",
    "collberg2015": "builds",
    "collberg2015c": "builds",
    "changli2015": "reported result recovered",
    "changli2015aid": "reported result recovered (author helped)",
    "hardwicke2018": "artifact present",
    "hardwicke2018r": "artifact present and usable",
    "hardwicke2018p": "reported result recovered",
    "hardwicke2018p2": "reported result recovered (author helped)",
    "stodden2018": "artifact present",
    "stodden2018r": "reported result recovered",
}

FIELD = {
    "trisovic2022": "social science (R, Dataverse)",
    "samuel2024": "biomedical (notebooks, PMC)",
    "samuel2024out": "biomedical (notebooks, PMC)",
    "pimentel2019": "general GitHub (notebooks)",
    "pimentel2019out": "general GitHub (notebooks)",
    "collberg2015": "CS systems",
    "collberg2015c": "CS systems",
    "changli2015": "economics",
    "changli2015aid": "economics",
    "hardwicke2018": "psychology (Cognition)",
    "hardwicke2018r": "psychology (Cognition)",
    "hardwicke2018p": "psychology (Cognition)",
    "hardwicke2018p2": "psychology (Cognition)",
    "stodden2018": "multidisciplinary (Science)",
    "stodden2018r": "multidisciplinary (Science)",
}

ABSTRACT_ONLY = {"stodden2018", "stodden2018r"}


def load():
    series = defaultdict(list)
    with open(FUNNELS, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("study,"):
                continue
            parts = line.split(",")
            study, order, stage, n, k, event, printed, unit, cluster_n = parts[:9]
            prov = ",".join(parts[9:])
            if not k:
                continue
            series[study].append({
                "study": study, "order": int(order), "stage": stage,
                "n": int(n), "k": int(k), "event": event,
                "printed": printed == "yes", "unit": unit,
                "clusters": int(cluster_n) if cluster_n else None,
                "prov": prov,
            })
    for s in series.values():
        s.sort(key=lambda r: r["order"])
    return series


# ----------------------------------------------------------------- statistics

def logit(p):
    return math.log(p / (1 - p))


def inv_logit(x):
    return 1.0 / (1.0 + math.exp(-x))


def logit_var(k, n):
    """Variance of the logit of a proportion, with a 0.5 continuity guard."""
    k = min(max(k, 0.5), n - 0.5)
    return 1.0 / k + 1.0 / (n - k)


def deff(n, clusters):
    if not clusters or clusters <= 0:
        return 1.0
    m = n / clusters
    return max(1.0, 1 + (m - 1) * ICC)


def dersimonian_laird(ys, vs):
    w = [1 / v for v in vs]
    sw = sum(w)
    ybar = sum(wi * yi for wi, yi in zip(w, ys)) / sw
    Q = sum(wi * (yi - ybar) ** 2 for wi, yi in zip(w, ys))
    dfree = len(ys) - 1
    C = sw - sum(wi ** 2 for wi in w) / sw
    tau2 = max(0.0, (Q - dfree) / C) if C > 0 else 0.0
    return tau2, Q, dfree


def paule_mandel(ys, vs, iters=200):
    """Iterative PM estimator of tau^2. Known to be less downward-biased than DL
    on heterogeneous small-k collections -- the same reason it is used in
    maria2026-analytic-variability-reanalysis."""
    tau2 = 0.0
    k = len(ys)
    for _ in range(iters):
        w = [1 / (v + tau2) for v in vs]
        sw = sum(w)
        ybar = sum(wi * yi for wi, yi in zip(w, ys)) / sw
        Q = sum(wi * (yi - ybar) ** 2 for wi, yi in zip(w, ys))
        if abs(Q - (k - 1)) < 1e-9:
            break
        deriv = sum(wi ** 2 * (yi - ybar) ** 2 for wi, yi in zip(w, ys))
        if deriv <= 0:
            break
        tau2 = max(0.0, tau2 + (Q - (k - 1)) / deriv)
    return tau2


def pool(rows, use_deff=True, label=""):
    ys, vs, names = [], [], []
    for r in rows:
        n = r["n"] / (deff(r["n"], r["clusters"]) if use_deff else 1.0)
        k = r["k"] / (deff(r["n"], r["clusters"]) if use_deff else 1.0)
        p = k / n
        ys.append(logit(min(max(p, 1e-6), 1 - 1e-6)))
        vs.append(logit_var(k, n))
        names.append(r["study"])
    tau2_dl, Q, dfree = dersimonian_laird(ys, vs)
    tau2_pm = paule_mandel(ys, vs)
    out = {}
    for tag, tau2 in (("DL", tau2_dl), ("PM", tau2_pm)):
        w = [1 / (v + tau2) for v in vs]
        sw = sum(w)
        mu = sum(wi * yi for wi, yi in zip(w, ys)) / sw
        se = math.sqrt(1 / sw)
        out[tag] = {"mu": mu, "se": se, "tau2": tau2,
                    "pooled": inv_logit(mu),
                    "lo": inv_logit(mu - 1.96 * se), "hi": inv_logit(mu + 1.96 * se),
                    "pi_lo": inv_logit(mu - 1.96 * math.sqrt(tau2 + se ** 2)),
                    "pi_hi": inv_logit(mu + 1.96 * math.sqrt(tau2 + se ** 2))}
    I2 = max(0.0, (Q - dfree) / Q) if Q > 0 else 0.0
    out["Q"] = Q
    out["df"] = dfree
    out["I2"] = I2
    out["k"] = len(ys)
    return out


def show_pool(res, label):
    d = res["DL"]
    p = res["PM"]
    print("  %-38s k=%d  Q=%.0f on %d df  I2=%.1f%%" % (label, res["k"], res["Q"], res["df"], 100 * res["I2"]))
    print("      DL pooled %.1f%%  [%.1f, %.1f]   tau=%.2f (logit)  95%% prediction interval [%.1f%%, %.1f%%]"
          % (100 * d["pooled"], 100 * d["lo"], 100 * d["hi"], math.sqrt(d["tau2"]),
             100 * d["pi_lo"], 100 * d["pi_hi"]))
    print("      PM pooled %.1f%%  [%.1f, %.1f]   tau=%.2f (logit)  95%% prediction interval [%.1f%%, %.1f%%]"
          % (100 * p["pooled"], 100 * p["lo"], 100 * p["hi"], math.sqrt(p["tau2"]),
             100 * p["pi_lo"], 100 * p["pi_hi"]))


# ----------------------------------------------------------------- report

def section_funnels(series):
    print("=" * 96)
    print("1. THE FUNNELS. Every rung each study defines, and which one it printed.")
    print("=" * 96)
    for st in sorted(series, key=lambda s: EVENT_CLASS[s]):
        rows = series[st]
        print("\n  %-18s %-42s  event: %s" % (st, FIELD[st], EVENT_CLASS[st]))
        for r in rows:
            mark = "  <== PRINTED" if r["printed"] else ""
            print("      %-58s %8d / %-9d = %6.2f%%%s"
                  % (r["stage"][:58], r["k"], r["n"], 100.0 * r["k"] / r["n"], mark))
    print()


def section_multiplier(series):
    print("=" * 96)
    print("2. THE DENOMINATOR MULTIPLIER.")
    print("   printed rate divided by the rate over the widest denominator the SAME")
    print("   study defines. 1.0 would mean the printed number is the population rate.")
    print("=" * 96)
    vals = []
    print("  %-18s %-30s %10s %10s %8s" % ("study", "event", "printed", "widest", "x"))
    for st in sorted(series, key=lambda s: EVENT_CLASS[s]):
        rows = series[st]
        printed = [r for r in rows if r["printed"]]
        if not printed:
            continue
        pr = printed[-1]
        wd = rows[0]
        rp = pr["k"] / pr["n"]
        rw = wd["k"] / wd["n"]
        mult = rp / rw if rw else float("nan")
        vals.append(mult)
        print("  %-18s %-30s %9.2f%% %9.2f%% %8.2f"
              % (st, EVENT_CLASS[st][:30], 100 * rp, 100 * rw, mult))
    vals.sort()
    print()
    print("  median multiplier %.2f, range %.2f to %.2f over %d study-events."
          % (vals[len(vals) // 2], vals[0], vals[-1], len(vals)))
    print("  Every one is >= 1.0 by construction of 'widest', but the SIZE is the point:")
    print("  the number a reader inherits is typically %.0f%% larger than the rate over the"
          % (100 * (vals[len(vals) // 2] - 1)))
    print("  study's own widest population, and for the three execution studies -- the ones")
    print("  with a real multi-stage pipeline -- the multiplier is 1.34, 1.72 and 2.06.")
    print()
    return vals


def section_pool(series):
    print("=" * 96)
    print("3. POOLING. Same numerators, two denominator conventions.")
    print("   Studies are stratified by EVENT. Pooling 'the code builds' with 'the")
    print("   number comes out again' is the error this whole record is about.")
    print("=" * 96)
    by_event = defaultdict(list)
    for st, rows in series.items():
        printed = [r for r in rows if r["printed"]]
        if not printed:
            continue
        by_event[EVENT_CLASS[st]].append((printed[-1], rows[0]))

    for event in sorted(by_event):
        pairs = by_event[event]
        if len(pairs) < 2:
            p, w = pairs[0]
            print("\n  EVENT: %s   (only one study -- no pooling)" % event)
            print("      %-18s printed %.2f%% (n=%d)  widest %.2f%% (n=%d)"
                  % (p["study"], 100 * p["k"] / p["n"], p["n"],
                     100 * w["k"] / w["n"], w["n"]))
            continue
        print("\n  EVENT: %s   (%d studies)" % (event, len(pairs)))
        for tag, idx in (("as printed", 0), ("widest denominator", 1)):
            rows = [pr[idx] for pr in pairs]
            res = pool(rows, use_deff=True)
            show_pool(res, tag + " (clustering-corrected)")
        rows = [pr[0] for pr in pairs]
        res = pool(rows, use_deff=False)
        show_pool(res, "as printed (NO clustering correction)")
    print()


def section_range(series):
    print("=" * 96)
    print("4. THE COMPARISON THAT MATTERS: within-study spread vs between-study spread.")
    print("=" * 96)
    print("  For each study, the spread its OWN funnel supports (widest to narrowest")
    print("  denominator, same numerator), against the spread BETWEEN studies at a")
    print("  fixed denominator convention. Both on the log-odds scale.")
    print()
    within = []
    for st, rows in series.items():
        if len(rows) < 2:
            continue
        ps = [r["k"] / r["n"] for r in rows]
        lo, hi = min(ps), max(ps)
        within.append((st, logit(hi) - logit(lo)))
    within.sort(key=lambda t: -t[1])
    print("  WITHIN-study log-odds range from denominator choice alone:")
    for st, d in within:
        print("      %-18s %5.2f  (a factor of %.1f in odds)" % (st, d, math.exp(d)))
    med_within = sorted(d for _, d in within)[len(within) // 2]
    print("      median %.2f" % med_within)
    print()
    for tag, idx in (("as printed", 0), ("widest", 1)):
        for event in ("runs", "builds", "reported result recovered"):
            rows = []
            for st, rr in series.items():
                if EVENT_CLASS[st] != event:
                    continue
                pr = [r for r in rr if r["printed"]]
                if not pr:
                    continue
                rows.append(pr[-1] if idx == 0 else rr[0])
            if len(rows) < 2:
                continue
            ps = [r["k"] / r["n"] for r in rows]
            d = logit(max(ps)) - logit(min(ps))
            print("  BETWEEN studies, event=%-28s %-10s log-odds range %5.2f (factor %.1f)"
                  % (event, tag, d, math.exp(d)))
    print()
    print("  READ THIS CAREFULLY. If the within-study range is of the same order as")
    print("  the between-study range, then 'field X reproduces at r%%' carries about as")
    print("  much information as 'the analyst chose a denominator'.")
    print()


def section_sensitivity(series):
    print("=" * 96)
    print("5. SENSITIVITY: drop the study I only have an abstract for.")
    print("=" * 96)
    for drop in (False, True):
        rows = []
        for st, rr in series.items():
            if EVENT_CLASS[st] != "reported result recovered":
                continue
            if drop and st in ABSTRACT_ONLY:
                continue
            pr = [r for r in rr if r["printed"]]
            if pr:
                rows.append(pr[-1])
        if len(rows) < 2:
            continue
        res = pool(rows, use_deff=True)
        show_pool(res, ("without stodden2018" if drop else "with stodden2018")
                  + "  [event = reported result recovered]")
    print()


def section_citation_drift():
    print("=" * 96)
    print("6. CITATION DRIFT, three documented cases found while reading these sources.")
    print("=" * 96)
    cases = [
        ("Pimentel et al. 2019 -> Collberg & Proebsting",
         "Pimentel: 'our 24.11% is close to the reproducibility rate of 24.9% that "
         "Collberg et al. achieved'. The TR I read reports 32.3% / 48.3% / 54.0% of "
         "402 code-backed papers; 24.9% is from the superseded 2014 version they cite. "
         "And the events differ: a C/C++ project BUILDING vs a notebook RUNNING."),
        ("Trisovic et al. 2022 -> Chang & Li 2015",
         "Trisovic: 'They successfully reproduced 33% of the results without contacting "
         "the authors and 43% with the authors' assistance.' Chang & Li's own abstract "
         "says 29 of 59 = 49% with assistance; 43% is 29/67, a denominator the citing "
         "authors substituted silently. Both defensible; neither flagged."),
        ("Samuel & Mietchen 2024, internally",
         "The abstract's narrative implies 1203/10388 = 11.6%; the Results print 7.61% "
         "(1203/15818); the corpus rate is 4.4% (1203/27271). All three are in the same "
         "paper and all three are correct."),
    ]
    for title, body in cases:
        print("\n  %s" % title)
        for i in range(0, len(body), 92):
            print("      " + body[i:i + 92])
    print()
    print("  Three cases, all found in one reading pass, in a literature whose subject")
    print("  is other people's numerical carelessness. The mechanism is not carelessness:")
    print("  it is that a proportion travels without its denominator.")
    print()


def section_synthetic():
    """Rule 3: feed the machinery a case whose answer is known, in both directions.

    (a) k studies drawn from ONE true proportion, with the wildly unequal sample
        sizes this collection actually has. The pooled estimate must land on the
        truth and tau^2 must be near zero.
    (b) k studies drawn from proportions that genuinely DIFFER. tau^2 must be
        large. If (b) does not separate from (a), the estimator cannot see
        heterogeneity and none of section 3 means anything.
    (c) One true proportion, but each study reports it over a denominator inflated
        by a random multiplier in the range measured in section 2. This is the
        situation I claim the literature is in. The pooled estimate must be biased
        upward and tau^2 must be spuriously large.
    """
    import random
    rng = random.Random(20260824)
    NS = [174, 204, 402, 601, 7621, 27271, 1159166]     # the real spread of sizes
    print("=" * 96)
    print("7. DOES THE POOLING MACHINERY WORK? Three synthetic cases with known answers.")
    print("=" * 96)

    def draw(n, p):
        return sum(1 for _ in range(min(n, 20000)) if rng.random() < p) * (n / min(n, 20000))

    def run(rows, tag, truth):
        res = pool(rows, use_deff=False)
        d = res["DL"]
        print("     %-46s pooled %5.1f%%  tau=%.2f  I2=%4.1f%%   truth %.1f%%"
              % (tag, 100 * d["pooled"], math.sqrt(d["tau2"]), 100 * res["I2"], 100 * truth))

    TRUE = 0.12
    print("\n  (a) homogeneous: every study really is %.0f%%" % (100 * TRUE))
    for rep in range(3):
        rows = [{"study": "s%d" % i, "n": n, "k": int(round(draw(n, TRUE))), "clusters": None}
                for i, n in enumerate(NS)]
        run(rows, "replicate %d" % (rep + 1), TRUE)

    print("\n  (b) genuinely heterogeneous: true rates 4%% to 40%%")
    trues = [0.04, 0.06, 0.10, 0.15, 0.22, 0.30, 0.40]
    for rep in range(3):
        rows = [{"study": "s%d" % i, "n": n, "k": int(round(draw(n, t))), "clusters": None}
                for i, (n, t) in enumerate(zip(NS, trues))]
        run(rows, "replicate %d" % (rep + 1), sum(trues) / len(trues))

    print("\n  (c) homogeneous truth %.0f%%, but each study prints it over a denominator"
          % (100 * TRUE))
    print("      shrunk by a random factor in [1.0, 2.1] -- the multipliers measured in")
    print("      section 2. This is the situation I claim the literature is in.")
    for rep in range(3):
        rows = []
        for i, n in enumerate(NS):
            k = int(round(draw(n, TRUE)))
            mult = rng.uniform(1.0, 2.1)
            rows.append({"study": "s%d" % i, "n": max(int(n / mult), k + 1), "k": k,
                         "clusters": None})
        run(rows, "replicate %d" % (rep + 1), TRUE)
    print("\n  If (a) sits on the truth with tau near 0, (b) shows a large tau, and (c) is")
    print("  biased upward with a spuriously large tau, the machinery is behaving and the")
    print("  section-3 contrast between 'as printed' and 'widest' is readable.")
    print()


def section_icc_sensitivity(series):
    """The ICC of 0.435 is measured on ONE corpus (samuel2024, 2021) and applied to
    trisovic2022 and pimentel2019 by assumption. How much does that assumption
    matter?"""
    global ICC
    print("=" * 96)
    print("8. HOW MUCH DOES THE BORROWED ICC MATTER?")
    print("=" * 96)
    print("  ICC = 0.435 is measured on the Samuel & Mietchen corpus and ASSUMED for")
    print("  Trisovic (files in packages) and Pimentel (notebooks in repositories).")
    print("  Sweeping it:")
    print()
    saved = ICC
    rows_printed, rows_widest = [], []
    for st, rr in series.items():
        if EVENT_CLASS[st] != "runs":
            continue
        pr = [r for r in rr if r["printed"]]
        if pr:
            rows_printed.append(pr[-1])
            rows_widest.append(rr[0])
    print("  %6s | %-34s | %-34s" % ("ICC", "pooled AS PRINTED [95% CI]", "pooled WIDEST [95% CI]"))
    for icc in (0.0, 0.2, 0.435, 0.7, 1.0):
        ICC = icc
        a = pool(rows_printed, use_deff=True)["DL"]
        b = pool(rows_widest, use_deff=True)["DL"]
        print("  %6.3f | %5.1f%% [%4.1f, %4.1f]  tau=%.2f      | %5.1f%% [%4.1f, %4.1f]  tau=%.2f"
              % (icc, 100 * a["pooled"], 100 * a["lo"], 100 * a["hi"], math.sqrt(a["tau2"]),
                 100 * b["pooled"], 100 * b["lo"], 100 * b["hi"], math.sqrt(b["tau2"])))
    ICC = saved
    print()
    print("  The point estimates barely move -- clustering widens intervals, it does not")
    print("  shift proportions. So the headline contrast (printed ~21%% vs widest ~12%%)")
    print("  does NOT depend on the borrowed ICC, and the intervals do.")
    print()


def main():
    series = load()
    section_funnels(series)
    section_multiplier(series)
    section_pool(series)
    section_range(series)
    section_sensitivity(series)
    section_citation_drift()
    section_synthetic()
    section_icc_sensitivity(series)


if __name__ == "__main__":
    main()
