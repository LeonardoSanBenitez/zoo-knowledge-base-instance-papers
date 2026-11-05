"""Which data-generating worlds reproduce RPP's real pattern (observed 24/73 significant replications while SH
expects 45.9 and N expects 55.4)?  p02 showed that honest selection on significance does NOT: SH stays roughly
calibrated there. Candidates here:
  Q1  p-hacking: each original tries up to K analyses (correlated rho = .5) and reports the first with |t| > 1.96
  Q2  small true effects r ~ .1 + selection, large n_r
  Q3  heterogeneity: theta_r = theta_o * attenuation (replication effect systematically smaller, "decline")
  Q4  mixture: 60% null + p-hacking K=5, 40% r=.25
Each world is run with RPP's (n_o, n_r) design; reports observed, N/SH/SA expected, and the distribution of |t_o|
(share in 1.96-2.5, the bunching a p-hacked literature shows), compared to RPP's own share.
Usage: python p04_qrp_worlds.py <RProjects.rda>   Writes out/p04.json.
"""
import json, os, sys
import numpy as np, pyreadr
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from selection_forecast import fit_g, p_sig_selection, p_sig_pawel, scores, ZC

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
R = pyreadr.read_r(sys.argv[1])["RProjects"]
ps = R[R.project == "Psychology"]
NO, NR = ps.no.values.astype(float), ps.nr.values.astype(float)
to_real = np.abs(ps.fiso / ps.se_fiso).values
rng = np.random.default_rng(7)


def draw_orig(th, so, K, rho=0.5):
    """K correlated analyses of the same data; report the first significant one (or the last tried)."""
    common = rng.normal(0, 1)
    for _ in range(K):
        e = np.sqrt(rho) * common + np.sqrt(1 - rho) * rng.normal(0, 1)
        est = th + so * e
        if abs(est / so) > ZC:
            return est, True
    return est, False


def world(theta_sampler, K=1, atten=1.0, tau=0.0, m=73, reps=100):
    acc = {k: [0, 0.0, []] for k in ("N", "SH", "SA08")}
    bunch = []
    for _ in range(reps):
        rows = []
        while len(rows) < m:
            j = rng.integers(len(NO)); so, sr = 1 / np.sqrt(NO[j] - 3), 1 / np.sqrt(NR[j] - 3)
            th = theta_sampler()
            est, ok = draw_orig(th + rng.normal(0, tau), so, K)
            if not ok:
                continue
            estr = atten * th + rng.normal(0, tau) + rng.normal(0, sr)
            rows.append((est, so, estr, sr))
        a = np.array(rows); sg = np.sign(a[:, 0]); toa = np.abs(a[:, 0] / a[:, 1])
        y = ((sg * a[:, 2] / a[:, 3]) > ZC).astype(int)
        c = a[:, 1] ** 2 / a[:, 3] ** 2; d = 0.08 ** 2 / a[:, 1] ** 2
        w, _ = fit_g(toa, a[:, 1], truncate=True)
        fc = {"N": p_sig_pawel(toa, c, d, "N"), "SH": p_sig_pawel(toa, c, d, "SH"),
              "SA08": p_sig_selection(toa, a[:, 1], a[:, 3], w, 0.08)[0]}
        for k, p in fc.items():
            s = scores(p, y); acc[k][0] += s["observed"]; acc[k][1] += s["expected"]; acc[k][2].append(s["BS"])
        bunch.append(np.mean((toa > ZC) & (toa < 2.5)))
    return {"observed_per_73": round(acc["N"][0] / reps, 1), **{f"exp_{k}": round(v[1] / reps, 1) for k, v in acc.items()},
            **{f"BS_{k}": round(float(np.mean(v[2])), 4) for k, v in acc.items()}, "share_|t_o|_in_1.96-2.5": round(float(np.mean(bunch)), 3)}


z03 = np.arctanh(.3)
W = {
    "Q0_honest_half_null": dict(theta_sampler=lambda: 0.0 if rng.random() < .5 else rng.normal(z03, .1)),
    "Q1_phack_K5_half_null": dict(theta_sampler=lambda: 0.0 if rng.random() < .5 else rng.normal(z03, .1), K=5),
    "Q1b_phack_K5_80pct_null": dict(theta_sampler=lambda: 0.0 if rng.random() < .8 else rng.normal(z03, .1), K=5),
    "Q2_small_r.1_all_true": dict(theta_sampler=lambda: rng.normal(np.arctanh(.1), .05)),
    "Q3_decline_atten.5_r.3": dict(theta_sampler=lambda: rng.normal(z03, .1), atten=0.5),
    "Q4_60null_phackK5_40_r.25": dict(theta_sampler=lambda: 0.0 if rng.random() < .6 else rng.normal(np.arctanh(.25), .1), K=5),
    "Q5_tau.15_honest_r.2": dict(theta_sampler=lambda: rng.normal(np.arctanh(.2), .05), tau=0.15),
}
res = {"RPP_real": {"observed": 24, "exp_N": 55.4, "exp_SH": 45.9, "exp_SA08": 40.1,
                    "share_|t_o|_in_1.96-2.5": round(float(np.mean((to_real > ZC) & (to_real < 2.5))), 3), "share_|t_o|>1.96": round(float(np.mean(to_real > ZC)), 3)}}
print("RPP_real", res["RPP_real"])
for k, v in W.items():
    res[k] = world(**v); print(k, res[k])
json.dump(res, open(os.path.join(OUT, "p04.json"), "w"), indent=1)
