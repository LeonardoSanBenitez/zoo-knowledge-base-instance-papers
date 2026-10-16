import numpy as np
def dist(h,label):
    h=h.dropna()
    print(f'--- {label} n={len(h)} mean={h.mean():.2f} median={h.median()} mode={h.mode().tolist()}')
    for lo,hi,name in [(0,49.99,'<50 (happiness weighs MORE)'),(50,51,'50-51 symmetric'),(51.01,99.99,'51<x<100 weighted asym'),(100,100,'100 (no happiness suffices / strict NU-like)')]:
        k=((h>=lo)&(h<=hi)).sum(); print(f'   {name:45s} {k:4d} {k/len(h):.3f}')
    # implied exchange rate r = h/(100-h) (happy needed per unhappy)
    r=h[h<100]/(100-h[h<100])
    print(f'   ratio-of-means implied rate {h.mean()/(100-h.mean()):.2f}; median individual rate {np.median(r):.2f}; geometric mean rate (h<100) {np.exp(np.log(r[r>0]).mean()):.2f}; mean individual rate {r.mean():.2f}')
    vc=h.value_counts().head(10); print('   top values', dict(vc))
