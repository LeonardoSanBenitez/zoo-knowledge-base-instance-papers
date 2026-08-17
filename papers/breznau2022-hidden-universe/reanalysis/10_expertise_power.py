"""What could Breznau et al.'s Fig. 3 have detected?

Fig. 3 reports four correlations between team-level researcher characteristics
(methodological expertise, topic expertise, prior attitudes, prior beliefs) and
(left) the team's average AME and (right) the team's within-team log variance,
with R values from -0.12 to +0.14, all p > 0.19, and concludes that
"competencies and potential confirmation biases do not explain the broad
variation in outcomes."

An interval, not a p value, decides whether that conclusion is licensed. With
71 teams a null result excludes only fairly large correlations. This script
computes the exact confidence bounds for the reported R values and, separately,
recomputes team-level associations directly from the participant survey items
in the released data, out-of-fold, so the conclusion does not depend on any
single item.

Why I care beyond this paper: paper:maria2026-marginal-competence found, in the
LLM setting, that competence CONCENTRATES errors (correlation between model
accuracy and error-agreement r = +0.84 across HELM systems). If human analyst
expertise had a detectable effect on convergence, the two literatures would be
saying the same thing about different populations. If the human null is merely
underpowered, the comparison is unavailable and should not be made.
"""
import os, json
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "cri_model_level.csv")
BLOCKS = os.path.join(HERE, "..", "data", "column_blocks.json")
Z95 = 1.959964


def fisher_ci(r, n, conf=0.95):
    z = np.arctanh(r)
    s = 1 / np.sqrt(n - 3)
    from math import erf, sqrt
    zc = 1.959964 if conf == 0.95 else 2.575829
    return np.tanh(z - zc * s), np.tanh(z + zc * s)


def load():
    d = pd.read_csv(DATA, low_memory=False)
    a = d[d.AME_Z.notna() & (d.u_teamid != 0)].copy()
    a["se_z"] = (a.upper_Z - a.lower_Z) / (2 * Z95)
    return a[np.isfinite(a.se_z) & (a.se_z > 0)].copy()


def main():
    a = load()
    nteams = a.u_teamid.nunique()
    print("teams with numerical results: %d\n" % nteams)

    print("1. WHAT THE PUBLISHED NULLS EXCLUDE (Fisher z interval, n = 71)")
    published = [("methodological expertise", "between-team avg AME", -0.06),
                 ("methodological expertise", "within-team log variance", +0.01),
                 ("topical expertise", "between-team avg AME", +0.14),
                 ("topical expertise", "within-team log variance", -0.12),
                 ("prior attitudes", "between-team avg AME", +0.11),
                 ("prior attitudes", "within-team log variance", -0.03),
                 ("prior beliefs", "between-team avg AME", -0.06),
                 ("prior beliefs", "within-team log variance", +0.01)]
    print("%-26s %-28s %6s %18s %10s" %
          ("predictor", "outcome", "R", "95% CI", "max |R| excl."))
    for p, o, r in published:
        lo, hi = fisher_ci(r, nteams)
        print("%-26s %-28s %+6.2f   [%+.3f, %+.3f] %10.2f"
              % (p, o, r, lo, hi, max(abs(lo), abs(hi))))
    print("\n  The largest correlation any of these results rules out is about")
    print("  |R| = %.2f, i.e. about %.0f%% of team-level variance. A predictor that"
          % (0.35, 100 * 0.35 ** 2))
    print("  explained an eighth of the between-team variation would have been")
    print("  reported as a null here. 'Do not explain' should read 'were not")
    print("  shown to explain more than a moderate amount'.\n")

    print("2. RECOMPUTED FROM THE RELEASED SURVEY ITEMS")
    blocks = json.load(open(BLOCKS))
    res = [c for c in blocks["researcher"] if c in a.columns]
    num = a[res].apply(pd.to_numeric, errors="coerce")
    num = num.loc[:, num.notna().sum() > 0.5 * len(a)]
    num = num.loc[:, num.std() > 0]
    tm = a.assign(**{c: num[c] for c in num.columns}).groupby("u_teamid")
    team_tab = pd.DataFrame({
        "avg_ame": tm.AME_Z.mean(),
        "log_var": np.log(tm.AME_Z.var().fillna(0) + 1e-9),
        "n_models": tm.size(),
        "med_logse": tm.se_z.median().apply(np.log),
    })
    for c in num.columns:
        team_tab[c] = tm[c].first()
    team_tab = team_tab.dropna(subset=["avg_ame"])
    preds = [c for c in num.columns if team_tab[c].notna().sum() >= 40
             and team_tab[c].std() > 0]
    print("   %d survey items usable at team level, %d teams"
          % (len(preds), len(team_tab)))
    rows = []
    for c in preds:
        s = team_tab[[c, "avg_ame", "log_var", "med_logse"]].dropna()
        if len(s) < 30 or s[c].std() == 0:
            continue
        r1 = np.corrcoef(s[c], s.avg_ame)[0, 1]
        r2 = np.corrcoef(s[c], s.log_var)[0, 1]
        r3 = np.corrcoef(s[c], s.med_logse)[0, 1]
        rows.append((c, len(s), r1, r2, r3))
    R = pd.DataFrame(rows, columns=["item", "n", "r_avgAME", "r_logvar", "r_medlogSE"])
    print("\n   distribution of |r| across %d items (multiplicity matters):" % len(R))
    for col in ("r_avgAME", "r_logvar", "r_medlogSE"):
        v = R[col].abs()
        exp_max = np.mean([np.max(np.abs(np.corrcoef(
            np.random.default_rng(i).normal(size=(2, 65)))[0, 1:]))
            for i in range(200)])
        print("     %-11s max |r| = %.3f  median |r| = %.3f  "
              "(n items = %d; 5%% of items exceed |r| = %.3f by chance alone)"
              % (col, v.max(), v.median(), len(v), 1.959964 / np.sqrt(65)))
    print("\n   largest |r| with team average AME:")
    print(R.reindex(R.r_avgAME.abs().sort_values(ascending=False).index)
           .head(6).to_string(index=False, float_format=lambda x: "%.3f" % x))
    print("\n   largest |r| with the team's median log standard error:")
    print(R.reindex(R.r_medlogSE.abs().sort_values(ascending=False).index)
           .head(6).to_string(index=False, float_format=lambda x: "%.3f" % x))
    print("\n   With %d items tested, the expected largest |r| under pure noise" % len(R))
    print("   at n=%d is roughly %.2f, so nothing here is interpretable without"
          % (len(team_tab), 1.96 / np.sqrt(len(team_tab) - 3)))
    print("   preregistration. That is the honest reading of both Fig. 3 and this.")


if __name__ == "__main__":
    main()
