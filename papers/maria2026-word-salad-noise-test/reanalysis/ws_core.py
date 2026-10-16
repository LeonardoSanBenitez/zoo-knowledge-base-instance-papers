import json, random, time, urllib.request, re, unicodedata
INSTR = ("You are given a question and you MUST respond by EXTRACTING the answer (max 5 tokens) from one of the provided "
         "documents. If none of the documents contain the answer, respond with NO-RES.")
def load(path='test_dataset.json'):
    return json.load(open(path, encoding='utf-8'))
def prompt(q, docs):
    body = '\n'.join(f'Document [{i+1}] {d}' for i, d in enumerate(docs))
    return f'{INSTR}\nDocuments:\n{body}\nQuestion: {q}\nAnswer:'
def ask(model, p, url='http://localhost:11434/api/generate'):
    req = urllib.request.Request(url, data=json.dumps({'model': model, 'prompt': p, 'stream': False, 'think': False,
        'options': {'temperature': 0, 'num_predict': 24, 'seed': 0, 'num_ctx': 4096}}).encode(), headers={'Content-Type': 'application/json'})
    t = time.time(); r = json.loads(urllib.request.urlopen(req, timeout=600).read()); return r['response'], time.time() - t, r.get('prompt_eval_count')
def norm(s):
    s = unicodedata.normalize('NFKD', s).lower(); s = re.sub(r'\b(a|an|the)\b', ' ', s); s = re.sub(r'[^a-z0-9 ]', ' ', s); return ' '.join(s.split())
def correct(resp, answers):  # Power-of-Noise style: any normalised gold answer contained in the normalised response
    r = norm(resp); return any(norm(a) and norm(a) in r for a in answers)
def parse_answers(a):
    import ast
    try: return ast.literal_eval(a) if isinstance(a, str) else list(a)
    except Exception: return [a]
