"""Fetch the abstracts of the 124 MBT trials (S2/S3 Appendix list: first author, year, journal) from PubMed,
so that k (mental-health outcomes reported per abstract) can be coded instead of swept.

Search per trial: <surname>[au] AND <year>[dp] AND (mindfulness OR MBSR OR MBCT OR meditation) -- journal used to
break ties (abbreviation compared loosely). Multi-publication trials list several first authors; the first is used.
Dissertations (13) are expected to miss.
Usage: python c02_fetch_abstracts.py <s003.docx> <out_json>
"""
import json, re, sys, time, zipfile, urllib.parse, urllib.request

x = zipfile.ZipFile(sys.argv[1]).read("word/document.xml").decode("utf8")
rows = []
for tr in re.findall(r"<w:tr[ >].*?</w:tr>", x, re.S):
    cells = [re.sub(r"<[^>]+>", "", "".join(re.findall(r"<w:t[^>]*>[^<]*</w:t>", tc))) for tc in re.findall(r"<w:tc>.*?</w:tc>", tr, re.S)]
    rows.append(cells)
E = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


def get(url):
    for i in range(4):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return r.read().decode("utf8")
        except Exception:
            time.sleep(2 + 3 * i)
    return ""


out = []
for r in rows[1:]:
    label = r[0]
    m = re.match(r"\s*([^,]+),\s*(\d{4})(.*)$", label)
    if not m:
        out.append({"label": label, "status": "unparsed"}); continue
    au, yr, rest = m.group(1).strip(), m.group(2), m.group(3)
    journal = re.split(r"[A-Z][a-z]+,\s*\d{4}", rest)[0].strip().rstrip("abcd ")
    term = f'{au}[au] AND {yr}[dp] AND (mindfulness OR MBSR OR MBCT OR meditation OR "mindfulness-based")'
    ids = re.findall(r"<Id>(\d+)</Id>", get(E + "esearch.fcgi?db=pubmed&retmax=10&term=" + urllib.parse.quote(term)))
    time.sleep(0.4)
    rec = {"label": label, "author": au, "year": yr, "journal_hint": journal, "pmids": ids}
    if ids:
        xml = get(E + "efetch.fcgi?db=pubmed&rettype=abstract&retmode=xml&id=" + ",".join(ids))
        time.sleep(0.4)
        arts = []
        for a in re.findall(r"<PubmedArticle>.*?</PubmedArticle>", xml, re.S):
            ta = re.search(r"<ISOAbbreviation>(.*?)</ISOAbbreviation>", a)
            ti = re.search(r"<ArticleTitle>(.*?)</ArticleTitle>", a, re.S)
            ab = " ".join(re.sub(r"<[^>]+>", "", t) for t in re.findall(r"<AbstractText[^>]*>(.*?)</AbstractText>", a, re.S))
            pm = re.search(r"<PMID[^>]*>(\d+)</PMID>", a)
            arts.append({"pmid": pm.group(1) if pm else None, "journal": ta.group(1) if ta else "", "title": re.sub(r"<[^>]+>", "", ti.group(1)) if ti else "", "abstract": ab})
        jh = re.sub(r"[^a-z]", "", journal.lower())
        best = [a for a in arts if jh and re.sub(r"[^a-z]", "", a["journal"].lower()).startswith(jh[:6])]
        rec["candidates"] = len(arts)
        rec["match"] = best[0] if len(best) == 1 else None
        rec["status"] = "matched" if len(best) == 1 else ("ambiguous" if len(best) > 1 else "no-journal-match")
        if len(best) > 1:
            rec["ambiguous"] = [{"pmid": a["pmid"], "title": a["title"]} for a in best]
    else:
        rec["status"] = "no-hit"
    out.append(rec)
    print(rec["status"], label, flush=True)
json.dump(out, open(sys.argv[2], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print({s: sum(o["status"] == s for o in out) for s in set(o["status"] for o in out)})
