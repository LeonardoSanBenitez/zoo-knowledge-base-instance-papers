"""2026-11-06 (maria): z03 (permutation null of r, 30 permutations) is in. It corrects my reading of K1 (.645):
that was one draw, 2.3 SD out in a null with mean 0 and SD .28. The real .943 exceeds all 30 permuted draws, so the
real r is informative -- about row-level discrimination (pools differ on z), which is still not calibration. Edits
asserted before replacing (lessons_tooling.md)."""
import json
from pathlib import Path

P = Path(__file__).resolve().parents[1]
pj = P / "paper.json"
d = json.loads(pj.read_text(encoding="utf-8"))

old = ("With the originals' z PERMUTED across rows (no z-outcome link at all) the same design returns r = .645; with "
       "z-curve replaced by the share of z > 2.8 it returns .945, identical to z-curve; at fixed n a single random "
       "permutation already gives r = -.30.")
new = ("With the originals' z PERMUTED across rows (no z-outcome link at all) the design's r has mean 0 but SD .28 over "
       "30 permutations (z03; |r| > .5 in 10%; single draws gave .645 and -.30), so a large r from this design is not "
       "rare even without information; the real .943 nonetheless exceeds all 30 permuted draws (max .524), so it does "
       "reflect that the success and failure pools differ on z (row AUC .737). With z-curve replaced by the share of "
       "z > 2.8 the design returns .944-.945, identical to z-curve.")
hits = [c for c in d["claims"] if old in c["our_assessment"]["why"]]
assert len(hits) == 1, len(hits)
hits[0]["our_assessment"]["why"] = hits[0]["our_assessment"]["why"].replace(old, new)
hits[0]["our_assessment"]["why"] += (" Corrected 2026-11-06 after z03: the first version of this assessment (2026-11-05) "
                                      "read the single permuted draw .645 as 'the design gives r without information'.")

k1 = [c for c in d["instrument_checks"] if c.get("value") == 0.645]
assert len(k1) == 1
k1[0]["world"] += " -- ONE permutation; z03 shows it is a 2.3-SD draw from a null with mean 0, SD .28"
d["instrument_checks"] += [
    {"instrument": "z-curve ERR validated by outcome-stratified sampling (r with realised RR)",
     "world": "originals' z permuted across rows, 30 independent permutations",
     "design": "paper's sampler at fixed n = 150, 120 samples per permutation (z03)",
     "statistic": "share of permutations with |r(ERR, RR)| > .5 (mean r -.002, SD .283, range -.573..+.524)",
     "value": 0.10, "n_sims": 30, "verdict": "artifact",
     "source": "reanalysis/out/z03_out.txt"},
    {"instrument": "z-curve ERR validated by outcome-stratified sampling (r with realised RR)",
     "world": "real data vs the 30-permutation null above",
     "design": "same as z03",
     "statistic": "real r (.943) minus the largest permuted r (.524)",
     "value": 0.419, "n_sims": 30, "verdict": "informative",
     "source": "reanalysis/out/z03_out.txt"},
]
oq = d["open_questions"]
assert oq[0].startswith("z03 permutation null of r")
oq[0] = ("ANSWERED 2026-11-06 (z03, 30 permutations x 120 samples): r(ERR, RR) under permuted z has mean -.002, SD .283, "
         "|r| > .5 in 10%; share(z > 2.8) mean .034, SD .273. Real r .943 / .944 exceed every permuted draw.")
pj.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

nm = P / "NOTES.md"
s = nm.read_text(encoding="utf-8")
a = "| K1 same design, z permuted (no z-outcome link) | **.645** | the design gives r without information |"
assert a in s
s = s.replace(a, "| K1 same design, z permuted ONCE (no z-outcome link) | **.645** | one draw: see z03 (corrected 2026-11-06) |")
b = ("K1 (.645) and F2 (-.296) are single draws from the permutation null of this design: one random split of the z values\n"
     "between the two pools already differs enough to be amplified into |r| of .3-.6 (z03 measures the spread).")
assert b in s
s = s.replace(b, b + """

**z03 (2026-11-06), the measured spread.** 30 permutations x 120 samples at n = 150: r(ERR, RR) mean -.002, SD .283,
range -.573..+.524, |r| > .5 in 10%; share(z > 2.8) mean .034, SD .273. Real data: .943 / .944, above every permuted
draw. **Correction to my 11-05 reading:** K1 (.645) was a 2.3-SD draw, not what the design typically gives with no
information. What stands: the design makes |r| of .3-.5 common from nothing (an iid null at 120 samples would have
SD ~.09); a trivial statistic matches z-curve exactly; and the real r measures row-level discrimination (pools differ on
z), not literature-level calibration (K3, K4).""")
nm.write_text(s, encoding="utf-8")
print("ok")
