"""Dependency length: observed vs FREE (random projective) and FIXED (random weight per relation type)
baselines, on content-head (UD as distributed) and function-head (case/mark promoted) trees.
Implements reanalysis/PLAN.md. One output row per sentence per head scheme.

Usage (from zoo root):
  python -I .../reanalysis/dlm.py <ud_dir> <out_csv> [n_lin=50] [seed=20261023]
"""
import csv, glob, os, random, sys
from multiprocessing import Pool

N_LIN = int(sys.argv[3]) if len(sys.argv) > 3 else 50
SEED = int(sys.argv[4]) if len(sys.argv) > 4 else 20261023


def read_conllu(path):
    sent = []
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            line = line.rstrip('\n')
            if not line:
                if sent:
                    yield sent
                sent = []
                continue
            if line.startswith('#'):
                continue
            f = line.split('\t')
            if '-' in f[0] or '.' in f[0]:
                continue                      # multiword tokens, empty nodes
            sent.append((int(f[0]), f[3], int(f[6]) if f[6] != '_' else -1, f[7].split(':')[0]))
    if sent:
        yield sent


def prepare(sent):
    """Drop PUNCT (re-attach any children to the punct's head), re-index, require a single root.
    Returns (heads, rels) with 1-based positions, head 0 = root, or None."""
    upos = {i: u for i, u, h, r in sent}
    head = {i: h for i, u, h, r in sent}
    rel = {i: r for i, u, h, r in sent}
    if any(h < 0 for h in head.values()):
        return None

    def up(h):
        seen = 0
        while h != 0 and upos.get(h) == 'PUNCT':
            h = head[h]; seen += 1
            if seen > 200:
                return None
        return h
    keep = [i for i in sorted(upos) if upos[i] != 'PUNCT']
    if not keep:
        return None
    pos = {i: k + 1 for k, i in enumerate(keep)}
    heads, rels = [], []
    for i in keep:
        h = up(head[i])
        if h is None:
            return None
        heads.append(0 if h == 0 else pos[h]); rels.append(rel[i])
    if heads.count(0) != 1:
        return None
    return heads, rels


def function_head(heads, rels):
    """Promote the first `case` or `mark` dependent of each word to be its head (paper: prepositional objects
    depend on their prepositions; verbs depend on their complementizers)."""
    heads = list(heads); n = len(heads)
    kids = [[] for _ in range(n + 1)]
    for d, h in enumerate(heads, 1):
        kids[h].append(d)
    for x in range(1, n + 1):
        fn = [c for c in kids[x] if rels[c - 1] in ('case', 'mark')]
        if not fn:
            continue
        c = min(fn, key=lambda c: abs(c - x))          # the closest function word
        hx = heads[x - 1]
        heads[c - 1] = hx                               # function word takes x's place
        heads[x - 1] = c                                # x now depends on it
    # sanity: still a tree with one root and no cycle
    if heads.count(0) != 1:
        return None
    for d in range(1, n + 1):
        seen, h = 0, d
        while h != 0:
            h = heads[h - 1]; seen += 1
            if seen > n:
                return None
    return heads


def dl(heads, order_pos):
    return sum(abs(order_pos[d] - order_pos[h]) for d, h in enumerate(heads, 1) if h != 0)


def children(heads):
    kids = [[] for _ in range(len(heads) + 1)]
    for d, h in enumerate(heads, 1):
        kids[h].append(d)
    return kids


def linearise(root, kids, key):
    """Projective linearisation: at each node, order [node] + child subtrees by `key(node, items)`."""
    out = []
    stack = [(root, False)]
    # iterative to avoid recursion limits: expand a node into its ordered items
    def expand(node):
        items = [node] + kids[node]
        return key(node, items)
    seq = [('n', root)]
    res = []
    while seq:
        kind, x = seq.pop()
        if kind == 'w':
            res.append(x); continue
        items = expand(x)
        for it in reversed(items):
            seq.append(('w', it) if it == x else ('n', it))
    return res


def baselines(heads, rels, rng, n_lin):
    kids = children(heads)
    root = kids[0][0]
    n = len(heads)
    free, fixed = [], []
    rel_types = sorted(set(rels))
    for _ in range(n_lin):
        def kfree(node, items):
            rng.shuffle(items); return items
        order = linearise(root, kids, kfree)
        pos = [0] * (n + 1)
        for k, w in enumerate(order, 1):
            pos[w] = k
        free.append(dl(heads, pos))
        wt = {r: rng.uniform(-1, 1) for r in rel_types}
        def kfix(node, items):
            tie = {it: rng.random() for it in items}
            return sorted(items, key=lambda it: (0.0 if it == node else wt[rels[it - 1]], tie[it]))
        order = linearise(root, kids, kfix)
        pos = [0] * (n + 1)
        for k, w in enumerate(order, 1):
            pos[w] = k
        fixed.append(dl(heads, pos))
    return sum(free) / n_lin, sum(fixed) / n_lin


def run_treebank(args):
    tbdir, n_lin, seed = args
    tb = os.path.basename(tbdir)
    rng = random.Random(f'{seed}-{tb}')
    rows = []
    skipped = 0
    for path in sorted(glob.glob(os.path.join(tbdir, '*.conllu'))):
        for k, sent in enumerate(read_conllu(path)):
            p = prepare(sent)
            if p is None or not (1 <= len(p[0]) <= 99):
                skipped += 1; continue
            heads, rels = p
            for scheme, hh in (('content', heads), ('function', function_head(heads, rels))):
                if hh is None:
                    skipped += 1; continue
                ident = list(range(len(hh) + 1))
                obs = dl(hh, ident)
                fr, fx = baselines(hh, rels, rng, n_lin) if len(hh) > 1 else (0.0, 0.0)
                rows.append((tb, scheme, os.path.basename(path), k, len(hh), obs, fr, fx))
    return tb, rows, skipped


def main(ud_dir, out_csv):
    tbs = sorted(d for d in glob.glob(os.path.join(ud_dir, 'UD_*')) if os.path.isdir(d))
    with Pool(min(len(tbs), os.cpu_count() or 4)) as pool:
        results = pool.map(run_treebank, [(d, N_LIN, SEED) for d in tbs])
    with open(out_csv, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['treebank', 'scheme', 'file', 'sent', 'length', 'obs', 'free_mean', 'fixed_mean'])
        for tb, rows, skipped in results:
            w.writerows(rows)
            print(f'{tb}: {len(rows)} rows, {skipped} skipped', flush=True)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
