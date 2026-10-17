"""g5 -- How many GSM-IC variants change the base problem beyond inserting one sentence?
Appendix A step 4: when the added sentence creates ambiguity the authors REWRITE the question. For each variant,
remove the inserted sentence (if found as a contiguous sentence) and compare with the original after whitespace
normalisation. Author: maria 2026-10-17."""
import json, re, collections, difflib
A = json.load(open('GSM-IC_2step.json', encoding='utf-8')) + json.load(open('GSM-IC_mstep.json', encoding='utf-8'))
ws = lambda s: ' '.join(s.split())
cnt = collections.Counter(); bases_edited = collections.Counter(); ex = {}
for x in A:
    o, n = ws(x['original_question']), ws(x['new_question'])
    so = re.split(r'(?<=[.!?])\s+', o); sn = re.split(r'(?<=[.!?])\s+', n)
    if len(sn) == len(so) + 1:
        cand = [sn[:i] + sn[i + 1:] for i in range(len(sn))]
        if any(c == so for c in cand): cnt['pure insertion'] += 1; continue
    cnt['other change'] += 1; bases_edited[o] += 1
    ex.setdefault(o, (o, n, x['role_label'], x['sentence_label']))
print(cnt, f"share other = {cnt['other change']/len(A):.3%}")
print('bases with any edited variant:', len(bases_edited), '| edited variants per such base (min/med/max):',
      min(bases_edited.values()), sorted(bases_edited.values())[len(bases_edited)//2], max(bases_edited.values()))
lab = collections.Counter((e[2], e[3]) for e in ex.values())
byrole = collections.Counter(x['role_label'] for x in A if ws(x['original_question']) in bases_edited and True)
for o, n, r, s in list(ex.values())[:4]:
    print('\nORIG:', o[-160:]); print('NEW :', n[-200:]); print(r, s)
