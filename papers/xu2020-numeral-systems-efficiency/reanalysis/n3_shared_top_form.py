"""n3 -- Xu, Liu & Regier (2020) deposit: exact-restricted languages whose 'higher' term reuses the form of the top exact numeral.

In langstrategy.py, some languages map ONE word form both to numeral ulim (a ONE/SUC rule) and to the range ulim+1..100
(a HIG rule). The cost function compute_cost_size_principle(ulim) assumes numeral ulim is uniquely identified. Under the
paper's own listener, a form covering {ulim..100} does not identify ulim; the consistent cost is size_principle(ulim - 1).
This script finds those languages by reading the source with ast (the code is never executed here), and re-scores them.

    python -I n3_shared_top_form.py <deposit dir> > out/n3_shared_top_form.txt
Author: maria, 2026-11-12.
"""
import ast
import math
import os
import sys

DEP = os.path.abspath(sys.argv[1])
src = open(os.path.join(DEP, "langstrategy.py"), encoding="utf-8", errors="replace").read()
tree = ast.parse(src)
NEED = [float(x) for x in open(os.path.join(DEP, "data/need_probs/needprobs_eng_fit.csv")).read().split()]


def size_principle(k):
    L = len(NEED)
    denom = L - k
    norm = sum(NEED[i] / denom for i in range(k, L))
    return sum(NEED[i] * -math.log(NEED[i] / denom / norm, 2) for i in range(k, L))


def hyp_complexity(tn):
    return tn * 3 + 4 if tn <= 3 else 13 + (tn - 3) * 4


# attested complexities as computed by their own code (n2 output), so this script needs no anytree
COMP = {}
for line in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "n2_deposit_exact_frontier.txt"), encoding="utf-8"):
    if line.startswith("  ") and "| ulim" not in line and ": ulim" in line:
        code = line.split(":")[0].strip()
        COMP[code] = int(line.split("|")[1])


def form_of(node, terms):
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) and node.value.id == "terms":
        return terms[ast.literal_eval(node.slice)]
    try:
        return ast.literal_eval(node)
    except Exception:  # noqa: BLE001
        return None


print("lang | ulim | n forms | exact forms (by rule) | HIG form | shared? | cost as coded | consistent cost | complexity | frontier at consistent k | dominated?")
for fn in [n for n in tree.body if isinstance(n, ast.FunctionDef) and len(n.name) == 3]:
    vals = {}
    for st in fn.body:
        if isinstance(st, ast.Assign) and isinstance(st.targets[0], ast.Name) and st.targets[0].id in ("num_type", "ulim", "terms"):
            try:
                vals[st.targets[0].id] = ast.literal_eval(st.value)
            except Exception:  # noqa: BLE001
                pass
    if vals.get("num_type") != 1:
        continue
    terms, ulim = vals.get("terms", []), vals["ulim"]
    exact, hig = {}, None
    for node in ast.walk(fn):
        if isinstance(node, ast.Call) and getattr(node.func, "id", getattr(node.func, "attr", "")) in ("first_three", "successors"):
            name = getattr(node.func, "id", getattr(node.func, "attr", ""))
            if name == "first_three":
                for c in range(3):
                    exact[c + 1] = terms[c]
            else:
                a, b = (ast.literal_eval(x) for x in node.args[2:4])
                for c in range(a, b):
                    exact[c + 1] = terms[c]
        if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "make_tree" and len(node.args) >= 3:
            op = form_of(node.args[2], terms)
            f = form_of(node.args[0], terms)
            num = form_of(node.args[1], terms)
            if op in ("ONE", "SUC") and isinstance(num, int):
                exact[num] = f
            if op == "HIG":
                hig = f
    shared = hig is not None and exact.get(ulim) == hig
    k_cons = ulim - 1 if shared else ulim
    c_coded, c_cons = size_principle(ulim), size_principle(k_cons)
    comp = COMP.get(fn.name)
    dom = None
    if comp is not None:
        dom = sum(1 for k in range(1, 100) if hyp_complexity(k) <= comp and size_principle(k) < c_cons - 1e-12)
    print(f"{fn.name} | {ulim} | {len(terms)} | {sorted(exact)} | {hig!r} | {'SHARED' if shared else 'no'} | {c_coded:.4f} | "
          f"{c_cons:.4f} | {comp} | {hyp_complexity(k_cons)} | {dom}")
