"""Selection-aware (SA) forecasts vs Pawel-Held N/SH on the four real projects (RProjects).

SA fits g(theta) per project on that project's ORIGINALS only (truncated at |t_o| > 1.96; originals that are not
significant on the Fisher-z scale are fitted without truncation and forecast with the untruncated posterior), then
forecasts each replication. Also reports what g implies: share of selected originals with theta ~ 0, median theta.
Usage: python p03_projects.py <RProjects.rda>   Writes out/p03.json.
"""
import json, os, sys
import numpy as np, pyreadr
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from selection_forecast import fit_g, p_sig_selection, p_sig_pawel, scores, posterior, GRID, ZC

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
R = pyreadr.read_r(sys.argv[1])["RProjects"]
res = {}
for proj, df in R.groupby("project"):
    to = (df.fiso / df.se_fiso).values; tr = (df.fisr / df.se_fisr).values
    so, sr = df.se_fiso.values, df.se_fisr.values
    to_abs = np.abs(to); y = ((np.sign(tr) == np.sign(to)) & (np.abs(tr) > ZC)).astype(int)
    c = so ** 2 / sr ** 2; d = 0.08 ** 2 / so ** 2
    sig = to_abs > ZC
    w, ll = fit_g(to_abs[sig], so[sig], truncate=True)
    out = {"n_pairs": int(len(y)), "n_orig_significant": int(sig.sum())}
    fc = {"N": p_sig_pawel(to_abs, c, d, "N"), "SH": p_sig_pawel(to_abs, c, d, "SH")}
    for tau, key in ((0.0, "SA0"), (0.08, "SA08"), (0.15, "SA15")):
        p = np.empty(len(y))
        p[sig], _ = p_sig_selection(to_abs[sig], so[sig], sr[sig], w, tau, truncate=True)
        if (~sig).any():
            p[~sig], _ = p_sig_selection(to_abs[~sig], so[~sig], sr[~sig], w, tau, truncate=False)
        fc[key] = p
    for k, p in fc.items():
        out[k] = scores(p, y)
    # what the fitted g says about the selected originals
    out["g_mass_|theta|<.05"] = round(float(w[np.abs(GRID) < 0.05].sum()), 3)
    cdf = np.cumsum(w); out["g_median_theta_r"] = round(float(np.tanh(GRID[np.searchsorted(cdf, .5)])), 3)
    out["g_mean_theta_r"] = round(float(np.tanh((w * GRID).sum())), 3)
    post = posterior(to_abs[sig], so[sig], w, truncate=True)
    out["mean_posterior_theta_over_estimate"] = round(float(np.mean((post * GRID).sum(1) / (to_abs[sig] * so[sig]))), 3)
    out["SH_mean_shrinkage_s"] = round(float(np.mean(np.maximum(1 - (1 + d) / to_abs ** 2, 0))), 3)
    res[proj] = out
    print(proj, {k: v for k, v in out.items() if not isinstance(v, dict)})
    for k in fc:
        print("   ", k, out[k])
json.dump(res, open(os.path.join(OUT, "p03.json"), "w"), indent=1)
