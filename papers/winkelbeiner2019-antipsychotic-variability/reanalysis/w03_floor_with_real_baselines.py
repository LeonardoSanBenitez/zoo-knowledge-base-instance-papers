"""w03 -- w02 test B was the one that bit, so run it properly.

w02 simulated the PANSS floor with GUESSED baseline distributions and found that a
world with zero heterogeneity produces D between -10.9 and -23.6 depending on the
guess, against an observed -27.5 [-45.1, -10.0]. That is close enough that the guess
is doing the work, which is not acceptable.

The deposit contains each comparison's own baseline SD for 38 of 75 comparisons
(`sd0tx`, `sd0ct`). It does NOT contain baseline MEANS -- so one parameter has to
come from outside, and the honest thing is to sweep it and report where the answer
changes rather than pick a value.

    for each comparison i and arm a:
        baseline_ij ~ N(mu_b, sd0_ia)          sd0 from the deposit where available,
                                               otherwise the corpus median
        change_ij   ~ N(m_ia, s_i)             SAME change SD in both arms
                                               => sigma_TE = 0 exactly
        change_ij   = min(change_ij, baseline_ij - 30)     PANSS cannot go below 30

Then pool D exactly as on the real data and compare. The question is not "does a floor
exist" -- it does -- but "does a floor of the size this scale actually imposes account
for the observed deficit at the baseline severities these trials actually recruited".

Also fixes w02 test C, which divided by control-arm mean changes as small as 0.4 and
produced a meaningless 12,675. The sign was right and the magnitude was noise.
"""
import csv
import io
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "tools"))
import statlib  # noqa: E402

CSV = os.path.join(HERE, "..", "artifacts", "response.csv")
FLOOR = 30.0


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def load():
    rows = []
    with io.open(CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            v = {k: num(r.get(k)) for k in
                 ("mu1tx", "mu1ct", "sd1tx", "sd1ct", "ntx", "nct",
                  "sd0tx", "sd0ct")}
            if any(v[k] is None for k in
                   ("mu1tx", "mu1ct", "sd1tx", "sd1ct", "ntx", "nct")):
                continue
            v["id"] = r["id"]
            rows.append(v)
    return rows


def A(rows, k):
    return np.array([r[k] for r in rows], float)


def pooled_D(s1, n1, s2, n2):
    d, v = statlib.var_diff(s1, n1, s2, n2, weight="pooled")
    return statlib.re_meta(d, v, method="PM")


def main():
    rows = load()
    n1, s1, m1 = A(rows, "ntx"), A(rows, "sd1tx"), np.abs(A(rows, "mu1tx"))
    n2, s2, m2 = A(rows, "nct"), A(rows, "sd1ct"), np.abs(A(rows, "mu1ct"))
    obs = pooled_D(s1, n1, s2, n2)
    print("observed D = %+.3f [%+.3f, %+.3f] PANSS points^2 (k = %d)"
          % (obs["mu"], obs["ci"][0], obs["ci"][1], obs["k"]))

    b_tx = np.array([r["sd0tx"] if r["sd0tx"] else np.nan for r in rows])
    b_ct = np.array([r["sd0ct"] if r["sd0ct"] else np.nan for r in rows])
    med0 = float(np.nanmedian(np.concatenate([b_tx, b_ct])))
    print("baseline SDs reported for %d of %d comparisons; median %.2f points"
          % (int(np.sum(np.isfinite(b_tx))), len(rows), med0))
    b_tx = np.where(np.isfinite(b_tx), b_tx, med0)
    b_ct = np.where(np.isfinite(b_ct), b_ct, med0)
    print("n-weighted mean symptom reduction: treated %.2f, control %.2f points"
          % (np.average(m1, weights=n1), np.average(m2, weights=n2)))
    print("median change ratio treated/control = %.3f  (the MEAN of that ratio is "
          "3.45 and is meaningless: some control arms changed by 0.4 points)"
          % float(np.median(m1 / m2)))

    rng = np.random.default_rng(30303)
    out = {"observed": dict(D=obs["mu"], ci=list(obs["ci"]))}

    print()
    print("=== the floor, with each trial's own baseline SD, sweeping baseline mean ===")
    print("  every simulated world has sigma_TE = 0 EXACTLY: the change SD is the same")
    print("  in both arms before the floor is applied.")
    print("  %-14s %-26s %-22s" % ("baseline mean", "D from a null world",
                                   "share of observed -27.5"))
    B = 200
    for mu_b in (75, 80, 85, 90, 95, 100):
        Ds = []
        for _ in range(B):
            e1, e2 = [], []
            for i in range(len(rows)):
                for nn, mm, sd0, store in ((n1[i], m1[i], b_tx[i], e1),
                                           (n2[i], m2[i], b_ct[i], e2)):
                    base = rng.normal(mu_b, sd0, int(nn))
                    ch = rng.normal(mm, s2[i], int(nn))
                    ch = np.minimum(ch, np.maximum(base - FLOOR, 0.0))
                    store.append(ch.std(ddof=1))
            Ds.append(pooled_D(np.array(e1), n1, np.array(e2), n2)["mu"])
        Ds = np.array(Ds)
        lo, hi = np.percentile(Ds, [2.5, 97.5])
        print("  %-14d %+7.2f  [%+7.2f, %+7.2f]   %5.0f%%"
              % (mu_b, Ds.mean(), lo, hi, 100 * Ds.mean() / obs["mu"]))
        out.setdefault("floor_sweep", {})[str(mu_b)] = dict(
            mean=float(Ds.mean()), ci=[float(lo), float(hi)])

    print()
    print("=== how often does the floor actually bind? ===")
    print("  fraction of simulated patients whose change was capped:")
    for mu_b in (80, 90, 95):
        cap1 = cap2 = tot1 = tot2 = 0
        for i in range(len(rows)):
            for nn, mm, sd0, which in ((n1[i], m1[i], b_tx[i], 1),
                                       (n2[i], m2[i], b_ct[i], 2)):
                base = rng.normal(mu_b, sd0, int(nn))
                ch = rng.normal(mm, s2[i], int(nn))
                c = int(np.sum(ch > np.maximum(base - FLOOR, 0.0)))
                if which == 1:
                    cap1 += c; tot1 += int(nn)
                else:
                    cap2 += c; tot2 += int(nn)
        print("    baseline mean %d:  treated %.2f%%, control %.2f%%  (difference "
              "%.2f points of percentage)"
              % (mu_b, 100.0 * cap1 / tot1, 100.0 * cap2 / tot2,
                 100.0 * cap1 / tot1 - 100.0 * cap2 / tot2))
        out.setdefault("capped_fraction", {})[str(mu_b)] = dict(
            treated=cap1 / tot1, control=cap2 / tot2)

    print()
    print("=== the same sweep on the ANTIDEPRESSANT corpus, as a control ===")
    print("  HAMD17 runs 0-52 with a floor at 0 and mean reductions of 9-11 points")
    print("  from a baseline near 22-25, so the floor sits about 3 SD away and should")
    print("  do almost nothing. If the mechanism is real it must be corpus-specific.")
    ad = os.path.join(HERE, "..", "..",
                      "ploderl2019-personalised-antidepressants", "reanalysis",
                      "dat.csv")
    if os.path.exists(ad):
        rr = []
        with io.open(ad, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter=";"):
                if r["scale"] != "HAMD17":
                    continue
                try:
                    rr.append(dict(n1=float(r["all_n"]), s1=float(r["all_sd"]),
                                   m1=float(r["all_m"]), n2=float(r["placebo_n"]),
                                   s2=float(r["placebo_sd"]),
                                   m2=float(r["placebo_m"]),
                                   base=float(r["baseline"])))
                except ValueError:
                    continue
        an1 = np.array([r["n1"] for r in rr]); as1 = np.array([r["s1"] for r in rr])
        am1 = np.array([r["m1"] for r in rr]); an2 = np.array([r["n2"] for r in rr])
        as2 = np.array([r["s2"] for r in rr]); am2 = np.array([r["m2"] for r in rr])
        ab = np.array([r["base"] for r in rr])
        real = pooled_D(as1, an1, as2, an2)
        Ds = []
        for _ in range(B):
            e1, e2 = [], []
            for i in range(len(rr)):
                for nn, mm, store in ((an1[i], am1[i], e1), (an2[i], am2[i], e2)):
                    base = rng.normal(ab[i], as2[i], int(nn))
                    ch = rng.normal(mm, as2[i], int(nn))
                    ch = np.minimum(ch, np.maximum(base, 0.0))
                    store.append(ch.std(ddof=1))
            Ds.append(pooled_D(np.array(e1), an1, np.array(e2), an2)["mu"])
        Ds = np.array(Ds)
        print("  HAMD17 k=%d: observed D %+.3f [%+.3f, %+.3f]; floor-only null "
              "%+.3f [%+.3f, %+.3f]"
              % (len(rr), real["mu"], real["ci"][0], real["ci"][1], Ds.mean(),
                 *np.percentile(Ds, [2.5, 97.5])))
        out["antidepressant_floor_control"] = dict(
            observed=real["mu"], null_mean=float(Ds.mean()),
            null_ci=[float(x) for x in np.percentile(Ds, [2.5, 97.5])])

    with io.open(os.path.join(HERE, "out_w03.json"), "w", encoding="utf-8",
                 newline="\n") as f:
        json.dump(out, f, indent=1)
    print()
    print("wrote out_w03.json")


if __name__ == "__main__":
    main()
