#!/usr/bin/env python3
"""One-shot generator for the three records added on 2026-09-02 alongside
kkm2023-conflict-resolved, and the artifact-id / evidence fixes to that one.
Kept in the tree because the records it writes are long and a future correction
should edit the record, not re-run this -- but the provenance of the first
version should be visible. maria, 2026-09-02."""
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def w(pid, obj):
    p = os.path.join(HERE, pid)
    os.makedirs(p, exist_ok=True)
    json.dump(obj, io.open(os.path.join(p, "paper.json"), "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)
    print("wrote", pid)


# ---------------------------------------------------------------- fix KKM ----
p = os.path.join(HERE, "kkm2023-conflict-resolved", "paper.json")
d = json.load(io.open(p, encoding="utf-8"))
for i, a in enumerate(d["artifacts"], 1):
    a["id"] = "a%d" % i
for c in d["claims"]:
    if c["id"] == "c1":
        c["evidence"] = ["a1", "a2"]
    if c["id"] == "c5":
        c["evidence"] = ["a1"]
json.dump(d, io.open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("patched kkm2023-conflict-resolved artifact ids + evidence")

# ------------------------------------------------- killingsworth 2021 --------
w("killingsworth2021-experienced-wellbeing", {
  "schema_version": "1.2",
  "id": "killingsworth2021-experienced-wellbeing",
  "title": "Experienced well-being rises with income, even above $75,000 per year",
  "authors": ["Matthew A. Killingsworth"],
  "year": 2021,
  "venue": "PNAS 118(4) e2016976118",
  "area": ["wellbeing-and-income"],
  "identifiers": {"doi": "10.1073/pnas.2016976118", "pmid": "33468644",
                  "url": "https://www.pnas.org/doi/10.1073/pnas.2016976118"},
  "record_status": "active",
  "read_depth": "read-and-reanalysed",
  "cost": {"tool_calls": 9, "bytes_downloaded": 89748,
           "compute_notes": "JATS full text 72,897 B + aggregate deposit 16,851 B. The aggregate file turned out to be the load-bearing artifact of the whole session: it carries per-band standard errors and person counts for ~32 variables, which is what made the measurement-artifact test in r09/r10/r11 possible at all.",
           "session": "2026-09-02 maria"},
  "triggers": [
    "is there a plateau in experienced well-being above 75000 dollars",
    "experience sampling study of income and happiness",
    "how many reports per person in trackyourhappiness",
    "slope of well-being on log income below and above 80000",
    "aggregate deposit with standard errors and person counts per income band",
    "a paper that reports two different totals for its own sample"],
  "methods": ["in-paper-table-transcription", "cross-table-checksum-reconciliation",
              "robust-dispersion-iqr"],
  "claims": [
    {"id": "c1",
     "statement": "Experienced well-being rises approximately linearly with log(income) with no plateau, and the slope above $80,000/y is approximately as steep as below it.",
     "scope": "33,391 employed US adults 18-65 with household income >= $10,000/y, 2009-2015, person-level means of momentary smartphone reports on a continuous 'Very bad'-'Very good' scale.",
     "quantities": [
       {"name": "wellbeing_log_income_slope_overall_sd_units", "value": 0.113, "unit": "SD of well-being per log(income)", "n": 33391, "source": "Table 1 col 1"},
       {"name": "wellbeing_log_income_slope_below_80k_sd_units", "value": 0.109, "unit": "SD per log(income)", "n": 33391, "source": "Table 1 col 1"},
       {"name": "wellbeing_log_income_slope_above_80k_sd_units", "value": 0.11, "unit": "SD per log(income)", "n": 33391, "source": "Table 1 col 1"},
       {"name": "wellbeing_log_income_slope_below_80k_sd_units_unrestricted", "value": 0.076, "unit": "SD per log(income)", "n": 41319, "source": "Table 1 col 3 (unrestricted US sample)"},
       {"name": "wellbeing_log_income_slope_above_80k_sd_units_unrestricted", "value": 0.101, "unit": "SD per log(income)", "n": 41319, "source": "Table 1 col 3 (unrestricted US sample)"},
       {"name": "esm_reports_total", "value": 1725994, "unit": "momentary reports", "n": 33391, "source": "Abstract and Results"},
       {"name": "esm_reports_total_methods", "value": 1704162, "unit": "momentary reports", "n": 33391, "source": "Materials and Methods, 'Experience Sampling Procedure': 'All other results for experienced well-being (e.g., regression results) are based on all 1,704,162 reports from 33,391 people.'"},
       {"name": "median_compliance_rate", "value": 0.72, "unit": "reports / notifications", "n": 33391, "source": "Methods"}],
     "evidence": ["a1", "a2"],
     "our_assessment": {
       "status": "accepted-narrower-scope",
       "why": "The central claim survives everything done to it here, including KKM 2023: the CENTRE of the well-being distribution rises with log income at a rate that does not change at $80,000 or at $100,000 (median slope 1.231 vs 1.273 points per log-unit either side of $100k, change z = 0.11; r07). What the paper misses is the second moment, which does change. Two internal notes. (i) The paper states its own report total twice with different values, 1,725,994 in the Abstract, the Significance statement and the Results, and 1,704,162 in the Methods -- a 21,832-report (1.3%) discrepancy, with the Methods sentence explicitly saying the smaller number is the one the regressions use. (ii) Table 1 column 3, the unrestricted sample, gives 0.076 below $80k and 0.101 above, i.e. a slope a third steeper above the threshold; the footnote describes all three columns as 'approximately as steep above $80,000/y as below it'.",
       "by": "maria, 2026-09-02"}},
    {"id": "c2",
     "statement": "The sample is not representative but behaves like one on the variables that can be compared, so the income-well-being relation should generalise.",
     "scope": "Self-selected participants of trackyourhappiness.org.",
     "our_assessment": {
       "status": "unverified",
       "why": "The generalisation argument is entirely about LEVELS and about the shape of the mean curve. Every finding that the 2023 paper and this reanalysis build on top of it is about DISPERSION, and self-selection into an app for tracking one's own happiness is exactly the kind of filter one would expect to compress or distort the second moment. Neither paper reports a dispersion comparison against a representative sample, and I could not construct one from the deposits.",
       "by": "maria, 2026-09-02"}}],
  "artifacts": [
    {"id": "a1", "role": "derived-data",
     "locator": "https://osf.io/nguwz/ file income_wellbeing.csv",
     "status": "verified-usable", "bytes": 16851,
     "sha256": "ac750a7f748a156b1f79dfed1e717dad14a59578c644654f52d0d5ef2fbeccfa",
     "local_path": "artifacts/k2021_income_wellbeing.csv",
     "fetch_cmd": "curl -sL -o k2021_income_wellbeing.csv https://osf.io/download/cfnbv/",
     "checked": {"on": "2026-09-02", "by": "maria",
       "how": "sha256sum; then reanalysis/r04_location_scale.py merges it against the 2023 person-level deposit, and r09-r11 use its per-variable standard errors and person counts",
       "result": "15 rows (one per income band) x 97 columns: mean, standard error and person count for ~32 variables. Reconciles with the SEPARATE 2023 person-level deposit to 3-4 significant figures on every band: person counts identical (n_diff = 0 for all 15 bands), band means differing by at most 0.012 points, band SDs by a factor of 0.999-1.003. Two files deposited two years apart, agreeing exactly. That cross-deposit check is cheap, almost nobody does it, and it is the only evidence available that either file is what it says it is."}},
    {"id": "a2", "role": "supplement",
     "locator": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7848527/fullTextXML",
     "status": "verified-usable", "bytes": 72897,
     "local_path": "artifacts/PMC7848527.xml",
     "fetch_cmd": "curl -sL -o PMC7848527.xml https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7848527/fullTextXML",
     "checked": {"on": "2026-09-02", "by": "maria",
       "how": "python tools/jats2txt.py PMC7848527.xml --tables --meta",
       "result": "Complete body and Table 1. The publisher PDF is behind Cloudflare from this box."}},
    {"id": "a3", "role": "raw-data",
     "locator": "granular per-report data, 'available to qualified researchers who wish to verify or extend the claims of this paper; contact the author for access information'",
     "status": "gated",
     "checked": {"on": "2026-09-02", "by": "maria",
       "how": "read the Data Availability statement; no request made",
       "result": "Gated by author correspondence. It is the artifact that would settle the one live threat to the 2023 paper's finding, because it contains the number of reports per person. Requesting it is a live option and a decision for Leonardo, not for me: it is a first contact with a named researcher about their published work."}},
    {"id": "a4", "role": "supplement",
     "locator": "SI Appendix (Tables S1-S9, Figs S1-S2)",
     "status": "dangling",
     "checked": {"on": "2026-09-02", "by": "maria",
       "how": "curl -sL https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7848527/supplementaryFiles -o PMC7848527_suppl.zip; file",
       "result": "190 bytes of nginx '503 Service Temporarily Unavailable' HTML, delivered with curl exit code 0 under the .zip filename requested. Table S1 (responses per secondary feeling) and Table S9 (regressions with demographic controls, below and above $80k) are cited in the body and were not obtainable. Retry before concluding the SI does not exist."}},
    {"id": "a5", "role": "in-paper-table",
     "locator": "Table 1 of the article, transcribed",
     "status": "verified-usable",
     "local_path": "artifacts/K2021.txt",
     "checked": {"on": "2026-09-02", "by": "maria",
       "how": "python tools/jats2txt.py PMC7848527.xml --tables",
       "result": "Three columns of slopes with sample sizes, extracted from JATS with row and column labels intact. Column 3 is the one worth keeping: it is the only place the below/above-$80k equality visibly fails."}}],
  "relations": [
    {"type": "cito:disagreesWith", "target": "kahneman2010-high-income",
     "why": "The paper exists to contradict the $75,000 plateau."},
    {"type": "cito:repliesTo", "target": "kkm2023-conflict-resolved",
     "why": "Reciprocal of KKM's repliesTo. Same author on both sides."},
    {"type": "zoo:reanalysedBy", "target": "maria2026-happiness-income-spread",
     "why": "Its aggregate deposit is used to test whether the dispersion finding in the 2023 paper is a measurement artifact."},
    {"type": "cito:sharesAuthorWith", "target": "kkm2023-conflict-resolved"}],
  "open_questions": [
    "Which report total is right, 1,725,994 or 1,704,162? The Methods sentence says the smaller one is what the regressions use, and the Abstract uses the larger. Neither deposit contains report counts, so it cannot be settled from the public materials.",
    "SI Appendix Table S1 gives responses per secondary feeling. That number would sharpen the measurement-artifact bound in maria2026-happiness-income-spread#c5 considerably. The SI was 503 on the day; retry."],
  "curation": {"author": "maria", "created": "2026-09-02", "verified": "2026-09-02",
               "notes_file": "instance-papers/papers/killingsworth2021-experienced-wellbeing/NOTES.md"}})

# -------------------------------------------------- kahneman 2010 stub -------
w("kahneman2010-high-income", {
  "schema_version": "1.2",
  "id": "kahneman2010-high-income",
  "title": "High income improves evaluation of life but not emotional well-being",
  "authors": ["Daniel Kahneman", "Angus Deaton"],
  "year": 2010,
  "venue": "PNAS 107(38) 16489-16493",
  "area": ["wellbeing-and-income"],
  "identifiers": {"doi": "10.1073/pnas.1011492107", "pmid": "20823223",
                  "url": "https://www.pnas.org/doi/10.1073/pnas.1011492107"},
  "record_status": "draft",
  "read_depth": "abstract-only",
  "cost": {"tool_calls": 6, "bytes_downloaded": 9000,
           "compute_notes": "Six retrieval attempts, all failed; see artifact a1. No assessments are carried in this record because none may be.",
           "session": "2026-09-02 maria"},
  "triggers": [
    "the 75000 dollar happiness threshold",
    "Kahneman Deaton 2010 emotional well-being plateau",
    "where does the 75000 number actually come from",
    "a paper that is free to read and still not retrievable"],
  "claims": [
    {"id": "c1",
     "statement": "Emotional well-being rises with log income but there is no further progress beyond an annual income of about $75,000, while life evaluation continues to rise.",
     "scope": "More than 450,000 responses to the Gallup-Healthways Well-Being Index, US, 2008-2009; dichotomous yes/no items about yesterday's emotions.",
     "quantities": [
       {"name": "claimed_satiation_income", "value": 75000, "unit": "USD/year (2008-9)", "n": "450,000+", "source": "SECOND-HAND, quoted in kkm2023-conflict-resolved. KKM note that $75,000 'is simply the midpoint of the 60 to 90K income category' and that 'a more precise statement would be that there is no further progress in average happiness beyond a threshold at or below 90K'."}],
     "our_assessment": {
       "status": "unverified",
       "why": "The primary source was not retrieved, so nothing here is assessed. Every number in this record is second-hand from KKM 2023, marked as such in its source field. Recording the paper anyway, because it is the anchor of a literature this corpus now holds three records on, and because a stub that says WHY it is a stub is more useful than a silent gap.",
       "by": "maria, 2026-09-02"}}],
  "artifacts": [
    {"id": "a1", "role": "supplement", "locator": "the article PDF / full text",
     "status": "absent",
     "checked": {"on": "2026-09-02", "by": "maria",
       "how": "six routes: (1) https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2944762/pdf/ -> 1,817 B of HTML; (2) https://www.ebi.ac.uk/europepmc/webservices/rest/PMC2944762/fullTextXML -> HTTP 200 with a ZERO-BYTE body; (3) https://www.pnas.org/doi/pdf/10.1073/pnas.1011492107 -> Cloudflare interstitial; (4) https://europepmc.org/articles/pmc2944762?pdf=render -> 403 on /api/getPdf; (5) https://pmc.ncbi.nlm.nih.gov/articles/PMC2944762/pdf/pnas.201011492.pdf -> 1,817 B of HTML; (6) NCBI OA service oa.fcgi -> 404, the endpoint is retired.",
       "result": "NOT RETRIEVABLE from this box. Unpaywall reports is_oa = true, oa_status = green, with exactly one location: the PMC record, which is the one that serves an interstitial. So the paper is free to read by a human with a browser and unavailable to any automated agent -- a state no availability metric in existence distinguishes from open. Semantic Scholar's openAccessPdf field points at route (4), which 403s. That is worth its own line: THREE independent open-access indexes assert this PDF is available and none of the URLs they give returns a PDF."}}],
  "relations": [
    {"type": "cito:disagreesWith", "target": "killingsworth2021-experienced-wellbeing"},
    {"type": "cito:repliesTo", "target": "kkm2023-conflict-resolved",
     "why": "Reciprocal: KKM qualifies this paper. Note the KKM footnote -- Angus Deaton did not participate in the adversarial collaboration and should not be taken as endorsing its conclusions."}],
  "open_questions": [
    "Leonardo has offered to fetch paywalled papers before. This one is not paywalled; it is bot-blocked, which is a different failure and may be easier to solve. Until it is read, kkm2023-conflict-resolved#c2 is accepted on argument rather than on evidence."],
  "curation": {"author": "maria", "created": "2026-09-02", "verified": "2026-09-02",
               "notes_file": "instance-papers/papers/kahneman2010-high-income/NOTES.md"}})
