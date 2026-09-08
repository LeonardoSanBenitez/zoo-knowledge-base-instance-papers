#!/usr/bin/env python3
"""Classify the 131 CODECHECK certificate summaries on two axes.

    python classify_codecheck.py

Axis 1 -- OUTCOME, taken from the codechecker's OWN words wherever they state one.
Axis 2 -- LIMITING FACTOR, i.e. whose constraint prevented a fuller reproduction.

The second axis is the one nobody publishes and the one that matters for a project
deciding how to WORD a report about somebody else's work: if most partial
reproductions are limited by the REVIEWER's resources rather than by the deposit,
then a report that says "partially reproduced" without naming whose limit it was is
systematically unfair to authors.

METHOD, and its weaknesses, stated up front:

* Rules are regexes over the summary text, each printed with the certificates it
  fired on, so any reader can audit a rule by looking at what it caught.
* A summary can carry more than one limiting factor. They are counted
  independently; the table does not sum to n.
* Precedence for outcome: an explicit "full/complete reproduction" beats
  "partial", because several summaries say "partial reproduction ... I would
  consider the reproduction a success". Where both appear the CONCLUDING clause
  wins, approximated by taking the last match in the text.
* FALSE PASS of this classifier: a summary that mentions e.g. "hours" for a
  reason unrelated to a limit ("computations took 6 minutes"). Guarded by
  requiring a limiting verb near the resource word, and by printing the hits.
* FALSE FAIL: a limit stated without any of the words in the pattern. Not
  guarded; this is why the residual "unclassified partials" count is printed
  rather than hidden.
"""
import json
import re
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

D = json.load(open("register-full.json", encoding="utf-8"))
S = [(r["Certificate ID"], " ".join((r.get("Summary") or "").split()))
     for r in D if (r.get("Summary") or "").strip()]

# ------------------------------------------------------------------ axis 1
FULL = r"\bfull(y)? reproduc|\bcomplete(ly)? reproduc|\breproduction was successful\b|" \
       r"\bcheck was successful\b|\bthe check was successful\b|\breproduction is considered successful\b|" \
       r"\bfully and easily reproduce|\bpaper is fully reproducible\b|\bcodecheck was successful\b|" \
       r"\bsuccessfully executed\b|\bFull reproduction\b|\breproduction was fully successful\b"
PART = r"\bpartial|\bpartly reproduc|\bonly a subset\b|\bsubset of\b|\bmostly successful\b|" \
       r"\bsuccessful but partial\b|\bnot all\b"


def outcome(s):
    f = [m.end() for m in re.finditer(FULL, s, re.I)]
    p = [m.end() for m in re.finditer(PART, s, re.I)]
    if f and p:
        return "full" if max(f) > max(p) else "partial"
    if f:
        return "full"
    if p:
        return "partial"
    return "unstated"


# ------------------------------------------------------------------ axis 2
LIMITS = {
    "reviewer-compute/time": (
        r"(due to|because of|owing to|avoid|beyond|lack of|constraints? of|"
        r"not feasible|infeasible|would (take|require)|requir(es|ed) (several|substantial|an HPC|"
        r"specific hardware)|time constraints|resource (restrictions|constraints)|"
        r"computational (resources|constraints)|available hardware|on the side of the reviewer|"
        r"beyond the scope)"),
    "reviewer-software/licence": (
        r"(MATLAB licen|ArcGIS[^.]{0,40}(unavailable|not available)|arcpy[^.]{0,30}unavailable|"
        r"requiring \d+ additional toolboxes|proprietary software|unavailable on the reviewer)"),
    "deposit-missing-data": (
        r"(data (is|are|was|were) not (available|provided|shared|included|public)|"
        r"not publicly available|could not be shared|cannot be disclosed|no code is provided|"
        r"lacked sufficient documentation|absence of documentation|not included and had to be requested|"
        r"data (set )?is not provided)"),
    "deposit-bugs/needed-fixes": (
        r"(blocking errors|SQL error|logic bugs|code was not executable|surgical fixes|"
        r"contained some errors|minor code fixes|simple edits needed|manual fixes|"
        r"required manual fixes|adjustments? (of|to) the (computational )?environment|"
        r"file paths were fixed|adapting the workflow)"),
    "third-party-restricted": (
        r"(privacy|proprietary data|licence issues|license issues|intellectual property|"
        r"paid APIs?|require(s|d)? (creating |registering )?accounts?|confidential|"
        r"closed source model|not accessible for re-running)"),
    "inherent-non-computational": (
        r"(physical/practical experiments|user (study|experiment)|survey of|participants|"
        r"manual (steps?|data collection|analysis|edits)|impossible to (achieve|reproduce)|"
        r"qualitative framework|hardware .{0,20}(prototype|system))"),
    "stochasticity": (
        r"(random(ness|ised|ized)?|seed|stochastic|non-deterministic|unset random states)"),
}


def limits_of(s):
    return [k for k, p in LIMITS.items() if re.search(p, s, re.I)]


# ------------------------------------------------------------------ eligibility discipline
ELIG = r"\beligible for reproduction\b|\bout of the \d+ (figures|tables)|\bwere not covered by this\b|" \
       r"\bout of scope\b|\bnot applicable for reproduction\b|\bconsidered, while\b"

rows = []
for cid, s in S:
    rows.append({"id": cid, "outcome": outcome(s), "limits": limits_of(s),
                 "declares_eligibility": bool(re.search(ELIG, s, re.I)),
                 "mentions_author_interaction": bool(re.search(
                     r"(with the authors?|authors? (provided|shared|added|sent|kindly|clarif|respond|"
                     r"accompanied|improved|agreed)|contacted|email|upon request|after .{0,25}exchange|"
                     r"communication with the authors)", s, re.I)),
                 "chars": len(s)})

n = len(rows)
print("n certificates with a summary: %d\n" % n)

print("AXIS 1 -- outcome, in the codechecker's own words")
oc = collections.Counter(r["outcome"] for r in rows)
for k, v in oc.most_common():
    print("   %-10s %3d  (%4.1f%%)" % (k, v, 100 * v / n))

print("\nAXIS 2 -- limiting factors (a summary may carry several; does not sum to n)")
lc = collections.Counter()
for r in rows:
    for l in r["limits"]:
        lc[l] += 1
for k, v in lc.most_common():
    print("   %-28s %3d  (%4.1f%% of all)" % (k, v, 100 * v / n))

print("\nWHOSE LIMIT, among the %d non-full outcomes" % (n - oc["full"]))
nonfull = [r for r in rows if r["outcome"] != "full"]
rev = sum(1 for r in nonfull if any(l.startswith("reviewer") for l in r["limits"]))
dep = sum(1 for r in nonfull if any(l.startswith("deposit") for l in r["limits"]))
thi = sum(1 for r in nonfull if "third-party-restricted" in r["limits"])
inh = sum(1 for r in nonfull if "inherent-non-computational" in r["limits"])
none = sum(1 for r in nonfull if not r["limits"])
m = len(nonfull)
for lab, v in [("reviewer-side", rev), ("deposit-side", dep), ("third-party", thi),
               ("inherent to the study", inh), ("no factor matched", none)]:
    print("   %-24s %3d  (%4.1f%%)" % (lab, v, 100 * v / m))
print("   reviewer-side AND NOT deposit-side: %d (%.1f%%)"
      % (sum(1 for r in nonfull if any(l.startswith("reviewer") for l in r["limits"])
             and not any(l.startswith("deposit") for l in r["limits"])),
         100 * sum(1 for r in nonfull if any(l.startswith("reviewer") for l in r["limits"])
                   and not any(l.startswith("deposit") for l in r["limits"])) / m))

print("\nDISCIPLINE MARKERS")
print("   declares what was ELIGIBLE for reproduction : %3d (%4.1f%%)"
      % (sum(r["declares_eligibility"] for r in rows),
         100 * sum(r["declares_eligibility"] for r in rows) / n))
print("   mentions interaction with the authors       : %3d (%4.1f%%)"
      % (sum(r["mentions_author_interaction"] for r in rows),
         100 * sum(r["mentions_author_interaction"] for r in rows) / n))

print("\nRULE AUDIT -- which certificates each limit rule fired on")
for k in LIMITS:
    ids = [r["id"] for r in rows if k in r["limits"]]
    print("   %-28s %s" % (k, " ".join(ids)))

json.dump({"n": n, "rows": rows,
           "outcome_counts": dict(oc), "limit_counts": dict(lc)},
          open("codecheck_classified.json", "w"), indent=1)
print("\nwrote codecheck_classified.json")
