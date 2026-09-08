#!/usr/bin/env python3
"""Hand-coded binding constraint for every CODECHECK certificate that reports a
less-than-complete reproduction.

    python handcode_limits.py

WHY BY HAND. The regex pass (`classify_codecheck.py`) was audited against the text
and failed in both directions, for reasons that are not fixable by better patterns:

  * "This reproduction required several hours of compute time, but the reproduction
    itself was straightforward" and "Due to long computation times, only a subset of
    the results could be checked" contain the same words and differ only in the
    consequence clause. (2020-011 vs 2021-001.)
  * "A full reproduction requires substantial computational resources" was classified
    as a FULL reproduction because the phrase "full reproduction" appeared after the
    word "Partial". It means the opposite. (2026-012, and 2026-011 the same way.)

So the coding below is one reader's judgement, and every row carries the fragment it
rests on so that a second reader can disagree per row rather than in general. That is
the most honest form available to a single coder: not "trust me", but "here is the
sentence, and here is what I made of it".

CODES for the binding constraint -- the thing that, if removed, would have allowed a
fuller reproduction:

  reviewer     the check ran out of the REVIEWER's compute, time, hardware or licence,
               or the reviewer chose a narrower scope. The deposit was not the limit.
  deposit      something the authors released was missing, undocumented, broken, or
               produced different numbers.
  third-party  data or software the authors are not free to share: privacy, IP,
               commercial licence, paid API, an account requirement.
  inherent     the study contains something no computational check can reproduce:
               a physical experiment, a human survey, a manual step.
  stochastic   the difference is randomness and nothing else.
  unclear      the summary states a partial outcome and does not say why.

Where two apply, both are listed and the FIRST is the one the summary presents as
binding.
"""
import collections
import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# id: (codes, evidence fragment quoted from the summary)
CODE = {
 "2020-014": (["deposit"], "Some of the original MATLAB code was provided ... this was a small subset of all the figures"),
 "2020-021": (["deposit"], "After some adjustments of the computational environment ... mostly successful"),
 "2020-022": (["deposit"], "some key figures were not created by the provided data and code"),
 "2021-001": (["reviewer"], "Due to long computation times, only a subset of the results could be checked"),
 "2021-002": (["third-party"], "not publicly available due to licence issues with the cooperating parties"),
 "2021-004": (["third-party"], "irreproducible because of proprietary data"),
 "2021-007": (["inherent", "reviewer"], "Some manual steps ... could not be reproduced, as well as a final step due to long execution time"),
 "2021-008": (["deposit"], "data provided by the authors via email ... figures ... are not identical to the figures in the paper"),
 "2022-002": (["deposit"], "the input data for Section 4.4 are not reproducible with the provided code"),
 "2022-003": (["third-party"], "authors claimed that input data cannot be disclosed"),
 "2022-005": (["reviewer"], "the time constraints of this review ... allowed only a partial reproduction ... with more time, a successful reproduction ... is highly likely"),
 "2022-007": (["third-party"], "a core analysis step based on proprietary software could not be evaluated"),
 "2022-008": (["third-party"], "Only two of the four online classification APIs were tested due to the requirement of registering accounts"),
 "2022-011": (["third-party", "deposit"], "One data set is not available due to privacy policy concerns ... one Figure was not reproducible"),
 "2022-013": (["deposit"], "One of the reproduced figures differed ... tables ... returned slightly different values"),
 "2022-014": (["deposit"], "the provided software scripts comprise reproduction of one out of the four data columns"),
 "2022-015": (["deposit"], "The repository contains only one out of two datasets presented in the paper"),
 "2022-016": (["deposit"], "no code is provided to visually recreate the figure ... For the rest of figures and tables, no code is provided"),
 "2023-005": (["third-party"], "not available due to intellectual property concerns"),
 "2023-007": (["deposit"], "the data processing steps were not detailed enough in the README files"),
 "2023-008": (["deposit"], "could be partially reproduced ... since the data used by the authors are not publicy available"),
 "2023-010": (["deposit", "stochastic"], "other quantitative results (tables in the paper) can not be created with the code"),
 "2024-006": (["reviewer"], "I did not reproduce the experiment or other results ... but I was able to set up and run the system"),
 "2024-007": (["reviewer"], "a prototype system that required specific hardware, therefore, I skipped this part"),
 "2024-013": (["reviewer"], "due to the lack of available computational resources on the side of the reviewer"),
 "2025-009": (["reviewer", "third-party"], "the time to collect the data is not feasible within the reproducibility review"),
 "2025-011": (["reviewer", "inherent"], "I only chose a subset of models to retrain ... A part of the inference ... was done manually"),
 "2025-012": (["reviewer", "third-party"], "due to computational and privacy constraints, only two basic examples could be reproduced"),
 "2025-013": (["deposit"], "could not be reproduced ... due to code issues; the GitHub repository contained 16 code files but lacked sufficient documentation"),
 "2025-016": (["reviewer"], "Partial reproduction with a focus on the analysis part presented in the paper"),
 "2025-017": (["reviewer"], "I could not re-run LLM-prompting and fine-tuning due to resource restrictions (time, specific hardware needed)"),
 "2025-028": (["deposit"], "Table 3 could not be linked to any of the output files"),
 "2026-001": (["unclear"], "Partial reproduction of figures in the publication"),
 "2026-005": (["deposit"], "the DEM file was not included and had to be requested from the authors, and the Figure 8 script contained an SQL error"),
 "2026-007": (["unclear"], "the reproduced results were mostly in accordance with the reported results"),
 "2026-008": (["deposit"], "some files in the repository were differentiated only by path rather than filename"),
 "2026-013": (["unclear"], "other manuscript outputs could be reproduced only partially"),
 "2026-015": (["reviewer"], "Successful but partial reproduction. The third part of the analysis reproduced smoothly"),
 # --- misclassified by the regex pass as FULL; they are not, and the reason is the
 #     phrase "a full reproduction would require ..."
 "2026-011": (["reviewer"], "A complete reproduction was infeasible as part of the review due to the computational environment required"),
 "2026-012": (["reviewer"], "A full reproduction requires substantial computational resources (in particular the fine-tuning in Step 2)"),
 "2026-016": (["third-party", "reviewer"], "data generation relied on paid APIs ... and indices/figures required ArcGIS/arcpy, which was unavailable on the reviewer's system"),
 "2025-006": (["reviewer"], "the author recommends the use of an HPC cluster, which is beyond the scope of this CODECHECK"),
 "2025-010": (["reviewer"], "I initially attempted a full reproduction, but had to abandon this due to time constraints"),
 "2025-019": (["reviewer"], "Figures 1-2 and Tables 1-3 were not covered by this CODECHECK"),
 "2024-014": (["reviewer"], "used a smaller sample dataset, since the original data set ... would require several days of computation on the available hardware"),
 "2024-015": (["reviewer"], "certain steps were omitted as they would take several hours to compute on the available hardware"),
 "2020-001": (["reviewer"], "Only visualiation steps performed, rather than machine learning (which could take several hours/days)"),
 "2020-015": (["deposit"], "The code to reproduce the figures given in the paper had more difficulties, with only some figures successfully recreated"),
 "2020-019": (["deposit"], "After initial problems because of absence of documentation, the reproduction was successful for some of the paper's figures, but not the maps"),
 "2020-023": (["deposit"], "After initial problems because of absence of documentation ... but not the maps"),
 "2020-005": (["deposit", "stochastic"], "two figures were very different from the originals. Some figures also varied considerably when changing the seed"),
 "2021-005": (["inherent"], "A complete reproduction is practically impossible to achieve"),
 "2022-009": (["inherent"], "a survey and user study ... almost impossible to reproduce"),
 "2022-010": (["inherent"], "the physical/practical experiments could not be reproduced"),
 "2024-008": (["reviewer", "inherent"], "confirm that that the analysis runs as intended, but not check the validity of the outputs shown in the paper"),
 "2024-009": (["inherent"], "The first two steps in the research design are out of scope of this reproducibility review"),
 "2024-022": (["deposit"], "The repository did not provide code to reproduce other plots (Figs. 7, 10 and 11)"),
 "2025-018": (["reviewer"], "To avoid the lengthy execution time required to run the full experiments, the pre-computed results provided in the repository were used"),
 "2026-019": (["stochastic"], "structural changes can occur, probably due to a non-deterministic order when processing input files"),
 "2024-016": (["stochastic"], "The resulting figures were not an exact match due to stochasticity"),
 "2023-011": (["deposit"], "With some fixes, the code was confirmed to work"),
 "2026-017": (["deposit"], "several surgical fixes were still required to address environment-specific dependency conflicts ... and logic bugs in the provided scripts"),
 "2026-005b": None,  # placeholder guard, removed below
}
CODE.pop("2026-005b")

D = json.load(open("register-full.json", encoding="utf-8"))
SUM = {r["Certificate ID"]: " ".join((r.get("Summary") or "").split()) for r in D}

# every coded fragment must actually occur in that certificate's summary
bad = []
for cid, (codes, frag) in CODE.items():
    s = SUM.get(cid, "")
    core = frag.split(" ... ")[0][:40]
    if core.lower() not in s.lower():
        bad.append((cid, core))
print("PROVENANCE CHECK -- every quoted fragment found in its own summary")
if bad:
    for cid, core in bad:
        print("  MISMATCH %s : %r" % (cid, core))
else:
    print("  ok, %d/%d fragments verified against register-full.json" % (len(CODE), len(CODE)))

n_total = sum(1 for r in D if (r.get("Summary") or "").strip())
n_coded = len(CODE)
print("\n%d of %d certificates report a less-than-complete reproduction "
      "and are coded here (%.0f%%)." % (n_coded, n_total, 100 * n_coded / n_total))

prim = collections.Counter(c[0][0] for c in CODE.values())
anyc = collections.Counter()
for codes, _ in CODE.values():
    for c in codes:
        anyc[c] += 1

print("\nBINDING CONSTRAINT (the code the summary presents as primary)")
for k, v in prim.most_common():
    print("   %-12s %3d  (%4.1f%%)" % (k, v, 100 * v / n_coded))

print("\nMENTIONED AT ALL (a row may carry two)")
for k, v in anyc.most_common():
    print("   %-12s %3d  (%4.1f%%)" % (k, v, 100 * v / n_coded))

not_the_deposit = sum(1 for codes, _ in CODE.values() if "deposit" not in codes)
print("\nTHE NUMBER THAT MATTERS FOR HOW A REPORT IS WORDED:")
print("   %d of %d incomplete reproductions (%.1f%%) were NOT limited by anything the "
      "authors did or failed to do." % (not_the_deposit, n_coded, 100 * not_the_deposit / n_coded))
print("   Reviewer-side alone accounts for %d (%.1f%%)."
      % (prim["reviewer"], 100 * prim["reviewer"] / n_coded))

# ---- sensitivity: how much does the headline depend on the three `unclear` rows
#      and on rows where "reviewer" is a scope CHOICE rather than a hard constraint?
unclear_ids = [k for k, v in CODE.items() if v[0][0] == "unclear"]
scope_choice = ["2024-006", "2025-016", "2026-015", "2020-001"]
worst = sum(1 for cid, (codes, _) in CODE.items()
            if "deposit" not in codes and cid not in unclear_ids)
print("")
print("SENSITIVITY")
print("   if all %d `unclear` rows were in fact deposit-limited: %d/%d = %.1f%%"
      % (len(unclear_ids), worst, n_coded, 100 * worst / n_coded))
print("   the %d rows where `reviewer` is a scope CHOICE rather than a hard limit "
      "(%s) are still not deposit-limited under any recoding, so they do not move the "
      "direction." % (len(scope_choice), ", ".join(scope_choice)))
print("   RANGE: %.0f%% to %.0f%% of incomplete reproductions are not the deposit's fault."
      % (100 * worst / n_coded, 100 * not_the_deposit / n_coded))

json.dump({"n_certificates_with_summary": n_total, "n_coded": n_coded,
           "sensitivity_low": worst, "unclear_ids": unclear_ids,
           "primary": dict(prim), "any": dict(anyc),
           "not_limited_by_deposit": not_the_deposit,
           "coding": {k: {"codes": v[0], "evidence": v[1]} for k, v in CODE.items()}},
          open("codecheck_handcoded.json", "w"), indent=1)
print("\nwrote codecheck_handcoded.json")
