"""Loader for the public #fincap team-level table.

Source: https://fincap.academy/data/fincap-data.zip (239,353 bytes,
sha256 9938ca5ccd5e16864afd43553e7f100042034d963b46b0bd72fa58295b34c6d8), the only
public release; the OSF project root (rkndz) is private -- 401 -- and only the
pre-analysis-plan component (vn6x4 / h82aj) is open.

RT_research_results.xlsx: 164 research teams x 6 hypotheses x 4 stages = 3,936 rows,
balanced, no missing estimates. `reproducibility_score` and the peer rating exist for
one stage only (984 rows).
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
XLS = os.path.join(HERE, '..', 'artifacts', 'fincap', 'RT_research_results.xlsx')
BEL = os.path.join(HERE, '..', 'artifacts', 'fincap', 'RT_beliefs.xlsx')


def results():
    d = pd.read_excel(XLS)
    d = d.rename(columns={
        'research_team_id': 'team', 'rt_hypothesis': 'hyp',
        'standard_error': 'se', 'first_principle_component_team_quality': 'quality',
        'reproducibility_score': 'repro',
        'average_rating_by_peers_after_removing_peer_fixed_effect': 'peer'})
    return d


def beliefs():
    return pd.read_excel(BEL)
