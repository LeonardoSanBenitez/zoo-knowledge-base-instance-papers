#!/usr/bin/env python3
"""
03 -- The Power-of-Noise effect as a NONSTANDARD ERROR.

THE IMPORT
----------
Menkveld et al. 2024 (J. Finance 79(3):2339-2390, 164 research teams) split the
dispersion of a reported number into

    standard error     -- dispersion from the DATA-generating process
    nonstandard error  -- dispersion from the EVIDENCE-generating process,
                          i.e. from the analyst's defensible choices,
                          measured as the IQR across teams, robust on purpose
                          because the across-team distribution has fat tails.

I recorded that record on 2026-08-12 (papers/menkveld2024-nonstandard-errors) and
found tau / median-SE = 1.72 in finance (164 teams) and 1.72 in sociology
(Breznau et al. 2022 CRI, 71 teams). Three-significant-figure agreement across
two fields is luck; the order of magnitude is the finding.

This script asks the obvious next question and, as far as I can find, an
unasked one: WHAT IS THE NONSTANDARD ERROR OF A RAG RESULT?

Mazuryk et al. 2026 is the right corpus for it without knowing that it is. It is
not a many-analysts study -- one team made every choice -- so it is a
SPECIFICATION CURVE, and the correct comparator in my earlier work is Breznau's
model level (1,253 models, IDR/IQR = 2.79), not the team level (IDR/IQR = 2.08).
That distinction is load-bearing and I keep it explicit throughout.

Estimand: the Power-of-Noise effect
        E = acc(14 random docs) - acc(0 random docs)
on a fixed set of n = 10,000 NQ-open questions, gold document Near.

Specification set: every (model, configuration) pair the paper reports on the
Random-Near setup with all four document counts. Nineteen of them. Each is a
choice the authors themselves argue is defensible -- indeed the paper's thesis is
that the *later* configurations are the MORE defensible ones.

Author: maria, 2026-08-12
"""
import importlib.util
import itertools
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("t", os.path.join(HERE, "01_transcribe_tables.py"))
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)

N = 10000
KS = [0, 10, 12, 14]
rng = np.random.default_rng(20260812)

# ---------------------------------------------------------------- build specs
SPECS = {}
for (m, c), d in t.TABLE6.items():
    SPECS[(m, c)] = dict(d)
for (m, c), d in t.TABLE5.items():
    if c in ("Instruct", "Max"):          # Base already present via Table 6
        SPECS[(m, c)] = dict(d)

SPECS = {k: v for k, v in SPECS.items() if all(kk in v for kk in KS)}
names = sorted(SPECS)
print(f"{len(names)} specifications, each measured at k = {KS} on n = {N:,} items\n")


def se_unpaired(p1, p2, n=N):
    """Upper bound on the standard error of a PAIRED difference of proportions.

    The two conditions share the 10,000 questions, so the true (McNemar) SE is
    smaller than this whenever the two are positively correlated, which they
    unavoidably are. Using the bound makes every NSE/SE ratio below CONSERVATIVE
    -- the real ratio is larger. The paper does not publish the discordance
    counts that would let anyone compute the exact value, which is itself worth
    noting: an accuracy table without a discordance table cannot be tested.
    """
    return float(np.sqrt(p1 * (1 - p1) / n + p2 * (1 - p2) / n))


rows = []
for key in names:
    d = SPECS[key]
    E = d[14] - d[0]
    slope = np.polyfit(KS, [d[k] for k in KS], 1)[0]          # per document
    rows.append(dict(model=key[0], config=key[1], E=E, slope=slope,
                     acc0=d[0], acc14=d[14],
                     se=se_unpaired(d[0], d[14]),
                     mean_acc=float(np.mean([d[k] for k in KS]))))

E = np.array([r["E"] for r in rows])
SE = np.array([r["se"] for r in rows])
SL = np.array([r["slope"] for r in rows])

print(f"{'model':<9}{'config':<10}{'acc@0':>8}{'acc@14':>8}{'E':>9}{'SE':>8}{'E/SE':>8}")
for r in sorted(rows, key=lambda r: r["E"]):
    print(f"{r['model']:<9}{r['config']:<10}{r['acc0']:>8.4f}{r['acc14']:>8.4f}"
          f"{r['E']:>+9.4f}{r['se']:>8.4f}{r['E']/r['se']:>8.1f}")


def iqr(x):
    return float(np.percentile(x, 75) - np.percentile(x, 25))


def idr(x):
    return float(np.percentile(x, 90) - np.percentile(x, 10))


print("\n" + "=" * 78)
print("1. THE NONSTANDARD ERROR")
print("=" * 78)
nse = iqr(E)
sd = float(np.std(E, ddof=1))
med_se = float(np.median(SE))
# DerSimonian-Laird tau^2 on the 19 estimates with their (bounded) SEs.
w = 1.0 / SE**2
mu = float(np.sum(w * E) / np.sum(w))
Q = float(np.sum(w * (E - mu) ** 2))
dfree = len(E) - 1
C = float(np.sum(w) - np.sum(w**2) / np.sum(w))
tau2 = max(0.0, (Q - dfree) / C)
tau = tau2 ** 0.5
print(f"  specifications                       {len(E)}")
print(f"  median  E                            {np.median(E):+.4f}")
print(f"  mean    E                            {E.mean():+.4f}")
print(f"  NONSTANDARD ERROR (IQR of E)         {nse:.4f}   [Menkveld's definition]")
print(f"  SD of E                              {sd:.4f}")
print(f"  median STANDARD error of one E       {med_se:.4f}   [upper bound, see se_unpaired]")
print(f"  Cochran Q                            {Q:,.0f} on {dfree} df")
print(f"  DerSimonian-Laird tau                {tau:.4f}")
print()
print(f"  NSE / median SE                      {nse/med_se:6.1f}")
print(f"  tau / median SE                      {tau/med_se:6.1f}   <-- the cross-corpus quantity")
print(f"""
  For comparison, the same quantity as I computed it on 2026-08-12:
      finance,   Menkveld 164 teams, 6 hypotheses      tau/median SE =   1.72
      sociology, Breznau CRI 71 teams                  tau/median SE =   1.72
      RAG,       Mazuryk 19 specifications             tau/median SE = {tau/med_se:6.2f}

  Two orders of magnitude. That is the result, and it is not a subtlety of
  estimation -- it survives any reasonable definition of either term, because
  the numerator is tenths and the denominator is thousandths.
""")

print("=" * 78)
print("2. WHY THE RATIO IS SO LARGE -- and why that is not a trick")
print("=" * 78)
print(f"""
  The denominator is small BY DESIGN, and this is the structural difference
  between a computational multiverse and a many-analysts study:

  * In Breznau's CRI and in Menkveld's fincap, every team chose its own sample.
    Sample size, exclusions and clustering varied across teams, so the standard
    error varied across teams by a factor of five. My 2026-08-12 grouped-CV
    result was that team identity predicts log(SE) with R^2 = 0.194 +- 0.024 and
    predicts the ESTIMATE with R^2 = -0.005. Analytic choice moved precision and
    not the answer.

  * Here every specification is evaluated on the identical 10,000 questions.
    The standard error is pinned to sqrt(p(1-p)/n) and can only move between
    {SE.min():.4f} and {SE.max():.4f}: a range of {SE.max()/SE.min():.2f}x, entirely a
    function of where accuracy sits on the p(1-p) parabola. There is no
    precision channel to absorb anything.

  So the RAG multiverse is the mirror image of the sociology one. Analytic
  choice there could only move precision; analytic choice here can ONLY move the
  estimate. Neither field is 'worse'. But the tools imported from one to the
  other must be re-derived, and the reflex of reporting a heterogeneity ratio
  without saying which channel was available is how that gets missed.
""")

print("=" * 78)
print("3. THE CONCLUSION SPLIT (Breznau's Fig. 2 applied to RAG)")
print("=" * 78)
z = E / SE
pos = int(np.sum(z > 2.576))          # p < 0.01 two-sided
neg = int(np.sum(z < -2.576))
nul = len(z) - pos - neg
print(f"  noise SIGNIFICANTLY helps   (z > +2.58):  {pos:>2}/{len(z)}  {100*pos/len(z):5.1f}%")
print(f"  no significant effect                  :  {nul:>2}/{len(z)}  {100*nul/len(z):5.1f}%")
print(f"  noise SIGNIFICANTLY hurts   (z < -2.58):  {neg:>2}/{len(z)}  {100*neg/len(z):5.1f}%")
print(f"""
  Breznau et al. 2022, 1,253 sociology models on one hypothesis, unweighted:
      25.4% significant negative / 57.7% null / 16.9% significant positive.
  Here:
      {100*pos/len(z):.1f}% significant positive / {100*nul/len(z):.1f}% null / {100*neg/len(z):.1f}% significant negative.

  The RAG multiverse is far MORE polarised than the sociology one: almost
  nothing lands in the null band, because n = 10,000 makes the null band about
  {2*2.576*med_se:.3f} wide and the specifications are spread over {E.max()-E.min():.3f}. A
  many-analysts study in sociology produces mostly nulls; a specification curve
  in RAG produces mostly significant results pointing both ways. Same
  underlying situation -- the specification determines the answer -- expressed
  as an epidemic of nulls in one field and an epidemic of confident
  contradictions in the other. The p-value is doing nothing in either.
""")

print("=" * 78)
print("4. DOES THE FUNCTIONAL MATTER? (six-functionals lesson, ported)")
print("=" * 78)
print("""  On 2026-08-12 I found that six defensible functionals of the CRI estimates
  implied tau from 0.0012 to 0.0160 -- a 13x range from the choice of what to
  summarise. Same check here, on two functionals of the same 19 runs:""")
for lbl, v in [("E = acc(14) - acc(0)", E), ("OLS slope in k, per doc", SL)]:
    print(f"    {lbl:<26} median {np.median(v):+.5f}  IQR {iqr(v):.5f}  "
          f"sign(median) {'+' if np.median(v) > 0 else '-'}")
agree = int(np.sum(np.sign(E) == np.sign(SL)))
print(f"    the two functionals agree on the SIGN in {agree}/{len(E)} specifications")
print("""    -- so the functional choice is a real but second-order degree of freedom
       here, unlike in CRI. Worth recording because it is the check that would
       have caught me if it were first-order.""")

print("=" * 78)
print("5. WHICH CHOICE CARRIES THE VARIANCE? (variance decomposition)")
print("=" * 78)


def r2_from_factor(y, labels):
    """One-way R^2: between-group SS over total SS. No shrinkage, no CV --
    this is descriptive and with 19 points it must not be read as predictive.
    Script 05 does the honest out-of-sample version."""
    y = np.asarray(y, float)
    grand = y.mean()
    sst = float(((y - grand) ** 2).sum())
    if sst == 0:
        return float("nan")
    ssb = 0.0
    for g in set(labels):
        idx = [i for i, l in enumerate(labels) if l == g]
        ssb += len(idx) * (y[idx].mean() - grand) ** 2
    return float(ssb / sst)


models = [r["model"] for r in rows]
configs = [r["config"] for r in rows]
print(f"  variance of E explained by MODEL   (5 levels): R^2 = {r2_from_factor(E, models):.3f}")
print(f"  variance of E explained by CONFIG  (5 levels): R^2 = {r2_from_factor(E, configs):.3f}")
lse = np.log(SE)
print(f"  variance of log SE explained by MODEL        : R^2 = {r2_from_factor(lse, models):.3f}")
print(f"  variance of log SE explained by CONFIG       : R^2 = {r2_from_factor(lse, configs):.3f}")
print(f"""
  In CRI the two rows were R^2 = -0.005 (estimate) and 0.194 (log SE). Here they
  are effectively swapped, and the log-SE row is an artifact: SE is a
  deterministic function of accuracy, so 'explaining' log SE is just explaining
  accuracy through the p(1-p) parabola. It is reported to show the channel is
  closed, not because it is informative.
""")

print("=" * 78)
print("6. TAIL SHAPE -- IDR/IQR, and an honest word about n = 19")
print("=" * 78)
r = idr(E) / iqr(E)
boot = []
for _ in range(20000):
    s = rng.choice(E, size=len(E), replace=True)
    q = iqr(s)
    if q > 0:
        boot.append(idr(s) / q)
boot = np.array(boot)
gauss = []
for _ in range(20000):
    s = rng.normal(size=len(E))
    q = iqr(s)
    if q > 0:
        gauss.append(idr(s) / q)
gauss = np.array(gauss)
print(f"  observed IDR/IQR of E                 {r:.2f}")
print(f"  bootstrap 90% interval                [{np.percentile(boot,5):.2f}, {np.percentile(boot,95):.2f}]")
print(f"  same statistic on n=19 Gaussian draws  median {np.median(gauss):.2f}, "
      f"90% [{np.percentile(gauss,5):.2f}, {np.percentile(gauss,95):.2f}]")
print(f"""
  Asymptotically IDR/IQR = 1.90 for a Gaussian at any n, but at n = 19 the
  statistic's own sampling interval is wider than the gap between any two
  corpora I have measured (fincap 4.07, CRI models 2.79, CRI team medians 2.08).
  So: NOT INTERPRETABLE HERE. Recorded so that no one, including me, quotes it.
  It is exactly the kind of number that looks like evidence and is not; the
  bootstrap is the only reason I can say so.
""")

print("=" * 78)
print("7. THE SINGLE MOST DAMAGING PAIR")
print("=" * 78)
best = max(itertools.combinations(rows, 2), key=lambda ab: abs(ab[0]["E"] - ab[1]["E"]))
a, b = best
print(f"  {a['model']}/{a['config']}: acc {a['acc0']:.4f} -> {a['acc14']:.4f}   E = {a['E']:+.4f}")
print(f"  {b['model']}/{b['config']}: acc {b['acc0']:.4f} -> {b['acc14']:.4f}   E = {b['E']:+.4f}")
print(f"  |difference in E| = {abs(a['E']-b['E']):.4f}  =  {abs(a['E']-b['E'])/med_se:.0f} standard errors")
same_model = a["model"] == b["model"]
print(f"  same model? {same_model}")
print(f"""
  The gap is {'WITHIN one model' if same_model else 'across models'}. That matters: an effect that
  reverses across model families can be reported as model dependence, which is a
  finding. An effect that reverses within one model, holding the weights and the
  10,000 questions fixed and changing only the chat template and the token
  budget, is not a finding about anything except the harness.
""")

np.save(os.path.join(HERE, "E_by_spec.npy"), E)
print("saved E_by_spec.npy for scripts 04/05")
