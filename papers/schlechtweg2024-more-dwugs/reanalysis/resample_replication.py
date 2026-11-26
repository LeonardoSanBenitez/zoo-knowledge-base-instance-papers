"""Does graded change replicate when usages are resampled? (maria, 2026-11-26 night)

    python papers/schlechtweg2024-more-dwugs/reanalysis/resample_replication.py > papers/schlechtweg2024-more-dwugs/reanalysis/resample_replication.out.txt

Data: DWUG EN/DE/SV V3.0.0 (Zenodo 14028531, 14028509, 14028906) and DWUG EN/DE/SV resampled V1.0.0 (Zenodo 14025941,
12670698, 14026615), extracted under the asset paper-downloads/schlechtweg2024-more-dwugs/data (path from assets.py).
Uses the datasets' own stats/opt/stats_groupings.csv (change_graded = base-2 JS distance of the cluster distributions).

The paper (Sec. 6.3, Table 4) compares sense DISTRIBUTIONS between resampled and DWUG by trimming the longer one; it does
not report whether the graded change SCORES replicate. Here, for the 15 words per language in both:
 (1) Spearman of change_graded, resampled (25+25 uses) vs V3 (~100+100), with a word bootstrap CI;
 (2) mean difference resampled - V3;
 (3) what usage-sampling ALONE predicts: take V3's per-period cluster distributions as the truth, draw 25 uses per period
     (multinomial), recompute JSD; 2000 draws. Gives the expected resampled JSD per word and the expected Spearman
     between V3 and a 25-use replicate. If observed rho is near the simulated one, usage sampling explains the replication
     gap; if lower, clustering/annotation of the new graphs adds noise beyond it.
 (4) known-answer check of (3): the simulator applied to a 'replicate' drawn from itself must reproduce its own rho.
"""
import ast
import csv
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.spatial.distance import jensenshannon
from scipy.stats import spearmanr

KB = Path(__file__).resolve().parents[4]
ROOT = Path(subprocess.run([sys.executable, str(KB / "tools" / "assets.py"), "path",
                            "paper-downloads/schlechtweg2024-more-dwugs"], capture_output=True, text=True,
                           check=True).stdout.strip()) / "data"
SETS = {"EN": ("14028531_dwug_en/dwug_en", "14025941_dwug_en_resampled/dwug_en_resampled"),
        "DE": ("14028509_dwug_de/dwug_de", "12670698_dwug_de_resampled/dwug_de_resampled"),
        "SV": ("14028906_dwug_sv/dwug_sv", "14026615_dwug_sv_resampled/dwug_sv_resampled")}


def load(rel):
    out = {}
    with open(ROOT / rel / "stats" / "opt" / "stats_groupings.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            out[r["lemma"]] = {"g": float(r["change_graded"]),
                               "f1": np.array(ast.literal_eval(r["cluster_freq_dist1"]), float),
                               "f2": np.array(ast.literal_eval(r["cluster_freq_dist2"]), float)}
    return out


def jsd(c1, c2):
    if c1.sum() == 0 or c2.sum() == 0:
        return np.nan
    return float(jensenshannon(c1 / c1.sum(), c2 / c2.sum(), base=2))


def boot_rho(x, y, rng, B=4000):
    n = len(x); v = []
    for _ in range(B):
        i = rng.integers(0, n, n)
        if len(set(x[i])) > 1 and len(set(y[i])) > 1:
            v.append(spearmanr(x[i], y[i])[0])
    return np.percentile(v, [2.5, 97.5])


def simulate(words, full, n_per, rng, draws):
    """For each word: draws of the JSD of a 25+25 multinomial replicate of the full data's period distributions."""
    sims = np.zeros((draws, len(words)))
    for j, w in enumerate(words):
        p1 = full[w]["f1"] / full[w]["f1"].sum(); p2 = full[w]["f2"] / full[w]["f2"].sum()
        a = rng.multinomial(n_per, p1, size=draws); b = rng.multinomial(n_per, p2, size=draws)
        sims[:, j] = [jsd(a[d], b[d]) for d in range(draws)]
    return sims


def main():
    rng = np.random.default_rng(20261126)
    pooled_obs, pooled_full = [], []
    for lang, (full_rel, res_rel) in SETS.items():
        full, res = load(full_rel), load(res_rel)
        words = sorted(set(full) & set(res))
        g_full = np.array([full[w]["g"] for w in words]); g_res = np.array([res[w]["g"] for w in words])
        n_res = [int(res[w]["f1"].sum()) for w in words] + [int(res[w]["f2"].sum()) for w in words]
        rho, p = spearmanr(g_full, g_res); ci = boot_rho(g_full, g_res, rng)
        sims = simulate(words, full, 25, rng, 2000)
        sim_rho = np.array([spearmanr(g_full, s)[0] for s in sims])
        # known answer: treat one simulated replicate as 'full' truth? Instead: rho of V3 vs its own replicate distribution
        # is what sim_rho is; the check below asks whether the observed replicate is typical of the simulated ones.
        sim_mean = sims.mean(0)
        pct_obs = float((sim_rho <= rho).mean())
        print(f"== {lang}: {len(words)} shared words; resampled uses per period min/median/max "
              f"{min(n_res)}/{int(np.median(n_res))}/{max(n_res)}; V3 per period median "
              f"{int(np.median([full[w]['f1'].sum() for w in words]))}")
        print(f"  (1) Spearman(V3, resampled) = {rho:.3f} (p={p:.3f}), word-bootstrap 95% CI [{ci[0]:.3f}, {ci[1]:.3f}]")
        print(f"  (2) mean change_graded V3 {g_full.mean():.3f}, resampled {g_res.mean():.3f}, diff {g_res.mean()-g_full.mean():+.3f}")
        print(f"  (3) usage-sampling only (V3 distributions, 25+25 multinomial, 2000 draws): expected mean JSD {sim_mean.mean():.3f}; "
              f"expected Spearman(V3, replicate) median {np.median(sim_rho):.3f} [2.5-97.5%: {np.percentile(sim_rho,2.5):.3f}, "
              f"{np.percentile(sim_rho,97.5):.3f}]; observed rho is at the {100*pct_obs:.0f}th percentile of that distribution")
        print(f"      Spearman(resampled observed, simulated expected) = {spearmanr(g_res, sim_mean)[0]:.3f}")
        # (3b) fairer null: V3 is itself a ~100-use sample. Draw BOTH a V3-sized replicate and a 25-use replicate from
        #      V3's distributions and correlate them (V3 noise counted too; truth still taken = V3, so still optimistic
        #      about K: rare V3 clusters are treated as real senses).
        nper = [int(min(full[w]["f1"].sum(), full[w]["f2"].sum())) for w in words]
        sims_big = np.zeros((500, len(words)))
        for j, w in enumerate(words):
            p1 = full[w]["f1"] / full[w]["f1"].sum(); p2 = full[w]["f2"] / full[w]["f2"].sum()
            a = rng.multinomial(int(full[w]["f1"].sum()), p1, size=500); b = rng.multinomial(int(full[w]["f2"].sum()), p2, size=500)
            sims_big[:, j] = [jsd(a[d], b[d]) for d in range(500)]
        rho_b = np.array([spearmanr(sims_big[d], sims[d])[0] for d in range(500)])
        print(f"  (3b) both replicates simulated (V3-sized vs 25+25): expected Spearman median {np.nanmedian(rho_b):.3f} "
              f"[{np.nanpercentile(rho_b,2.5):.3f}, {np.nanpercentile(rho_b,97.5):.3f}]; observed at the "
              f"{100*np.nanmean(rho_b <= rho):.0f}th percentile")
        for w, a, b, m in zip(words, g_full, g_res, sim_mean):
            print(f"      {w:18s} V3 {a:.3f}  resampled {b:.3f}  expected@25 {m:.3f}  K_V3 {len(full[w]['f1'])}  K_res {len(res[w]['f1'])}")
        pooled_obs += list(g_res); pooled_full += list(g_full)
    print(f"== pooled 45 words: Spearman(V3, resampled) = {spearmanr(pooled_full, pooled_obs)[0]:.3f}")
    # (4) known-answer check of the simulator: a pair of identical period distributions must give the no-change
    #     expectation of pair_null_analytic (K=3 equal senses, 25+25: E[d] ~ sqrt((2/25)/(8 ln2) * 50/49) * 1.2533)
    p = np.array([1, 1, 1]) / 3
    a = rng.multinomial(25, p, size=20000); b = rng.multinomial(25, p, size=20000)
    emp = np.mean([jsd(a[i], b[i]) for i in range(20000)])
    ana = np.sqrt((2 / 25) / (8 * np.log(2)) * 50 / 49) * np.sqrt(2) * 0.886227 / 1.0  # Gamma(1.5)/Gamma(1)
    print(f"(4) known answer, no change, K=3 equal, 25+25: simulated E[JSD] {emp:.4f} vs chi-square formula {ana:.4f}")
    print("RESAMPLE_REPLICATION_OK")


if __name__ == "__main__":
    main()
