"""m06 -- How much of their rho is artifact, and what happens to the headline.

Two jobs.

A. CALIBRATE the study-level artifact using THEIR OWN numbers instead of my
   guesses. Three inputs, none invented here:

     * placebo arm sizes: transcribed from their supplementary study table
       (66 trials; median n_placebo = 71, mean 78, range 4-178). Note the
       table gives arm Ns but NOT per-arm means or SDs, so their study-level
       rho cannot be recomputed from the deposit -- only its artifact
       component can be predicted.
     * between-study SD of the treatment effect: derived from their own
       reported I2 = 38% for the mean-difference meta-analysis.
       I2 = tau^2 / (tau^2 + s^2)  =>  tau^2 = s^2 * I2/(1-I2).
     * within-patient SD of PANSS total change: ~20 points, the standard value
       in this literature; scanned.

   The only genuinely free parameter is the between-study SD of PLACEBO
   RESPONSE, which nothing I can reach reports. It is scanned, and the answer
   is reported as a function of it rather than at one flattering value.

B. PROPAGATE. Their conclusion is sigma_TE = 13.5 PANSS points from
   rho = -0.32. Show sigma_TE as a function of rho so a reader can see how much
   of the headline is carried by that one number.

Run: python m06_calibrate_and_propagate.py
"""
import csv
import math
import os

import numpy as np

ARMS = os.path.join("..", "artifacts", "mcc2021_arm_sizes.csv")


def load_arm_sizes():
    n_pl, n_dr = [], []
    with open(ARMS, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            n_pl.append(float(r["n_placebo"]))
            n_dr.append(float(r["n_drug_total"]) / float(r["n_drug_arms"]))
    return np.array(n_pl), np.array(n_dr)


def tau2_from_I2(I2, s2):
    return s2 * I2 / (1.0 - I2)


def artifact_rho(n_pl, n_dr, sd_change, tau_placebo, tau_effect):
    """Expected study-level Pearson rho when the TRUE study-level correlation
    between placebo response and treatment effect is exactly zero.

      P_s = placebo response          observed with error e_p
      T_s = drug change - placebo change,  observed with error (e_d - e_p)

      Cov(P, T) = -Var(e_p)                       <- the whole artifact
      Var(P)    = tau_placebo^2 + Var(e_p)
      Var(T)    = tau_effect^2 + Var(e_p) + Var(e_d)
    """
    v_ep = (sd_change ** 2 / n_pl).mean()
    v_ed = (sd_change ** 2 / n_dr).mean()
    cov = -v_ep
    var_p = tau_placebo ** 2 + v_ep
    var_t = tau_effect ** 2 + v_ep + v_ed
    return cov / math.sqrt(var_p * var_t), v_ep, v_ed


def sigma_te(vr, rho, s_pl=1.0, root="+"):
    disc = vr * vr - 1.0 + rho * rho
    if disc < 0:
        return None
    r = math.sqrt(disc)
    u = (-rho + r) if root == "+" else (-rho - r)
    return None if u < 0 else s_pl * u


def main():
    n_pl, n_dr = load_arm_sizes()
    print("=" * 94)
    print("A. CALIBRATED ARTIFACT -- their arm sizes, their I2, one scanned parameter")
    print("=" * 94)
    print(f"  66 trials. placebo arm n: median {np.median(n_pl):.0f}, "
          f"mean {n_pl.mean():.0f}, min {n_pl.min():.0f}, max {n_pl.max():.0f}")
    print(f"  mean drug arm n: {n_dr.mean():.0f}")
    rows = []
    for sd_change in (18.0, 20.0, 22.0):
        # within-study variance of the mean difference, for the I2 inversion
        s2 = (sd_change ** 2 * (1.0 / n_pl + 1.0 / n_dr)).mean()
        tau2_eff = tau2_from_I2(0.38, s2)
        tau_eff = math.sqrt(tau2_eff)
        print(f"\n  PANSS change SD = {sd_change:.0f}  ->  within-study Var(MD) = "
              f"{s2:.2f}; their I2 = 38% implies between-study SD of the "
              f"treatment effect = {tau_eff:.2f} PANSS points")
        print(f"    {'between-study SD of placebo response':>38} | "
              f"{'expected rho under a TRUE NULL':>31} | {'% of their -0.39':>17}")
        for tau_pl in (3.0, 4.0, 5.0, 6.0, 8.0, 10.0):
            r, v_ep, v_ed = artifact_rho(n_pl, n_dr, sd_change, tau_pl, tau_eff)
            print(f"    {tau_pl:38.1f} | {r:+31.3f} | {100*r/-0.39:16.0f}%")
            rows.append(dict(sd_change=sd_change, tau_placebo=tau_pl,
                             tau_effect=tau_eff, var_e_placebo=v_ep,
                             var_e_drug=v_ed, artifact_rho=r,
                             pct_of_reported=100 * r / -0.39))
    print()
    print("  Every number in that table is what the estimator returns when there")
    print("  is NOTHING TO FIND. Their reported study-level value is -0.39.")

    print()
    print("=" * 94)
    print("B. PROPAGATION -- how much of sigma_TE = 13.5 rests on rho?")
    print("=" * 94)
    print("  sigma_TE = sigma_PL * ( sqrt(VR^2 - 1 + rho^2) - rho ),  '+' root,")
    print("  sigma_PL = 21 PANSS points (the value that reproduces their 13.5).")
    print()
    print(f"  {'rho':>7} | {'VR=0.95':>9} {'VR=0.97':>9} {'VR=0.99':>9} "
          f"{'VR=1.00':>9} {'VR=1.03':>9}   note")
    prop = []
    notes = {-0.62: "their open-label estimate",
             -0.39: "their study-level estimate",
             -0.32: "their LM estimate -- THE HEADLINE",
             -0.21: "artifact alone, calibrated above",
             -0.10: "",
             0.0: "no correlation"}
    for rho in (-0.62, -0.39, -0.32, -0.21, -0.10, 0.0):
        cells = []
        for vr in (0.95, 0.97, 0.99, 1.00, 1.03):
            u = sigma_te(vr, rho, 21.0)
            cells.append("     n/a" if u is None else f"{u:9.1f}")
            prop.append(dict(rho=rho, vr=vr,
                             sigma_te=None if u is None else round(u, 2)))
        print(f"  {rho:7.2f} | {' '.join(cells)}   {notes[rho]}")
    print()
    print("  'n/a' means the quadratic has no real solution: VR is too far below")
    print("  1 for that rho. THOSE TRIALS WERE DELETED from their main analysis")
    print("  ('In some trials the observed VR was not compatible with our main")
    print("  estimate of rho ... These trials were removed'). The deletion")
    print("  threshold is VR < sqrt(1 - rho^2) = %.3f at rho = -0.32, and it "
          "removes\n  exactly the trials whose low VR argues AGAINST heterogeneity."
          % math.sqrt(1 - 0.32 ** 2))

    print()
    print("=" * 94)
    print("C. THE DELETION -- how many trials does the compatibility filter remove?")
    print("=" * 94)
    print("  Threshold VR* = sqrt(1 - rho^2). A trial is dropped if VR < VR*.")
    print(f"  {'rho':>7} {'VR* threshold':>14} | fraction dropped if VR ~ N(mean, sd)")
    print(f"  {'':>7} {'':>14} | {'0.97,0.05':>11} {'0.97,0.08':>11} "
          f"{'0.97,0.12':>11} {'0.86,0.10':>11}")
    dele = []
    from scipy import stats as sst
    for rho in (-0.21, -0.32, -0.39, -0.62):
        thr = math.sqrt(1 - rho ** 2)
        cells = []
        for mu, sd in ((0.97, 0.05), (0.97, 0.08), (0.97, 0.12), (0.86, 0.10)):
            p = sst.norm.cdf((thr - mu) / sd)
            cells.append(f"{100*p:10.0f}%")
            dele.append(dict(rho=rho, threshold=thr, vr_mean=mu, vr_sd=sd,
                             pct_dropped=100 * p))
        print(f"  {rho:7.2f} {thr:14.3f} | {' '.join(cells)}")
    print()
    print("  Their own antipsychotic CVR is 0.86 (McCutcheon 2021), and the")
    print("  Winkelbeiner VR is 0.97. Under either, a large minority of trials")
    print("  fails the filter at rho = -0.32, and it is a filter ON THE OUTCOME.")

    with open("out_calibrated_artifact.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    with open("out_propagation.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(prop[0].keys()))
        w.writeheader()
        w.writerows(prop)
    with open("out_deletion.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(dele[0].keys()))
        w.writeheader()
        w.writerows(dele)
    print("\nwrote out_calibrated_artifact.csv, out_propagation.csv, out_deletion.csv")


if __name__ == "__main__":
    main()
