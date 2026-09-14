"""F8. The ratio this record has been quoting, recomputed for all six hypotheses, and a
correction to how I computed it.

NOTES.md (2026-08-12) carries, for '#fincap RT-H1':
    tau = sqrt((IQR/1.349)^2 - medianSE^2),   tau / medianSE = 1.72
That recipe is mine, not Menkveld et al.'s -- they compare NSE and SE as magnitudes and
do not subtract. **The subtraction is wrong for a same-data design.** All 164 teams
analyse the SAME dataset, so their estimates are not independent draws and there is no
sampling variance across teams to remove; the whole observed spread IS the nonstandard
error. The recipe announces its own failure: on three of the six hypotheses the quantity
under the square root is NEGATIVE.

Reported here: NSE/medianSE directly, per hypothesis, and the minimum rank correlation
this design can resolve.
"""
import sys, os, json
import numpy as np
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import f0_load


def main():
    d = f0_load.results()
    out = {'per_hypothesis': {}}
    print(f"{'hyp':>3} {'NSE=IQR/1.349':>14} {'medianSE':>10} {'NSE/medSE':>10} "
          f"{'tau^2 sign':>11} {'tau/medSE':>10}")
    ratios = []
    for h in range(1, 7):
        g = d[(d.hyp == h) & (d.stage == 1)]
        e = g['estimate'].values
        nse = float((np.percentile(e, 75) - np.percentile(e, 25)) / 1.349)
        mse = float(np.median(g['se'].values))
        inner = nse ** 2 - mse ** 2
        tau = float(np.sqrt(inner)) if inner > 0 else None
        ratios.append(nse / mse)
        out['per_hypothesis'][str(h)] = dict(
            nse=nse, median_se=mse, nse_over_median_se=float(nse / mse),
            tau_squared=float(inner),
            tau_over_median_se=(float(tau / mse) if tau else None))
        print(f"{h:3d} {nse:14.4f} {mse:10.4f} {nse/mse:10.3f} "
              f"{'positive' if inner > 0 else 'NEGATIVE':>11} "
              f"{(tau/mse if tau else float('nan')):10.3f}")
    out['nse_over_median_se_summary'] = dict(
        per_hyp=[round(float(x), 4) for x in ratios],
        median=float(np.median(ratios)), min=float(min(ratios)), max=float(max(ratios)),
        n_hyp_with_negative_tau_squared=int(sum(
            1 for v in out['per_hypothesis'].values() if v['tau_squared'] <= 0)))
    print(f"\nNSE/medianSE across the six hypotheses: "
          f"median {np.median(ratios):.3f}, range {min(ratios):.3f} to {max(ratios):.3f}")
    print(f"tau^2 negative on {out['nse_over_median_se_summary']['n_hyp_with_negative_tau_squared']} "
          f"of 6 hypotheses -- which is the recipe telling us it does not apply here")

    # resolving power of the team-level rank correlations in f7
    n = 164
    zc = stats.norm.ppf(0.975)
    rho_sig = float(np.tanh(zc / np.sqrt(n - 3)))
    rho_80 = float(np.tanh((zc + stats.norm.ppf(0.80)) / np.sqrt(n - 3)))
    out['team_level_resolving_power'] = dict(
        n=n, smallest_significant_rho=rho_sig, rho_at_80pct_power=rho_80)
    print(f"\nat n = {n} teams a rank correlation reaches p < 0.05 at |rho| = "
          f"{rho_sig:.3f} and 80% power at |rho| = {rho_80:.3f}. "
          f"Any null below that is 'cannot tell'.")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                           'artifacts', 'f8_nse_over_se.json'), 'w') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()
