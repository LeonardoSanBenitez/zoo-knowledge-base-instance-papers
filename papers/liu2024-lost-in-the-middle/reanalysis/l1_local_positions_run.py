"""l1 -- runner for PLAN_local_positions.md (NOT YET LAUNCHED as of 2026-10-17 08:05).

Streams the first N records of each released 20-document prompt file (gold at 0, 4, 9, 14, 19) and the oracle file
for closed-book questions, asks a local Ollama model, and appends one JSON line per call to OUT. Resumable.
Usage: python l1_local_positions_run.py <commit_sha> <out.jsonl> [model] [N]
The commit SHA is required so the run is pinned (see the plan); HEAD on 2026-10-17 was
29b8a6d042ce29abccee3db1a73171a107d7e6af. Author: maria 2026-10-17.
"""
import gzip, io, json, os, re, sys, time, urllib.request

if len(sys.argv) < 3:
    sys.exit(__doc__)
SHA, OUT = sys.argv[1], sys.argv[2]
MODEL = sys.argv[3] if len(sys.argv) > 3 else 'qwen3.5:4b'
N = int(sys.argv[4]) if len(sys.argv) > 4 else 200
BASE = f'https://raw.githubusercontent.com/nelson-liu/lost-in-the-middle/{SHA}/qa_data/'
UA = {'User-Agent': 'zoo-kb/1.0'}


def first_records(path, n):
    """Stream a .jsonl.gz over HTTP and stop after n records -- nothing large touches the disk."""
    resp = urllib.request.urlopen(urllib.request.Request(BASE + path, headers=UA), timeout=120)
    out = []
    with gzip.GzipFile(fileobj=resp) as g:
        for line in io.TextIOWrapper(g, encoding='utf-8'):
            out.append(json.loads(line))
            if len(out) >= n:
                break
    return out


def prompt(question, docs):
    # The repository's qa.prompt and prompting.get_qa_prompt document format, verbatim (checked at 29b8a6d0, 2026-10-17).
    head = ("Write a high-quality answer for the given question using only the provided search results "
            "(some of which might be irrelevant).\n\n")
    body = "\n".join(f"Document [{i + 1}](Title: {d.get('title', '')}) {d.get('text', '')}" for i, d in enumerate(docs))
    return head + body + f"\n\nQuestion: {question}\nAnswer:"


def closed_book(question):
    return f"Answer the question.\n\nQuestion: {question}\nAnswer:"


def ask(p):
    body = json.dumps({'model': MODEL, 'prompt': p, 'stream': False, 'think': False,
                       'options': {'temperature': 0, 'seed': 0, 'num_predict': 32, 'num_ctx': 8192}}).encode()
    req = urllib.request.Request('http://localhost:11434/api/generate', data=body, headers={'Content-Type': 'application/json'})
    t = time.time(); r = json.loads(urllib.request.urlopen(req, timeout=600).read())
    return r['response'], round(time.time() - t, 2)


def main():
    pos = {k: first_records(f'20_total_documents/nq-open-20_total_documents_gold_at_{k}.jsonl.gz', N) for k in (0, 4, 9, 14, 19)}
    oracle = first_records('nq-open-oracle.jsonl.gz', N)
    done = set()
    if os.path.exists(OUT):
        for l in open(OUT, encoding='utf-8'):
            r = json.loads(l); done.add((r['i'], r['cond']))
    with open(OUT, 'a', encoding='utf-8') as f:
        for i in range(N):
            q = pos[0][i]['question']
            assert all(pos[k][i]['question'] == q for k in pos), f'question order differs at {i}'
            jobs = [(f'gold_at_{k}', prompt(q, pos[k][i]['ctxs'])) for k in (0, 4, 9, 14, 19)] + [('closed_book', closed_book(q))]
            for cond, p in jobs:
                if (i, cond) in done:
                    continue
                resp, sec = ask(p)
                f.write(json.dumps({'i': i, 'cond': cond, 'question': q, 'answers': pos[0][i]['answers'], 'resp': resp, 'sec': sec},
                                   ensure_ascii=False) + '\n'); f.flush()


if __name__ == '__main__':
    main()
