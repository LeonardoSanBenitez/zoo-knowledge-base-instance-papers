#!/bin/sh
# Regenerates every number in ../paper.json and ../NOTES.md from the authors' OSF deposit.
# Run from the paper folder:  sh reanalysis/run_all.sh
# Fetch: the zoo's shared acquirer (sha256+md5 verified, version-pinned; 40/40 verified on 2026-10-16).
set -e
mkdir -p work out
[ -d work/osf ] || python ../../../../dev-science-ops/paper-retrospective-reproducibility/tools/acquire.py osf:qt65w --out work/osf
for s in s1 s1b s1c s1b_scale s2 s2_types s2_neutral s3a s3a_carryover s3a_identifiability s3b s3bd s3c; do
  echo "== $s"; PYTHONPATH=reanalysis python reanalysis/$s.py > out/$s.txt 2>&1 || { echo FAILED $s; cat out/$s.txt; exit 1; }
done
echo "all scripts ran; outputs in out/. work/ holds the authors' data (no licence declared on OSF: not committed)."
