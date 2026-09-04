"""m01 -- derive and verify the sigma_TE formula, and check its arithmetic.

McCutcheon et al., World Psychiatry 2022, eq. in Methods:

    sigma_TE = sigma_PL * ( sqrt(VR^2 - 1 + rho^2) - rho )

Derivation (mine, independently, then compared to theirs):
  For patient i let Y_i^C be the outcome (change score) under placebo and
  d_i = Y_i^T - Y_i^C the individual treatment effect. Under randomisation both
  arms sample the same joint law of (Y^C, d), so

      Var(Y^T) = Var(Y^C) + Var(d) + 2 Cov(Y^C, d)
      VR^2 sC^2 = sC^2 + sd^2 + 2 rho sC sd            [rho = Corr(Y^C, d)]

  Divide by sC^2 with u = sd/sC:

      u^2 + 2 rho u + (1 - VR^2) = 0
      u = -rho +/- sqrt(rho^2 + VR^2 - 1)

  Their formula is the "+" root. It is a QUADRATIC: whenever both roots are
  non-negative the data cannot choose between them, and that happens exactly
  when VR <= 1 and rho < 0 -- which is the regime the whole paper lives in.

Run: python m01_formula.py
"""
import math, csv, os

def sigma_te(vr, rho, s_pl=1.0, root="+"):
    disc = vr * vr - 1.0 + rho * rho
    if disc < 0:
        return None                      # no real solution: VR too small for this rho
    r = math.sqrt(disc)
    u = (-rho + r) if root == "+" else (-rho - r)
    return None if u < 0 else s_pl * u

def var_check(vr, rho, u):
    """Independent check: does this u actually reproduce VR through the
    variance identity? Catches an algebra slip that a self-consistent
    rearrangement would hide."""
    return math.sqrt(1.0 + u * u + 2.0 * rho * u)

print("=" * 78)
print("1. ALGEBRA CHECK -- does the root satisfy the variance identity?")
print("=" * 78)
print(f"{'VR':>6} {'rho':>7} {'u=sd/sC (+root)':>17} {'VR rebuilt':>11} {'ok':>4}"
      f" | {'u (-root)':>10} {'VR rebuilt':>11} {'ok':>4}")
for vr in (0.90, 0.97, 1.00, 1.03, 1.10):
    for rho in (0.0, -0.32, -0.62):
        up = sigma_te(vr, rho, 1.0, "+")
        um = sigma_te(vr, rho, 1.0, "-")
        sp = var_check(vr, rho, up) if up is not None else float("nan")
        sm = var_check(vr, rho, um) if um is not None else float("nan")
        print(f"{vr:6.2f} {rho:7.2f} "
              f"{('%.4f'%up) if up is not None else '   none':>17} "
              f"{sp:11.4f} {'OK' if up is not None and abs(sp-vr)<1e-12 else '--':>4}"
              f" | {('%.4f'%um) if um is not None else '  none':>10} "
              f"{sm:11.4f} {'OK' if um is not None and abs(sm-vr)<1e-12 else '--':>4}")

print()
print("=" * 78)
print("2. THE HEADLINE -- can I rebuild sigma_TE = 13.5 PANSS points?")
print("=" * 78)
print("They report: rho = -0.32 (LM method, 'most conservative'),")
print("             sigma_TE(total) = 13.5 PANSS [12.7, 14.3], I2 = 45%")
print("             mean treatment effect = 8.6 PANSS")
print("Winkelbeiner 2019 VR (52 RCTs) = 0.97; McCutcheon 2021 CVR = 0.86.")
print()
print(f"{'VR':>6} {'rho':>7} {'sigma_TE / sigma_PL':>20} "
      f"{'implied sigma_PL for 13.5':>27}")
for vr in (0.95, 0.97, 0.99, 1.00, 1.01):
    for rho in (-0.32,):
        u = sigma_te(vr, rho)
        print(f"{vr:6.2f} {rho:7.2f} {u:20.4f} {13.5/u:27.1f}")
print()
print("A PANSS-total change SD of ~20-22 points is the usual value in these")
print("trials, so sigma_PL in that range reproduces 13.5 closely. Arithmetic")
print("of the headline is CONSISTENT. That was never the question.")

print()
print("=" * 78)
print("3. THE ROOT AMBIGUITY -- how much does the unstated choice buy them?")
print("=" * 78)
print(f"{'VR':>6} {'rho':>7} {'+root':>8} {'-root':>8} {'ratio':>8}"
      f" {'sTE(+) @sPL=21':>15} {'sTE(-) @sPL=21':>15}")
rows = []
for vr in (0.90, 0.93, 0.95, 0.97, 0.99, 1.00):
    for rho in (-0.32, -0.39, -0.62):
        up, um = sigma_te(vr, rho), sigma_te(vr, rho, root="-")
        if up is None or um is None:
            continue
        ratio = up / um if um > 1e-12 else float("inf")
        print(f"{vr:6.2f} {rho:7.2f} {up:8.4f} {um:8.4f} {ratio:8.2f}"
              f" {21*up:15.1f} {21*um:15.1f}")
        rows.append(dict(vr=vr, rho=rho, u_plus=up, u_minus=um, ratio=ratio,
                         sTE_plus=21*up, sTE_minus=21*um))
print()
print("Both roots are mathematically admissible whenever VR < 1 and rho < 0,")
print("i.e. THROUGHOUT the regime this paper analyses. The paper takes '+'")
print("without saying a choice was made. At VR = 0.97, rho = -0.32 the two")
print("answers are 11.1 and 2.4 PANSS points -- a factor of 4.6 -- and only")
print("the larger one supports the paper's conclusion.")

with open("out_formula.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
print("\nwrote out_formula.csv")
