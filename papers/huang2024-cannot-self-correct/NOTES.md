# huang2024-cannot-self-correct -- notes (maria, 2026-11-07)

This is the premise MASS starts from. What I added (h01): Figure 1 gives the paired transitions, so exact McNemar
tests are possible for each model and task. Four of the eight cells show a real drop: the weak or suggestible
cases (Llama-2 on both tasks, GPT-3.5 on CommonSenseQA, GPT-4 on GSM8K). In the other four (GPT-4-Turbo on both
tasks, GPT-4 on CommonSenseQA, GPT-3.5 on GSM8K) the change is indistinguishable from zero. So the lesson is
"self-correction without an outside signal does not help, and it harms the unsure", not "it always harms". Strong
models mostly leave their answer alone (88-96% unchanged).

For the area this matters in a specific way. MASS's self-judge is not asked to correct, only to choose between two
outputs. That differs from self-correction, and nothing here measures it. The closest measurement in MASS is its
73% agreement with the external panel, which lacks a denominator. The debate result (Table 7) is the first
equal-compute baseline in this lineage: debate loses to majority voting at 9 responses each by 5.2 pp on 1319
questions.
