"""
src/data_processing/validators.py
----------------------------------
Validates that a raw job DataFrame contains the required columns
and that data types are sensible.

Think of this as a quality-control checkpoint before we do any
analysis — if the data doesn't look right, we log a warning
instead of silently producing wrong numbers.
"""

import logging
from typing import Tuple, List
import pandas as pd

logger = logging.getLogger(__name__)

# Columns that MUST exist (even if some rows are empty)
REQUIRED_COLUMNS = [
    "job_id", "title", "source", "scraped_at"
]

# All expected columns (used to detect schema drift)
EXPECTED_COLUMNS = [
    "job_id", "title", "company", "location", "category",
    "salary_min", "salary_max", "salary_currency",
    "experience_min", "experience_max", "education", "job_type",
    "skills", "description", "posting_date", "source",
    "job_url", "scraped_at",
]


def validate_required_columns(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Check that all required columns are present.

    Returns:
        (is_valid, list_of_missing_columns)
    """
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        logger.warning(f"Missing required columns: {missing}")
        return False, missing
    return True, []


def validate_schema(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Check that all expected columns exist.
    Returns a warning (not an error) if optional columns are absent —
    the pipeline can still continue with reduced information.
    """
    missing = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing:
        logger.info(f"Optional columns not found (this is OK): {missing}")
    return True, missing


def validate_date_column(df: pd.DataFrame, col: str = "posting_date") -> pd.DataFrame:
    """
    Convert a date column to proper datetime, coercing invalid values to NaT.
    Logs how many rows had unparseable dates.
    """
    if col not in df.columns:
        return df
    original_nulls = df[col].isna().sum()
    df[col] = pd.to_datetime(df[col], errors="coerce")
    new_nulls = df[col].isna().sum()
    if new_nulls > original_nulls:
        logger.warning(
            f"Column '{col}': {new_nulls - original_nulls} value(s) could not be "
            f"parsed as dates and were set to NaT."
        )
    return df


def validate_numeric_range(
    df: pd.DataFrame,
    min_col: str,
    max_col: str,
) -> pd.DataFrame:
    """
    Ensure that min_col <= max_col for each row.
    Rows where max < min are flagged with NaN (we don't invent correct values).
    """
    if min_col not in df.columns or max_col not in df.columns:
        return df

    df[min_col] = pd.to_numeric(df[min_col], errors="coerce")
    df[max_col] = pd.to_numeric(df[max_col], errors="coerce")

    # Find rows where the range is logically impossible
    invalid_mask = (
        df[min_col].notna() &
        df[max_col].notna() &
        (df[min_col] > df[max_col])
    )
    if invalid_mask.any():
        count = invalid_mask.sum()
        logger.warning(
            f"{count} row(s) have {min_col} > {max_col}. "
            f"Both values set to NaN for those rows."
        )
        df.loc[invalid_mask, [min_col, max_col]] = None

    return df


def generate_quality_report(df: pd.DataFrame) -> dict:
    """
    Produce a simple data-quality summary dictionary.
    Useful for displaying statistics in the dashboard.
    """
    total = len(df)
    report = {
        "total_rows": total,
        "missing_values": {},
        "completeness_pct": {},
    }
    for col in df.columns:
        missing_count = df[col].isna().sum()
        report["missing_values"][col] = int(missing_count)
        report["completeness_pct"][col] = round(
            (1 - missing_count / total) * 100, 1
        ) if total > 0 else 0.0

    return report
