"""n4 -- does the deposit's complexity measure depend on WHICH form the HIG rule uses?

For Achagua (acg: terms bague, chamai, matalii; HIG rule uses 'matalii' for 4..100), build the forest exactly as
langstrategy.acg() does, then again with a distinct, invented higher-term form, and compare calc_complexity.
If equal, the shared string is a placeholder as far as the model is concerned: complexity and cost (ulim 3) both
describe 'three exact terms plus a distinct higher term', which is what the paper's Figure 3 caption says.

    <venv with anytree==2.8.0>/python -I n4_complexity_form_sensitivity.py <deposit dir>
Author: maria, 2026-11-12.
"""
import os
import sys

DEP = os.path.abspath(sys.argv[1])
sys.path.insert(0, DEP)
os.chdir(DEP)
import langstrategy  # noqa: E402
import language_tree  # noqa: E402

terms = ["bague", "chamai", "matalii"]
for label, hig in (("as deposited (HIG reuses 'matalii')", "matalii"), ("distinct invented higher form", "zz_higher")):
    forest = langstrategy.first_three([], terms)
    forest.append(language_tree.make_tree(hig, [4, 100], "HIG"))
    print(f"{label:40s} complexity = {language_tree.calc_complexity(forest)}")
orig = langstrategy.acg()[0]
print(f"{'langstrategy.acg() itself':40s} complexity = {language_tree.calc_complexity(orig)}")
