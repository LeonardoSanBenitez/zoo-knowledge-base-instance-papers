"""What Cohen's d does a binary rate change produce, as a function of the unit of analysis?

Arslan et al. 2026 (BMJ Health Care Inform 33:e101877) report context-seeking rate
7.8% -> 97.3% (GPT-4.1-mini) with Cohen's d = 16.38, and 0.0% -> 73.5% (GPT-4o-mini)
with d = 19.54, on 200 HealthBench Hard vignettes x 5 seeds. The paper does not say
(in the main text) over which unit the SD was taken. This script simulates the design
and computes d under each defensible unit, so the reader can see that the number is set
by the unit, not by the behaviour. Stdlib only. Run: python cohens_d_by_unit.py
"""
import random, statistics as st

def sim(p0, p1, cases=200, seeds=5, case_sd=0.0, rng=None):
    # per-case propensity on the logit-free scale: clamp p + N(0, case_sd)
    out = []
    for arm_p in (p0, p1):
        props = [min(1, max(0, arm_p + rng.gauss(0, case_sd))) for _ in range(cases)]
        out.append([[1 if rng.random() < q else 0 for _ in range(seeds)] for q in props])
    return out  # [arm][case][seed]

def d_indep(a, b):
    sp = ((st.pvariance(a) + st.pvariance(b)) / 2) ** 0.5
    return (st.mean(b) - st.mean(a)) / sp if sp > 0 else float('inf')

def report(p0, p1, case_sd, rng):
    A, B = sim(p0, p1, case_sd=case_sd, rng=rng)
    resp_a = [x for c in A for x in c]; resp_b = [x for c in B for x in c]
    case_a = [st.mean(c) for c in A]; case_b = [st.mean(c) for c in B]
    seed_a = [st.mean(c[s] for c in A) for s in range(5)]
    seed_b = [st.mean(c[s] for c in B) for s in range(5)]
    diff = [b - a for a, b in zip(case_a, case_b)]
    dz = st.mean(diff) / st.pstdev(diff) if st.pstdev(diff) > 0 else float('inf')
    return dict(response=d_indep(resp_a, resp_b), case_mean=d_indep(case_a, case_b),
                case_paired_dz=dz, seed_mean=d_indep(seed_a, seed_b))

if __name__ == '__main__':
    rng = random.Random(20260930)
    for label, p0, p1, target in [('GPT-4.1-mini', .078, .973, 16.38), ('GPT-4o-mini', .0001, .735, 19.54)]:
        for case_sd in (0.0, 0.1, 0.2):
            reps = [report(p0, p1, case_sd, rng) for _ in range(200)]
            med = {k: st.median(r[k] for r in reps) for k in reps[0]}
            print(f"{label:13s} case_sd={case_sd:.1f}  " + "  ".join(f"{k}={v:6.2f}" for k, v in med.items()) + f"   reported={target}")
    # Known-answer control: identical arms must give d ~ 0 under every unit.
    r = report(.5, .5, 0.1, rng)
    print('null control (p0=p1=0.5):', {k: round(v, 2) for k, v in r.items()})
