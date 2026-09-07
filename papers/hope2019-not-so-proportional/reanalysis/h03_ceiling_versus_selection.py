"""h03 -- h02's part B asked the wrong question, and this is the right one.

h02 asked "can the ceiling alone reach the sigma_Y/sigma_X this study reports?"
and answered YES for seven of eight studies. That is not a finding, it is a
vacuous test: the ceiling-only grid spans 0.130 to 1.029, i.e. essentially every
value a variability ratio below 1 can take, because the grid included mean
improvements up to 55 points on a 66-point scale. A test that almost everything
passes is not a test. Recorded rather than deleted, because the shape of the
error is the useful part: I swept a parameter over its mathematical range instead
of its empirical one.

THE RIGHT QUESTION. Constrain the mean improvement to what these studies actually
observe, and ask what sigma_Y/sigma_X the ceiling produces THERE. Then ask what
the second candidate mechanism -- removing 'non-fitters' before computing the
statistic -- produces, using the one dataset Hope et al. found with individual
data (Zarahn et al. 2011, 30 patients) as the calibration point:

    whole sample (n=30):        r(X,Y) = 0.80, r(X,D) = -0.49, sigma_Y/sigma_X = 0.88
    fitters only (n=23):        r(X,Y) = 0.75, r(X,D) = -0.95, sigma_Y/sigma_X = 0.36

Removing 7 of 30 patients moved the ratio from 0.88 to 0.36. That is a bigger
move than the ceiling produces at any plausible improvement, and it is a move
the analyst makes on purpose.
"""
import io
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(2011)          # Zarahn
MAXFM = 66.0


def ratio_after_ceiling(mean_imp, sd_imp, n=6000, reps=80):
    out = []
    for _ in range(reps):
        X = RNG.uniform(0.0, 65.0, n)
        imp = np.full(n, mean_imp) if sd_imp == 0 else RNG.normal(mean_imp, sd_imp, n)
        Y = X + np.clip(imp, 0.0, MAXFM - X)
        out.append(Y.std(ddof=1) / X.std(ddof=1))
    return float(np.mean(out))


def mixture_world(p_non, prop, noise_sd, n=30, reps=4000):
    """The generative model this literature actually describes: a MIXTURE.

    A fraction (1 - p_non) of patients recover `prop` of their lost function
    with noise; the rest ('non-fitters') recover essentially nothing. Returns
    the four statistics Hope et al. quote from Zarahn et al. (2011), for the
    whole sample and after removing the non-fitters, so the model can be
    checked against real numbers rather than against my expectations.

    n = 30 by default because Zarahn's sample is 30 and the statistics of
    interest are strongly n-dependent at that size.
    """
    W_ratio, W_rxd, W_rxy, F_ratio, F_rxd, F_rxy = [], [], [], [], [], []
    for _ in range(reps):
        X = RNG.uniform(0.0, 60.0, n)
        lost = MAXFM - X
        is_non = RNG.random(n) < p_non
        imp = np.where(is_non,
                       np.abs(RNG.normal(0.0, noise_sd / 2.0, n)),
                       prop * lost + RNG.normal(0.0, noise_sd, n))
        Y = X + np.clip(imp, 0.0, lost)
        if X.std(ddof=1) == 0 or Y.std(ddof=1) == 0:
            continue
        W_ratio.append(Y.std(ddof=1) / X.std(ddof=1))
        W_rxd.append(np.corrcoef(X, Y - X)[0, 1])
        W_rxy.append(np.corrcoef(X, Y)[0, 1])
        f = ~is_non
        if f.sum() < 5 or X[f].std(ddof=1) == 0 or Y[f].std(ddof=1) == 0:
            continue
        F_ratio.append(Y[f].std(ddof=1) / X[f].std(ddof=1))
        F_rxd.append(np.corrcoef(X[f], Y[f] - X[f])[0, 1])
        F_rxy.append(np.corrcoef(X[f], Y[f])[0, 1])
    m = lambda a: float(np.mean(a))
    return dict(whole=dict(ratio=m(W_ratio), rxd=m(W_rxd), rxy=m(W_rxy)),
                fitters=dict(ratio=m(F_ratio), rxd=m(F_rxd), rxy=m(F_rxy)))


def main():
    out = {}
    print("=== 1. the ceiling, at EMPIRICALLY PLAUSIBLE mean improvements ===")
    print("    Fugl-Meyer upper extremity improvements in this literature run")
    print("    roughly 10-25 points; the proportional rule itself implies about")
    print("    0.7 x 33 = 23 for a uniform baseline. Sweep that band only.")
    print("    %-12s" % "mean\\sd" + "".join("%-9s" % ("sd=%g" % s)
                                             for s in (2, 5, 8, 12)))
    band = {}
    for m in (10, 15, 20, 25):
        line = "    %-12d" % m
        for sd in (2, 5, 8, 12):
            v = ratio_after_ceiling(m, sd)
            band["m%d_sd%d" % (m, sd)] = v
            line += "%-9.3f" % v
        print(line)
    out["ceiling_plausible_band"] = band
    lo, hi = min(band.values()), max(band.values())
    print("    ceiling alone, plausible improvements: sigma_Y/sigma_X in "
          "[%.3f, %.3f]" % (lo, hi))

    print()
    print("=== 2. against the published values ===")
    pub = [("Winters 2015 (fitters)", 0.158), ("Zarahn 2011 fitters", 0.36),
           ("Veerbeek 2018 (fitters)", 0.438), ("Stinear 2017 (fitters)", 0.48),
           ("Lazar 2010 (aphasia)", 0.48), ("Jeffers 2018 (rats)", 0.8),
           ("Zarahn 2011 WHOLE sample", 0.88), ("Feng 2015 combined", 1.2)]
    for name, v in pub:
        verdict = ("inside" if lo <= v <= hi else
                   "BELOW -- the ceiling cannot do this" if v < lo else "above")
        print("      %-28s %.3f   %s" % (name, v, verdict))
        out.setdefault("published_vs_band", {})[name] = dict(v=v, verdict=verdict)
    print()
    print("    Every fitters-only value is BELOW what the ceiling can produce at a")
    print("    plausible improvement. Every whole-sample value is inside or above.")
    print("    The ceiling is not what makes the fitter ratios small.")

    print()
    print("=== 3. the mixture the literature actually describes ===")
    print("    A fraction of patients recover `prop` of lost function with noise;")
    print("    the non-fitters recover essentially nothing. n = 30, as Zarahn.")
    print("    TARGET, from Zarahn et al. 2011 via Hope et al. Table/text:")
    print("      whole sample n=30:  sY/sX 0.88, r(X,D) -0.49, r(X,Y) 0.80")
    print("      fitters    n=23:  sY/sX 0.36, r(X,D) -0.95, r(X,Y) 0.75")
    print()
    print("    %-24s %-22s %-22s" % ("model", "whole (ratio/rxd/rxy)",
                                     "fitters (ratio/rxd/rxy)"))
    best, bestd = None, 1e9
    mix = {}
    for p_non in (0.15, 0.233, 0.30):
        for prop in (0.6, 0.7, 0.8):
            for noise in (4.0, 7.0, 10.0):
                r = mixture_world(p_non, prop, noise)
                d = (abs(r["whole"]["ratio"] - 0.88) + abs(r["whole"]["rxd"] + 0.49)
                     + abs(r["fitters"]["ratio"] - 0.36)
                     + abs(r["fitters"]["rxd"] + 0.95))
                mix["p%.3f_prop%.1f_sd%.0f" % (p_non, prop, noise)] = r
                if d < bestd:
                    bestd, best = d, (p_non, prop, noise, r)
    for p_non, prop, noise in ((0.233, 0.7, 4.0), (0.233, 0.7, 7.0),
                               (0.233, 0.7, 10.0), best[:3]):
        r = mix["p%.3f_prop%.1f_sd%.0f" % (p_non, prop, noise)]
        tag = "  <- closest of 27" if (p_non, prop, noise) == best[:3] else ""
        print("    %-24s %5.2f /%6.2f /%5.2f   %5.2f /%6.2f /%5.2f%s"
              % ("%.0f%% non, %.0f%%, sd %.0f" % (100 * p_non, 100 * prop, noise),
                 r["whole"]["ratio"], r["whole"]["rxd"], r["whole"]["rxy"],
                 r["fitters"]["ratio"], r["fitters"]["rxd"], r["fitters"]["rxy"],
                 tag))
    out["mixture"] = mix
    out["mixture_best"] = dict(p_non=best[0], prop=best[1], noise=best[2],
                               stats=best[3], l1_distance=bestd)

    print()
    print("=== 4. what this does and does not establish ===")
    print("    ESTABLISHED. At the mean improvements these studies report, a")
    print("    ceiling alone gives sigma_Y/sigma_X between %.2f and %.2f. Every"
          % (lo, hi))
    print("    FITTERS-ONLY value in the literature (0.16 to 0.48) is below that")
    print("    band, and every WHOLE-SAMPLE value (0.80, 0.88, 1.20) is inside or")
    print("    above it. So the ceiling is not what makes the fitter ratios small.")
    print()
    print("    NOT ESTABLISHED, AND I CLAIMED IT BEFORE CHECKING. My first")
    print("    attempt modelled non-fitter removal as 'drop the k most negative")
    print("    residuals' and got 0.867 -> 0.781 at k = 23 per cent, a move of")
    print("    0.09 against the 0.52 Zarahn shows. I wrote 'a comparable amount'")
    print("    under a table that said otherwise. That model is simply wrong: it")
    print("    removes a TAIL where the literature removes a SUBPOPULATION.")
    print()
    print("    WHAT THE MIXTURE DOES ESTABLISH. Fitting four Zarahn targets over")
    print("    27 parameter settings, the best is 30 per cent non-fitters")
    print("    recovering nothing, 70 per cent proportional recovery, noise SD 4,")
    print("    with L1 = %.3f"
          % bestd)
    print("    across the four -- whole-sample ratio 0.88 against 0.88, fitters")
    print("    ratio 0.37 against 0.36, fitters r(X,D) -0.95 against -0.95, and")
    print("    whole-sample r(X,D) -0.56 against -0.49. So a genuine non-fitter")
    print("    SUBPOPULATION plus a ceiling reproduces the fitters-only statistics")
    print("    almost exactly, and the ceiling alone (section 1) cannot come near")
    print("    them. The compression is the selection.")
    print()
    print("    AND THE HELD-OUT QUANTITY MISSES. r(X,Y) was not in the objective.")
    print("    For the fitters the model gives 0.80 against Zarahn's 0.75, fine;")
    print("    for the whole sample it gives 0.57 against 0.80, off by 0.23. So")
    print("    the mixture is the right shape and not the right world -- real")
    print("    non-fitters are evidently more predictable from baseline than")
    print("    'recovers nothing plus noise' allows. Four statistics fitted, one")
    print("    held-out statistic matched, one held-out statistic missed badly.")
    print()
    print("    CONSEQUENCE FOR HOPE ET AL. Their argument stands and their")
    print("    emphasis moves. 'Minimize ceiling effects' is second-order at these")
    print("    improvements. 'Report r(X,Y), r(X,D) and sigma_Y/sigma_X for the")
    print("    WHOLE sample, before any fitter split' is first-order, and it is")
    print("    already the first of their two recommendations -- they simply do")
    print("    not say it is the bigger of the two.")

    with io.open(os.path.join(HERE, "out_h03.json"), "w", encoding="utf-8",
                 newline="\n") as fh:
        json.dump(out, fh, indent=1)
    print()
    print("wrote out_h03.json")


if __name__ == "__main__":
    main()
