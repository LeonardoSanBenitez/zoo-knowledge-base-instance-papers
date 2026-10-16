#!/bin/sh
# Run from the paper folder: sh reanalysis/run_all.sh
# Data: artifacts/InfoRateData.csv (CC-BY 4.0, copied from github.com/keruiduo/SupplMatInfoRate @ 00798db).
set -e
mkdir -p out re
for s in r1 r2 r3 r4 r5_known_answer; do echo "== $s"; INFORATE_REPO=artifacts/ python reanalysis/$s.py > out/$s.txt 2>&1 || { cat out/$s.txt; exit 1; }; done
rm -rf re
