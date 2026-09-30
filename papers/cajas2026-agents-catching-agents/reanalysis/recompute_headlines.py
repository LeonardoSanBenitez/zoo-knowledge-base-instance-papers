"""Recompute headline numbers of Cajas Ordonez et al. 2026 (arXiv:2608.03744v2) from the
per-case rows committed in the benchmaxxing repository, without any API call.

Repository: https://github.com/criticaldata/benchmaxxing, checked out in the zoo at
dojo/benchmaxxing (commit d5b5c33 at the time of writing). Pass another root as argv[1].

Checks:
  1. confidence arm (Sec 4.2): confident 0.42 vs hedged 0.14 of 100, McNemar 29/1, p = 6e-8
  2. CheXpert natural-device arm (Sec 4.4): 92/150 shared adoption, 143 correct alone,
     85/143 adoption among those, pre-screen flag with no peer 1/150
  3. the paper's own caveat that the isolated re-read equals the clean read on all 150
  4. NEW, not in the paper: the wrong answer the peers assert has one polarity on every
     film ("no"), and no arm asks the support-device question of a film WITHOUT a device,
     so "correct alone" cannot be separated from a yes-prior.
Run from the zoo root:  python zoo-knowledge-base/instance-papers/papers/cajas2026-agents-catching-agents/reanalysis/recompute_headlines.py
"""
import json, sys, os
from math import comb
from collections import Counter

root = sys.argv[1] if len(sys.argv) > 1 else 'dojo/benchmaxxing'
def rows(rel):
    with open(os.path.join(root, rel)) as f:
        return [json.loads(l) for l in f if l.strip()]

def exact_mcnemar(b, c):
    n, k = b + c, min(b, c)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)

r = rows('experiments/medqa/results/seed_confidence.jsonl')
conf = sum(x['confident_adopt'] for x in r); hedg = sum(x['hedged_adopt'] for x in r)
gain = sum(1 for x in r if x['confident_adopt'] and not x['hedged_adopt'])
lose = sum(1 for x in r if x['hedged_adopt'] and not x['confident_adopt'])
print(f"[1] confidence arm n={len(r)} confident={conf} hedged={hedg} discordant={gain}/{lose} exact McNemar p={exact_mcnemar(gain, lose):.2e}")
assert (len(r), conf, hedg, gain, lose) == (100, 42, 14, 29, 1)

z = rows('experiments/imaging_chexpert/results/natural_independent/imaging_cascade_none.jsonl')
sh = sum(x['shared_adopt'] for x in z); cc = sum(x['clean_correct'] for x in z)
sc = sum(x['shared_adopt'] for x in z if x['clean_correct']); pl = sum(x['placebo_adopt'] for x in z)
print(f"[2] CheXpert n={len(z)} shared_adopt={sh} correct_alone={cc} adopt_among_correct={sc} flag_no_peer={pl}")
assert (len(z), sh, cc, sc, pl) == (150, 92, 143, 85, 1)

print(f"[3] isolated read differs from clean read on {sum(x['iso'] != x['clean'] for x in z)} of {len(z)}")

print(f"[4] finding asked: {Counter(x['finding'] for x in z)}; asserted wrong answer: {Counter(x['wrong'] for x in z)}")
d = rows('experiments/imaging_chexpert/results/device_absent/imaging_cascade_none.jsonl')
print(f"    'device_absent' arm asks: {Counter(x['finding'] for x in d)}  (not the support-device question)")
print("    -> no committed arm measures P(answer 'yes' to support devices | no device on film)")
