# MPE-92M reanalysis — replicability of the factor structure

maria, 2026-08-16. Findings and their caveats live in `../NOTES.md`; the
machine-readable record is `../paper.json`. This file is only how to re-run it.

## Get the data (it is NOT stored here)

```
curl -sL -o mpe.zip "https://osf.io/download/xerhg/"
unzip -o mpe.zip && rm -rf __MACOSX
```

The link printed in the 2021 paper (`osf.io/gb76x`) is **410 Gone**; the 2024
correction (PLOS ONE e0314290) repoints it to `xerhg`. Do not spend calls on the
printed one.

- `MPE92M_Gamma_Metzinger_271020_stata14_R.dta` — 2435125 bytes,
  sha256 `a85e6e521f01127cded59f3eba31d7f10ee3d6f7b6ca93d7d37b3a9196dac9ca`.
  Use this variant; the plain Stata 14 file has a string column too long for
  some readers.
- The archive also ships all five language versions of the questionnaire as PDF,
  which is what makes item wording auditable.

## Dependencies

```
pip install pandas numpy scipy scikit-learn factor_analyzer
```

## Run, in this order

```
python validate_synthetic.py       #  ~99s  validate the instrument FIRST
python run_replicability.py        # ~250s  -> results_replicability.json
python run_clone_test.py           # ~150s  -> results_clone.json
python run_clone_oblique.py        # ~180s  -> results_clone_oblique.json
python run_groups.py               # ~300s  -> results_groups.json
python run_perturbation_sweep.py   #  ~90s  -> results_sweep.json
```

`validate_synthetic.py` is first on purpose and is not optional. It is the only
thing standing between this analysis and the failure mode that produced it —
an instrument that agrees with you because it cannot see anything. If its three
cases (TRUE-5 recovered with a cliff; pure noise pinned at .10–.33; general +
specific not inflating spurious factors) do not come out, nothing downstream is
interpretable.

## `mpelib.py`

Instrument-agnostic given an item matrix, which is the point: pointing it at
another phenomenology questionnaire (MODTAS, PCI, 5D-ASC, MEQ30) is the top
open question in `../paper.json`. Only `load()` is MPE-specific.

Two implementation facts worth knowing before editing:

1. `factor_analyzer` refuses `method='principal'` on a correlation matrix. So
   items are **rank-transformed and passed as raw data** — Pearson on ranks is
   Spearman, verified at 1.9e-15 by `check_rank_trick()`. Do not "simplify" this
   to a Pearson fit on raw scores; that silently stops reproducing the paper.
2. There are no bare `except` blocks, deliberately. An earlier version swallowed
   every fit failure and reported an empty result set as if it were data.

## Earlier pass

`analyze.py` / `efa.py` from 2026-07-31 (eigenvalues, Horn parallel analysis,
oblimin loadings) are in `.claude/memory/maria/mpe92m_reanalysis/` and are the
source of claims c2's numbers. They predate this folder; leave them where they
are unless someone re-runs and re-verifies them here.
