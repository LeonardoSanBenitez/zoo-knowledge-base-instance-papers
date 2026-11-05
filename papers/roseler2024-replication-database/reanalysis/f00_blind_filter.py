"""Blinded copy of FReD (FORRT Replication Database).

mark's known-answer control (2026-10-23) blinds maria to the fate of 8 Psychological Science 2014 papers until he
unblinds. FReD may contain their replications. This script drops every row that could be one of them BEFORE anything
is shown, over-inclusively (DOI match, or any first-author surname in ref/author/title of the ORIGINAL), and prints
nothing about the dropped rows -- not even a count, because a count is itself information about their fate.

Usage: python f00_blind_filter.py <FReD.xlsx> <out_csv>
Remove this filter only after mark has unblinded (record the date in the paper.json when that happens).
"""
import sys
import pandas as pd

DOIS = {"10.1177/0956797615572806", "10.1177/0956797614529979", "10.1177/0956797614552828", "10.1177/0956797614535937",
        "10.1177/0956797614567511", "10.1177/0956797614530571", "10.1177/0956797614547916", "10.1177/0956797614537833"}
SURNAMES = ["jara-ettinger", "jara ettinger", "desteno", "joel", "gaskell", "walasek", "maglio", "faivre", "mcnulty"]

x = pd.read_excel(sys.argv[1])
doi = x["doi_o"].astype(str).str.lower().str.replace("https://doi.org/", "", regex=False).str.strip()
hay = (x["ref_o"].astype(str) + " " + x["author_o"].astype(str) + " " + x["title_o"].astype(str)).str.lower()
drop = doi.isin(DOIS) | hay.apply(lambda s: any(n in s for n in SURNAMES))
x.loc[~drop].to_csv(sys.argv[2], index=False)
print("blinded copy written:", sys.argv[2])
