"""Fetch DWUG EN/DE/SV V1 and V2 from Zenodo and keep only their stats files (the zips are 11-33 MB each).

    python papers/schlechtweg2024-more-dwugs/reanalysis/fetch_versions.py

Versions follow the paper's Table 2: DE 1.1.0 / 2.3.0, EN 1.0.0 / 2.0.1, SV 1.0.0 / 2.0.1.
A zip is deleted only after its stats_groupings.csv files are verified on disk.
"""
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

KB = Path(__file__).resolve().parents[4]
ROOT = Path(subprocess.run([sys.executable, str(KB / "tools" / "assets.py"), "path",
                            "paper-downloads/schlechtweg2024-more-dwugs"], capture_output=True, text=True,
                           check=True).stdout.strip()) / "data"
REC = {("de", "v1"): 5544198, ("de", "v2"): 7441645, ("en", "v1"): 5544444, ("en", "v2"): 7387261,
       ("sv", "v1"): 5090648, ("sv", "v2"): 7389506}
for (lang, v), rec in REC.items():
    out = ROOT / f"dwug_{lang}_{v}"
    if list(out.rglob("stats_groupings.csv")):
        print("have", out); continue
    z = ROOT / f"dwug_{lang}_{v}.zip"
    urllib.request.urlretrieve(f"https://zenodo.org/records/{rec}/files/dwug_{lang}.zip?download=1", z)
    with zipfile.ZipFile(z) as zf:
        names = [n for n in zf.namelist() if "/stats/" in n and n.endswith(".csv")]
        for n in names:
            zf.extract(n, out)
    got = list(out.rglob("stats_groupings.csv"))
    print(lang, v, rec, len(names), "stats csv;", [str(g.relative_to(out)) for g in got])
    if got:
        z.unlink()
    else:
        print("  KEPT zip: no stats_groupings.csv extracted", z)
print("FETCH_VERSIONS_OK")
