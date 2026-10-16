#!/bin/sh
# Run from the paper folder: sh reanalysis/run_all.sh
set -e
mkdir -p work out
for g in erp2z c4qy9; do [ -d work/osf_$g ] || python ../../../../dev-science-ops/paper-retrospective-reproducibility/tools/acquire.py osf:$g --out work/osf_$g; done
python reanalysis/x1.py > out/x1_printed_chisq.txt
SCHUBERT_DATA=work python reanalysis/x2.py > out/x2_port.txt 2>&1
python reanalysis/free_text.py > out/free_text.txt
