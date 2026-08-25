"""Is logit.py's IRLS correct? Three independent checks, because the whole
reanalysis of Malka et al. Figure 6 rests on it.

A. one binary predictor -> must equal the CLOSED-FORM 2x2 log odds ratio exactly
B. four predictors      -> must equal a generic BFGS optimiser on the same NLL
C. 40 seeds             -> mean (fitted - planted)/SE must be ~0, i.e. unbiased

Written 2026-08-25 after an absolute-tolerance check flagged one coefficient as
wrong. It was one unlucky draw at 3.5 SE, not a bug -- but "it was probably fine"
is not a check, so here is the check.
"""
import numpy as np
from scipy import optimize
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "..", "tools"))
from statlib import logit_fit

ok = True
rng = np.random.default_rng(1)
n = 200000
x = rng.binomial(1, 0.3, n).astype(float)
y = rng.binomial(1, 1 / (1 + np.exp(-(-1.0 + np.log(2.0) * x))))
a = ((x == 1) & (y == 1)).sum(); b = ((x == 1) & (y == 0)).sum()
c = ((x == 0) & (y == 1)).sum(); d = ((x == 0) & (y == 0)).sum()
closed = np.log((a * d) / (b * c))
f = logit_fit(x[:, None], y)
dA = abs(closed - f["beta"][1])
print("A  closed-form log OR %+.8f   IRLS %+.8f   |diff| %.2e  %s"
      % (closed, f["beta"][1], dA, "ok" if dA < 1e-8 else "FAIL"))
ok &= dA < 1e-8

rng = np.random.default_rng(0)
n = 40000
prev = np.array([0.16, 0.43, 0.30, 0.05]); bt = np.log(np.array([2.0, 0.6, 1.5, 3.0]))
X = np.column_stack([rng.binomial(1, p, n) for p in prev]).astype(float)
y = rng.binomial(1, 1 / (1 + np.exp(-(-1.2 + X @ bt))))
Xc = np.column_stack([np.ones(n), X])
nll = lambda bb: float(np.sum(np.logaddexp(0, Xc @ bb) - y * (Xc @ bb)))
opt = optimize.minimize(nll, np.zeros(5), method="BFGS",
                        options=dict(maxiter=5000, gtol=1e-10))
f2 = logit_fit(X, y)
dB = float(np.max(np.abs(f2["beta"] - opt.x)))
print("B  IRLS vs BFGS   max|diff| %.2e  %s" % (dB, "ok" if dB < 1e-5 else "FAIL"))
ok &= dB < 1e-5

devs = []
for s in range(40):
    r = np.random.default_rng(100 + s)
    X = np.column_stack([r.binomial(1, p, n) for p in prev]).astype(float)
    y = r.binomial(1, 1 / (1 + np.exp(-(-1.2 + X @ bt))))
    ff = logit_fit(X, y)
    devs.append((ff["beta"][1:] - bt) / ff["se"][1:])
devs = np.array(devs)
m = devs.mean(axis=0)
print("C  40 seeds, mean (fitted-planted)/SE %s   sd %s  %s"
      % (np.round(m, 3), np.round(devs.std(axis=0), 3),
         "ok" if np.max(np.abs(m)) < 0.35 else "FAIL"))
ok &= np.max(np.abs(m)) < 0.35
print("\nFITTER VALIDATED" if ok else "\nFITTER NOT VALIDATED -- stop")
