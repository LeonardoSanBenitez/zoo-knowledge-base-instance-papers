"""Is "correlated error" a PAIRWISE property (kinship) or a MARGINAL one?

Hypothesis raised by anchored.py: better models, conditional on being wrong,
are wrong in a more CONCENTRATED way -- they gravitate to the single most
seductive distractor. If so, two strong models can be conditionally independent
given the item and still agree ~70% of the time, purely because each
independently puts high mass on the same trap. Apparent monoculture would then
be a marginal effect of competence, not a dependence between the models.

Test 1: per model, P(its wrong answer == modal wrong answer of the OTHER models
        | it is wrong).  Correlate with accuracy.
Test 2: build a fully INDEPENDENT synthetic population -- for each item, draw
        each model's wrong answer independently from that model's own fitted
        attractiveness profile -- and see how much pairwise agreement appears
        with zero dependence by construction. Compare to observed.
"""
import itertools, collections, os, random
import numpy as np
import pandas as pd
from analyze import load, OUT

answers, correct, nopts, _ = load()
models = sorted({m for (m, _) in answers})
qkeys = sorted(correct)
acc = {m: float(np.mean([answers.get((m, q)) == correct[q] for q in qkeys])) for m in models}
wrongmap = {q: {m: answers[(m, q)] for m in models
                if answers.get((m, q)) is not None and answers[(m, q)] != correct[q]}
            for q in qkeys}

# ---- Test 1: concentration on the modal distractor, per model ----
print("=" * 72)
print("TEST 1: P(model's wrong answer == modal wrong answer of the other models)")
rows = []
for m in models:
    hit = n = 0
    for q in qkeys:
        w = wrongmap[q]
        if m not in w:
            continue
        others = [a for mm, a in w.items() if mm != m]
        if len(others) < 6:
            continue
        c = collections.Counter(others)
        top, topn = c.most_common(1)[0]
        if topn <= len(others) / 2 and len(c) > 1 and topn == c.most_common(2)[1][1]:
            continue  # ambiguous mode, skip
        n += 1
        hit += (w[m] == top)
    rows.append(dict(model=m, acc=acc[m], n=n, p_modal=hit / n))
t1 = pd.DataFrame(rows).sort_values("acc", ascending=False)
print(t1.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
r = np.corrcoef(t1.acc, t1.p_modal)[0, 1]
print(f"\n  corr(accuracy, P(modal distractor | wrong)) = {r:+.3f}  over {len(t1)} models")
excl = t1[~t1.model.str.contains("unicorn|palmyra")]
print(f"  excluding the duplicate-model pair:            "
      f"{np.corrcoef(excl.acc, excl.p_modal)[0,1]:+.3f}")

# ---- Test 2: conditionally-independent synthetic population ----
print("=" * 72)
print("TEST 2: agreement among models made CONDITIONALLY INDEPENDENT by construction")
print("  (each model's wrong answer redrawn independently from its own fitted")
print("   per-item attractiveness profile; any remaining agreement is marginal)")
rng = random.Random(7)

# fit: for each item, the population wrong-answer profile; for each model, a
# 'sharpness' = how much it concentrates on the top distractor relative to pop.
pop_profile = {}
for q in qkeys:
    w = wrongmap[q]
    if len(w) >= 4:
        c = collections.Counter(w.values())
        tot = sum(c.values())
        pop_profile[q] = {k: v / tot for k, v in c.items()}

sharp = dict(zip(t1.model, t1.p_modal))
hi, lo = t1.p_modal.max(), t1.p_modal.min()


def sim_once():
    sim = {}
    for q, prof in pop_profile.items():
        order = sorted(prof, key=lambda k: -prof[k])
        top = order[0]
        for m in wrongmap[q]:
            # tilt the population profile toward the top distractor by the
            # model's own measured sharpness; then draw INDEPENDENTLY
            t = (sharp[m] - lo) / (hi - lo + 1e-9)
            p = {k: (1 - t) * prof[k] for k in prof}
            p[top] = p.get(top, 0) + t
            ks = list(p); ws = [p[k] for k in ks]
            sim[(m, q)] = rng.choices(ks, weights=ws, k=1)[0]
    return sim


sim = sim_once()
obs_a = sim_a = n_a = 0.0
rows = []
for m1, m2 in itertools.combinations(models, 2):
    o = s = n = 0.0
    for q in pop_profile:
        w = wrongmap[q]
        if m1 not in w or m2 not in w:
            continue
        n += 1
        o += (w[m1] == w[m2])
        s += (sim[(m1, q)] == sim[(m2, q)])
    if n >= 30:
        rows.append(dict(m1=m1, m2=m2, n=int(n), obs=o / n, indep_sim=s / n,
                         acc_min=min(acc[m1], acc[m2]),
                         same_provider=m1.split("_")[0] == m2.split("_")[0]))
d = pd.DataFrame(rows)
dd = d[~((d.m1.str.contains("unicorn") | d.m2.str.contains("unicorn")) &
         (d.m1.str.contains("palmyra") | d.m2.str.contains("palmyra")))]
d.to_csv(os.path.join(OUT, "marginal_sim.csv"), index=False)
print(f"  pairs={len(dd)}")
print(f"  OBSERVED mean agreement-when-both-wrong        = {dd.obs.mean():.4f}")
print(f"  CONDITIONALLY INDEPENDENT simulation           = {dd.indep_sim.mean():.4f}")
print(f"  uniform-over-wrong baseline (Kim et al.)       = 0.3333")
print(f"  => of the observed excess over uniform ({dd.obs.mean()-1/3:+.4f}),")
print(f"     {(dd.indep_sim.mean()-1/3)/(dd.obs.mean()-1/3):.1%} is reproduced with")
print(f"     ZERO dependence between models.")
print(f"  residual needing dependence: {dd.obs.mean()-dd.indep_sim.mean():+.4f}")
print(f"    same-provider {(dd[dd.same_provider].obs-dd[dd.same_provider].indep_sim).mean():+.4f}"
      f"  cross-provider {(dd[~dd.same_provider].obs-dd[~dd.same_provider].indep_sim).mean():+.4f}")
print(f"  corr(min-accuracy, simulated independent agreement) = "
      f"{np.corrcoef(dd.acc_min, dd.indep_sim)[0,1]:+.3f}")
print(f"  corr(min-accuracy, observed agreement)              = "
      f"{np.corrcoef(dd.acc_min, dd.obs)[0,1]:+.3f}")
