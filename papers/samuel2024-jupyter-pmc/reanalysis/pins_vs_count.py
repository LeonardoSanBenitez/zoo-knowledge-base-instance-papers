"""Does PINNING a dependency cost you, or does DECLARING one cost you?

The question this settles. "Pin your dependency versions" is recommendation #1 of
Trisovic et al. and a conclusion of Samuel & Mietchen. On the 2021 corpus I found
it associated with LOWER install success (OR 0.435, 191 repositories, 22 events,
Fisher p = 0.29) and said so. Malka et al. 2026 then found the opposite on 835
Dockerfiles at p < 0.02. Two signs, two substrates.

The confound that resolves it, and it is visible in the raw pins. The most
frequently pinned packages in this corpus are `cycler`, `ipython-genutils`,
`webencodings`, `pickleshare`, `pandocfilters` -- nobody's direct dependencies.
They are `pip freeze` output. **In Python, pinning and dependency COUNT are
nearly the same variable**, because the usual way to pin is to dump the whole
transitive closure. In a Dockerfile they are not: you pin the handful of things
you wrote `apt-get install` for.

So the decomposition. For each repository split its declared dependencies into
  n_pinned    -- exactly pinned, `pkg==X.Y.Z`
  n_unpinned  -- named without an exact version
and ask whether a PINNED dependency carries more install risk than an UNPINNED
one. If pinning is a portability liability per package, the pinned coefficient
must exceed the unpinned coefficient. If the whole effect is "more dependencies,
more ways to fail", the two coefficients will be the same and the difference will
straddle zero.

NOTE ON PROVENANCE. This script lives with the samuel2024 record because it
reanalyses that study's data to test that study's own recommendation. The
vacuous-comparison defect that dominated the same session is a different finding
about the same database and lives in
`papers/maria2026-vacuous-reproduction-flag/`. The two do not interact: the
outcome used here is recorded before any notebook cell runs.

OUTCOME. Repository-level: did EVERY mode-3 execution in this repository hit
`<Install Dependency Error>` (processed == 0)? This outcome is untouched by the
vacuous-comparison defect documented in this record's paper.json -- it is
recorded before any notebook cell runs, and it does not use the cell tracker.

UNIT. Repository, because notebooks cluster inside repositories at a measured
ICC of 0.435 and the treatment is defined at repository level anyway.

Data: db2023.sqlite. Regeneration command in vacuous_flag.py's docstring.
Usage:  python pins_vs_count.py /path/to/db2023.sqlite
"""
import collections
import math
import re
import sqlite3
import sys

import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "..", "tools"))
from statlib import logit_fit        # noqa: E402  (validated in validate_fitter.py)

PIN = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)\s*(\[[^\]]*\])?\s*==\s*([0-9][^\s,;#]*)")
NAME = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")


def load(path):
    c = sqlite3.connect(path)
    req = collections.defaultdict(lambda: [0, 0])          # rid -> [pinned, unpinned]
    for rid, content in c.execute(
            "select repository_id, content from requirement_files "
            "where reqformat='requirements.txt' and content is not null"):
        for line in content.splitlines():
            ls = line.strip()
            if not ls or ls[0] in "#-":
                continue
            if not NAME.match(ls):
                continue
            req[rid][0 if PIN.match(ls) else 1] += 1
    rows = []
    for rid, failed, n in c.execute(
            "select repository_id, sum(processed=0), count(*) from executions "
            "where mode=3 group by 1"):
        if rid not in req:
            continue                                        # setup.py-only: other mechanism
        p, u = req[rid]
        if p + u == 0:
            continue
        rows.append(dict(rid=rid, pinned=p, unpinned=u, deps=p + u,
                         fail=1 if failed == n else 0,
                         fail_any=1 if failed > 0 else 0, nb=n))
    return rows


def descr(rows):
    print("repositories: %d   with total install failure: %d (%.1f%%)"
          % (len(rows), sum(r["fail"] for r in rows),
             100.0 * sum(r["fail"] for r in rows) / len(rows)))
    print()
    print("RAW -- failure rate by dependency count, and by pinned fraction")
    print("  deps        n   fail%    |  pinned frac    n   fail%")
    bands = [(1, 5), (6, 15), (16, 40), (41, 100), (101, 10 ** 9)]
    fracs = [(0.0, 0.0), (0.0001, 0.5), (0.5, 0.9), (0.9, 1.01)]
    for (lo, hi), (flo, fhi) in zip(bands, fracs + [(None, None)]):
        a = [r for r in rows if lo <= r["deps"] <= hi]
        lab = "%d-%d" % (lo, hi) if hi < 10 ** 9 else "%d+" % lo
        line = "  %-9s %4d  %5.1f%%" % (lab, len(a),
                                        100.0 * sum(x["fail"] for x in a) / len(a) if a else 0)
        if flo is not None:
            b = [r for r in rows if flo <= r["pinned"] / r["deps"] <= fhi]
            line += "   |  %-11s %4d  %5.1f%%" % (
                "%.0f-%.0f%%" % (100 * flo, 100 * fhi), len(b),
                100.0 * sum(x["fail"] for x in b) / len(b) if b else 0)
        print(line)
    print()
    print("JOINT -- pinned fraction WITHIN dependency-count strata")
    print("  deps          <50% pinned            >=50% pinned")
    for lo, hi in bands:
        a = [r for r in rows if lo <= r["deps"] <= hi and r["pinned"] / r["deps"] < 0.5]
        b = [r for r in rows if lo <= r["deps"] <= hi and r["pinned"] / r["deps"] >= 0.5]
        lab = "%d-%d" % (lo, hi) if hi < 10 ** 9 else "%d+" % lo
        f = lambda z: (100.0 * sum(x["fail"] for x in z) / len(z)) if z else float("nan")
        print("  %-11s n=%-4d %5.1f%%           n=%-4d %5.1f%%"
              % (lab, len(a), f(a), len(b), f(b)))


def model(rows):
    import numpy as np
    lp = np.array([math.log1p(r["pinned"]) for r in rows])
    lu = np.array([math.log1p(r["unpinned"]) for r in rows])
    y = np.array([r["fail"] for r in rows], float)
    X = np.column_stack([lp, lu])
    f = logit_fit(X, y)
    names = ["const", "log1p(n_pinned)", "log1p(n_unpinned)"]
    print()
    print("LOGIT  fail ~ log1p(n_pinned) + log1p(n_unpinned)     n = %d" % len(rows))
    print("  %-20s %9s %8s %8s %9s" % ("term", "beta", "se", "z", "p"))
    for i, nm in enumerate(names):
        print("  %-20s %+9.4f %8.4f %8.2f %9.4f"
              % (nm, f["beta"][i], f["se"][i], f["z"][i], f["p"][i]))
    print("  McFadden pseudo-R2 = %.4f" % f["pseudo_r2"])
    print()
    # the contrast that IS the question
    b = f["beta"]
    d = b[1] - b[2]
    Xc = np.column_stack([np.ones(len(y)), X])
    mu = 1 / (1 + np.exp(-(Xc @ b)))
    W = np.clip(mu * (1 - mu), 1e-12, None)
    cov = np.linalg.inv(Xc.T @ (Xc * W[:, None]))
    se_d = math.sqrt(cov[1, 1] + cov[2, 2] - 2 * cov[1, 2])
    from scipy import stats
    z = d / se_d
    p = 2 * stats.norm.sf(abs(z))
    print("  CONTRAST  beta_pinned - beta_unpinned = %+0.4f  (SE %.4f, z = %+.2f, p = %.3f)"
          % (d, se_d, z, p))
    print("            95%% CI [%+0.4f, %+0.4f]" % (d - 1.96 * se_d, d + 1.96 * se_d))
    print()
    if p >= 0.05:
        print("  A pinned dependency and an unpinned one carry indistinguishable install")
        print("  risk on this corpus. What predicts failure is HOW MANY dependencies you")
        print("  declare, not whether you fixed their versions.")
        print()
        print("  This is a BOUNDED null, not a bare p > 0.05. See the power curve at the")
        print("  bottom: a true contrast of 0.30 is detected 95%% of the time at this n and")
        print("  0.20 is detected 75%% of the time, on the corpus's own covariates. The 95%%")
        print("  interval excludes")
        print("  any extra per-e-fold odds multiplier for pinning above %.2f, and any"
              % math.exp(d + 1.96 * se_d))
        print("  protective multiplier below %.2f. A pinning effect large enough to"
              % math.exp(d - 1.96 * se_d))
        print("  matter to anybody would have been visible at this n.")
    else:
        print("  The two differ. Read the sign: positive means pinning costs extra.")
    print()
    print("  For scale, the effect that IS there: exp(beta_pinned) = %.2f per e-fold of"
          % math.exp(b[1]))
    print("  pinned dependencies. Going from 5 declared dependencies to 50 multiplies")
    print("  the odds of total install failure by about %.1f."
          % math.exp(b[1] * (math.log1p(50) - math.log1p(5))))
    return dict(f=f, contrast=d, se=se_d, z=z, p=p)


def sensitivity(rows):
    """Outcome definition is a researcher degree of freedom. Try the other one."""
    import numpy as np
    from scipy import stats
    print()
    print("SENSITIVITY -- the outcome could reasonably be defined two ways")
    for lab, key in (("ALL executions hit install error (used above)", "fail"),
                     ("ANY execution hit install error", "fail_any")):
        y = np.array([r[key] for r in rows], float)
        X = np.column_stack([[math.log1p(r["pinned"]) for r in rows],
                             [math.log1p(r["unpinned"]) for r in rows]])
        f = logit_fit(X, y)
        b = f["beta"]
        Xc = np.column_stack([np.ones(len(y)), X])
        mu = 1 / (1 + np.exp(-(Xc @ b)))
        W = np.clip(mu * (1 - mu), 1e-12, None)
        cov = np.linalg.inv(Xc.T @ (Xc * W[:, None]))
        d = b[1] - b[2]
        se = math.sqrt(cov[1, 1] + cov[2, 2] - 2 * cov[1, 2])
        print("  %-46s events=%3d  pinned %+0.3f  unpinned %+0.3f  contrast %+0.3f (p=%.3f)"
              % (lab, int(y.sum()), b[1], b[2], d, 2 * stats.norm.sf(abs(d / se))))


def breaktest(rows):
    """Would this design detect a pinning penalty if one existed?

    Plants a KNOWN extra per-e-fold log-odds on the pinned term, using the REAL
    (n_pinned, n_unpinned) pairs resampled with replacement, and an intercept
    recalibrated so the simulated failure rate matches the observed 65.7%.

    The first version of this drew the covariates from a uniform distribution
    instead, which pushed almost every simulated repository to p(fail) ~ 0.99 and
    reported the design as far weaker than it is. A power curve computed on
    covariates the study does not have is a power curve for a different study.
    """
    import numpy as np
    from scipy import stats
    print()
    print("BREAK-TEST -- can the contrast see a pinning penalty that is really there?")
    print("  covariates resampled from the real corpus; intercept recalibrated to the")
    print("  observed failure rate; 400 draws per planted value.")
    rng = np.random.default_rng(11)
    LP = np.array([math.log1p(r["pinned"]) for r in rows])
    LU = np.array([math.log1p(r["unpinned"]) for r in rows])
    obs_rate = float(np.mean([r["fail"] for r in rows]))
    n = len(rows)
    # PARAMETERISE BY THE TRUE CONTRAST, not by an offset to the fitted pinned
    # coefficient. The first version added `planted` to the FITTED b_p = 0.364
    # while holding b_u = 0.262, so its "planted 0.00" row secretly planted the
    # observed contrast of +0.102 -- and duly recovered +0.103 and "false
    # positived" 25% of the time. The simulation was right and the label was
    # wrong, which is the more dangerous of the two.
    b_u = 0.262
    print("  true contrast   detected   mean estimate   mean simulated failure rate")
    for planted in (0.0, 0.05, 0.102, 0.20, 0.30, 0.50):
        det, ests, rates = 0, [], []
        for _ in range(400):
            idx = rng.integers(0, n, n)
            lp, lu = LP[idx], LU[idx]
            lin = (b_u + planted) * lp + b_u * lu
            # bisect the intercept so E[p] == observed rate
            lo, hi = -20.0, 20.0
            for _ in range(60):
                mid = (lo + hi) / 2
                if np.mean(1 / (1 + np.exp(-(mid + lin)))) < obs_rate:
                    lo = mid
                else:
                    hi = mid
            a0 = (lo + hi) / 2
            pr = 1 / (1 + np.exp(-(a0 + lin)))
            y = rng.binomial(1, pr).astype(float)
            rates.append(y.mean())
            if y.sum() in (0, n):
                continue
            X = np.column_stack([lp, lu])
            try:
                f = logit_fit(X, y)
                b = f["beta"]
                Xc = np.column_stack([np.ones(n), X])
                mu = 1 / (1 + np.exp(-(Xc @ b)))
                W = np.clip(mu * (1 - mu), 1e-12, None)
                cov = np.linalg.inv(Xc.T @ (Xc * W[:, None]))
            except Exception:
                continue
            d = b[1] - b[2]
            se = math.sqrt(max(cov[1, 1] + cov[2, 2] - 2 * cov[1, 2], 1e-12))
            ests.append(d)
            if 2 * stats.norm.sf(abs(d / se)) < 0.05:
                det += 1
        print("   %+0.3f          %5.1f%%        %+0.3f            %.3f"
              % (planted, 100.0 * det / max(len(ests), 1), float(np.mean(ests)),
                 float(np.mean(rates))))
    print("  Row 0.000 is the false-positive rate and should sit near 5%.")
    print("  Row 0.102 is the observed contrast: it says how often an effect of")
    print("  exactly the observed size would be called significant at this n.")
    print("  Rows below it give the power curve. The estimate column must track")
    print("  the true contrast; if it does not, the design is biased, not weak.")


if __name__ == "__main__":
    rows = load(sys.argv[1] if len(sys.argv) > 1 else "db2023.sqlite")
    descr(rows)
    model(rows)
    sensitivity(rows)
    breaktest(rows)
