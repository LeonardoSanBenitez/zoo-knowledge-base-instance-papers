"""Known-answer worlds for replication forecasts: does a forecaster stay calibrated when the truth is known?

Sample sizes are taken from the real Psychology (RPP) pairs in RProjects (n_o, n_r), so the worlds have RPP's design.
True Fisher-z effects theta are drawn from a stated g; originals are drawn and SELECTED (|t_o| > 1.96, or no selection);
replications are drawn at n_r with between-study heterogeneity tau_true. Forecasters: Pawel-Held N, SH (tau = .08),
and the selection-aware NPMLE (SA, tau = 0 and .08) fitted on the selected originals only.

A forecaster is calibrated in a world if expected == observed (Spiegelhalter z ~ N(0,1)). The point: if SH is
miscalibrated in a world with selection but NO heterogeneity and NO QRPs, then SH's residual miscalibration on real
data cannot be read as evidence of heterogeneity/QRPs -- it is the model's selection-blindness.

Usage: python p02_known_answer.py <RProjects.rda>   Writes out/p02.json.
"""
import json, os, sys
import numpy as np, pyreadr
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from selection_forecast import fit_g, p_sig_selection, p_sig_pawel, scores, ZC

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"); os.makedirs(OUT, exist_ok=True)
R = pyreadr.read_r(sys.argv[1])["RProjects"]
ps = R[R.project == "Psychology"]
NO, NR = ps.no.values.astype(float), ps.nr.values.astype(float)
rng = np.random.default_rng(11)

WORLDS = {
    # name: (sampler of theta, selection on?, tau_true)
    "A_half_null_half_r.3_selected": (lambda k: np.where(rng.random(k) < .5, 0.0, rng.normal(np.arctanh(.3), .1, k)), True, 0.0),
    "B_all_true_r.3_selected": (lambda k: rng.normal(np.arctanh(.3), .1, k), True, 0.0),
    "C_half_null_selected_tau.08": (lambda k: np.where(rng.random(k) < .5, 0.0, rng.normal(np.arctanh(.3), .1, k)), True, 0.08),
    "D_no_selection_r~N(.2,.15)": (lambda k: rng.normal(np.arctanh(.2), .15, k), False, 0.0),
    "E_80pct_null_selected": (lambda k: np.where(rng.random(k) < .8, 0.0, rng.normal(np.arctanh(.3), .1, k)), True, 0.0),
}


def one_project(sampler, select, tau_true, m=73):
    """Draw a project of m selected pairs using RPP's (n_o, n_r) design (resampled)."""
    rows = []
    while len(rows) < m:
        j = rng.integers(len(NO)); no, nr = NO[j], NR[j]
        so, sr = 1 / np.sqrt(no - 3), 1 / np.sqrt(nr - 3)
        th = sampler(1)[0]
        th_o = th + rng.normal(0, tau_true); th_r = th + rng.normal(0, tau_true)
        est = th_o + rng.normal(0, so)
        if select and abs(est / so) <= ZC:
            continue
        estr = th_r + rng.normal(0, sr)
        rows.append((est, so, estr, sr))
    a = np.array(rows)
    sgn = np.sign(a[:, 0])
    to_abs = np.abs(a[:, 0] / a[:, 1]); y = ((sgn * a[:, 2] / a[:, 3]) > ZC).astype(int)
    return to_abs, a[:, 1], a[:, 3], y


res = {}
REPS = 100
for name, (sampler, select, tau_true) in WORLDS.items():
    acc = {k: {"obs": 0, "exp": 0.0, "bs": [], "z": []} for k in ("N", "SH", "SA0", "SA08")}
    for _ in range(REPS):
        to_abs, so, sr, y = one_project(sampler, select, tau_true)
        c = so ** 2 / sr ** 2; d = 0.08 ** 2 / so ** 2
        fc = {"N": p_sig_pawel(to_abs, c, d, "N"), "SH": p_sig_pawel(to_abs, c, d, "SH")}
        w, _ = fit_g(to_abs, so, truncate=select)
        fc["SA0"], _ = p_sig_selection(to_abs, so, sr, w, 0.0, truncate=select)
        fc["SA08"], _ = p_sig_selection(to_abs, so, sr, w, 0.08, truncate=select)
        for k, p in fc.items():
            s = scores(p, y)
            acc[k]["obs"] += s["observed"]; acc[k]["exp"] += s["expected"]; acc[k]["bs"].append(s["BS"]); acc[k]["z"].append(s["spiegelhalter_z"])
    res[name] = {k: {"observed_per_73": round(v["obs"] / REPS, 1), "expected_per_73": round(v["exp"] / REPS, 1), "mean_BS": round(float(np.mean(v["bs"])), 4),
                     "mean_spiegelhalter_z": round(float(np.mean(v["z"])), 2), "share_|z|>1.96": round(float(np.mean(np.abs(v["z"]) > 1.96)), 2)}
                 for k, v in acc.items()}
    print(name)
    for k, v in res[name].items():
        print("   ", k, v)
json.dump(res, open(os.path.join(OUT, "p02.json"), "w"), indent=1)
