"""n2 -- Xu, Liu & Regier (2020), with the OSF deposit (jmrqw, numeral_systems_analysis-master.zip, sha256 01b0b72e...).

Question (open question 1 of the record): restricted to prefix-respecting hypothetical systems, are attested exact-restricted
systems still near-optimal, i.e. does efficiency say anything about them beyond "count from one"?

What the deposit's own code does (aggregate_complexities_and_costs.py):
  attested exact-restricted cost  = compute_cost_size_principle(ulim[lang], need)          # depends on ulim only
  hypothetical 'efficient' exact  = compute_cost_size_principle(tn, need), tn = 1..        # the SAME function
  hypothetical 'inefficient' exact= compute_cost_size_principle_arb(modemap)               # extra exact terms at 97..100
  hypothetical exact complexity   = 3*tn + 4 (tn <= 3) else 13 + 4*(tn - 3)                # a formula
  attested complexity             = language_tree.calc_complexity(langstrategy.<lang>())   # from each grammar
So for exact-restricted languages, any distance from the frontier can only come from COMPLEXITY. This script:
  1. runs their language_tree/langstrategy (unmodified) for every language's complexity, num_type and ulim;
  2. reimplements the two cost functions verbatim and checks them on the deposit's need file;
  3. prints, per attested exact language: ulim, attested complexity, frontier complexity at the same ulim, cost;
  4. the prefix-restricted null: among ALL prefix systems {1..k} + 'many' (k = 1..99), what fraction has lower cost at
     lower-or-equal complexity than each attested language (= how many dominate it), with complexity by their formula.

    <venv with anytree==2.8.0>/python -I n2_deposit_exact_frontier.py <deposit dir> > out/n2_deposit_exact_frontier.txt
Author: maria, 2026-11-12.
"""
import math
import os
import sys

DEP = os.path.abspath(sys.argv[1])
sys.path.insert(0, DEP)
os.chdir(DEP)  # their modules read relative paths at import time
import langstrategy  # noqa: E402  (theirs, unmodified)
import language_tree  # noqa: E402

NEED = [float(x) for x in open(os.path.join(DEP, "data/need_probs/needprobs_eng_fit.csv")).read().split()]
assert len(NEED) == 100, len(NEED)


def size_principle(upper_lim, need):
    """Verbatim logic of routines/compute_cost.py compute_cost_size_principle."""
    length = len(need)
    unit = [0.0] * length
    denom = length - (upper_lim + 1) + 1
    norm = sum(need[i] / denom for i in range(upper_lim, length))
    for i in range(upper_lim, length):
        unit[i] = -math.log(need[i] / denom / norm, 2)
    return sum(n * u for n, u in zip(need, unit))


def hyp_complexity(tn):
    return tn * 3 + 4 if tn <= 3 else 3 * 3 + (tn - 3) * 4 + 4


# sanity: the size-principle listener over the residual is the Bayesian listener: cost = H(residual) weighted
k3 = size_principle(3, NEED)
res = NEED[3:]
z = sum(res)
bayes3 = sum(n * -math.log(n / z, 2) for n in res)
assert abs(k3 - bayes3) < 1e-9, (k3, bayes3)

codes = [n for n, f in vars(langstrategy).items() if callable(f) and len(n) == 3 and n.islower()]
rows = []
for c in sorted(codes):
    try:
        comp, num_type, ulim = language_tree.build_language(c, save=False)
    except Exception as e:  # noqa: BLE001
        print(f"{c}: build failed: {e!r}")
        continue
    rows.append((c, num_type, ulim, comp))

print("need mass 1..3 = %.3f, 1..5 = %.3f, 1..10 = %.3f" % (sum(NEED[:3]), sum(NEED[:5]), sum(NEED[:10])))
print("\nexact-restricted (num_type 1): ulim | attested complexity | frontier complexity at same ulim | cost (bits)")
exact = [r for r in rows if r[1] == 1]
prefix = [(k, hyp_complexity(k), size_principle(k, NEED)) for k in range(1, 100)]
for c, _, ulim, comp in exact:
    cost = size_principle(ulim, NEED)
    dominated_by = [k for k, hc, hcost in prefix if hc <= comp and hcost < cost - 1e-12]
    print(f"  {c}: ulim {ulim:3d} | {comp:4d} | {hyp_complexity(ulim):4d} | {cost:.4f} | prefix systems dominating it: {len(dominated_by)}"
          + (f" (k = {dominated_by[:5]}{'...' if len(dominated_by) > 5 else ''})" if dominated_by else ""))
print("\nall languages built: " + ", ".join(f"{c}(type {t}, ulim {u}, comp {k})" for c, t, u, k in rows))
print("\nprefix frontier: every k is Pareto-optimal among prefix systems? ",
      all(not any(hc2 <= hc and hcost2 < hcost - 1e-12 and k2 != k for k2, hc2, hcost2 in prefix) for k, hc, hcost in prefix))
