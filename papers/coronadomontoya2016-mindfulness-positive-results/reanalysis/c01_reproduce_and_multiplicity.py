"""Coronado-Montoya et al. (2016, PLoS ONE 11(4):e0153220) -- reproduce Table 1 from S3 Appendix, then ask what
the 'expected number of positive trials' should be under the paper's OWN definition of positive.

The paper's definition (Kyzas method): a trial is positive if AT LEAST ONE between-groups mental-health outcome in
the abstract is significant (or, with no between-groups result, a within-group one: 14 of 108). Its expected count
(65.7) sums single-test power at d = .55. With k outcomes per abstract, P(at least one significant) exceeds
single-test power even with no reporting bias at all. k is not in the paper's appendices, so it is swept.

Usage: python c01_reproduce_and_multiplicity.py <s003.docx>    Writes out/c01.json
"""
import json, os, re, sys, zipfile
import numpy as np
from scipy import stats

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"); os.makedirs(OUT, exist_ok=True)
x = zipfile.ZipFile(sys.argv[1]).read("word/document.xml").decode("utf8")
rows = []
for tr in re.findall(r"<w:tr[ >].*?</w:tr>", x, re.S):
    cells = [re.sub(r"<[^>]+>", "", "".join(re.findall(r"<w:t[^>]*>[^<]*</w:t>", tc))) for tc in re.findall(r"<w:tc>.*?</w:tc>", tr, re.S)]
    rows.append(cells)
hdr, body = rows[0], rows[1:]
T = []
for r in body:
    m = re.match(r"\s*(\d+)\s*/\s*(\d+)", r[5])
    T.append({"study": r[0], "abstract_pos": r[1].strip(), "concl": r[4].strip(), "n1": int(m.group(1)), "n2": int(m.group(2)),
              "power_pub": float(r[6]), "registered": r[7].strip()})
n1 = np.array([t["n1"] for t in T]); n2 = np.array([t["n2"] for t in T]); pw_pub = np.array([t["power_pub"] for t in T]) / 100
pos = np.array([t["abstract_pos"].lower().startswith("pos") for t in T])


def power(d, a, b, alpha=0.05):
    df = a + b - 2; nc = d * np.sqrt(a * b / (a + b)); tc = stats.t.isf(alpha / 2, df)
    p = stats.nct.sf(tc, df, nc) + stats.nct.cdf(-tc, df, nc)
    return np.nan_to_num(p, nan=1.0)  # scipy's nct returns NaN far in the tail (power ~ 1 there)


res = {"n_trials": len(T), "n_positive_abstract": int(pos.sum()),
       "conclusion_counts": {k: int(sum(t["concl"] == k for t in T)) for k in set(t["concl"] for t in T)}}
pw = power(0.55, n1, n2)
res["max_abs_diff_power_vs_published"] = round(float(np.max(np.abs(pw - pw_pub))), 4)
res["expected_positive_d.55"] = round(float(pw.sum()), 1)  # paper 65.7
bins = [(0, .25), (.25, .5), (.5, .75), (.75, 1.01)]
res["table1"] = [{"bin": f"{a}-{b}", "n": int(((pw_pub >= a) & (pw_pub < b)).sum()), "observed": int(pos[(pw_pub >= a) & (pw_pub < b)].sum()),
                  "expected": round(float(pw_pub[(pw_pub >= a) & (pw_pub < b)].sum()), 1)} for a, b in bins]
from scipy.optimize import brentq
res["d_for_expected_108"] = round(brentq(lambda d: power(d, n1, n2).sum() - 108, 0.1, 2), 3)  # paper 1.03
res["d_for_expected_94_between_groups_only"] = round(brentq(lambda d: power(d, n1, n2).sum() - 94, 0.1, 2), 3)


# P(at least one of k equicorrelated outcomes significant in the effect direction OR either direction?)
# The paper counts significant between-groups outcomes "in favour of MBT"; use the one-sided-in-favour version.
def p_any(d, a, b, k, rho, reps=20000, rng=np.random.default_rng(1)):
    """Monte Carlo with z-approximation: z_j = d*sqrt(n_h/2)... per outcome, equicorrelated rho; P(max z_j > 1.96)."""
    ncp = d * np.sqrt(a * b / (a + b))
    common = rng.normal(size=(reps, 1)); idio = rng.normal(size=(reps, k))
    z = ncp + np.sqrt(rho) * common + np.sqrt(1 - rho) * idio
    return float(np.mean(z.max(1) > 1.96))


grid = {}
for k in (1, 2, 3, 4, 6):
    for rho in (0.3, 0.5, 0.7):
        for d in (0.0, 0.2, 0.3, 0.44, 0.55):
            e = sum(p_any(d, a, b, k, rho, reps=4000) for a, b in zip(n1, n2))
            grid[f"k{k}_rho{rho}_d{d}"] = round(e, 1)
res["expected_positive_under_honest_multiplicity"] = grid
# which (k, rho) reach 108 at the AHRQ upper bound d = .44 and at the paper's d = .55?
res["reach_108"] = sorted([kk for kk, v in grid.items() if v >= 108])
res["reach_94"] = sorted([kk for kk, v in grid.items() if v >= 94])
print(json.dumps({k: v for k, v in res.items() if k != "expected_positive_under_honest_multiplicity"}, indent=1))
for kk, v in grid.items():
    print(kk, v)
json.dump(res, open(os.path.join(OUT, "c01.json"), "w"), indent=1)
