"""Two things:

(A) CONFIRM THE TAUTOLOGY. followup.py returned "100.0% explained by item
structure" in every stratum. That is not robustness, it is an identity. Claim:

    For one item, let W be the set of models that answered it wrongly, |W|=w>=4,
    and let c be the number of concordant pairs within W. The observed collision
    rate is c / C(w,2). For pair (i,j), the leave-pair-out null is
    c_{-ij} / C(w-2,2). Each concordant pair {k,l} is disjoint from exactly
    C(w-2,2) pairs {i,j}, so  sum_{ij} c_{-ij} = c * C(w-2,2), hence
        mean_{ij} [ leave-pair-out null ]  ==  c / C(w,2)  ==  mean_{ij} [ observed ].

    The leave-pair-out nonparametric item null has EXACTLY ZERO expected excess
    agreement, for any dataset whatsoever. It has no power to detect monoculture;
    it can only rank pairs relative to each other.

    This is a concrete instance of Jo, Garg & Raghavan (2026) Thm 1 / Prop 2:
    a sufficiently expressive null absorbs all cross-model correlation. Here the
    absorption is not asymptotic, it is exact and algebraic.

    Verified numerically below on random synthetic data with INJECTED correlation:
    if the identity holds, the null reports ~0 excess even when the truth is
    strongly correlated.

(B) A NULL THAT ACTUALLY HAS POWER. Estimate each item's distractor-attractiveness
    profile from an ANCHOR set of models, then measure excess agreement among pairs
    drawn from a DISJOINT TARGET set. The identity breaks, so the statistic can be
    nonzero, and it tests Kim et al.'s claim that more accurate models are more
    correlated -- against a null built from models that are not those models.
"""
import os, itertools, collections, random
import numpy as np
import pandas as pd
from analyze import load, OUT

# ---------------------------------------------------------------- (A)
print("=" * 72)
print("(A) does the leave-pair-out null have power? synthetic test")
rng = random.Random(0)


def collision_stats(resp):
    """resp: list of lists, resp[item] = list of chosen wrong options."""
    obs = null = n = 0.0
    for row in resp:
        w = len(row)
        if w < 4:
            continue
        for i, j in itertools.combinations(range(w), 2):
            others = [row[k] for k in range(w) if k not in (i, j)]
            c = collections.Counter(others); tot = len(others)
            n += 1
            obs += (row[i] == row[j])
            null += sum(v * (v - 1) for v in c.values()) / (tot * (tot - 1))
    return obs / n, null / n


for name, p in [("independent uniform (no monoculture)", None),
                ("STRONG monoculture: 80% pick the same trap", 0.8),
                ("EXTREME monoculture: 99% pick the same trap", 0.99)]:
    resp = []
    for _ in range(400):
        row = []
        for _m in range(20):
            if p is not None and rng.random() < p:
                row.append("TRAP")
            else:
                row.append(rng.choice(["a", "b", "c"]))
        resp.append(row)
    o, nu = collision_stats(resp)
    print(f"   {name:45s} observed={o:.4f}  leave-pair-out null={nu:.4f}  "
          f"excess={o-nu:+.5f}")
print("   -> the null tracks the observed value exactly, however extreme the")
print("      monoculture. Zero power, by construction. Confirmed.")

# ---------------------------------------------------------------- (B)
print("=" * 72)
print("(B) anchored null: item profile from a DISJOINT set of models")
answers, correct, nopts, _ = load()
models = sorted({m for (m, _) in answers})
qkeys = sorted(correct)
acc = {m: np.mean([answers.get((m, q)) == correct[q] for q in qkeys]) for m in models}
ranked = sorted(models, key=lambda m: -acc[m])
print("   model accuracies (this 2918-item subsample):")
for m in ranked:
    print(f"     {acc[m]:.3f}  {m}")

wrongmap = {q: {m: answers[(m, q)] for m in models
                if answers.get((m, q)) is not None and answers[(m, q)] != correct[q]}
            for q in qkeys}


def anchored_excess(anchor, target, min_anchor=4):
    """mean over target pairs of (observed agreement - anchor-estimated null)."""
    rows = []
    for m1, m2 in itertools.combinations(target, 2):
        obs = null = n = 0.0
        for q in qkeys:
            w = wrongmap[q]
            if m1 not in w or m2 not in w:
                continue
            av = [w[a] for a in anchor if a in w]
            if len(av) < min_anchor:
                continue
            n += 1
            obs += (w[m1] == w[m2])
            c = collections.Counter(av); tot = len(av)
            null += sum(v * (v - 1) for v in c.values()) / (tot * (tot - 1))
        if n >= 30:
            rows.append(dict(m1=m1, m2=m2, n=int(n), obs=obs / n, null=null / n,
                             excess=(obs - null) / n,
                             same_provider=m1.split("_")[0] == m2.split("_")[0]))
    return pd.DataFrame(rows)


strong = [m for m in ranked[:8]]
weak = [m for m in ranked[-8:]]
mid = [m for m in ranked[8:14]]

for lbl, anchor, target in [
        ("null from WEAK 8   -> excess among STRONG 8", weak, strong),
        ("null from STRONG 8 -> excess among WEAK 8", strong, weak),
        ("null from MID 6    -> excess among STRONG 8", mid, strong),
        ("null from MID 6    -> excess among WEAK 8", mid, weak)]:
    d = anchored_excess(anchor, target)
    if not len(d):
        print(f"   {lbl}: no pairs")
        continue
    # drop the duplicate-model pair, which is a data-integrity case not a model fact
    dd = d[~((d.m1.str.contains("unicorn") | d.m2.str.contains("unicorn")) &
             (d.m1.str.contains("palmyra") | d.m2.str.contains("palmyra")))]
    print(f"   {lbl}")
    print(f"      pairs={len(dd):3d}  mean obs={dd.obs.mean():.4f}  "
          f"mean null={dd.null.mean():.4f}  MEAN EXCESS={dd.excess.mean():+.4f}"
          f"  (sd={dd.excess.std():.4f}, {(dd.excess>0).mean():.0%} positive)")
    if dd.same_provider.any():
        print(f"      same-provider pairs excess={dd[dd.same_provider].excess.mean():+.4f}"
              f" (n={dd.same_provider.sum()})   cross-provider="
              f"{dd[~dd.same_provider].excess.mean():+.4f} (n={(~dd.same_provider).sum()})")

# full: anchor = all models NOT in the pair's provider families, target = all
print("=" * 72)
print("(B2) leave-provider-out null: for each pair, estimate the item profile")
print("     using only models from OTHER providers than either member")
rows = []
prov = lambda s: s.split("_")[0]
for m1, m2 in itertools.combinations(models, 2):
    anchor = [m for m in models if prov(m) not in (prov(m1), prov(m2))]
    obs = null = n = 0.0
    for q in qkeys:
        w = wrongmap[q]
        if m1 not in w or m2 not in w:
            continue
        av = [w[a] for a in anchor if a in w]
        if len(av) < 4:
            continue
        n += 1
        obs += (w[m1] == w[m2])
        c = collections.Counter(av); tot = len(av)
        null += sum(v * (v - 1) for v in c.values()) / (tot * (tot - 1))
    if n >= 30:
        rows.append(dict(m1=m1, m2=m2, n=int(n), obs=obs / n, null=null / n,
                         excess=(obs - null) / n, acc_min=min(acc[m1], acc[m2]),
                         same_provider=prov(m1) == prov(m2)))
d = pd.DataFrame(rows)
d.to_csv(os.path.join(OUT, "anchored_pairs.csv"), index=False)
dd = d[~((d.m1.str.contains("unicorn") | d.m2.str.contains("unicorn")) &
         (d.m1.str.contains("palmyra") | d.m2.str.contains("palmyra")))]
print(f"   pairs={len(dd)}  mean observed={dd.obs.mean():.4f}  mean null={dd.null.mean():.4f}")
print(f"   MEAN EXCESS = {dd.excess.mean():+.4f}  (sd {dd.excess.std():.4f}, "
      f"{(dd.excess>0).mean():.0%} of pairs positive)")
print(f"   same-provider {dd[dd.same_provider].excess.mean():+.4f} (n={dd.same_provider.sum()})"
      f" vs cross-provider {dd[~dd.same_provider].excess.mean():+.4f} "
      f"(n={(~dd.same_provider).sum()})")
lo, hi = dd.acc_min.median(), None
print(f"   Kim et al.'s claim (more accurate -> more correlated), against this null:")
print(f"     corr(excess, min accuracy of pair) = "
      f"{np.corrcoef(dd.acc_min, dd.excess)[0,1]:+.3f}")
print(f"     top-half-accuracy pairs excess={dd[dd.acc_min>=lo].excess.mean():+.4f}  "
      f"bottom-half={dd[dd.acc_min<lo].excess.mean():+.4f}")
print("\n   top 8 pairs by anchored excess:")
print(dd.nlargest(8, "excess")[["m1", "m2", "n", "obs", "null", "excess"]]
      .to_string(index=False, float_format=lambda x: f"{x:.4f}"))
