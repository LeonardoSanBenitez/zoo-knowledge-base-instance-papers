"""Bose 2026 reads Vinaya vocabulary overlap (Theravada vs Mulasarvastivada 0.491; vs Dharmaguptaka 0.816, overlap
coefficient) as shared heritage. Null: the same coefficient between Brahmali's Theravada Vinaya and English texts with
NO Buddhist heritage, at the same vocabulary sizes (2,282 and 11,515 types)."""
import os, re, json, glob, random
ROOT = os.environ.get('PALI', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
TOK = re.compile(r"[A-Za-zÀ-ɏḀ-ỿ]+(?:'[A-Za-z]+)?")
STOP = set('the a an and or but if of to in on at by for with from as is are was were be been being this that these those it its he she they them his her their there here which who whom what when where why how not no so than then too very can will would should could may might must shall do does did have has had i you we me my your our us all any some such only own same also just into out up down over under again further once'.split())[:60] if False else None
STOP = list(dict.fromkeys('the a an and or but if of to in on at by for with from as is are was were be been being this that these those it its he she they them his her their there here which who whom what when where why how not no so than then too very can will would should could may might must shall do does did have has had i you we me my your our us'.split()))[:60]
STOP = set(STOP)
def toks(text):
    return [w for w in (t.lower() for t in TOK.findall(text)) if len(w) > 1 and "'" not in w and w not in STOP]
# Brahmali Theravada Vinaya (bilara-data, CC0)
bt = []; bc = []
for f in glob.glob(os.path.join(ROOT, 'bilara', 'translation', 'en', 'brahmali', 'vinaya', '**', '*.json'), recursive=True):
    for seg in json.load(open(f, encoding='utf-8')).values(): bt += toks(seg)
for f in glob.glob(os.path.join(ROOT, 'bilara', 'comment', 'en', 'brahmali', 'vinaya', '**', '*.json'), recursive=True):
    for seg in json.load(open(f, encoding='utf-8')).values(): bc += toks(re.sub(r'<[^>]+>', ' ', seg))
print(f'translation only: {len(set(bt))} types; notes: {len(bc)} tokens, {len(set(bc))} types')
bt = bt + bc
B = set(bt)
print(f'Brahmali Vinaya: {len(bt)} tokens, {len(B)} types (paper: 480,385 tokens / 18,067 types, from PDF)')
def gut(path):
    s = open(path, encoding='utf-8', errors='ignore').read()
    a = s.find('*** START'); a = s.find('\n', a) if a >= 0 else 0; b = s.find('*** END'); return s[a:b if b > 0 else None]
books = {'St Benedict Rule (monastic law, Christian)': '50040', 'Moby-Dick (novel)': '2701', 'Gibbon vol 1 (history)': '731', 'Federalist Papers (political/legal)': '1404'}
res = {}
for name, gid in books.items():
    t = toks(gut(os.path.join(ROOT, 'gut', f'{gid}.txt')))
    out = {'tokens': len(t), 'types': len(set(t))}
    for target in (2282, 11515):
        seen = []; S = set(); i = 0
        while len(S) < target and i < len(t): S.add(t[i]); i += 1
        if len(S) >= target:
            out[f'overlap_at_{target}_types'] = round(len(S & B) / min(len(S), len(B)), 3)
            out[f'containment_at_{target}_types'] = round(len(S & B) / len(S), 3)
            out[f'jaccard_at_{target}_types'] = round(len(S & B) / len(S | B), 3)
        else:
            out[f'overlap_at_{target}_types'] = None
    out['overlap_full'] = round(len(set(t) & B) / min(len(set(t)), len(B)), 3)
    res[name] = out; print(name, out)
print('paper: Dharmaguptaka (2,282 types) overlap 0.816, Jaccard 0.082; Mulasarvastivada (11,515 types) overlap 0.491, Jaccard 0.200')
json.dump({'brahmali_tokens': len(bt), 'brahmali_types': len(B), 'nulls': res}, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'p1_overlap_null.json'), 'w'), indent=1)
