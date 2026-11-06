# mosolova2026-wsi-llm-era -- notes (maria, 2026-11-06)

Read for arena-lsc (SemEval-2027 Task 3), while pre-registering InventoryBreadth.

**What reproduces.** The 1cpl rows from the released csvs, to the printed decimal (r01). 1cpex is a few tenths low.

**What the headline means.** "Nothing beats one cluster per lemma" is arithmetic of the sample: 28% of dev instances
belong to monosemous lemmas (1cpl perfect there), and on polysemous lemmas 1cpl is 63.4. A WSI system is therefore
judged mostly on whether it refrains from splitting -- the same thing BCubed rewards in SemEval-2027 Task 3 1a, where
arena finding F7 says "1b forgives merging, not splitting" and precision on minority senses beats recall.

**Relevance to the arena.** (1) Their future-work idea (induce a sense list, then assign) is our llm_inventory.py;
their direct-clustering LLM result (GPT-4o 66.9 < 1cpl) and our induce-assign result (1a falls by .17 on SV dev) agree:
LLM inventories over-split for BCubed. (2) External k beats internal k -> H3 of InventoryBreadth. (3) Unlabeled
augmentation (+100-150 corpus usages per lemma) is a cheap untested lever for the arena.
