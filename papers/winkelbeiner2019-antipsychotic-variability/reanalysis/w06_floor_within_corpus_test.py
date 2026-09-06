"""w06 -- test the floor mechanism against the data instead of against a simulation.

w05 corrects each published VR by a factor computed from a truncated-normal model.
That model could be wrong in ways a simulation cannot reveal, because the simulation
is the model. So: does the mechanism leave a fingerprint in the OBSERVED data?

THE PREDICTION. If a floor compresses an arm's SD, then trials with LESS headroom
should show LOWER lnVR, and by a specific amount. For trial i compute the predicted
log bias

    pred_i = log f(z_treated,i) - log f(z_control,i),
    z_arm,i = (baseline_i - mean change_arm,i) / SD change_arm,i

and regress the observed lnVR_i on pred_i. Under the mechanism the slope is 1. Under
no mechanism it is 0. The estimator has its own scale, as always, so both anchors are
simulated rather than assumed.

DATA. This needs a per-trial baseline mean, which the antipsychotic deposit does not
contain (that is the parameter w05 had to sweep). The antidepressant corpus does
contain it, so the test runs there: 68 HAMD17 trials from
`ploderl2019-personalised-antidepressants/reanalysis/dat.csv`, floor at 0.

It is a test of the MECHANISM, on the corpus that can support it. If the mechanism is
real in one bounded scale it is real in the other, and the antipsychotic correction
stands or falls with it.
"""
import csv
import io
import json
import os
import sys

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "tools"))
import statlib  # noqa: E402

RNG = np.random.default_rng(60606)
NSIM = 200000
_CACHE = {}


def f_shrink(z, h_disp):
    key = (round(float(z), 3), round(float(h_disp), 3))
    if key not in _CACHE:
        x = RNG.normal(0.0, 1.0, NSIM)
        h = np.full(NSIM, key[0]) if key[1] <= 0 else RNG.normal(key[0], key[1], NSIM)
        _CACHE[key] = float(np.minimum(x, h).std(ddof=1))
    return _CACHE[key]


def load():
    p = os.path.join(HERE, "..", "..",
                     "ploderl2019-personalised-antidepressants", "reanalysis",
                     "dat.csv")
    rr = []
    with io.open(p, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter=";"):
            if r["scale"] != "HAMD17" or not r["baseline"]:
                continue
            try:
                rr.append(dict(m1=float(r["all_m"]), m2=float(r["placebo_m"]),
                               s1=float(r["all_sd"]), s2=float(r["placebo_sd"]),
                               n1=float(r["all_n"]), n2=float(r["placebo_n"]),
                               b=float(r["baseline"])))
            except ValueError:
                continue
    return rr


def predicted_bias(b, m1, s1, m2, s2, h_disp):
    zt = (b - m1) / s1
    zc = (b - m2) / s2
    return np.array([np.log(f_shrink(a, h_disp)) - np.log(f_shrink(c, h_disp))
                     for a, c in zip(zt, zc)]), zt, zc


def main():
    rr = load()
    g = lambda k: np.array([r[k] for r in rr], float)
    n1, s1, m1 = g("n1"), g("s1"), g("m1")
    n2, s2, m2 = g("n2"), g("s2"), g("m2")
    b = g("b")
    H_DISP = 0.6
    print("HAMD17, k = %d trials with a reported baseline mean" % len(rr))
    pred, zt, zc = predicted_bias(b, m1, s1, m2, s2, H_DISP)
    print("  headroom z: treated median %.2f (range %.2f to %.2f), control median %.2f"
          % (np.median(zt), zt.min(), zt.max(), np.median(zc)))
    print("  predicted per-trial log bias: median %+.4f, range %+.4f to %+.4f"
          % (np.median(pred), pred.min(), pred.max()))

    y, v = statlib.lnvr(s1, n1, s2, n2)
    obs = stats.linregress(pred, y)
    print()
    print("  OBSERVED slope of lnVR on the predicted bias = %+.3f (SE %.3f, r %+.3f, "
          "p %.3f)" % (obs.slope, obs.stderr, obs.rvalue, obs.pvalue))

    def simulate(with_floor, B=300, recompute=True):
        """B replicates. `recompute` rebuilds the regressor from each replicate's OWN
        simulated SDs and means, which is what happens on the real data.

        THIS IS THE WHOLE TEST. z = (baseline - mean change) / SD, so the regressor
        CONTAINS the same arm SDs as lnVR = log(s1/s2): a trial that draws a large s1
        gets a smaller z_treated and hence a more negative predicted bias, while its
        lnVR goes up. That coupling is present in the real data by construction and
        must therefore be present in the null. Holding `pred` fixed at its observed
        value across replicates -- which is what the first version of this script did
        -- breaks the coupling in the null only, and manufactures a spurious result.
        The first run reported an observed slope of -1.197 against a null of +0.010,
        p < 0.001, "inconsistent with both". That number was an artifact of the null,
        not a finding about the world.
        """
        out = []
        for _ in range(B):
            S1, S2, M1, M2 = [], [], [], []
            for i in range(len(rr)):
                for nn, mm, sstore, mstore in ((n1[i], m1[i], S1, M1),
                                               (n2[i], m2[i], S2, M2)):
                    ch = RNG.normal(mm, s2[i], int(nn))
                    if with_floor:
                        base = RNG.normal(b[i], H_DISP * s2[i], int(nn))
                        ch = np.minimum(ch, np.maximum(base, 0.0))
                    sstore.append(ch.std(ddof=1))
                    mstore.append(abs(ch.mean()))
            S1, S2 = np.array(S1), np.array(S2)
            M1, M2 = np.array(M1), np.array(M2)
            yy, _ = statlib.lnvr(S1, n1, S2, n2)
            pp = (predicted_bias(b, M1, S1, M2, S2, H_DISP)[0] if recompute
                  else pred)
            out.append(stats.linregress(pp, yy).slope)
        return np.array(out)

    a0 = simulate(False)
    a1 = simulate(True)
    print("  simulated slope, NO floor (mechanism absent)   = %+.3f [%+.3f, %+.3f]"
          % (a0.mean(), *np.percentile(a0, [2.5, 97.5])))
    print("  simulated slope, FLOOR ONLY (mechanism is all) = %+.3f [%+.3f, %+.3f]"
          % (a1.mean(), *np.percentile(a1, [2.5, 97.5])))
    # RESOLVING POWER FIRST. The rescaling divides by (a1 - a0). If the two anchors
    # are not separated by more than their own noise, that denominator is noise and
    # the ratio is meaningless however tight its bootstrap looks. Ratios of near-zero
    # quantities are not effect sizes -- my own CONTRIBUTING.md rule 3, which I broke
    # in the first version of this script by printing -2.03 as if it meant something.
    sep = a1.mean() - a0.mean()
    noise = np.sqrt(a0.std(ddof=1) ** 2 + a1.std(ddof=1) ** 2)
    print()
    print("  RESOLVING POWER: the two anchors are %+.3f apart; the spread of each is"
          % sep)
    print("  %.3f and %.3f, combined %.3f. Separation / noise = %.2f."
          % (a0.std(ddof=1), a1.std(ddof=1), noise, abs(sep) / noise))
    verdict = None
    if abs(sep) < noise:
        verdict = "NO RESOLVING POWER -- the design cannot tell the two worlds apart"
        print("  -> %s." % verdict)
        print("  The anchors' own 95% ranges overlap over most of their length, so")
        print("  rescaling the observation against them would divide by noise. NOT")
        print("  DOING IT. What this test can honestly report is: the observed slope")
        print("  %+.3f lies %.2f combined-noise units from the no-floor anchor and"
              % (obs.slope, abs(obs.slope - a0.mean()) / noise))
        print("  %.2f from the floor-only anchor, and neither distance is decisive."
              % (abs(obs.slope - a1.mean()) / noise))
        share, lo, hi = float("nan"), float("nan"), float("nan")
    else:
        share = (obs.slope - a0.mean()) / sep
        boots = []
        idx = np.arange(len(rr))
        for _ in range(4000):
            j = RNG.choice(idx, size=len(idx), replace=True)
            bb = stats.linregress(pred[j], y[j]).slope
            boots.append((bb - a0.mean()) / sep)
        lo, hi = np.percentile(boots, [2.5, 97.5])
        print("  rescaled: the observed pattern is %.2f [%.2f, %.2f] of what a"
              % (share, lo, hi))
        print("  floor-only world produces. 0 = no fingerprint, 1 = entirely the floor.")
        verdict = ("no detectable fingerprint" if lo <= 0 <= hi and hi < 1
                   else "consistent with the floor" if lo <= 1 <= hi
                   else "inconsistent with both")
        print("  verdict: %s" % verdict)
    print()
    print("  WHY IT IS SO WEAK. k = %d, and the predicted biases span only %.4f log"
          % (len(rr), pred.max() - pred.min()))
    print("  units -- about 11% -- while the per-trial lnVR sampling SD is around")
    print("  %.3f. The signal is an order of magnitude under the noise per trial, and"
          % float(np.sqrt(np.mean(v))))
    print("  68 trials do not recover that. The floor correction in w05 therefore")
    print("  remains a MODEL-BASED adjustment which this corpus cannot confirm or")
    print("  refute. Say so wherever it is quoted.")

    out = dict(k=len(rr), h_disp=H_DISP,
               observed_slope=float(obs.slope), se=float(obs.stderr),
               p=float(obs.pvalue),
               null_no_floor=float(a0.mean()),
               null_floor_only=float(a1.mean()),
               share=float(share), share_ci=[float(lo), float(hi)],
               verdict=verdict,
               pred_range=[float(pred.min()), float(pred.max())])
    with io.open(os.path.join(HERE, "out_w06.json"), "w", encoding="utf-8",
                 newline="\n") as f:
        json.dump(out, f, indent=1)
    print()
    print("wrote out_w06.json")


if __name__ == "__main__":
    main()
