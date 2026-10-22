"""Fetch the deposit (osf.io/3mn9y and its components 24xe9, 76ud3) and check each file's sha256 against
OSF's own hash. The data are NOT committed to the knowledge base: they carry Prolific participant IDs.
Usage (from zoo root): python -I zoo-knowledge-base/instance-papers/papers/vandam2025-meditation-adverse-effects-representative/reanalysis/fetch.py <dest_dir>
Pinned by content: CSC_UnusualExp_data_8APR24.rds sha256 is printed and compared with the value in paper.json.
"""
import hashlib, json, os, sys, urllib.request

H = {'User-Agent': 'zoo-kb/1.0'}
WANT = {'3mn9y': ('CSC_UnusualExp_data_8APR24.rds', 'CSC_UnusualExp_data.rds', 'UE_dataDictionary_final.xlsx',
                  '01_preprocess_UEPrev.Rmd'),
        '24xe9': ('IME_Incidence_Predictors_14MAY2024.pdf', 'Predictors_and_Incidence_8Apr2024.R',
                  'ProportionTests_inclBayesian.R'),
        '76ud3': ('Items.csv', 'IUE_EFA_CFA_DFA.R', 'IME_Psychometrics_10MAY24.pdf')}


def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=120).read()


def main(dest):
    os.makedirs(dest, exist_ok=True)
    bad = 0
    for node, names in WANT.items():
        for x in json.loads(get(f'https://api.osf.io/v2/nodes/{node}/files/osfstorage/'))['data']:
            at = x['attributes']
            if at['name'] not in names:
                continue
            b = get(x['links']['download'])
            h = hashlib.sha256(b).hexdigest()
            ok = h == at['extra']['hashes'].get('sha256')
            bad += not ok
            open(os.path.join(dest, at['name']), 'wb').write(b)
            print(f'{"ok " if ok else "BAD"} {node} {at["name"]} {len(b)} {h[:16]} modified {at["date_modified"][:10]}')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
