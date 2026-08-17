"""Extract a small tidy model-level table from the 912 MB CRI repo.

The repo (https://github.com/nbreznau/CRI @ dd5dcb27) is far above the 50 MB
keep-threshold in instance-papers/CONTRIBUTING.md, so it is inspected and deleted;
this script is the fetch+reduce step that regenerates everything the reanalysis
needs from a fresh clone.

Usage:
    git clone https://github.com/nbreznau/CRI.git
    cd CRI && git checkout dd5dcb27a190bfb27209018f1b02af3fedda9f55
    python 00_extract.py <path-to-CRI>

Source file: CRI/data/cri.csv  -- 1309 rows x 479 cols, latin-1 (utf-8 read FAILS
at byte 0x91, position 230354: a curly quote in a free-text field).
"""
import sys, os, json, hashlib
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data")

def main(cri_root):
    src = os.path.join(cri_root, "data", "cri.csv")
    raw = open(src, "rb").read()
    print("source sha256", hashlib.sha256(raw).hexdigest(), len(raw), "bytes")
    d = pd.read_csv(src, low_memory=False, encoding="latin-1")
    cols = list(d.columns)
    print("raw shape", d.shape)

    meta = ['u_teamid', 'id', 'AME', 'lower', 'upper', 'error', 'z', 'p',
            'AME_Z', 'lower_Z', 'upper_Z', 'inv_weight',
            'DV', 'main_IV_type', 'main_IV_source', 'main_IV_measurement',
            'main_IV_time', 'main_IV_effect', 'package', 'num_countries',
            'team_size', 'Hresult', 'AME_sup_p05', 'AME_neg_p05', 'AME_ns_p05',
            'countries', 'software', 'iv_type']
    # the contiguous block of analytic-decision indicators, in file order
    i0, i1 = cols.index('Jobs'), cols.index('anynonlin')
    decisions = cols[i0:i1 + 1]
    researcher = [c for c in cols if c.startswith(
        ('belief_', 'attitude_', 'backgr_', 'delib_', 'u_expgroup', 'model_eval'))]

    keep = list(dict.fromkeys([c for c in meta + decisions + researcher if c in cols]))
    os.makedirs(OUT, exist_ok=True)
    d[keep].to_csv(os.path.join(OUT, "cri_model_level.csv"), index=False, encoding="utf-8")
    json.dump({"meta": meta, "decisions": decisions, "researcher": researcher},
              open(os.path.join(OUT, "column_blocks.json"), "w"), indent=1)
    print("kept", len(keep), "cols =", len(meta), "meta +", len(decisions),
          "decisions +", len(researcher), "researcher")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
