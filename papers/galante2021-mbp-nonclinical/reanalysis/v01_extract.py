#!/usr/bin/env python3
"""v01 -- build an arm-level table of means, SDs and n from Galante et al. (2021),
for a variability-ratio analysis the original review did not perform.

THE QUESTION.  The review establishes that mindfulness-based programmes move the
AVERAGE of anxiety, depression, distress and well-being relative to a passive
control (SMD -0.56 to +0.33). It says nothing about whether they move the
VARIANCE. Those are different claims with different consequences:

  * If MBPs shift everyone by roughly the same amount, the treated arm's SD equals
    the control arm's, and there is no individual to "personalise" for.
  * If MBPs help some people a great deal and others not at all, the treated arm's
    SD must exceed the control arm's.

The variability ratio VR = SD_treated / SD_control is the standard instrument for
this (Nakagawa et al. 2015) and has been applied to antipsychotics, antidepressants
and psychotherapy for depression and PTSD -- where it lands near 1 every time. It
does not appear to have been applied to mindfulness in nonclinical settings, and
this deposit contains everything needed.

THE BUILT-IN NEGATIVE CONTROL, which is why this dataset is worth the work: it
carries BASELINE arm SDs as well as post-intervention ones. At baseline the two
arms are, by randomisation, draws from the same distribution, so the pooled lnVR
must be zero. Anything else measures extraction error, selective reporting or
failed randomisation, and would make the post-intervention number uninterpretable.
CONTRIBUTING.md rule 3 asks for a case where the answer is known in advance. Here
the data supply one.

PARSING POLICY.  Every field in this file is a string and several carry human
annotations ("assume 42", "NR", "impute SD"). Nothing is coerced silently:
unparseable values are counted, categorised and printed, never dropped quietly.
The one thing that must not happen is a row disappearing without anyone knowing.

Output: out_arms.csv, and a printed accounting of every row that did not make it.
"""
import io
import os
import re
import sys
from collections import Counter

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "..", "artifacts", "galante_csv")
# The Stata export is cp1252, not UTF-8: 0xd7 (multiplication sign), 0x96 (en
# dash), 0x92 (right quote), 0xfc (u-umlaut). Reading it as UTF-8 raises; reading
# it with errors='replace' silently corrupts an instrument name. Name the codec.
ENC = "cp1252"

CTRL_CAT = {"1": "passive", "2": "active-nonspecific", "3": "active-specific"}
KEEP_TRANGE = ["Baseline", "Postintervention", "1-6months", "6+months"]


def parse_number(s):
    """Return (value, note). note is '' for a clean number, otherwise the reason."""
    s = (s or "").strip()
    if s in ("", "NA", "NR", "NR ns", "nr", "-"):
        return None, "not-reported"
    if re.fullmatch(r"-?\d+(\.\d+)?", s):
        return float(s), ""
    m = re.fullmatch(r"(assume|approx|about|~|est\.?)\s*(-?\d+(\.\d+)?)", s, re.I)
    if m:
        return float(m.group(2)), "assumed-by-review-authors"
    m = re.search(r"-?\d+(\.\d+)?", s)
    if m:
        return float(m.group(0)), "extracted-from-annotated-string:" + s[:30]
    return None, "unparseable:" + s[:30]


def main():
    d = pd.read_csv(os.path.join(ART, "Outcomes_extracted_from_trials.csv"),
                    dtype=str, keep_default_na=False, encoding=ENC)
    sub = pd.read_csv(os.path.join(ART, "Data_for_sensitivity_subgroup_analyses.csv"),
                      dtype=str, keep_default_na=False, encoding=ENC)
    print("source rows %d, studies %d; moderator file rows %d"
          % (len(d), d.studytab_name.nunique(), len(sub)))

    reject = Counter()
    rows = []
    for _, r in d.iterrows():
        if r.trange not in KEEP_TRANGE:
            reject["timepoint not a level (change score or unlisted): " + r.trange] += 1
            continue
        # arm 1 is the mindfulness arm in 1142/1169 rows; check rather than assume
        if not re.search(r"mindful|MBSR|MBCT|mindfulness", r.a1, re.I) \
                and r.a1 not in ("Intervention group",):
            reject["arm 1 is not identifiably a mindfulness arm: " + r.a1[:28]] += 1
            continue
        if r.priority_oa1em_central not in ("Mean", "mean") \
                or r.priority_oa2em_central not in ("Mean", "mean"):
            reject["central tendency is not a mean in one/both arms"] += 1
            continue
        if r.priority_oa1em_dc != "SD" or r.priority_oa2em_dc != "SD":
            reject["dispersion is not an SD in one/both arms (%s / %s)"
                   % (r.priority_oa1em_dc[:14], r.priority_oa2em_dc[:14])] += 1
            continue
        vals, notes, bad = {}, [], False
        for arm in (1, 2):
            for field, col in (("n", "oa%dn" % arm),
                               ("m", "value_prior_oa%dem_central" % arm),
                               ("sd", "value_prior_oa%dem_dc" % arm)):
                v, note = parse_number(r[col])
                if v is None:
                    reject["%s missing for arm %d (%s)" % (field, arm, note)] += 1
                    bad = True
                    break
                vals["%s%d" % (field, arm)] = v
                if note:
                    notes.append("arm%d.%s=%s" % (arm, field, note))
            if bad:
                break
        if bad:
            continue
        if vals["sd1"] <= 0 or vals["sd2"] <= 0:
            reject["a reported SD is zero or negative"] += 1
            continue
        if vals["n1"] < 3 or vals["n2"] < 3:
            reject["arm n below 3, lnVR variance undefined"] += 1
            continue
        rows.append({
            "study": r.studytab_name.strip(),
            "domain": r.domain, "instrument": r.instrument[:60],
            "outcome": r["name"][:60],
            "trange": r.trange, "dir_imp": r.dir_imp,
            "ctrl_cat": CTRL_CAT.get(r.ctrlcata2.strip(), "unknown:" + r.ctrlcata2),
            "design": r.trial_design,
            "n_mbp": vals["n1"], "m_mbp": vals["m1"], "sd_mbp": vals["sd1"],
            "n_ctl": vals["n2"], "m_ctl": vals["m2"], "sd_ctl": vals["sd2"],
            "parse_notes": ";".join(notes),
            "arm1_label": r.a1, "arm2_label": r.a2,
        })

    out = pd.DataFrame(rows)
    print("\nKEPT %d arm-pair rows from %d studies" % (len(out), out.study.nunique()))
    print("\nEVERY ROW THAT DID NOT MAKE IT, and why "
          "(total dropped %d = %d source - %d kept):"
          % (len(d) - len(out), len(d), len(out)))
    for k, v in reject.most_common():
        print("  %5d  %s" % (v, k))
    assert sum(reject.values()) == len(d) - len(out), \
        "the rejection ledger does not add up -- a row vanished without a reason"
    print("  ledger balances: every source row is either kept or has a reason")

    print("\nkept rows by timepoint x control category")
    print(pd.crosstab(out.trange, out.ctrl_cat).to_string())
    print("\nkept rows by domain")
    print(out.domain.value_counts().to_string())
    print("\nrows carrying a parse note: %d" % (out.parse_notes != "").sum())
    if (out.parse_notes != "").sum():
        print(out.loc[out.parse_notes != "", ["study", "trange", "parse_notes"]]
              .head(20).to_string(index=False))

    # moderators
    sub = sub.rename(columns={"studytab_name": "study"})
    sub["study"] = sub["study"].str.strip()
    keep = ["study", "country", "USA", "participanttype", "contacthours",
            "nr_rand", "d1", "d2", "d3", "d4", "d5", "coi", "taught"]
    out = out.merge(sub[keep], on="study", how="left")
    miss = out.country.isna().sum()
    print("\nmoderator merge: %d of %d rows unmatched (%d studies)"
          % (miss, len(out), out.loc[out.country.isna(), "study"].nunique()))
    if miss:
        print("  unmatched study names: %s"
              % sorted(out.loc[out.country.isna(), "study"].unique())[:10])

    out.to_csv(os.path.join(HERE, "out_arms.csv"), index=False, encoding="utf-8")
    print("\nwrote out_arms.csv")


if __name__ == "__main__":
    main()
