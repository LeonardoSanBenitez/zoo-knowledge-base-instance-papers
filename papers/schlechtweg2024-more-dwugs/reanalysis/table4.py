"""Reproduce Table 4 of Schlechtweg et al. 2024 (More DWUGs): JS distance between the sense distribution of each
resampled word and the same word in DWUG V1 / V2, "trimming the longer distribution to match the shorter one".
Printed columns read as min / mean / max over words (text: averages 0.08-0.22, maximum 0.48, zero values exist).

    python papers/schlechtweg2024-more-dwugs/reanalysis/table4.py > papers/schlechtweg2024-more-dwugs/reanalysis/table4.out.txt

Interpretation tried (the paper does not specify more): the POOLED cluster_prob_dist from stats/opt/stats_groupings.csv
(sorted by cluster size, as the files list them), trimmed to the shorter length, renormalised (scipy does), base 2.
Variant B: per-period distributions, averaged over the two periods.
Break check: the distance is computed on frequency-sorted profiles, so two words with no sense in common but the same
profile get 0, and any word with one cluster on either side gets 0 by construction. Counted below.
Also: a shuffled-word control (resampled word i vs version word j != i): if Table 4's numbers are not clearly below this,
they do not show that the same senses were found.
"""
import ast
import csv
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.spatial.distance import jensenshannon

KB = Path(__file__).resolve().parents[4]
ROOT = Path(subprocess.run([sys.executable, str(KB / "tools" / "assets.py"), "path",
                            "paper-downloads/schlechtweg2024-more-dwugs"], capture_output=True, text=True,
                           check=True).stdout.strip()) / "data"
RES = {"de": "12670698_dwug_de_resampled/dwug_de_resampled", "en": "14025941_dwug_en_resampled/dwug_en_resampled",
       "sv": "14026615_dwug_sv_resampled/dwug_sv_resampled"}
VER = {"v1": "dwug_{l}_v1/dwug_{l}", "v2": "dwug_{l}_v2/dwug_{l}", "v3": None}
V3 = {"de": "14028509_dwug_de/dwug_de", "en": "14028531_dwug_en/dwug_en", "sv": "14028906_dwug_sv/dwug_sv"}
PRINTED = {("de", "v1"): (.0, .10, .28), ("de", "v2"): (.0, .08, .20), ("en", "v1"): (.11, .22, .45),
           ("en", "v2"): (.0, .19, .42), ("sv", "v1"): (.0, .19, .48), ("sv", "v2"): (.0, .10, .42)}


def load(rel):
    out = {}
    with open(ROOT / rel / "stats" / "opt" / "stats_groupings.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            out[r["lemma"]] = {k: np.array(ast.literal_eval(r[k]), float)
                               for k in ("cluster_prob_dist", "cluster_freq_dist1", "cluster_freq_dist2")}
    return out


def trim_jsd(p, q):
    p = np.sort(p)[::-1]; q = np.sort(q)[::-1]; k = min(len(p), len(q))
    p, q = p[:k], q[:k]
    if p.sum() == 0 or q.sum() == 0:
        return np.nan
    return float(jensenshannon(p, q, base=2))


def summ(v):
    v = np.array([x for x in v if not np.isnan(x)])
    return f"{v.min():.2f} {v.mean():.2f} {v.max():.2f}"


for lang in ("de", "en", "sv"):
    res = load(RES[lang])
    for ver in ("v1", "v2", "v3"):
        full = load(V3[lang] if ver == "v3" else VER[ver].format(l=lang))
        words = sorted(set(res) & set(full))
        a = [trim_jsd(res[w]["cluster_prob_dist"], full[w]["cluster_prob_dist"]) for w in words]
        b = [np.nanmean([trim_jsd(res[w][c], full[w][c]) for c in ("cluster_freq_dist1", "cluster_freq_dist2")]) for w in words]
        k1 = sum(min(len(res[w]["cluster_prob_dist"]), len(full[w]["cluster_prob_dist"])) == 1 for w in words)
        zeros = sum(x == 0 for x in a)
        rng = np.random.default_rng(0)
        sh = []
        for _ in range(200):
            perm = rng.permutation(len(words))
            while len(words) > 1 and np.any(perm == np.arange(len(words))):
                perm = rng.permutation(len(words))
            sh.append(np.nanmean([trim_jsd(res[words[i]]["cluster_prob_dist"], full[words[j]]["cluster_prob_dist"])
                                  for i, j in enumerate(perm)]))
        pr = PRINTED.get((lang, ver))
        print(f"{lang.upper()} {ver}: n={len(words)}  pooled trimmed min/mean/max {summ(a)}  | per-period {summ(b)}  | "
              f"printed {pr}  | zeros {zeros} (min K = 1 in {k1})  | shuffled-word control mean {np.mean(sh):.2f} "
              f"[{np.percentile(sh, 2.5):.2f}, {np.percentile(sh, 97.5):.2f}]")
print("TABLE4_OK")
