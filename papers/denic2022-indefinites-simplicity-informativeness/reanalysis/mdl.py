"""Exact shortest union/intersection formula length (leaves counted with repetition) over 6 flavours, by DP closure."""
FULL = 63
def closure(prims, ops=('u', 'i')):
    """prims: dict bitmask -> leaf cost. returns dict bitmask -> min tree-leaf cost"""
    best = dict()
    for m, c in prims.items():
        if m and (m not in best or c < best[m]): best[m] = c
    changed = True
    while changed:
        changed = False
        ks = list(best.items())
        for a, ca in ks:
            for b, cb in ks:
                c = ca + cb
                outs = []
                if 'u' in ops: outs.append(a | b)
                if 'i' in ops: outs.append(a & b)
                if 'd' in ops: outs.append(a & ~b & FULL)
                for m in outs:
                    if m and (m not in best or c < best[m]):
                        best[m] = c; changed = True
    return best
def bm(fl, order=('sk', 'su', 'ns', 'npi', 'fci', 'nq')):
    return sum(1 << order.index(f) for f in fl)
HASP = {bm(['sk']): 1, bm(['su', 'ns', 'npi', 'fci', 'nq']): 1, bm(['sk', 'su']): 1, bm(['ns', 'npi', 'fci', 'nq']): 1,
        bm(['npi', 'fci', 'nq']): 1, bm(['sk', 'su', 'ns']): 1, bm(['nq']): 1, bm(['sk', 'su', 'ns', 'npi', 'fci']): 1,
        bm(['npi', 'nq']): 2, bm(['fci']): 2}  # R+/R- only as SE+ & R
def tup2bm(t): return sum(1 << j for j in range(6) if t[j])
