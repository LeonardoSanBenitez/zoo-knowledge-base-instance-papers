"""r01: reproduce every L, L_r, tau, r and Holm p of the paper from the deposited filtered corpora,
and check the Appendix A identity L - L_r = (n-1) s_p s_l r on every file.

Compared against (a) the deposit's own results/filtered/scores_{pud,cv}.csv (the paper's Tables B3-B5
reproduce those files; B3 checked by hand below) and (b) my transcription of Table B3 (13 rows printed).
Usage: python -I r01_reproduce.py <repo_dir> <out_dir>
"""
import csv, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import read_pud, read_cv, summary, holm

root, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
PUD = {'Arabic': 'ara_pud', 'Czech': 'ces_pud', 'German': 'deu_pud', 'English': 'eng_pud', 'Finnish': 'fin_pud',
       'French': 'fra_pud', 'Hindi': 'hin_pud', 'Indonesian': 'ind_pud', 'Icelandic': 'isl_pud', 'Italian': 'ita_pud',
       'Japanese': 'jpn_pud', 'Japanese-romaji': 'jpn_pud_romaji', 'Japanese-strokes': 'jpn_pud_strokes',
       'Korean': 'kor_pud', 'Polish': 'pol_pud', 'Portuguese': 'por_pud', 'Russian': 'rus_pud', 'Spanish': 'spa_pud',
       'Swedish': 'swe_pud', 'Thai': 'tha_pud', 'Turkish': 'tur_pud', 'Chinese': 'zho_pud',
       'Chinese-pinyin': 'zho_pud_pinyin', 'Chinese-strokes': 'zho_pud_strokes'}
# Table B3 as printed (L, Lr, tau, r), transcribed from the arXiv v2 PDF p.28
B3 = {'Arabic': (4.03, 5.54, -0.13, -0.13), 'Czech': (5.44, 7.27, -0.22, -0.15), 'English': (4.87, 7.00, -0.20, -0.12),
      'French': (4.81, 7.47, -0.16, -0.12), 'German': (5.74, 8.56, -0.23, -0.12), 'Indonesian': (5.96, 7.35, -0.11, -0.12),
      'Italian': (4.85, 7.64, -0.16, -0.13), 'Polish': (6.07, 8.00, -0.19, -0.13), 'Portuguese': (4.35, 7.47, -0.20, -0.12),
      'Russian': (6.04, 8.08, -0.19, -0.13), 'Spanish': (4.83, 7.59, -0.16, -0.11), 'Swedish': (5.41, 7.99, -0.23, -0.13),
      'Turkish': (6.43, 7.94, -0.24, -0.12)}


def load_scores(path, length_def):
    d = {}
    with open(path, encoding='utf-8') as fh:
        for row in csv.DictReader(fh):
            if row['length_def'] == length_def:
                d[row['language']] = {k: float(row[k]) for k in ('tau', 'tau_pval', 'r', 'r_pval', 'L', 'Lrand')}
    return d


rows = []
cv_codes = {}
with open(os.path.join(root, 'data', 'filtered', 'descriptive_tables', 'common_voice.csv'), encoding='utf-8') as fh:
    for row in csv.DictReader(fh):
        cv_codes[row['language']] = row['iso_code']
for coll, length, names, reader in (('pud', 'characters', PUD, lambda c: read_pud(root, c)),
                                    ('cv', 'characters', cv_codes, lambda c: read_cv(root, c, 'n_characters')),
                                    ('cv', 'medianDuration', cv_codes, lambda c: read_cv(root, c, 'medianDuration'))):
    ref = load_scores(os.path.join(root, 'results', 'filtered', f'scores_{coll}.csv'), length)
    res = {}
    for lang, code in names.items():
        f, l = reader(code)
        res[lang] = summary(f, l)
    langs = sorted(res)
    for key in ('tau_p', 'r_p'):
        adj = holm([res[x][key] for x in langs])
        for x, a in zip(langs, adj):
            res[x][key + '_holm'] = float(a)
    worst = {k: 0.0 for k in ('L', 'Lr', 'tau', 'r')}
    missing = []
    for x in langs:
        if x not in ref:
            missing.append(x); continue
        for k, rk in (('L', 'L'), ('Lr', 'Lrand'), ('tau', 'tau'), ('r', 'r')):
            worst[k] = max(worst[k], abs(res[x][k] - ref[x][rk]))
        rows.append(dict(collection=coll, length=length, language=x, **res[x],
                         ref_L=ref[x]['L'], ref_Lr=ref[x]['Lrand'], ref_tau=ref[x]['tau'], ref_r=ref[x]['r'],
                         ref_tau_p=ref[x]['tau_pval'], ref_r_p=ref[x]['r_pval']))
    n_neg_gap = sum(res[x]['L'] < res[x]['Lr'] for x in langs)
    n_neg_r = sum(res[x]['r'] < 0 for x in langs)
    max_id = max(abs(res[x]['identity_gap']) for x in langs)
    sig_tau = sum(res[x]['tau_p_holm'] <= 0.05 for x in langs)
    sig_r = sum(res[x]['r_p_holm'] <= 0.05 for x in langs)
    print(f'{coll}/{length}: {len(langs)} files; max |mine - deposit|: ' +
          ', '.join(f'{k} {v:.2e}' for k, v in worst.items()) + (f'; not in deposit: {missing}' if missing else ''))
    print(f'   L < L_r in {n_neg_gap}/{len(langs)}; r < 0 in {n_neg_r}/{len(langs)}; '
          f'max |identity residual| {max_id:.1e}; Holm p<=.05: tau {sig_tau}, r {sig_r}')
    if coll == 'pud':
        dev = max(max(abs(round(res[x][k], 2) - B3[x][i]) for i, k in enumerate(('L', 'Lr', 'tau', 'r'))) for x in B3)
        print(f'   Table B3 (13 printed rows) vs mine rounded to 2 dp: max deviation {dev:.3f}. '
              f'B3 omits {len(langs) - len(B3)} of the {len(langs)} PUD files: '
              f'{", ".join(sorted(set(langs) - set(B3)))}')
with open(os.path.join(out, 'r01_reproduce.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
print('wrote', os.path.join(out, 'r01_reproduce.csv'), len(rows), 'rows')
