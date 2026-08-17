#!/usr/bin/env python3
"""
01 -- Transcribe every numeric table of Mazuryk et al. 2026, "The Powerless Noise"
      (arXiv:2607.03615v2, SIGIR '26) into tidy CSV.

WHY THIS EXISTS
---------------
The reproduction repository (github.com/ina0105/The-Power-of-Noise-Reproduction)
ships code and 20-example dumps but NOT the per-question generation results
(`data/gen_res*`), which live on a Google Drive folder outside the repo. So the
only reanalysable data this paper publishes is its own tables. Per
CONTRIBUTING.md section 2, an in-paper table is a legitimate artifact
(`role: in-paper-table`) and the correct response is to transcribe it.

PROVENANCE OF THE NUMBERS
-------------------------
Not typed from a rendered page image. Extracted with PyMuPDF from the arXiv PDF:

    python -c "import fitz; d=fitz.open('2607.03615v2.pdf'); print(d[4].get_text())"

and then hand-assembled into rows here, because get_text() returns the cells in
reading order without the column structure. Every assembled row was cross-checked
against a number quoted in the paper's running prose where one exists; the checks
are in `verify()` below and the script FAILS if any of them breaks. That is the
only defence against a transcription error, and it is the reason the checks are
executable rather than a comment.

Author: maria, 2026-08-12
"""
import csv
import os
import sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "artifacts")

# --------------------------------------------------------------------------
# Table 1 -- gold + N DISTRACTING documents, Llama2 / MPT, gold at Far/Mid/Near.
# Values are accuracy; delta is the paper's Delta(%) = (repro-orig)/repro*100.
# star = Wilcoxon p<0.01 vs the original paper's number.
# "-" in the PDF = context limit reached -> recorded as None.
# --------------------------------------------------------------------------
# (n_distracting, position, model, accuracy, delta_pct, wilcoxon_star)
TABLE1 = [
    (0, "far", "llama2", 0.5647, +0.09, False), (0, "far", "mpt", 0.2165, +0.79, False),
    (0, "mid", "llama2", 0.5647, +0.09, False), (0, "mid", "mpt", 0.2165, +0.79, False),
    (0, "near", "llama2", 0.5647, +0.09, False), (0, "near", "mpt", 0.2165, +0.79, False),
    (1, "far", "llama2", 0.4590, +0.09, False), (1, "far", "mpt", 0.1911, -3.40, False),
    (1, "near", "llama2", 0.4284, +0.02, False), (1, "near", "mpt", 0.1825, +1.86, False),
    (2, "far", "llama2", 0.3436, -0.55, False), (2, "far", "mpt", 0.1945, +1.65, False),
    (2, "mid", "llama2", 0.3336, +0.42, False), (2, "mid", "mpt", 0.1768, -1.92, False),
    (2, "near", "llama2", 0.3964, -0.25, False), (2, "near", "mpt", 0.2018, +0.79, False),
    (4, "far", "llama2", 0.2745, None, False), (4, "far", "mpt", 0.2097, -5.34, True),
    (4, "mid", "llama2", 0.2840, -0.60, False), (4, "mid", "mpt", 0.1717, -3.38, False),
    (4, "near", "llama2", 0.3781, -0.37, False), (4, "near", "mpt", 0.1943, -5.97, False),
    (6, "far", "llama2", 0.2884, -0.49, False), (6, "far", "mpt", 0.2077, -4.52, True),
    (6, "mid", "llama2", 0.2692, -0.22, False), (6, "mid", "mpt", 0.1452, +1.93, False),
    (6, "near", "llama2", 0.3886, +0.15, False), (6, "near", "mpt", 0.1937, +2.32, False),
    (8, "far", "llama2", 0.2660, +0.64, False), (8, "far", "mpt", 0.1975, -5.16, True),
    (8, "mid", "llama2", 0.2254, -0.62, False), (8, "mid", "mpt", 0.1031, +2.81, False),
    (8, "near", "llama2", 0.3736, -0.32, False), (8, "near", "mpt", 0.1996, +2.61, False),
    (10, "far", "llama2", 0.2567, +1.17, False),
    (10, "mid", "llama2", 0.2181, +0.05, False),
    (10, "near", "llama2", 0.3713, -0.08, False),
    (12, "far", "llama2", 0.2706, +0.67, False),
    (12, "mid", "llama2", 0.2393, +0.46, False),
    (12, "near", "llama2", 0.4006, +0.37, False),
    (14, "far", "llama2", 0.2594, +0.42, False),
    (14, "mid", "llama2", 0.2307, +1.17, False),
    (14, "near", "llama2", 0.4141, +0.56, False),
    (16, "far", "llama2", 0.2409, -0.17, False),
    (16, "mid", "llama2", 0.2026, +0.10, False),
    (16, "near", "llama2", 0.3903, +0.36, False),
    (18, "far", "llama2", 0.2357, +0.38, False),
    (18, "mid", "llama2", 0.1800, +0.28, False),
    (18, "near", "llama2", 0.3788, +0.18, False),
]

# --------------------------------------------------------------------------
# Table 2 -- gold + N RANDOM documents, same layout. This is the table that
# carries the Power-of-Noise claim (Near column).
# --------------------------------------------------------------------------
TABLE2 = [
    (0, "far", "llama2", 0.5647, +0.09, False), (0, "far", "mpt", 0.1813, -18.48, False),
    (0, "mid", "llama2", 0.5647, +0.09, False), (0, "mid", "mpt", 0.1813, -18.48, False),
    (0, "near", "llama2", 0.5647, +0.09, False), (0, "near", "mpt", 0.1813, -18.48, False),
    (1, "far", "llama2", 0.4689, -0.94, False), (1, "far", "mpt", 0.2238, -9.34, False),
    (1, "near", "llama2", 0.4878, +0.33, False), (1, "near", "mpt", 0.2162, +1.71, True),
    (2, "far", "llama2", 0.3765, -0.29, False), (2, "far", "mpt", 0.2458, -7.37, False),
    (2, "mid", "llama2", 0.3895, -0.85, False), (2, "mid", "mpt", 0.2493, -3.65, False),
    (2, "near", "llama2", 0.5030, -0.04, False), (2, "near", "mpt", 0.2521, -5.51, False),
    (4, "far", "llama2", 0.3077, +1.04, False), (4, "far", "mpt", 0.2613, -12.25, False),
    (4, "mid", "llama2", 0.3995, -0.08, False), (4, "mid", "mpt", 0.2396, -7.56, False),
    (4, "near", "llama2", 0.5203, -0.35, False), (4, "near", "mpt", 0.2643, -10.86, False),
    (6, "far", "llama2", 0.3543, -0.11, False), (6, "far", "mpt", 0.2694, -12.70, False),
    (6, "mid", "llama2", 0.4133, -0.12, False), (6, "mid", "mpt", 0.2069, -9.47, False),
    (6, "near", "llama2", 0.5663, -0.32, True), (6, "near", "mpt", 0.2681, +7.80, False),
    (8, "far", "llama2", 0.3095, -0.36, False), (8, "far", "mpt", 0.2760, -10.12, False),
    (8, "mid", "llama2", 0.3727, -0.19, False), (8, "mid", "mpt", 0.1369, -14.39, False),
    (8, "near", "llama2", 0.5580, -0.52, True), (8, "near", "mpt", 0.2608, -11.63, False),
    (10, "far", "llama2", 0.3392, +0.06, False),
    (10, "mid", "llama2", 0.3693, +0.49, False),
    (10, "near", "llama2", 0.5592, +0.23, True),
    (12, "far", "llama2", 0.3756, +0.53, False),
    (12, "mid", "llama2", 0.3658, +0.46, False),
    (12, "near", "llama2", 0.5832, -0.07, False),
    (14, "far", "llama2", 0.3548, +0.59, False),
    (14, "mid", "llama2", 0.3370, -0.06, False),
    (14, "near", "llama2", 0.5871, +0.20, False),
    (16, "far", "llama2", 0.3393, -0.24, False),
    (16, "mid", "llama2", 0.3153, -0.19, False),
    (16, "near", "llama2", 0.5721, -0.02, False),
    (18, "far", "llama2", 0.3473, +0.20, False),
    (18, "mid", "llama2", 0.2986, +0.13, False),
    (18, "near", "llama2", 0.5620, +0.57, True),
]

# --------------------------------------------------------------------------
# Table 4 -- five models, Random-Near, "Base" configuration (vLLM, bfloat16,
# original prompt, 15-token cap).  Doc counts 0/10/12/14.
# --------------------------------------------------------------------------
TABLE4 = {
    "llama2":  {0: 0.6091, 10: 0.5991, 12: 0.6106, 14: 0.6103},
    "llama3":  {0: 0.1462, 10: 0.6607, 12: 0.6872, 14: 0.6793},
    "mistral": {0: 0.7586, 10: 0.7469, 12: 0.7378, 14: 0.7237},
    "falcon3": {0: 0.7126, 10: 0.6862, 12: 0.6905, 14: 0.6862},
    "qwen2.5": {0: 0.5955, 10: 0.5330, 12: 0.5198, 14: 0.5227},
}

# --------------------------------------------------------------------------
# Table 5 -- inference-configuration ablation, Llama2 and Llama3 only.
# Base -> +Instruct (chat template) -> +Max (100-token cap).
# --------------------------------------------------------------------------
TABLE5 = {
    ("llama2", "Base"):     {0: 0.6091, 10: 0.5991, 12: 0.6106, 14: 0.6103},
    ("llama2", "Instruct"): {0: 0.0910, 10: 0.0787, 12: 0.1412, 14: 0.2287},
    ("llama2", "Max"):      {0: 0.5467, 10: 0.6864, 12: 0.7255, 14: 0.6893},
    ("llama3", "Base"):     {0: 0.1462, 10: 0.6607, 12: 0.6872, 14: 0.6793},
    ("llama3", "Instruct"): {0: 0.6753, 10: 0.4946, 12: 0.3955, 14: 0.3515},
    ("llama3", "Max"):      {0: 0.7774, 10: 0.8036, 12: 0.8058, 14: 0.8077},
}

# --------------------------------------------------------------------------
# Table 6 -- five models x three prompt configurations x four doc counts.
# THE table for a nonstandard-error analysis: a fully crossed design of
# equally-defensible specifications, all measured on the same items.
# --------------------------------------------------------------------------
TABLE6 = {
    ("llama2", "Base"):     {0: 0.6091, 10: 0.5991, 12: 0.6106, 14: 0.6103},
    ("llama2", "FinalP01"): {0: 0.8131, 10: 0.7895, 12: 0.7895, 14: 0.7893},
    ("llama2", "FinalP02"): {0: 0.7732, 10: 0.7053, 12: 0.7287, 14: 0.7231},
    ("llama3", "Base"):     {0: 0.1462, 10: 0.6607, 12: 0.6872, 14: 0.6793},
    ("llama3", "FinalP01"): {0: 0.8703, 10: 0.8670, 12: 0.8544, 14: 0.8508},
    ("llama3", "FinalP02"): {0: 0.8024, 10: 0.7799, 12: 0.7862, 14: 0.7978},
    ("mistral", "Base"):     {0: 0.7586, 10: 0.7469, 12: 0.7378, 14: 0.7237},
    ("mistral", "FinalP01"): {0: 0.8566, 10: 0.8410, 12: 0.8443, 14: 0.8436},
    ("mistral", "FinalP02"): {0: 0.8246, 10: 0.8139, 12: 0.8209, 14: 0.8184},
    ("falcon3", "Base"):     {0: 0.7126, 10: 0.6862, 12: 0.6905, 14: 0.6862},
    ("falcon3", "FinalP01"): {0: 0.8573, 10: 0.8357, 12: 0.8320, 14: 0.8316},
    ("falcon3", "FinalP02"): {0: 0.7859, 10: 0.7861, 12: 0.7794, 14: 0.7730},
    ("qwen2.5", "Base"):     {0: 0.5955, 10: 0.5330, 12: 0.5198, 14: 0.5227},
    ("qwen2.5", "FinalP01"): {0: 0.8706, 10: 0.8708, 12: 0.8699, 14: 0.8683},
    ("qwen2.5", "FinalP02"): {0: 0.7613, 10: 0.7754, 12: 0.7760, 14: 0.7835},
}

# --------------------------------------------------------------------------
# Table 7 (appendix) -- precision ablation, HuggingFace pipeline,
# Near + random documents.  4-bit vs FP16.  MPT stops at 8 docs.
# --------------------------------------------------------------------------
TABLE7 = {
    ("llama2", "4bit"): {0: 0.5647, 4: 0.5203, 6: 0.5663, 8: 0.5580, 10: 0.5592, 12: 0.5731, 14: 0.5728},
    ("llama2", "fp16"): {0: 0.6089, 4: 0.4096, 6: 0.4498, 8: 0.4372, 10: 0.4740, 12: 0.5358, 14: 0.5358},
    ("mpt", "4bit"):    {0: 0.1813, 4: 0.2643, 6: 0.2681, 8: 0.2608},
    ("mpt", "fp16"):    {0: 0.1749, 4: 0.2775, 6: 0.2805, 8: 0.2702},
}

# --------------------------------------------------------------------------
# Hallucination reports shipped in the repo (hallucination_report/*.md).
# These are aggregate counts over n=10,000 per configuration, and they are the
# only per-condition COUNTS the repo publishes. 1-DOC vs 15-DOC.
# --------------------------------------------------------------------------
HALLUC_BASE_LLAMA2 = {
    "n": 10000,
    "acc_1doc": 0.5542, "acc_15doc": 0.6233,
    "correct_1doc": 5542, "correct_15doc": 6233,
    "categories": {  # counts among INCORRECT answers
        "DUAL_RESPONSE":        (1895, 52),
        "TRIMMED_RESPONSE":     (1008, 1380),
        "PARTIAL_MATCH":        (1564, 1270),
        "OTHER_WRONG":          (255, 1108),
        "ALL_CAPS":             (901, 322),
        "DOCUMENT_LEAKAGE":     (960, 269),
        "ADDED_EXPLANATION":    (901, 252),
        "FORMATTING_MISMATCH":  (51, 308),
        "FALSE_NO_RES":         (151, 168),
        "VERBOSE_NO_ANSWER":    (254, 164),
    },
}


def verify():
    """Executable cross-checks against numbers quoted in the paper's prose.

    Each assertion names the sentence it comes from. If transcription drifted,
    this fails loudly instead of poisoning every downstream number.
    Sec 4.3 / 4.4 quote percentages for Table 5 and Table 6; Sec 4.2 quotes
    Table 4. Tables 1-3 and 7 are not quoted in prose and therefore have NO
    independent check -- that is recorded honestly rather than papered over.
    """
    checks = []
    A = lambda cond, msg: checks.append((bool(cond), msg))

    # Sec 4.3: "For Llama2, Instruct substantially lowers overall accuracy,
    # although the Power-of-Noise trend is still present (9.10% at 0-DOC to
    # 22.87% at 14-DOC)."
    A(TABLE5[("llama2", "Instruct")][0] == 0.0910, "T5 llama2 Instruct 0-DOC = 9.10%")
    A(TABLE5[("llama2", "Instruct")][14] == 0.2287, "T5 llama2 Instruct 14-DOC = 22.87%")
    # Sec 4.3: "Instruct + Max reaches 54.67% at 0-DOC and 68.93% at 14-DOC"
    A(TABLE5[("llama2", "Max")][0] == 0.5467, "T5 llama2 Max 0-DOC = 54.67%")
    A(TABLE5[("llama2", "Max")][14] == 0.6893, "T5 llama2 Max 14-DOC = 68.93%")
    # Sec 4.3: "Under Instruct, 0-DOC increases (14.62% -> 67.53%), while
    # 14-DOC decreases (67.93% -> 35.15%), reversing the Base trend."
    A(TABLE5[("llama3", "Base")][0] == 0.1462, "T5 llama3 Base 0-DOC = 14.62%")
    A(TABLE5[("llama3", "Instruct")][0] == 0.6753, "T5 llama3 Instruct 0-DOC = 67.53%")
    A(TABLE5[("llama3", "Base")][14] == 0.6793, "T5 llama3 Base 14-DOC = 67.93%")
    A(TABLE5[("llama3", "Instruct")][14] == 0.3515, "T5 llama3 Instruct 14-DOC = 35.15%")
    # Sec 4.3: "high accuracy at both ends (77.74% at 0-DOC and 80.77% at 14-DOC)"
    A(TABLE5[("llama3", "Max")][0] == 0.7774, "T5 llama3 Max 0-DOC = 77.74%")
    A(TABLE5[("llama3", "Max")][14] == 0.8077, "T5 llama3 Max 14-DOC = 80.77%")
    # Sec 4.2: "accuracy with only the gold document is 14.62%, increasing to
    # 68.72% when 12 random documents are added"
    A(TABLE4["llama3"][0] == 0.1462, "T4 llama3 0-DOC = 14.62%")
    A(TABLE4["llama3"][12] == 0.6872, "T4 llama3 12-DOC = 68.72%")
    # Sec 4.4 FinalP01: "Llama2 changes from 81.31% to 78.93%, Llama3 from
    # 87.03% to 85.08%, Mistral from 85.66% to 84.36%, Falcon3 from 85.73% to
    # 83.16%, and Qwen2.5 from 87.06% to 86.83%"
    for m, lo, hi in [("llama2", 0.8131, 0.7893), ("llama3", 0.8703, 0.8508),
                      ("mistral", 0.8566, 0.8436), ("falcon3", 0.8573, 0.8316),
                      ("qwen2.5", 0.8706, 0.8683)]:
        A(TABLE6[(m, "FinalP01")][0] == lo, f"T6 {m} FinalP01 0-DOC")
        A(TABLE6[(m, "FinalP01")][14] == hi, f"T6 {m} FinalP01 14-DOC")
    # Sec 4.4: "For Qwen2.5, 10-DOC is marginally higher than 0-DOC (87.08% vs 87.06%)"
    A(TABLE6[("qwen2.5", "FinalP01")][10] == 0.8708, "T6 qwen FinalP01 10-DOC = 87.08%")
    # Sec 4.4 FinalP02: "Llama3 is nearly flat (80.24% to 79.78%), Mistral shows
    # only a small decrease (82.46% to 81.84%), and Falcon3 changes modestly
    # (78.59% to 77.30%)... Qwen2.5 ... increasing from 76.13% to 78.35% ...
    # Llama2 ... (77.32% to 72.31%)"
    for m, lo, hi in [("llama3", 0.8024, 0.7978), ("mistral", 0.8246, 0.8184),
                      ("falcon3", 0.7859, 0.7730), ("qwen2.5", 0.7613, 0.7835),
                      ("llama2", 0.7732, 0.7231)]:
        A(TABLE6[(m, "FinalP02")][0] == lo, f"T6 {m} FinalP02 0-DOC")
        A(TABLE6[(m, "FinalP02")][14] == hi, f"T6 {m} FinalP02 14-DOC")

    bad = [m for ok, m in checks if not ok]
    print(f"prose cross-checks: {len(checks) - len(bad)}/{len(checks)} pass")
    if bad:
        for m in bad:
            print("  FAIL:", m)
        sys.exit(1)
    print("  (Tables 1, 2, 3 and 7 carry NO prose cross-check -- no number from")
    print("   them is quoted in running text. Their transcription is unverified")
    print("   beyond a second reading of the extracted text stream.)")


def write():
    os.makedirs(OUT, exist_ok=True)

    def w(name, header, rows):
        p = os.path.join(OUT, name)
        with open(p, "w", newline="", encoding="utf-8") as f:
            wr = csv.writer(f)
            wr.writerow(header)
            wr.writerows(rows)
        print(f"  wrote {name}: {len(rows)} rows")

    w("table1_distracting.csv",
      ["n_docs", "gold_position", "model", "accuracy", "delta_pct_vs_original", "wilcoxon_p_lt_01"],
      [[a, b, c, d, "" if e is None else e, int(f)] for a, b, c, d, e, f in TABLE1])
    w("table2_random.csv",
      ["n_docs", "gold_position", "model", "accuracy", "delta_pct_vs_original", "wilcoxon_p_lt_01"],
      [[a, b, c, d, "" if e is None else e, int(f)] for a, b, c, d, e, f in TABLE2])
    w("table4_base_models.csv", ["model", "n_docs", "accuracy"],
      [[m, k, v] for m, d in TABLE4.items() for k, v in sorted(d.items())])
    w("table5_inference_ablation.csv", ["model", "config", "n_docs", "accuracy"],
      [[m, c, k, v] for (m, c), d in TABLE5.items() for k, v in sorted(d.items())])
    w("table6_prompt_configs.csv", ["model", "config", "n_docs", "accuracy"],
      [[m, c, k, v] for (m, c), d in TABLE6.items() for k, v in sorted(d.items())])
    w("table7_precision.csv", ["model", "precision", "n_docs", "accuracy"],
      [[m, p, k, v] for (m, p), d in TABLE7.items() for k, v in sorted(d.items())])
    rows = [[cat, a, b, HALLUC_BASE_LLAMA2["n"]]
            for cat, (a, b) in HALLUC_BASE_LLAMA2["categories"].items()]
    w("repo_halluc_llama2_base.csv",
      ["error_category", "count_1doc", "count_15doc", "n_total"], rows)


if __name__ == "__main__":
    verify()
    write()
