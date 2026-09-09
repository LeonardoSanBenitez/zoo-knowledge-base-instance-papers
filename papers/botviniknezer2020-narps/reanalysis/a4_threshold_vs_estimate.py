"""A4. Where does the disagreement live -- in the map, or in the threshold?

For every pair of teams and every hypothesis we have two things at once:
  (a) the Spearman correlation between their unthresholded statistical maps -- how much
      they agree about the ESTIMATE;
  (b) whether they gave the same yes/no answer -- how much they agree about the ANSWER.

NARPS says, in prose, that results varied "even for teams whose statistical maps were
highly correlated". This puts a number on it, and gives it a null.

The null that matters. Two teams agree by chance at rate a0 = p^2 + (1-p)^2 where p is
the hypothesis's marginal yes-rate. For a hypothesis where 5.7% say yes, a0 = 0.89 --
almost all pairs agree WITHOUT ANY shared information. So raw agreement is uninterpretable
and everything below is reported against a0, or as an AUC (which is invariant to a0).
"""
import sys, os, json
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import load

HYPS = [1, 2, 5, 6, 7, 8, 9]
RNG = np.random.default_rng(20260909)


def auc(scores, labels):
    """P(score of a concordant pair > score of a discordant pair), ties at 0.5."""
    labels = np.asarray(labels).astype(bool)
    if labels.all() or (~labels).any() is False or labels.sum() == 0:
        return float('nan')
    order = np.argsort(scores)
    ranks = np.empty(len(scores), float)
    s = np.asarray(scores)[order]
    r = np.arange(1, len(s) + 1, dtype=float)
    # average ranks for ties
    i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and s[j + 1] == s[i]:
            j += 1
        r[i:j + 1] = (i + j + 2) / 2.0
        i = j + 1
    ranks[order] = r
    n1 = labels.sum()
    n0 = (~labels).sum()
    return float((ranks[labels].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def main():
    D = load.decisions()
    out = {'per_hypothesis': {}}
    pooled_r, pooled_agree, pooled_h = [], [], []
    for h in HYPS:
        C = load.unthresh_corr(h)
        teams = [t for t in C.index if t in D.index]
        C = C.loc[teams, teams]
        dec = D.loc[teams, h].values
        n = len(teams)
        iu = np.triu_indices(n, 1)
        r = C.values[iu].astype(float)
        agree = (dec[iu[0]] == dec[iu[1]]).astype(int)
        p = dec.mean()
        a0 = p ** 2 + (1 - p) ** 2
        # agreement as a function of map-correlation decile
        q = np.quantile(r, np.linspace(0, 1, 11))
        bins = np.clip(np.digitize(r, q[1:-1]), 0, 9)
        by_dec = [{'decile': int(d + 1),
                   'r_mid': float(np.median(r[bins == d])),
                   'n_pairs': int((bins == d).sum()),
                   'agreement': float(agree[bins == d].mean())} for d in range(10)]
        top = r >= np.quantile(r, 0.9)
        out['per_hypothesis'][h] = dict(
            n_teams=n, n_pairs=int(len(r)), p_yes=float(p),
            chance_agreement_a0=float(a0),
            observed_agreement=float(agree.mean()),
            excess_over_chance=float(agree.mean() - a0),
            auc_mapcorr_predicts_agreement=auc(r, agree),
            agreement_in_top_decile_of_map_corr=float(agree[top].mean()),
            median_r_in_top_decile=float(np.median(r[top])),
            disagreement_in_top_decile=float(1 - agree[top].mean()),
            deciles=by_dec,
        )
        pooled_r.append(r); pooled_agree.append(agree); pooled_h.append(np.full(len(r), h))

    r = np.concatenate(pooled_r); agree = np.concatenate(pooled_agree)
    hh = np.concatenate(pooled_h)
    # pooled AUC computed WITHIN hypothesis then averaged, since a0 differs wildly
    aucs = [out['per_hypothesis'][h]['auc_mapcorr_predicts_agreement'] for h in HYPS]
    out['pooled'] = dict(
        n_pairs=int(len(r)),
        mean_within_hyp_auc=float(np.nanmean(aucs)),
        auc_per_hyp={str(h): out['per_hypothesis'][h]['auc_mapcorr_predicts_agreement']
                     for h in HYPS},
    )
    # the headline: restrict to the strongly-agreeing pairs (r > 0.8) and ask how often
    # they still disagree, per hypothesis, against a0
    strong = {}
    for h in HYPS:
        C = load.unthresh_corr(h)
        teams = [t for t in C.index if t in D.index]
        C = C.loc[teams, teams]; dec = D.loc[teams, h].values
        n = len(teams); iu = np.triu_indices(n, 1)
        rr = C.values[iu].astype(float); ag = (dec[iu[0]] == dec[iu[1]]).astype(int)
        p = dec.mean(); a0 = p ** 2 + (1 - p) ** 2
        for thr in (0.7, 0.8, 0.9):
            m = rr >= thr
            strong.setdefault(str(thr), {})[str(h)] = dict(
                n_pairs=int(m.sum()),
                agreement=float(ag[m].mean()) if m.sum() else None,
                chance=float(a0),
                disagreement=float(1 - ag[m].mean()) if m.sum() else None)
    out['strongly_correlated_pairs'] = strong
    print(json.dumps(out['pooled'], indent=1))
    for h in HYPS:
        v = out['per_hypothesis'][h]
        print(f"h{h}: p_yes={v['p_yes']:.3f} chance={v['chance_agreement_a0']:.3f} "
              f"obs={v['observed_agreement']:.3f} excess={v['excess_over_chance']:+.3f} "
              f"AUC={v['auc_mapcorr_predicts_agreement']:.3f} "
              f"top-decile r={v['median_r_in_top_decile']:.2f} disagree={v['disagreement_in_top_decile']:.3f}")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                           'artifacts', 'a4_threshold_vs_estimate.json'), 'w') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()
