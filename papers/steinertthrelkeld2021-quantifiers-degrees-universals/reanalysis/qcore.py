"""Vectorised re-implementation of SimInf_Quantifiers SimMax informativeness and SumComplexity (final.json setup)."""
import os, numpy as np, dill
R = os.environ.get('ST_RESULTS', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results', 'final_length=12_size=10'))
def L(name): return dill.load(open(os.path.join(R, name), 'rb'))
def universe(size=10):
    U = []
    for AmB in range(size + 1):
        for AB in range(size + 1 - AmB):
            for BmA in range(size + 1 - AmB - AB):
                U.append((AmB, AB, BmA))  # (A-B, A&B, B-A); B = BmA + AB
    return U
UNIV = universe()
def _dist(s1, s2):
    a = s1[0] - s2[0]; b = s1[1] - s2[1]; c = s1[2] - s2[2]
    tot = (s2[0] + s2[1] + s2[2]) - (s1[0] + s1[1] + s1[2])  # (AminusB + B) of s2 minus s1
    return max(a, 0) + max(b, 0) + max(c, 0) + max(tot, 0)
N = len(UNIV)
S = np.array([[1.0 if i == j else 1 / (_dist(UNIV[i], UNIV[j]) + 1) for j in range(N)] for i in range(N)])
def informativeness(Wbool):
    """Wbool: k x N boolean matrix of word meanings."""
    W = np.asarray(Wbool, dtype=float)
    n = W.sum(0); size = W.sum(1)
    inv_n = np.divide(1.0, n, out=np.zeros_like(n), where=n > 0)
    # utility = (1/N) sum_w (1/|w|) sum_{s in w} (1/n_s) sum_{s' in w} S[s,s']
    return float(sum(((W[k] * inv_n) @ S @ W[k]) / size[k] for k in range(W.shape[0]) if size[k] > 0) / N)
