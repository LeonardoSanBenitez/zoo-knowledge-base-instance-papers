"""Word-salad test of the Power-of-Noise claim (cuconasu2024#c4) with a local model.
Per question (paired): C0 gold only; C1 gold + K word-salad docs; C2 gold + K unrelated Wikipedia passages.
Gold placed LAST (nearest the question, the paper's 'Near'). Word salad: tokens sampled from the unigram distribution
of all gold passages, length-matched to the C2 passages. Resumable: appends to results.jsonl, skips done ids."""
import json, os, random, sys
from ws_core import *
MODEL = sys.argv[1] if len(sys.argv) > 1 else 'qwen3.5:4b'; K = 5; N = int(sys.argv[2]) if len(sys.argv) > 2 else 600
d = load(); rng = random.Random(20261016)
order = list(range(len(d))); rng.shuffle(order)
vocab = [w for r in d for w in r['text'].split()]
out = f'results_{MODEL.replace(":", "_")}.jsonl'
done = set()
if os.path.exists(out):
    for line in open(out, encoding='utf-8'): done.add(json.loads(line)['i'])
with open(out, 'a', encoding='utf-8') as f:
    for i in order[:N]:
        if i in done: continue
        x = d[i]; ans = parse_answers(x['answers'])
        r2 = random.Random(i)
        others = [d[j]['text'] for j in r2.sample([j for j in range(len(d)) if j != i], K)]
        salad = [' '.join(r2.choice(vocab) for _ in range(len(o.split()))) for o in others]
        rec = {'i': i, 'q': x['question'], 'answers': ans}
        for name, docs in (('C0', [x['text']]), ('C1', salad + [x['text']]), ('C2', others + [x['text']])):
            resp, t, n = ask(MODEL, prompt(x['question'], docs))
            rec[name] = {'resp': resp, 'ok': correct(resp, ans), 'sec': round(t, 2), 'ptok': n}
        f.write(json.dumps(rec, ensure_ascii=False) + '\n'); f.flush()
