#!/bin/sh
# Run from the paper folder: sh reanalysis/run_all.sh   (needs ~430 MB free in work/; deleted afterwards is fine)
# 1. model: the authors' released IB model (Dropbox; the repo's own loader URL)
# 2. WCS data: the code's ICSI URLs are DEAD (timeout 2026-10-16); the archive now lives at linguistics.berkeley.edu
set -e
mkdir -p work/repo/models work/wcs out
[ -f work/repo/models/IB_color_naming_model/IB_color_naming.pkl ] || { curl -sL -o work/repo/models/temp.zip "https://www.dropbox.com/s/70w953orv27kz1o/IB_color_naming_model.zip?dl=1"; (cd work/repo/models && python -c "import zipfile;zipfile.ZipFile('temp.zip').extractall('.')"); }
for f in data/20021219/txt/term.txt data/20021219/txt/chip.txt data/cnum-maps/cnum-vhcm-lab-new.txt; do [ -f work/wcs/$(basename $f) ] || curl -sL -o work/wcs/$(basename $f) "https://linguistics.berkeley.edu/wcs/$f"; done
mkdir -p work/re; cp reanalysis/c*.py work/re/
cd work && IBC=. python re/c1.py > ../out/c1.txt && python re/c2.py > ../out/c2.txt && python re/c3.py > ../out/c3.txt && python re/c4.py > ../out/c4.txt
