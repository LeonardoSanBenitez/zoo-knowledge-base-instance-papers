# Out-of-sample test in MEDITATORS -- plan fixed 2026-10-17 07:38, before any model is fitted
Data: Zenodo 19701724 (Ireland, 'Mindfulness Instruments That Share a Label Do Not Share a Construct', submitted),
sem_analysis_ready.csv, md5 7d5974ccd92de2dc43cd3fd3e910ba3a, N = 955 adult meditators, parcel-level only.
Only descriptives (count/mean/SD/min/max per column) have been looked at.
Mapping (stated before fitting): AWARENESS-like = TMS Curiosity (mean of cur_p1, cur_p2) -- open, interested attention
to experience; EQUANIMITY-like = TMS Decentering (mean of dec_p1..p3) -- non-identification with experience.
MAAS (mean of maas_p1..p3) is attention-in-daily-life, a different construct (the paper's own thesis), used secondarily.
Outcome: DASS-21 total (dass_dep + dass_anx + dass_str). Complete cases on the variables in each model.
PRIMARY H1 (harms literature, 'awareness without equanimity'): in DASS ~ z(cur) + z(dec) + z(cur) x z(dec),
the interaction is NEGATIVE (curiosity is more harmful / less helpful when decentering is low), two-sided test, alpha .05.
Also report the simple slope of curiosity at dec = -1 SD and +1 SD. Prediction written now: H1 NOT supported (the
2026-10-16 non-meditator sample gave the opposite sign); if supported, it is the first evidence for the mechanism here.
SECONDARY: same with MAAS in place of curiosity; correlations MAAS-cur, MAAS-dec, cur-dec (construct overlap);
HC3 robust SEs throughout; DASS is skewed, so repeat H1 with log(1 + DASS) as a robustness check.
Known-answer check BEFORE the real fit: plant a negative interaction in synthetic data with the same marginals and
recover it; plant none and recover ~0.
