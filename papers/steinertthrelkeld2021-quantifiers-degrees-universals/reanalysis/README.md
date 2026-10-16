# Reanalysis: Steinert-Threlkeld (2021), Entropy 23:1335

Author: maria, 2026-10-16. Python 3 + numpy, pandas, scipy, statsmodels, dill.

    curl -sL -o results.zip https://osf.io/download/610852e5e380130045962b8c/   # 50,538,787 B, sha256 4dd9b263...623ea
    unzip results.zip 'results/final_length=12_size=10/*'
    git clone https://github.com/shanest/SimInf_Quantifiers repo   # @ a0df2a5; needed on PYTHONPATH to unpickle
    export ST_RESULTS=$PWD/results/final_length=12_size=10 PYTHONPATH=$PWD/repo

`qcore.py` re-implements the SimMax informativeness (vectorised; the authors' version is a
pure-Python triple loop) and the sum complexity. Verified: informativeness to 2.4e-13 and
complexity exactly on 300 random Experiment-1 languages; frontier distance to 1.7e-13.

| script | result |
|---|---|
| q1.py | reproduces every r in analysis_output.txt; degrees in the Exp-1 sample r = .19/.23 (unreported); naturalness survives complexity control (beta .25 -> .23) |
| q2_ladder.py | mean distance to frontier: random .071, conservative .068, monotone .060, mono+cons .056, quasi-natural .051 (300 langs/size) |
| q3_matched.py | complexity-profile-matched: mono+cons non-natural .0435 vs quasi-natural .0486 (paired t = -11.5); more informative too |
| q4_graded_vs_binary.py | pooled r(mono) -.059 vs mean within-size r +.173 |
| q5_within_size.py | per-size r(mono) -.21 (n=1) ... +.57 (n=9); r(cons) positive at every size; bootstrap CIs |
