import csv, os, numpy as np
from scipy.optimize import least_squares
from core import D
def fit_frontier(fname='pareto_dominant.csv', costcol='costoflanguages', folder=D):
    rows = list(csv.DictReader(open(os.path.join(folder, fname))))
    c = np.array([float(r[costcol]) for r in rows]); y = np.array([float(r['complexityoflanguages']) for r in rows])
    res = least_squares(lambda p: p[0] / (p[1] + c) - y, [1, 0])
    return res.x, c, y
def grid(p, lo=0.89, hi=14.5, n=10000):
    x = np.linspace(lo, hi, n); return x, p[0] / (p[1] + x)
def mindist(cost, comp, gx, gy, sx=1.0, sy=1.0):
    return float(np.min(np.hypot((gx - cost) / sx, (gy - comp) / sy)))
