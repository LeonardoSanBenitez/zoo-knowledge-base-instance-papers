"""Is the MPE-92M sample a MIXTURE of populations with different phenomenological
structure? The candidate mechanism for the replicability deficit.

Design, and the control that makes it honest:

  For a grouping variable with groups A (n_a) and B (n_b), compute the matched
  Tucker phi between the factor solution of A and that of B. That number ALONE
  is uninterpretable: smaller groups give lower congruence for reasons that have
  nothing to do with the grouping.

  The null is therefore RANDOM SPLITS OF THE POOLED SAMPLE AT EXACTLY THE SAME
  TWO SIZES (n_a, n_b). Group membership is destroyed, n is preserved. If the
  observed between-group phi sits inside that distribution, the groups share a
  structure. If it sits below it, they do not.

Grouping variables: questionnaire language, sex, and the meditation traditions
the respondent reports practising. Traditions are NOT mutually exclusive in this
questionnaire (respondents tick several), so each is tested as
practises-X vs does-not, which is a weaker contrast than a pure between-tradition
one and biases the test TOWARD finding no difference. Recorded because it bounds
the conclusion in the safe direction.

Run: python run_groups.py  ->  results_groups.json
"""
import json
import numpy as np
import mpelib as M

KS = [5, 12]
N_NULL = 25
X, cov = M.load()
rng = np.random.default_rng(53)

GROUPS = {
    'language_3_vs_1': (cov['qlang'] == 3, cov['qlang'] == 1),
    'sex_m_vs_f': (cov['male'] == 1, cov['male'] == 0),
    'vipassana_y_vs_n': (cov['medit_tech_vipassana'] == 1, cov['medit_tech_vipassana'] == 0),
    'zen_y_vs_n': (cov['medit_tech_zen'] == 1, cov['medit_tech_zen'] == 0),
    'metta_y_vs_n': (cov['medit_tech_metta'] == 1, cov['medit_tech_metta'] == 0),
    'dzogchen_y_vs_n': (cov['medit_tech_maha_dzog'] == 1, cov['medit_tech_maha_dzog'] == 0),
    'buddhist_y_vs_n': (cov['rel_buddhist'] == 1, cov['rel_buddhist'] == 0),
    'psychedelics_y_vs_n': (cov['subst_psychedelics'] == 1, cov['subst_psychedelics'] == 0),
}

out = {'ks': KS, 'n_null': N_NULL, 'groups': {}}

for name, (ma, mb) in GROUPS.items():
    ia = np.where(ma.values)[0]
    ib = np.where(mb.values)[0]
    pool = np.concatenate([ia, ib])
    Xp = X.iloc[pool].reset_index(drop=True)
    print(f"\n=== {name}   n_a={len(ia)}  n_b={len(ib)}")
    out['groups'][name] = {'n_a': int(len(ia)), 'n_b': int(len(ib)), 'k': {}}
    for k in KS:
        obs, _ = M.group_congruence(X, ia, ib, k)
        null = M.split_half_congruence(Xp, k, n_splits=N_NULL, seed=900 + k,
                                       sizes=(len(ia), len(ib)))
        nm = np.median(null, 0)
        # one-sided empirical p on the MEAN matched phi
        null_means = null.mean(1)
        p = float((null_means <= obs.mean()).mean())
        print(f"  k={k:2d}  observed mean phi={obs.mean():.3f}   "
              f"size-matched null mean={null_means.mean():.3f} "
              f"[{np.percentile(null_means,5):.3f},{np.percentile(null_means,95):.3f}]"
              f"   p(null<=obs)={p:.3f}")
        print(f"        obs per-factor: " + " ".join(f"{v:.2f}" for v in obs))
        print(f"        null per-factor:" + " ".join(f"{v:.2f}" for v in nm))
        out['groups'][name]['k'][str(k)] = {
            'obs': obs.tolist(), 'obs_mean': float(obs.mean()),
            'null_median': nm.tolist(),
            'null_mean_mean': float(null_means.mean()),
            'null_mean_p05': float(np.percentile(null_means, 5)),
            'null_mean_p95': float(np.percentile(null_means, 95)),
            'p_null_le_obs': p}

json.dump(out, open('results_groups.json', 'w'), indent=1)
print("\nwrote results_groups.json")
