"""m03 -- How much can self-evaluation filter the SFT data in Algorithm 3?

Config (configs/paper.json, repo commit fb40358): 18 candidates per task, 6 opponents each in a ring
tournament (54 comparisons), Bradley-Terry, ranks 1-15 -> train, rank 16 -> validation, ranks 17-18
dropped. Only COMPLETED episodes enter the ranking (pipeline.rank -> completed()).

So the self-evaluator can remove at most 3 of 18 trajectories from training (2 dropped + 1 to
validation). Question: what is the ceiling of that filter, in SD units of within-workflow trajectory
quality, and how much of it survives a judge of realistic accuracy?

World: latent quality z_j ~ N(0,1) for the 18 trajectories of one task. The judge prefers a over b
with probability sigmoid(s*(z_a - z_b)); s is set so that pairwise accuracy against the latent truth
is 0.60, 0.73 (the paper's L0 agreement with its external panel, which is NOT ground truth) or 0.93.
Known answers: s = infinity must give the order-statistic ceiling; s = 0 must give zero gain.

Functions tournament_pairs and bradley_terry are copied VERBATIM from the repo
(mass/pipeline.py, mass/ranking.py at fb40358) so this script is self-contained.
Run: python m03_teacher_selection_ceiling.py   (numpy)
"""
import json, math, os, random
import numpy as np


def tournament_pairs(names, opponents, seed):  # verbatim, mass/pipeline.py
    if opponents < 2 or opponents % 2:
        raise ValueError("Use an even opponents_per_episode >= 2")
    names = sorted(names)
    random.Random(seed).shuffle(names)
    pairs = {tuple(sorted((name, names[(i + d) % len(names)])))
             for i, name in enumerate(names) for d in range(1, min(opponents // 2, len(names) - 1) + 1)}
    pairs = sorted(pairs)
    rng = random.Random(seed + 1)
    return [(b, a) if rng.random() < .5 else (a, b) for a, b in pairs]


def bradley_terry(episodes, matches, iters=500, prior=0.5):  # verbatim, mass/ranking.py
    idx = {e: i for i, e in enumerate(episodes)}
    n = len(episodes)
    wins = [[0.0] * n for _ in range(n)]
    for (a, b), per in matches.items():
        if a not in idx or b not in idx:
            continue
        for lab in per.values():
            if lab == a:
                wins[idx[a]][idx[b]] += 1
            elif lab == b:
                wins[idx[b]][idx[a]] += 1
            else:
                wins[idx[a]][idx[b]] += 0.5; wins[idx[b]][idx[a]] += 0.5
    p = [1.0] * n
    for _ in range(iters):
        newp = []
        for i in range(n):
            W = sum(wins[i]) + prior
            denom = prior / (p[i] + 1.0)
            for j in range(n):
                if i == j:
                    continue
                nij = wins[i][j] + wins[j][i]
                if nij:
                    denom += nij / (p[i] + p[j])
            newp.append(W / denom if denom > 0 else p[i])
        s = sum(newp) / n
        p = [x / s for x in newp]
    return {e: math.log(p[idx[e]]) for e in episodes}


rng = np.random.default_rng(7)
M, TRAIN = 18, 15

def accuracy_for_s(s, n=200000):
    d = rng.normal(0, math.sqrt(2), n)
    return float(np.mean((1 / (1 + np.exp(-s * np.abs(d)))))) if s < 1e6 else 1.0

def one_task(s, seed):
    z = rng.normal(0, 1, M)
    names = [f"e{j:02d}" for j in range(M)]
    pairs = tournament_pairs(names, 6, seed)
    matches = {}
    for a, b in pairs:
        za, zb = z[int(a[1:])], z[int(b[1:])]
        if s >= 1e6:
            pa = 1.0 if za > zb else 0.0
        else:
            pa = 1 / (1 + math.exp(-s * (za - zb)))
        matches[(a, b)] = {"self": a if rng.random() < pa else b}
    sc = bradley_terry(sorted(names), matches, iters=200)
    order = sorted(names, key=lambda n: (-sc[n], n))
    sel = [z[int(n[1:])] for n in order[:TRAIN]]
    return float(np.mean(sel) - np.mean(z)), len(pairs)

out = {}
# calibrate s to target accuracies by bisection on the analytic expectation
def s_for(target):
    lo, hi = 0.0, 50.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if accuracy_for_s(mid, 40000) < target: lo = mid
        else: hi = mid
    return (lo + hi) / 2

R = 300
for label, s in [("random_judge_s0", 0.0), ("acc0.60", s_for(0.60)), ("acc0.73", s_for(0.73)),
                 ("acc0.93", s_for(0.93)), ("perfect", 1e9)]:
    gains = []
    for r in range(R):
        g, npairs = one_task(s, 1234 + r)
        gains.append(g)
    out[label] = {"s": s, "mean_gain_SD_top15_minus_all18": round(float(np.mean(gains)), 4),
                  "sd_of_gain": round(float(np.std(gains)), 4), "pairs_per_task": npairs}

# analytic ceiling: E[mean of top 15 of 18 N(0,1)] - 0 = -(E[sum of bottom 3])/15 ... simulate directly
zz = np.sort(rng.normal(0, 1, (200000, M)), axis=1)
out["order_statistic_ceiling"] = round(float(np.mean(zz[:, M - TRAIN:].mean(axis=1))), 4)
out["note"] = ("Gain is in SD units of WITHIN-workflow trajectory quality; it says nothing about how "
               "large that SD is relative to the between-model differences the paper reports.")
here = os.path.dirname(os.path.abspath(__file__))
json.dump(out, open(os.path.join(here, "m03_out.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
