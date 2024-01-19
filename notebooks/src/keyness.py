from typing import Dict, Tuple

import numpy as np
import pandas as pd

_SMALL = 1e-20


def compute_expected(observed: np.array) -> np.array:
    """Computes the contingency table of the expected values given a contingency table
    of the observed values."""
    expected = np.array([
        [
            observed[0, :].sum() * observed[:, 0].sum() / observed.sum(),
            observed[0, :].sum() * observed[:, 1].sum() / observed.sum()
        ],
        [
            observed[1, :].sum() * observed[:, 0].sum() / observed.sum(),
            observed[1, :].sum() * observed[:, 1].sum() / observed.sum()
        ]
    ])
    return expected


def get_observed_from_row(row: Dict, source: str, totals: pd.DataFrame) -> np.array:
    t_target = row[source]
    t_ref = get_complement_from_row(row, source)
    nt_target = totals.loc[source].target_freq - t_target
    nt_ref = totals.loc[source].ref_freq - t_ref
    observed = np.array([
        [t_target, t_ref],
        [nt_target, nt_ref]
    ])
    return observed


def get_complement_from_row(row: Dict, source: str) -> float:
    return row['Total'] - row[source]


def compute_log_likelihood_from_observed(observed: np.array) -> Tuple[float, str]:
    """Computes the log likelihood ratio for given a target token, and target and
    reference analysers and counters."""
    sum_likelihood = 0
    expected = compute_expected(observed)
    for i in [0, 1]:
        for j in [0, 1]:
            sum_likelihood += observed[i, j] * np.log((observed[i, j] + _SMALL) / (expected[i, j] + _SMALL))
    return 2 * sum_likelihood, 'more' if observed[0, 0] > expected[0, 0] else 'less'


def compute_log_likelihood_from_row(row: Dict, source: str, totals: pd.DataFrame) -> float:
    observed = get_observed_from_row(row, source, totals)
    ll, sign = compute_log_likelihood_from_observed(observed)
    # return ll if sign == 'more' else -ll
    return ll


def compute_category_totals(keyword_cat_freq: pd.DataFrame) -> pd.DataFrame:
    """Compute the total number of keyword frequencies per category and the
    total number of keyword frequencies of the complement (all other categories).

    For each category, the total is the total of the category as target category.
    The complement is the total of the reference corpus."""
    keyword_cat_totals = keyword_cat_freq.sum()
    keyword_cat_totals = keyword_cat_totals.rename('target_freq').to_frame()
    keyword_cat_totals['ref_freq'] = (keyword_cat_totals.loc['Total'] - keyword_cat_totals)
    return keyword_cat_totals


def compute_keyword_category_freq(df: pd.DataFrame, category_col: str,
                                  keyword_col: str) -> pd.DataFrame:
    """Compute frequency of keywords per category."""
    key_cat_freq = df.groupby(keyword_col)[category_col].value_counts().unstack().fillna(0)
    key_cat_freq['Total'] = key_cat_freq.sum(axis=1)
    return key_cat_freq


def compute_keyness(keyword_cat_freq: pd.DataFrame, keyword_cat_totals: pd.DataFrame,
                    category: str) -> pd.Series:
    # keyword_cat_totals = compute_category_totals(keyword_cat_freq)
    return keyword_cat_freq.apply(lambda keyword: compute_log_likelihood_from_row(keyword,
                                                                                  category,
                                                                                  keyword_cat_totals), axis=1)


def compute_percent_diff(keyword_cat_freq: pd.DataFrame, cat_totals: pd.DataFrame):
    percent_diff = pd.DataFrame()
    for category in keyword_cat_freq.columns:
        if category == 'Total':  # != genre:
            continue
        keyword_cat_frac_target = keyword_cat_freq / cat_totals.target_freq
        keyword_cat_frac_ref = (keyword_cat_freq.Total - keyword_cat_freq[category]) / cat_totals.loc[category].ref_freq
        percent_diff[category] = 100 * (keyword_cat_frac_target[category] - keyword_cat_frac_ref) / keyword_cat_frac_ref
    return percent_diff

"""
def compute_percent_diff(keyword_cat_freq: pd.DataFrame, cat_totals: pd.DataFrame):

    key_cat_target_frac = keyword_cat_freq.div(keyword_cat_freq.sum())
    key_cat_target_frac = keyword_cat_freq.div(cat_totals.sum())
    percent_diff = pd.DataFrame()
    for category in keyword_cat_freq.columns:
        key_cat_ref_freq = keyword_cat_freq.Total - keyword_cat_freq[category]
        key_cat_ref_frac = key_cat_ref_freq / key_cat_ref_freq.sum()
        percent_diff[category] = 100 * (key_cat_target_frac[category] - key_cat_ref_frac) / key_cat_ref_frac
        percent_diff[category] = 100 * (key_cat_target_frac[category] - key_cat_ref_frac) / key_cat_ref_frac
    return percent_diff
"""
