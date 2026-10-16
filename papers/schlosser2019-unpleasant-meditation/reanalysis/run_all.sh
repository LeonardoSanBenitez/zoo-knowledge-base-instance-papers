#!/bin/sh
# Run from the paper folder: sh reanalysis/run_all.sh
# Fetches the authors' data (OSF component d6mgj, hash-verified) unless SCHLOSSER_DATA points at it.
set -e
mkdir -p work re out
[ -d work/osf_d6mgj ] || python ../../../../dev-science-ops/paper-retrospective-reproducibility/tools/acquire.py osf:d6mgj --out work/osf_d6mgj
export SCHLOSSER_DATA=${SCHLOSSER_DATA:-work/osf_d6mgj/files/osfstorage/}
for s in m1 m2 m3 m4; do echo "== $s"; python reanalysis/$s.py > out/$s.txt 2>&1 || { cat out/$s.txt; exit 1; }; done
