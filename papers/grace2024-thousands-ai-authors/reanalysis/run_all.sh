#!/bin/sh
# Run from the paper folder: sh reanalysis/run_all.sh   (several minutes: ~5,000 least-squares CDF fits)
# Data: OSF vmdny (CC BY-SA 4.0), fetched and hash-verified by the zoo's acquirer; not committed (10.5 MB).
set -e
mkdir -p work out
[ -d work/osf ] || python ../../../../dev-science-ops/paper-retrospective-reproducibility/tools/acquire.py osf:vmdny --out work/osf
export ESPAI_DATA=${ESPAI_DATA:-work/osf/files/osfstorage/}
python reanalysis/e1.py > out/e1_extinction.txt 2>&1
python reanalysis/e3.py hlmi > out/e3_hlmi.txt 2>&1
python reanalysis/e3.py faol > out/e3_faol.txt 2>&1
python reanalysis/e4.py > out/e4_family.txt 2>&1
# e2_nelder_mead_crosscheck.py is the slower first implementation (12 Nelder-Mead starts); it gave the same
# HLMI quantiles to the year (2027/2048/2198 vs 2028/2048/2200) and is kept as a fitter cross-check, not run here.
