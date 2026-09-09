"""Shared loader for the NARPS deposited derived data.

Data: Zenodo 3709275 results.tgz (52.3 MB), sha256 21e07696...3abce1
      fetch: curl -sL -o narps_results.tgz \
        https://zenodo.org/api/records/3709275/files/results.tgz/content
Extracted to artifacts/narps_results/.
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', 'artifacts', 'narps_results')


def decisions():
    d = pd.read_csv(os.path.join(ROOT, 'figures', 'DecisionDataWide.csv'), index_col='teamID')
    d.columns = [int(c) for c in d.columns]
    return d


def confidence():
    d = pd.read_csv(os.path.join(ROOT, 'figures', 'ConfidenceDataWide.csv'), index_col='teamID')
    d.columns = [int(c) for c in d.columns]
    return d


def metadata():
    return pd.read_csv(os.path.join(ROOT, 'metadata', 'all_metadata.csv'))


def median_pattern_corr():
    return pd.read_csv(os.path.join(ROOT, 'metadata', 'median_pattern_corr.csv'))


def smoothness():
    return pd.read_csv(os.path.join(ROOT, 'metadata', 'smoothness_est.csv'))


def unthresh_corr(hyp):
    p = os.path.join(ROOT, 'output', 'correlation_unthresh', f'spearman_unthresh_hyp{hyp}.csv')
    return pd.read_csv(p, index_col=0)
