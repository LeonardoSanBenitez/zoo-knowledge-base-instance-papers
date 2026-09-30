"""Internal-consistency checks on Huang et al. 2026, arXiv:2609.28614v1, from printed numbers only
(no artifact is released: red-team prompts, scorer vulnerabilities and CHEAT_SUMMARY files are
withheld, Sec 'Broader impact'). Stdlib. Run: python internal_consistency.py
"""
from math import sqrt

def wilson(k, n, z=1.959964):
    p = k / n; d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d; h = z*sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return round(100*(c-h), 1), round(100*(c+h), 1)

print('E2 confirmed hacks 505/677 =', round(100*505/677, 1), '% (paper 74.6)')
print('E2 evasions 33/505 =', round(100*33/505, 1), '% Wilson', wilson(33, 505), '(paper 6.5 [4.7, 9.0])')
print('compliant controls 0/102 Wilson', wilson(0, 102), '(paper [0, 3.6])')
print('E3 round-1 7/150 Wilson', wilson(7, 150), '(paper 4.7 [2.3, 9.3]); round-5 56/150 Wilson', wilson(56, 150), '(paper 37 [30, 45])')
print('E3 paired 79: detailed 32/79 =', round(100*32/79, 1), ' retry-only 16/79 =', round(100*16/79, 1), '(paper 40.5 vs 20.3)')

# Table 2: Setting-2 family sizes and evasion rates must add back to the 33 evasions.
s2 = {'leakage': (403, .025), 'scorer': (24, .208), 'fabrication': (27, .185), 'lookup': (21, .0), 'distill': (7, .571), 'other': (18, .50)}
print('Table 2 S2 sizes sum', sum(n for n, _ in s2.values()), '(paper 500); implied evasions',
      {k: round(n*r, 2) for k, (n, r) in s2.items()}, 'total', round(sum(n*r for n, r in s2.values()), 1), '(paper 33)')
pooled = {'leakage': (694, .030), 'scorer': (64, .25), 'fabrication': (46, .239), 'lookup': (44, .114), 'distill': (32, .375), 'other': (43, .535)}
tot = sum(n*r for n, r in pooled.values())
print('Table 2 pooled sizes sum', sum(n for n, _ in pooled.values()), '(paper 923); implied evasions', round(tot, 1),
      '-> Setting-3 share', round(tot - 33, 1), 'vs 56 E3 pairs that evaded (attempt-level vs pair-level, and 5 E2 hacks lack summaries)')
print('distillation 12/32 Wilson', wilson(12, 32), '(paper 38% [20, 52])')

# Setting 1: 17 models x 38 tasks, 20 research-pipeline and 18 task-specific.
full_R, full_K = 17*20, 17*18
sols = [(x, R, 105-x, K) for R in range(250, full_R+1) for x in range(R+1) if round(100*x/R, 1) == 30.5
        for K in range(200, full_K+1) if 0 <= 105-x <= K and round(100*(105-x)/K, 1) == 2.9]
print(f'Setting 1: full grid is {full_R} research + {full_K} kernel cells.',
      'No integer count over the FULL research grid gives 30.5%:', [x for x in range(full_R+1) if round(100*x/full_R, 1) == 30.5])
print('  consistent (hacks, cells) solutions summing to 105 hacks, first 5:', sols[:5], '... total', len(sols))
