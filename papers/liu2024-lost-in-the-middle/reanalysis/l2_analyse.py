"""l2 -- analysis for PLAN_local_positions.md. Written 2026-11-12 while l1 was running, before reading any output.

Usage:
  python l2_analyse.py out/l1_local_positions.jsonl      # the pre-registered analysis
  python l2_analyse.py --selftest                       # known-answer controls on synthetic data (run first)

Metrics (both pre-registered):
  SUB = the paper's metric: some gold answer, normalised, is a substring of the normalised output
        (normalisation as in the repository's best_subspan_em: lowercase, drop punctuation, drop a/an/the, squeeze spaces)
  EM  = normalised output == some normalised gold answer
Primary tests (Holm over the two):
  P1 U-shape: per question d = s(mid=9) - (s(0) + s(19)) / 2; exact two-sided sign test on the non-zero d.
  P2 c2: s(9) vs closed-book; exact two-sided McNemar on discordant pairs.
Secondary: same with EM; paired/independent variance ratio Var(d) / (Var(x) + Var(y)) for each contrast.
Only questions with all 6 conditions are analysed (plan's stop rule). Author: maria.
"""
import json
import math
import random
import re
import string
import sys
from collections import defaultdict

CONDS = ['gold_at_0', 'gold_at_4', 'gold_at_9', 'gold_at_14', 'gold_at_19', 'closed_book']
ARTICLES = re.compile(r'\b(a|an|the)\b')
PUNCT = set(string.punctuation)


def norm(s):
    s = s.lower()
    s = ''.join(ch for ch in s if ch not in PUNCT)
    s = ARTICLES.sub(' ', s)
    return ' '.join(s.split())


def sub_score(resp, answers):
    r = norm(resp)
    return int(any(norm(a) and norm(a) in r for a in answers))


def em_score(resp, answers):
    r = norm(resp)
    return int(any(norm(a) == r for a in answers))


def binom_two_sided(k, n):
    """Exact two-sided binomial test at p = 0.5 (sum of outcomes no more likely than the observed one)."""
    if n == 0:
        return 1.0
    pk = math.comb(n, k) / 2 ** n
    return min(1.0, sum(math.comb(n, i) / 2 ** n for i in range(n + 1) if math.comb(n, i) / 2 ** n <= pk * (1 + 1e-12)))


def perm_ushape(triples):
    """Exact within-question permutation test for P1 (replaces the sign test; see the plan's deviation note).
    H0: within each question the three scores at positions 0, 9, 19 are exchangeable. Under H0 each of the three
    values is equally likely to be the one labelled 'mid'. Statistic 2*T = sum_q (3*v_mid - sum_q), an integer, so
    its exact null distribution is a convolution of per-question 3-point distributions. Two-sided p =
    min(1, 2 * min(P(T <= t), P(T >= t)))."""
    dist = {0: 1.0}
    t_obs = 0
    for s0, s9, s19 in triples:
        tot = s0 + s9 + s19
        t_obs += 3 * s9 - tot
        step = defaultdict(float)
        for v in (s0, s9, s19):
            step[3 * v - tot] += 1 / 3
        new = defaultdict(float)
        for a, pa in dist.items():
            for b, pb in step.items():
                new[a + b] += pa * pb
        dist = new
    lo = sum(p for t, p in dist.items() if t <= t_obs)
    hi = sum(p for t, p in dist.items() if t >= t_obs)
    return min(1.0, 2 * min(lo, hi)), t_obs / 2


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, running = [0.0] * len(ps), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(ps) - rank) * ps[i]))
        adj[i] = running
    return adj


def var(xs):
    m = sum(xs) / len(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - 1) if len(xs) > 1 else float('nan')


def wilson(k, n, z=1.96):
    if n == 0:
        return (float('nan'), float('nan'))
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (round(c - h, 3), round(c + h, 3))


def analyse(table):
    """table: {question_index: {cond: 0/1}} for complete questions only."""
    qs = sorted(table)
    n = len(qs)
    out = {'n_questions': n, 'accuracy': {}}
    for c in CONDS:
        k = sum(table[q][c] for q in qs)
        out['accuracy'][c] = {'k': k, 'n': n, 'p': round(k / n, 3) if n else None, 'wilson95': wilson(k, n)}
    # P1
    d = [table[q]['gold_at_9'] - (table[q]['gold_at_0'] + table[q]['gold_at_19']) / 2 for q in qs]
    neg, pos = sum(1 for x in d if x < 0), sum(1 for x in d if x > 0)
    p_sign = binom_two_sided(min(neg, pos), neg + pos)
    p1, _ = perm_ushape([(table[q]['gold_at_0'], table[q]['gold_at_9'], table[q]['gold_at_19']) for q in qs])
    ends = [(table[q]['gold_at_0'] + table[q]['gold_at_19']) / 2 for q in qs]
    mid = [table[q]['gold_at_9'] for q in qs]
    out['P1_ushape'] = {'mean_d': round(sum(d) / n, 4), 'n_neg_mid_worse': neg, 'n_pos_mid_better': pos, 'p_exact': p1,
                        'p_sign_test_INVALID_as_preregistered': p_sign,
                        'direction_as_predicted': neg > pos,
                        'var_ratio_paired_over_independent': round(var(d) / (var(mid) + var(ends)), 3)
                        if (var(mid) + var(ends)) > 0 else None}
    # P2
    b = sum(1 for q in qs if table[q]['gold_at_9'] == 1 and table[q]['closed_book'] == 0)
    c = sum(1 for q in qs if table[q]['gold_at_9'] == 0 and table[q]['closed_book'] == 1)
    p2 = binom_two_sided(min(b, c), b + c)
    cb = [table[q]['closed_book'] for q in qs]
    d2 = [m - x for m, x in zip(mid, cb)]
    out['P2_mid_vs_closedbook'] = {'mid_minus_cb': round((sum(mid) - sum(cb)) / n, 4), 'b_mid_only': b, 'c_cb_only': c,
                                   'p_exact_mcnemar': p2, 'mid_below_closed_book': c > b,
                                   'var_ratio_paired_over_independent': round(var(d2) / (var(mid) + var(cb)), 3)
                                   if (var(mid) + var(cb)) > 0 else None}
    h = holm([p1, p2])
    out['P1_ushape']['p_holm'], out['P2_mid_vs_closedbook']['p_holm'] = round(h[0], 6), round(h[1], 6)
    return out


def load(path):
    rows = defaultdict(dict)
    meta = {}
    for line in open(path, encoding='utf-8'):
        r = json.loads(line)
        rows[r['i']][r['cond']] = r
        meta[r['i']] = r['answers']
    complete = {i: v for i, v in rows.items() if all(c in v for c in CONDS)}
    return complete, len(rows)


def tables(complete, scorer):
    return {i: {c: scorer(v[c]['resp'], v[c]['answers']) for c in CONDS} for i, v in complete.items()}


def synth(n, acc, seed):
    rnd = random.Random(seed)
    return {i: {c: int(rnd.random() < acc[c]) for c in CONDS} for i in range(n)}


def selftest():
    """Known-answer controls. The analysis must find a forced U-shape, must NOT find one when absent,
    and its false-positive rate under the null must be near (at most) alpha."""
    flat = {c: 0.6 for c in CONDS}
    ushape = dict(flat, gold_at_9=0.45, gold_at_4=0.5, gold_at_14=0.5)
    ok = True
    r = analyse(synth(200, ushape, 1))
    print('forced U (ends .60, mid .45), n=200:', r['P1_ushape'])
    ok &= r['P1_ushape']['p_exact'] < 0.05 and r['P1_ushape']['direction_as_predicted']
    # null calibration: 1000 synthetic runs with no position effect and no closed-book difference
    fp1 = fp2 = fps = 0
    for s in range(1000):
        r = analyse(synth(200, flat, 1000 + s))
        fp1 += r['P1_ushape']['p_exact'] < 0.05
        fps += r['P1_ushape']['p_sign_test_INVALID_as_preregistered'] < 0.05
        fp2 += r['P2_mid_vs_closedbook']['p_exact_mcnemar'] < 0.05
    print(f'null worlds: P1 permutation false-positive {fp1}/1000, P1 sign test (as pre-registered) {fps}/1000, '
          f'P2 false-positive {fp2}/1000 (expect <= 50)')
    ok &= fp1 <= 60 and fp2 <= 60
    # a null world with CORRELATED conditions (question difficulty shared across positions), as real data will have
    fpc = sum(analyse({i: {c: int(random.Random(9000 + s * 1000 + i).random() < ((i * 7919 + s) % 100) / 100)
                            for c in CONDS} for i in range(200)})['P1_ushape']['p_exact'] < 0.05 for s in range(300))
    print(f'correlated null worlds (per-question difficulty shared by all positions): P1 false-positive {fpc}/300 '
          f'(expect <= 15)')
    ok &= fpc <= 21
    # power at the size this run can afford, for a modest real U (10 points)
    hit = sum(analyse(synth(200, dict(flat, gold_at_9=0.5), 5000 + s))['P1_ushape']['p_exact'] < 0.05 for s in range(300))
    print(f'power, U of 10 points at n=200 (independent noise -- a lower bound, real conditions are correlated): {hit}/300')
    # metric checks on literal strings
    assert sub_score('The answer is **Wilhelm Conrad Röntgen** of Germany.', ['Wilhelm Conrad Röntgen']) == 1
    assert sub_score('No confirmed release date.', ['May 18, 2018']) == 0
    assert em_score('The Beatles.', ['Beatles']) == 1
    assert sub_score('theatre', ['the']) == 0  # an article-only gold normalises to empty and must not match
    print('SELFTEST', 'PASS' if ok else 'FAIL')
    return ok


def main():
    if sys.argv[1:] == ['--selftest']:
        sys.exit(0 if selftest() else 1)
    complete, seen = load(sys.argv[1])
    res = {'questions_seen': seen, 'questions_complete': len(complete)}
    for name, scorer in (('SUB_paper_metric', sub_score), ('EM_secondary', em_score)):
        res[name] = analyse(tables(complete, scorer))
    print(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == '__main__':
    main()
