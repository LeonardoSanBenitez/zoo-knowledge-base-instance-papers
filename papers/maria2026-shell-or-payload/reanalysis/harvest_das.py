#!/usr/bin/env python3
"""Harvest data-availability statements and the links inside them, from a stratified
sample of PLOS ONE open-access articles.

    python harvest_das.py            # writes das_links.json

WHY. The question is: **when a data link resolves, how often does it return a payload
rather than a shell?** Nobody has measured it. Briney 2024 gets closest -- 13.4% of shared
URLs point at a website homepage -- but a homepage is only one shell shape. A Git LFS
pointer, a client-rendered single-page-application frame and a login wall are others, and
all of them return HTTP 200 with bytes.

To measure that I need a corpus of real data links. This harvests one.

SAMPLING. Four year strata (2016, 2019, 2022, 2025), PLOS ONE, open access, taken in the
order Europe PMC returns them. That is NOT a random sample and the record says so: it is
whatever the search index puts first, which is correlated with PMCID and therefore roughly
with deposit order within the year. Age strata are here so that any rate can be reported
against publication age, which is the one covariate everything in this literature depends on.

ONE JOURNAL, ON PURPOSE. PLOS ONE requires a data availability statement in every article
and makes publication conditional on the policy. That removes the biggest confound in a
mixed corpus -- whether a statement exists at all -- and it costs external validity, which
is the trade this measurement wants: I am measuring the behaviour of LINKS, not the
behaviour of journals.
"""
import json
import re
import sys
import time
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
UA = {"User-Agent": "zoo-research/1.0 (mailto:lsbenitezpereira@gmail.com)"}
YEARS = [2016, 2019, 2022, 2025]
PER_YEAR = 40


def get(url, tries=4):
    for i in range(tries):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90)
            return r.status, r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                time.sleep(2 * (i + 1))
                continue
            return e.code, b""
        except Exception as e:  # noqa: BLE001
            time.sleep(1 + i)
            last = type(e).__name__
    return "EXC", b""


def search(year, n):
    q = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?query="
         "JOURNAL%%3A%%22PLoS%%20One%%22%%20AND%%20OPEN_ACCESS%%3Ay%%20AND%%20PUB_YEAR%%3A%d"
         "&format=json&pageSize=%d&resultType=lite" % (year, n))
    s, b = get(q)
    if s != 200:
        return []
    return [(r.get("pmcid"), r.get("doi"), r.get("title", "")[:120])
            for r in json.loads(b)["resultList"]["result"] if r.get("pmcid")]


DAS_PATTERNS = [
    r'<custom-meta[^>]*id="data-availability"[^>]*>.*?</custom-meta>',
    r'<sec[^>]*sec-type="data-availability"[^>]*>.*?</sec>',
    r'Data Availability[^<]{0,40}</title>.{0,4000}?</sec>',
]
URL_RE = re.compile(r'(?:https?://|www\.)[^\s"<>\)\],;]+', re.I)
DOI_RE = re.compile(r'\b10\.\d{4,9}/[^\s"<>\)\],;]+', re.I)


def extract_das(xml_text):
    for pat in DAS_PATTERNS:
        m = re.search(pat, xml_text, re.S | re.I)
        if m:
            txt = re.sub(r"<[^>]+>", " ", m.group(0))
            return re.sub(r"\s+", " ", txt).strip()
    return None


def main():
    out = []
    for y in YEARS:
        hits = search(y, PER_YEAR)
        print("%d: %d article(s) from the search index" % (y, len(hits)))
        for pmcid, doi, title in hits:
            s, b = get("https://www.ebi.ac.uk/europepmc/webservices/rest/%s/fullTextXML" % pmcid)
            if s != 200 or len(b) < 500:
                out.append({"year": y, "pmcid": pmcid, "doi": doi, "status": s, "das": None})
                continue
            xml = b.decode("utf-8", "replace")
            das = extract_das(xml)
            urls = sorted(set(u.rstrip(".") for u in URL_RE.findall(das or "")))
            dois = sorted(set(d.rstrip(".") for d in DOI_RE.findall(das or "")))
            out.append({"year": y, "pmcid": pmcid, "doi": doi, "title": title,
                        "status": s, "xml_bytes": len(b),
                        "das": das[:1200] if das else None,
                        "urls": urls, "dois": dois})
            time.sleep(0.25)
        print("   with a DAS: %d ; with >=1 url: %d ; with >=1 doi-in-das: %d"
              % (sum(1 for r in out if r["year"] == y and r.get("das")),
                 sum(1 for r in out if r["year"] == y and r.get("urls")),
                 sum(1 for r in out if r["year"] == y and r.get("dois"))))
    with open("das_links.json", "w", encoding="utf-8") as fh:
        json.dump({"years": YEARS, "per_year": PER_YEAR, "n_articles": len(out),
                   "sampling": "Europe PMC search index order, not random. See module docstring.",
                   "articles": out}, fh, indent=1, ensure_ascii=False)
    nurl = sum(len(r.get("urls") or []) for r in out)
    ndoi = sum(len(r.get("dois") or []) for r in out)
    print("\n%d articles, %d URL(s), %d DOI(s) inside data availability statements"
          % (len(out), nurl, ndoi))
    print("wrote das_links.json")


if __name__ == "__main__":
    main()
