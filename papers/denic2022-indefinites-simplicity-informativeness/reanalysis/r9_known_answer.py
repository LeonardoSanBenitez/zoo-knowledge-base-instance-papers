import json, random, statistics as st
from scipy import stats
d = json.load(open('out/out_r4.json'))
art = [m['d_ga'] for m in d['art']]
random.seed(4)
for name in ['null1', 'null3']:
    pool = [m['d_ga'] for m in d[name]]
    rej = 0; ts = []
    for _ in range(1000):
        s = random.sample(pool, 40); t = stats.ttest_ind(s, art, equal_var=False)
        ts.append(t.statistic); rej += (t.pvalue < .001 and t.statistic < 0)
    print(f"{name}: paper's Exp1 test (Welch, GA frontier, vs 479 matched artificial) rejects at p<.001 in {rej/10:.1f}% of 1000 draws; median t {st.median(ts):.1f} (paper's natural: -16.0)")
