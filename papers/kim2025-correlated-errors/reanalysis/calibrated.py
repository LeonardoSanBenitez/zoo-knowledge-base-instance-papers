"""Recalibrated version of marginal.py Test 2 (which overshot by 236%).

FINDINGS.md section 4 records that failure and specifies this fix: parameterise
each model so that its simulated P(modal distractor | wrong) MATCHES the value
measured in Test 1, instead of tilting by an uncalibrated amount.

Model. Every MMLU item here has 4 options, so 3 wrong ones (verified: the uniform
baseline is exactly 1/3 for every item in the sample). Let M be the item's modal
wrong answer in the population. Model m, when wrong, picks:
    - the modal wrong answer M with probability s_m
    - otherwise uniformly among the 3 wrong options
Then
    q_m := P(m picks M | m wrong) = s_m + (1 - s_m)/3
and s_m is IDENTIFIED by the measured q_m:      s_m = (3 q_m - 1) / 2.

Under CONDITIONAL INDEPENDENCE given the item, the agreement of a pair is exact,
no simulation needed:
    P(agree | both wrong) = q_1 q_2  +  2 * [(1-s_1)/3] * [(1-s_2)/3]
                            \_ both M _/    \_ both the same non-modal option _/

This is a genuine null: it uses only MARGINAL, per-model quantities plus the item's
modal structure. Any excess of observed over it needs dependence between the models.
"""
import itertools, collections, os
import numpy as np
import pandas as pd
from analyze import load, OUT

answers, correct, nopts, _ = load()
models = sorted({m for (m, _) in answers})
qkeys = sorted(correct)
assert set(nopts.values()) == {4}, f"model assumes 4 options, got {set(nopts.values())}"

acc = {m: float(np.mean([answers.get((m, q)) == correct[q] for q in qkeys])) for m in models}
wrongmap = {q: {m: answers[(m, q)] for m in models
                if answers.get((m, q)) is not None and answers[(m, q)] != correct[q]}
            for q in qkeys}

# ---- measure q_m = P(picks the modal wrong answer | wrong), leave-self-out ----
qm, modal = {}, {}
for q in qkeys:
    w = wrongmap[q]
    if len(w) >= 7:
        c = collections.Counter(w.values())
        top, n1 = c.most_common(1)[0]
        if len(c) == 1 or n1 > c.most_common(2)[1][1]:
            modal[q] = top
for m in models:
    hit = n = 0
    for q, top in modal.items():
        w = wrongmap[q]
        if m not in w:
            continue
        # leave-self-out: recompute the mode without m so q_m is not self-fulfilling
        others = [a for mm, a in w.items() if mm != m]
        c = collections.Counter(others)
        if not c:
            continue
        t, n1 = c.most_common(1)[0]
        if len(c) > 1 and n1 == c.most_common(2)[1][1]:
            continue
        n += 1
        hit += (w[m] == t)
    qm[m] = hit / n

print("=" * 74)
print("calibrated independence model: s_m = (3*q_m - 1)/2")
print(f"{'model':<38}{'acc':>7}{'q_m':>8}{'s_m':>8}")
s = {}
for m in sorted(models, key=lambda x: -acc[x]):
    s[m] = (3 * qm[m] - 1) / 2
    print(f"{m:<38}{acc[m]:7.3f}{qm[m]:8.3f}{s[m]:8.3f}")
neg = [m for m in models if s[m] < 0]
print(f"\n  {len(neg)} model(s) with s_m < 0 -- they pick the popular trap LESS often")
print(f"  than uniform-at-random among wrong options: {', '.join(neg) if neg else 'none'}")
print("  s_m < 0 is outside the mixture's intended range but the algebra stays valid")
print("  (it just means anti-preference for the modal distractor); not clamped.")
print(f"  corr(acc, q_m) = {np.corrcoef([acc[m] for m in models],[qm[m] for m in models])[0,1]:+.3f}")

# ---- exact predicted agreement under conditional independence ----
rows = []
for m1, m2 in itertools.combinations(models, 2):
    obs = n = 0.0
    for q in modal:
        w = wrongmap[q]
        if m1 not in w or m2 not in w:
            continue
        n += 1
        obs += (w[m1] == w[m2])
    if n < 30:
        continue
    q1, q2 = qm[m1], qm[m2]
    pred = q1 * q2 + 2 * ((1 - s[m1]) / 3) * ((1 - s[m2]) / 3)
    rows.append(dict(m1=m1, m2=m2, n=int(n), obs=obs / n, pred_indep=pred,
                     excess=obs / n - pred, acc_min=min(acc[m1], acc[m2]),
                     same_provider=m1.split("_")[0] == m2.split("_")[0]))
d = pd.DataFrame(rows)
dup = ((d.m1.str.contains("unicorn") | d.m2.str.contains("unicorn")) &
       (d.m1.str.contains("palmyra") | d.m2.str.contains("palmyra")))
dd = d[~dup]
d.to_csv(os.path.join(OUT, "calibrated_pairs.csv"), index=False)

print("=" * 74)
print(f"pairs = {len(dd)} (duplicate pair excluded; it is separately {d[dup].excess.iloc[0]:+.3f})")
print(f"  mean OBSERVED agreement-when-both-wrong        = {dd.obs.mean():.4f}")
print(f"  mean PREDICTED under conditional independence  = {dd.pred_indep.mean():.4f}")
print(f"  uniform-over-wrong baseline (Kim et al.)       = 0.3333")
eu = dd.obs.mean() - 1 / 3
ei = dd.pred_indep.mean() - 1 / 3
print(f"\n  excess over the uniform baseline               = {eu:+.4f}")
print(f"  of which reproduced with ZERO dependence       = {ei:+.4f}  ({ei/eu:.1%})")
print(f"  residual requiring dependence between models   = {dd.excess.mean():+.4f}  "
      f"({dd.excess.mean()/eu:.1%})")
print(f"  pairs with positive residual: {(dd.excess>0).mean():.0%}   sd {dd.excess.std():.4f}")
print(f"\n  same-provider residual   {dd[dd.same_provider].excess.mean():+.4f} (n={dd.same_provider.sum()})")
print(f"  cross-provider residual  {dd[~dd.same_provider].excess.mean():+.4f} (n={(~dd.same_provider).sum()})")
pos, negg = dd[dd.same_provider].excess.values, dd[~dd.same_provider].excess.values
dcoh = (pos.mean() - negg.mean()) / np.sqrt((pos.std(ddof=1)**2 + negg.std(ddof=1)**2) / 2)
print(f"  Cohen's d for same-provider on the RESIDUAL: {dcoh:+.3f}")
print(f"\n  corr(min pair accuracy, PREDICTED independent agreement) = "
      f"{np.corrcoef(dd.acc_min, dd.pred_indep)[0,1]:+.3f}")
print(f"  corr(min pair accuracy, observed agreement)              = "
      f"{np.corrcoef(dd.acc_min, dd.obs)[0,1]:+.3f}")
print(f"  corr(min pair accuracy, RESIDUAL)                        = "
      f"{np.corrcoef(dd.acc_min, dd.excess)[0,1]:+.3f}")
print("\n  top 6 pairs by residual (these are the ones needing real dependence):")
print(dd.nlargest(6, "excess")[["m1", "m2", "n", "obs", "pred_indep", "excess"]]
      .to_string(index=False, float_format=lambda x: f"{x:.4f}"))
