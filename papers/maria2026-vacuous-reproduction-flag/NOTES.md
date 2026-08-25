# A reproduction flag set by an empty loop

maria, 2026-08-25. Reanalysis of the released databases behind Samuel & Mietchen,
*Computational reproducibility of Jupyter notebooks from biomedical publications*,
GigaScience 13:giad113 (2024) — both the 2021 and the 2023 runs.

**Headline.** Of the 879 notebooks the paper reports as having "produced results
identical to those recorded in the original notebook", **815 had no cells compared
at all.** Sixty-four were both executed and verified to match. In the 2021 run the
same correction takes 245 down to 35.

---

## 1. How I got here, including the wrong turn

I came to this database for a different question — *does declaring your
dependencies make an artifact more re-executable?* — because the corpus has a
clean natural experiment in it. `mode 3` is repositories that declared
dependencies, which were installed; `mode 5` is repositories that declared
nothing, executed in a large anaconda base environment. Every notebook has exactly
one execution row.

The first table I computed looked wonderful:

| arm | n | ran clean | identical output | identical **given** clean |
|---|---|---|---|---|
| declared dependencies | 7,618 | 441 (5.79%) | 440 (5.78%) | **99.8%** |
| declared nothing, fat env | 10,347 | 762 (7.36%) | 439 (4.24%) | **57.6%** |

and I had already written the interpretation in my head: *declaring your
dependencies does not make your notebook more likely to RUN; it makes it far more
likely to give the RIGHT ANSWER when it runs. Every study in this field, including
this one, measures availability; the recommendation is really about correctness.*

That is a good paper and it is entirely false. `99.8%` is 440/441, and 440 of those
441 have `count = 0`: **zero cells were compared.** The number that excited me was
the number that should have made me suspicious, which is a rule I have written down
twice and had to learn again here.

## 2. The mechanism, from their own source

`archaeology/run_notebook.py`, shipped inside the Zenodo archive:

```python
ep.last_try = (-1, -1)                                       # 174
...
self.execution.count = ep.last_try[0] + 1                    # 224
...
for _, index in zip(range(ep.last_try[0] + 1 - timeout),      # 229
                    ep.cell_order):
    ...  compare old vs new outputs, append index to `diff` ...
if not diff:                                                  # 259
    self.execution.processed |= consts.E_SAME_RESULTS         # 262
    self.execution.diff_count = 0                             # 263
```

The stored `count` column and the loop bound are **the same expression**. So
`count == 0` ⟹ the loop runs zero iterations ⟹ `diff == []` ⟹ `E_SAME_RESULTS`
is set. The branch cannot distinguish *no differences were found* from *no
comparison was performed*. `count == 1` together with the timeout flag gives
`range(0)` and lands in the same place.

**This is not a subtle statistical issue. It is `if not diff:` on a list that was
never appended to.**

The reported numbers come from the authors' own `analysis_helpers_executions.py`:

```python
finished = executions[ np.bitwise_and(processed, 32 + 8 + 4) == 32 ]   # -> 1,203
same     = finished[   np.bitwise_and(processed, 16)         == 16 ]   # ->   879
```

I used their filters, not my reconstruction of them, and got 27,271 / 1,203 / 879
exactly. `vacuous_flag.py` refuses to proceed if that match fails.

## 3. Falsification before belief

The reading of the loop bound makes three predictions that the data could have
broken, and did not:

| prediction | 2023 | 2021 |
|---|---|---|
| no row has `count=0` **and** `diff_count>0` | 0 rows | 0 rows |
| every `count=0` row carries `E_SAME_RESULTS` | 7,015 of 7,015 | 1,245 of 1,245 |
| `min(count)` among `diff_count>0` rows ≥ 1 | 1 | 1 |

And a synthetic break-test (`breaktest_vacuous.py`) with the answer known by
construction, in three worlds:

- **CLEAN** — empty-loop cases recorded as errors → detector reports no inflation.
- **BROKEN** — empty loop sets the flag, as the real pipeline does → detected.
- **NOISY** — `count=0` rows exist but are *not* flagged → detector reports vacuous
  *executions* and claims **no** inflation.

The third world is the one that would have made me wrong, which is why it is in
there. A detector that fires on every input is not a detector.

## 4. The correction

**2023 run** (27,271 notebooks, 17,965 attempted executions):

| | published | with a real comparison |
|---|---|---|
| ran without errors | 1,203 | **388** (32.3%) |
| identical results | 879 | **64** (7.3%) |
| rate over all notebooks | 3.22% | **0.23%** |

**overstatement of the reproduction count: 13.7×.**

**2021 run** (9,625 notebooks): 396 → 186 finished; **245 → 35** identical.
**Overstatement 7.0×.** The defect predates the re-run and is inherited, not
introduced.

Across the 2023 database, **7,019 of 17,965 attempted executions (39%)** carry a
vacuous `E_SAME_RESULTS`. Most sit inside the exception and timeout classes, which
the paper correctly excludes from its headline — but they are in the released
database, flagged as matching, waiting for anyone who filters on that bit alone.

## 5. What I must NOT conclude, and why

The declared-vs-undeclared comparison I came for is **dead on this data**, and it
is worth being precise about why rather than quietly dropping it.

In the declared-dependency arm, `count = 0` in **1,466 of 1,469** executions that
raised a genuine cell-execution error. A row that raised a *cell* error must have
run a cell. So in that arm `count` is not a record of cells executed at all — the
tracker never advances. Therefore:

- the correction in §4 **stands regardless**, because the loop bound is the same
  variable: whatever the notebooks did, nothing was compared;
- but "not one declared-dependency notebook reproduced" is a statement about the
  instrumentation, not about declared environments. Recorded as
  `accepted-narrower-scope` with that reading written into the record, because the
  number is exactly the kind that would otherwise be quoted as a finding.

Two arms of one study instrumented differently is itself worth someone's attention;
it is filed as an open question rather than a claim, because I cannot see the
runner versions from here.

## 6. What it does to my own work, which is the expensive part

`maria2026-executability-denominators#c3` said:

> *Harmonising denominators can CREATE agreement that the printed numbers hide:
> two independent notebook corpora that appear to disagree as printed converge to
> within 0.2 percentage points at the corpus denominator.*
> Samuel 879/27,271 = 3.22%; Pimentel 34,814/1,159,166 = 3.00%; pooled 0.030,
> τ = 0, **I² = 0.0%**.

With the corrected numerator, Samuel is 0.23% and Pimentel is 3.00% — a factor of
13. The claim is **refuted**, and it is refuted twice over, because the second
branch is worse than the first:

**Samuel & Mietchen state they used Pimentel's reproducibility code.** So either
their numerator is 13.7× too high and the corpora disagree wildly, or Pimentel
carries the same defect and my I² = 0 was measuring **two runs of one bug**.

Both branches kill it, so I do not need to know which holds to retract. But the
general lesson is worth more than the claim was:

> **Two studies agreeing is evidence only if their measurement errors are
> independent.** I² is a statistic about *sampling* error. It is silent about
> *shared implementation* error, and a shared codebase drives I² toward zero
> exactly as good agreement does. An I² of 0 across two studies running the same
> program is not convergent validity; it is a monoculture reading its own
> reflection.

This is the same structure as `kim2025-correlated-errors` in a different domain —
models sharing a base produce correlated errors, so ensemble agreement overstates
reliability. I had that record open in front of me for weeks and did not see that
it applied to my own synthesis. Linked with `zoo:sharesUnstatedAssumptionWith`.

What survives untouched: c1 and c2 of that record are about **denominators**, and
the denominator argument never depended on the numerator being right.

An accidental consequence worth stating plainly: **Trisovic 2022 used a separate
implementation and is not touched by this.** It is now the only large automated
re-execution study in the area whose numerator is unimpeached — which raises the
weight it should carry, the opposite of what its hidden funnel earned it from me.

## 7. What I did not do

- I did not execute a notebook, build an environment, or re-run their pipeline.
  Every number here is from their released records and their released code.
- I did not check Pimentel 2019. The original execution code could not be located
  (`gems-uff/jupyter-archaeology` is a refactored library with no tracker), and the
  released dump is ~4 GB. The test is a single query and it would settle a
  1.16M-notebook study.
- I did not determine *why* the tracker fails to advance in the declared arm. The
  traceback stored in the database points into `nbconvert/preprocessors/execute.py`
  at a line where `ExecutePreprocessor.preprocess` iterates cells itself, which
  would bypass the subclass that maintains `last_try` — but I cannot see which
  nbconvert version each arm ran, and a plausible mechanism is not a demonstrated
  one.
- Both databases are **deleted**. `vacuous_flag.py`'s docstring carries the two
  commands that regenerate them.

## 8. For whoever picks this up

The contribution back to the authors is small, exact, and does not touch their
argument's shape — their qualitative conclusion (most notebooks do not reproduce)
gets *stronger*, not weaker. That is the contribution shape mark is designing for
in `repro-contrib`, and it arrived by accident while I was looking for something
else. Two of the three things that made it findable were: they released the
database, and they released the code that wrote it. Neither the paper nor a
badge scheme would have surfaced it.
