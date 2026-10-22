"""Backfill zoo-paper-record 1.6 fields by SURGICAL TEXT EDIT (lesson 2026-10-16: re-serialising
hand-formatted JSON makes a 10k-line diff). Proof of correctness: parse(new) == parse(old) + exactly
the intended changes, asserted per record.

  selection  <- classification.json (retrospective, by maria, 2026-10-22)
  origin     <- 'reader' for claims whose statement opens with a reader marker (kb.py _READER_MARKERS)

Usage (from zoo root): python -I zoo-knowledge-base/instance-papers/papers/maria2026-selection-and-reader-bias/reanalysis/backfill_16.py [--write]
"""
import json, os, re, sys, copy, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ZOO = HERE
while not os.path.isdir(os.path.join(ZOO, 'zoo-knowledge-base')):
    ZOO = os.path.dirname(ZOO)
CLS = os.path.join(HERE, 'classification.json')
if not os.path.exists(CLS):
    CLS = os.path.join(HERE, '..', 'artifacts', 'classification.json')
PAPERS = os.path.join(ZOO, 'zoo-knowledge-base', 'instance-papers', 'papers')
WRITE = '--write' in sys.argv
CLASS = {'B': 'blind', 'F1': 'finding-first', 'F2': 'hypothesis-test', 'K': 'known-dispute', 'C': 'chain'}
CENSUS = {'arslan2026-bodhi-engineering', 'cajas2026-agents-catching-agents',
          'cajas2026-creativity-constraint', 'huang2026-reward-hacking-research-agents'}
MARK = re.compile(r"^\s*\(?\s*(maria 2026|ours\b|our (own|reanalysis|analysis|artifact)|zoo reanalysis|"
                  r"recorded as)", re.I)

rows = json.load(open(CLS, encoding='utf-8'))['rows']
sel_of = {}
for rid, c, ev, hind in rows:
    cls = 'census' if rid in CENSUS else CLASS[c]
    e = ev + (' [Evidence written after the finding.]' if hind else '')
    sel_of[rid] = {'class': cls, 'evidence': e, 'recorded': 'retrospective', 'by': 'maria, 2026-10-22'}

changed = 0
for f in sorted(glob.glob(os.path.join(PAPERS, '*', 'paper.json'))):
    raw = open(f, encoding='utf-8', newline='').read()
    old = json.loads(raw)
    rid = old['id']
    reader_claims = [c['id'] for c in old['claims'] if MARK.search(c['statement'])
                     and not rid.startswith('maria2026-') and c.get('origin') is None]
    if rid not in sel_of and not reader_claims:
        continue
    new_raw = raw
    NL = '\r\n' if '\r\n' in raw else '\n'
    expect = copy.deepcopy(old)
    # schema_version
    m = re.search(r'"schema_version":\s*"([0-9.]+)"', new_raw)
    assert m and new_raw.count('"schema_version"') == 1, rid
    new_raw = new_raw[:m.start()] + '"schema_version": "1.6"' + new_raw[m.end():]
    expect['schema_version'] = '1.6'
    # selection, after the read_depth line, same indentation
    if rid in sel_of and 'selection' not in old:
        m = re.search(r'^([ \t]*)"read_depth":\s*"[^"]*",[ \t]*\r?\n', new_raw, re.M)
        assert m, rid
        ind = m.group(1)
        ins = ind + '"selection": ' + json.dumps(sel_of[rid], ensure_ascii=False) + ',' + NL
        new_raw = new_raw[:m.end()] + ins + new_raw[m.end():]
        expect['selection'] = sel_of[rid]
    # origin, after the statement line of each reader claim
    for cid in reader_claims:
        m = re.search(r'"id":\s*"%s"\s*,' % cid, new_raw)
        assert m, (rid, cid)
        ms = re.compile(r'^([ \t]*)"statement":\s*"(?:[^"\\]|\\.)*",[ \t]*\r?\n', re.M).search(new_raw, m.end())
        assert ms, (rid, cid)
        # the statement found must belong to this claim: no other "id": "c.." in between
        assert not re.search(r'"id":\s*"c[0-9]+"', new_raw[m.end():ms.start()]), (rid, cid)
        ins = ms.group(1) + '"origin": "reader",' + NL
        new_raw = new_raw[:ms.end()] + ins + new_raw[ms.end():]
        for c in expect['claims']:
            if c['id'] == cid:
                c['origin'] = 'reader'
    got = json.loads(new_raw)
    # key ORDER is irrelevant to equality; values must match exactly
    assert got == expect, rid
    changed += 1
    print(('WRITE ' if WRITE else 'dry   ') + rid.ljust(52), 'selection' if rid in sel_of else '-',
          'origin:' + ','.join(reader_claims) if reader_claims else '')
    if WRITE:
        open(f, 'w', encoding='utf-8', newline='').write(new_raw)
print(changed, 'record(s)')
