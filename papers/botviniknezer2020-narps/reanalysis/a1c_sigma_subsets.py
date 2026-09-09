"""A1c. The random-intercept SD, refitted on map-disjoint subsets.

sigma = 1.32 on all nine hypotheses could be inflated by the fact that H1/H3 and H2/H4
are the SAME statistical map read in two ROIs and H7/H8/H9 are all amygdala-loss. Refit
on subsets that share no map.
"""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import load
from a1b_icc_and_dissent import fit_sigma

SUBSETS = {
    'all9': [1, 2, 3, 4, 5, 6, 7, 8, 9],
    'disjoint_A': [1, 2, 5, 6, 7, 8, 9],
    'disjoint_B': [3, 4, 5, 6, 7, 8, 9],
    'no_amygdala_disjoint': [1, 2, 5, 6],
    'gains_only_disjoint': [1, 2],
    'losses_only': [5, 6, 7, 8, 9],
}

def main():
    D = load.decisions()
    out = {}
    for name, cols in SUBSETS.items():
        Y = D[cols].values.astype(float)
        s, nll = fit_sigma(Y)
        _, nll0 = fit_sigma(Y, fix_sigma_zero=True)
        out[name] = dict(k=len(cols), sigma=s,
                         icc=float(s**2/(s**2+np.pi**2/3)),
                         lrt_chi2=float(2*(nll0-nll)))
        print(f"{name:22s} k={len(cols)} sigma={s:.3f} icc={out[name]['icc']:.3f} "
              f"LRT chi2={out[name]['lrt_chi2']:.1f}")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..',
                           'artifacts','a1c_sigma_subsets.json'),'w') as f:
        json.dump(out,f,indent=1)

if __name__=='__main__':
    main()
