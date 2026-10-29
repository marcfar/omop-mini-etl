"""Data quality checks. Each check returns the DataFrame so it can be used with .pipe()."""

import pandas as pd


class DataQualityError(Exception):
    """Raised when a data quality check fails."""


def assert_unique(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    n_dup = df.duplicated(subset=cols, keep=False).sum()
    if n_dup:
        raise DataQualityError(f"{n_dup} rows with duplicated {cols}")
    return df


def assert_no_nulls(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    nulls = df[cols].isna().sum()
    nulls = nulls[nulls > 0]
    if not nulls.empty:
        raise DataQualityError(f"Null values found: {nulls.to_dict()}")
    return df


