#!/bin/sh
# From the zoo root. Regenerates every number in paper.json. ~64 MB download; r02 is the slow step.
set -e
P=zoo-knowledge-base/instance-papers/papers/petrini2023-compression-word-lengths
D=${1:-zoo-knowledge-base/.research/petrini2023-repo}
python -I $P/reanalysis/fetch.py "$D"
python -I $P/reanalysis/r01_reproduce.py "$D" $P/artifacts | tee $P/artifacts/r01_out.txt
python -I $P/reanalysis/r02_known_answer.py "$D" $P/artifacts 20 | tee $P/artifacts/r02_out.txt
python -I $P/reanalysis/r03_sample_size_and_duration.py "$D" $P/artifacts | tee $P/artifacts/r03_out.txt
python -I $P/reanalysis/r05_markov_typing.py "$D" $P/artifacts 10 | tee $P/artifacts/r05_out.txt
python -I $P/reanalysis/r06_markov_order_k.py "$D" $P/artifacts 5 | tee $P/artifacts/r06_out.txt
PYTHONIOENCODING=utf-8 python -I $P/reanalysis/r04_descriptive_tables.py "$D" | tee $P/artifacts/r04_out.txt
