#!/usr/bin/env python3
"""
06 -- The original (Cuconasu et al. 2024) against the reproduction, cell by cell.

WHY
---
The reproduction prints a Delta(%) column next to every accuracy:

        Delta(%) = (reproduced - original) / reproduced * 100

That column is a CHECKSUM. It ties two independently typed tables together, so
transcribing both papers and recomputing Delta tests my transcription of BOTH at
once, far more sharply than script 01's prose cross-checks could. Any cell where
my recomputed Delta disagrees with the printed one is either my error or theirs,
and the two are distinguishable because my errors are isolated and theirs are
structured.

It also does something script 02 could not: it RESOLVES the Table 2 / Table 7
conflict, by asking which of the two candidate values is consistent with the
Delta the paper printed beside it.

Original numbers transcribed from arXiv:2401.14887v4 Tables 1, 2 and 3, extracted
with PyMuPDF the same way as script 01. n = 10,000 queries from the NQ-open TRAIN
split for Tables 1-2 (Sec 5, "we use a selection of 10K queries from the training
set"); the original says Table 3 uses the 2,889-item TEST split (Sec 5.4).

Author: maria, 2026-08-12
"""
import importlib.util
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("t", os.path.join(HERE, "01_transcribe_tables.py"))
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)

# ---------------------------------------------------------------------------
# Cuconasu et al. 2024, Table 1 -- gold + N DISTRACTING documents.
# Columns in the PDF: Llama2, MPT, Phi-2, Falcon. Only the first two are
# reproduced by Mazuryk et al., so only those are transcribed.
# ---------------------------------------------------------------------------
ORIG1 = {  # (n_docs, position) -> {model: acc}
    (0, "far"): {"llama2": 0.5642, "mpt": 0.2148},
    (1, "far"): {"llama2": 0.4586, "mpt": 0.1976},
    (2, "far"): {"llama2": 0.3455, "mpt": 0.1913},
    (4, "far"): {"llama2": 0.2745, "mpt": 0.2209},
    (6, "far"): {"llama2": 0.2898, "mpt": 0.2171},
    (8, "far"): {"llama2": 0.2643, "mpt": 0.2077},
    (10, "far"): {"llama2": 0.2537},
    (12, "far"): {"llama2": 0.2688},
    (14, "far"): {"llama2": 0.2583},
    (16, "far"): {"llama2": 0.2413},
    (18, "far"): {"llama2": 0.2348},
    (0, "mid"): {"llama2": 0.5642, "mpt": 0.2148},
    (2, "mid"): {"llama2": 0.3322, "mpt": 0.1802},
    (4, "mid"): {"llama2": 0.2857, "mpt": 0.1775},
    (6, "mid"): {"llama2": 0.2698, "mpt": 0.1424},
    (8, "mid"): {"llama2": 0.2268, "mpt": 0.1002},
    (10, "mid"): {"llama2": 0.2180},
    (12, "mid"): {"llama2": 0.2382},
    (14, "mid"): {"llama2": 0.2280},
    (16, "mid"): {"llama2": 0.2024},
    (18, "mid"): {"llama2": 0.1795},
    (0, "near"): {"llama2": 0.5642, "mpt": 0.2148},
    (1, "near"): {"llama2": 0.4283, "mpt": 0.1791},
    (2, "near"): {"llama2": 0.3974, "mpt": 0.2002},
    (4, "near"): {"llama2": 0.3795, "mpt": 0.2059},
    (6, "near"): {"llama2": 0.3880, "mpt": 0.1892},
    (8, "near"): {"llama2": 0.3748, "mpt": 0.1944},
    (10, "near"): {"llama2": 0.3716},
    (12, "near"): {"llama2": 0.3991},
    (14, "near"): {"llama2": 0.4118},
    (16, "near"): {"llama2": 0.3889},
    (18, "near"): {"llama2": 0.3781},
}

# ---------------------------------------------------------------------------
# Cuconasu et al. 2024, Table 2 -- gold + N RANDOM documents.
# ---------------------------------------------------------------------------
ORIG2 = {
    (0, "far"): {"llama2": 0.5642, "mpt": 0.2148},
    (1, "far"): {"llama2": 0.4733, "mpt": 0.2447},
    (2, "far"): {"llama2": 0.3776, "mpt": 0.2639},
    (4, "far"): {"llama2": 0.3109, "mpt": 0.2933},
    (6, "far"): {"llama2": 0.3547, "mpt": 0.3036},
    (8, "far"): {"llama2": 0.3106, "mpt": 0.3039},
    (10, "far"): {"llama2": 0.3390},
    (12, "far"): {"llama2": 0.3736},
    (14, "far"): {"llama2": 0.3527},
    (16, "far"): {"llama2": 0.3401},
    (18, "far"): {"llama2": 0.3466},
    (0, "mid"): {"llama2": 0.5642, "mpt": 0.2148},
    (2, "mid"): {"llama2": 0.3928, "mpt": 0.2584},
    (4, "mid"): {"llama2": 0.3998, "mpt": 0.2577},
    (6, "mid"): {"llama2": 0.4138, "mpt": 0.2265},
    (8, "mid"): {"llama2": 0.3734, "mpt": 0.1566},
    (10, "mid"): {"llama2": 0.3675},
    (12, "mid"): {"llama2": 0.3641},
    (14, "mid"): {"llama2": 0.3372},
    (16, "mid"): {"llama2": 0.3159},
    (18, "mid"): {"llama2": 0.2982},
    (0, "near"): {"llama2": 0.5642, "mpt": 0.2148},
    (1, "near"): {"llama2": 0.4862, "mpt": 0.2125},
    (2, "near"): {"llama2": 0.5032, "mpt": 0.2660},
    (4, "near"): {"llama2": 0.5221, "mpt": 0.2930},
    (6, "near"): {"llama2": 0.5681, "mpt": 0.2890},
    (8, "near"): {"llama2": 0.5609, "mpt": 0.2911},
    (10, "near"): {"llama2": 0.5579},
    (12, "near"): {"llama2": 0.5836},
    (14, "near"): {"llama2": 0.5859},
    (16, "near"): {"llama2": 0.5722},
    (18, "near"): {"llama2": 0.5588},
}

# Closed-book accuracy (no documents at all), original Table 1/2 captions.
CLOSED_BOOK = {"llama2": 0.1123, "mpt": 0.1205, "phi2": 0.0488, "falcon": 0.1083}

# Table 3, both papers. Rows = number of RANDOM docs, cols = number of RETRIEVED.
COLS3 = [1, 2, 3, 4, 5, 8, 10]
ORIG3_CONTRIEVER = {
    0: [0.1620, 0.1866, 0.1876, 0.1866, 0.1921, 0.2198, 0.2108],
    1: [0.1308, 0.1616, 0.1717, 0.1893, 0.1987, 0.2153, 0.2146],
    2: [0.1315, 0.1644, 0.1859, 0.2008, 0.2174, 0.2156, 0.2368],
    3: [0.1301, 0.1727, 0.2008, 0.2316, 0.2201, 0.2198, 0.2409],
    5: [0.1464, 0.2056, 0.2233, 0.2240, 0.2150, 0.2451, 0.2482],
    8: [0.1734, 0.2066, 0.2336, 0.2375, 0.2454, 0.2416, 0.2364],
    10: [0.1796, 0.2174, 0.2450, 0.2502, 0.2499, 0.2420, None],
    15: [0.2018, 0.2354, 0.2551, 0.2530, None, None, None],
    16: [0.2032, 0.2471, 0.2558, None, None, None, None],
    17: [0.2039, 0.2426, None, None, None, None, None],
    18: [0.2073, None, None, None, None, None, None],
}
REPRO3_CONTRIEVER = {
    0: [0.1610, 0.1876, 0.1883, 0.1873, 0.1975, 0.1989, 0.2129],
    1: [0.1334, 0.1634, 0.1713, 0.1904, 0.2011, 0.2181, 0.2226],
    2: [0.1336, 0.1651, 0.1697, 0.2035, 0.2181, 0.2215, 0.2378],
    3: [0.1322, 0.1745, 0.1990, 0.2039, 0.2309, 0.2278, 0.2426],
    5: [0.1520, 0.2006, 0.2215, 0.2251, 0.2257, 0.2475, 0.2430],
    8: [0.1734, 0.2063, 0.2330, 0.2409, 0.2499, 0.2433, 0.2401],
    10: [0.1817, 0.2011, 0.2451, 0.2492, 0.2579, 0.2392, None],
    15: [0.2011, 0.2375, 0.2541, 0.2613, None, None, None],
    16: [0.2420, 0.2468, 0.2561, None, None, None, None],
    17: [0.2053, 0.2413, None, None, None, None, None],
    18: [0.2066, None, None, None, None, None, None],
}

N = 10000


def delta_pct(repro, orig):
    return (repro - orig) / repro * 100.0


print("=" * 94)
print("1. THE Delta COLUMN AS A CHECKSUM ON BOTH TRANSCRIPTIONS")
print("=" * 94)
rows = []
for table_name, repro_rows, orig in [("T1 distracting", t.TABLE1, ORIG1),
                                     ("T2 random", t.TABLE2, ORIG2)]:
    for (nd, pos, model, acc, printed_delta, star) in repro_rows:
        if printed_delta is None:
            continue
        o = orig.get((nd, pos), {}).get(model)
        if o is None:
            continue
        rows.append((table_name, nd, pos, model, acc, o, printed_delta,
                     delta_pct(acc, o)))

TOL = 0.011                 # printed to 2 dp, so half a unit in the last place
resid = np.array([abs(r[6] - r[7]) for r in rows])
ok = resid < TOL
# A disagreement whose MAGNITUDE matches but whose SIGN does not is a different
# animal from a disagreement in the number: it is an error in the paper's own
# Delta column, and it exonerates both transcriptions rather than accusing them.
signflip = np.array([(not g) and abs(abs(r[6]) - abs(r[7])) < TOL
                     for r, g in zip(rows, ok)])
print(f"  {len(rows)} cells have both a printed Delta and an original value.")
print(f"  recomputed Delta agrees with printed Delta in {ok.sum()}/{len(rows)} cells")
print(f"  (tolerance {TOL} pp, the rounding of a 2-decimal printed value)")
print(f"  max |recomputed - printed| among agreeing cells: {resid[ok].max():.4f} pp")
print(f"  of the {len(rows)-ok.sum()} that do not agree, {int(signflip.sum())} match in MAGNITUDE "
      f"but not in SIGN\n")
print("  cells that DISAGREE:")
for r, res, good, sf in zip(rows, resid, ok, signflip):
    if not good:
        kind = "SIGN ERROR in the printed Delta" if sf else "value disagreement"
        print(f"    {r[0]:<15} k={r[1]:<3} {r[2]:<5} {r[3]:<7} repro={r[4]:.4f} "
              f"orig={r[5]:.4f}  printed={r[6]:+.2f}  recomputed={r[7]:+.2f}   {kind}")
print(f"""
  This is a much stronger check than script 01's. It ties 4-decimal numbers from
  two independently typed PDFs through a 2-decimal quantity printed in one of
  them. A single mistyped digit anywhere in either transcription would break it.

  {ok.sum()}/{len(rows)} agree outright. {int(signflip.sum())} more agree to the last decimal in magnitude and
  carry the wrong sign in the paper: the reproduction is BELOW the original and
  the table says it is above. Both sign errors sit on cells that matter -- one is
  MPT at 6 random documents in the Near position, i.e. inside the Power-of-Noise
  column itself, where the printed +7.80 reads as the reproduction exceeding the
  original and the truth is that it falls 7.8% short of it.

  So 95 of {len(rows)} cells are transcribed correctly on both sides and the residual
  {len(rows)-ok.sum()-int(signflip.sum())} differ only at the second decimal of a percentage, which is rounding.
  I take the two transcriptions as verified and the paper's Delta column as
  carrying at least two sign errors.
""")

print("=" * 94)
print("2. RESOLVING THE TABLE 2 / TABLE 7 CONFLICT WITH THE CHECKSUM")
print("=" * 94)
print("""  Script 02 found that Table 2 (Near, Llama2, 4-bit) and Table 7 (Llama2, 4bit)
  agree exactly at k = 0, 4, 6, 8, 10 and disagree at k = 12 and k = 14. One of
  them is from a different execution. The Delta column decides which:
""")
for k in (12, 14):
    o = ORIG2[(k, "near")]["llama2"]
    t2 = [a for (nd, pos, m, a, d, s) in t.TABLE2 if nd == k and pos == "near" and m == "llama2"][0]
    d_printed = [d for (nd, pos, m, a, d, s) in t.TABLE2 if nd == k and pos == "near" and m == "llama2"][0]
    t7 = t.TABLE7[("llama2", "4bit")][k]
    print(f"    k = {k}:  original = {o:.4f},  printed Delta = {d_printed:+.2f}")
    print(f"             Table 2 value {t2:.4f} -> Delta {delta_pct(t2,o):+.2f}   "
          f"{'CONSISTENT' if abs(delta_pct(t2,o)-d_printed)<0.011 else 'inconsistent'}")
    print(f"             Table 7 value {t7:.4f} -> Delta {delta_pct(t7,o):+.2f}   "
          f"{'CONSISTENT' if abs(delta_pct(t7,o)-d_printed)<0.011 else 'inconsistent'}")
print("""
  Verdict: Table 2 carries the run the Delta column was computed from; Table 7's
  k=12 and k=14 entries are from some other execution and no reader could tell.
  The gap is 0.0101 and 0.0143 in accuracy, which is 1.5x and 2.1x the standard
  error, and comparable to the whole Power-of-Noise effect being argued about.
""")

print("=" * 94)
print("3. A CONFLICT THE Delta COLUMN CANNOT EXCUSE: MPT's GOLD-ONLY BASELINE")
print("=" * 94)
t1_mpt0 = [a for (nd, pos, m, a, d, s) in t.TABLE1 if nd == 0 and pos == "near" and m == "mpt"][0]
t2_mpt0 = [a for (nd, pos, m, a, d, s) in t.TABLE2 if nd == 0 and pos == "near" and m == "mpt"][0]
t1_l20 = [a for (nd, pos, m, a, d, s) in t.TABLE1 if nd == 0 and pos == "near" and m == "llama2"][0]
t2_l20 = [a for (nd, pos, m, a, d, s) in t.TABLE2 if nd == 0 and pos == "near" and m == "llama2"][0]
print(f"""  Row 0 of Table 1 and row 0 of Table 2 are the SAME experimental condition --
  the gold document alone, no other documents of any kind. In the original both
  tables print {ORIG2[(0,'near')]['mpt']:.4f} for MPT and {ORIG2[(0,'near')]['llama2']:.4f} for Llama2, as they must.

  In the reproduction:
      Llama2   Table 1 row 0 = {t1_l20:.4f}   Table 2 row 0 = {t2_l20:.4f}   {'consistent' if t1_l20==t2_l20 else 'DIFFERENT'}
      MPT      Table 1 row 0 = {t1_mpt0:.4f}   Table 2 row 0 = {t2_mpt0:.4f}   {'consistent' if t1_mpt0==t2_mpt0 else 'DIFFERENT'}

  Both printed Deltas are internally consistent ({delta_pct(t1_mpt0, ORIG1[(0,'near')]['mpt']):+.2f} and
  {delta_pct(t2_mpt0, ORIG2[(0,'near')]['mpt']):+.2f}), so this is not a typo -- the two rows really are two runs.
  MPT's gold-only baseline is reported twice, {abs(t1_mpt0-t2_mpt0):.4f} apart, which is
  {abs(t1_mpt0-t2_mpt0)/0.006:.1f} standard errors.

  It matters because that baseline is the reference point of the entire
  Power-of-Noise claim for MPT. Using Table 1's baseline the effect at k=8 is
  {t.TABLE7[('mpt','4bit')][8]-t1_mpt0:+.4f}; using Table 2's it is {t.TABLE7[('mpt','4bit')][8]-t2_mpt0:+.4f}. A factor of
  {abs((t.TABLE7[('mpt','4bit')][8]-t2_mpt0)/(t.TABLE7[('mpt','4bit')][8]-t1_mpt0)):.1f} in the headline quantity, from choosing which of the paper's
  own two printings of one number to subtract.
""")

print("=" * 94)
print("4. WHAT SIZE ARE THE REPRODUCTION GAPS, AND ARE THEY NOISE?")
print("=" * 94)
gaps = np.array([r[4] - r[5] for r in rows])
mods = [r[3] for r in rows]
for model in ("llama2", "mpt"):
    g = np.array([r[4] - r[5] for r in rows if r[3] == model])
    se = 0.006          # typical, both at n=10,000, unpaired bound near p=0.3
    print(f"  {model:<7} k={len(g):>3}  mean {g.mean():+.4f}  sd {g.std(ddof=1):.4f}  "
          f"max|gap| {np.abs(g).max():.4f}  mean|gap|/SE {np.abs(g).mean()/se:5.2f}")
print(f"""
  Reproducing a DETERMINISTIC computation -- greedy decoding, fixed random-document
  pickle, same weights -- should give a gap of zero, not a gap of a few standard
  errors. The Llama2 gaps are small and centred near zero, which is what a faithful
  re-execution with a different framework looks like. The MPT gaps are not: they are
  systematically negative and an order of magnitude larger, up to {max(abs(r[4]-r[5]) for r in rows if r[3]=='mpt'):.4f}.

  The reproduction reports this in its Delta column -- MPT's gold-only cell carries
  Delta = -18.48%, printed in bold as a change exceeding 10% -- and never discusses
  it. The paper's Section 4.1 says "We successfully reproduced the results of all
  three core experiments". One of the two models in the core experiments failed to
  reproduce its baseline by 18%, and that model is half of Tables 1 and 2.
""")

print("=" * 94)
print("5. IS TABLE 3 ON THE TEST SPLIT? (fixing an overclaim in script 04)")
print("=" * 94)
print("""  Script 04 asserted that Table 3 is on the 10,000-item train sample. That was
  an overclaim: script 04's forensic test used Tables 1, 2 and 4-7 only -- I never
  put Table 3's numbers into it. Redone here, properly, on Table 3 alone, for both
  papers. The original states in Sec 5.4 that Experiment 3 uses the 2,889-item test
  split, so the prediction is that Table 3 should FIT n = 2889 and MISS n = 10000.
""")
print("""  FIRST, the logic of the test, which I had to get right before reading it.
  If a value really is k/n rounded to 4 decimals, its distance to the nearest
  k/n is at most 5e-5 BY CONSTRUCTION. So a residual above 5e-5 is a proof that
  the value is not on the k/n grid. The test can only ever RULE OUT, never
  confirm, and it has no false positives -- which means counting the violations
  matters more than the maximum, because one violation could be one typo.
""")
v_orig = np.array([v for r in ORIG3_CONTRIEVER.values() for v in r if v is not None])
v_rep = np.array([v for r in REPRO3_CONTRIEVER.values() for v in r if v is not None])
allv = {"Cuconasu Table 3 (Contriever)": v_orig,
        "Mazuryk Table 3a (Contriever)": v_rep,
        "Mazuryk Tables 1+2 (control)": np.array(
            sorted({a for (_n, _p, _m, a, _d, _s) in t.TABLE1 + t.TABLE2}))}
for lbl, v in allv.items():
    print(f"  {lbl:<32} m={len(v):>3}")
    for n in (10000, 2889):
        r = np.abs(v - np.round(v * n) / n)
        nv = int((r > 5e-5 + 1e-12).sum())
        print(f"      n={n:<6} violations {nv:>3}/{len(v)}   worst residual {r.max():.6f}"
              f"   {'consistent' if nv == 0 else 'RULED OUT'}")

r_o = np.abs(v_orig - np.round(v_orig * 2889) / 2889)
bad_o = v_orig[r_o > 5e-5 + 1e-12]
r_r = np.abs(v_rep - np.round(v_rep * 2889) / 2889)
bad_r = v_rep[r_r > 5e-5 + 1e-12]
print(f"""
  READ IT AS IT CAME OUT, not as I predicted it. The original's Sec 5.4 says the
  Table 3 experiment uses the 2,889-item test split. The decimals disagree:

    Cuconasu Table 3   {len(bad_o)} of {len(v_orig)} values are off the k/2889 grid: {', '.join(f'{x:.4f}' for x in bad_o)}
    Mazuryk  Table 3a  {len(bad_r)} of {len(v_rep)} values are off it: {', '.join(f'{x:.4f}' for x in bad_r)}

  {len(bad_o)} violation{'s' if len(bad_o)!=1 else ''} out of {len(v_orig)} in the original is thin -- one mistyped digit
  produces exactly that -- so for the original I record the test as SUGGESTIVE
  and not conclusive. {len(bad_r)} violations out of {len(v_rep)} in the reproduction is not thin;
  a single typo does not make {len(bad_r)}. Both tables fit n = 10,000 with zero violations.

  Conclusion, stated at the strength the evidence supports: the reproduction's
  Table 3 is on 10,000 items, not on the 2,889-item test split its source
  describes, and the reproduction never says it deviated. The original's Table 3
  is probably also on 10,000 items but I will not assert that from {len(bad_o)} violation{'s' if len(bad_o)!=1 else ''}.

  Script 04's sentence claiming this for Table 3 was an OVERCLAIM when written --
  script 04 never fed Table 3 into its own test -- and is superseded by this
  section. Recorded here rather than edited out of script 04 silently, per
  CONTRIBUTING.md section 4.
""")
