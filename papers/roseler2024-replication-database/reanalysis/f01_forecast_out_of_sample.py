"""Out-of-sample test of Pawel & Held (2020) replication forecasts on FReD (blinded copy, see f00_blind_filter.py).

Per pair we need only: |t_o| of the original, n_o, n_r, and whether the replication was significant in the
original's direction. Pawel-Held's model then needs c = se_o^2/se_r^2 ~ (n_r - 3)/(n_o - 3)^-1 (Fisher-z SEs; exact
for correlations, an approximation for other designs) and d = tau^2 (n_o - 3).

|t_o|: exact two-sided original p (pval_type_o '=') -> probit; else a 1-df test statistic parsed from es_value_o
(t(df)=x, F(1,df)=x, z=x, chi2(1,..)=x, r(df)=x) -> p -> probit. One-tailed p doubled.
Outcome y = 1 if replication p <= .05 (exact '=' with value < .05, or '<' with bound <= .05) AND the replicators did
not code it 'failed' (a significant replication in the wrong direction is coded 'failed'). Rows with no usable
replication p are dropped.
Usage: python f01_forecast_out_of_sample.py <FReD_blinded.csv>     Writes out/f01.json
"""
import json, os, re, sys
import numpy as np, pandas as pd
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "pawel2020-probabilistic-forecasting-replication", "reanalysis"))
from selection_forecast import fit_g, p_sig_selection, p_sig_pawel, scores, ZC

OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
x = pd.read_csv(sys.argv[1], low_memory=False)
num = lambda s: pd.to_numeric(s, errors="coerce")


def parse_stat(s):
    s = str(s).replace("χ", "X").replace("−", "-").replace(" ", "")
    m = re.match(r"^t\((\d+\.?\d*)\)=(-?\d*\.?\d+)", s)
    if m: return float(stats.t.sf(abs(float(m.group(2))), float(m.group(1))) * 2)
    m = re.match(r"^F\(1,(\d+\.?\d*)\)=(\d*\.?\d+)", s)
    if m: return float(stats.f.sf(float(m.group(2)), 1, float(m.group(1))))
    m = re.match(r"^[zZ]=(-?\d*\.?\d+)", s)
    if m: return float(2 * stats.norm.sf(abs(float(m.group(1)))))
    m = re.match(r"^(X2|chi2|X\^2)\(1(,N=\d+)?\)=(\d*\.?\d+)", s, re.I)
    if m: return float(stats.chi2.sf(float(m.group(3)), 1))
    m = re.match(r"^r\((\d+)\)=(-?\d*\.?\d+)", s)
    if m:
        df_, r = float(m.group(1)), float(m.group(2))
        if abs(r) < 1:
            t = r * np.sqrt(df_ / (1 - r * r)); return float(stats.t.sf(abs(t), df_) * 2)
    return np.nan


po = num(x.pval_value_o); tails = x.pval_tails_o.astype(str).str[0]
exact = x.pval_type_o.astype(str).str.contains("=") & ~x.pval_type_o.astype(str).str.contains("<|>")
p_o = np.where(exact, np.where(tails == "1", 2 * po, po), np.nan)
parsed = x.es_value_o.apply(parse_stat)
src = np.where(~np.isnan(p_o), "exact_p", np.where(~parsed.isna(), "parsed_stat", "none"))
p_o = np.where(np.isnan(p_o), parsed, p_o)
x["p_o"] = np.clip(p_o, 1e-15, 1); x["p_o_source"] = src
pr = num(x.pval_value_r); tr_ = x.pval_type_r.astype(str)
sig_r = np.where(tr_.str.contains("=") & ~tr_.str.contains("<|>"), pr < 0.05,
                 np.where(tr_.str.contains("<"), pr <= 0.05, np.where(tr_.str.contains(">"), False, np.nan)))
x["y"] = np.where(pd.isna(sig_r) | pr.isna(), np.nan, (sig_r == 1) & (x.reported_success != "failed"))
x["n_o"] = num(x.n_o); x["n_r"] = num(x.n_r)
ok = x.p_o.notna() & x.y.notna() & (x.n_o > 4) & (x.n_r > 4) & (x.p_o < 1)
d = x[ok].copy()
d["to_abs"] = stats.norm.isf(d.p_o / 2)
d["so"] = 1 / np.sqrt(d.n_o - 3); d["sr"] = 1 / np.sqrt(d.n_r - 3)
y = d.y.astype(int).values
res = {"n_rows_blinded": int(len(x)), "n_usable": int(len(d)), "p_o_source": d.p_o_source.value_counts().to_dict(),
       "n_originals_distinct": int(d.doi_o.fillna(d.ref_o).nunique()), "share_orig_significant": round(float(np.mean(d.to_abs > ZC)), 3),
       "observed_success_rate": round(float(y.mean()), 3),
       "agreement_y_vs_reported_successful": round(float(np.mean(y == (d.reported_success == "successful").values)), 3)}
to_abs, so, sr = d.to_abs.values, d.so.values, d.sr.values
c = so ** 2 / sr ** 2
sig = to_abs > ZC
w, _ = fit_g(to_abs[sig], so[sig], truncate=True)


def forecasts(idx, tau_sh=0.08):
    dd = tau_sh ** 2 / so[idx] ** 2
    fc = {"N": p_sig_pawel(to_abs[idx], c[idx], dd, "N"), "SH": p_sig_pawel(to_abs[idx], c[idx], dd, "SH"),
          "SH_tau.2": p_sig_pawel(to_abs[idx], c[idx], 0.2 ** 2 / so[idx] ** 2, "SH")}
    for tau, k in ((0.08, "SA08"), (0.15, "SA15")):
        p = np.empty(idx.sum() if idx.dtype == bool else len(idx))
        s_i = sig[idx]
        p[s_i] = p_sig_selection(to_abs[idx][s_i], so[idx][s_i], sr[idx][s_i], w, tau, truncate=True)[0]
        if (~s_i).any():
            p[~s_i] = p_sig_selection(to_abs[idx][~s_i], so[idx][~s_i], sr[idx][~s_i], w, tau, truncate=False)[0]
        fc[k] = p
    return fc


allidx = np.ones(len(d), bool)
FC = forecasts(allidx)
res["all"] = {k: scores(p, y) for k, p in FC.items()}
# cluster bootstrap (by original) of observed - expected for SH
cl = d.doi_o.fillna(d.ref_o).astype(str).values
ucl = np.unique(cl); rng = np.random.default_rng(3)
pos = {u: np.where(cl == u)[0] for u in ucl}
for k in ("N", "SH", "SA08"):
    diffs = []
    for _ in range(1000):
        take = np.concatenate([pos[u] for u in rng.choice(ucl, len(ucl))])
        diffs.append((y[take].sum() - FC[k][take].sum()) / len(take))
    res["all"][k]["obs_minus_exp_per_pair_95ci"] = [round(float(np.quantile(diffs, q)), 3) for q in (.025, .975)]
# subgroups
groups = {"discipline=Social Psychology": d.discipline.values == "Social Psychology",
          "discipline=Cognitive Psychology": d.discipline.values == "Cognitive Psychology",
          "discipline=other": ~np.isin(d.discipline.values, ["Social Psychology", "Cognitive Psychology"]),
          "orig p < .005": d.p_o.values < .005, "orig .005 <= p < .05": (d.p_o.values >= .005) & (d.p_o.values < .05),
          "orig p >= .05": d.p_o.values >= .05,
          "n_r/n_o >= 2.5": (d.n_r / d.n_o).values >= 2.5, "n_r/n_o < 2.5": (d.n_r / d.n_o).values < 2.5,
          "prereg_r present": d.prereg_r.notna().values, "year_o < 2010": num(d.year_o).values < 2010, "year_o >= 2010": num(d.year_o).values >= 2010}
res["subgroups"] = {}
for g, m in groups.items():
    if m.sum() < 20: continue
    res["subgroups"][g] = {k: scores(p[m], y[m]) for k, p in FC.items()}
# calibration table by SH decile
q = pd.qcut(FC["SH"], 5, labels=False, duplicates="drop")
res["SH_calibration_quintiles"] = [{"mean_forecast": round(float(FC["SH"][q == i].mean()), 3), "observed": round(float(y[q == i].mean()), 3), "n": int((q == i).sum())} for i in range(int(q.max()) + 1)]
print(json.dumps({k: v for k, v in res.items() if k != "subgroups"}, indent=1))
for g, v in res["subgroups"].items():
    print(g, {k: (s["n"], s["observed"], s["expected"], s["BS"], s["AUC"]) for k, s in v.items()})
json.dump(res, open(os.path.join(OUT, "f01.json"), "w"), indent=1)
