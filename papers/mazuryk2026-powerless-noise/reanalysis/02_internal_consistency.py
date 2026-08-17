#!/usr/bin/env python3
"""
02 -- Internal consistency of the paper's own tables.

QUESTION
--------
Several cells of Mazuryk et al. 2026 report the SAME quantity twice: the same
model, the same Near/random setup, the same document count, under a
configuration the paper describes as identical. Do the duplicates agree?

This is the `kb.py conflicts` idea applied inside one paper instead of across
records. It costs nothing and nobody does it, because the duplicates sit in
tables 30 pages apart in the reader's attention.

CALIBRATION -- what counts as "disagree"
----------------------------------------
Every table is accuracy over the same fixed n = 10,000 NQ-open questions
(README of the repo: "a smaller sample of 10K entries was employed";
hallucination_report/*.md: "Total Samples: 10,000 per configuration"). Decoding
is greedy (temperature 0.0, do_sample=False) and the random documents are NOT
resampled per run -- they are read from a fixed pickle,
`data/10k_random_results_at60.pkl`, and sliced as `random_indices[:k]`, so the
k-document context is a deterministic prefix. Two runs of the same specification
should therefore differ only by GPU/batching nondeterminism.

The paper supplies its own measurement of that floor, and I use it rather than
assuming one. See FLOOR below.

Author: maria, 2026-08-12
"""
import importlib.util
import os
import math

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("t", os.path.join(HERE, "01_transcribe_tables.py"))
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)

N = 10000


def near_random(table, model):
    """Accuracy vs n_docs for `model` in the Near + random-documents setting."""
    return {n: acc for (n, pos, m, acc, _d, _s) in table if pos == "near" and m == model}


def report(label, a, b, note=""):
    keys = sorted(set(a) & set(b))
    diffs = [(k, a[k], b[k], b[k] - a[k]) for k in keys]
    print(f"\n--- {label} ---")
    if note:
        print(f"    {note}")
    print(f"    {'ndoc':>5} {'A':>8} {'B':>8} {'B-A':>9} {'|B-A|*N':>8}")
    for k, x, y, d in diffs:
        flag = "   <-- disagree" if abs(d) > 0.0005 else ""
        print(f"    {k:>5} {x:>8.4f} {y:>8.4f} {d:>+9.4f} {abs(d)*N:>8.0f}{flag}")
    bad = [d for _, _, _, d in diffs if abs(d) > 0.0005]
    print(f"    -> {len(bad)}/{len(diffs)} cells disagree by more than 5 questions in 10,000")
    return diffs


print("=" * 78)
print("A. CELLS THAT MUST BE IDENTICAL BY CONSTRUCTION (same run, reprinted)")
print("=" * 78)

t4_l2 = t.TABLE4["llama2"]
t5_l2 = t.TABLE5[("llama2", "Base")]
t6_l2 = t.TABLE6[("llama2", "Base")]
t4_l3 = t.TABLE4["llama3"]
t5_l3 = t.TABLE5[("llama3", "Base")]
t6_l3 = t.TABLE6[("llama3", "Base")]
for lbl, x, y in [("T4 llama2 vs T5 llama2/Base", t4_l2, t5_l2),
                  ("T4 llama2 vs T6 llama2/Base", t4_l2, t6_l2),
                  ("T4 llama3 vs T5 llama3/Base", t4_l3, t5_l3),
                  ("T4 llama3 vs T6 llama3/Base", t4_l3, t6_l3)]:
    same = all(abs(x[k] - y[k]) < 1e-9 for k in x)
    print(f"  {lbl}: {'IDENTICAL' if same else 'DIFFER'}")

print("""
  These four are the paper's internal control and they pass exactly. It means
  the Base column is one run reprinted three times, which is what it should be,
  and it means the tables were not independently retyped. Good.
""")

print("=" * 78)
print("B. SAME SPECIFICATION, TWO TABLES -- Table 2 (Near/random, 4-bit HF)")
print("   versus Table 7 (precision ablation, 4-bit column, Near/random)")
print("=" * 78)
d_l2 = report("Llama2, 4-bit",
              near_random(t.TABLE2, "llama2"), t.TABLE7[("llama2", "4bit")],
              "A = Table 2 (Near, Llama2). B = Table 7 (Llama2, 4bit). "
              "Both HuggingFace, 4-bit, gold Near, k random docs.")
d_mpt = report("MPT, 4-bit",
               near_random(t.TABLE2, "mpt"), t.TABLE7[("mpt", "4bit")],
               "A = Table 2 (Near, MPT). B = Table 7 (MPT, 4bit).")

print("""
  Rows 0, 4, 6, 8, 10 agree to the last digit for Llama2 and rows 0, 4, 6, 8 for
  MPT -- so these ARE the same run reprinted. Rows 12 and 14 for Llama2 do not.
  A single run cannot disagree with itself; one of the two tables carries numbers
  from a different execution at k = 12 and k = 14, and the paper does not say
  which or why.
""")

print("=" * 78)
print("C. THE LARGE ONE -- Table 4 'Base' versus Table 7 'FP16'")
print("=" * 78)
print("""
  Section 4.2: "Based on these findings, we use FP16 precision in all subsequent
  experiments." Table 4's Base column is a subsequent experiment on the same
  Random-Near setup with the same original prompt and 15-token cap. Read
  literally, Table 4/Llama2/Base and Table 7/Llama2/FP16 are the same
  specification.  They are not the same numbers.
""")
d_fp = report("Llama2: Table 7 FP16 (A) vs Table 4 Base (B)",
              t.TABLE7[("llama2", "fp16")], t4_l2)

FLOOR = abs(t.TABLE7[("llama2", "fp16")][0] - t4_l2[0])
print(f"""
  CALIBRATION. At k = 0 the two pipelines agree to {FLOOR:.4f} = {FLOOR*N:.0f} questions
  in {N:,}. With no random documents in the prompt the two are the same
  system and they behave like it. That number is an EMPIRICAL floor for
  run-to-run instability of this pipeline, measured by the authors without
  meaning to.
""")
worst = max((abs(d), k) for k, _, _, d in d_fp if k > 0)
print(f"  At k >= 10 the same two pipelines differ by up to {worst[0]:.4f} "
      f"({worst[0]*N:.0f} questions, at k = {worst[1]}).")
print(f"  Ratio of the largest disagreement to the k=0 floor: {worst[0]/FLOOR:.0f}x")

pon_effect_t4 = t4_l2[14] - t4_l2[0]
pon_effect_t7 = t.TABLE7[("llama2", "fp16")][14] - t.TABLE7[("llama2", "fp16")][0]
print(f"""
  AND THE POINT. The quantity under dispute in this whole literature is the
  Power-of-Noise effect, acc(k=14) - acc(k=0):

      from Table 4 (Base):        {pon_effect_t4:+.4f}
      from Table 7 (FP16):        {pon_effect_t7:+.4f}

  Same model, same items, same nominal specification, opposite sign. The
  disagreement between two printings of one experiment is {abs(pon_effect_t7-pon_effect_t4)/max(abs(pon_effect_t4),1e-9):.0f}x
  the effect itself as Table 4 measures it.
""")

print("=" * 78)
print("D. WHAT THE CODE SAYS THE DIFFERENCE ACTUALLY IS")
print("=" * 78)
print("""
  Checked in github.com/ina0105/The-Power-of-Noise-Reproduction @ f5a482d:

    jobs/*/run_experiments*.sh   every vLLM job sets DTYPE="bfloat16"
                                 (22 occurrences, no job sets float16)
    src/llm.py                   the HuggingFace path loads in the dtype the
                                 checkpoint ships and applies bitsandbytes
                                 quantization when asked

  So the paper's "FP16" (Table 7, HuggingFace) and everything downstream of
  Section 4.2 (vLLM) are not the same numeric format. bfloat16 and float16 have
  the same width and different splits -- 8 exponent / 7 mantissa bits versus
  5 / 10. A paper whose thesis is that undocumented inference settings
  manufacture the effect changes the float format between its precision
  ablation and every table that uses the ablation's conclusion.

  I cannot attribute the 12.5-point gap to dtype specifically: framework,
  dtype, stop-token list and batching all change together between Table 7 and
  Table 4. That is the finding. The comparison is not identified, and the
  paper's own claim that migrating to vLLM produced "negligible differences in
  evaluation outcomes between the two frameworks" (Sec 3.5) is contradicted by
  its own appendix at every document count except zero.
""")
