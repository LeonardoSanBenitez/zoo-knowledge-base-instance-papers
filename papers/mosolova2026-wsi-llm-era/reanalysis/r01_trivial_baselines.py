"""r01: reproduce the 1cpl / 1cpex F-B3 rows of Tables 2, 3, 6 from the released SemCor-WSI csvs, and measure how
1cpl's score depends on the share of monosemous lemmas (the paper's explanation for why nothing beats it).

    python r01_trivial_baselines.py <fullcorpus_wsi dir>   (default: assets.py path paper-downloads/mosolova2026-wsi-llm-era)/fullcorpus_wsi
F-B3 per lemma = item-level BCubed (single label: precision/recall per item), weighted mean over lemmas by #instances
(== item-level micro mean), as the paper states in sec. 3.2 ("weighted average F-B3").
"""
import subprocess, sys
from pathlib import Path
import pandas as pd
import numpy as np

def root():
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    kb = Path(__file__).resolve().parents[4]
    p = subprocess.run([sys.executable, str(kb / "tools" / "assets.py"), "path", "paper-downloads/mosolova2026-wsi-llm-era"],
                       capture_output=True, text=True).stdout.strip().splitlines()[-1]
    return Path(p) / "fullcorpus_wsi"

def bcubed_lemma(gold, pred):
    gold = np.asarray(gold); pred = np.asarray(pred)
    P = np.mean([np.mean(gold[pred == pred[i]] == gold[i]) for i in range(len(gold))])
    R = np.mean([np.mean(pred[gold == gold[i]] == pred[i]) for i in range(len(gold))])
    return P, R, 2 * P * R / (P + R)

def run(df, how):
    fs, ws, Ps, Rs = [], [], [], []
    for lem, g in df.groupby(["lemma", "pos"]):
        gold = g["lexsn"].astype(str).tolist()
        pred = [0] * len(gold) if how == "1cpl" else list(range(len(gold)))
        P, R, F = bcubed_lemma(gold, pred)
        fs.append(F); ws.append(len(gold)); Ps.append(P); Rs.append(R)
    ws = np.array(ws)
    wf = float(np.sum(np.array(fs) * ws) / ws.sum())
    # paper's evaluate.py computes P and R globally per call; report the F of weighted P and R too
    wP = float(np.sum(np.array(Ps) * ws) / ws.sum()); wR = float(np.sum(np.array(Rs) * ws) / ws.sum())
    return wf, 2 * wP * wR / (wP + wR), float(np.mean(fs))

R = root() / "datasets"
print("file                    n_inst n_lemma mono_lemma% mono_inst%  1cpl wF / F(wP,wR) / unweighted   1cpex wF")
for split in ["dev", "test"]:
    for pos in ["verb", "adj", "noun", "dataset_all"]:
        df = pd.read_csv(R / f"semcorwsi_{pos}_{split}.csv")
        k = df.groupby(["lemma", "pos"])["lexsn"].nunique()
        n = df.groupby(["lemma", "pos"]).size()
        a = run(df, "1cpl"); b = run(df, "1cpex")
        print(f"{pos+'_'+split:22s} {len(df):6d} {len(k):6d} {100*(k==1).mean():9.1f} {100*n[k==1].sum()/n.sum():9.1f}"
              f"   {100*a[0]:.1f} / {100*a[1]:.1f} / {100*a[2]:.1f}    {100*b[0]:.1f}")

# Decomposition: weighted F(1cpl) = share_mono_instances * 1 + share_poly * F_poly(1cpl). Any system that never
# splits a monosemous lemma must beat F_poly on the polysemous ones; one that splits them pays on 28% of instances.
print("\nsplit  F(1cpl) on polysemous lemmas only (instance-weighted); mono share")
for split in ["dev", "test"]:
    df = pd.read_csv(R / f"semcorwsi_dataset_all_{split}.csv")
    k = df.groupby(["lemma", "pos"])["lexsn"].transform("nunique")
    a = run(df[k > 1], "1cpl")
    print(f"{split:5s}  {100*a[0]:.1f}   {100*(k==1).mean():.1f}%")
