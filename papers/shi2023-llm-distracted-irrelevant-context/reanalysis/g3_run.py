"""Run the plan in re/PLAN.md. Resumable: appends one JSON line per call to re/g3_results.jsonl."""
import json, random, re, sys, time, os, urllib.request
MODEL = sys.argv[1] if len(sys.argv) > 1 else 'qwen3.5:4b'; OUT = 're/g3_results.jsonl'; DEADLINE = os.environ.get('DEADLINE', '08:45')
EX = ("Q: Elsa has 5 apples. Anna has 2 more apples than Elsa. How many apples do they have together?\n"
      "A: Anna has 2 more apples than Elsa, so Anna has 2 + 5 = 7 apples. Elsa and Anna have 5 + 7 = 12 apples together. The answer is 12.\n\n")
NEUTRAL = "This problem is from a worksheet."
def ask(p):
    req = urllib.request.Request('http://localhost:11434/api/generate', data=json.dumps({'model': MODEL, 'prompt': p, 'stream': False, 'think': False,
        'options': {'temperature': 0, 'num_predict': 256, 'seed': 0, 'num_ctx': 4096}}).encode(), headers={'Content-Type': 'application/json'})
    t = time.time(); r = json.loads(urllib.request.urlopen(req, timeout=600).read()); return r['response'], round(time.time() - t, 2)
def parse(resp):
    s = resp.replace(',', '').replace('$', '')
    m = re.findall(r'answer is\s*:?\s*(-?\d+(?:\.\d+)?)', s, flags=re.I)
    if not m: m = re.findall(r'-?\d+(?:\.\d+)?', s)
    return m[-1] if m else None
def ok(pred, gold):
    try: return pred is not None and abs(float(pred) - float(str(gold).replace(',', ''))) < 1e-9
    except ValueError: return False
def insert_before_question(q, sent):
    parts = re.split(r'(?<=[.!?])\s+', q.strip())
    return ' '.join(parts[:-1] + [sent, parts[-1]])
A = json.load(open('GSM-IC_2step.json', encoding='utf-8')) + json.load(open('GSM-IC_mstep.json', encoding='utf-8'))
D = [json.loads(l) for l in open('gsm8k_validation.jsonl', encoding='utf-8')]
cls = {}
for x in A: cls.setdefault(x['original_question'], []).append(x)
rng = random.Random(7); bases = sorted(cls); rng.shuffle(bases)
jobs = []
for bi, b in enumerate(bases):
    gold = cls[b][0]['answer']
    jobs += [(f'b{bi}', 'B', b, gold, {}), (f'b{bi}', 'N', insert_before_question(b, NEUTRAL), gold, {})]
    for j, v in enumerate(rng.sample(cls[b], 3)):
        jobs.append((f'b{bi}', f'V{j+1}', v['new_question'], v['answer'], {k: v[k] for k in ('role_label', 'number_label', 'sentence_label')}))
others = [d for d in D if d['question'] not in cls]; rng.shuffle(others)
jobs += [(f'd{i}', 'B', d['question'], d['answer'], {'n_steps': d['n_steps']}) for i, d in enumerate(others[:200])]
done = set()
if os.path.exists(OUT):
    for l in open(OUT, encoding='utf-8'): r = json.loads(l); done.add((r['unit'], r['cond']))
with open(OUT, 'a', encoding='utf-8') as f:
    for unit, cond, q, gold, meta in jobs:
        if (unit, cond) in done: continue
        if time.strftime('%H:%M') >= DEADLINE: print('deadline reached'); break
        resp, sec = ask(EX + f"Q: {q}\nA:"); pred = parse(resp)
        f.write(json.dumps({'unit': unit, 'cond': cond, 'q': q, 'gold': gold, 'pred': pred, 'ok': ok(pred, gold), 'resp': resp, 'sec': sec, **meta}, ensure_ascii=False) + '\n'); f.flush()
print('finished', len(jobs))
