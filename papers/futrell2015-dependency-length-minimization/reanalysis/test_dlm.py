"""Known-answer tests for dlm.py (run before any real treebank result is read).
1. every FREE / FIXED linearisation is a permutation and projective (no crossing arcs);
2. a corpus whose observed orders ARE random projective linearisations shows d ~ 0 and no slope;
3. a corpus whose observed orders are dependency-length-minimal (greedy: shortest subtrees nearest the head,
   alternating sides) shows d << 0 and a negative slope;
4. function_head on 'in the house' style trees moves case to the head and keeps a tree.
Usage: python -I test_dlm.py
"""
import os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dlm


def random_tree(n, rng):
    heads = [0] + [rng.randrange(1, i + 1) for i in range(1, n)]      # node i+1 attaches to an earlier node
    return heads


def projective(heads, pos):
    arcs = [(min(pos[d], pos[h]), max(pos[d], pos[h])) for d, h in enumerate(heads, 1) if h]
    for a, b in arcs:
        for c, e in arcs:
            if a < c < b < e:
                return False
    return True


def relabel(heads, order):
    """Return heads re-expressed in the positions given by `order` (order[k] = node at position k+1)."""
    pos = {w: k + 1 for k, w in enumerate(order)}
    new = [0] * len(heads)
    for d, h in enumerate(heads, 1):
        new[pos[d] - 1] = 0 if h == 0 else pos[h]
    return new


def min_linearise(heads):
    kids = dlm.children(heads); size = {}
    def sz(x):
        if x not in size:
            size[x] = 1 + sum(sz(c) for c in kids[x])
        return size[x]
    def key(node, items):
        cs = sorted([c for c in items if c != node], key=sz)
        left, right = [], []
        for k, c in enumerate(cs):
            (right if k % 2 == 0 else left).append(c)
        return list(reversed(left)) + [node] + right     # shortest nearest the head on both sides
    return dlm.linearise(dlm.children(heads)[0][0], kids, key)


rng = random.Random(1)
# 1
for _ in range(300):
    n = rng.randint(2, 30); h = random_tree(n, rng); rels = [rng.choice('abc') for _ in range(n)]
    kids = dlm.children(h); root = kids[0][0]
    for _k in range(5):
        def kf(node, items):
            rng.shuffle(items); return items
        o = dlm.linearise(root, kids, kf)
        assert sorted(o) == list(range(1, n + 1))
        pos = [0] * (n + 1)
        for k, w in enumerate(o, 1):
            pos[w] = k
        assert projective(h, pos)
print('1. 1500 random linearisations: all permutations, all projective')

# 2 and 3
import statistics
for label, make in (('random-projective corpus', 'rand'), ('minimal corpus', 'min')):
    ds, ls = [], []
    for _ in range(600):
        n = rng.randint(3, 40); h = random_tree(n, rng); rels = [rng.choice('abcd') for _ in range(n)]
        kids = dlm.children(h)
        if make == 'rand':
            def kf(node, items):
                rng.shuffle(items); return items
            order = dlm.linearise(kids[0][0], kids, kf)
        else:
            order = min_linearise(h)
        h2 = relabel(h, order); rels2 = [None] * n
        for d in range(1, n + 1):
            rels2[order.index(d)] = rels[d - 1]
        obs = dlm.dl(h2, list(range(n + 1)))
        fr, fx = dlm.baselines(h2, rels2, rng, 30)
        ds.append(obs - fr); ls.append(n * n)
    mean_d = statistics.mean(ds)
    mx, my = statistics.mean(ls), mean_d
    slope = sum((x - mx) * (y - my) for x, y in zip(ls, ds)) / sum((x - mx) ** 2 for x in ls)
    print(f'{"2" if make == "rand" else "3"}. {label}: mean d = {mean_d:+.2f}, slope on length^2 = {slope:+.4f}')
    if make == 'rand':
        assert abs(mean_d) < 1.0 and abs(slope) < 0.005, 'random corpus should show no effect'
    else:
        assert mean_d < -10 and slope < -0.01, 'minimal corpus should show a strong effect'

# 4: 'saw  the  house  in'  style: x=house(3) has case 'in'(4); heads: saw root(1), the->house, house->saw, in->house
heads = [0, 3, 1, 3]; rels = ['root', 'det', 'obl', 'case']
fh = dlm.function_head(heads, rels)
assert fh == [0, 3, 4, 1], fh
print('4. function_head: case promoted, tree kept:', fh)
print('ALL KNOWN-ANSWER TESTS PASSED')
