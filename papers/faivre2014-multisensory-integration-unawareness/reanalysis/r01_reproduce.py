"""Faivre, Mudrik, Schwartz & Koch (2014) -- reproduce Tables 2 and 4 from the OSF deposit (usfa5, files.zip),
then probe the inference.

Columns per readme: initials, id, trial, primecong (cong = visual and auditory primes identical),
rel (prime-target congruency), audUnmasked, visUnmasked, audPrime, audTarget, visPrime, visTarget,
respTarget (1 = 'identical'), rtTarget, respPrime (1 = 'identical'), rtPrime.

Usage (from the zoo root):
  python zoo-knowledge-base/instance-papers/papers/faivre2014-multisensory-integration-unawareness/reanalysis/r01_reproduce.py \
    "$(python zoo-knowledge-base/tools/assets.py path paper-downloads/faivre2014-multisensory-integration-unawareness)/osf_usfa5/files/osfstorage/unz/data"
Writes out/r01.json.
"""
import glob, json, os, sys, itertools
import numpy as np, pandas as pd
from scipy import stats
D = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"); os.makedirs(OUT, exist_ok=True)
cols = ["ini", "id", "trial", "primecong", "rel", "audU", "visU", "aP", "aT", "vP", "vT", "respT", "rtT", "respP", "rtP"]

def load(e):
    fs = sorted(glob.glob(os.path.join(D, f"Exp{e}", "*.dat")))
    x = pd.concat([pd.read_csv(f, sep=r"\s+", header=None, names=cols).assign(file=os.path.basename(f)) for f in fs])
    x["primes_identical"] = (x.primecong == "cong").astype(int)
    x["targets_identical"] = (x.aT == x.vT).astype(int)
    # The readme calls column 5 'relation between prime and target congruency', but in the data 'rel'
    # marks IDENTICAL TARGETS (checked: rel <=> audTarget == visTarget on every row). Congruency is derived.
    x["check_rel"] = ((x.rel == "rel").astype(int) == x.targets_identical).astype(int)
    x["congruent"] = (x.primes_identical == x.targets_identical).astype(int)
    x["masked"] = ((x.audU == 0) | (x.visU == 0)).astype(int)
    x["block_trial"] = x.groupby(["file", "masked"]).cumcount() + 1
    x["correctT"] = (x.respT == x.targets_identical).astype(int)
    x["correctP"] = (x.respP == x.primes_identical).astype(int)
    return x

res = {}
paper_t2 = {1: (53.3, "t(16)=2.06 p=.06"), 2: (51.6, "t(21)=1.47 p=.16"), 3: (47.2, "t(20)=-2.27 p=.035"), 4: (50.0, "t(21)=0.04 p=.97")}
paper_t4 = {1: (89, 47, -17), 2: (61, -11, 37), 3: (95, 59, -32), 4: (79, 25, 4)}

def priming(sub, how="exp_of_logmeans", lo=300, hi=4000, drop_first=5):
    s = sub[(sub.block_trial > drop_first) & (sub.correctT == 1) & (sub.rtT >= lo) & (sub.rtT < hi)].copy()
    s["lrt"] = np.log(s.rtT)
    rows = []
    for f, g in s.groupby("file"):
        r = {}
        for ti in (1, 0):
            gg = g[g.targets_identical == ti]
            mi = gg[gg.congruent == 0].lrt.mean(); mc = gg[gg.congruent == 1].lrt.mean()
            if how == "exp_of_logmeans":
                r[ti] = np.exp(mi) - np.exp(mc)
            elif how == "raw_means":
                r[ti] = gg[gg.congruent == 0].rtT.mean() - gg[gg.congruent == 1].rtT.mean()
            elif how == "raw_medians":
                r[ti] = gg[gg.congruent == 0].rtT.median() - gg[gg.congruent == 1].rtT.median()
        sem = np.exp(g[g.targets_identical == 0].lrt.mean()) - np.exp(g[g.targets_identical == 1].lrt.mean())
        # log-scale cell means for the 2x2 interaction
        cm = {(ti, c): g[(g.targets_identical == ti) & (g.congruent == c)].lrt.mean() for ti in (0, 1) for c in (0, 1)}
        inter = (cm[(1, 0)] - cm[(1, 1)]) - (cm[(0, 0)] - cm[(0, 1)])
        main = ((cm[(1, 0)] + cm[(0, 0)]) - (cm[(1, 1)] + cm[(0, 1)])) / 2
        rows.append({"file": f, "prim_ident": r[1], "prim_diff": r[0], "sem_rel": sem, "inter_log": inter, "main_log": main})
    return pd.DataFrame(rows)

for e in (1, 2, 3, 4):
    x = load(e)
    r = {"n_participants": int(x.file.nunique()), "trials_per_participant": sorted(set(x.groupby("file").size())),
         "rel_label_equals_target_identity": float(x.check_rel.mean())}
    unc = x[(x.masked == 1) & (x.block_trial > 5)]
    pa = unc.groupby("file").correctP.mean() * 100
    t = stats.ttest_1samp(pa, 50)
    r["prime_acc_unconscious"] = {"mean": float(pa.mean()), "t": float(t.statistic), "df": len(pa) - 1, "p": float(t.pvalue), "paper": paper_t2[e]}
    r["prime_acc_participants_above_65"] = int((pa > 65).sum())
    r["target_acc_unconscious"] = float((unc.groupby("file").correctT.mean() * 100).mean())
    # response copying: how often does the prime answer equal the target answer?
    cp = unc.groupby("file").apply(lambda g: (g.respP == g.respT).mean()) * 100
    r["prime_answer_equals_target_answer_pct"] = float(cp.mean())
    # prime accuracy split by congruency (copying predicts high on congruent, low on incongruent)
    r["prime_acc_by_congruency"] = {int(k): float(v) for k, v in (unc.groupby(["congruent", "file"]).correctP.mean().groupby("congruent").mean() * 100).items()}
    # d' style: sensitivity to prime identity controlling for target answer -- logistic of respP on primes_identical + respT per participant
    pr = priming(x[x.masked == 1])
    tt = {}
    for k in ("sem_rel", "prim_ident", "prim_diff", "inter_log", "main_log"):
        tt[k] = {"mean": float(pr[k].mean()), "t": float(stats.ttest_1samp(pr[k], 0).statistic), "p": float(stats.ttest_1samp(pr[k], 0).pvalue)}
    r["unconscious_rt"] = tt; r["paper_table4_sem_identPriming_diffPriming"] = paper_t4[e]
    # multiverse on the identical/different priming cells
    mv = {}
    for how, lo, hi, df_ in itertools.product(("exp_of_logmeans", "raw_means", "raw_medians"), (200, 300), (2000, 3000, 4000, 10**9), (0, 5)):
        p_ = priming(x[x.masked == 1], how, lo, hi, df_)
        mv[f"{how}|{lo}|{hi}|drop{df_}"] = {"ident_p": float(stats.ttest_1samp(p_.prim_ident, 0).pvalue), "diff_p": float(stats.ttest_1samp(p_.prim_diff, 0).pvalue),
                                             "inter_p": float(stats.ttest_1samp(p_.inter_log, 0).pvalue)}
    r["multiverse_n"] = len(mv)
    key = "prim_ident" if e in (1, 3) else ("prim_diff" if e == 2 else None)
    if key:
        kk = "ident_p" if key == "prim_ident" else "diff_p"
        r["multiverse_share_p_lt_05_for_reported_cell"] = float(np.mean([v[kk] < .05 for v in mv.values()]))
        r["multiverse_share_inter_p_lt_05"] = float(np.mean([v["inter_p"] < .05 for v in mv.values()]))
    # within-participant permutation null of the paper's criterion: interaction p < .05 OR any cell p < .05
    rng = np.random.default_rng(e)
    sub = x[x.masked == 1].copy()
    hits_any = hits_int = 0; P = 300
    for _ in range(P):
        sub["congruent"] = sub.groupby("file").congruent.transform(lambda v: rng.permutation(v.values))
        p_ = priming(sub)
        pi = stats.ttest_1samp(p_.inter_log, 0).pvalue
        pc = min(stats.ttest_1samp(p_.prim_ident, 0).pvalue, stats.ttest_1samp(p_.prim_diff, 0).pvalue)
        hits_int += pi < .05; hits_any += (pi < .05) or (pc < .05)
    r["perm_null_rate_interaction_p05"] = hits_int / P
    r["perm_null_rate_interaction_or_any_cell_p05"] = hits_any / P
    res[f"exp{e}"] = r
    print(f"\n=== Exp {e}: n={r['n_participants']} trials/participant={r['trials_per_participant']} rel==targets-identical share={r['rel_label_equals_target_identity']}")
    print(f"  prime accuracy (unconscious): {pa.mean():.1f}% t({len(pa)-1})={t.statistic:.2f} p={t.pvalue:.3f}  | paper {paper_t2[e]} | participants >65%: {r['prime_acc_participants_above_65']}")
    print(f"  target accuracy {r['target_acc_unconscious']:.1f}%; prime answer == target answer {cp.mean():.1f}%; prime accuracy by congruency {r['prime_acc_by_congruency']}")
    print("  RT (exp of log means, ms):", {k: (round(v['mean'], 1) if 'log' not in k else round(v['mean'], 4), round(v['t'], 2), round(v['p'], 3)) for k, v in tt.items()}, "| paper sem/ident/diff:", paper_t4[e])
    if key:
        print(f"  multiverse ({len(mv)} specs): reported cell p<.05 in {r['multiverse_share_p_lt_05_for_reported_cell']:.2f}; interaction p<.05 in {r['multiverse_share_inter_p_lt_05']:.2f}")
    print(f"  permutation null (P={P}): interaction p<.05 {r['perm_null_rate_interaction_p05']:.3f}; interaction-or-any-cell {r['perm_null_rate_interaction_or_any_cell_p05']:.3f}")
with open(os.path.join(OUT, "r01.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(res, f, indent=1, default=float)
